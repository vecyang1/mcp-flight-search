"""
Unit tests for mcp-flight-search package.
"""
import os
import re
import unittest
from mcp_flight_search.utils.airports import resolve_airport
from mcp_flight_search.utils.cache import make_cache_key, get_cached_flight_search, set_cached_flight_search, CACHE_FILE
from mcp_flight_search.utils.ground_alternatives import get_ground_alternative
from mcp_flight_search.services.search_service import format_flight_results
from flight_search import get_date_range

class TestAirportResolver(unittest.TestCase):
    def test_iata_passthrough(self):
        self.assertEqual(resolve_airport("HAN"), "HAN")
        self.assertEqual(resolve_airport("kwl"), "KWL")
        self.assertEqual(resolve_airport("SGN"), "SGN")

    def test_city_name_resolution_english(self):
        self.assertEqual(resolve_airport("hanoi"), "HAN")
        self.assertEqual(resolve_airport("Guilin"), "KWL")
        self.assertEqual(resolve_airport("Bangkok"), "BKK")
        self.assertEqual(resolve_airport("Tokyo"), "TYO")
        self.assertEqual(resolve_airport("Shanghai"), "PVG")

    def test_city_name_resolution_chinese(self):
        self.assertEqual(resolve_airport("河内"), "HAN")
        self.assertEqual(resolve_airport("桂林"), "KWL")
        self.assertEqual(resolve_airport("胡志明"), "SGN")
        self.assertEqual(resolve_airport("南宁"), "NNG")
        self.assertEqual(resolve_airport("广州"), "CAN")
        self.assertEqual(resolve_airport("香港"), "HKG")

class TestGroundAlternatives(unittest.TestCase):
    def test_han_kwl_alternative(self):
        alt = get_ground_alternative("HAN", "KWL")
        self.assertIsNotNone(alt)
        self.assertIn("南宁", alt)

    def test_szx_hkg_alternative(self):
        alt = get_ground_alternative("SZX", "HKG")
        self.assertIsNotNone(alt)
        self.assertIn("高铁", alt)

    def test_unknown_corridor(self):
        alt = get_ground_alternative("JFK", "LAX")
        self.assertIsNone(alt)

class TestCacheLayer(unittest.TestCase):
    def test_cache_key_generation(self):
        k1 = make_cache_key("HAN", "KWL", "2026-09-02", None, "CNY")
        k2 = make_cache_key("han", "kwl", "2026-09-02", None, "cny")
        self.assertEqual(k1, k2)

    def test_cache_set_and_get(self):
        key = "test_cache_dummy_key"
        data = [{"airline": "TestAir", "price": "100"}]
        set_cached_flight_search(key, data)
        retrieved = get_cached_flight_search(key, max_age_seconds=60)
        self.assertEqual(retrieved, data)

class TestFlightFormatting(unittest.TestCase):
    def test_combine_best_and_other_flights(self):
        mock_raw = {
            "search_parameters": {"departure_id": "HAN", "arrival_id": "KWL"},
            "best_flights": [
                {
                    "price": 873,
                    "total_duration": 870,
                    "flights": [
                        {"airline": "Shandong", "flight_number": "SC8072", "departure_airport": {"id": "HAN", "time": "2026-09-02 02:20"}, "arrival_airport": {"id": "TNA", "time": "2026-09-02 06:40"}},
                        {"airline": "Shandong", "flight_number": "SC8763", "departure_airport": {"id": "TNA", "time": "2026-09-02 15:20"}, "arrival_airport": {"id": "KWL", "time": "2026-09-02 17:50"}}
                    ],
                    "layovers": [{"name": "Jinan Yaoqiang International Airport", "duration": 520}]
                }
            ],
            "other_flights": [
                {
                    "price": "¥2,105",
                    "total_duration": 1415,
                    "flights": [
                        {"airline": "Shenzhen", "flight_number": "ZH9016", "departure_airport": {"id": "HAN", "time": "2026-09-02 15:05"}, "arrival_airport": {"id": "SZX", "time": "2026-09-02 18:00"}},
                        {"airline": "Shenzhen", "flight_number": "ZH9223", "departure_airport": {"id": "SZX", "time": "2026-09-03 14:00"}, "arrival_airport": {"id": "KWL", "time": "2026-09-03 15:40"}}
                    ],
                    "layovers": [{"name": "Shenzhen Bao'an International Airport", "duration": 1200}]
                }
            ]
        }
        res = format_flight_results(mock_raw)
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0]["category"], "best")
        self.assertEqual(res[1]["category"], "other")
        self.assertIn("Jinan Yaoqiang (8h 40m)", res[0]["transit_cities"])

    def test_price_numeric_regex_extraction(self):
        cases = [
            ("¥873", 873.0),
            ("$305", 305.0),
            ("1,234.50 €", 1234.5),
            ("2,044", 2044.0),
        ]
        for raw, expected in cases:
            cleaned = re.sub(r'[^\d.]', '', raw)
            self.assertEqual(float(cleaned), expected)

class TestDateRanges(unittest.TestCase):
    def test_date_range_days(self):
        dates = get_date_range("2026-09-01", days=3, interval=1)
        self.assertEqual(dates, ["2026-09-01", "2026-09-02", "2026-09-03"])

if __name__ == "__main__":
    unittest.main()
