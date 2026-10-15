#!/usr/bin/env python3
"""raw/sweep2-labels.json (sweep_curl.py) -> raw/sweep2-google.md in the sweep1-google.md block format read by build_gba.py.
Excluded carriers (../excluded_airlines.py) are omitted here so the public raw file never lists them (build_gba.py drops them too)."""
import json, re, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from excluded_airlines import is_excluded
CAPTURED = "2026-10-15"
D = json.loads((ROOT / "raw/sweep2-labels.json").read_text())
APT = [("Suvarnabhumi", "BKK"), ("Don Mueang", "DMK"), ("Hong Kong", "HKG"), ("Baiyun", "CAN"), ("Guangzhou", "CAN"), ("Bao'an", "SZX"), ("Bao’an", "SZX"), ("Shenzhen", "SZX"), ("Macau", "MFM"), ("Macao", "MFM")]
def apt(n):
    for k, c in APT:
        if k in n: return c
    raise SystemExit("unknown airport " + n)
R = re.compile(r"(?:From (\d+) Thai baht[^.]*|Total price is unavailable)\. (Nonstop|\d+ stops?) flight with (.+?)\. Leaves (.+?) at (\d+:\d+\s?[AP]M) on (\w+), [^.]*? and arrives at (.+?) at (\d+:\d+\s?[AP]M) on (\w+), .*?Total duration ([^.]+)\.")
def hm(t): return t.replace("\u202f", " ").strip()
out = [f"# Sweep 2 — Google Flights raw results (captured {CAPTURED}, curl HTML aria-labels; no browser)",
       "Format per row: airline | route | outbound depart–arrive | duration | stops | price per person (RT total for RT, one-way for OW)", ""]
stats = dict(blocks=0, rows=0, priced=0, excluded=0, stops=0, empty=0, nomatch=0)
def key(k): return int(k.split()[0])
for k in sorted(D, key=key):
    v = D[k]; rows = []
    for l in v["labels"]:
        m = R.search(l.replace("\u202f", " "))
        if not m: stats["nomatch"] += 1; continue
        price, stops, al, frm, dep, dday, to, arr, aday, dur = m.groups()
        if stops != "Nonstop": stats["stops"] += 1; continue
        if is_excluded(name=al): stats["excluded"] += 1; continue
        nx = "+1" if dday != aday else ""
        rows.append(f"{al} | {apt(frm)}–{apt(to)} | {hm(dep)}–{hm(arr)}{nx} | {dur.strip()} | Nonstop | " + (f"THB {int(price):,}" if price else "price unavailable"))
    rows = list(dict.fromkeys(rows))
    title = v["title"].replace(" | Google Flights", "").strip() or "(no title)"
    lvl = f" — Prices are currently {v['level']}" if v.get("level") else ""
    out.append(f"## {k}")
    out.append(f"title ok: {title}{lvl}{'' if rows else ' — NO RESULTS'} | Google Flights — {len(rows)} results")
    out += rows; out.append("")
    stats["blocks"] += 1; stats["rows"] += len(rows); stats["priced"] += sum(1 for r in rows if "THB" in r); stats["empty"] += (not rows)
(ROOT / "raw/sweep2-google.md").write_text("\n".join(out) + "\n")
print(stats)
