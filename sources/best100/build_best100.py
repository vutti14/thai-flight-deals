#!/usr/bin/env python3
import html
"""Build the public Trip.Best 100 page -> ../site/best100/index.html (self-contained, data inline).
Inputs: raw/tripbest-lists.json (extract_lists.py), raw/direct-labels.json (direct_sweep.py), destinations.py.
Public page: no personal data. Excluded airlines (Spring 9C/IJ, 9 Air AQ) are never shown."""
import json, re, sys, pathlib, collections
ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent)); sys.path.insert(0, str(ROOT))
from destinations import D, CODESHARE_ONLY, SWEEP_KEY
CAPTURED = "2026-11-20"   # Hainan/Qingdao/India lists fetched 20 Nov; older lists 19 Nov
SAMPLE_DATES = ["2027-01-20", "2027-01-23"]
EXCL_NAMES = ("Spring", "9 Air")          # Google Flights display names of excluded carriers
LISTS = json.loads((ROOT / "raw/tripbest-lists.json").read_text())
LBL = {"glob_lux": "Global 100 · โรงแรมหรู", "glob_scen": "Global 100 · โรงแรมวิวสวย", "glob_ttd": "Global 100 · ที่เที่ยว",
       "glob_fama": "Global 100 · เที่ยวกับครอบครัว", "asia_lux": "Asia 100 · โรงแรมหรู", "asia_scen": "Asia 100 · โรงแรมวิวสวย",
       "asia_cult": "Asia 100 · โรงแรมสัมผัสวัฒนธรรม", "asia_ttd": "Asia 100 · ที่เที่ยว", "asia_fama": "Asia 100 · เที่ยวกับครอบครัว",
       "asia_night": "Asia 100 · เที่ยวกลางคืน"}
CITY_TOP = 8
def thurl(u):   # same trip.com page, Thai locale + THB
    u = html.unescape(u) if "&amp;" in u else u
    base, _, q = u.partition("?")
    q = "&".join(p for p in q.split("&") if p and not p.startswith(("locale=", "curr=")))
    u = base + ("?" + q if q else "")
    return u + ("&" if "?" in u else "?") + "locale=th-TH&curr=THB"
# ---- direct flights ----
LAB = {}
for fn in ("raw/direct-labels.json", "raw/direct-hainan-tao.json", "raw/direct-india.json"):   # 2nd: HAK/SYX/TAO 4 origins 5 dates; 3rd: India, BKK, 3 dates Dec 26–Feb 27
    if (ROOT / fn).exists(): LAB.update(json.loads((ROOT / fn).read_text()))
APT = {"Suvarnabhumi Airport": "BKK", "Don Mueang International Airport": "DMK", "Phuket International Airport": "HKT", "Chiang Mai International Airport": "CNX"}
def ok_name(n, code): return not n.startswith(EXCL_NAMES) and n not in CODESHARE_ONLY and (n, code) not in CODESHARE_ONLY
def flights(code):
    key = SWEEP_KEY.get(code, code); al = {}; durs = []; nflt = collections.Counter()
    for k, v in LAB.items():
        if k.split()[0] != key: continue
        for l in v.get("labels", []):
            m = re.search(r"Nonstop flight with (.+?)\. Leaves (.+?) at .*?Total duration (\d+) hr(?: (\d+) min)?", l)
            if not m: continue
            names = [re.sub(r"\. Operated by.*", "", n.strip()) for n in re.split(r", | and ", m.group(1)) if n.strip()]
            apt = APT.get(m.group(2), m.group(2)); ok = False
            for n in names:
                if ok_name(n, code): al.setdefault(n, set()).add(apt); ok = True
            if ok: durs.append(int(m.group(3)) * 60 + int(m.group(4) or 0)); nflt[k] += 1
    f = dict(airlines=[[n, sorted(a)] for n, a in sorted(al.items(), key=lambda x: (x[0] != "THAI", x[0]))],
             dur=min(durs) if durs else None, perday=max(nflt.values()) if nflt else 0)
    p = ROOT / f"raw/onestop-{code}.json"
    if not f["airlines"] and p.exists():   # no nonstop: best 1-stop routings seen on >= 3 of the sample dates
        agg = {}
        for dt, v in json.loads(p.read_text()).items():
            for l in v["labels"]:
                m = re.search(r"1 stop flight with (.+?)\. Leaves .*?Total duration (\d+) hr(?: (\d+) min)?\..*?Layover \(1 of 1\) is a (\d+) hr(?: (\d+) min)? layover at .+? in (.+?)\.", l)
                if not m or any(not ok_name(n.strip(), code) for n in re.split(r", | and ", m.group(1))): continue
                pr = re.search(r"From (\d+) Thai baht", l)
                a = agg.setdefault((m.group(1), m.group(6)), dict(al=m.group(1), via=m.group(6), dates=set(), dur=9999, lay=9999, price=None))
                a["dates"].add(dt); a["dur"] = min(a["dur"], int(m.group(2)) * 60 + int(m.group(3) or 0)); a["lay"] = min(a["lay"], int(m.group(4)) * 60 + int(m.group(5) or 0))
                if pr: a["price"] = min(a["price"] or 10**9, int(pr.group(1)))
        r = [a for a in agg.values() if len(a["dates"]) >= 3 and (a["price"] or 0) < 30000]
        r.sort(key=lambda a: a["dur"])
        f["routes"] = [dict(al=a["al"], via=a["via"], dur=a["dur"], lay=a["lay"], price=a["price"], n=len(a["dates"])) for a in r[:4]]
        f["ndates"] = len(json.loads(p.read_text()))
    return f
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
SLUG2 = {}   # slug -> (dest code, near label or None)
for d in D:
    for sl in d["slugs"]: SLUG2[sl] = (d["code"], None)
    for sl, lab in d.get("near", {}).items(): SLUG2.setdefault(sl, (d["code"], lab))
ITEMS = {d["code"]: collections.OrderedDict() for d in D}
BIZ = {d["code"]: [] for d in D}
def add(code, it, badge, lst, nearlabel):
    items = ITEMS[code]; k = it["pid"]
    if k not in items:
        items[k] = dict(n=it["name"], u=thurl(it["url"]), k=it["kind"], r=it.get("rating"), b=[], near=nearlabel, best=9999)
    if not items[k]["r"] and it.get("rating"): items[k]["r"] = it["rating"]
    if badge not in items[k]["b"]: items[k]["b"].append(badge)
    items[k]["best"] = min(items[k]["best"], badge[2] + (0 if lst["scope"] != "city" else 1000))
def citylab(lst, d):
    cn = re.search(r" in (.+?)(?: –|$)", lst["title"]); cn = cn.group(1) if cn else d["en"]
    kind = lst["id"].rsplit("_", 1)[1]
    return {"lux": "Top โรงแรมหรู ", "prem": "Top โรงแรมระดับพรีเมียม ", "upsc": "Top โรงแรม 4 ดาว ", "gtph": "Top โรงแรมที่นักเดินทางต่างชาติเลือก ",
            "ttd": "Top ที่เที่ยว "}.get(kind, "Top ") + cn, kind
for lst in LISTS:   # Global / Asia 100: every item located in a destination (or its near-by towns)
    if lst["scope"] == "city": continue
    for it in lst["items"]:
        if it["slug"] in SLUG2:
            c, nl = SLUG2[it["slug"]]; add(c, it, [LBL[lst["id"]], lst["url"], it["pos"]], lst, nl)
for d in D:   # city Top lists: top N per list; an item that sits in another destination's city goes there
    for c in d.get("city", []):
        for lst in LISTS:
            if lst["scope"] != "city" or not lst["id"].startswith(f"c_{c}_"): continue
            lab, kind = citylab(lst, d)
            top = d.get("top", {}).get(kind, CITY_TOP if kind in ("lux", "ttd") else 0)
            for it in lst["items"][:top]:
                if d.get("hx") and re.search(d["hx"], it["name"]): continue   # India: keep the 5-star picks only
                if d.get("strict") and it["slug"] not in SLUG2: continue      # e.g. Gaya 'luxury' list = a Varanasi hotel
                dc, nl = SLUG2.get(it["slug"], (d["code"], None))   # unknown town -> stays with the list's own city
                add(dc, it, [lab, lst["url"], it["pos"]], lst, nl)
            for rx, blab in d.get("biz", []):   # business-friendly picks: Trip.com location tag of the hotel card
                for it in lst["items"]:
                    if lst["kind"] == "hotel" and it.get("loc") and re.search(rx, it["loc"]) and it["slug"] in d["slugs"]:
                        add(d["code"], it, [lab, lst["url"], it["pos"]], lst, None)
                        if not any(b[0] == it["name"] for b in BIZ[d["code"]]): BIZ[d["code"]].append([it["name"], thurl(it["url"]), blab, it["loc"]])
out = []; tot = collections.Counter()
for d in D:
    items = ITEMS[d["code"]]
    hotels = sorted([v for v in items.values() if v["k"] == "hotel"], key=lambda v: (v["near"] is not None, v["best"]))
    attrs = sorted([v for v in items.values() if v["k"] == "attr"], key=lambda v: (v["near"] is not None, v["best"]))
    hotels = [dict(v) for v in hotels]; attrs = [dict(v) for v in attrs]
    for v in hotels + attrs: v.pop("best"); v.pop("k")
    f = flights(d["code"])
    if d.get("tg"): f["tg"] = d["tg"]
    if not f["airlines"] and not d.get("nodirect"): raise SystemExit(f"{d['code']}: no nonstop flight found — remove from destinations.py")
    links = []
    for c in d.get("city", []):
        for l in LISTS:
            if l["scope"] == "city" and l["id"].startswith(f"c_{c}_"):
                links.append([citylab(l, d)[0].replace("Top ", "", 1), thurl(l["url"])])
    rel = []
    if d["code"] in GBA: rel.append(["โซน GBA (ราคาตั๋ว + งานแฟร์)", "../gba/"])
    if TGMAP.get(d["code"], d["code"]) in TG: rel.append(["ราคาการบินไทย", "../"])
    if BUDMAP.get(d["code"], d["code"]) in BUD: rel.append(["สายการบินราคาประหยัด", "../budget/"])
    out.append(dict(code=d["code"], ap=d.get("airports", d["code"]), th=d["th"], en=d["en"], flag=d["flag"], g=d["group"], why=d["why"],
                    note=d.get("note"), fl=f, h=hotels, a=attrs, links=links, rel=rel, biz=BIZ[d["code"]]))
    tot["h"] += len(hotels); tot["a"] += len(attrs)
    print(f"{d['code']:4} {d['th']:14} hotels {len(hotels):3} attrs {len(attrs):3}  airlines {len(f['airlines'])}  biz {len(BIZ[d['code']])}  routes {len(f.get('routes', []))}")
out = [o for o in out if o["h"] or o["a"]]
meta = dict(captured=CAPTURED, sample=SAMPLE_DATES, ndest=len(out), nh=tot["h"], na=tot["a"],
            lists=[[LBL.get(l["id"], l["title"]), thurl(l["url"]), l["n"]] for l in LISTS if l["scope"] != "city"])
data = json.dumps(dict(meta=meta, dest=out), ensure_ascii=False, separators=(",", ":")).replace("&", "\\u0026").replace("<", "\\u003c")
html = (ROOT / "best100_template.html").read_text().replace("/*__DATA__*/null", data)
dst = ROOT.parent / "site/best100/index.html"; dst.parent.mkdir(parents=True, exist_ok=True); dst.write_text(html)
print("wrote", dst, len(html), "bytes ·", meta["ndest"], "destinations ·", tot["h"], "hotels ·", tot["a"], "attractions")
