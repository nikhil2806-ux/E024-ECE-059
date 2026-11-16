import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]

class OfficialPackTests(unittest.TestCase):
    def test_official_outputs_and_planted_scenarios(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "output"
            subprocess.run([sys.executable, "main.py", "--output", str(out)], cwd=PROJECT, check=True, capture_output=True, text=True)
            with (out / "quotations.csv").open(newline="", encoding="utf-8") as f:
                rows = {r["request_id"]: r for r in csv.DictReader(f)}
            with (out / "fleet_usage.csv").open(newline="", encoding="utf-8") as f:
                fleet = list(csv.DictReader(f))

            self.assertEqual(len(rows), 30)
            self.assertEqual(list(rows[next(iter(rows))].keys()), [
                "request_id", "pitch", "cabinets", "billable_sqft",
                "rental_gross_rs", "multiday_discount_rs", "setup_rs",
                "transport_rs", "generator_rs", "operator_rs", "subtotal_rs",
                "gst_rs", "total_rs", "availability", "shortfall_cabinets",
            ])
            self.assertTrue(all(r["availability"] in {"AVAILABLE", "UNAVAILABLE"} for r in rows.values()))
            for row in rows.values():
                for field in ("rental_gross_rs", "multiday_discount_rs", "setup_rs",
                              "transport_rs", "generator_rs", "operator_rs",
                              "subtotal_rs", "gst_rs", "total_rs"):
                    self.assertTrue(row[field].lstrip("-").isdigit(), (row["request_id"], field, row[field]))
            self.assertEqual(rows["EVR-002"]["cabinets"], "25")
            self.assertEqual(rows["EVR-002"]["setup_rs"], "4000")
            self.assertEqual(rows["EVR-003"]["billable_sqft"], "300.0")
            self.assertEqual(rows["EVR-003"]["transport_rs"], "2070")
            self.assertEqual(rows["EVR-004"]["multiday_discount_rs"], "1944")
            self.assertEqual(rows["EVR-007"]["transport_rs"], "0")
            self.assertEqual(rows["EVR-021"]["transport_rs"], "90")
            self.assertEqual(rows["EVR-025"]["availability"], "AVAILABLE")
            self.assertEqual(rows["EVR-026"]["availability"], "UNAVAILABLE")
            self.assertEqual(rows["EVR-026"]["shortfall_cabinets"], "6")
            self.assertEqual(rows["EVR-027"]["cabinets"], "24")
            self.assertEqual(rows["EVR-014"]["transport_rs"], "4680")
            self.assertEqual(rows["EVR-023"]["operator_rs"], "1500")
            self.assertEqual(rows["EVR-028"]["operator_rs"], "3000")
            self.assertEqual(len(fleet), 305)
            self.assertEqual(list(fleet[0].keys()), ["date", "pitch", "cabinets_held", "fleet_cabinets", "free_cabinets"])
            self.assertTrue(all(int(r["cabinets_held"]) + int(r["free_cabinets"]) == int(r["fleet_cabinets"]) for r in fleet))
            self.assertEqual(fleet[0]["date"], "2026-11-01")
            self.assertEqual(fleet[-1]["date"], "2026-12-31")
            dec12 = next(r for r in fleet if r["date"] == "2026-12-12" and r["pitch"] == "P2.5")
            self.assertEqual(dec12["cabinets_held"], "120")

if __name__ == "__main__":
    unittest.main()
