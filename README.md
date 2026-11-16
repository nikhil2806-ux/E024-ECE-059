# E024-ECE-059 — LED Display and Signage Rental Quotation Engine

A command-file-driven Python 3.10+ application that calculates LED video-wall rental quotations and checks cabinet availability by pitch and date.

## Team
- Team ID: E024
- Members: Nandini Girish and Nikhil P Karamadi
- Problem statement: ECE-059

## Requirements
- Python 3.10 or newer
- No third-party packages required

## Run
Keep `commands.txt`, `rate_card.csv`, and `requests.csv` in the repository root. From that directory run:

```bash
python3 main.py
```

The command file selects the input files and the fleet reporting date range. To specify another command file or output directory:

```bash
python3 main.py --commands commands.txt --output output
```

## Official input files
- `commands.txt`: commands are read from top to bottom.
- `rate_card.csv`: official ECE-059 rate card (pitch, environment, daily rate, cabinet area and fleet count).
- `requests.csv`: official event requests, processed in file order.
- `sample_data_README.md`: official sample-pack column reference, planted scenarios and evaluation output specification.

The request's environment is obtained from the matching pitch in the rate card; it is not a column in `requests.csv`.

## Output files
The application writes exactly these evaluation CSVs to `output/`:
- `quotations.csv`: one row per request in input order.
- `fleet_usage.csv`: one row per pitch per date, ordered by date then pitch.

Column names and order follow the official sample-pack README.

## Run tests

```bash
python3 -m unittest discover -s tests -v
```

## Implemented business rules
- Cabinet count is rounded up; billable area is cabinets multiplied by cabinet area.
- Saturday and Sunday rental days are charged at 1.25×.
- Rental discount: 10% for 4–7 days; 20% for 8+ days.
- Setup: ₹4,000 for billable area up to 100 sq ft; otherwise ₹4,000 + ₹35 for each sq ft above 100.
- Outdoor setup includes a 20% rigging surcharge.
- Transport is ₹45 per km beyond 15 km, each way; return trip is included.
- Billable area above 300 sq ft requires a second vehicle at the same transport charge.
- Generator: ₹2,500 per day.
- Operators: one per 150 sq ft or part thereof, at ₹1,500 per operator per day.
- GST: 18% of subtotal.
- Each monetary line is rounded half-up to whole rupees; rounded lines are added for subtotal, then GST is rounded half-up.
- Fleet capacity is shared per pitch across environments. A request reserves cabinets only if every event date is within capacity. An unavailable request reserves nothing and reports the largest date-specific shortfall.

## Project layout
- `main.py`: sequential command-file interpreter and application entry point
- `src/models.py`: data models
- `src/loader.py`: CSV parsing and validation of required columns, identifiers, dates, numeric fields and allowed values
- `src/fleet.py`: date-by-date fleet availability and reservation
- `src/quotation.py`: quotation calculations
- `src/writer.py`: evaluation-format CSV output, triggered by `PRINT_QUOTES` and `PRINT_FLEET`
- `tests/`: unit and official-pack regression tests
- `design_document.md`: design document source
- `decision_log.md`: implementation decisions and rationale
- `docs/`: supporting project documents
