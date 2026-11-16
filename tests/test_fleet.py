import unittest
from datetime import date
from decimal import Decimal
from src.models import RateCardEntry, EventRequest
from src.fleet import FleetManager

def req(rid, start, days, width=6):
    return EventRequest(rid, rid, Decimal(width), Decimal("1"), "P2.5", "INDOOR",
                        date.fromisoformat(start), days, Decimal("0"), "MAINS")

class FleetTests(unittest.TestCase):
    def setUp(self):
        self.rate = RateCardEntry("P2.5", "INDOOR", Decimal("10"), Decimal("1"), 10)
        self.fleet = FleetManager({"P2.5": self.rate})

    def test_competing_for_last_cabinets(self):
        ok1, short1 = self.fleet.check_and_reserve(req("A", "2026-10-20", 2, 6), 6)
        ok2, short2 = self.fleet.check_and_reserve(req("B", "2026-10-20", 2, 5), 5)
        self.assertTrue(ok1)
        self.assertFalse(ok2)
        self.assertEqual(short2, 1)

    def test_failed_multiday_request_reserves_nothing(self):
        self.fleet.check_and_reserve(req("A", "2026-10-21", 1, 6), 6)
        ok, shortfall = self.fleet.check_and_reserve(req("B", "2026-10-20", 2, 5), 5)
        self.assertFalse(ok)
        self.assertEqual(shortfall, 1)
        ok2, _ = self.fleet.check_and_reserve(req("C", "2026-10-20", 1, 5), 5)
        self.assertTrue(ok2)

    def test_different_dates_do_not_conflict(self):
        self.assertTrue(self.fleet.check_and_reserve(req("A", "2026-10-20", 1, 10), 10)[0])
        self.assertTrue(self.fleet.check_and_reserve(req("B", "2026-10-21", 1, 10), 10)[0])

if __name__ == "__main__":
    unittest.main()
