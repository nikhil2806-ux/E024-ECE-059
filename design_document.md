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
Conceptually identified by `(pitch, environment, date)`. Each accepted event reserves its required cabinet count on each date. The booking is committed only after every requested date passes.

Relationship summary:
- One rate-card entry is selected by each request's `(pitch, environment)`.
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
- **BR-12:** Check requested cabinet capacity for each pitch/environment/date.
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
`pitch,environment,rate_per_sq_ft_per_day,cabinet_area_sq_ft,fleet_cabinet_count`

`event_requests.csv` fields:
`request_id,client,width_ft,height_ft,pitch,environment,start_date,days,distance_km,power_source`

Dates use `YYYY-MM-DD`. Environment values are `INDOOR` or `OUTDOOR`; power values are `GENERATOR` or `MAINS`.

## 9. Output formats
- `quotations.csv`: itemized monetary lines, areas, cabinets, status, pre-tax total, GST and grand total.
- `availability.csv`: status, cabinets required, affected dates and shortfall.
- `errors.csv`: invalid/unsupported request IDs and explanations.

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

## 11. Assumptions requiring verification
The assignment brief leaves some implementation details unspecified. These must be checked against the official visible expected outputs:
- Whether ₹35 applies only to each square foot above 100, or is intended as a different tier calculation.
- Whether indoor/outdoor rates represent separate fleet pools or shared physical cabinets.
- The exact rounding sequence for lines, totals and GST.
- Whether unavailable requests should show an indicative monetary quote.
- Exact output filenames, column order and text formatting.
- Whether malformed individual requests should stop the batch or be written to the error file.

## 12. Testing and reproducibility
Run tests with:
`python3 -m unittest discover -s tests -v`

Run the application with:
`python3 main.py`

The included rate-card and event-request CSVs are synthetic development fixtures and must be replaced by the official sample data before output matching.
