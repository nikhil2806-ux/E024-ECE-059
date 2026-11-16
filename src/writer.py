"""Write evaluation-format quotation and fleet CSV files."""
import csv

QUOTATION_FIELDS = [
    "request_id", "pitch", "cabinets", "billable_sqft", "rental_gross_rs",
    "multiday_discount_rs", "setup_rs", "transport_rs", "generator_rs",
    "operator_rs", "subtotal_rs", "gst_rs", "total_rs", "availability",
    "shortfall_cabinets",
]
FLEET_FIELDS = ["date", "pitch", "cabinets_held", "fleet_cabinets", "free_cabinets"]


def write_quotations(output_dir, quotations):
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "quotations.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=QUOTATION_FIELDS)
        writer.writeheader()
        for quote in quotations:
            writer.writerow({
                "request_id": quote.request_id,
                "pitch": quote._pitch,
                "cabinets": quote.cabinet_count,
                "billable_sqft": quote.billable_area_sq_ft,
                "rental_gross_rs": quote.rental_gross,
                "multiday_discount_rs": quote.rental_discount,
                "setup_rs": quote.setup,
                "transport_rs": quote.transport,
                "generator_rs": quote.generator,
                "operator_rs": quote.operators,
                "subtotal_rs": quote.pre_tax_total,
                "gst_rs": quote.gst,
                "total_rs": quote.grand_total,
                "availability": quote.status,
                "shortfall_cabinets": int(quote.shortfall or 0),
            })


def write_fleet_usage(output_dir, fleet_rows):
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "fleet_usage.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FLEET_FIELDS)
        writer.writeheader()
        writer.writerows(fleet_rows)


def write_outputs(output_dir, quotations, fleet_rows):
    """Backward-compatible convenience wrapper for tests and callers."""
    write_quotations(output_dir, quotations)
    write_fleet_usage(output_dir, fleet_rows)
