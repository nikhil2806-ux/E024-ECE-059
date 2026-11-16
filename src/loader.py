"""CSV input loading and strict validation for the official ECE-059 pack."""
import csv
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation

from .models import EventRequest, RateCardEntry


class InputDataError(ValueError):
    """Raised when an input CSV does not satisfy the published schema."""


def _decimal(value, field, row_number):
    try:
        result = Decimal(str(value).strip())
    except (InvalidOperation, AttributeError, ValueError):
        raise InputDataError(f"Row {row_number}: '{field}' must be a number.")
    if not result.is_finite():
        raise InputDataError(f"Row {row_number}: '{field}' must be finite.")
    return result


def _required(row, field, row_number):
    value = (row.get(field) or "").strip()
    if not value:
        raise InputDataError(f"Row {row_number}: missing required field '{field}'.")
    return value


def _date(value, field, row_number):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise InputDataError(f"Row {row_number}: '{field}' must use YYYY-MM-DD.")


def _read_csv(path, required_columns, label):
    try:
        handle = open(path, newline="", encoding="utf-8-sig")
    except OSError:
        raise
    with handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise InputDataError(f"{label} is empty or has no header row.")
        if len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise InputDataError(f"{label} contains duplicate column names.")
        missing = required_columns - set(reader.fieldnames)
        if missing:
            raise InputDataError(f"{label} must contain columns: {', '.join(sorted(missing))}")
        return list(enumerate(reader, 2))


def load_rate_card(path):
    required = {"pitch", "environment", "rate_per_sqft_day_rs", "cabinet_area_sqft", "fleet_cabinets"}
    rows = _read_csv(path, required, "Rate card")
    entries = {}
    for row_number, row in rows:
        pitch = _required(row, "pitch", row_number).upper()
        environment = _required(row, "environment", row_number).upper()
        if pitch not in {"P2.5", "P2.9", "P3.9", "P4.8", "P6"}:
            raise InputDataError(f"Row {row_number}: unsupported pitch '{pitch}'.")
        if environment not in {"INDOOR", "OUTDOOR"}:
            raise InputDataError(f"Row {row_number}: invalid environment '{environment}'.")
        rate = _decimal(row.get("rate_per_sqft_day_rs"), "rate_per_sqft_day_rs", row_number)
        cabinet_area = _decimal(row.get("cabinet_area_sqft"), "cabinet_area_sqft", row_number)
        fleet_text = _required(row, "fleet_cabinets", row_number)
        if not re.fullmatch(r"\d+", fleet_text):
            raise InputDataError(f"Row {row_number}: fleet_cabinets must be a non-negative integer.")
        fleet = int(fleet_text)
        if rate < 0 or cabinet_area <= 0:
            raise InputDataError(f"Row {row_number}: rate must be non-negative and cabinet area must be positive.")
        if pitch in entries:
            raise InputDataError(f"Row {row_number}: duplicate pitch '{pitch}'. The official fleet is per pitch.")
        entries[pitch] = RateCardEntry(pitch, environment, rate, cabinet_area, fleet)
    if not entries:
        raise InputDataError("Rate card contains no entries.")
    return entries


def load_event_requests(path, rate_card):
    required = {
        "request_id", "received_date", "client", "event_name", "venue",
        "wall_width_ft", "wall_height_ft", "pitch", "start_date", "days",
        "distance_km", "power_source",
    }
    rows = _read_csv(path, required, "Requests")
    requests = []
    seen_ids = set()
    for row_number, row in rows:
        request_id = _required(row, "request_id", row_number)
        if not re.fullmatch(r"EVR-\d{3}", request_id):
            raise InputDataError(f"Row {row_number}: request_id must use EVR-nnn format.")
        if request_id in seen_ids:
            raise InputDataError(f"Row {row_number}: duplicate request_id '{request_id}'.")
        seen_ids.add(request_id)

        _date(_required(row, "received_date", row_number), "received_date", row_number)
        client = _required(row, "client", row_number)
        _required(row, "event_name", row_number)
        _required(row, "venue", row_number)
        pitch = _required(row, "pitch", row_number).upper()
        if pitch not in rate_card:
            raise InputDataError(f"Row {row_number}: unknown pitch '{pitch}'.")

        width = _decimal(row.get("wall_width_ft"), "wall_width_ft", row_number)
        height = _decimal(row.get("wall_height_ft"), "wall_height_ft", row_number)
        start_date = _date(_required(row, "start_date", row_number), "start_date", row_number)
        days_text = _required(row, "days", row_number)
        if not re.fullmatch(r"\d+", days_text):
            raise InputDataError(f"Row {row_number}: 'days' must be a whole number.")
        days = int(days_text)
        distance_text = _required(row, "distance_km", row_number)
        if not re.fullmatch(r"\d+", distance_text):
            raise InputDataError(f"Row {row_number}: 'distance_km' must be a non-negative integer.")
        distance = Decimal(distance_text)
        power = _required(row, "power_source", row_number).upper()

        if width <= 0 or height <= 0:
            raise InputDataError(f"Row {row_number}: wall dimensions must be positive.")
        if not 1 <= days <= 8:
            raise InputDataError(f"Row {row_number}: days must be between 1 and 8.")
        if start_date.year != 2026 or start_date.month not in {11, 12}:
            raise InputDataError(f"Row {row_number}: start_date must be in November or December 2026.")
        if power not in {"MAINS", "GENERATOR"}:
            raise InputDataError(f"Row {row_number}: invalid power_source '{power}'.")

        requests.append(EventRequest(
            request_id, client, width, height, pitch, rate_card[pitch].environment,
            start_date, days, distance, power,
        ))
    return requests
