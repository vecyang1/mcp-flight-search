"""
AeroDataBox API Service via RapidAPI.
Provides:
- Real-time Flight Status & Delays by Flight Number/Callsign (Terminals, Gates, Baggage, Actual vs Scheduled)
- Live Airport FIDS Flight Boards (Arrivals & Departures)
- Airport Technical Info & METAR Weather
- Quota Guard (Local caching + 1 req/s rate limiter for 600 monthly unit allowance)
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from mcp_flight_search.utils.aerodatabox_resolver import resolve_aerodatabox_key
from mcp_flight_search.utils.airports import resolve_airport

AERODATABOX_HOST = "aerodatabox.p.rapidapi.com"
AERODATABOX_BASE_URL = f"https://{AERODATABOX_HOST}"
CACHE_FILE = Path.home() / ".cache" / "mcp_flight_search" / "aerodatabox_cache.json"

# Last request timestamp for 1 req/s rate-limiting
_LAST_REQUEST_TIME = 0.0


def _rate_limit_throttle(min_interval: float = 1.0):
    """Enforce 1 request per second rate limit."""
    global _LAST_REQUEST_TIME
    elapsed = time.time() - _LAST_REQUEST_TIME
    if elapsed < min_interval:
        time.sleep(min_interval - elapsed)
    _LAST_REQUEST_TIME = time.time()


class AeroDataBoxClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key, self.key_source = resolve_aerodatabox_key(api_key)

    def _get_cache(self, key: str, max_age_seconds: int) -> Optional[Any]:
        """Read from local file cache if within TTL."""
        if not CACHE_FILE.is_file():
            return None
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                entry = data.get(key)
                if entry and (time.time() - entry.get("timestamp", 0)) < max_age_seconds:
                    return entry.get("data")
        except Exception:
            pass
        return None

    def _set_cache(self, key: str, data: Any):
        """Write entry to local file cache."""
        try:
            CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
            cache_data = {}
            if CACHE_FILE.is_file():
                try:
                    with open(CACHE_FILE, "r", encoding="utf-8") as f:
                        cache_data = json.load(f)
                except Exception:
                    cache_data = {}
            cache_data[key] = {
                "timestamp": time.time(),
                "data": data,
            }
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
        cache_ttl_seconds: int = 900,  # 15 mins default
    ) -> Any:
        """
        Execute API request against AeroDataBox with caching and rate-limiting.
        """
        if not self.api_key:
            raise RuntimeError(
                "AeroDataBox RapidAPI key not found. "
                "Ensure it is in 1Password ('op://Agent Automation/4yoyezeykzvblmlu7kc3pce3pm/credential'), "
                "or set AERODATABOX_API_KEY / RAPIDAPI_KEY in environment or .env."
            )

        clean_endpoint = endpoint.lstrip("/")
        cache_key = f"{clean_endpoint}?{urllib.parse.urlencode(params or {})}"

        if use_cache:
            cached_val = self._get_cache(cache_key, cache_ttl_seconds)
            if cached_val is not None:
                return cached_val

        _rate_limit_throttle(1.0)

        url = f"{AERODATABOX_BASE_URL}/{clean_endpoint}"
        if params:
            clean_params = {k: str(v) for k, v in params.items() if v is not None}
            if clean_params:
                url += "?" + urllib.parse.urlencode(clean_params)

        headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": AERODATABOX_HOST,
            "Accept": "application/json",
            "User-Agent": "mcp-flight-search/2.0 (AeroDataBoxClient)",
        }

        req = urllib.request.Request(url, headers=headers, method="GET")

        try:
            with urllib.request.urlopen(req, timeout=12.0) as resp:
                if resp.status == 204:
                    return []
                body = resp.read().decode("utf-8")
                parsed = json.loads(body) if body else {}
                if use_cache and parsed:
                    self._set_cache(cache_key, parsed)
                return parsed
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            if e.code == 404:
                return [] if "/flights/" in endpoint else {}
            elif e.code == 429:
                raise RuntimeError(
                    f"AeroDataBox RapidAPI Rate Limit or Monthly Quota (600 Units) exceeded: {err_body}"
                )
            elif e.code in (401, 403):
                raise RuntimeError(
                    f"AeroDataBox RapidAPI Auth Failed (HTTP {e.code}): {err_body}. Check API key in 1Password."
                )
            else:
                raise RuntimeError(f"AeroDataBox API Error (HTTP {e.code}): {err_body}")
        except Exception as ex:
            raise RuntimeError(f"Failed to connect to AeroDataBox: {ex}")


def get_flight_status(
    flight_number: str,
    date: Optional[str] = None,
    use_cache: bool = True,
) -> List[Dict[str, Any]]:
    """
    Retrieve real-time commercial flight status, terminals, gates, delays, and baggage info.
    :param flight_number: Airline flight number (e.g. 'VN123', 'CA981', 'AF123')
    :param date: Flight date in YYYY-MM-DD (defaults to today UTC)
    """
    clean_fn = re.sub(r"\s+", "", flight_number).upper()
    if not date:
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    client = AeroDataBoxClient()
    endpoint = f"flights/number/{clean_fn}/{date}"
    raw_data = client.request(endpoint, use_cache=use_cache, cache_ttl_seconds=600)  # 10 min cache

    if not raw_data:
        # Fallback to callsign endpoint if number returned nothing
        try:
            raw_data = client.request(f"flights/callsign/{clean_fn}", use_cache=use_cache, cache_ttl_seconds=600)
        except Exception:
            raw_data = []

    if isinstance(raw_data, dict):
        raw_data = [raw_data]

    results = []
    for f in raw_data or []:
        dep = f.get("departure") or {}
        arr = f.get("arrival") or {}
        dep_apt = dep.get("airport") or {}
        arr_apt = arr.get("airport") or {}
        airline = f.get("airline") or {}
        aircraft = f.get("aircraft") or {}

        dep_sched = (dep.get("scheduledTime") or {}).get("local") or (dep.get("scheduledTime") or {}).get("utc")
        dep_actual = (dep.get("actualTime") or {}).get("local") or (dep.get("revisedTime") or {}).get("local")
        arr_sched = (arr.get("scheduledTime") or {}).get("local") or (arr.get("scheduledTime") or {}).get("utc")
        arr_actual = (arr.get("actualTime") or {}).get("local") or (arr.get("revisedTime") or {}).get("local")

        results.append({
            "flight_number": f.get("number") or clean_fn,
            "callsign": f.get("callSign") or f.get("callsign"),
            "status": f.get("status", "Unknown"),
            "airline": airline.get("name"),
            "aircraft_model": aircraft.get("model"),
            "aircraft_reg": aircraft.get("reg"),
            "departure": {
                "iata": dep_apt.get("iata"),
                "icao": dep_apt.get("icao"),
                "airport": dep_apt.get("name"),
                "city": dep_apt.get("municipalityName"),
                "terminal": dep.get("terminal"),
                "gate": dep.get("gate"),
                "checkin_desk": dep.get("checkInDesk"),
                "scheduled": dep_sched,
                "actual_or_revised": dep_actual,
                "delay_minutes": dep.get("delay"),
            },
            "arrival": {
                "iata": arr_apt.get("iata"),
                "icao": arr_apt.get("icao"),
                "airport": arr_apt.get("name"),
                "city": arr_apt.get("municipalityName"),
                "terminal": arr.get("terminal"),
                "gate": arr.get("gate"),
                "baggage_belt": arr.get("baggageBelt"),
                "scheduled": arr_sched,
                "actual_or_revised": arr_actual,
                "delay_minutes": arr.get("delay"),
            },
        })
    return results


def get_airport_fids(
    airport_code: str,
    direction: str = "arrivals",  # "arrivals", "departures", or "both"
    hours: int = 6,
    use_cache: bool = True,
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Retrieve live Flight Information Display System (FIDS) board for an airport.
    """
    resolved_code = resolve_airport(airport_code)
    client = AeroDataBoxClient()

    now_utc = datetime.now(timezone.utc)
    from_local = now_utc.strftime("%Y-%m-%dT%H:%M")
    to_local = (now_utc + timedelta(hours=min(hours, 12))).strftime("%Y-%m-%dT%H:%M")

    # Determine whether to query IATA (3-letter) or ICAO (4-letter)
    is_icao = len(resolved_code) == 4
    ep_prefix = "icao" if is_icao else "iata"
    endpoint = f"flights/airports/{ep_prefix}/{resolved_code}/{from_local}/{to_local}"

    dir_param = "Both"
    if direction.lower().startswith("arr"):
        dir_param = "Arrival"
    elif direction.lower().startswith("dep"):
        dir_param = "Departure"

    params = {
        "direction": dir_param,
        "withCancelled": "true",
        "withCargo": "false",
    }

    raw = client.request(endpoint, params=params, use_cache=use_cache, cache_ttl_seconds=900)
    arrivals_list = []
    departures_list = []

    for a in (raw.get("arrivals") or []):
        dep = a.get("departure") or {}
        arr = a.get("arrival") or {}
        dep_apt = dep.get("airport") or {}
        airline = a.get("airline") or {}
        arrivals_list.append({
            "flight_number": a.get("number"),
            "airline": airline.get("name"),
            "origin": dep_apt.get("iata") or dep_apt.get("name"),
            "scheduled": (arr.get("scheduledTime") or {}).get("local"),
            "actual": (arr.get("actualTime") or {}).get("local") or (arr.get("revisedTime") or {}).get("local"),
            "terminal": arr.get("terminal"),
            "gate": arr.get("gate"),
            "baggage_belt": arr.get("baggageBelt"),
            "status": a.get("status"),
        })

    for d in (raw.get("departures") or []):
        dep = d.get("departure") or {}
        arr = d.get("arrival") or {}
        arr_apt = arr.get("airport") or {}
        airline = d.get("airline") or {}
        departures_list.append({
            "flight_number": d.get("number"),
            "airline": airline.get("name"),
            "destination": arr_apt.get("iata") or arr_apt.get("name"),
            "scheduled": (dep.get("scheduledTime") or {}).get("local"),
            "actual": (dep.get("actualTime") or {}).get("local") or (dep.get("revisedTime") or {}).get("local"),
            "terminal": dep.get("terminal"),
            "gate": dep.get("gate"),
            "status": d.get("status"),
        })

    return {
        "airport": resolved_code,
        "arrivals": arrivals_list,
        "departures": departures_list,
    }


def get_airport_info(airport_code: str, use_cache: bool = True) -> Dict[str, Any]:
    """
    Retrieve airport details (IATA, ICAO, runways, coordinates, timezone, elevation).
    """
    resolved_code = resolve_airport(airport_code)
    client = AeroDataBoxClient()
    is_icao = len(resolved_code) == 4
    ep_prefix = "icao" if is_icao else "iata"
    endpoint = f"airports/{ep_prefix}/{resolved_code}"

    raw = client.request(endpoint, use_cache=use_cache, cache_ttl_seconds=86400)  # 24h cache
    return {
        "iata": raw.get("iata"),
        "icao": raw.get("icao"),
        "name": raw.get("name"),
        "city": raw.get("municipalityName"),
        "country": (raw.get("country") or {}).get("name") if isinstance(raw.get("country"), dict) else raw.get("country"),
        "continent": raw.get("continent"),
        "elevation_ft": (raw.get("elevation") or {}).get("feet") if isinstance(raw.get("elevation"), dict) else raw.get("elevation"),
        "timezone": raw.get("timeZone"),
        "location": raw.get("location"),
        "runway_count": len(raw.get("runways") or []),
    }
