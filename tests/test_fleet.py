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
        self.fleet = FleetManager({("P2.5", "INDOOR"): self.rate})

    def test_competing_for_last_cabinets(self):
        ok1, _, _ = self.fleet.check_and_reserve(req("A", "2026-10-20", 2, 6), 6)
        ok2, dates, shortfall = self.fleet.check_and_reserve(req("B", "2026-10-20", 2, 5), 5)
        self.assertTrue(ok1)
        self.assertFalse(ok2)
        self.assertIn("2026-10-20", dates)
        self.assertIn("1", shortfall)

    def test_failed_multiday_request_reserves_nothing(self):
        # Capacity 10; reserve 6 cabinets only on the second date.
        self.fleet.check_and_reserve(req("A", "2026-10-21", 1, 6), 6)
        # This request needs 5 cabinets on both days, fails on day 2.
        ok, _, _ = self.fleet.check_and_reserve(req("B", "2026-10-20", 2, 5), 5)
        self.assertFalse(ok)
        # It must not reserve day 1. A 5-cabinet booking can still be accepted there.
        ok2, _, _ = self.fleet.check_and_reserve(req("C", "2026-10-20", 1, 5), 5)
        self.assertTrue(ok2)

    def test_different_dates_do_not_conflict(self):
        self.assertTrue(self.fleet.check_and_reserve(req("A", "2026-10-20", 1, 10), 10)[0])
        self.assertTrue(self.fleet.check_and_reserve(req("B", "2026-10-21", 1, 10), 10)[0])


if __name__ == "__main__":
    unittest.main()
