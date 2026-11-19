#!/usr/bin/env python3
"""Parse Trip.Best list pages saved by fetch_tripbest.py (default dir /tmp/tb) into raw/tripbest-lists.json.
Ranking order + names come from the page's embedded state (businessId/businessName/rank); each item's trip.com URL is
the hotel-detail / attraction link with the same id found in the rendered page. Nothing is typed in by hand."""
import json, re, sys, pathlib, html as H
SRC = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parent / "cache")
ROOT = pathlib.Path(__file__).resolve().parent
REG = {"glob_lux":"global","glob_scen":"global","glob_ttd":"global","glob_fama":"global",
       "asia_lux":"asia","asia_scen":"asia","asia_cult":"asia","asia_ttd":"asia","asia_fama":"asia","asia_night":"asia"}
def jstr(s): return json.loads('"' + s + '"')
out = []
for f in list(REG) + sorted(p.stem for p in SRC.glob("c_*.html")):
    p = SRC / (f + ".html")
    if not p.exists(): print("missing", f); continue
    h = p.read_text()
    title = H.unescape(re.search(r"<title>(.*?)</title>", h, re.S).group(1)).split(" | ")[0].strip()
    ogu = re.search(r'<meta property="og:url" content="([^"]+)"', h)
    urls = {}
    for m in re.finditer(r'https://www\.trip\.com/(?:hotels|travel-guide/attraction)/[^"\s&;]+?-(\d+)(?:/hotel/)?(?=[?"&])', h):
        urls.setdefault(m.group(1), m.group(0))
    txt = [re.sub(r"[\ue000-\uf8ff\U000f0000-\U000fffff]", "", l).strip() for l in (SRC / (f + ".txt")).read_text().split("\n")]
    seen = set(); items = []
    for bid, name, btype, rank in re.findall(r'\{"businessId":"(\d+)","businessName":"((?:[^"\\]|\\.)*)","businessType":"(\w+)","rank":(\d+)', h):
        if bid in seen: continue
        seen.add(bid); name = jstr(name); u = urls.get(bid)
        if not u: continue
        mm = re.search(r"/hotels/([a-z0-9-]+)-hotel-detail-", u) or re.search(r"/attraction/([a-z0-9-]+)/", u)
        rating = None
        for i in (j for j, l in enumerate(txt) if l == name or (l.startswith(name) and re.fullmatch(r"\d+", l[len(name):]))):
            for l in txt[i+1:i+5]:
                if re.fullmatch(r"\d+(\.\d)?", l): rating = l; break
            if rating: break
        items.append(dict(pos=int(rank), name=name, url=u, rating=rating, slug=mm.group(1), pid=bid,
                          kind="hotel" if "/hotels/" in u else "attr"))
    if not items:   # city lists: JSON-LD ItemList carries name + url for the rendered items
        for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
            try: d = json.loads(m.group(1))
            except Exception: continue
            if not (isinstance(d, dict) and d.get("@type") == "ItemList"): continue
            for e in d["itemListElement"]:
                it = e.get("item", {}); u = it.get("url") or ""
                mm = re.search(r"/hotels/([a-z0-9-]+)-hotel-detail-(\d+)", u) or re.search(r"/attraction/([a-z0-9-]+)/[^?]*?-(\d+)(?:\?|$)", u)
                if not mm or mm.group(2) in seen: continue
                seen.add(mm.group(2))
                items.append(dict(pos=e.get("position"), name=it.get("name"), url=u, rating=(it.get("aggregateRating") or {}).get("ratingValue"),
                                  slug=mm.group(1), pid=mm.group(2), kind="hotel" if "/hotels/" in u else "attr"))
    items.sort(key=lambda x: x["pos"])
    for it in items:   # hotel location tag shown on the card, e.g. "Near Haikou Meilan International Airport | ..."
        for i in (j for j, l in enumerate(txt) if l == it["name"] or l.startswith(it["name"])):
            loc = next((l for l in txt[i+1:i+4] if l.startswith("Near ")), None)
            if loc: it["loc"] = loc; break
    if not items: print("no items", f); continue
    out.append(dict(id=f, title=title, url=ogu.group(1) if ogu else None, scope=REG.get(f, "city"), kind=items[0]["kind"], n=len(items), items=items))
    print(f, len(items), title[:70])
# merge: lists fetched this run replace the stored copy with the same id; others are kept (cache may be partial)
P = ROOT / "raw/tripbest-lists.json"
old = json.loads(P.read_text()) if P.exists() else []
new = {l["id"]: l for l in out}
merged = [new.pop(l["id"], l) for l in old] + list(new.values())
if out: P.write_text(json.dumps(merged, ensure_ascii=False, indent=1))
print("lists stored:", len(merged), "updated:", len(out))
