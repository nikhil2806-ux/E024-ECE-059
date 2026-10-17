"""CSV input loading and validation."""
import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from .models import EventRequest, RateCardEntry


class InputDataError(ValueError):
    """Raised when an input file contains invalid data."""


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
    required = {"pitch", "environment", "rate_per_sq_ft_per_day",
                "cabinet_area_sq_ft", "fleet_cabinet_count"}
    entries = {}
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
                raise InputDataError(f"Rate card must contain columns: {', '.join(sorted(required))}")
            for row_number, row in enumerate(reader, start=2):
                pitch = _required(row, "pitch", row_number).upper()
                environment = _required(row, "environment", row_number).upper()
                if environment not in {"INDOOR", "OUTDOOR"}:
                    raise InputDataError(f"Row {row_number}: environment must be INDOOR or OUTDOOR.")
                rate = _decimal(row.get("rate_per_sq_ft_per_day"), "rate_per_sq_ft_per_day", row_number)
                cabinet_area = _decimal(row.get("cabinet_area_sq_ft"), "cabinet_area_sq_ft", row_number)
                try:
                    fleet = int(_required(row, "fleet_cabinet_count", row_number))
                except ValueError:
                    raise InputDataError(f"Row {row_number}: fleet_cabinet_count must be an integer.")
                if rate < 0 or cabinet_area <= 0 or fleet < 0:
                    raise InputDataError(f"Row {row_number}: rates/fleet cannot be negative and cabinet area must be positive.")
                key = (pitch, environment)
                if key in entries:
                    raise InputDataError(f"Row {row_number}: duplicate rate-card entry for {pitch}/{environment}.")
                entries[key] = RateCardEntry(pitch, environment, rate, cabinet_area, fleet)
    except OSError as exc:
        raise InputDataError(f"Cannot read rate card '{path}': {exc}")
    if not entries:
        raise InputDataError("Rate card contains no entries.")
    return entries


def load_event_requests(path):
    required = {"request_id", "client", "width_ft", "height_ft", "pitch",
                "environment", "start_date", "days", "distance_km", "power_source"}
    requests = []
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
                raise InputDataError(f"Event requests must contain columns: {', '.join(sorted(required))}")
            seen_ids = set()
            for row_number, row in enumerate(reader, start=2):
                request_id = _required(row, "request_id", row_number)
                if request_id in seen_ids:
                    raise InputDataError(f"Row {row_number}: duplicate request_id '{request_id}'.")
                seen_ids.add(request_id)
                client = _required(row, "client", row_number)
                width = _decimal(row.get("width_ft"), "width_ft", row_number)
                height = _decimal(row.get("height_ft"), "height_ft", row_number)
                pitch = _required(row, "pitch", row_number).upper()
                environment = _required(row, "environment", row_number).upper()
                try:
                    start_date = datetime.strptime(_required(row, "start_date", row_number), "%Y-%m-%d").date()
                except ValueError:
                    raise InputDataError(f"Row {row_number}: start_date must use YYYY-MM-DD.")
                try:
                    days = int(_required(row, "days", row_number))
                except ValueError:
                    raise InputDataError(f"Row {row_number}: days must be a whole number.")
                distance = _decimal(row.get("distance_km"), "distance_km", row_number)
                power = _required(row, "power_source", row_number).upper()
                if width <= 0 or height <= 0:
                    raise InputDataError(f"Row {row_number}: width_ft and height_ft must be greater than zero.")
                if days < 1:
                    raise InputDataError(f"Row {row_number}: days must be at least 1.")
                if distance < 0:
                    raise InputDataError(f"Row {row_number}: distance_km cannot be negative.")
                if environment not in {"INDOOR", "OUTDOOR"}:
                    raise InputDataError(f"Row {row_number}: environment must be INDOOR or OUTDOOR.")
                if power not in {"GENERATOR", "MAINS"}:
                    raise InputDataError(f"Row {row_number}: power_source must be GENERATOR or MAINS.")
                requests.append(EventRequest(request_id, client, width, height, pitch,
                                             environment, start_date, days, distance, power))
    except OSError as exc:
        raise InputDataError(f"Cannot read event requests '{path}': {exc}")
    return requests
