"""Small data models used by the quotation engine."""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class RateCardEntry:
    pitch: str
    environment: str
    rate_per_sq_ft_per_day: Decimal
    cabinet_area_sq_ft: Decimal
    fleet_cabinet_count: int


@dataclass(frozen=True)
class EventRequest:
    request_id: str
    client: str
    width_ft: Decimal
    height_ft: Decimal
    pitch: str
    environment: str
    start_date: date
    days: int
    distance_km: Decimal
    power_source: str


@dataclass
class Quotation:
    request_id: str
    client: str
    status: str
    requested_area_sq_ft: Decimal
    cabinet_count: int
    billable_area_sq_ft: Decimal
    rental_gross: Decimal
    rental_discount: Decimal
    rental_net: Decimal
    setup: Decimal
    rigging: Decimal
    transport: Decimal
    generator: Decimal
    operators_count: int
    operators: Decimal
    pre_tax_total: Decimal
    gst: Decimal
    grand_total: Decimal
    affected_dates: str = ""
    shortfall: str = ""
    error_code: str = ""
    error_message: str = ""
