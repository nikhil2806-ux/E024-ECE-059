"""Entry point for the E024-ECE-059 quotation engine."""
import argparse
import csv
import sys
from pathlib import Path

from src.loader import load_rate_card, load_event_requests, InputDataError
from src.fleet import FleetManager
from src.quotation import calculate_quotation
from src.writer import write_outputs


def main():
    parser = argparse.ArgumentParser(description="LED Display and Signage Rental Quotation Engine")
    parser.add_argument("--rate-card", default="data/rate_card.csv", help="Path to rate-card CSV")
    parser.add_argument("--requests", default="data/event_requests.csv", help="Path to event-request CSV")
    parser.add_argument("--output", default="output", help="Directory for generated CSV files")
    args = parser.parse_args()

    try:
        rate_card = load_rate_card(args.rate_card)
        requests = load_event_requests(args.requests)
        fleet = FleetManager(rate_card)
        quotations = []
        errors = []
        for request in requests:
            key = (request.pitch, request.environment)
            if key not in rate_card:
                errors.append({
                    "request_id": request.request_id,
                    "error_code": "UNKNOWN_RATE",
                    "error_message": f"No rate card entry for {request.pitch}/{request.environment}"
                })
                continue
            quotations.append(calculate_quotation(request, rate_card[key], fleet))
        write_outputs(Path(args.output), quotations, errors)
    except InputDataError as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 2

    print(f"Processed {len(requests)} request(s); generated {len(quotations)} quotation(s).")
    print(f"Invalid/unsupported requests: {len(errors)}.")
    print(f"Outputs written to: {Path(args.output).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
