import csv
import tempfile
import unittest
from pathlib import Path
from src.loader import load_rate_card, load_event_requests, InputDataError


class LoaderTests(unittest.TestCase):
    def test_valid_rate_card(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "rates.csv"
            p.write_text("pitch,environment,rate_per_sq_ft_per_day,cabinet_area_sq_ft,fleet_cabinet_count\nP2.5,INDOOR,100,10,20\n")
            self.assertEqual(len(load_rate_card(p)), 1)

    def test_duplicate_rate_card_entry_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "rates.csv"
            p.write_text("pitch,environment,rate_per_sq_ft_per_day,cabinet_area_sq_ft,fleet_cabinet_count\nP2.5,INDOOR,100,10,20\nP2.5,INDOOR,110,10,20\n")
            with self.assertRaises(InputDataError):
                load_rate_card(p)

    def test_invalid_event_dimensions_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "events.csv"
            p.write_text("request_id,client,width_ft,height_ft,pitch,environment,start_date,days,distance_km,power_source\nE1,A,0,10,P2.5,INDOOR,2026-10-20,1,5,MAINS\n")
            with self.assertRaises(InputDataError):
                load_event_requests(p)


if __name__ == "__main__":
    unittest.main()
