---
name: mcp-flight-search
description: Global flight pricing & schedule search (Google Flights SerpAPI), live flight status & delay tracking (AeroDataBox: gates, terminals, baggage belts), airport FIDS flight boards, airport info/METAR, and ground rail alternatives.
---

# Flight Search & Aviation Intelligence Skill (`mcp-flight-search`)

Comprehensive aviation and flight intelligence suite integrating **SerpAPI Google Flights** (airfare pricing & schedules), **AeroDataBox** (live commercial flight status, terminals, gates, baggage claim, delay minutes, and airport FIDS boards), and **ground high-speed rail alternative advice**.

## Quick Commands

```bash
# Navigate to skill directory
cd ~/.gemini/antigravity/skills/mcp-flight-search

# ==========================================
# 1. Google Flights Price & Itinerary Search
# ==========================================
# One-way by airport code or city name (English/Chinese)
python3 flight_search.py HAN KWL 2026-09-02
python3 flight_search.py 河内 桂林 2026-09-02 --currency CNY

# Multi-day price trend (scans range, picks daily lowest)
python3 flight_search.py 河内 广州 2026-09-01 --days 7 --currency CNY

# Round trip
python3 flight_search.py SGN CAN 2026-09-10 --return-date 2026-09-20 --currency CNY

# ==========================================
# 2. AeroDataBox Live Flight Status & Delays
# ==========================================
# Query flight by number: terminal, gate, baggage belt, actual vs scheduled times, delays
python3 flight_search.py status VN123 2026-08-27
python3 flight_search.py status CA981 --format json

# ==========================================
# 3. Airport FIDS Live Flight Boards
# ==========================================
# Query airport arrivals or departures board (next 6 hours)
python3 flight_search.py fids HAN --direction arrival --hours 6
python3 flight_search.py fids SGN --direction departure

# ==========================================
# 4. Airport Technical Info & Geography
# ==========================================
python3 flight_search.py airport HAN
python3 flight_search.py airport PVG
```

## Features & Architectural Safeguards

- **Multi-Modal Aviation Suite**: Combines commercial airfare search (SerpAPI), live flight ops / gate / delay tracking (AeroDataBox), and real-time aircraft physics telemetry (`opensky-network-cli`).
- **1Password Integration**: Resolves credentials seamlessly via 1Password:
  - SerpAPI: `.env` / environment variable `SERP_API_KEY`
  - AeroDataBox: `op://Agent Automation/4yoyezeykzvblmlu7kc3pce3pm/credential` (RapidAPI)
- **Quota Protection & Rate Limiting**:
  - SerpAPI: 2-hour local caching in `~/.cache/mcp_flight_search/flight_cache.json`.
  - AeroDataBox: Local file caching in `~/.cache/mcp_flight_search/aerodatabox_cache.json` (15m status, 24h airport info) + strict 1 req/s throttling to safeguard the 600 monthly unit allowance.
- **FastMCP Server**: Exposes 4 tools for AI Agents:
  - `search_flights_tool(origin, destination, outbound_date, ...)`
  - `flight_status_tool(flight_number, date)`
  - `airport_fids_tool(airport_code, direction, hours)`
  - `airport_info_tool(airport_code)`
  - `ground_alternative_tool(origin, destination)`

## Python / Service Usage

```python
import asyncio
from mcp_flight_search.services.search_service import search_flights
from mcp_flight_search.services.aerodatabox_service import get_flight_status, get_airport_fids

async def example():
    # 1. Search flight price
    flights = await search_flights("河内", "桂林", "2026-09-02", currency="CNY")
    print(f"Found {len(flights)} flights. Cheapest: {flights[0]['price']}")

    # 2. Check live flight status
    status = get_flight_status("VN123", "2026-08-27")
    if status:
        f = status[0]
        print(f"Status: {f['status']} | Gate: {f['departure']['gate']} -> {f['arrival']['gate']}")

asyncio.run(example())
```

## Verification

```bash
cd ~/.gemini/antigravity/skills/mcp-flight-search
uv run python3 -m unittest discover -s tests
```

## 🌐 2nd Brain Travel Ecosystem Workflow

| Stage | Tool / Skill | Route | Capability |
| :--- | :--- | :--- | :--- |
| **1. Flight Search & Airfare** | `mcp-flight-search` | `~/.gemini/antigravity/skills/mcp-flight-search` | Commercial airfare trends, schedules, rail alternatives |
| **2. Flight Ops & Gate Tracking**| `mcp-flight-search` (`status` / `fids`) | `~/.gemini/antigravity/skills/mcp-flight-search` | Live delays, terminals, gates, baggage claim, airport flight boards |
| **3. Aircraft Radar Telemetry** | `opensky-network-cli` | `~/.gemini/antigravity/skills/opensky-network-cli` | ADS-B live physics radar (lat/lon, altitude, speed, squawk) |
| **4. Hotel & Accommodation** | `agoda-orders-cli` / `agoda-price-tracker` | `{A_CODING}/26.06.15-agoda-orders-cli` | Hotel booking records, pricing intelligence |
| **5. Activities & Tours** | `activity-intel-cli` | `{A_CODING}/26.08.26-activity-intel-cli` | Bookable experiences, Klook tours, Airbnb Experiences |

## 🧬 Self-Evolution (Autopoiesis)

**Post-Task Reflection**: 
Before ending the session, the Agent MUST ask: "Did I learn a new pattern, fix a bug, or add a critical feature?"
- **YES**: Log it in `CHANGELOG.md` and update `SKILL.md` / `references/` immediately.
- **NO**: Do nothing.
- **Constraint**: Only log **High-Signal** improvements. Ignore noise.
