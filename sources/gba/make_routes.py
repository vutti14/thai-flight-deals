#!/usr/bin/env python3
"""Build gba/routes.json + routes.md: nonstop Bangkok (BKK+DMK) <-> GBA (CAN, SZX, HKG, MFM), Oct 2026 - Apr 2027.
Inputs: src/2lnr_parsed.json (parse_2lnr.py), src/probe-gf-oneway.json (probe_gba.py) + manual EXTRA/NEWS from web sources."""
import json, re, collections, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from excluded_airlines import is_excluded, EXCLUDED_AIRLINES   # permanent rule: no Spring (9C/IJ) or 9 Air (AQ)
L = json.load(open("src/2lnr_parsed.json"))
G = json.load(open("src/probe-gf-oneway.json"))
CITY = {"HKG": ("Hong Kong", "ฮ่องกง"), "CAN": ("Guangzhou", "กวางโจว"), "SZX": ("Shenzhen", "เซินเจิ้น"), "MFM": ("Macau", "มาเก๊า")}
GN = {"Cathay Pacific": "CX", "THAI": "TG", "Hong Kong Express": "UO", "Hong Kong Airlines": "HX", "Greater Bay Airlines": "HB", "United": "UA",
      "Emirates": "EK", "China Southern": "CZ", "China Eastern": "MU", "Shenzhen": "ZH", "Spring": "9C", "9 Air": "AQ", "Kenya Airways": "KQ",
      "Air Macau": "NX", "Thai AirAsia": "FD", "Thai Lion Air": "SL", "Thai Vietjet Air": "VZ"}
AIRLINE = {"CX": "Cathay Pacific", "TG": "Thai Airways", "UO": "HK Express", "HX": "Hong Kong Airlines", "HB": "Greater Bay Airlines", "UA": "United Airlines",
           "EK": "Emirates", "CZ": "China Southern", "MU": "China Eastern", "ZH": "Shenzhen Airlines", "9C": "Spring Airlines", "AQ": "9 Air", "KQ": "Kenya Airways",
           "NX": "Air Macau", "FD": "Thai AirAsia", "SL": "Thai Lion Air", "VZ": "Thai Vietjet Air"}
KIND = {"TG": "full", "CX": "full", "HX": "full", "HB": "full", "UA": "full", "EK": "full", "CZ": "full", "MU": "full", "ZH": "full", "NX": "full", "KQ": "full",
        "UO": "lcc", "FD": "lcc", "SL": "lcc", "VZ": "lcc", "9C": "lcc", "AQ": "lcc"}
BIZ = {"TG": "yes", "CX": "yes", "HX": "yes", "UA": "yes (Polaris, 787-9)", "EK": "yes (A380; First also sold)", "CZ": "yes (small J cabin on A320/A321/737)",
       "MU": "yes", "ZH": "yes", "NX": "yes", "KQ": "yes (787)", "HB": "check (sweep will show)", "UO": "no", "FD": "no", "SL": "no",
       "VZ": "no (SkyBoss fare only)", "9C": "no", "AQ": "no"}
WINTER = ["2026-11-17", "2026-11-20", "2026-11-22", "2027-01-16", "2027-03-06"]
def h24(t):
    m = re.match(r"(\d+):(\d+)\s*([AP]M)", t); h, mi, ap = m.groups(); return f"{int(h) % 12 + (12 if ap == 'PM' else 0):02d}:{mi}"
def mins(t): h, m = map(int, t.split(":")); return h * 60 + m
gf = collections.defaultdict(lambda: collections.defaultdict(set))
for k, v in G.items():
    rt, date, _ = k.split(); o, d = rt.split("-")
    for f in v["flights"]:
        if f["stops"] != "Nonstop": continue
        code = GN.get(f["al"], f["al"]); out = o in ("BKK", "DMK")
        gba = d if out else o; bk = o if out else d
        gf[(gba, "out" if out else "back", code, bk)][(h24(f["dep"]), h24(f["arr"]))].add(date)
ln = collections.defaultdict(dict)
for r, v in L.items():
    o, d = r.split("-"); out = o in ("BKK", "DMK"); gba = d if out else o; bk = o if out else d
    for x in v["rows"]:
        e = ln[(gba, "out" if out else "back", x["flt"].split()[0], bk)].setdefault(x["flt"], {"dep": x["dep"], "arr": x["arr"], "ac": x["ac"], "days": set()})
        e["days"].add(x["date"][:3])
TRUNC = {r for r, v in L.items() if v.get("shown")}
FIX = {("HKG", "out", "TG", "15:35"): "TG 606", ("HKG", "back", "TG", "20:30"): "TG 607"}   # AeroRoutes 14 Jul 2026 (5th daily from 1 Dec 2026)
EXTRA = [
 dict(gba="HKG", code="FD", apt="DMK", dir="out", flt="FD 518", dep="08:45", arr="12:25", days="daily", start="2026-10-25",
      src="flightmapper.net Thai AirAsia DMK-HKG (FD518 daily eff 25 Oct 2026, continues HKG-OKA)",
      note="Thai AirAsia resumes DMK–HKG 25 Oct 2026 (FD518 continues to Okinawa). Not shown on Google Flights in our probe — verify on airasia.com; no return flight found in sources."),
 dict(gba="MFM", code="VZ", apt="BKK", dir="out", flt="VZ 3732", dep="16:45", arr="20:40", days="Wed/Fri/Sun", src="airportia.com VZ3732; airpaz.com",
      note="Charter-style flight number, 3 weekly (Sep–Oct 2026); not on Google Flights; winter continuation unconfirmed."),
 dict(gba="MFM", code="VZ", apt="BKK", dir="back", flt="VZ 3733", dep="21:40", arr="23:25", days="Wed/Fri/Sun", src="planemapper.com / airpaz.com VZ3733; FR24 lists 13:40→16:25 for early Oct",
      note="Return time conflicts between sources (21:40 vs 13:40) — verify."),
]
NEWS = {
 "HKG": ["THAI 5th daily BKK–HKG from 1 Dec 2026: TG606 BKK 16:05→20:00 / TG607 HKG 21:00→22:55 (A320) — AeroRoutes 14 Jul 2026 https://www.aeroroutes.com/eng/260714-tgnw26hkg (Google shows 15:35→19:30 / 20:30→22:25 in Jan–Mar samples).",
         "HK Express 4 daily BKK–HKG (UO704/705, 700/701, 702/703, 732/733) — AeroRoutes 4 Mar 2026 https://www.aeroroutes.com/eng/260304-uons26bkk; winter retimes from Google probe.",
         "Greater Bay Airlines BKK–HKG was cut to 2 weekly in parts of May–Aug 2026 (AeroRoutes 19 Apr 2026 https://www.aeroroutes.com/eng/260419-hbmay26); Google shows HB daily 01:45 BKK→HKG / 20:55 HKG→BKK on every winter sample.",
         "Thai AirAsia FD518 DMK–HKG resumes 25 Oct 2026 08:45→12:25 (flightmapper.net). Thai Lion Air 2nd daily DMK–HKG (15:30 out / 20:25 back) on Google from Jan 2027."],
 "CAN": ["THAI 2 daily BKK–CAN (TG668/669; TG678/679 from 1 Aug 2026) — AeroRoutes 29 Jun 2026 https://www.aeroroutes.com/eng/260629-tgaug26can; winter on Google: 09:20→13:20 & 15:25→19:05 out, 14:50→17:10 & 20:25→22:45 back.",
         "Kenya Airways KQ886/887 (fifth-freedom, 787) some days; China Eastern MU2077/2078 daily red-eye."],
 "SZX": ["Shenzhen Airlines timetable (to 24 Oct 2026): ZH306/305, ZH310/309, ZH308/307 daily — globalpage.shenzhenair.com FlightTimetable_EN20260821.pdf; THAI sells ZH306 as codeshare TG6456. A THAI-operated BKK–SZX route was reported as 'planned late 2026' (travelandtourworld.com) but nothing is filed — not included.",
         "Thai AirAsia DMK–SZX (FD596/597) cut to 4–5 weekly May–Jul 2026; daily in 2LNR Oct table and on Google Nov samples.",
         "No daytime morning BKK→SZX flight: before 11:00 only red-eyes (ZH 02:20, CZ 02:40). For a true morning-out 2D1N, fly to HKG and cross the border."],
 "MFM": ["Air Macau 3 daily BKK–MFM (NX995/996, NX935/936, NX991/992); winter retimes on Google: 10:35, 13:30, 20:05 out; 08:05 (some days), 10:20, 16:50 back — no departure from MFM after 16:50 in winter.",
         "Thai AirAsia DMK–MFM winter: 06:45→10:20 & 13:50→17:25 out, 10:50→12:45 & 17:55→19:50 back (Google). Thai Lion Air SL372/373 and SL370/371 daily (2LNR).",
         "Thai Vietjet BKK–MFM VZ3732/3733 3 weekly (Wed/Fri/Sun) — airportia/planemapper; not on Google Flights.",
         "Google prices Thai Lion Air one-ways but shows Air Macau and Thai AirAsia as 'price unavailable' (16 Jan probe: SL 10:15 out ฿2,745, SL 22:05 back ฿2,535)."],
}
def fit_out(dep, gba=""): return (0 if gba == "SZX" else 300) <= mins(dep) < 660
def fit_back(dep): return mins(dep) >= 1080
routes = []
for gba in ["HKG", "CAN", "SZX", "MFM"]:
    keys = sorted({k for k in {k[2:] for k in list(gf) + list(ln) if k[0] == gba} | {(x["code"], x["apt"]) for x in EXTRA if x["gba"] == gba} if not is_excluded(k[0])},
                  key=lambda x: (KIND.get(x[0], "z"), x[0], x[1]))
    carriers = []
    for code, bk in keys:
        flights = []
        for direction in ("out", "back"):
            g = gf.get((gba, direction, code, bk), {}); l = ln.get((gba, direction, code, bk), {})
            wint = {t: ds for t, ds in g.items() if ds & set(WINTER)}
            used = set()
            for (dep, arr), ds in sorted(wint.items()):
                best = None
                for fn, e in l.items():
                    if fn in used: continue
                    dd = abs(mins(e["dep"]) - mins(dep)); dd = min(dd, 1440 - dd)
                    if dd <= 90 and (best is None or dd < best[0]): best = (dd, fn)
                fn = best[1] if best else FIX.get((gba, direction, code, dep))
                if fn in l: used.add(fn)
                e = l.get(fn, {}); seen = sorted(set(ds) & set(WINTER))
                flights.append(dict(dir=direction, flt=fn, winter=f"{dep}→{arr}", summer=(f"{e['dep']}→{e['arr']}" if e else None), aircraft=e.get("ac"),
                    seen_winter=f"{len(seen)}/5 sample dates", seen_dates=seen,
                    freq=("daily" if len(seen) == 5 else ("from Jan 2027" if seen[0] >= "2027-01" else "some days")),
                    fits_2d1n=(fit_out(dep, gba) if direction == "out" else fit_back(dep))))
            for fn, e in l.items():
                if fn in used: continue
                days = "/".join(d for d in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"] if d in e["days"])
                r = f"{bk}-{gba}" if direction == "out" else f"{gba}-{bk}"
                flights.append(dict(dir=direction, flt=fn, winter=None, summer=f"{e['dep']}→{e['arr']}", aircraft=e["ac"],
                    summer_days=("daily" if len(e["days"]) == 7 else days + (" (2LNR table truncated)" if r in TRUNC else "")),
                    freq="Oct (summer) only / not matched in winter samples", fits_2d1n=(fit_out(e["dep"], gba) if direction == "out" else fit_back(e["dep"]))))
        for x in EXTRA:
            if x["gba"] == gba and x["code"] == code and x["apt"] == bk:
                flights.append(dict(dir=x["dir"], flt=x["flt"], winter=f"{x['dep']}→{x['arr']}", summer=None, freq=x["days"], start=x.get("start"),
                    fits_2d1n=(fit_out(x["dep"], gba) if x["dir"] == "out" else fit_back(x["dep"])), source=x["src"], note=x["note"]))
        if not flights: continue
        flights.sort(key=lambda f: (f["dir"] != "out", (f["winter"] or f["summer"])[:5]))
        carriers.append(dict(code=code, airline=AIRLINE.get(code, code), kind=KIND.get(code, "?"), bangkok_airport=bk, business=BIZ.get(code, "?"), flights=flights))
    def lab(f, c): return f"{f['flt'] or c} {f['winter']}{' (red-eye)' if mins(f['winter'][:5]) < 300 else ''}{' from '+f['start'] if f.get('start') else ''}{'' if f['freq']=='daily' else ' ['+f['freq']+']'}"
    o2 = [lab(f, c["code"]) for c in carriers for f in c["flights"] if f["dir"] == "out" and f["fits_2d1n"] and f["winter"]]
    b2 = [lab(f, c["code"]) for c in carriers for f in c["flights"] if f["dir"] == "back" and f["fits_2d1n"] and f["winter"]]
    routes.append(dict(code=gba, city=CITY[gba][0], city_th=CITY[gba][1], carriers=carriers, news=NEWS[gba], fit_2d1n=dict(morning_out=o2, late_back=b2)))
meta = dict(built="2026-10-11", window="2026-10-17 – 2027-04-30", seasons="IATA winter 25 Oct 2026 – 27 Mar 2027; summer from 28 Mar 2027",
  rules=dict(two_d1n="2D1N = leave Bangkok 05:00–10:59 (SZX 00:00–10:59, red-eye only) and leave GBA 18:00–23:59 next day (MFM sweep uses 17:00+ to catch Thai AirAsia 17:55)",
             three_d2n="3D2N = any times"),
  sources=["2LNR route pages (schedule data dated 4 Oct 2026, departures 9–15 Oct 2026; fetched 11 Oct 2026) https://www.2lnr.com/routes/bkk-hkg etc. — flight numbers, aircraft, summer times",
           "Google Flights one-way nonstop probe, fetched 11 Oct 2026, dates 17/20/22 Nov 2026, 16 Jan, 6 Mar, 13 Apr 2027 (src/probe-gf-oneway.json) — winter times + carriers",
           "AeroRoutes, Shenzhen Airlines timetable PDF, flightmapper.net, airportia/planemapper/airpaz (see per-city notes)"],
  caveats=["Excluded by user rule (all sweeps and dashboards): " + ", ".join(f"{v} ({k})" for k, v in EXCLUDED_AIRLINES.items()) + ".",
           "Google returns at most ~20 flights per search, so on busy routes (HKG, CAN) 'some days' usually means the flight was cut off the list (per-airline searches found more), not a non-daily service.",
           "Winter flight numbers are matched to the October (summer) 2LNR flight with the nearest departure (≤90 min) — likely right, confirm on booking.",
           "Google returned nothing for several DMK one-way queries on 17 Nov and drops Thai AirAsia/Thai Lion on some dates; DMK flights marked 'some days' are often daily in 2LNR.",
           "Thai AirAsia DMK–HKG and Thai Vietjet BKK–MFM never appear on Google Flights."],
  holidays={"thai": {"2026-10-23": "วันปิยมหาราช (Fri)", "2026-12-05": "วันพ่อ (Sat)", "2026-12-07": "ชดเชยวันพ่อ (Mon)", "2026-12-10": "วันรัฐธรรมนูญ (Thu)",
            "2026-12-31": "สิ้นปี (Thu)", "2027-01-01": "ปีใหม่ (Fri)", "2027-02-21": "มาฆบูชา (Sun)", "2027-02-22": "ชดเชยมาฆบูชา (Mon)", "2027-04-06": "วันจักรี (Tue)",
            "2027-04-13": "สงกรานต์ (Tue)", "2027-04-14": "สงกรานต์", "2027-04-15": "สงกรานต์ (Thu)"},
            "china_hk_macau": {"2027-02-06": "Chinese New Year (Sat; eve Fri 5 Feb) — mainland Spring Festival holiday expected ~5–13 Feb; HK/Macau 6–9 Feb; fares/hotels peak ~1–15 Feb",
                               "2026-12-25": "Christmas (HK/Macau holiday)", "2027-04-05": "Ching Ming (approx.; HK/Macau/China)"},
            "sources": ["myhora.com/calendar/holiday-2570.aspx (มาฆบูชา 21 ก.พ. 2570 + ชดเชย 22 ก.พ.)", "bot.or.th holiday notice 2570"]})
json.dump(dict(meta=meta, routes=routes), open("routes.json", "w"), ensure_ascii=False, indent=1)
md = ["# Zone GBA — nonstop Bangkok ⇄ Guangzhou / Shenzhen / Hong Kong / Macau", "", f"Built {meta['built']} · window {meta['window']} · {meta['seasons']}", "",
      f"- {meta['rules']['two_d1n']}", f"- {meta['rules']['three_d2n']}", "",
      "Times local. **Winter** = Google Flights probe (Nov 2026–Mar 2027 samples). **Summer** = 2LNR Oct 2026 table (matches Google's 13 Apr 2027 sample). ✅ = fits 2D1N.", ""]
for r in routes:
    md += [f"## {r['code']} {r['city']} ({r['city_th']})", "", "| Airline | BKK apt | Dir | Flight | Winter | Summer | Freq | Aircraft | J | 2D1N |", "|---|---|---|---|---|---|---|---|---|---|"]
    for c in r["carriers"]:
        for f in c["flights"]:
            md.append(f"| {c['airline']} ({c['code']}{' LCC' if c['kind']=='lcc' else ''}) | {c['bangkok_airport']} | {'BKK→' if f['dir']=='out' else '→BKK'} | {f.get('flt') or '–'} | {f.get('winter') or '–'} | {f.get('summer') or '–'} | {f.get('freq')}{' · '+f['summer_days'] if f.get('summer_days') else ''}{' · from '+f['start'] if f.get('start') else ''} | {f.get('aircraft') or '–'} | {c['business'].split(' ')[0]} | {'✅' if f['fits_2d1n'] else ''} |")
    md += ["", f"**2D1N morning out (winter):** {', '.join(r['fit_2d1n']['morning_out']) or 'none'}", "", f"**2D1N late back (winter):** {', '.join(r['fit_2d1n']['late_back']) or 'none'}", "", "Notes / sources:"]
    md += [f"- {n}" for n in r["news"]] + [f"- {f['flt']}: {f['note']} ({f['source']})" for c in r["carriers"] for f in c["flights"] if f.get("note")] + [""]
md += ["## Holidays & peaks", ""] + [f"- {k}: {v}" for k, v in {**meta["holidays"]["thai"], **meta["holidays"]["china_hk_macau"]}.items()]
md += ["", "## Sources", ""] + [f"- {s}" for s in meta["sources"] + meta["holidays"]["sources"]] + ["", "## Caveats", ""] + [f"- {s}" for s in meta["caveats"]]
open("routes.md", "w").write("\n".join(md) + "\n")
for r in routes:
    print(r["code"], len(r["carriers"]), "carriers:", ", ".join(f"{c['code']}/{c['bangkok_airport']}" for c in r["carriers"]))
    print("   out:", r["fit_2d1n"]["morning_out"]); print("   back:", r["fit_2d1n"]["late_back"])
