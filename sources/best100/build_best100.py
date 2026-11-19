#!/usr/bin/env python3
"""Build the public Trip.Best 100 page -> ../site/best100/index.html (self-contained, data inline).
Inputs: raw/tripbest-lists.json (extract_lists.py), raw/direct-labels.json (direct_sweep.py), destinations.py.
Public page: no personal data. Excluded airlines (Spring 9C/IJ, 9 Air AQ) are never shown."""
import json, re, sys, pathlib, collections
ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent)); sys.path.insert(0, str(ROOT))
from destinations import D, CODESHARE_ONLY, SWEEP_KEY
CAPTURED = "2026-11-19"
SAMPLE_DATES = ["2027-01-20", "2027-01-23"]
EXCL_NAMES = ("Spring", "9 Air")          # Google Flights display names of excluded carriers
LISTS = json.loads((ROOT / "raw/tripbest-lists.json").read_text())
LBL = {"glob_lux": "Global 100 · โรงแรมหรู", "glob_scen": "Global 100 · โรงแรมวิวสวย", "glob_ttd": "Global 100 · ที่เที่ยว",
       "glob_fama": "Global 100 · เที่ยวกับครอบครัว", "asia_lux": "Asia 100 · โรงแรมหรู", "asia_scen": "Asia 100 · โรงแรมวิวสวย",
       "asia_cult": "Asia 100 · โรงแรมสัมผัสวัฒนธรรม", "asia_ttd": "Asia 100 · ที่เที่ยว", "asia_fama": "Asia 100 · เที่ยวกับครอบครัว",
       "asia_night": "Asia 100 · เที่ยวกลางคืน"}
CITY_TOP = 8
def thurl(u):   # same trip.com page, Thai locale + THB
    u = re.sub(r"([?&])(locale|curr)=[^&]*&?", r"\1", u).rstrip("?&")
    return u + ("&" if "?" in u else "?") + "locale=th-TH&curr=THB"
# ---- direct flights ----
LAB = json.loads((ROOT / "raw/direct-labels.json").read_text())
APT = {"Suvarnabhumi Airport": "BKK", "Don Mueang International Airport": "DMK"}
def flights(code):
    key = SWEEP_KEY.get(code, code); al = {}; durs = []; nflt = collections.Counter()
    for d in SAMPLE_DATES:
        for l in LAB.get(f"{key} {d}", {}).get("labels", []):
            m = re.search(r"Nonstop flight with (.+?)\. Leaves (.+?) at .*?Total duration (\d+) hr(?: (\d+) min)?", l)
            if not m: continue
            names = [n.strip() for n in re.split(r", | and ", m.group(1)) if n.strip()]
            names = [re.sub(r"\. Operated by.*", "", n) for n in names]
            apt = APT.get(m.group(2), m.group(2))
            ok = False
            for n in names:
                if n.startswith(EXCL_NAMES): continue
                if n in CODESHARE_ONLY or (n, code) in CODESHARE_ONLY: continue
                al.setdefault(n, set()).add(apt); ok = True
            if ok:
                durs.append(int(m.group(3)) * 60 + int(m.group(4) or 0)); nflt[d] += 1
    return dict(airlines=[[n, sorted(a)] for n, a in sorted(al.items(), key=lambda x: (x[0] != "THAI", x[0]))],
                dur=min(durs) if durs else None, perday=max(nflt.values()) if nflt else 0)
# ---- related dashboards ----
TG = set(); BUD = set()
import glob
snap = sorted(glob.glob(str(ROOT.parent / "data/snapshots/*economy.json")))[-1]
for r in json.loads(open(snap).read())["routes"]: TG.add(r["code"])
for r in json.loads((ROOT.parent / "budget/routes.json").read_text())["routes"]: BUD.add(r["code"])
GBA = {"HKG", "CAN", "SZX", "MFM"}
TGMAP = {"TYO": "TYO", "PVG": "PVG", "PEK": "PEK", "CTU": "TFU"}
BUDMAP = {"TYO": "NRT", "CTU": "TFU"}
# ---- assemble ----
out = []; tot = collections.Counter(); used_lists = {}
for d in D:
    slugs = set(d["slugs"]); near = d.get("near", {})
    items = collections.OrderedDict()
    def add(it, badge, lst, nearlabel):
        k = it["pid"]
        if k not in items:
            items[k] = dict(n=it["name"], u=thurl(it["url"]), k=it["kind"], r=it.get("rating"), b=[], near=nearlabel, best=9999)
        if not items[k]["r"] and it.get("rating"): items[k]["r"] = it["rating"]
        items[k]["b"].append(badge); items[k]["best"] = min(items[k]["best"], badge[2] + (0 if lst["scope"] != "city" else 1000))
        used_lists[lst["id"]] = lst
    for lst in LISTS:
        if lst["scope"] == "city": continue
        for it in lst["items"]:
            if it["slug"] in slugs or it["slug"] in near:
                add(it, [LBL[lst["id"]], lst["url"], it["pos"]], lst, near.get(it["slug"]))
    for c in d.get("city", []):
        for lst in LISTS:
            if lst["id"] in (f"c_{c}_lux", f"c_{c}_ttd"):
                cityname = re.search(r" in (.+?) –", lst["title"]); cityname = cityname.group(1) if cityname else d["en"]
                lab = ("Top โรงแรมหรู " if lst["kind"] == "hotel" else "Top ที่เที่ยว ") + cityname
                for it in lst["items"][:CITY_TOP]:
                    add(it, [lab, lst["url"], it["pos"]], lst, near.get(it["slug"]) if it["slug"] not in slugs else None)
    hotels = sorted([v for v in items.values() if v["k"] == "hotel"], key=lambda v: (v["near"] is not None, v["best"]))
    attrs = sorted([v for v in items.values() if v["k"] == "attr"], key=lambda v: (v["near"] is not None, v["best"]))
    for v in hotels + attrs: v.pop("best"); v.pop("k")
    f = flights(d["code"])
    if not f["airlines"]: raise SystemExit(f"{d['code']}: no nonstop flight found — remove from destinations.py")
    links = [[("โรงแรมหรู" if l["kind"] == "hotel" else "ที่เที่ยว") + " " + (re.search(r" in (.+?) –", l["title"]) or [None, d["en"]])[1], thurl(l["url"])]
             for l in LISTS if l["scope"] == "city" and any(l["id"] in (f"c_{c}_lux", f"c_{c}_ttd") for c in d.get("city", []))]
    rel = []
    if d["code"] in GBA: rel.append(["โซน GBA (ราคาตั๋ว + งานแฟร์)", "../gba/"])
    if TGMAP.get(d["code"], d["code"]) in TG: rel.append(["ราคาการบินไทย", "../"])
    if BUDMAP.get(d["code"], d["code"]) in BUD: rel.append(["สายการบินราคาประหยัด", "../budget/"])
    out.append(dict(code=d["code"], ap=d.get("airports", d["code"]), th=d["th"], en=d["en"], flag=d["flag"], g=d["group"], why=d["why"],
                    note=d.get("note"), fl=f, h=hotels, a=attrs, links=links, rel=rel))
    tot["h"] += len(hotels); tot["a"] += len(attrs)
    print(f"{d['code']:4} {d['th']:14} hotels {len(hotels):3} attrs {len(attrs):3}  airlines {len(f['airlines'])}")
out = [o for o in out if o["h"] or o["a"]]
meta = dict(captured=CAPTURED, sample=SAMPLE_DATES, ndest=len(out), nh=tot["h"], na=tot["a"],
            lists=[[LBL.get(l["id"], l["title"]), thurl(l["url"]), l["n"]] for l in LISTS if l["scope"] != "city"])
data = json.dumps(dict(meta=meta, dest=out), ensure_ascii=False, separators=(",", ":")).replace("&", "\\u0026").replace("<", "\\u003c")
html = (ROOT / "best100_template.html").read_text().replace("/*__DATA__*/null", data)
dst = ROOT.parent / "site/best100/index.html"; dst.parent.mkdir(parents=True, exist_ok=True); dst.write_text(html)
print("wrote", dst, len(html), "bytes ·", meta["ndest"], "destinations ·", tot["h"], "hotels ·", tot["a"], "attractions")
