#!/usr/bin/env python3
"""Search for flights from Da Nang to Xi'an in February 2026."""
import os
import sys
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mcp_flight_search.services.search_service import search_flights

os.environ['SERP_API_KEY'] = 'd7b73d39cf3c2b31e58410bec0d7adb04cfda1b113ae73075f8180a279e7dacd'

async def search_xian_flights():
    """Search for cheapest flights to Xi'an."""
    
    print("🔍 Searching Da Nang → Xi'an (February 2026)\n")
    
    dates = [
        "2026-02-14", "2026-02-15", "2026-02-16", 
        "2026-02-17", "2026-02-18", "2026-02-20",
        "2026-02-22", "2026-02-25", "2026-02-28"
    ]
    
    cheapest = None
    
    for date in dates:
        try:
            flights = await search_flights(
                origin="DAD",
                destination="XIY",  # Xi'an airport code
                outbound_date=date,
                return_date=None
            )
            
            if flights and len(flights) > 0:
                flight = flights[0]
                price_str = flight.get('price', 'N/A')
                
                if price_str != 'N/A':
                    price = int(price_str.replace('$','').replace(',',''))
                    
                    if cheapest is None or price < cheapest['price_num']:
                        cheapest = {
                            'date': date,
                            'price': price_str,
                            'price_num': price,
                            'airline': flight.get('airline', 'N/A'),
                            'duration': flight.get('duration', 'N/A'),
                            'stops': flight.get('stops', 0)
                        }
                        print(f"✅ Found cheaper: ${price} on {date} ({flight.get('airline')})")
                        
        except Exception as e:
            continue
    
    print(f"\n{'='*70}")
    print("📊 BEST OPTION: Da Nang → Xi'an")
    print(f"{'='*70}\n")
    
    if cheapest:
        print(f"💰 Price: ${cheapest['price_num']} USD")
        print(f"📅 Date: {cheapest['date']}")
        print(f"✈️  Airline: {cheapest['airline']}")
        print(f"⏱️  Duration: {cheapest['duration']} min")
        print(f"🔄 Stops: {cheapest['stops']} stop(s)")
    else:
        print("❌ No flights found to Xi'an in February")

if __name__ == '__main__':
    asyncio.run(search_xian_flights())
