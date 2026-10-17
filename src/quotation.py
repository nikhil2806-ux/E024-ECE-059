"""Business-rule calculations for LED display rental quotations."""
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP
from math import ceil
from .models import Quotation

ZERO = Decimal("0")
ONE = Decimal("1")


def money(value):
    """Round a monetary amount to whole rupees using half-up rounding."""
    return Decimal(value).quantize(Decimal("1"), rounding=ROUND_HALF_UP)


def calculate_quotation(request, rate, fleet_manager):
    requested_area = request.width_ft * request.height_ft
    cabinets = int(ceil(requested_area / rate.cabinet_area_sq_ft))
    billable_area = Decimal(cabinets) * rate.cabinet_area_sq_ft

    # BR-04/05: apply weekend rate day by day, then the duration discount.
    rental_gross = ZERO
    for offset in range(request.days):
        day = request.start_date + timedelta(days=offset)
        multiplier = Decimal("1.25") if day.weekday() >= 5 else ONE
        rental_gross += billable_area * rate.rate_per_sq_ft_per_day * multiplier

    discount_rate = Decimal("0")
    if 4 <= request.days <= 7:
        discount_rate = Decimal("0.10")
    elif request.days >= 8:
        discount_rate = Decimal("0.20")
    rental_discount = rental_gross * discount_rate
    rental_net = rental_gross - rental_discount

    # BR-07: base setup applies through 100 sq ft, with incremental charge above.
    setup = Decimal("4000")
    if billable_area > Decimal("100"):
        setup += (billable_area - Decimal("100")) * Decimal("35")

    # BR-08: rigging is 20% of base setup for outdoor walls.
    rigging = setup * Decimal("0.20") if request.environment == "OUTDOOR" else ZERO

    # BR-09/10: excess distance is charged both ways; >300 sq ft needs 2 vehicles.
    one_vehicle_transport = Decimal("45") * max(ZERO, request.distance_km - Decimal("15")) * Decimal("2")
    vehicle_count = 2 if billable_area > Decimal("300") else 1
    transport = one_vehicle_transport * vehicle_count

    generator = Decimal("2500") * request.days if request.power_source == "GENERATOR" else ZERO
    operators_count = int(ceil(billable_area / Decimal("150")))
    operators = Decimal(operators_count * 1500 * request.days)

    # Availability is checked after calculations so unavailable requests can
    # still receive an indicative itemized quote. Failed requests reserve nothing.
    available, affected_dates, shortfall = fleet_manager.check_and_reserve(request, cabinets)

    # Proposed output policy: round each displayed line, sum rounded pre-tax lines,
    # then compute and round GST from that displayed subtotal.
    lines = {
        "rental_gross": money(rental_gross),
        "rental_discount": money(rental_discount),
        "rental_net": money(rental_net),
        "setup": money(setup),
        "rigging": money(rigging),
        "transport": money(transport),
        "generator": money(generator),
        "operators": money(operators),
    }
    pre_tax = sum((lines[k] for k in ("rental_net", "setup", "rigging", "transport", "generator", "operators")), ZERO)
    gst = money(pre_tax * Decimal("0.18"))
    grand_total = pre_tax + gst

    return Quotation(
        request_id=request.request_id,
        client=request.client,
        status="AVAILABLE" if available else "UNAVAILABLE",
        requested_area_sq_ft=requested_area,
        cabinet_count=cabinets,
        billable_area_sq_ft=billable_area,
        rental_gross=lines["rental_gross"],
        rental_discount=lines["rental_discount"],
        rental_net=lines["rental_net"],
        setup=lines["setup"],
        rigging=lines["rigging"],
        transport=lines["transport"],
        generator=lines["generator"],
        operators_count=operators_count,
        operators=lines["operators"],
        pre_tax_total=pre_tax,
        gst=gst,
        grand_total=grand_total,
        affected_dates=affected_dates,
        shortfall=shortfall,
    )
