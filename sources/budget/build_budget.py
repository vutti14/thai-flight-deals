#!/usr/bin/env python3
"""Build the public budget-airline dashboard -> ../site/budget/index.html (self-contained, data inline).
Inputs: raw/sweep1-parsed.json (from parse_sweep.py), routes.json, ../data/snapshots/*-full.json (public TG economy)."""
import json, pathlib, re
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from excluded_airlines import is_excluded   # permanent rule: no Spring (9C/IJ) or 9 Air (AQ)
ROOT = pathlib.Path(__file__).resolve().parent
P = json.loads((ROOT / "raw/sweep1-parsed.json").read_text())
R = json.loads((ROOT / "routes.json").read_text())
TG = json.loads((ROOT.parent / "data/snapshots/2026-10-09-full.json").read_text())

CITY = {r["code"]: dict(th=r["city_th"], en=r["city"], country=r["country"], region=r["region"]) for r in R["routes"]}
COUNTRY_TH = {"China":"จีน","Hong Kong":"ฮ่องกง","Macau":"มาเก๊า","Taiwan":"ไต้หวัน","Japan":"ญี่ปุ่น","South Korea":"เกาหลีใต้","Vietnam":"เวียดนาม",
  "India":"อินเดีย","Myanmar":"เมียนมา","Singapore":"สิงคโปร์","Malaysia":"มาเลเซีย","Indonesia":"อินโดนีเซีย"}
used = sorted({e["code"] for e in P["priced"] + P["unpriced"] + P["empty"]})
cities = {c: dict(CITY[c], country_th=COUNTRY_TH.get(CITY[c]["country"], CITY[c]["country"])) for c in used}
# route info per (code, carrier) for status tags + typical return times
rinfo = {}
for r in R["routes"]:
    if r["code"] not in used: continue
    for c in r["carriers"]:
        rinfo[f'{r["code"]}|{c["carrier"]}'] = {k: c.get(k) for k in ("status", "start", "end", "days", "per_week", "ret_times", "out_times", "note", "origin")}
# TG public economy: cheapest per city per month
TGMAP = {"NRT": "TYO"}
tg = {}
for r in TG["routes"]:
    for m, v in (r.get("monthly_cheapest") or {}).items():
        tg[f'{r["code"]}|{m}'] = {"p": v["price"], "dep": v["dep"], "ret": v["ret"], "approx": bool(v.get("approx"))}
tgx = {f'{t["code"]}|{t["dep"]}|{t["ret"]}': t["price"] for t in TG["trips"]}
def dmin(s):
    h = re.search(r"(\d+) hr", s); m = re.search(r"(\d+) min", s)
    return (int(h.group(1)) if h else 0) * 60 + (int(m.group(1)) if m else 0)
opts = []
for e in P["priced"]:
    if is_excluded(e["al"]) or is_excluded(name=e.get("alname")): continue
    opts.append(dict(c=e["code"], d=e["dep"], r=e["ret"], a=e["al"], o=e["org"], od=e["out_dep"], oa=e["out_arr"], nx=e["out_next"],
                     m=dmin(e["dur"]), p=e["price"], u=e["url"]))
sched = [dict(c=e["code"], d=e["dep"], r=e["ret"], a=e["al"], o=e["org"], od=e["out_dep"], oa=e["out_arr"], nx=e["out_next"], m=dmin(e["dur"]), u=e["url"]) for e in P["unpriced"]]
empty = [dict(c=e["code"], d=e["dep"], r=e["ret"], u=e["url"]) for e in P["empty"]]
DATA = dict(captured="2026-10-11", opts=opts, sched=sched, empty=empty, cities=cities, rinfo=rinfo, tg=tg, tgx=tgx, tgmap=TGMAP,
            tg_snap=TG["searched_at"])
js = json.dumps(DATA, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/").replace("&", "\\u0026")
from time_bands import js_snippet
html = (ROOT / "budget_template.html").read_text().replace("/*__DATA__*/null", js).replace("/*__BANDS__*/", js_snippet())
out = ROOT.parent / "site" / "budget"; out.mkdir(parents=True, exist_ok=True)
(out / "index.html").write_text(html, encoding="utf-8")
print("built", out / "index.html", len(opts), "options,", len({(o["c"], o["d"], o["r"]) for o in opts}), "priced searches,", len({o["c"] for o in opts}), "cities")
