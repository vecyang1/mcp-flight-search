"""
Deterministic offline unit tests for AeroDataBox service, resolver, and formatting.
Requires 0 live network calls.
"""
import json
import unittest
from unittest.mock import MagicMock, patch

from mcp_flight_search.utils.aerodatabox_resolver import resolve_aerodatabox_key
from mcp_flight_search.services.aerodatabox_service import (
    AeroDataBoxClient,
    get_flight_status,
    get_airport_fids,
    get_airport_info,
)


class TestAeroDataBoxResolver(unittest.TestCase):
    def test_explicit_key(self):
        k, src = resolve_aerodatabox_key("custom_key_123")
        self.assertEqual(k, "custom_key_123")
        self.assertEqual(src, "explicit_arguments")

    @patch("mcp_flight_search.utils.aerodatabox_resolver._read_from_1password")
    def test_1password_key(self, mock_1p):
        mock_1p.return_value = "secret_1p_key"
        with patch.dict("os.environ", {}, clear=True):
            k, src = resolve_aerodatabox_key()
            self.assertEqual(k, "secret_1p_key")
            self.assertEqual(src, "1password_vault")


class TestAeroDataBoxService(unittest.TestCase):
    @patch("urllib.request.urlopen")
    def test_flight_status_parsing(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps([
            {
                "number": "VN123",
                "callSign": "HVN123",
                "status": "Active",
                "airline": {"name": "Vietnam Airlines"},
                "aircraft": {"model": "Boeing 787-9", "reg": "VN-A861"},
                "departure": {
                    "airport": {"iata": "HAN", "icao": "VVNB", "name": "Noi Bai Intl", "municipalityName": "Hanoi"},
                    "scheduledTime": {"local": "2026-08-27 08:00+07:00"},
                    "actualTime": {"local": "2026-08-27 08:15+07:00"},
                    "terminal": "T1",
                    "gate": "12",
                    "delay": 15,
                },
                "arrival": {
                    "airport": {"iata": "SGN", "icao": "VVTS", "name": "Tan Son Nhat Intl", "municipalityName": "Ho Chi Minh City"},
                    "scheduledTime": {"local": "2026-08-27 10:15+07:00"},
                    "revisedTime": {"local": "2026-08-27 10:30+07:00"},
                    "terminal": "T2",
                    "gate": "24",
                    "baggageBelt": "4",
                    "delay": 15,
                }
            }
        ]).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        with patch("mcp_flight_search.services.aerodatabox_service.resolve_aerodatabox_key", return_value=("test_key", "test")):
            results = get_flight_status("VN123", "2026-08-27", use_cache=False)
            self.assertEqual(len(results), 1)
            f = results[0]
            self.assertEqual(f["flight_number"], "VN123")
            self.assertEqual(f["status"], "Active")
            self.assertEqual(f["departure"]["terminal"], "T1")
            self.assertEqual(f["departure"]["gate"], "12")
            self.assertEqual(f["departure"]["delay_minutes"], 15)
            self.assertEqual(f["arrival"]["baggage_belt"], "4")

    @patch("urllib.request.urlopen")
    def test_airport_fids_parsing(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps({
            "arrivals": [
                {
                    "number": "CA981",
                    "airline": {"name": "Air China"},
                    "departure": {"airport": {"iata": "PEK", "name": "Beijing Capital"}},
                    "arrival": {
                        "scheduledTime": {"local": "2026-08-27 14:00+07:00"},
                        "actualTime": {"local": "2026-08-27 14:10+07:00"},
                        "terminal": "T2",
                        "gate": "30",
                        "baggageBelt": "2",
                    },
                    "status": "Expected",
                }
            ],
            "departures": [],
        }).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        with patch("mcp_flight_search.services.aerodatabox_service.resolve_aerodatabox_key", return_value=("test_key", "test")):
            fids = get_airport_fids("HAN", direction="arrivals", use_cache=False)
            self.assertEqual(fids["airport"], "HAN")
            self.assertEqual(len(fids["arrivals"]), 1)
            self.assertEqual(fids["arrivals"][0]["flight_number"], "CA981")
            self.assertEqual(fids["arrivals"][0]["gate"], "30")


if __name__ == "__main__":
    unittest.main()
