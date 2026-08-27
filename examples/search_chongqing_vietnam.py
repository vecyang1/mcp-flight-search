#!/usr/bin/env python3
"""Search for flights from Chongqing to Vietnam cities in February 2026."""
import os
import sys
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mcp_flight_search.services.search_service import search_flights

os.environ['SERP_API_KEY'] = 'd7b73d39cf3c2b31e58410bec0d7adb04cfda1b113ae73075f8180a279e7dacd'

async def search_chongqing_to_vietnam():
    """Search for cheapest flights from Chongqing to Vietnam."""
    
    print("🔍 Searching Chongqing → Vietnam (February 2026)\n")
    
    cities = [
        ("HAN", "Hanoi"),
        ("SGN", "Ho Chi Minh City"),
        ("DAD", "Da Nang")
    ]
    
    dates = [
        "2026-02-14", "2026-02-15", "2026-02-16", 
        "2026-02-17", "2026-02-18", "2026-02-20",
        "2026-02-22", "2026-02-25"
    ]
    
    all_results = []
    
    for dest_code, dest_name in cities:
        print(f"\n{'='*70}")
        print(f"🎯 Route: Chongqing (CKG) → {dest_name} ({dest_code})")
        print(f"{'='*70}")
        
        route_cheapest = None
        
        for date in dates:
            try:
                flights = await search_flights(
                    origin="CKG",
                    destination=dest_code,
                    outbound_date=date,
                    return_date=None
                )
                
                if flights and len(flights) > 0:
                    flight = flights[0]
                    price_str = flight.get('price', 'N/A')
                    
                    if price_str != 'N/A':
                        price = int(price_str.replace('$','').replace(',',''))
                        
                        if route_cheapest is None or price < route_cheapest['price_num']:
                            route_cheapest = {
                                'destination': dest_name,
                                'dest_code': dest_code,
                                'date': date,
                                'price': price_str,
                                'price_num': price,
                                'airline': flight.get('airline', 'N/A'),
                                'duration': flight.get('duration', 'N/A'),
                                'stops': flight.get('stops', 0)
                            }
                            
            except Exception as e:
                continue
        
        if route_cheapest:
            all_results.append(route_cheapest)
            print(f"\n✅ Cheapest: {route_cheapest['price']}")
            print(f"   📅 Date: {route_cheapest['date']}")
            print(f"   ✈️  Airline: {route_cheapest['airline']}")
            print(f"   ⏱️  Duration: {route_cheapest['duration']} min")
            print(f"   🔄 Stops: {route_cheapest['stops']}")
        else:
            print(f"\n❌ No flights found")
    
    print(f"\n\n{'='*70}")
    print("📊 FINAL RESULTS - Cheapest from Chongqing to Vietnam")
    print(f"{'='*70}\n")
    
    if all_results:
        sorted_results = sorted(all_results, key=lambda x: x['price_num'])
        
        for i, result in enumerate(sorted_results, 1):
            print(f"{i}. {result['destination']} ({result['dest_code']})")
            print(f"   💰 Price: {result['price']}")
            print(f"   📅 Date: {result['date']}")
            print(f"   ✈️  Airline: {result['airline']}")
            print(f"   ⏱️  Duration: {result['duration']} min")
            print(f"   🔄 Stops: {result['stops']}\n")

if __name__ == '__main__':
    asyncio.run(search_chongqing_to_vietnam())
