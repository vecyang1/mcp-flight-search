"""
File-based cache layer for SerpAPI Google Flights queries.
Reduces API costs and avoids duplicate requests for the same flight search.
"""
import os
import json
import time
import hashlib
from typing import Optional, Any, Dict
from mcp_flight_search.utils.logging import logger

CACHE_DIR = os.path.expanduser("~/.cache/mcp_flight_search")
CACHE_FILE = os.path.join(CACHE_DIR, "flight_cache.json")
DEFAULT_TTL_SECONDS = 7200  # 2 hours

def _ensure_cache_dir():
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
    except Exception as e:
        logger.debug(f"Failed to create cache dir {CACHE_DIR}: {e}")

def make_cache_key(origin: str, destination: str, outbound_date: str, return_date: Optional[str] = None, currency: str = "USD") -> str:
    raw = f"{origin.upper()}_{destination.upper()}_{outbound_date}_{return_date or 'NONE'}_{currency.upper()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

def load_cache() -> Dict[str, Any]:
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.debug(f"Failed to read cache file: {e}")
        return {}

def save_cache(cache: Dict[str, Any]):
    _ensure_cache_dir()
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.debug(f"Failed to write cache file: {e}")

def get_cached_flight_search(cache_key: str, max_age_seconds: int = DEFAULT_TTL_SECONDS) -> Optional[Dict[str, Any]]:
    cache = load_cache()
    entry = cache.get(cache_key)
    if not entry:
        return None
    
    timestamp = entry.get("timestamp", 0)
    if time.time() - timestamp > max_age_seconds:
        return None
    
    logger.info(f"⚡ Cache hit for key {cache_key} (age: {int(time.time() - timestamp)}s)")
    return entry.get("data")

def set_cached_flight_search(cache_key: str, data: Any):
    cache = load_cache()
    # Prune old cache entries if cache is growing too large (> 500 entries)
    if len(cache) > 500:
        now = time.time()
        cache = {k: v for k, v in cache.items() if now - v.get("timestamp", 0) < DEFAULT_TTL_SECONDS * 3}
    
    cache[cache_key] = {
        "timestamp": time.time(),
        "data": data
    }
    save_cache(cache)
