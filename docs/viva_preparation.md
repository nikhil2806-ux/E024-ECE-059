# Viva preparation — E024-ECE-059

Use this as a learning guide, not a script to memorise. Both team members should be able to explain the design and trace one request through the code.

## 1. Project overview
**Q: What problem does the project solve?**  
A: It automates LED video-wall rental quotations and checks whether enough cabinets of the requested pixel pitch are available on every event date.

**Q: Why is it a command-line application?**  
A: The assignment specifies a no-UI command-line engine. Inputs and outputs are files, and `commands.txt` defines the processing sequence.

**Q: What are the main modules?**  
A: `main.py` executes commands; `loader.py` validates CSV inputs; `models.py` defines data structures; `quotation.py` calculates prices; `fleet.py` manages capacity; `writer.py` creates output CSVs.

## 2. Pricing and business rules
**Q: Why use ceiling for cabinet count?**  
A: A partial cabinet cannot satisfy a physical wall requirement, so any fraction requires one additional cabinet.

**Q: What is billable area?**  
A: Whole cabinet count multiplied by the area of one cabinet. It can exceed requested wall area.

**Q: How are weekends handled?**  
A: Each Saturday and Sunday rental day is multiplied by 1.25 before daily charges are summed and the duration discount is applied.

**Q: Is the duration discount applied to the entire quotation?**  
A: No. It applies to gross rental only, not setup, transport, generator, operator charges or GST.

**Q: What happens at exactly 100 sq ft?**  
A: Setup remains the flat ₹4,000. The excess-area formula applies only above 100 sq ft.

**Q: What happens at exactly 300 sq ft?**  
A: One vehicle. The second vehicle is required only when billable area is strictly greater than 300 sq ft.

**Q: Why does exactly 15 km have no transport charge?**  
A: Transport is charged only for distance beyond 15 km.

**Q: How are operators calculated?**  
A: `ceil(billable_area / 150)` operators, each charged ₹1,500 per event day.

**Q: How is GST calculated?**  
A: Round each charge line half-up to a whole rupee, add rounded lines for subtotal, then calculate 18% GST on that subtotal and round GST half-up.

## 3. Fleet logic
**Q: What is the fleet key?**  
A: `(pitch, date)`. Indoor and outdoor do not have separate fleet pools.

**Q: Why check all dates before reserving?**  
A: To avoid partial bookings. A request is accepted only if every date has sufficient capacity.

**Q: What happens to an unavailable request?**  
A: It still gets a full indicative quotation, but reserves no cabinets.

**Q: How is shortfall calculated?**  
A: For each event date, calculate held cabinets + required cabinets − fleet capacity. The reported shortfall is the largest positive result across the event dates.

**Q: Why does processing order matter?**  
A: Earlier available requests reserve capacity first. The official sample pack requires requests to be processed in file/received order.

## 4. Input validation and command processing
**Q: What does the loader validate?**  
A: Required columns and values, duplicate headers, supported pitch and environment, unique EVR-nnn IDs, dates, dimensions, days, distance, power source, rates, cabinet area and fleet count.

**Q: Why validate `received_date`, `event_name`, and `venue` if they do not affect price?**  
A: They are required by the official CSV schema. The loader validates them, even though the calculation model does not need to retain them.

**Q: What does `commands.txt` do?**  
A: It controls the sequence of loading, quoting and output generation. Unknown commands, incorrect argument counts and invalid command order are rejected.

## 5. Python concepts
Be ready to explain `dataclass`, `Decimal`, `ROUND_HALF_UP`, `csv.DictReader`, `csv.DictWriter`, `datetime.strptime`, `math.ceil`, `unittest`, and `pathlib.Path`.

## 6. Live coding exercises
Practise implementing or explaining:
1. Change a distance and predict transport charge.
2. Change a wall size and calculate cabinets and billable area by hand.
3. Explain why `>` rather than `>=` is used for the 300 sq ft second-vehicle threshold.
4. Add a test for 151 sq ft billable area.
5. Add a test for an invalid power source.
6. Explain how the fleet manager prevents partial reservation on a multi-day failure.
7. Explain how command order is validated.

## 7. Team practice
Both members should understand the complete project. For rehearsal, one person can lead the command interpreter, loader and data models; the other can lead quotation calculations, fleet logic and output writer. Swap roles and question each other before the viva.
