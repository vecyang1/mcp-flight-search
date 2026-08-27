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

### 1. Installation

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
# Search by IATA code or City Name (English / Chinese)
python3 flight_search.py HAN KWL 2026-09-02
python3 flight_search.py 河内 桂林 2026-09-02 --currency CNY

# Multi-day price trend scan (finds daily lowest across N days)
python3 flight_search.py 河内 广州 2026-09-01 --days 7 --currency CNY

# Round-trip flight search
python3 flight_search.py SGN CAN 2026-09-10 --return-date 2026-09-20 --currency CNY

# Force live query (bypass local cache)
python3 flight_search.py HAN BKK 2026-09-05 --no-cache

# Export to CSV or JSON
python3 flight_search.py SGN HND 2026-09-15 --format csv --output-file tokyo_flights.csv
```

### Example Terminal Output

```text
🔍 Route: 河内 (HAN) -> 桂林 (KWL) | 1 date(s)
Date         Price      Airline            Dep/Arr                             Dur      Stops                   
------------------------------------------------------------------------------------------------------------------
2026-09-02   873        Shandong           2026-09-02 02:20 -> 2026-09-02 17:50 14h 30m  Jinan Yaoqiang (8h 40m) 
2026-09-02   2105       Shenzhen           2026-09-02 15:05 -> 2026-09-03 15:40 23h 35m  Shenzhen Bao'an (3h 40m)
2026-09-02   2165       Shenzhen           2026-09-02 15:05 -> 2026-09-03 12:05 20h 0m   Shenzhen Bao'an (3h 15m)
------------------------------------------------------------------------------------------------------------------
✨ Cheapest: 2026-09-02 at 873 (Shandong)

💡 陆路/高铁优选建议：河内 ➔ 桂林直飞较少，转机需14~17小时(约¥850~2000+)。更优方案为【陆路大巴过友谊关至南宁(约4~5h, ¥150~200)】+【南宁东高铁至桂林(2h, ¥108)】，全程约6~7小时，总花费仅约¥260~330($40左右)，省时又省钱。
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
   - `origin` *(string)*: Departure airport code or city name (e.g. `HAN`, `Hanoi`, `河内`)
   - `destination` *(string)*: Arrival airport code or city name (e.g. `KWL`, `Guilin`, `桂林`)
   - `outbound_date` *(string)*: Departure date (`YYYY-MM-DD`)
   - `return_date` *(string, optional)*: Return date for round trips (`YYYY-MM-DD`)
   - `currency` *(string, default "USD")*: ISO 4217 currency code (`USD`, `CNY`, `EUR`, etc.)
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
    flights = await search_flights("河内", "桂林", "2026-09-02", currency="CNY")
    for f in flights[:3]:
        print(f"{f['airline']} | {f['price']} | {f['departure']} -> {f['arrival']} | Stops: {f['transit_cities']}")
        
    tip = get_ground_alternative("HAN", "KWL")
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
