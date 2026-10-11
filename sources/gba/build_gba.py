#!/usr/bin/env python3
"""Build the public Zone GBA dashboard -> ../site/gba/index.html (self-contained, data inline).
Inputs: raw/sweep1-google.md (Google Flights results, index = line number in urls-sweep1.txt; a later block with the same index
(recheck) replaces the earlier one), urls-sweep1.txt, routes.json, tfs_gba.js (Business links for Economy-only dates)."""
import json, re, pathlib, subprocess, statistics, datetime as dt, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from excluded_airlines import is_excluded   # permanent rule: Spring (9C/IJ) and 9 Air (AQ) rows are dropped
ROOT = pathlib.Path(__file__).resolve().parent
CAPTURED = "2026-10-11"
R = json.loads((ROOT / "routes.json").read_text())
U = [l.split() for l in (ROOT / "urls-sweep1.txt").read_text().splitlines() if l.strip()]
UK = {tuple(x[:4]): x for x in U}
NAMES = [("Cathay Pacific","CX"),("Hong Kong Express","UO"),("Hong Kong Airlines","HX"),("Greater Bay Airlines","HB"),("Emirates","EK"),("United","UA"),
 ("Thai Lion Air","SL"),("Thai AirAsia","FD"),("Thai Vietjet","VZ"),("THAI","TG"),("China Southern","CZ"),("China Eastern","MU"),("Shenzhen","ZH"),
 ("Kenya Airways","KQ"),("Air Macau","NX")]
def al(name):
    for n, c in NAMES:
        if name.startswith(n): return c, name[len(n):].strip(" ,")
    raise SystemExit("unknown airline " + name)
def h24(t):
    m = re.match(r"(\d+):(\d+)\s*([AP]M)", t.strip()); h, mi, ap = m.groups(); return f"{int(h) % 12 + (12 if ap == 'PM' else 0):02d}:{mi}"
def dmin(s):
    h = re.search(r"(\d+) hr", s); m = re.search(r"(\d+) min", s); return (int(h.group(1)) if h else 0) * 60 + (int(m.group(1)) if m else 0)
def mins(t): h, m = map(int, t.split(":")); return h * 60 + m
# flight-number lookup from routes.json
FL = {}; BACK = {}
for r in R["routes"]:
    for c in r["carriers"]:
        if is_excluded(c["code"]): continue
        for f in c["flights"]:
            for season in ("winter", "summer"):
                if f.get(season) and f.get("flt"):
                    dep, arr = f[season].split("→")
                    FL.setdefault((r["code"], f["dir"], c["code"], season), []).append((dep, f["flt"]))
                    if f["dir"] == "back" and mins(dep) >= (17 * 60 if r["code"] == "MFM" else 18 * 60):
                        BACK.setdefault(r["code"], {}).setdefault(season, {}).setdefault(c["code"], []).append([f["flt"], dep, arr, c["bangkok_airport"]])
def season(d): return "summer" if d < "2026-10-25" or d >= "2027-03-28" else "winter"
def fltno(city, direction, code, dep, d):
    best = None
    for s in (season(d), "winter" if season(d) == "summer" else "summer"):
        for t, fn in FL.get((city, direction, code, s), []):
            dd = abs(mins(t) - mins(dep))
            if dd <= 10 and (best is None or dd < best[0]): best = (dd, fn)
        if best: return best[1]
    return None
# parse sweep
S = {}; DROPPED = []
blocks = re.split(r"^## ", (ROOT / "raw/sweep1-google.md").read_text(), flags=re.M)[1:]
for b in blocks:
    lines = b.split("\n"); hd = lines[0].split()
    idx = tuple(hd[1:5]); city, cab, typ, dep, ret, url = UK[idx]   # match by city/cabin/type/date (sweep order differs from file order)
    opts = []
    for l in lines[1:]:
        f = l.split(" | ")
        if len(f) < 5 or l.startswith(("Bangkok and", "Macao to", "title")): continue
        if is_excluded(name=f[0]): DROPPED.append((city, cab, typ, dep, f[0])); continue
        code, cs = al(f[0])
        if is_excluded(code): DROPPED.append((city, cab, typ, dep, f[0])); continue
        org, dst = f[1].split("–")
        a, z = f[2].split("–"); nx = "+1" in z; z = z.replace("+1", "")
        p = f[-1].strip(); price = int(p.replace("THB", "").replace(",", "").strip()) if p.startswith("THB") else None
        od, oa = h24(a), h24(z); legd = dep
        direction = "out" if org in ("BKK", "DMK") else "back"
        opts.append(dict(a=code, cs=cs, o=org if direction == "out" else dst, od=od, oa=oa, nx=nx, m=dmin(f[3]), p=price,
                         f=fltno(city, direction, code, od, legd)))
    pr = [o["p"] for o in opts if o["p"]]
    if len(pr) >= 3 and cab == "ECO":
        med = statistics.median(pr)
        for o in opts:
            if o["p"] and o["p"] > 4 * med: o["x"] = 1   # outlier (e.g. Spring 117,814 on an economy search)
    S[idx] = dict(c=city, cab=cab, t=typ, d=dep, r=None if ret == "-" else ret, u=url, o=opts, typical="typical" in lines[0] + lines[1] if len(lines) > 1 else False)
# trips
def plus(d, n): return (dt.date.fromisoformat(d) + dt.timedelta(days=n)).isoformat()
trips = {}; extra_biz = []
for i, s in S.items():
    if s["t"] in ("OW-OUT", "OW-BACK"):
        d = s["d"] if s["t"] == "OW-OUT" else plus(s["d"], -1)
        t = trips.setdefault((s["c"], "2D1N", d), dict(c=s["c"], t="2D1N", d=d, r=plus(d, 1)))
        t.setdefault("eco", {"ow": {}})["ow"]["out" if s["t"] == "OW-OUT" else "back"] = dict(u=s["u"], o=s["o"])
    else:
        t = trips.setdefault((s["c"], s["t"], s["d"]), dict(c=s["c"], t=s["t"], d=s["d"], r=s["r"]))
        t["eco" if s["cab"] == "ECO" else "biz"] = dict(u=s["u"], o=s["o"])
for t in trips.values():
    if "biz" not in t and not (t["c"] == "MFM" and t["t"] == "2D1N"):
        win = ([0, 10] if t["c"] == "SZX" else [5, 10], [18, 23]) if t["t"] == "2D1N" else (None, None)
        extra_biz.append((t, dict(o=["BKK", "DMK"], d=[t["c"]], a=t["d"], b=t["r"], k=3, wo=win[0], wb=win[1])))
js = "const {url}=require('./tfs_gba.js');for(const s of " + json.dumps([x[1] for x in extra_biz]) + ")console.log(url(s.o,s.d,s.a,s.b,s.k,[],s.wo,s.wb))"
for (t, _), u in zip(extra_biz, subprocess.check_output(["node", "-e", js], cwd=ROOT).decode().split()): t["bizu"] = u
cities = {r["code"]: dict(en=r["city"], th=r["city_th"]) for r in R["routes"]}
sched = []
for r in R["routes"]:
    sched.append(dict(c=r["code"], news=r["news"], fit=r["fit_2d1n"],
        car=[dict(code=c["code"], kind=c["kind"], apt=c["bangkok_airport"], biz=c["business"],
                  fl=[{k: f.get(k) for k in ("dir", "flt", "winter", "summer", "freq", "fits_2d1n", "aircraft", "start", "note")} for f in c["flights"]]) for c in r["carriers"]]))
empty = [dict(c=s["c"], cab=s["cab"], t=s["t"], d=s["d"], r=s["r"], u=s["u"]) for s in S.values() if not s["o"]]
DATA = dict(captured=CAPTURED, trips=sorted(trips.values(), key=lambda t: (t["d"], t["c"], t["t"])), cities=cities, sched=sched, back=BACK,
            empty=empty, nsearch=len(S))
out = json.dumps(DATA, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/").replace("&", "\\u0026")
html = (ROOT / "gba_template.html").read_text().replace("/*__DATA__*/null", out)
dst = ROOT.parent / "site" / "gba"; dst.mkdir(parents=True, exist_ok=True); (dst / "index.html").write_text(html, encoding="utf-8")
nopt = sum(len(x["o"]) for s in S.values() for x in [s]); npr = sum(1 for s in S.values() for o in s["o"] if o["p"])
print("built", dst / "index.html", "| searches", len(S), "| trips", len(trips), "| flight rows", nopt, "priced", npr, "| empty", len(empty),
      "| unmatched flt", sum(1 for s in S.values() for o in s["o"] if not o["f"]))
print("unmatched:", sorted({(s["c"], o["a"], o["od"]) for s in S.values() for o in s["o"] if not o["f"]}))
print("dropped (excluded airlines):", len(DROPPED))
print("outliers:", [(s["c"], s["d"], o["a"], o["p"]) for s in S.values() for o in s["o"] if o.get("x")])
