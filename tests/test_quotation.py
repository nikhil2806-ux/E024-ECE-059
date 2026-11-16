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

def rate(fleet=1000, cabinet_area="10", price="100", environment="INDOOR", pitch="P2.5"):
    return RateCardEntry(pitch, environment, Decimal(price), Decimal(cabinet_area), fleet)

def quote(r, entry):
    return calculate_quotation(r, entry, FleetManager({entry.pitch: entry}))

class QuotationTests(unittest.TestCase):
    def test_cabinet_rounding_up(self):
        q = quote(request(width="12", height="8"), rate(cabinet_area="10"))
        self.assertEqual(q.cabinet_count, 10)
        self.assertEqual(q.billable_area_sq_ft, Decimal("100"))

    def test_exactly_100_setup(self):
        self.assertEqual(quote(request(), rate(cabinet_area="100")).setup, Decimal("4000"))

    def test_setup_above_100(self):
        self.assertEqual(quote(request(width="11", height="10"), rate(cabinet_area="1")).setup, Decimal("4350"))

    def test_exactly_300_no_second_vehicle(self):
        q = quote(request(width="30", height="10", distance="20"), rate(cabinet_area="1"))
        self.assertEqual(q.transport, Decimal("450"))

    def test_above_300_second_vehicle(self):
        q = quote(request(width="301", height="1", distance="20"), rate(cabinet_area="1"))
        self.assertEqual(q.transport, Decimal("900"))

    def test_15_km_transport_free(self):
        self.assertEqual(quote(request(distance="15"), rate()).transport, Decimal("0"))

    def test_weekend_then_four_day_discount(self):
        q = quote(request(start="2026-10-23", days=4), rate(cabinet_area="100", price="10"))
        self.assertEqual(q.rental_gross, Decimal("4500"))
        self.assertEqual(q.rental_discount, Decimal("450"))

    def test_eight_day_discount(self):
        q = quote(request(start="2026-10-19", days=8), rate(cabinet_area="100", price="10"))
        self.assertEqual(q.rental_discount, money(q.rental_gross * Decimal("0.20")))

    def test_generator_charge(self):
        self.assertEqual(quote(request(days=3, power="GENERATOR"), rate()).generator, Decimal("7500"))

    def test_operator_boundary_150_and_151(self):
        entry = rate(cabinet_area="1")
        q150 = quote(request(width="150", height="1"), entry)
        q151 = quote(request(request_id="T2", width="151", height="1"), entry)
        self.assertEqual(q150.operators_count, 1)
        self.assertEqual(q151.operators_count, 2)

    def test_outdoor_setup_includes_20_percent(self):
        q = quote(request(environment="OUTDOOR"), rate(environment="OUTDOOR"))
        self.assertEqual(q.setup, Decimal("4800"))

    def test_half_up_rounding(self):
        self.assertEqual(money(Decimal("10.5")), Decimal("11"))

if __name__ == "__main__":
    unittest.main()
