# Decision Log — E024-ECE-059

| ID | Decision | Reason / status |
|---|---|---|
| D-01 | Process valid event requests in input-file order. | Gives deterministic booking priority; confirm if the official output specifies another order. |
| D-02 | Rental dates are consecutive calendar dates including the start date. | Matches ordinary event-duration interpretation. |
| D-03 | Weekend multiplier is applied to each Saturday/Sunday rental day before discount. | Explicit requirement in assignment brief. |
| D-04 | Multi-day discounts apply to rental charges only. | The brief says the rental sum is discounted; other lines are not included. |
| D-05 | Setup above 100 sq ft is ₹4,000 plus ₹35 per excess sq ft. | Interprets “₹4,000 flat up to 100 sq ft, ₹35 per sq ft beyond.” Confirm against sample output. |
| D-06 | Transport uses excess distance beyond 15 km, charged ₹45/km each way, doubled for return. | Explicit requirement. |
| D-07 | A billable area strictly greater than 300 sq ft requires two vehicles. | Explicit threshold wording “above 300.” |
| D-08 | Outdoor rigging equals 20% of setup. | Explicit requirement; calculated from base setup. |
| D-09 | Operators are rounded up in groups of 150 sq ft and charged per day. | Explicit requirement. |
| D-10 | Failed multi-day fleet checks reserve no cabinets on any date. | Explicit requirement; implemented atomically. |
| D-11 | Requests are unavailable if any event date exceeds fleet capacity. | Explicit requirement. |
| D-12 | Monetary arithmetic uses `Decimal`; whole-rupee rounding uses `ROUND_HALF_UP`. | Avoids binary floating-point surprises; rounding sequence must be checked against visible expected output. |
| D-13 | Displayed pre-tax charge lines are rounded first; pre-tax total is their sum; GST is 18% of that total rounded to a whole rupee. | Deterministic interpretation of “all lines rounded”; confirm against expected output. |
| D-14 | An unavailable request still gets an indicative quote. | Brief requires quote marked unavailable but does not explicitly say to suppress amounts. Confirm output format. |
| D-15 | Fleet is keyed by pitch and environment. | Rate-card entries include both; confirm whether indoor/outdoor cabinets share the same physical fleet. |
| D-16 | Unknown pitch/environment combinations are reported in `errors.csv` and are not quoted. | Prevents guessing a rate. |
| D-17 | Sample CSV data is illustrative, not official. | Replace with official Week 2 data and compare output before final submission. |
