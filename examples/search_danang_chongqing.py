#!/usr/bin/env python3
"""
Search for cheapest flights from Da Nang to Chongqing and nearby cities in February 2026.
"""
import os
import sys
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mcp_flight_search.services.search_service import search_flights

os.environ['SERP_API_KEY'] = 'd7b73d39cf3c2b31e58410bec0d7adb04cfda1b113ae73075f8180a279e7dacd'

async def find_cheapest_flights():
    """Search for cheapest flights from Da Nang to Chongqing/nearby cities."""
    
    print("🔍 Searching Da Nang → Chongqing & Nearby Cities (February 2026)\n")
    
    # Routes to search
    routes = [
        ("CKG", "Chongqing"),
        ("CTU", "Chengdu"),
        ("KMG", "Kunming"),
        ("CAN", "Guangzhou"),
    ]
    
    # Dates to try in February
    dates = [
        "2026-02-14", "2026-02-15", "2026-02-16", 
        "2026-02-17", "2026-02-18", "2026-02-20",
        "2026-02-22", "2026-02-25", "2026-02-28"
    ]
    
    all_results = []
    
    for dest_code, dest_name in routes:
        print(f"\n{'='*70}")
        print(f"🎯 Route: Da Nang (DAD) → {dest_name} ({dest_code})")
        print(f"{'='*70}")
        
        route_cheapest = None
        
        for date in dates:
            try:
                flights = await search_flights(
                    origin="DAD",
                    destination=dest_code,
                    outbound_date=date,
                    return_date=None
                )
                
                if flights and len(flights) > 0:
                    cheapest = flights[0]
                    price = cheapest.get('price', 'N/A')
                    
                    if price != 'N/A' and (route_cheapest is None or 
                        int(price.replace('$','').replace(',','')) < 
                        int(route_cheapest['price'].replace('$','').replace(',',''))):
                        route_cheapest = {
                            'date': date,
                            'price': price,
                            'airline': cheapest.get('airline', 'N/A'),
                            'destination': dest_name,
                            'dest_code': dest_code
                        }
                        
            except Exception as e:
                continue
        
        if route_cheapest:
            all_results.append(route_cheapest)
            print(f"\n✅ Cheapest found: {route_cheapest['price']}")
            print(f"   📅 Date: {route_cheapest['date']}")
            print(f"   ✈️  Airline: {route_cheapest['airline']}")
        else:
            print(f"\n❌ No flights found for this route")
    
    # Final summary
    print(f"\n\n{'='*70}")
    print("📊 FINAL RESULTS - Cheapest Options from Da Nang")
    print(f"{'='*70}\n")
    
    if all_results:
        sorted_results = sorted(all_results, 
            key=lambda x: int(x['price'].replace('$','').replace(',','')))
        
        for i, result in enumerate(sorted_results, 1):
            print(f"{i}. {result['destination']} ({result['dest_code']})")
            print(f"   💰 Price: {result['price']}")
            print(f"   📅 Date: {result['date']}")
            print(f"   ✈️  Airline: {result['airline']}\n")
    else:
        print("❌ No flights found. Try different dates or routes.\n")

if __name__ == '__main__':
    asyncio.run(find_cheapest_flights())
