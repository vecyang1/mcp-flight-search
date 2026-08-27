# Changelog

## [Unreleased]
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
