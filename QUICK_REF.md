# MCP Flight Search & AeroDataBox Quick Reference

## Commands
```bash
# Flight Price Search
python3 flight_search.py HAN KWL 2026-09-02 --currency CNY
python3 flight_search.py 河内 广州 2026-09-01 --days 7 --currency CNY

# Live Flight Status (AeroDataBox)
python3 flight_search.py status VN123 2026-08-27
python3 flight_search.py status CA981 --format json

# Airport FIDS Flight Boards (AeroDataBox)
python3 flight_search.py fids HAN --direction arrival --hours 6
python3 flight_search.py fids SGN --direction departure

# Airport Details
python3 flight_search.py airport HAN
```

## MCP Server Tools
- `search_flights_tool`: Google Flights SerpAPI pricing
- `flight_status_tool`: AeroDataBox live status, delays, gates, baggage
- `airport_fids_tool`: AeroDataBox airport arrival/departure board
- `airport_info_tool`: AeroDataBox airport technical metadata
- `ground_alternative_tool`: High-speed rail / ground alternatives

## Environment & 1Password
- `SERP_API_KEY`: SerpAPI Search Key (`.env` or env var)
- `AERODATABOX_API_KEY`: 1Password `op://Agent Automation/4yoyezeykzvblmlu7kc3pce3pm/credential`
