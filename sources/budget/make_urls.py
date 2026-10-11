"""Sweep-1 URL list for the budget dashboard: Google Flights, economy, 1 adult, THB, round trip, nonstop only,
airline filter = FD,XJ,D7,AK,VZ,VJ,SL,DD (repeated leg field f6), origin DMK and/or BKK (repeated f13).
Same idea as the TG sweep: one anchor URL per route/month/duration, opened in Google Flights, then read the
Date grid / Price graph around it. Anchors are shifted (±3 days) so the out AND return weekday exist for
at least one carrier on low-frequency routes."""
import json, subprocess, datetime as dt
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from excluded_airlines import is_excluded   # permanent rule: no Spring (9C/IJ) or 9 Air (AQ)
AL = ",".join(c for c in "FD,XJ,D7,AK,VZ,VJ,SL,DD".split(",") if not is_excluded(c))
D = {r["code"]: r for r in json.load(open("routes.json"))["routes"]}
ANCH = {  # month: {nights: (dep, label)}
 "2026-11": {2: ("2026-11-20", "Fri-Sun"), 3: ("2026-11-19", "Thu-Sun")},
 "2026-12": {2: ("2026-12-05", "Sat-Mon, long weekend (5 Dec Father's Day, Mon 7 Dec substitute holiday)"),
             3: ("2026-12-10", "Thu-Sun, long weekend (Thu 10 Dec Constitution Day)")},
 "2027-01": {2: ("2027-01-15", "Fri-Sun"), 3: ("2027-01-14", "Thu-Sun")},
}
TIER_A = ["HAN","SGN","DAD","TPE","NRT","KIX","KUL","SIN","HKG","MFM","CAN","TFU"]
TIER_B = ["PVG","KMG","CKG","CSX","HGH","SZX","ICN","FUK","CTS","PQC","CXR","PEN","DPS","RGN","CCU","DEL"]
DOW = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
OK = {"operating","resumes","seasonal","suspended","tentative"}
def days(s, wk):
    if not s or s == "daily" or (isinstance(wk, int) and wk >= 7 and "/" not in (s or "")): return set(range(7))
    return {DOW.index(x) for x in s.split("/") if x in DOW}
def carriers(code, date):
    out = []
    for c in D[code]["carriers"]:
        if c["status"] not in OK: continue
        if c["status"] == "tentative": continue
        if c.get("start") and date < dt.date.fromisoformat(c["start"]): continue
        od, rd = days(c.get("days"), c.get("per_week")), days(c.get("ret_days") or c.get("days"), c.get("per_week"))
        if code == "CTS" and date >= dt.date(2026, 12, 1): od = rd = set(range(7))   # XJ daily 1 Dec-27 Mar
        out.append((c, od, rd))
    return out
def pick(code, anchor, nights):
    a = dt.date.fromisoformat(anchor)
    for shift in [0, -1, 1, -2, 2, -3, 3]:
        d = a + dt.timedelta(days=shift); r = d + dt.timedelta(days=nights)
        cs = [c for c, od, rd in carriers(code, d) if d.weekday() in od and r.weekday() in rd]
        if cs: return d, r, shift, cs
    return None
lines, plan = [], []
for code in TIER_A + TIER_B:
    tier = "A" if code in TIER_A else "B"
    combos = [(m, n) for m in ANCH for n in (2, 3)] if tier == "A" else [("2026-11", 2), ("2026-12", 3), ("2027-01", 2)]
    for m, n in combos:
        anchor, why = ANCH[m][n]
        p = pick(code, anchor, n)
        if not p: plan.append((code, m, n, "NO VALID DATE")); continue
        d, r, shift, cs = p
        origins = sorted({c["origin"] for c in cs} | {c["origin"] for c, _, _ in carriers(code, d)})
        js = ["node", "tfs_lcc.js", ",".join(origins), code, str(d), str(r), AL]
        url = subprocess.check_output(js).decode().strip()
        org = "+".join(origins)
        lines.append(f"{code} {org} {d} {r} {url}")
        plan.append((code, m, n, f"{d} {DOW[d.weekday()]} -> {r} {DOW[r.weekday()]} ({n+1}D{n}N){' shifted %+d' % shift if shift else ''} via {'/'.join(sorted({c['carrier'] for c in cs}))}"))
open("urls-sweep1.txt", "w").write("\n".join(lines) + "\n")
with open("urls-sweep1-plan.md", "w") as f:
    f.write("# Sweep 1 plan (Nov 2026 – Jan 2027)\n\nFormat of urls-sweep1.txt: `<IATA> <AIRPORT-ORIGIN> <depart> <return> <url>` (origin `DMK+BKK` = both airports in one search).\n")
    f.write(f"Filter: airlines {AL} (f6 repeated per leg), nonstop only (leg f5=0), economy (f9=1), 1 adult (f8=1), round trip (f19=1), curr=THB.\n\n")
    f.write("Anchors: Nov Fri 20–Sun 22 / Thu 19–Sun 22 · Dec Sat 5–Mon 7 (long weekend) / Thu 10–Sun 13 (long weekend) · Jan Fri 15–Sun 17 / Thu 14–Sun 17.\n")
    f.write("Tier A = 6 URLs (3 months × 3D2N + 4D3N); Tier B = 3 URLs (Nov 3D2N, Dec 4D3N, Jan 3D2N). Read Date grid/Price graph around each anchor like the TG sweep.\n\n")
    f.write("| City | Month | Nights | Dates (carriers valid both ways) |\n|---|---|---|---|\n")
    for c, m, n, s in plan: f.write(f"| {c} | {m} | {n} | {s} |\n")
print(len(lines), "URLs"); print("\n".join(f"{c} {m} {n} {s}" for c, m, n, s in plan if "shifted" in s or "NO" in s))
