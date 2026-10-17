"""Write quotation, availability, and input-error CSV files."""
import csv
from decimal import Decimal


def _fmt(value):
    if isinstance(value, Decimal):
        return str(int(value))
    return value


def write_outputs(output_dir, quotations, errors=None):
    output_dir.mkdir(parents=True, exist_ok=True)
    quote_fields = [
        "request_id", "client", "status", "requested_area_sq_ft",
        "cabinet_count", "billable_area_sq_ft", "rental_gross",
        "rental_discount", "rental_net", "setup", "rigging", "transport",
        "generator", "operators_count", "operators", "pre_tax_total", "gst",
        "grand_total"
    ]
    availability_fields = ["request_id", "status", "cabinets_required", "affected_dates", "shortfall"]
    with open(output_dir / "quotations.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=quote_fields)
        writer.writeheader()
        for q in quotations:
            writer.writerow({
                "request_id": q.request_id, "client": q.client, "status": q.status,
                "requested_area_sq_ft": _fmt(q.requested_area_sq_ft),
                "cabinet_count": q.cabinet_count, "billable_area_sq_ft": _fmt(q.billable_area_sq_ft),
                "rental_gross": _fmt(q.rental_gross), "rental_discount": _fmt(q.rental_discount),
                "rental_net": _fmt(q.rental_net), "setup": _fmt(q.setup), "rigging": _fmt(q.rigging),
                "transport": _fmt(q.transport), "generator": _fmt(q.generator),
                "operators_count": q.operators_count, "operators": _fmt(q.operators),
                "pre_tax_total": _fmt(q.pre_tax_total), "gst": _fmt(q.gst), "grand_total": _fmt(q.grand_total)
            })
    with open(output_dir / "availability.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=availability_fields)
        writer.writeheader()
        for q in quotations:
            writer.writerow({
                "request_id": q.request_id, "status": q.status, "cabinets_required": q.cabinet_count,
                "affected_dates": q.affected_dates, "shortfall": q.shortfall
            })
    with open(output_dir / "errors.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["request_id", "error_code", "error_message"])
        writer.writeheader()
        for error in (errors or []):
            writer.writerow(error)
