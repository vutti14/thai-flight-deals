import re, json
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from excluded_airlines import is_excluded   # permanent rule: no Spring (9C/IJ) or 9 Air (AQ)
txt = open("raw/sweep1-google.md").read()
secs = re.split(r"\n## ", txt)[1:]
AL = {"Thai AirAsia":"FD","Thai AirAsia X":"XJ","AirAsia":"AK","Thai Lion Air":"SL","Thai Vietjet Air":"VZ","Vietjet":"VJ","Nok Air":"DD"}
def h24(t):
    m = re.match(r"(\d+):(\d+)\s*([AP]M)(\+1)?", t.strip()); h, mi, ap, p = m.groups(); h = int(h) % 12 + (12 if ap == "PM" else 0)
    return f"{h:02d}:{mi}", bool(p)
out, empty, unp = [], [], []
for s in secs:
    hd = s.split("\n")[0]; m = re.match(r"(\d+)\. (\w{3}) (\S+) (\S+)→(\S+)", hd)
    n, code, org, dep, ret = m.groups()
    url = re.search(r"URL: (\S+)", s).group(1)
    rows = [r for r in re.findall(r"^- (.+)$", s, re.M) if r.count("|") >= 4]
    if not rows: empty.append(dict(n=int(n), code=code, dep=dep, ret=ret, url=url)); continue
    for r in rows:
        p = [x.strip() for x in r.split("|")]
        al, rt, tm, du, pr = p[:5]
        if is_excluded(name=al) or is_excluded(AL.get(al)): continue
        a, b = tm.split("–"); od, _ = h24(a); oa, nx = h24(b)
        o, d = rt.split("–")
        e = dict(n=int(n), code=code, dep=dep, ret=ret, al=AL.get(al, al), alname=al, org=o, out_dep=od, out_arr=oa, out_next=nx,
                 dur=du, url=url)
        pm = re.search(r"THB ([\d,]+)", pr)
        if pm: e["price"] = int(pm.group(1).replace(",", "")); out.append(e)
        else: unp.append(e)
json.dump(dict(priced=out, unpriced=unp, empty=empty), open("raw/sweep1-parsed.json", "w"), ensure_ascii=False, indent=1)
print(len(out), "priced", len(unp), "unpriced", len(empty), "empty")
from collections import Counter
print(Counter(e["al"] for e in out)); print(Counter(e["al"] for e in unp)); print(sorted({e["code"] for e in out}))
print([ (e['code'],e['dep']) for e in empty])
