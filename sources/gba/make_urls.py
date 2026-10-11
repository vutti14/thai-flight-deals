#!/usr/bin/env python3
"""GBA sweep 1 URL list -> urls-sweep1.txt + urls-sweep1-plan.md
Line format: <IATA> <ECO|BIZ> <2D1N|3D2N|OW-OUT|OW-BACK> <depart> <return|-> <url>
All airlines except the excluded list in ../excluded_airlines.py (Spring 9C/IJ, 9 Air AQ — Google tfs has no exclude field, so build_gba.py drops their rows), nonstop, 1 adult, THB, origin BKK+DMK combined.
2D1N round trips carry Google's per-leg departure-hour window (leg f8/f9): out 05-10h (SZX 00-10h: only red-eyes before 11:00), back 18-23h.
Macau: round-trip 2D1N returned no priced pairing in testing (5 Dec: Air Macau has no MFM departure after 16:50 in winter; Air Macau + Thai AirAsia
show 'price unavailable'), but Thai Lion Air one-ways are priced (16 Jan: SL 10:15 out 2,745 + SL 22:05 back 2,535). So Macau Economy 2D1N =
two one-way URLs per date: OW-OUT (BKK/DMK->MFM, dep 05-10h, on the depart date) + OW-BACK (MFM->BKK/DMK, dep 17-23h, next day; 17h catches FD 17:55).
Macau Business 2D1N dropped (no business-class departure from MFM after 16:50 in winter); Macau 3D2N 23 Apr dropped (total 166)."""
import json, subprocess, datetime as dt
from collections import Counter
CITIES = ["HKG", "CAN", "SZX", "MFM"]
ECO_2D1N = [("2026-10-17","ปกติ (ตารางบินฤดูร้อน)"),("2026-10-24","หยุดยาวปิยมหาราช 23–25 ต.ค."),("2026-11-14","สุดสัปดาห์"),("2026-11-24","กลางสัปดาห์"),
  ("2026-12-05","วันพ่อ (หยุดยาว 5–7 ธ.ค.)"),("2026-12-10","วันรัฐธรรมนูญ"),("2026-12-19","สุดสัปดาห์ก่อนคริสต์มาส"),("2026-12-31","ข้ามปีใหม่"),
  ("2027-01-16","สุดสัปดาห์"),("2027-01-30","สุดสัปดาห์ก่อนตรุษจีน"),("2027-02-20","หยุดยาวมาฆบูชา 20–22 ก.พ."),("2027-03-13","สุดสัปดาห์"),("2027-04-06","วันจักรี")]
ECO_3D2N = [("2026-10-23","หยุดยาวปิยมหาราช"),("2026-11-06","สุดสัปดาห์"),("2026-11-18","กลางสัปดาห์"),("2026-12-05","วันพ่อ + ชดเชย"),("2026-12-10","วันรัฐธรรมนูญ (พฤ.–ส.)"),
  ("2026-12-24","คริสต์มาส"),("2026-12-31","ปีใหม่"),("2027-01-22","สุดสัปดาห์"),("2027-02-05","ตรุษจีน (คืนส่งท้าย 5 ก.พ., ชิวอิก 6 ก.พ.) — คาดราคาสูง"),
  ("2027-02-20","มาฆบูชา + ชดเชย"),("2027-03-12","สุดสัปดาห์"),("2027-04-04","วันจักรี (อา.–อ.)"),("2027-04-13","สงกรานต์ (อ.–พฤ.)"),("2027-04-23","สุดสัปดาห์หลังสงกรานต์")]
BIZ_2D1N = ["2026-10-24","2026-11-14","2026-12-19","2027-01-16","2027-02-20","2027-03-13"]
BIZ_3D2N = ["2026-10-23","2026-11-18","2026-12-10","2026-12-31","2027-02-05","2027-03-12","2027-04-13"]
def plus(d, n): return (dt.date.fromisoformat(d) + dt.timedelta(days=n)).isoformat()
rows = []   # (city, cabin, type, depart, return|-, url_spec)
for c in CITIES:
    for cab, A, B in (("ECO", [d for d, _ in ECO_2D1N], [d for d, _ in ECO_3D2N]), ("BIZ", BIZ_2D1N, BIZ_3D2N)):
        for d in A:
            if c == "MFM" and cab == "ECO":
                rows.append((c, cab, "OW-OUT", d, "-", dict(o=["BKK","DMK"], d=[c], a=d, b=None, wo=[5,10], wb=None)))
                rows.append((c, cab, "OW-BACK", plus(d, 1), "-", dict(o=[c], d=["BKK","DMK"], a=plus(d, 1), b=None, wo=[17,23], wb=None)))
            elif c == "MFM": continue
            else: rows.append((c, cab, "2D1N", d, plus(d, 1), dict(o=["BKK","DMK"], d=[c], a=d, b=plus(d, 1), wo=([0,10] if c == "SZX" else [5,10]), wb=[18,23])))
        for d in B:
            if c == "MFM" and cab == "ECO" and d == "2027-04-23": continue
            rows.append((c, cab, "3D2N", d, plus(d, 2), dict(o=["BKK","DMK"], d=[c], a=d, b=plus(d, 2), wo=None, wb=None)))
specs = [dict(r[5], k=3 if r[1] == "BIZ" else 1) for r in rows]
js = "const {url}=require('./tfs_gba.js');for(const s of " + json.dumps(specs) + ")console.log(url(s.o,s.d,s.a,s.b,s.k,[],s.wo,s.wb))"
urls = subprocess.check_output(["node", "-e", js]).decode().split()
assert len(urls) == len(rows)
with open("urls-sweep1.txt", "w") as f:
    for r, u in zip(rows, urls): f.write(f"{r[0]} {r[1]} {r[2]} {r[3]} {r[4]} {u}\n")
cnt = Counter((r[0], r[1], r[2]) for r in rows)
plan = ["# GBA sweep 1 — URL plan", "", f"**{len(rows)} URLs** in `urls-sweep1.txt` (format `<IATA> <ECO|BIZ> <2D1N|3D2N|OW-OUT|OW-BACK> <depart> <return|-> <url>`).", "",
  "| City | ECO 2D1N | ECO OW-OUT | ECO OW-BACK | ECO 3D2N | BIZ 2D1N | BIZ 3D2N | Total |", "|---|---|---|---|---|---|---|---|"]
for c in CITIES:
    v = [cnt[(c, "ECO", "2D1N")], cnt[(c, "ECO", "OW-OUT")], cnt[(c, "ECO", "OW-BACK")], cnt[(c, "ECO", "3D2N")], cnt[(c, "BIZ", "2D1N")], cnt[(c, "BIZ", "3D2N")]]
    plan.append(f"| {c} | " + " | ".join(map(str, v)) + f" | {sum(v)} |")
plan += ["", "- All airlines (no airline filter), nonstop only (leg f5=0), 1 adult, THB, origin BKK+DMK combined. Business dates ⊂ Economy dates (Economy and Business side by side).",
  "- **2D1N** round trips add Google's per-leg departure-hour window (leg f8 = earliest, f9 = latest hour, inclusive; verified live 11 Oct 2026): out leaves Bangkok 05:00–10:59, back leaves GBA 18:00–23:59, so Google's price is already a morning-out/late-back pairing.",
  "- **SZX 2D1N** outbound window is 00:00–10:59 because the only BKK→SZX flights before 11:00 are red-eyes (ZH 02:20, CZ 02:40) — flag them in the dashboard.",
  "- **MFM 2D1N** = `OW-OUT` (BKK/DMK→MFM, leaves 05–10h, on the depart date) + `OW-BACK` (MFM→BKK/DMK, leaves 17–23h, next day); the dashboard sums the two one-way fares. Reason: round-trip 2D1N to MFM returned no priced pairing in testing (Air Macau's last winter departure from MFM is 16:50; Air Macau and Thai AirAsia show 'price unavailable'), while Thai Lion Air one-ways are priced. 17h on the back leg so Thai AirAsia's 17:55 counts. No MFM Business 2D1N (no business-class departure from MFM after 16:50 in winter). MFM 3D2N 23 Apr dropped (total 166).",
  "- **3D2N** = no time window.", "- Record per row: airline, airport (BKK/DMK), out dep/arr, duration, price (THB; round trip per person, or one-way for OW rows) or 'Price unavailable' — same format as budget/raw/sweep1-google.md, plus the cabin.",
  "- Chinese New Year 2027 = Sat 6 Feb (eve Fri 5 Feb); mainland Spring Festival holiday expected ~5–13 Feb, HK/Macau 6–9 Feb. 5–7 Feb sampled on purpose to show the peak; regular weekends 30 Jan and 20 Feb on either side.",
  "- Summer-schedule rows: 17–18 Oct, 23–25 Oct (summer ends 24 Oct), and all April dates (summer from 28 Mar 2027).", "",
  "| Depart → return | Trip | Why | Economy | Business |", "|---|---|---|---|---|"]
for d, why in ECO_2D1N: plan.append(f"| {d} → {plus(d,1)} | 2D1N | {why} | 4 cities (MFM as 2 one-ways) | {'HKG/CAN/SZX' if d in BIZ_2D1N else '–'} |")
for d, why in ECO_3D2N: plan.append(f"| {d} → {plus(d,2)} | 3D2N | {why} | {'HKG/CAN/SZX' if d == '2027-04-23' else '4 cities'} | {'4 cities' if d in BIZ_3D2N else '–'} |")
open("urls-sweep1-plan.md", "w").write("\n".join(plan) + "\n")
print(len(rows)); print("\n".join(plan[4:10]))
