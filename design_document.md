# Design Document
## E024-ECE-059 — LED Display and Signage Rental Quotation Engine

**Team:** E024  
**Members:** Nandini Girish (1AT24UE046), Nikhil P Karamadi (1AT24UE047)  
**Section:** ECM B  
**Language:** Python 3.10+  
**Application type:** Command-file driven; no user interface

## 1. Problem statement
Build a quotation engine for indoor and outdoor LED video walls. The application reads a rate card and event requests, calculates itemized quotations, checks cabinet availability across each requested date, and writes deterministic CSV output.

## 2. Scope
Included: input loading and validation, cabinet rounding, daily rental calculation, weekend rates, duration discounts, setup, outdoor rigging, transport, generator, operators, GST, fleet reservations, output files, and unit tests.

Optional stretch goals not implemented in the baseline: multi-wall events in one quote and early-booking discount.

## 3. Architecture
- `main.py`: orchestrates loading, validation, fleet checking, pricing and output.
- `src/models.py`: typed data structures for rate-card entries, requests and quotations.
- `src/loader.py`: validates required headers, data types, dates, ranges and duplicate keys.
- `src/fleet.py`: maintains per-date cabinet allocations and commits only fully feasible bookings.
- `src/quotation.py`: contains pure pricing calculations and calls the fleet manager.
- `src/writer.py`: writes quotations, availability and errors as CSV.
- `tests/`: tests calculations, fleet conflicts and invalid input.

## 4. Entities and relationships
### RateCardEntry
Attributes: `pitch`, `environment`, `rate_per_sq_ft_per_day`, `cabinet_area_sq_ft`, `fleet_cabinet_count`.

### EventRequest
Attributes: `request_id`, `client`, `width_ft`, `height_ft`, `pitch`, `environment`, `start_date`, `days`, `distance_km`, `power_source`.

### Quotation
Contains requested area, cabinet count, billable area, rental gross, discount, net rental, setup, rigging, transport, generator, operator count and charge, pre-tax total, GST, grand total, and availability status/shortfall.

### Fleet allocation
Identified by `(pitch, date)`. Fleet capacity is shared per pitch. Each accepted event reserves its required cabinet count on each date; the booking is committed only after every requested date passes.

Relationship summary:
- One rate-card entry is selected by each request's `pitch`; its environment determines the outdoor setup surcharge.
- One request produces one quotation.
- One accepted request creates one allocation per rental date.
- A rejected request creates no allocations.

## 5. Business rules
- **BR-01:** Requested area = width × height, in square feet.
- **BR-02:** Cabinet count = ceiling(requested area / cabinet area).
- **BR-03:** Billable area = cabinet count × cabinet area.
- **BR-04:** Daily rental = billable area × rate; Saturday/Sunday multiplier = 1.25.
- **BR-05:** Sum daily rental charges, then discount 10% for 4–7 days or 20% for 8+ days; otherwise no discount.
- **BR-06:** Setup/dismantle = ₹4,000 through 100 sq ft; above 100 sq ft, ₹4,000 + ₹35 × (billable area − 100).
- **BR-07:** Outdoor rigging surcharge = 20% of setup; indoor surcharge = zero.
- **BR-08:** Transport per vehicle = ₹45 × max(0, distance − 15) × 2.
- **BR-09:** If billable area >300 sq ft, use two vehicles; otherwise one.
- **BR-10:** Generator charge = ₹2,500 × rental days only for GENERATOR power.
- **BR-11:** Operator count = ceiling(billable area / 150); charge = count × ₹1,500 × days.
- **BR-12:** Check requested cabinet capacity for each pitch/date; indoor and outdoor do not create separate fleet pools.
- **BR-13:** If any date is over capacity, mark UNAVAILABLE and record shortfall; do not reserve any date for that request.
- **BR-14:** GST = 18% of the pre-tax total.
- **BR-15:** Round printed monetary lines to whole rupees using the documented rounding policy.
- **BR-16:** Validate required input fields, allowed values, numeric ranges, dates, duplicate identifiers and rate-card keys.

## 6. Calculation order
1. Validate request and locate its rate-card entry.
2. Calculate requested area, cabinet count and billable area.
3. Calculate each day's rental charge, including weekend multiplier.
4. Sum daily rental charges and apply the applicable rental discount.
5. Calculate setup, outdoor rigging, transport, generator and operator charges.
6. Check fleet availability across all dates; reserve only if all dates pass.
7. Round output lines according to the chosen policy.
8. Sum pre-tax charge lines, calculate GST, and produce grand total.

The fleet decision is independent of the monetary total. An unavailable request is still reported with its availability status and shortfall.

## 7. State diagram
```text
RECEIVED
   |
   v
VALIDATING ---- invalid ----> INPUT_ERROR
   |
   v
RATE_CARD_LOOKUP ---- missing rate ----> INPUT_ERROR
   |
   v
CALCULATING_QUOTE
   |
   v
CHECKING_ALL_DATES
   |                 |
   | all dates pass  | one or more dates fail
   v                 v
AVAILABLE          UNAVAILABLE
   |                 |
   v                 v
RESERVE_CAPACITY   DO_NOT_RESERVE
   |                 |
   +--------+--------+
            v
      WRITE_OUTPUT
```

## 8. Input formats
`rate_card.csv` fields:
`pitch,environment,rate_per_sqft_day_rs,cabinet_area_sqft,fleet_cabinets`

`requests.csv` fields:
`request_id,received_date,client,event_name,venue,wall_width_ft,wall_height_ft,pitch,start_date,days,distance_km,power_source`

Dates use `YYYY-MM-DD`. Environment values are `INDOOR` or `OUTDOOR`; power values are `GENERATOR` or `MAINS`.

## 9. Output formats
- `quotations.csv`: one row per request with the official 15-column evaluation schema.
- `fleet_usage.csv`: one row per pitch per date with held, total and free cabinets.

## 10. Edge-case test plan
1. Billable area exactly 100 sq ft: setup ₹4,000.
2. Billable area exactly 300 sq ft: no second vehicle.
3. Billable area just above 300 sq ft: second vehicle.
4. Four-day event spanning a weekend: weekend multipliers before 10% discount.
5. Distance exactly 15 km: transport is free.
6. Competing requests for remaining fleet: deterministic input order.
7. A multi-day booking fails on one date: no partial reservation.
8. Width/height produce fractional cabinet count: ceiling is used.
9. Exactly 150 sq ft versus 151 sq ft: one operator versus two.
10. Generator versus mains power.
11. Indoor versus outdoor rigging.
12. Eight-day rental discount.
13. Invalid dates, negative distances, zero dimensions, unsupported power and duplicate rate entries.
14. Half-rupee rounding uses the documented rule.

## 11. Official sample-pack conventions
The official sample-pack README resolves the main implementation assumptions: setup above 100 sq ft is ₹4,000 + ₹35 per excess sq ft; fleet is tracked per pitch/date; unavailable requests still carry a full quotation; shortfall is the maximum date-specific shortage; each line is rounded half-up before subtotal and GST; and output filenames and column order are fixed. The sample pack does not provide expected quotation values for these 30 requests, so the planted scenarios are used as regression checks.

## 12. Testing and reproducibility
Run tests with:
`python3 -m unittest discover -s tests -v`

Run the application with:
`python3 main.py`

The root-level `rate_card.csv`, `requests.csv`, and `commands.txt` are the official Team E024 sample-data files supplied by 10 SECONDS. The expected-output schema and planted scenarios are documented in `sample_data_README.md`.
