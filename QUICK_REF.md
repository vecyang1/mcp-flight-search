# Flight Search Skill - Quick Reference

## Quick CLI Usage

```bash
# Basic single-date search (supports IATA codes or city names)
python3 ~/.gemini/antigravity/skills/mcp-flight-search/flight_search.py HAN KWL 2026-09-02
python3 ~/.gemini/antigravity/skills/mcp-flight-search/flight_search.py 河内 桂林 2026-09-02 --currency CNY

# Multi-day search (scans N days, finds cheapest per day)
python3 ~/.gemini/antigravity/skills/mcp-flight-search/flight_search.py 河内 广州 2026-09-01 --days 7 --currency CNY

# Round trip
python3 ~/.gemini/antigravity/skills/mcp-flight-search/flight_search.py SGN CAN 2026-09-10 --return-date 2026-09-20

# Force live query (skip cache)
python3 ~/.gemini/antigravity/skills/mcp-flight-search/flight_search.py HAN BKK 2026-09-05 --no-cache
```

## Features

1. **City Name Auto-Resolution**: Pass `河内`, `桂林`, `广州`, `Hanoi`, `Bangkok`, etc. directly.
2. **Built-in Smart Caching**: Results cached in `~/.cache/mcp_flight_search/` for 2 hours.
3. **Ground/Rail Alternatives**: Auto-suggests high-speed rail/buses for corridors where flying is inefficient.
4. **Full Tier Parsing**: Ingests both `best_flights` and `other_flights` + exact layover duration.

## Test Verification

```bash
cd ~/.gemini/antigravity/skills/mcp-flight-search
uv run python3 -m unittest discover -s tests
```
