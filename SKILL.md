---
name: mcp-flight-search
description: Quick flight search using SerpAPI Google Flights. Real-time pricing from airlines.
---

# Flight Search Skill (`mcp-flight-search`)

Search affordable flights using SerpAPI Google Flights integration with local caching, smart city/IATA resolution, and ground travel alternatives.

## Quick Commands

```bash
# Navigate to skill directory
cd ~/.gemini/antigravity/skills/mcp-flight-search

# Basic: One-way by airport code or city name (English/Chinese)
python3 flight_search.py HAN KWL 2026-09-02
python3 flight_search.py 河内 桂林 2026-09-02 --currency CNY

# Multi-day price trend (scans range, picks daily lowest)
python3 flight_search.py 河内 广州 2026-09-01 --days 7 --currency CNY

# Round trip
python3 flight_search.py SGN CAN 2026-09-10 --return-date 2026-09-20 --currency CNY

# Bypass cache for live fetch
python3 flight_search.py HAN BKK 2026-09-05 --no-cache
```

## Features & Capabilities

- **Smart Airport & City Resolver**: Supports 3-letter IATA codes (`HAN`, `KWL`, `SGN`, `CAN`, `PVG`) as well as city names in English and Chinese (`河内`, `桂林`, `胡志明`, `广州`, `上海`, `曼谷`, `东京`, `伦敦`, etc.).
- **Automatic Caching**: Stores search results in `~/.cache/mcp_flight_search/flight_cache.json` (2-hour TTL) to prevent draining SerpAPI quota on repeated checks.
- **Full Coverage (`best_flights` + `other_flights`)**: Ingests all flight tiers so regional/low-frequency routes are never falsely reported as "no flights".
- **Exact Layover Parsing**: Shows exact layover durations (e.g. `厦门高崎 (13h 10m)`) parsed from SerpAPI layover data.
- **Ground & High-Speed Rail Alternative Advisor**: Detects cross-border and regional corridors (e.g., Hanoi ➔ Guilin / Nanning, Shenzhen ➔ Hong Kong, Shanghai ➔ Hangzhou, Tokyo ➔ Osaka) where high-speed trains or coaches are faster, cheaper, and more convenient than multi-stop flights.
- **Multi-Currency Support**: Supports any ISO 4217 currency (`CNY`, `USD`, `EUR`, `VND`, etc.) with robust regex price parsing.
- **Output Formats**:
  - `table`: Human-readable terminal table with dep/arr times, durations, stops, and travel advice.
  - `json`: Structured raw data for downstream agent processing.
  - `csv`: Exportable spreadsheet format (`--output-file flights.csv`).

## Python / Service Usage

```python
import asyncio
import sys
sys.path.insert(0, '/Users/vecsatfoxmailcom/.gemini/antigravity/skills/mcp-flight-search')
from mcp_flight_search.services.search_service import search_flights
from mcp_flight_search.utils.airports import resolve_airport
from mcp_flight_search.utils.ground_alternatives import get_ground_alternative

async def example():
    # Pass city names or airport codes directly
    flights = await search_flights("河内", "桂林", "2026-09-02", currency="CNY")
    print(f"Found {len(flights)} flights. Cheapest: {flights[0]['price']}")
    
    # Ground alternative advice
    tip = get_ground_alternative("HAN", "KWL")
    if tip:
        print(tip)

asyncio.run(example())
```

## Verification

```bash
cd ~/.gemini/antigravity/skills/mcp-flight-search
uv run python3 -m unittest discover -s tests
```

## Configuration

- **API Key**: Managed in `.env` (`SERP_API_KEY=...`) or environment variable.
- **MCP Server**: FastMCP server in `mcp_flight_search/server.py` supporting `stdio` and `sse`.

## 🧬 Self-Evolution (Autopoiesis)

**Post-Task Reflection**: 
Before ending the session, the Agent MUST ask: "Did I learn a new pattern, fix a bug, or add a critical feature?"
- **YES**: Log it in `CHANGELOG.md` and update `SKILL.md` / `references/` immediately.
- **NO**: Do nothing.
- **Constraint**: Only log **High-Signal** improvements. Ignore noise.
