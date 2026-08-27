#!/usr/bin/env python3
"""
Test script to search for flights from Vietnam to China using the MCP Flight Search service.
"""
import os
import sys
import asyncio
from datetime import datetime

# Add the mcp_flight_search module to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mcp_flight_search.services.search_service import search_flights

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))

async def search_affordable_flights():
    """Search for affordable flights from Vietnam to China after Feb 13, 2026."""
    
    print("🔍 Searching for affordable flights from Vietnam to China (after Feb 13, 2026)...\n")
    
    # Define search queries - comparing multiple routes for best prices
    searches = [
        {
            "name": "Hanoi → Guangzhou (Feb 16)",
            "origin": "HAN",
            "destination": "CAN",
            "outbound_date": "2026-02-16",
            "return_date": None
        },
        {
            "name": "Ho Chi Minh City → Guangzhou (Feb 16)",
            "origin": "SGN",
            "destination": "CAN",
            "outbound_date": "2026-02-16",
            "return_date": None
        },
        {
            "name": "Hanoi → Kunming (Feb 15)",
            "origin": "HAN",
            "destination": "KMG",
            "outbound_date": "2026-02-15",
            "return_date": None
        },
        {
            "name": "Ho Chi Minh City → Shenzhen (Feb 17)",
            "origin": "SGN",
            "destination": "SZX",
            "outbound_date": "2026-02-17",
            "return_date": None
        }
    ]
    
    all_results = []
    
    for search in searches:
        print(f"\n{'='*60}")
        print(f"Route: {search['name']}")
        print(f"{'='*60}")
        
        try:
            result = await search_flights(
                origin=search['origin'],
                destination=search['destination'],
                outbound_date=search['outbound_date'],
                return_date=search['return_date']
            )
            
            if result and result.get('flights'):
                flights = result['flights'][:3]  # Show top 3 cheapest
                print(f"\n✈️  Found {len(result['flights'])} flights. Top 3 cheapest:\n")
                
                for i, flight in enumerate(flights, 1):
                    price = flight.get('price', 'N/A')
                    airline = flight.get('airline', 'N/A')
                    departure = flight.get('departure_time', 'N/A')
                    arrival = flight.get('arrival_time', 'N/A')
                    duration = flight.get('duration', 'N/A')
                    stops = flight.get('stops', 0)
                    
                    print(f"#{i}: {airline}")
                    print(f"    💰 Price: {price}")
                    print(f"    🕐 Time: {departure} → {arrival}")
                    print(f"    ⏱️  Duration: {duration}")
                    print(f"    🔄 Stops: {stops}")
                    print()
                    
                all_results.append({
                    'route': search['name'],
                    'cheapest_price': flights[0].get('price', 'N/A') if flights else 'N/A',
                    'airline': flights[0].get('airline', 'N/A') if flights else 'N/A'
                })
            else:
                print("❌ No flights found for this route.\n")
                
        except Exception as e:
            print(f"❌ Error searching flights: {str(e)}\n")
            import traceback
            traceback.print_exc()
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 SUMMARY - Cheapest Options")
    print(f"{'='*60}\n")
    
    if all_results:
        sorted_results = sorted(all_results, key=lambda x: str(x['cheapest_price']))
        for i, result in enumerate(sorted_results, 1):
            print(f"{i}. {result['route']}")
            print(f"   {result['cheapest_price']} - {result['airline']}\n")
    else:
        print("No results found. Please check API key and try again.\n")

if __name__ == '__main__':
    asyncio.run(search_affordable_flights())

