# E024-ECE-059 — LED Display and Signage Rental Quotation Engine

A command-line Python 3.10+ application for calculating LED video-wall rental quotations and checking fleet availability by pitch and date.

## Team
- Team ID: E024
- Members: Nandini Girish and Nikhil P Karamadi
- Problem: ECE-059

## Requirements
- Python 3.10 or newer
- No third-party Python packages required to run the application

## Run
From the repository root:

```bash
python3 main.py
```

Custom paths are supported:

```bash
python3 main.py --rate-card data/rate_card.csv --requests data/event_requests.csv --output output
```

The application writes:
- `output/quotations.csv`
- `output/availability.csv`
- `output/errors.csv`

## Run tests

```bash
python3 -m unittest discover -s tests -v
```

## Input formats

### Rate card
Required columns: `pitch,environment,rate_per_sq_ft_per_day,cabinet_area_sq_ft,fleet_cabinet_count`

### Event requests
Required columns: `request_id,client,width_ft,height_ft,pitch,environment,start_date,days,distance_km,power_source`

Use `INDOOR` or `OUTDOOR`, `GENERATOR` or `MAINS`, and ISO dates (`YYYY-MM-DD`).

**The included CSV values are illustrative development data only. Replace them with the official files supplied by 10 SECONDS.**

## Business-rule overview
- Cabinet count is rounded up.
- Billable area equals cabinet count times cabinet area.
- Weekend rental rate is 1.25× per Saturday/Sunday before the multi-day discount.
- Rental discount: 10% for 4–7 days, 20% for 8+ days.
- Setup: ₹4,000 through 100 sq ft, then ₹35 per sq ft above 100.
- Outdoor rigging: 20% of setup.
- Transport: ₹45 per km beyond 15 km, each way; return trip included.
- A billable wall above 300 sq ft requires a second vehicle.
- Generator: ₹2,500 per day.
- Operators: one per 150 sq ft or part thereof, ₹1,500 per operator per day.
- GST: 18%.
- Fleet bookings are accepted only if every date has sufficient cabinets. Rejected bookings reserve nothing.

## Important assumptions to confirm against official expected output
1. Requests are processed in input-file order.
2. Setup above 100 sq ft means ₹4,000 plus ₹35 for each sq ft above 100.
3. The second vehicle has the same transport charge as the first.
4. Monetary values use decimal arithmetic and `ROUND_HALF_UP`; each displayed line is rounded to whole rupees, and GST is calculated on the sum of rounded pre-tax lines.
5. Unavailable requests still receive an indicative quotation breakdown.
6. Fleet capacity is keyed by pitch and environment because the rate card is supplied for indoor/outdoor entries. If the official rules define a shared fleet across environments, update `src/fleet.py`.

These decisions are recorded in `decision_log.md` and should be reconciled with the visible expected output when supplied.

## Project layout
- `main.py`: command-line entry point
- `src/models.py`: data models
- `src/loader.py`: CSV parsing and validation
- `src/fleet.py`: date-by-date availability and reservation
- `src/quotation.py`: pricing rules
- `src/writer.py`: output CSV generation
- `tests/`: automated tests
- `design_document.md`: design document source
- `docs/design_document.pdf`: generated design document

