# GBA sweep 1 — URL plan

**166 URLs** in `urls-sweep1.txt` (format `<IATA> <ECO|BIZ> <2D1N|3D2N|OW-OUT|OW-BACK> <depart> <return|-> <url>`).

| City | ECO 2D1N | ECO OW-OUT | ECO OW-BACK | ECO 3D2N | BIZ 2D1N | BIZ 3D2N | Total |
|---|---|---|---|---|---|---|---|
| HKG | 13 | 0 | 0 | 14 | 6 | 7 | 40 |
| CAN | 13 | 0 | 0 | 14 | 6 | 7 | 40 |
| SZX | 13 | 0 | 0 | 14 | 6 | 7 | 40 |
| MFM | 0 | 13 | 13 | 13 | 0 | 7 | 46 |

- All airlines (no airline filter), nonstop only (leg f5=0), 1 adult, THB, origin BKK+DMK combined. Business dates ⊂ Economy dates (Economy and Business side by side).
- **2D1N** round trips add Google's per-leg departure-hour window (leg f8 = earliest, f9 = latest hour, inclusive; verified live 11 Oct 2026): out leaves Bangkok 05:00–10:59, back leaves GBA 18:00–23:59, so Google's price is already a morning-out/late-back pairing.
- **SZX 2D1N** outbound window is 00:00–10:59 because the only BKK→SZX flights before 11:00 are red-eyes (ZH 02:20, CZ 02:40) — flag them in the dashboard.
- **MFM 2D1N** = `OW-OUT` (BKK/DMK→MFM, leaves 05–10h, on the depart date) + `OW-BACK` (MFM→BKK/DMK, leaves 17–23h, next day); the dashboard sums the two one-way fares. Reason: round-trip 2D1N to MFM returned no priced pairing in testing (Air Macau's last winter departure from MFM is 16:50; Air Macau and Thai AirAsia show 'price unavailable'), while Thai Lion Air one-ways are priced. 17h on the back leg so Thai AirAsia's 17:55 counts. No MFM Business 2D1N (no business-class departure from MFM after 16:50 in winter). MFM 3D2N 23 Apr dropped (total 166).
- **3D2N** = no time window.
- Record per row: airline, airport (BKK/DMK), out dep/arr, duration, price (THB; round trip per person, or one-way for OW rows) or 'Price unavailable' — same format as budget/raw/sweep1-google.md, plus the cabin.
- Chinese New Year 2027 = Sat 6 Feb (eve Fri 5 Feb); mainland Spring Festival holiday expected ~5–13 Feb, HK/Macau 6–9 Feb. 5–7 Feb sampled on purpose to show the peak; regular weekends 30 Jan and 20 Feb on either side.
- Summer-schedule rows: 17–18 Oct, 23–25 Oct (summer ends 24 Oct), and all April dates (summer from 28 Mar 2027).

| Depart → return | Trip | Why | Economy | Business |
|---|---|---|---|---|
| 2026-10-17 → 2026-10-18 | 2D1N | ปกติ (ตารางบินฤดูร้อน) | 4 cities (MFM as 2 one-ways) | – |
| 2026-10-24 → 2026-10-25 | 2D1N | หยุดยาวปิยมหาราช 23–25 ต.ค. | 4 cities (MFM as 2 one-ways) | HKG/CAN/SZX |
| 2026-11-14 → 2026-11-15 | 2D1N | สุดสัปดาห์ | 4 cities (MFM as 2 one-ways) | HKG/CAN/SZX |
| 2026-11-24 → 2026-11-25 | 2D1N | กลางสัปดาห์ | 4 cities (MFM as 2 one-ways) | – |
| 2026-12-05 → 2026-12-06 | 2D1N | วันพ่อ (หยุดยาว 5–7 ธ.ค.) | 4 cities (MFM as 2 one-ways) | – |
| 2026-12-10 → 2026-12-11 | 2D1N | วันรัฐธรรมนูญ | 4 cities (MFM as 2 one-ways) | – |
| 2026-12-19 → 2026-12-20 | 2D1N | สุดสัปดาห์ก่อนคริสต์มาส | 4 cities (MFM as 2 one-ways) | HKG/CAN/SZX |
| 2026-12-31 → 2027-01-01 | 2D1N | ข้ามปีใหม่ | 4 cities (MFM as 2 one-ways) | – |
| 2027-01-16 → 2027-01-17 | 2D1N | สุดสัปดาห์ | 4 cities (MFM as 2 one-ways) | HKG/CAN/SZX |
| 2027-01-30 → 2027-01-31 | 2D1N | สุดสัปดาห์ก่อนตรุษจีน | 4 cities (MFM as 2 one-ways) | – |
| 2027-02-20 → 2027-02-21 | 2D1N | หยุดยาวมาฆบูชา 20–22 ก.พ. | 4 cities (MFM as 2 one-ways) | HKG/CAN/SZX |
| 2027-03-13 → 2027-03-14 | 2D1N | สุดสัปดาห์ | 4 cities (MFM as 2 one-ways) | HKG/CAN/SZX |
| 2027-04-06 → 2027-04-07 | 2D1N | วันจักรี | 4 cities (MFM as 2 one-ways) | – |
| 2026-10-23 → 2026-10-25 | 3D2N | หยุดยาวปิยมหาราช | 4 cities | 4 cities |
| 2026-11-06 → 2026-11-08 | 3D2N | สุดสัปดาห์ | 4 cities | – |
| 2026-11-18 → 2026-11-20 | 3D2N | กลางสัปดาห์ | 4 cities | 4 cities |
| 2026-12-05 → 2026-12-07 | 3D2N | วันพ่อ + ชดเชย | 4 cities | – |
| 2026-12-10 → 2026-12-12 | 3D2N | วันรัฐธรรมนูญ (พฤ.–ส.) | 4 cities | 4 cities |
| 2026-12-24 → 2026-12-26 | 3D2N | คริสต์มาส | 4 cities | – |
| 2026-12-31 → 2027-01-02 | 3D2N | ปีใหม่ | 4 cities | 4 cities |
| 2027-01-22 → 2027-01-24 | 3D2N | สุดสัปดาห์ | 4 cities | – |
| 2027-02-05 → 2027-02-07 | 3D2N | ตรุษจีน (คืนส่งท้าย 5 ก.พ., ชิวอิก 6 ก.พ.) — คาดราคาสูง | 4 cities | 4 cities |
| 2027-02-20 → 2027-02-22 | 3D2N | มาฆบูชา + ชดเชย | 4 cities | – |
| 2027-03-12 → 2027-03-14 | 3D2N | สุดสัปดาห์ | 4 cities | 4 cities |
| 2027-04-04 → 2027-04-06 | 3D2N | วันจักรี (อา.–อ.) | 4 cities | – |
| 2027-04-13 → 2027-04-15 | 3D2N | สงกรานต์ (อ.–พฤ.) | 4 cities | 4 cities |
| 2027-04-23 → 2027-04-25 | 3D2N | สุดสัปดาห์หลังสงกรานต์ | HKG/CAN/SZX | – |
