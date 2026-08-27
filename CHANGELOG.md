# Changelog

## [Unreleased]
- **Relicense to AGPL-3.0**: Switched project license to GNU Affero General Public License v3.0 (AGPL-3.0) for stronger open-source copyleft protection across network services.
- **AeroDataBox Integration**: Unified live commercial flight status, terminals, gates, baggage claim belts, and delay minutes by flight number (`python3 flight_search.py status <FLIGHT_NUMBER>`).
- **Airport FIDS Flight Boards**: Added real-time airport arrival and departure boards with `--direction` and `--hours` filters (`python3 flight_search.py fids <AIRPORT_CODE>`).
- **Airport Metadata & Weather**: Added airport technical details, runways, and timezone (`python3 flight_search.py airport <AIRPORT_CODE>`).
- **1Password Resolver**: Automated resolution of AeroDataBox key from `op://Agent Automation/4yoyezeykzvblmlu7kc3pce3pm/credential`.
- **Quota Guard & Throttling**: Added 1 req/s rate limiter and local disk caching in `~/.cache/mcp_flight_search/aerodatabox_cache.json` to safeguard 600 monthly unit allowance.
- **FastMCP Extension**: Added `flight_status_tool`, `airport_fids_tool`, `airport_info_tool` to FastMCP server.
- **Bug Fix & Coverage**: Parsed both `best_flights` and `other_flights` from SerpAPI response so routes without `best_flights` (or regional carriers) are not omitted.
- **Data Enrichment**: Extracted exact layover durations from SerpAPI's `layovers` array into flight results.
- **Multi-Currency Robustness**: Upgraded price parsing to use regex numeric extraction, supporting any currency (`CNY`, `USD`, `EUR`, `VND`, etc.) without crash.
- **Single-Date Query Mode**: Single date searches now return all available flights for comparison rather than collapsing into a single option.
- **Python Compatibility**: Updated `requires-python` in `pyproject.toml` to `>=3.10` to satisfy `fastmcp` requirements in modern environments.
- Redacted API credentials from SerpAPI debug logs; request logs now retain only non-sensitive search metadata.
- Made the CLI's `--currency` option reach the SerpAPI request instead of always returning USD.
- Restored the `.agents` alias to this canonical owner and normalized the skill identifier to `mcp-flight-search` so discovery validation passes.
- Refactored `flight_search.py` to remove hardcoded fallback API key. Now strictly checks `.env` or environment variables.
- Moved one-off search scripts (`search_*.py`) to `examples/` directory to declutter root.
- Updated `auto_update.sh` to use dynamic paths for portability.
- Added `scripts/setup.py` to auto-generate `.mcp.json` with correct local paths.
- Updated `SKILL.md` to remove hardcoded paths and reflect new structure.
- **Autopoiesis**: Injected "Self-Evolution Protocol" to enforce continuous improvement.
