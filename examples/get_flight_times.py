#!/usr/bin/env python3
"""Get detailed flight times for Da Nang to Chongqing on Feb 16, 2026."""
import os
import sys
import asyncio
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mcp_flight_search.services.search_service import search_flights

os.environ['SERP_API_KEY'] = 'd7b73d39cf3c2b31e58410bec0d7adb04cfda1b113ae73075f8180a279e7dacd'

async def get_flight_details():
    """Get detailed times for DAD → CKG on Feb 16."""
    
    print("🔍 Getting flight details for Da Nang → Chongqing (Feb 16, 2026)\n")
    
    flights = await search_flights(
        origin="DAD",
        destination="CKG",
        outbound_date="2026-02-16",
        return_date=None
    )
    
    if flights and len(flights) > 0:
        print(f"Found {len(flights)} flights:\n")
        
        for i, flight in enumerate(flights, 1):
            print(f"{'='*70}")
            print(f"Flight #{i}: {flight.get('airline', 'N/A')}")
            print(f"{'='*70}")
            print(f"💰 Price: {flight.get('price', 'N/A')}")
            print(f"🛫 Departure: {flight.get('departure_time', 'N/A')}")
            print(f"🛬 Arrival: {flight.get('arrival_time', 'N/A')}")
            print(f"⏱️  Duration: {flight.get('duration', 'N/A')}")
            print(f"🔄 Stops: {flight.get('stops', 0)}")
            
            if flight.get('layovers'):
                print(f"✈️  Layovers: {flight.get('layovers')}")
            
            print()
    else:
        print("No flights found.")

if __name__ == '__main__':
    asyncio.run(get_flight_details())
