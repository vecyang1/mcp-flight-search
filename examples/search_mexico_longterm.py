#!/usr/bin/env python3
"""
Long-term flight search: SGN to Mexico (Feb 6 - May 31, 2026)
Samples every 3-4 days to find cheapest options
"""
import os
import sys
import asyncio
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mcp_flight_search.services.search_service import search_flights

os.environ['SERP_API_KEY'] = 'd7b73d39cf3c2b31e58410bec0d7adb04cfda1b113ae73075f8180a279e7dacd'

async def search_mexico_long_term():
    """Search SGN to Mexico City across Feb-May 2026."""
    
    print("🔍 Searching SGN → Mexico City (Feb 6 - May 31, 2026)")
    print("Sampling every 3 days to find best prices...\n")
    
    start = datetime(2026, 2, 6)
    end = datetime(2026, 5, 31)
    
    # Sample every 3 days
    dates = []
    current = start
    while current <= end:
        dates.append(current.strftime('%Y-%m-%d'))
        current += timedelta(days=3)
    
    print(f"Searching {len(dates)} dates...\n")
    
    results = []
    
    for i, date in enumerate(dates, 1):
        try:
            flights = await search_flights("SGN", "MEX", date)
            
            if flights and len(flights) > 0:
                best = flights[0]
                price_str = best.get('price', 'N/A')
                
                if price_str != 'N/A':
                    price = int(price_str.replace('$','').replace(',',''))
                    results.append({
                        'date': date,
                        'price': price,
                        'price_str': price_str,
                        'airline': best.get('airline', 'N/A'),
                        'duration': best.get('duration', 'N/A'),
                        'stops': best.get('stops', 0)
                    })
                    print(f"✓ {i}/{len(dates)}: {date} - ${price} ({best.get('airline')})")
                else:
                    print(f"✗ {i}/{len(dates)}: {date} - No price")
            else:
                print(f"✗ {i}/{len(dates)}: {date} - No flights")
                
        except Exception as e:
            print(f"✗ {i}/{len(dates)}: {date} - Error: {str(e)}")
            continue
    
    # Sort by price
    results.sort(key=lambda x: x['price'])
    
    print(f"\n\n{'='*80}")
    print("📊 RANKED RESULTS - Cheapest Flights SGN → Mexico City")
    print(f"{'='*80}\n")
    
    if results:
        print(f"{'Rank':<6} {'Date':<12} {'Price':<10} {'Airline':<20} {'Duration':<12} {'Stops'}")
        print("-" * 80)
        
        for i, r in enumerate(results[:30], 1):  # Show top 30
            duration_hrs = f"{r['duration']//60}h {r['duration']%60}m" if r['duration'] != 'N/A' else 'N/A'
            print(f"{i:<6} {r['date']:<12} ${r['price']:<9} {r['airline']:<20} {duration_hrs:<12} {r['stops']}")
        
        print(f"\n✨ Best deal: {results[0]['date']} at ${results[0]['price']}")
        print(f"💰 Price range: ${results[0]['price']} - ${results[-1]['price']}")
        print(f"📅 Total dates with flights: {len(results)}")
    else:
        print("❌ No flights found in this period")

if __name__ == '__main__':
    asyncio.run(search_mexico_long_term())
