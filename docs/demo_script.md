# Five-minute demo script — E024-ECE-059

## 0:00–0:30 — Introduction
“Our project is ECE-059, an LED display rental quotation engine written in Python 3.10+. It reads a rate card and event requests, produces itemized quotations and checks fleet availability by date.”

## 0:30–1:10 — Architecture and files
Show the repository. Explain `main.py`, `src/loader.py`, `src/quotation.py`, `src/fleet.py`, and `src/writer.py`. Point out that input and output are CSV files and there is no UI.

## 1:10–2:10 — Demonstrate a quotation
Run `python3 main.py`. Open `output/quotations.csv`. Explain requested area, cabinet rounding, billable area, rental charges, discount, setup, transport, operator/generator charges and GST.

## 2:10–3:00 — Explain weekend discount
Show the test for a four-day event spanning a weekend. Explain that Saturday and Sunday rental rates are multiplied by 1.25 individually before the 10% multi-day discount is applied to the daily sum.

## 3:00–4:00 — Demonstrate fleet handling
Explain that fleet capacity is shared per pitch and checked for every requested date. If one date fails, the whole booking is unavailable and no cabinets are reserved for it. Show the fleet unit tests.

## 4:00–4:40 — Run tests
Run `python3 -m unittest discover -s tests -v`. Explain the boundary tests for 100 sq ft, 300 sq ft, 15 km, operator thresholds and competing requests.

## 4:40–5:00 — Close
Mention validation, deterministic processing, the decision log, and that the official 30-request sample pack has been used for regression checks. The pack does not include expected quotation totals; its planted scenarios and required output schema are covered by our tests.
