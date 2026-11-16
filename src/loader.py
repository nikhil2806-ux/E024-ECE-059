"""CSV input loading and validation for the official ECE-059 pack."""
import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
from .models import EventRequest, RateCardEntry

class InputDataError(ValueError):
    pass

def _decimal(value, field, row_number):
    try:
        result = Decimal(str(value).strip())
    except (InvalidOperation, AttributeError):
        raise InputDataError(f"Row {row_number}: '{field}' must be a number.")
    if not result.is_finite():
        raise InputDataError(f"Row {row_number}: '{field}' must be finite.")
    return result

def _required(row, field, row_number):
    value = (row.get(field) or "").strip()
    if not value:
        raise InputDataError(f"Row {row_number}: missing required field '{field}'.")
    return value

def load_rate_card(path):
    required = {"pitch", "environment", "rate_per_sqft_day_rs", "cabinet_area_sqft", "fleet_cabinets"}
    entries = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise InputDataError(f"Rate card must contain columns: {', '.join(sorted(required))}")
        for n, row in enumerate(reader, 2):
            pitch = _required(row, "pitch", n).upper()
            env = _required(row, "environment", n).upper()
            if env not in {"INDOOR", "OUTDOOR"}:
                raise InputDataError(f"Row {n}: invalid environment '{env}'.")
            rate = _decimal(row.get("rate_per_sqft_day_rs"), "rate_per_sqft_day_rs", n)
            area = _decimal(row.get("cabinet_area_sqft"), "cabinet_area_sqft", n)
            try: fleet = int(_required(row, "fleet_cabinets", n))
            except ValueError: raise InputDataError(f"Row {n}: fleet_cabinets must be an integer.")
            if rate < 0 or area <= 0 or fleet < 0:
                raise InputDataError(f"Row {n}: invalid negative rate/fleet or non-positive cabinet area.")
            if pitch in entries:
                raise InputDataError(f"Row {n}: duplicate pitch '{pitch}'. The official fleet is per pitch.")
            entries[pitch] = RateCardEntry(pitch, env, rate, area, fleet)
    if not entries: raise InputDataError("Rate card contains no entries.")
    return entries

def load_event_requests(path, rate_card):
    required = {"request_id", "client", "wall_width_ft", "wall_height_ft", "pitch", "start_date", "days", "distance_km", "power_source"}
    requests = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise InputDataError(f"Requests must contain columns: {', '.join(sorted(required))}")
        seen = set()
        for n, row in enumerate(reader, 2):
            rid = _required(row, "request_id", n)
            if rid in seen: raise InputDataError(f"Row {n}: duplicate request_id '{rid}'.")
            seen.add(rid)
            client = _required(row, "client", n)
            pitch = _required(row, "pitch", n).upper()
            if pitch not in rate_card: raise InputDataError(f"Row {n}: unknown pitch '{pitch}'.")
            width = _decimal(row.get("wall_width_ft"), "wall_width_ft", n)
            height = _decimal(row.get("wall_height_ft"), "wall_height_ft", n)
            try: start = datetime.strptime(_required(row, "start_date", n), "%Y-%m-%d").date()
            except ValueError: raise InputDataError(f"Row {n}: start_date must use YYYY-MM-DD.")
            try: days = int(_required(row, "days", n))
            except ValueError: raise InputDataError(f"Row {n}: days must be a whole number.")
            distance = _decimal(row.get("distance_km"), "distance_km", n)
            power = _required(row, "power_source", n).upper()
            if width <= 0 or height <= 0 or not 1 <= days <= 8 or distance < 0:
                raise InputDataError(f"Row {n}: dimensions must be positive, days must be 1–8, and distance must be non-negative.")
            if power not in {"MAINS", "GENERATOR"}: raise InputDataError(f"Row {n}: invalid power_source '{power}'.")
            requests.append(EventRequest(rid, client, width, height, pitch, rate_card[pitch].environment, start, days, distance, power))
    return requests
