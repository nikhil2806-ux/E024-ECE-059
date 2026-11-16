# Five-minute demonstration script — E024-ECE-059

## Before recording
Open Terminal in the repository root. Confirm that `commands.txt`, `rate_card.csv`, and `requests.csv` are present.

## 0:00–0:30 — Introduction
“Our project is ECE-059, an LED Display and Signage Rental Quotation Engine. It is a Python command-line application. It reads a rate card and event requests, calculates itemized rental quotations, checks cabinet availability, and writes two CSV output files.”

## 0:30–1:10 — Repository and architecture
Show the repository and identify `main.py`, `src/loader.py`, `src/models.py`, `src/quotation.py`, `src/fleet.py`, `src/writer.py`, and `tests/`. Mention Python 3.10+ and no third-party packages.

## 1:10–1:50 — Command file
Open `commands.txt`. Explain that commands execute top-to-bottom: load rate card, load requests, quote all requests in received order, print quotations, and print fleet usage for the requested date range.

Run:
```bash
python3 main.py
```
Show the processed request and quotation counts.

## 1:50–2:40 — Quotation output
Open `output/quotations.csv`. Explain cabinet count using ceiling, billable area, daily rental, weekend multiplier, duration discount, setup, transport, generator and operator charges, rounded subtotal and GST.

Point to a planted case in `sample_data_README.md`, such as EVR-002 (100 sq ft billable), EVR-003 (300 sq ft billable), or EVR-007 (exactly 15 km).

## 2:40–3:40 — Fleet availability
Show `src/fleet.py` and the planted fleet competition in `sample_data_README.md`. Explain that fleet capacity is shared per pitch and checked for every requested date. If any date exceeds capacity, the request is unavailable, the shortfall is the largest date-specific shortage, and no cabinets are reserved.

## 3:40–4:30 — Validation and tests
Run:
```bash
python3 -m unittest discover -s tests -v
```
At the audited revision, 26 tests pass. Mention command-order tests, invalid-input tests, fleet tests and quotation boundary tests.

## 4:30–5:00 — Close
“Our implementation uses the official Team E024 sample-data pack and produces the required `quotations.csv` and `fleet_usage.csv` schemas. The pack does not include expected totals for all 30 events, so we tested the published planted scenarios and the specified output structure.”

## Demo discipline
Do not claim multi-wall events or the early-booking discount are implemented. Do not claim every output value was compared against an official expected-output file; the sample pack says those expected totals are not supplied.
