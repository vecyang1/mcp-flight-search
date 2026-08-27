# MCP Flight Search (Enhanced) ✈️

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Standard](https://img.shields.io/badge/MCP-Standard-green.svg)](https://modelcontextprotocol.io/)
[![Unit Tests](https://img.shields.io/badge/tests-11%2F11%20passing-brightgreen.svg)](tests/)

An enhanced, production-ready **Model Context Protocol (MCP) Flight Search Server & CLI** powered by SerpAPI Google Flights. Designed for AI Agents (Claude Desktop, Cursor, Antigravity, Windsurf) and human travelers.

> **Note**: Forked from [`arjunprabhulal/mcp-flight-search`](https://github.com/arjunprabhulal/mcp-flight-search) with comprehensive enhancements: smart multi-language city resolution, quota-saving local caching, full flight tier aggregation, exact layover durations, ground/rail alternative advisor, and a feature-rich CLI.

---

## ✨ Key Enhancements

- 🌍 **Smart City & Airport Resolver**: Pass city names in English or Chinese (`Hanoi`, `河内`, `Guilin`, `桂林`, `Bangkok`, `曼谷`, `Tokyo`, `东京`) or standard 3-letter IATA codes (`HAN`, `KWL`, `BKK`, `TYO`). Auto-resolves 300+ major worldwide hubs.
- ⚡ **Local Response Caching**: Built-in 2-hour TTL cache (`~/.cache/mcp_flight_search/`) prevents draining SerpAPI search credits on duplicate checks. Zero latency on cache hits.
- 🛡️ **Full Flight Coverage (`best` + `other`)**: Ingests all flight tiers returned by Google Flights so regional and low-frequency airline schedules are never falsely reported as "no flights".
- ⏱️ **Exact Layover Parsing**: Extracts precise layover durations (e.g. `Xiamen Gaoqi (13h 10m)`) from SerpAPI layover metadata.
- 🚄 **Ground & High-Speed Rail Advisor**: Automatically suggests ground/rail alternatives for corridors where high-speed trains or coaches are significantly faster and cheaper than flying (e.g., Hanoi ➔ Nanning / Guilin, Shenzhen ➔ Hong Kong, Shanghai ➔ Hangzhou, Tokyo ➔ Osaka).
- 💱 **Multi-Currency Support**: Full support for any ISO 4217 currency (`USD`, `CNY`, `EUR`, `VND`, etc.) with robust regex price parsing.
- 💻 **Advanced CLI (`flight_search.py`)**: Multi-day price trend scans (`--days 7`), round-trip searches (`--return-date`), and multi-format outputs (`table`, `json`, `csv`).
- 🧪 **Offline Test Suite**: 11 unit tests ensuring zero regression across parsing, resolution, and caching.

---

## 🚀 Quick Start

### ⚡ One-Line Install via Smithery (Claude / Cursor / Windsurf)

```bash
# For Claude Desktop
npx -y @smithery/cli install @vecyang1/mcp-flight-search --client claude

# For Cursor
npx -y @smithery/cli install @vecyang1/mcp-flight-search --client cursor

# For Windsurf
npx -y @smithery/cli install @vecyang1/mcp-flight-search --client windsurf
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/vecyang1/mcp-flight-search.git
cd mcp-flight-search

# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

### 2. Configure API Key

Set your SerpAPI key via environment variable or in a local `.env` file:

```bash
export SERP_API_KEY="your_serpapi_key_here"
```

---

## 🖥️ CLI Usage (`flight_search.py`)

Search flights directly from your terminal:

```bash
# Search by Airport Code or City Name (English / Local)
python3 flight_search.py NRT BKK 2026-10-15 --currency USD
python3 flight_search.py Tokyo Bangkok 2026-10-15 --currency USD

# Multi-day price trend scan (finds daily lowest across N days)
python3 flight_search.py Tokyo Bangkok 2026-10-10 --days 7 --currency USD

# Round-trip flight search
python3 flight_search.py TYO SIN 2026-11-01 --return-date 2026-11-10 --currency USD

# Force live query (bypass local cache)
python3 flight_search.py HND BKK 2026-10-15 --no-cache

# Export to CSV or JSON
python3 flight_search.py NRT BKK 2026-10-15 --format csv --output-file tokyo_bangkok.csv
```

### Example Terminal Output

```text
🔍 Route: Tokyo (NRT) -> Bangkok (BKK) | 1 date(s)
Date         Price (USD) Airline            Dep/Arr                             Dur     Stops                   
------------------------------------------------------------------------------------------------------------------
2026-10-15   $185        Zipair             2026-10-15 09:15 -> 2026-10-15 14:10 6h 55m  Non-stop
2026-10-15   $215        AirAsia X          2026-10-15 11:30 -> 2026-10-15 16:35 7h 5m   Non-stop
2026-10-15   $295        Thai Airways       2026-10-15 12:00 -> 2026-10-15 16:50 6h 50m  Non-stop
------------------------------------------------------------------------------------------------------------------
✨ Cheapest: 2026-10-15 at $185 (Zipair, Non-stop)

💡 Ground/Rail Advisor: For regional city pairs (e.g., Tokyo ➔ Osaka, Shenzhen ➔ Hong Kong), high-speed rail options (Shinkansen bullet train / HSR) are automatically evaluated and recommended if faster and more cost-effective than flying.
```

---

## 🤖 MCP Server Configuration

To use this server with **Claude Desktop**, **Cursor**, **Windsurf**, or **Antigravity**, add it to your MCP configuration:

### Claude Desktop / Cursor Config (`claude_desktop_config.json` or `.cursor/mcp.json`)

```json
{
  "mcpServers": {
    "flight-search": {
      "command": "python3",
      "args": ["-m", "mcp_flight_search.server", "--connection_type", "stdio"],
      "cwd": "/path/to/mcp-flight-search",
      "env": {
        "SERP_API_KEY": "your_serpapi_key_here"
      }
    }
  }
}
```

### Exposed MCP Tools

1. **`search_flights_tool`**:
   - `origin` *(string)*: Departure airport code or city name (e.g. `NRT`, `Tokyo`, `HND`, `JFK`)
   - `destination` *(string)*: Arrival airport code or city name (e.g. `BKK`, `Bangkok`, `SIN`, `LHR`)
   - `outbound_date` *(string)*: Departure date (`YYYY-MM-DD`)
   - `return_date` *(string, optional)*: Return date for round trips (`YYYY-MM-DD`)
   - `currency` *(string, default "USD")*: ISO 4217 currency code (`USD`, `EUR`, `GBP`, `JPY`, `CNY`)
   - `no_cache` *(boolean, default false)*: Force live search bypassing local cache
2. **`ground_alternative_tool`**:
   - `origin` *(string)*: Origin airport or city name
   - `destination` *(string)*: Destination airport or city name
   - Returns ground/high-speed rail alternative advice when available.
3. **`server_status`**: Check health of the MCP server.

---

## 🐍 Python SDK Usage

```python
import asyncio
from mcp_flight_search.services.search_service import search_flights
from mcp_flight_search.utils.ground_alternatives import get_ground_alternative

async def main():
    # Pass city names or airport codes directly
    flights = await search_flights("Tokyo", "Bangkok", "2026-10-15", currency="USD")
    for f in flights[:3]:
        print(f"{f['airline']} | ${f['price']} | {f['departure']} -> {f['arrival']} | Stops: {f['transit_cities']}")
        
    tip = get_ground_alternative("TYO", "OSA")
    if tip:
        print(tip)

asyncio.run(main())
```

---

## 🧪 Testing

Run the offline unit test suite:

```bash
uv run python3 -m unittest discover -s tests
```

---

## 📄 License & Credits

- Original base project created by [Arjun Prabhulal](https://github.com/arjunprabhulal/mcp-flight-search).
- Enhanced & maintained by [Vec Yang](https://github.com/vecyang1).
- Licensed under the **MIT License**. See [LICENSE](LICENSE) for details.
