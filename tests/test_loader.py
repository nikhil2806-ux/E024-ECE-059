import tempfile
import unittest
from pathlib import Path
from src.loader import load_rate_card, load_event_requests, InputDataError

RATE_HEADER = "pitch,environment,rate_per_sqft_day_rs,cabinet_area_sqft,fleet_cabinets\n"
REQUEST_HEADER = "request_id,received_date,client,event_name,venue,wall_width_ft,wall_height_ft,pitch,start_date,days,distance_km,power_source\n"

class LoaderTests(unittest.TestCase):
    def test_valid_rate_card(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "rates.csv"
            p.write_text(RATE_HEADER + "P2.5,INDOOR,38.00,4.0,120\n")
            card = load_rate_card(p)
            self.assertEqual(card["P2.5"].fleet_cabinet_count, 120)

    def test_duplicate_pitch_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "rates.csv"
            p.write_text(RATE_HEADER + "P2.5,INDOOR,38,4,120\nP2.5,OUTDOOR,40,6,100\n")
            with self.assertRaises(InputDataError):
                load_rate_card(p)

    def test_invalid_event_dimensions_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            rates = Path(temp) / "rates.csv"
            rates.write_text(RATE_HEADER + "P2.5,INDOOR,38,4,120\n")
            p = Path(temp) / "events.csv"
            p.write_text(REQUEST_HEADER + "EVR-001,2026-10-05,Client,Event,Venue,0,10,P2.5,2026-11-01,1,5,MAINS\n")
            with self.assertRaises(InputDataError):
                load_event_requests(p, load_rate_card(rates))

    def test_official_requests_schema_loads(self):
        project = Path(__file__).resolve().parents[1]
        card = load_rate_card(project / "rate_card.csv")
        requests = load_event_requests(project / "requests.csv", card)
        self.assertEqual(len(requests), 30)
        self.assertEqual(requests[0].request_id, "EVR-001")
        self.assertEqual(requests[-1].request_id, "EVR-030")

    def test_missing_received_date_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            rates = Path(temp) / "rates.csv"
            rates.write_text(RATE_HEADER + "P2.5,INDOOR,38,4,120\n")
            p = Path(temp) / "events.csv"
            p.write_text("request_id,client,event_name,venue,wall_width_ft,wall_height_ft,pitch,start_date,days,distance_km,power_source\n"
                         "EVR-001,Client,Event,Venue,10,10,P2.5,2026-11-01,1,5,MAINS\n")
            with self.assertRaisesRegex(InputDataError, "received_date"):
                load_event_requests(p, load_rate_card(rates))

    def test_non_integer_distance_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            rates = Path(temp) / "rates.csv"
            rates.write_text(RATE_HEADER + "P2.5,INDOOR,38,4,120\n")
            p = Path(temp) / "events.csv"
            p.write_text(REQUEST_HEADER + "EVR-001,2026-10-05,Client,Event,Venue,10,10,P2.5,2026-11-01,1,5.5,MAINS\n")
            with self.assertRaisesRegex(InputDataError, "distance_km"):
                load_event_requests(p, load_rate_card(rates))

if __name__ == "__main__":
    unittest.main()
