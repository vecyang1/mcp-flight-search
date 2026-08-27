#!/usr/bin/env python3
"""
Advanced Flight Search CLI
Robust, multi-modal flight search tool for Agents and Users.
Supports: One-way, Round-trip, Date Ranges, Filters, and Exporting.
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

try:
    from mcp_flight_search.services.search_service import search_flights
    from mcp_flight_search.utils.airports import resolve_airport
    from mcp_flight_search.utils.ground_alternatives import get_ground_alternative
except ImportError:
    # Fallback if run from outside directory structure
    sys.path.insert(0, os.path.join(os.path.dirname(current_dir), 'mcp-flight-search'))
    from mcp_flight_search.services.search_service import search_flights
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

if not os.getenv('SERP_API_KEY'):
    print("Warning: SERP_API_KEY not found in environment or .env. Search may fail.", file=sys.stderr)

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
        # Post-processing filters
        valid_flights = []
        if flights:
            for f in flights:
                # Basic cleaning
                f['search_date'] = date
                f['type'] = 'Round Trip' if args.return_date else 'One Way'
                
                # Parse numeric price for sorting/filter (robust to any currency)
                price_str = str(f.get('price', '0'))
                try:
                    cleaned = re.sub(r'[^\d.]', '', price_str)
                    price_num = float(cleaned) if cleaned else float('inf')
                except:
                    price_num = float('inf')
                f['price_num'] = price_num
                
                # Stops filter
                if args.max_stops is not None:
                    stops = f.get('stops', 0)
                    if isinstance(stops, str): # Handle "Non-stop" or "1 stop" strings if raw
                        stops = 0 if 'Non' in stops else int(stops.split()[0])
                    if stops > args.max_stops:
                        continue
                        
                valid_flights.append(f)
                
        return valid_flights
        
    except Exception as e:
        if args.verbose:
            print(f"Error searching {date}: {e}")
        return []

async def main():
    parser = argparse.ArgumentParser(description="Advanced Flight Search CLI")
    
    # Core arguments
    parser.add_argument("origin", help="Origin airport code or city name (e.g., SGN, Hanoi, 河内)")
    parser.add_argument("destination", help="Destination airport code or city name (e.g., MEX, Guilin, 桂林)")
    parser.add_argument("date", help="Outbound date (YYYY-MM-DD)")
    
    # Range arguments
    parser.add_argument("--days", type=int, default=0, help="Search N consecutive days starting from date")
    parser.add_argument("--end-date", help="Search range until this date (YYYY-MM-DD)")
    parser.add_argument("--interval", type=int, default=1, help="Interval between dates in range (default: 1)")
    
    # Trip details
    parser.add_argument("--return-date", help="Return date for Round Trip (YYYY-MM-DD)")
    parser.add_argument("--currency", default="USD", help="ISO 4217 currency code for returned prices (default: USD)")
    parser.add_argument("--no-cache", action="store_true", help="Bypass local cache and force live query")
    
    # Filters
    parser.add_argument("--max-stops", type=int, help="Maximum number of stops (0=Non-stop)")
    
    # Output
    parser.add_argument("--format", choices=['table', 'json', 'csv'], default='table', help="Output format")
    parser.add_argument("--output-file", help="Save output to file")
    parser.add_argument("--verbose", action="store_true", help="Show progress")
    
    args = parser.parse_args()
    
    # Normalize and resolve inputs
    raw_origin = args.origin
    raw_dest = args.destination
    args.origin = resolve_airport(raw_origin)
    args.destination = resolve_airport(raw_dest)
    
    # Generate search dates
    search_dates = get_date_range(args.date, args.days, args.end_date, args.interval)
    
    if args.verbose or (raw_origin != args.origin or raw_dest != args.destination):
        route_desc = f"{raw_origin} ({args.origin}) -> {raw_dest} ({args.destination})" if (raw_origin != args.origin or raw_dest != args.destination) else f"{args.origin} -> {args.destination}"
        print(f"🔍 Route: {route_desc} | {len(search_dates)} date(s)")
        if args.return_date:
            print(f"🔄 Round Trip returning: {args.return_date}")
            
    # Execute searches
    all_results = []
    
    for i, d in enumerate(search_dates):
        if args.verbose:
            print(f"[{i+1}/{len(search_dates)}] Checking {d}...", end='\r')
            
        results = await search_single(args, d)
        if results:
            if len(search_dates) == 1:
                # For single date search, show all flights
                all_results.extend(results)
            else:
                # For multi-date range, pick cheapest flight per day
                cheapest = min(results, key=lambda x: x['price_num'])
                all_results.append(cheapest)
    
    if args.verbose:
        print("\nSearch complete.\n")

    # Sort final results by price
    all_results.sort(key=lambda x: x['price_num'])

    # OUTPUT HANDLERS
    if args.format == 'json':
        output_str = json.dumps(all_results, indent=2)
        print(output_str)
        
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
            
    else: # Table (Human Readable)
        if not all_results:
            print("❌ No flights found matching criteria.")
        else:
            # Enhanced Table Header
            print(f"{'Date':<12} {'Price':<10} {'Airline':<18} {'Dep/Arr':<35} {'Dur':<8} {'Stops':<24}")
            print("-" * 114)
            for r in all_results:
                try:
                    dep_str = r.get('departure', '').split('(')[0].strip()[-16:]
                    if len(dep_str) > 16: dep_str = dep_str[-16:]
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
            
        # Ground alternative advice if applicable
        alt_tip = get_ground_alternative(args.origin, args.destination)
        if alt_tip:
            print(f"\n{alt_tip}\n")
            
    # Save to file if requested and format was not CSV
    if args.output_file and args.format in ['json', 'table']:
        with open(args.output_file, 'w') as f:
            if args.format == 'json':
                f.write(json.dumps(all_results, indent=2))
            else:
                 f.write(f"Search Results: {args.origin} -> {args.destination}\n")
                 for r in all_results:
                     f.write(f"{r['search_date']}: {r['price']} ({r.get('airline')})\n")

if __name__ == "__main__":
    asyncio.run(main())
