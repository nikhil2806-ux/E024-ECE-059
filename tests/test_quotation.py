import unittest
from datetime import date
from decimal import Decimal
from src.models import RateCardEntry, EventRequest
from src.fleet import FleetManager
from src.quotation import calculate_quotation, money


def request(request_id="T", width="10", height="10", start="2026-10-23",
            days=1, distance="15", environment="INDOOR", power="MAINS", pitch="P2.5"):
    return EventRequest(request_id, "Test Client", Decimal(width), Decimal(height), pitch,
                        environment, date.fromisoformat(start), days, Decimal(distance), power)


def rate(fleet=100, cabinet_area="10", price="100", environment="INDOOR", pitch="P2.5"):
    return RateCardEntry(pitch, environment, Decimal(price), Decimal(cabinet_area), fleet)


class QuotationTests(unittest.TestCase):
    def test_cabinet_rounding_up(self):
        r = request(width="12", height="8")
        q = calculate_quotation(r, rate(cabinet_area="10"), FleetManager({("P2.5", "INDOOR"): rate(cabinet_area="10")}))
        self.assertEqual(q.cabinet_count, 10)
        self.assertEqual(q.billable_area_sq_ft, Decimal("100"))

    def test_exactly_100_setup(self):
        r = request(width="10", height="10")
        entry = rate(cabinet_area="10")
        q = calculate_quotation(r, entry, FleetManager({("P2.5", "INDOOR"): entry}))
        self.assertEqual(q.setup, Decimal("4000"))

    def test_setup_above_100(self):
        r = request(width="11", height="10")
        entry = rate(cabinet_area="1")
        q = calculate_quotation(r, entry, FleetManager({("P2.5", "INDOOR"): entry}))
        self.assertEqual(q.setup, Decimal("4350"))

    def test_exactly_300_no_second_vehicle(self):
        r = request(width="30", height="10", distance="20")
        entry = rate(cabinet_area="1")
        q = calculate_quotation(r, entry, FleetManager({("P2.5", "INDOOR"): entry}))
        self.assertEqual(q.transport, Decimal("450"))

    def test_above_300_second_vehicle(self):
        r = request(width="301", height="1", distance="20")
        entry = rate(cabinet_area="1")
        q = calculate_quotation(r, entry, FleetManager({("P2.5", "INDOOR"): entry}))
        self.assertEqual(q.transport, Decimal("900"))

    def test_15_km_transport_free(self):
        r = request(distance="15")
        entry = rate()
        q = calculate_quotation(r, entry, FleetManager({("P2.5", "INDOOR"): entry}))
        self.assertEqual(q.transport, Decimal("0"))

    def test_weekend_before_four_day_discount(self):
        # Fri 23 Oct 2026 through Mon 26 Oct 2026: Fri/Sat/Sun/Mon.
        r = request(start="2026-10-23", days=4, width="10", height="10")
        entry = rate(cabinet_area="100", price="10")
        q = calculate_quotation(r, entry, FleetManager({("P2.5", "INDOOR"): entry}))
        # 100 sq ft * 10 * (1 + 1.25 + 1.25 + 1) = 4500; 10% discount = 450.
        self.assertEqual(q.rental_gross, Decimal("4500"))
        self.assertEqual(q.rental_discount, Decimal("450"))

    def test_eight_day_discount(self):
        r = request(start="2026-10-19", days=8, width="10", height="10")
        entry = rate(cabinet_area="100", price="10")
        q = calculate_quotation(r, entry, FleetManager({("P2.5", "INDOOR"): entry}))
        self.assertEqual(q.rental_discount, money(q.rental_gross * Decimal("0.20")))

    def test_generator_charge(self):
        r = request(days=3, power="GENERATOR")
        entry = rate()
        q = calculate_quotation(r, entry, FleetManager({("P2.5", "INDOOR"): entry}))
        self.assertEqual(q.generator, Decimal("7500"))

    def test_operator_boundary_150_and_151(self):
        entry = rate(cabinet_area="1")
        q150 = calculate_quotation(request(width="150", height="1"), entry, FleetManager({("P2.5", "INDOOR"): entry}))
        q151 = calculate_quotation(request(request_id="T2", width="151", height="1"), entry, FleetManager({("P2.5", "INDOOR"): entry}))
        self.assertEqual(q150.operators_count, 1)
        self.assertEqual(q151.operators_count, 2)

    def test_outdoor_rigging(self):
        r = request(environment="OUTDOOR")
        entry = rate(environment="OUTDOOR")
        q = calculate_quotation(r, entry, FleetManager({("P2.5", "OUTDOOR"): entry}))
        self.assertEqual(q.rigging, Decimal("800"))

    def test_half_up_rounding(self):
        self.assertEqual(money(Decimal("10.5")), Decimal("11"))


if __name__ == "__main__":
    unittest.main()
