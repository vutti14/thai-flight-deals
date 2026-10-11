# Budget-airline fare dashboard: design proposal (not built yet)

Status: proposal, 11 Oct 2026. It shares the look of the Thai Airways dashboard (same CSS tokens, Thai labels, mobile-first) but is a separate page with its own data.
No personal data: no names, member numbers, miles or balances.

## Where to publish it
- Put it on the same public GitHub Pages repo **vutti14/thai-flight-deals**, under **`/budget/`**:
  `https://vutti14.github.io/thai-flight-deals/budget/`. The files would be `budget/index.html` and `budget/snapshots.js`. Push them to both `gh-pages` and `main`, the same way the TG site is published.
- Add a two-tab switch at the top of both pages: **การบินไทย** | **สายการบินราคาประหยัด**. Each page links to the other.
  `#` hash state, such as `#month=2026-12&n=12&org=dmk`, carries over to the other page where it applies.
- Before every push, run the same personal-data grep as the TG site (0 hits required).

## Who it is for
Picking a destination and dates to take a **staff or team group** (5 to 30 people) on a trip with an LCC.
The question it answers: "Where can the group go on date X, how much will it cost all together, and are the flight times reasonable?"

## Controls (sticky bar)
- **Number of travellers (N)**: a stepper with quick picks 1 / 5 / 10 / 15 / 20 / 30. It sets every "total" figure.
  It is saved in the hash `n=`. For N ≥ 10, show a note about the group booking channel (see the tips below).
- Month (Nov / Dec / Jan first, then Feb–Apr) · Duration **3D2N / 4D3N** · Region chips (China / HK-Macau / Taiwan / Japan / Korea / Vietnam / India / ASEAN).
- **Departure airport**: All / DMK / BKK. Coloured badges: DMK amber, BKK indigo. Thai AirAsia, AirAsia X, Thai Lion and Nok use DMK; Thai Vietjet and VietJet use BKK.
- Airline chips: FD · XJ · SL · VZ · VJ · DD. Toggles: **"ซ่อนไฟลท์ดึก/เช้ามืด"** (hide red-eye and very early flights) and **"รวมค่ากระเป๋า 20 กก."** (include 20 kg bag).

## Summary cards (top)
1. **ถูกสุดต่อคน** (cheapest per person): trip, airline, DMK/BKK, dates, ฿/person. A line underneath gives **× N = ฿ total**.
2. **ถูกสุดทั้งกลุ่ม รวมกระเป๋า** (cheapest for the whole group, bag included): fare plus a 20 kg checked bag per person, × N. This can change the ranking, because bag prices differ by airline.
3. **เวลาบินดีสุดในงบ** (best flight times within budget): the cheapest trip whose time score is "ดี". Daytime outbound, return lands before 22:00.
4. Per-region cards: **ถูกสุดจีน**, **ญี่ปุ่น**, **เวียดนาม** (two different cities, like the TG China card).
5. **เทียบการบินไทย** (compare with Thai Airways): for the same city and month, "pay ฿X/person more to fly TG with a 20–30 kg bag and a meal". This uses the TG public snapshot.

## Trip row / calendar cell
- City, airline badge(s), **DMK/BKK badge**, dates (3D2N / 4D3N), **฿/person**, **฿ total for N**.
- The fare is the base fare with **7 kg carry-on only**. Add a muted line: "+ กระเป๋า 20 กก. ~฿X/คน/เที่ยว".
  Per-airline figures come from a static reference table, marked "ประมาณการ เช็กราคาจริงตอนจอง" (estimate, check the real price when booking).
- **Flight-time quality** for each leg (out and return):
  - ดี (good): leaves 07:00–15:00, lands before 22:00.
  - พอใช้ (fair): leaves 05:00–07:00 or 15:00–20:00.
  - ดึก (red-eye): leaves 20:00–05:00, or lands after midnight.

  Many LCC routes are red-eye only (BKK→NRT VZ 23:55, DMK→TFU FD 22:05, India late evenings, Japan XJ 00:45–01:55), so this matters for groups.
- Weekday warning when a route is not daily, for example "บินเฉพาะ อ./พฤ./ส./อา.". The same approach is used for TG XMN.
- Status chips from routes.json: **เริ่มบิน 17 ธ.ค.** (resumes 17 Dec), **เช่าเหมาลำ** (charter), **ยังไม่เปิดขาย** (not on sale yet), **NEW**.
- "Seats: price for 1 seat" caveat icon. LCC fare buckets are small, so 10+ seats often price higher than the single-seat fare shown.

## Group-travel tips panel (collapsible, Thai)
- Price check for N people: search with the real head-count, or in blocks of 4–6. The lowest bucket may only have a few seats.
- For 10+ people, use the airline's **group booking** channel (AirAsia, Thai Lion and Vietjet each have group-request forms). Compare it with booking in blocks. Note the name-change and deposit rules.
- Bags: buying in advance online is much cheaper than at the airport. Bag allowance is per person and cannot be pooled. Watch the 7 kg cabin limit.
- Seats together: seat selection costs extra. Check in early or buy seats for the group.
- DMK vs BKK: DMK has no rail link to BKK. If someone in the group connects to TG or another airline, allow 2–3 hours by road. DMK Terminal 1 is international.
- Return the evening before a workday: avoid the last flight of the day. Delays are common, and an LCC usually will not reroute you onto another airline.
- Payment card fees and fare-bundle names (Value Pack / Premium Flex / Eco/Deluxe) differ by airline. The total shown is approximate.

## Data model (snapshot per sweep)
Same structure as the TG snapshots, plus these fields per trip:
`airline` (FD/XJ/SL/VZ/VJ/DD), `origin` (DMK/BKK), `out_dep/out_arr/ret_dep/ret_arr`, `nights`, `price_pp`, `bag_incl_kg` (0/7/20),
`price_source` (`google` | `airasia.com` | `lionairthai.com` | `vietjetair.com`), `approx`, `checked_at`. Route metadata comes from `budget/routes.json`.

## Important data-source finding (affects the fare sweep)
Google Flights live checks were run on 11 Oct 2026 using the URLs in urls-sweep1.txt:
- **Thai Vietjet (VZ) / VietJet (VJ)**: priced on most routes, for example PVG, HGH, NRT, KIX, ICN, HAN, SGN.
  **But VZ BKK–DAD, PQC and CXR do not appear at all.**
- **Thai AirAsia (FD) / AirAsia X (XJ)**: schedules are listed but show **"Total price is unavailable"**. Google has no fares for them.
- **Thai Lion Air (SL)**: priced on a few routes (HGH, TPE, KHH) and missing on others (PVG, CAN, HKG and more).

So: the Google Flights sweep gives VZ/VJ prices and some SL prices, plus schedule and time confirmation for FD/XJ.
FD and XJ fares need **airasia.com**: its low-fare calendar can be read by a browser subagent per route and month.
SL fares need **lionairthai.com**. Record the source per price.
