# ECE-059 – LED Display and Signage Rental Quotation Engine — Sample Data Pack
Prepared by 10 SECONDS for Team E024.

This pack is the input for an LED video-wall rental quotation engine: a rate card of 5 pixel pitches with fleet counts and 30 event requests for November–December 2026. Your engine reads `commands.txt`, quotes every request in file order (received order), checks fleet availability date by date, and prints the quotations and the fleet usage.

Pack conventions where the brief is silent: an event occupies its cabinets on every date from start_date for `days` days. Every AVAILABLE quote immediately holds its cabinets for those dates; an UNAVAILABLE quote holds nothing. Shortfall = the largest (cabinets already held on a date + cabinets needed − fleet) over the event's dates. Weekend = Saturday and Sunday. Setup = Rs 4,000 for billable area ≤ 100 sq ft, else Rs 4,000 + Rs 35 × (billable − 100); outdoor pitches add 20%. Transport = Rs 45 × 2 × (distance − 15) for distance > 15 km, doubled when billable area is above 300 sq ft. Operators = ceil(billable / 150) × Rs 1,500 × days. Rounding: compute each line exactly, round it half up to whole rupees, add the rounded lines for the subtotal, then GST = 18% of the subtotal rounded to whole rupees.

## Files
| File | What it holds | Rows |
|---|---|---|
| rate_card.csv | Pixel pitches with rate, cabinet area and fleet | 5 |
| requests.csv | Event requests in received order | 30 |
| commands.txt | Load commands, quoting and print commands | 5 |

## Column reference
Conventions: dates `YYYY-MM-DD`; timestamps `YYYY-MM-DD HH:MM:SS` (24h, IST, no timezone suffix); money in Rs as plain decimals (no commas, no symbol); percentages as plain numbers (12.5 = 12.5%); booleans `true`/`false`; IDs uppercase with a fixed prefix.

### rate_card.csv
| Column | Type | Units / format | Allowed values | Notes |
|---|---|---|---|---|
| pitch | string | - | P2.5, P2.9, P3.9, P4.8, P6 | Primary key |
| environment | string | - | INDOOR, OUTDOOR | OUTDOOR adds 20% to setup |
| rate_per_sqft_day_rs | decimal | Rs, 2 dp |  |  |
| cabinet_area_sqft | decimal | sq ft, 1 dp | 4.0 (2 × 2 ft), 6.0 (2 × 3 ft) |  |
| fleet_cabinets | integer | cabinets |  | Limit per date |

### requests.csv
| Column | Type | Units / format | Allowed values | Notes |
|---|---|---|---|---|
| request_id | string | EVR-nnn | unique | Processing order |
| received_date | date | YYYY-MM-DD |  | File is sorted by this |
| client | string | - |  |  |
| event_name | string | - |  |  |
| venue | string | - |  | Not used by any rule |
| wall_width_ft | decimal | ft, 1 dp |  |  |
| wall_height_ft | decimal | ft, 1 dp |  |  |
| pitch | string | - | must exist in rate_card.csv |  |
| start_date | date | YYYY-MM-DD | Nov–Dec 2026 | First event day |
| days | integer | days | 1–8 |  |
| distance_km | integer | km |  | One-way distance from the warehouse |
| power_source | string | - | MAINS, GENERATOR | GENERATOR adds Rs 2,500 per day |

## Command file format
`commands.txt` holds one command per line as `COMMAND_NAME|arg1|arg2|...`. Commands must be processed in file order, top to bottom. Lines starting with `#` are comments and blank lines are ignored.

| Command | Arguments (in order) | Meaning |
|---|---|---|
| LOAD_RATE_CARD / LOAD_REQUESTS | file | Load the two files |
| QUOTE_ALL | (none) | Quote every request in file order, with the fleet check |
| PRINT_QUOTES | (none) | Print every quotation |
| PRINT_FLEET | from_date \| to_date | Print cabinets held per pitch per date |

All money columns are whole rupees (no decimals); `multiday_discount_rs` is shown as a positive number and subtracted. `availability` is AVAILABLE or UNAVAILABLE; `shortfall_cabinets` 0 when available. An UNAVAILABLE row still carries the full quotation.

## Planted scenarios
Line numbers count the header row as line 1, so the first data row of a CSV is line 2. For commands.txt the line number is the physical line in the file (comment lines included).

- **Wall of exactly 100 sq ft and exactly 300 sq ft billable** — requests.csv line 3 (EVR-002, 10.0 × 10.0 ft P2.9, 2026-11-04 for 2 day(s), 12 km): 100 sq ft → 25 cabinets → exactly 100 sq ft billable → setup is the flat Rs 4,000. requests.csv line 4 (EVR-003, 20.0 × 15.0 ft P4.8, 2026-11-10 for 3 day(s), 38 km): 300 sq ft → 50 outdoor cabinets → exactly 300 sq ft billable → Rs 4,000 + 200 × 35, plus 20% outdoor rigging; NOT above 300 sq ft, so one vehicle; 2 operators (300 / 150).
- **Event of exactly 4 days spanning a weekend** — requests.csv line 5 (EVR-004, 16.0 × 9.0 ft P3.9, 2026-11-20 for 4 day(s), 22 km): Friday to Monday — Saturday and Sunday are charged at 1.25× per day; the 4-day sum is then discounted 10%.
- **Venue at exactly 15 km** — requests.csv line 8 (EVR-007, 12.0 × 8.0 ft P2.5, 2026-11-26 for 1 day(s), 15 km): venue exactly 15 km → no transport charge. requests.csv line 22 (EVR-021, 12.0 × 8.0 ft P2.5, 2026-12-01 for 1 day(s), 16 km): 16 km → (16 − 15) × Rs 45 × 2 ways = Rs 90.
- **Two quotes competing for the last cabinets on the same dates** — requests.csv line 23 (EVR-022, 24.0 × 16.0 ft P2.5, 2026-12-11 for 4 day(s), 9 km) holds 96 of the 120 P2.5 cabinets on its dates. requests.csv line 26 (EVR-025, 12.0 × 8.0 ft P2.5, 2026-12-12 for 2 day(s), 11 km) needs 24 cabinets on overlapping dates → 96 + 24 = 120 = fleet → AVAILABLE (exactly at the limit). requests.csv line 27 (EVR-026, 6.0 × 4.0 ft P2.5, 2026-12-12 for 3 day(s), 14 km) arrives next for the same dates and needs 6 → 126 > 120 → UNAVAILABLE with a shortfall of 6 cabinets; it holds nothing.
- **Width that is not a multiple of cabinet size** — requests.csv line 28 (EVR-027, 13.5 × 7.0 ft P2.9, 2026-12-15 for 2 day(s), 27 km): 13.5 ft is not a multiple of the 2 ft cabinet: 13.5 × 7 = 94.5 sq ft / 4 = 23.6 → 24 cabinets → 96 sq ft billable.

Extra traps (realistic things your validation should catch):

- **8-day event and second vehicle** — requests.csv line 15 (EVR-014, 30.0 × 12.0 ft P6, 2026-11-30 for 8 day(s), 41 km): 8 days → 20% off; 360 sq ft billable is above 300 sq ft → transport is charged twice (second vehicle); generator for 8 days.
- **Operators at 150 sq ft** — requests.csv line 24 (EVR-023, 15.0 × 10.0 ft P6, 2026-12-23 for 1 day(s), 6 km) → exactly 150 sq ft billable → 1 operator; requests.csv line 29 (EVR-028, 15.0 × 10.5 ft P6, 2026-12-24 for 1 day(s), 6 km) → 157.5 sq ft → 27 cabinets → 162 sq ft → 2 operators.
- **Unavailable quotes do not hold cabinets** — A quote marked UNAVAILABLE is not counted against the fleet, so a later, smaller request for the same dates can still be AVAILABLE.

## What is NOT in this pack
Expected outputs are not provided for this set. Validate your engine with your own test suite against the rules in your brief (BR-01 … BR-07). A separate hidden input set with the same schema will be used at final evaluation; outputs are compared field-for-field, so follow the column formats above exactly in your own output.

## Output format expected at evaluation
Produce these files (CSV, header row, same conventions as above). Column order matters.

### quotations.csv
One row per request in file order.

Columns in order: `request_id`, `pitch`, `cabinets`, `billable_sqft`, `rental_gross_rs`, `multiday_discount_rs`, `setup_rs`, `transport_rs`, `generator_rs`, `operator_rs`, `subtotal_rs`, `gst_rs`, `total_rs`, `availability`, `shortfall_cabinets`

### fleet_usage.csv
One row per pitch per date with cabinets held, ordered by date then pitch.

Columns in order: `date`, `pitch`, `cabinets_held`, `fleet_cabinets`, `free_cabinets`
