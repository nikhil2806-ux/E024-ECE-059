# Design Document
## E024-ECE-059 — LED Display and Signage Rental Quotation Engine

**Team:** E024  
**Members:** Nandini Girish and Nikhil P Karamadi  
**Section:** ECM B  
**Language:** Python 3.10+  
**Application type:** Command-file-driven Python CLI; no graphical user interface

## 1. Problem statement
The project implements a quotation engine for indoor and outdoor LED video-wall rentals. It reads a rate card and event requests, calculates an itemized quotation for each request, checks cabinet availability by pitch and date, and produces evaluation-format CSV files.

## 2. Scope and constraints
The implemented baseline includes CSV loading and validation, cabinet rounding, billable area, daily and weekend rental pricing, duration discounts, setup and outdoor rigging, transport, generator, operator charges, GST, fleet allocation, command-file execution, and CSV output. The optional stretch goals of multi-wall events in one quote and an early-booking discount are not implemented.

## 3. System architecture
| Module | Responsibility |
|---|---|
| `main.py` | Parses and executes commands in `commands.txt` order; coordinates the application |
| `src/models.py` | Defines `RateCardEntry`, `EventRequest`, and `Quotation` data classes |
| `src/loader.py` | Reads CSV files and validates headers, identifiers, dates, numeric values, ranges, pitches and power sources |
| `src/fleet.py` | Tracks cabinets held by pitch and date; checks all dates before committing a reservation |
| `src/quotation.py` | Calculates rental, discounts, setup, transport, generator, operators, GST and availability |
| `src/writer.py` | Writes `quotations.csv` and `fleet_usage.csv` with fixed evaluation column order |
| `tests/` | Unit and regression tests for commands, input validation, pricing, fleet logic and official sample scenarios |

No third-party Python packages are required.

## 4. Data model
### `RateCardEntry`
Stores `pitch`, `environment`, `rate_per_sq_ft_per_day`, `cabinet_area_sq_ft`, and `fleet_cabinet_count`. The rate card has one entry per pitch, and the fleet is shared by that pitch.

### `EventRequest`
Stores `request_id`, `client`, `width_ft`, `height_ft`, `pitch`, `environment`, `start_date`, `days`, `distance_km`, and `power_source`. The official requests file does not contain an environment column; the loader obtains environment from the rate-card entry for the requested pitch. The request model does not retain the informational `received_date`, `event_name`, or `venue` fields after validating them.

### `Quotation`
Stores request and calculation results, including status, requested area, cabinet count, billable area, gross rental, discount, net rental, setup, rigging, transport, generator, operator count and charge, pre-tax total, GST, grand total, and fleet shortfall details.

### Fleet allocation
Fleet availability is keyed by `(pitch, date)`, not by environment. An accepted request reserves its required cabinet count on each event date. A request that fails on any date does not reserve cabinets on any date.

## 5. Business rules
1. Requested wall area = width × height.
2. Cabinet count = ceiling(requested area ÷ cabinet area).
3. Billable area = cabinet count × cabinet area.
4. Daily rental = billable area × rate per sq ft per day.
5. Saturday and Sunday rental days use a 1.25 multiplier.
6. Sum daily rental charges, then apply a rental discount: 10% for 4–7 days; 20% for 8 days; otherwise no duration discount.
7. Setup/dismantle is ₹4,000 for billable area up to and including 100 sq ft. Above 100 sq ft, setup = ₹4,000 + ₹35 × (billable area − 100).
8. Outdoor setup adds a 20% rigging surcharge.
9. Transport is free through 15 km. Above 15 km, transport per vehicle = ₹45 × 2 × (distance − 15).
10. Billable area strictly above 300 sq ft requires two vehicles; otherwise one.
11. Generator charge = ₹2,500 × event days when power source is `GENERATOR`; otherwise zero.
12. Operator count = ceiling(billable area ÷ 150); operator charge = count × ₹1,500 × event days.
13. Fleet is checked for each pitch/date. Requests are processed in file order.
14. A request is `AVAILABLE` only if every event date has enough remaining cabinets. Otherwise it is `UNAVAILABLE`; shortfall is the largest date-specific excess over fleet capacity. Unavailable requests reserve nothing.
15. Each monetary line is calculated exactly and rounded half-up to a whole rupee. The subtotal is the sum of rounded charge lines. GST is 18% of that subtotal, rounded half-up. Total = subtotal + GST.

## 6. Command interpreter and execution flow
`main.py` reads `commands.txt` from top to bottom. Blank lines and lines beginning with `#` are ignored. Each command is validated for its name and argument count.

Supported commands:
- `LOAD_RATE_CARD|file`
- `LOAD_REQUESTS|file`
- `QUOTE_ALL`
- `PRINT_QUOTES`
- `PRINT_FLEET|from_date|to_date`

The rate card must be loaded before requests; both must be loaded before `QUOTE_ALL`. Output files are written only when their corresponding print commands are reached. Fleet report dates must be valid ISO dates, and the end date cannot precede the start date. Required output commands must be present.

Execution flow:
1. Parse command file.
2. Load and validate rate card.
3. Load and validate requests.
4. Quote requests in file order, checking and reserving fleet as each request is processed.
5. On `PRINT_QUOTES`, write quotations.
6. On `PRINT_FLEET`, write pitch/date fleet usage for the requested period.

## 7. State model
```text
START
  |
  v
READ_COMMANDS
  |
  v
LOAD_RATE_CARD ---- invalid/missing ----> ERROR
  |
  v
LOAD_REQUESTS ----- invalid/missing ----> ERROR
  |
  v
QUOTE_ALL
  |
  v
FOR EACH REQUEST (received order)
  |
  v
CALCULATE QUOTE
  |
  v
CHECK EVERY EVENT DATE
  |                         |
  | all dates available    | any date over capacity
  v                         v
AVAILABLE                 UNAVAILABLE
  |                         |
  v                         v
RESERVE ALL DATES         RESERVE NOTHING
  |                         |
  +------------+------------+
               |
               v
       NEXT REQUEST / DONE
               |
       +-------+--------+
       |                |
       v                v
 PRINT_QUOTES      PRINT_FLEET
       |                |
       v                v
 quotations.csv    fleet_usage.csv
```

## 8. Input and output formats
### Inputs
`rate_card.csv` columns: `pitch,environment,rate_per_sqft_day_rs,cabinet_area_sqft,fleet_cabinets`

`requests.csv` columns: `request_id,received_date,client,event_name,venue,wall_width_ft,wall_height_ft,pitch,start_date,days,distance_km,power_source`

`commands.txt` contains ordered commands. Dates use `YYYY-MM-DD`; the official sample pack covers November and December 2026.

### Outputs
`quotations.csv` contains one row per request, in request-file order. Column order:
`request_id,pitch,cabinets,billable_sqft,rental_gross_rs,multiday_discount_rs,setup_rs,transport_rs,generator_rs,operator_rs,subtotal_rs,gst_rs,total_rs,availability,shortfall_cabinets`

`fleet_usage.csv` contains one row per pitch per date, ordered by date then pitch. Column order:
`date,pitch,cabinets_held,fleet_cabinets,free_cabinets`

## 9. Validation
The loader checks required headers, duplicate headers, required fields, supported pitch values, unique `EVR-nnn` request IDs, valid ISO dates, positive dimensions, integer rental days from 1 through 8, non-negative integer distance, supported power sources, non-negative rates, positive cabinet area, and non-negative integer fleet counts. It rejects duplicate pitch entries because the official fleet is per pitch.

The command interpreter rejects unknown commands, incorrect argument counts, invalid command ordering, invalid fleet-report dates and missing required print commands.

## 10. Test strategy and edge cases
Run `python3 -m unittest discover -s tests -v`.

The current suite contains 26 tests covering command execution order, unknown commands, missing output commands, invalid sequencing, fleet contention, different dates, no partial reservation after a failed multi-day request, duplicate pitch, invalid dimensions, missing required fields, invalid integer distance, official input loading, output schema, planted scenarios, cabinet rounding, 100 and 300 sq ft boundaries, transport at 15 km, weekend calculation before duration discount, 8-day discount, generator charge, operator threshold, outdoor rigging and half-up rounding.

The official sample-data README does not provide expected totals for all 30 requests. Tests therefore verify its stated planted scenarios, output schema and business-rule behavior; no claim is made that all 30 rows have been compared to unpublished expected totals.

## 11. Reproducibility
Requirements: Python 3.10+; no third-party dependencies.

Run the application from the project root using `python3 main.py`. Run tests using `python3 -m unittest discover -s tests -v`.

The root-level `rate_card.csv`, `requests.csv`, and `commands.txt` are the official Team E024 sample-data files supplied for this assignment.
