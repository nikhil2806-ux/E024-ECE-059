"""Command-driven ECE-059 LED rental quotation engine."""
import argparse
from datetime import datetime
from pathlib import Path

from src.loader import load_rate_card, load_event_requests, InputDataError
from src.fleet import FleetManager
from src.quotation import calculate_quotation
from src.writer import write_quotations, write_fleet_usage


def _parse_commands(path):
    commands = []
    with path.open(encoding="utf-8-sig") as handle:
        for line_number, raw in enumerate(handle, 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = [part.strip() for part in line.split("|")]
            name = parts[0]
            expected_args = {"LOAD_RATE_CARD": 1, "LOAD_REQUESTS": 1,
                             "QUOTE_ALL": 0, "PRINT_QUOTES": 0, "PRINT_FLEET": 2}
            if name not in expected_args:
                raise InputDataError(f"commands.txt line {line_number}: unknown command '{name}'.")
            if len(parts) - 1 != expected_args[name] or any(not p for p in parts[1:]):
                raise InputDataError(f"commands.txt line {line_number}: invalid arguments for {name}.")
            commands.append((line_number, name, parts[1:]))
    return commands


def execute_commands(commands_path, output_dir):
    commands = _parse_commands(commands_path)
    base_dir = commands_path.resolve().parent
    rate_card = None
    requests = None
    fleet = None
    quotations = None
    wrote_quotes = False
    wrote_fleet = False

    for line_number, name, args in commands:
        if name == "LOAD_RATE_CARD":
            rate_card = load_rate_card(base_dir / args[0])
            fleet = FleetManager(rate_card)
            quotations = None
        elif name == "LOAD_REQUESTS":
            if rate_card is None:
                raise InputDataError(f"commands.txt line {line_number}: LOAD_RATE_CARD must come before LOAD_REQUESTS.")
            requests = load_event_requests(base_dir / args[0], rate_card)
            quotations = None
        elif name == "QUOTE_ALL":
            if rate_card is None or requests is None:
                raise InputDataError(f"commands.txt line {line_number}: load rate card and requests before QUOTE_ALL.")
            if quotations is not None:
                raise InputDataError(f"commands.txt line {line_number}: QUOTE_ALL may only run once per loaded request set.")
            quotations = []
            for request in requests:
                quote = calculate_quotation(request, rate_card[request.pitch], fleet)
                quote._pitch = request.pitch
                quotations.append(quote)
        elif name == "PRINT_QUOTES":
            if quotations is None:
                raise InputDataError(f"commands.txt line {line_number}: run QUOTE_ALL before PRINT_QUOTES.")
            write_quotations(output_dir, quotations)
            wrote_quotes = True
        elif name == "PRINT_FLEET":
            if fleet is None or rate_card is None:
                raise InputDataError(f"commands.txt line {line_number}: load rate card before PRINT_FLEET.")
            try:
                start = datetime.strptime(args[0], "%Y-%m-%d").date()
                end = datetime.strptime(args[1], "%Y-%m-%d").date()
            except ValueError:
                raise InputDataError(f"commands.txt line {line_number}: PRINT_FLEET dates must use YYYY-MM-DD.")
            if end < start:
                raise InputDataError(f"commands.txt line {line_number}: PRINT_FLEET end date precedes start date.")
            write_fleet_usage(output_dir, fleet.usage_rows(rate_card, start, end))
            wrote_fleet = True

    if not wrote_quotes or not wrote_fleet:
        missing = []
        if not wrote_quotes:
            missing.append("PRINT_QUOTES")
        if not wrote_fleet:
            missing.append("PRINT_FLEET")
        raise InputDataError("commands.txt is missing required output command(s): " + ", ".join(missing))
    return len(requests or []), len(quotations or [])


def main():
    parser = argparse.ArgumentParser(description="ECE-059 LED Display and Signage Rental Quotation Engine")
    parser.add_argument("--commands", default="commands.txt")
    parser.add_argument("--output", default="output")
    args = parser.parse_args()
    try:
        count_requests, count_quotes = execute_commands(Path(args.commands), Path(args.output))
    except (InputDataError, OSError, ValueError) as exc:
        print(f"Input/command error: {exc}")
        return 2
    print(f"Processed {count_requests} request(s); generated {count_quotes} quotation(s).")
    print(f"Outputs written to: {Path(args.output).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
