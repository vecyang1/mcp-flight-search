#!/usr/bin/env python3
"""
Advanced Flight Search & Aviation Intelligence CLI
Multi-modal flight search tool for Agents and Users.
Capabilities:
- Google Flights Price & Itinerary Search (SerpAPI)
- Live Commercial Flight Status & Delays (AeroDataBox: Terminals, Gates, Baggage, Actual Times)
- Airport FIDS Flight Boards (Arrivals & Departures)
- Airport Geography & METAR Weather
"""
import os
import sys
import asyncio
import argparse
import json
import csv
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any

# Ensure we can import the module
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from mcp_flight_search.services.search_service import search_flights
from mcp_flight_search.services.aerodatabox_service import (
    get_flight_status,
    get_airport_fids,
    get_airport_info,
)
from mcp_flight_search.utils.airports import resolve_airport
from mcp_flight_search.utils.ground_alternatives import get_ground_alternative

# Load API Key from .env if not in environment
if not os.getenv('SERP_API_KEY'):
    env_path = os.path.join(current_dir, '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('SERP_API_KEY='):
                    os.environ['SERP_API_KEY'] = line.strip().split('=', 1)[1]
                    break


def parse_date(date_str: str) -> datetime:
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        print(f"Error: Invalid date format '{date_str}'. Use YYYY-MM-DD.")
        sys.exit(1)


def get_date_range(start_date: str, days: int = 0, end_date: str = None, interval: int = 1) -> List[str]:
    start = parse_date(start_date)
    dates = []
    if end_date:
        end = parse_date(end_date)
        curr = start
        while curr <= end:
            dates.append(curr.strftime('%Y-%m-%d'))
            curr += timedelta(days=interval)
    elif days > 0:
        for i in range(0, days, interval):
            dates.append((start + timedelta(days=i)).strftime('%Y-%m-%d'))
    else:
        dates.append(start_date)
    return dates


def _format_table(headers: List[str], rows: List[List[str]]) -> str:
    """Render a clean text table with aligned columns."""
    if not rows:
        return "(No records found)"
    col_widths = [len(h) for h in headers]
    for row in rows:
        for idx, val in enumerate(row):
            col_widths[idx] = max(col_widths[idx], len(str(val)))

    header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    sep_line = "-+-".join("-" * col_widths[i] for i in range(len(headers)))
    row_lines = [
        " | ".join(str(val).ljust(col_widths[i]) for i, val in enumerate(r))
        for r in rows
    ]
    return f"{header_line}\n{sep_line}\n" + "\n".join(row_lines)


# =========================================================================
# AeroDataBox Handlers (Status, FIDS, Airport)
# =========================================================================

def handle_status(args):
    """Handle live flight status query."""
    flights = get_flight_status(args.flight_number, date=args.date, use_cache=not args.no_cache)
    if not flights:
        print(f"❌ No live status records found for flight '{args.flight_number}'.")
        return

    if args.format == "json":
        print(json.dumps(flights, indent=2, ensure_ascii=False))
        return

    if args.format == "csv":
        writer = csv.writer(sys.stdout)
        writer.writerow(["Flight", "Status", "Airline", "Dep_Airport", "Dep_Sched", "Dep_Actual", "Dep_Terminal", "Dep_Gate", "Dep_Delay", "Arr_Airport", "Arr_Sched", "Arr_Actual", "Arr_Terminal", "Arr_Gate", "Baggage"])
        for f in flights:
            d = f["departure"]
            a = f["arrival"]
            writer.writerow([
                f["flight_number"], f["status"], f["airline"],
                d["iata"] or d["airport"], d["scheduled"], d["actual_or_revised"], d["terminal"], d["gate"], d["delay_minutes"],
                a["iata"] or a["airport"], a["scheduled"], a["actual_or_revised"], a["terminal"], a["gate"], a["baggage_belt"],
            ])
        return

    # Table format
    print(f"\n--- Live Flight Status: {args.flight_number.upper()} ({len(flights)} Segment(s)) ---")
    for f in flights:
        d = f["departure"]
        a = f["arrival"]
        dep_str = f"{d['city'] or d['iata']} ({d['iata']})"
        arr_str = f"{a['city'] or a['iata']} ({a['iata']})"

        print(f"✈️  Flight   : {f['flight_number']} ({f['airline'] or 'Commercial Airline'})")
        print(f"📊 Status   : {f['status']} | Aircraft: {f['aircraft_model'] or 'N/A'} (Reg: {f['aircraft_reg'] or 'N/A'})")
        print(f"🛫 Departure: {dep_str}")
        print(f"   - Sched  : {d['scheduled'] or 'N/A'}")
        print(f"   - Actual : {d['actual_or_revised'] or 'On Time'} (Delay: {d['delay_minutes'] or 0} min)")
        print(f"   - Gate   : Terminal {d['terminal'] or '-'}, Gate {d['gate'] or '-'}")
        print(f"🛬 Arrival  : {arr_str}")
        print(f"   - Sched  : {a['scheduled'] or 'N/A'}")
        print(f"   - Actual : {a['actual_or_revised'] or 'On Time'} (Delay: {a['delay_minutes'] or 0} min)")
        print(f"   - Gate   : Terminal {a['terminal'] or '-'}, Gate {a['gate'] or '-'} | Baggage Belt: {a['baggage_belt'] or '-'}")
        print("-" * 65)
    print()


def handle_fids(args):
    """Handle live airport flight board (FIDS) query."""
    data = get_airport_fids(args.airport, direction=args.direction, hours=args.hours, use_cache=not args.no_cache)
    if args.format == "json":
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    airport_code = data["airport"]
    arrivals = data.get("arrivals") or []
    departures = data.get("departures") or []

    if args.direction in ("both", "arrivals", "arr"):
        print(f"\n--- Airport Arrivals: {airport_code} ({len(arrivals)} Flights) ---")
        headers = ["Flight", "Airline", "Origin", "Scheduled", "Actual/Est", "Terminal", "Gate", "Baggage", "Status"]
        rows = []
        for a in arrivals:
            rows.append([
                a.get("flight_number") or "-", (a.get("airline") or "-")[:16],
                a.get("origin") or "-", (a.get("scheduled") or "-")[-8:],
                (a.get("actual") or "-")[-8:], a.get("terminal") or "-",
                a.get("gate") or "-", a.get("baggage_belt") or "-", a.get("status") or "-"
            ])
        print(_format_table(headers, rows))

    if args.direction in ("both", "departures", "dep"):
        print(f"\n--- Airport Departures: {airport_code} ({len(departures)} Flights) ---")
        headers = ["Flight", "Airline", "Destination", "Scheduled", "Actual/Est", "Terminal", "Gate", "Status"]
        rows = []
        for d in departures:
            rows.append([
                d.get("flight_number") or "-", (d.get("airline") or "-")[:16],
                d.get("destination") or "-", (d.get("scheduled") or "-")[-8:],
                (d.get("actual") or "-")[-8:], d.get("terminal") or "-",
                d.get("gate") or "-", d.get("status") or "-"
            ])
        print(_format_table(headers, rows))
    print()


def handle_airport(args):
    """Handle airport details & weather."""
    info = get_airport_info(args.airport, use_cache=not args.no_cache)
    if args.format == "json":
        print(json.dumps(info, indent=2, ensure_ascii=False))
        return

    print(f"\n--- Airport Information: {info.get('name') or args.airport} ---")
    print(f"IATA / ICAO  : {info.get('iata') or '-'} / {info.get('icao') or '-'}")
    print(f"City / Country: {info.get('city') or '-'}, {info.get('country') or '-'}")
    print(f"Elevation    : {info.get('elevation_ft') or '-'} ft")
    print(f"Timezone     : {info.get('timezone') or '-'}")
    print(f"Runways      : {info.get('runway_count') or '-'}")
    print("---------------------------------------------------\n")


# =========================================================================
# Google Flights Pricing Search (SerpAPI)
# =========================================================================

async def search_single(args, date: str) -> List[Dict]:
    """Perform a search for a single outbound date."""
    try:
        flights = await search_flights(
            origin=args.origin,
            destination=args.destination,
            outbound_date=date,
            return_date=args.return_date,
            currency=args.currency,
            use_cache=not args.no_cache,
        )
        valid_flights = []
        if flights:
            for f in flights:
                f['search_date'] = date
                f['type'] = 'Round Trip' if args.return_date else 'One Way'
                price_str = str(f.get('price', '0'))
                try:
                    cleaned = re.sub(r'[^\d.]', '', price_str)
                    price_num = float(cleaned) if cleaned else float('inf')
                except:
                    price_num = float('inf')
                f['price_num'] = price_num
                
                if args.max_stops is not None:
                    if f.get('stops', 0) > args.max_stops:
                        continue
                if args.airline:
                    if args.airline.lower() not in f.get('airline', '').lower():
                        continue
                valid_flights.append(f)
        return valid_flights
    except Exception as e:
        print(f"Error searching date {date}: {str(e)}", file=sys.stderr)
        return []


async def handle_pricing_search(args):
    raw_origin = args.origin
    raw_dest = args.destination
    args.origin = resolve_airport(args.origin)
    args.destination = resolve_airport(args.destination)

    search_dates = get_date_range(args.date, args.days, args.end_date, args.interval)

    if args.verbose or (raw_origin != args.origin or raw_dest != args.destination):
        route_desc = f"{raw_origin} ({args.origin}) -> {raw_dest} ({args.destination})" if (raw_origin != args.origin or raw_dest != args.destination) else f"{args.origin} -> {args.destination}"
        print(f"🔍 Route: {route_desc} | {len(search_dates)} date(s)")
        if args.return_date:
            print(f"🔄 Round Trip returning: {args.return_date}")

    all_results = []
    for i, d in enumerate(search_dates):
        if args.verbose:
            print(f"[{i+1}/{len(search_dates)}] Checking {d}...", end='\r')
        results = await search_single(args, d)
        if results:
            if len(search_dates) == 1:
                all_results.extend(results)
            else:
                cheapest = min(results, key=lambda x: x['price_num'])
                all_results.append(cheapest)

    if args.verbose:
        print("\nSearch complete.\n")

    all_results.sort(key=lambda x: x['price_num'])

    if args.format == 'json':
        print(json.dumps(all_results, indent=2))
    elif args.format == 'csv':
        fieldnames = ['search_date', 'airline', 'flight_numbers', 'price', 
                      'departure', 'arrival', 'total_duration', 'stops', 'transit_cities', 'type']
        if args.output_file:
            with open(args.output_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(all_results)
        else:
            writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(all_results)
    else:
        if not all_results:
            print("❌ No flights found matching criteria.")
        else:
            print(f"{'Date':<12} {'Price':<10} {'Airline':<18} {'Dep/Arr':<35} {'Dur':<8} {'Stops':<24}")
            print("-" * 114)
            for r in all_results:
                try:
                    dep_str = r.get('departure', '').split('(')[0].strip()[-16:]
                    arr_str = r.get('arrival', '').split('(')[0].strip()[-16:]
                    times_route = f"{dep_str} -> {arr_str}"
                except:
                    times_route = "N/A"

                transit = r.get('transit_cities', 'None')
                if len(transit) > 24: transit = transit[:21] + "..."

                try:
                    dur_min = int(r.get('total_duration', '0').replace(' min', ''))
                    dur_str = f"{dur_min//60}h {dur_min%60}m"
                except:
                    dur_str = r.get('total_duration', 'N/A')

                print(f"{r['search_date']:<12} {r['price']:<10} {r.get('airline', 'N/A')[:18]:<18} {times_route:<35} {dur_str:<8} {transit:<24}")

            print("-" * 114)
            print(f"✨ Cheapest: {all_results[0]['search_date']} at {all_results[0]['price']} ({all_results[0].get('airline', 'N/A')})")

        alt_tip = get_ground_alternative(args.origin, args.destination)
        if alt_tip:
            print(f"\n{alt_tip}\n")

    if args.output_file and args.format in ['json', 'table']:
        with open(args.output_file, 'w') as f:
            if args.format == 'json':
                f.write(json.dumps(all_results, indent=2))
            else:
                f.write(f"Search Results: {args.origin} -> {args.destination}\n")
                for r in all_results:
                    f.write(f"{r['search_date']}: {r['price']} ({r.get('airline')})\n")


# =========================================================================
# Main Router
# =========================================================================

def main():
    # If first argument is one of the subcommands, parse accordingly
    if len(sys.argv) > 1 and sys.argv[1] in ("status", "fids", "airport"):
        subcmd = sys.argv[1]
        parser = argparse.ArgumentParser(description=f"AeroDataBox - {subcmd.capitalize()}")
        parser.add_argument("subcommand", choices=["status", "fids", "airport"])
        parser.add_argument("--format", choices=["table", "json", "csv"], default="table")
        parser.add_argument("--no-cache", action="store_true", help="Bypass local cache")

        if subcmd == "status":
            parser.add_argument("flight_number", help="Flight number (e.g. VN123, CA981)")
            parser.add_argument("date", nargs="?", default=None, help="Flight date (YYYY-MM-DD)")
            args = parser.parse_args()
            handle_status(args)
            return

        elif subcmd == "fids":
            parser.add_argument("airport", help="Airport code (e.g. HAN, SGN, CAN, VVNB)")
            parser.add_argument("--direction", choices=["arrivals", "departures", "both", "arr", "dep"], default="arrivals")
            parser.add_argument("--hours", type=int, default=6, help="Lookahead hours (max 12)")
            args = parser.parse_args()
            handle_fids(args)
            return

        elif subcmd == "airport":
            parser.add_argument("airport", help="Airport code (e.g. HAN, CAN, PVG, VVNB)")
            args = parser.parse_args()
            handle_airport(args)
            return

    # Standard Google Flights Pricing Search (Backward compatible)
    parser = argparse.ArgumentParser(description="Advanced Flight Price Search & Aviation Intelligence")
    parser.add_argument('origin', help="Origin Airport Code or City (e.g. HAN, 河内, SGN)")
    parser.add_argument('destination', help="Destination Airport Code or City (e.g. KWL, 桂林, CAN)")
    parser.add_argument('date', help="Outbound Date (YYYY-MM-DD)")
    parser.add_argument('--return-date', help="Return Date (YYYY-MM-DD) for Round Trip")
    parser.add_argument('--days', type=int, default=0, help="Number of days to check for lowest fare trend")
    parser.add_argument('--end-date', help="End Date for range search (inclusive)")
    parser.add_argument('--interval', type=int, default=1, help="Interval in days for range search")
    parser.add_argument('--currency', default="USD", help="Currency code (e.g. USD, CNY, EUR, VND)")
    parser.add_argument('--max-stops', type=int, default=None, help="Maximum number of stops allowed")
    parser.add_argument('--airline', help="Filter by Airline Name substring")
    parser.add_argument('--format', choices=['table', 'json', 'csv'], default='table', help="Output format")
    parser.add_argument('--output-file', help="Save results to specified file")
    parser.add_argument('--no-cache', action='store_true', help="Bypass local cache")
    parser.add_argument('--verbose', '-v', action='store_true', help="Verbose output")

    args = parser.parse_args()
    asyncio.run(handle_pricing_search(args))


if __name__ == "__main__":
    main()
