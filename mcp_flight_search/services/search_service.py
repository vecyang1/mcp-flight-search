"""
Flight search service implementation.
"""
from typing import List, Dict, Optional, Any, Union
from mcp_flight_search.utils.logging import logger
from mcp_flight_search.services.serpapi_client import run_search, prepare_flight_search_params
from mcp_flight_search.utils.airports import resolve_airport
from mcp_flight_search.utils.cache import make_cache_key, get_cached_flight_search, set_cached_flight_search

async def search_flights(
    origin: str,
    destination: str,
    outbound_date: str,
    return_date: Optional[str] = None,
    currency: str = "USD",
    use_cache: bool = True,
) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Search for flights using SerpAPI Google Flights with auto-airport resolution and caching.
    
    Args:
        origin: Departure airport code or city name (e.g., ATL, JFK, Hanoi, 河内)
        destination: Arrival airport code or city name (e.g., LAX, ORD, Guilin, 桂林)
        outbound_date: Departure date (YYYY-MM-DD)
        return_date: Return date for round trips (YYYY-MM-DD)
        currency: ISO 4217 currency code for the returned prices
        use_cache: Whether to check/store local cache
        
    Returns:
        A list of available flights with details
    """
    # 1. Resolve airport codes from city names or aliases
    norm_origin = resolve_airport(origin)
    norm_dest = resolve_airport(destination)
    
    logger.info(f"Searching flights: {origin}({norm_origin}) to {destination}({norm_dest}), dates: {outbound_date} - {return_date}")
    
    # 2. Check cache
    cache_key = make_cache_key(norm_origin, norm_dest, outbound_date, return_date, currency)
    if use_cache:
        cached_data = get_cached_flight_search(cache_key)
        if cached_data is not None:
            return cached_data
            
    # 3. Prepare search parameters
    params = prepare_flight_search_params(
        norm_origin,
        norm_dest,
        outbound_date,
        return_date,
        currency,
    )
    
    # 4. Execute search
    logger.debug("Executing SerpAPI search...")
    search_results = await run_search(params)
    
    # Check for errors
    if "error" in search_results:
        logger.error(f"Flight search error: {search_results['error']}")
        return {"error": search_results["error"]}
    
    # 5. Process flight results
    formatted = format_flight_results(search_results)
    
    # 6. Save to cache
    if use_cache and formatted and not isinstance(formatted, dict):
        set_cached_flight_search(cache_key, formatted)
        
    return formatted

def format_flight_results(search_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Format raw flight search results into a standardized format.
    
    Args:
        search_results: Raw search results from SerpAPI
        
    Returns:
        Formatted list of flight information
    """
    best_flights = search_results.get("best_flights", [])
    other_flights = search_results.get("other_flights", [])
    all_flights = best_flights + other_flights
    logger.debug(f"Search complete. Found {len(best_flights)} best flights and {len(other_flights)} other flights")
    
    if not all_flights:
        logger.warning("No flights found in search results")
        return []
    
    # Format flight data
    formatted_flights = []
    for i, flight in enumerate(all_flights):
        logger.debug(f"Processing flight {i+1} of {len(all_flights)}")
        segments = flight.get("flights", [])
        if not segments:
            continue
        
        # 1. Overall Flight Info
        first_segment = segments[0]
        last_segment = segments[-1]
        
        # Departure: First segment departure
        dep_time = first_segment.get("departure_airport", {}).get("time", "N/A")
        dep_code = first_segment.get("departure_airport", {}).get("id", "???")
        
        # Arrival: Last segment arrival
        arr_time = last_segment.get("arrival_airport", {}).get("time", "N/A")
        arr_code = last_segment.get("arrival_airport", {}).get("id", "???")
        
        # 2. Transit / Layover Info
        transit_details = []
        layovers = flight.get("layovers", [])
        if layovers:
            for lo in layovers:
                name = lo.get("name", "Unknown").replace(" International Airport", "").replace(" Airport", "").replace(" International", "")
                dur = lo.get("duration", 0)
                dur_str = f"{dur//60}h {dur%60}m" if dur >= 60 else f"{dur}m"
                transit_details.append(f"{name} ({dur_str})")
        elif len(segments) > 1:
            for j in range(len(segments) - 1):
                stop_airport = segments[j].get("arrival_airport", {})
                city = stop_airport.get("name", "Unknown City").replace(" International Airport", "").replace(" Airport", "").replace(" International", "")
                code = stop_airport.get("id", "")
                transit_details.append(f"{city} ({code})")
        
        transit_str = ", ".join(transit_details) if transit_details else "Direct / Non-stop"
            
        # 3. Flight Legs Details (Airline + Flight Num for each leg)
        legs_info = []
        for seg in segments:
            airline = seg.get("airline", "Unknown")
            flight_no = seg.get("flight_number", "")
            legs_info.append(f"{airline} {flight_no}")
        
        legs_str = " + ".join(legs_info)

        # Marketing carrier usually from first leg
        marketing_airline = first_segment.get("airline", "Unknown")

        formatted_flights.append({
            "airline": marketing_airline,
            "flight_numbers": legs_str,
            "price": str(flight.get("price", "N/A")),
            "total_duration": f"{flight.get('total_duration', 'N/A')} min",
            "stops": len(segments) - 1,
            "transit_cities": transit_str,
            "departure": f"{dep_time} ({dep_code})",
            "arrival": f"{arr_time} ({arr_code})",
            "type": "Round Trip" if "return_date" in search_results.get("search_parameters", {}) else "One Way",
            "category": "best" if i < len(best_flights) else "other",
            "airline_logo": first_segment.get("airline_logo", "")
        })
    
    logger.info(f"Returning {len(formatted_flights)} formatted flights")
    return formatted_flights 
