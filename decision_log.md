# Decision Log — E024-ECE-059

| ID | Decision | Reason / status |
|---|---|---|
| D-01 | Process event requests in CSV file order. | Official sample-pack instructions specify received order. |
| D-02 | An event occupies every consecutive calendar date from `start_date` for `days` days. | Explicit official sample-pack convention. |
| D-03 | Apply the 1.25× weekend multiplier to each Saturday/Sunday rental day before the duration discount. | Assignment brief and official planted four-day scenario. |
| D-04 | Apply multi-day discounts to gross rental only. | Official README describes discounting the rental sum. |
| D-05 | For billable area above 100 sq ft, setup is ₹4,000 + ₹35 × (billable area − 100). | Explicit official sample-pack convention. |
| D-06 | Transport is ₹45 × 2 × (distance − 15) for distances above 15 km. | Official sample-pack convention. |
| D-07 | Billable area strictly above 300 sq ft doubles transport for the second vehicle. | Official sample-pack convention; exactly 300 sq ft remains one vehicle. |
| D-08 | Outdoor setup is increased by 20%. | Assignment rule; applied to setup as a whole. |
| D-09 | Operator count is ceiling(billable area / 150); charge is count × ₹1,500 × days. | Official sample-pack convention. |
| D-10 | Check fleet for every date before reserving; failed requests reserve no cabinets. | Official sample-pack convention. |
| D-11 | Fleet is shared per pitch, not split by environment. | Official README defines fleet usage per pitch and the rate card has one row per pitch. |
| D-12 | Calculate monetary lines with `Decimal`; round each line half-up to whole rupees. | Official sample-pack rounding convention. |
| D-13 | Subtotal is the sum of rounded lines; GST is 18% of subtotal rounded half-up. | Explicit official sample-pack convention. |
| D-14 | An unavailable request still receives a full indicative quotation. | Explicit official sample-pack output convention. |
| D-15 | Shortfall is the largest `(cabinets already held + cabinets needed − fleet)` across the event dates. | Explicit official sample-pack convention. |
| D-16 | Environment is selected from the rate-card entry matching the request pitch. | Official `requests.csv` has no environment column; each pitch maps to one rate-card row. |
| D-17 | Write only `quotations.csv` and `fleet_usage.csv`, using the official column order. | Explicit official evaluation output specification. |
| D-18 | Execute each command immediately in file order; reject unknown commands, invalid arguments and invalid command sequencing. | Audit improvement to match the official command-file contract. |
| D-19 | Validate all documented request columns, ISO dates, EVR-nnn IDs, integer day/distance fields and allowed values before quoting. | Audit improvement to reject malformed input clearly. |
| D-20 | Write quotations and fleet usage only when their respective PRINT commands are reached. | Audit improvement to make PRINT commands control output generation. |

