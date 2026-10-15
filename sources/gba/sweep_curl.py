#!/usr/bin/env python3
"""Curl-based Google Flights sweep (no browser): for each line of urls-sweep1.txt fetch the results HTML, keep the
aria-label flight strings, save raw labels to raw/sweep2-labels.json (incremental). fmt_sweep.py turns it into raw/sweep2-google.md."""
import subprocess, re, html, json, time, os, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
OUT = ROOT / "raw/sweep2-labels.json"
data = json.loads(OUT.read_text()) if OUT.exists() else {}
U = [l.split() for l in (ROOT / "urls-sweep1.txt").read_text().splitlines() if l.strip()]
def fetch(u):
    r = subprocess.run(["curl", "-sL", "--max-time", "30", "-A", UA, "-H", "Accept-Language: en-US,en;q=0.9", "-b", "CONSENT=YES+", u], capture_output=True)
    s = r.stdout.decode(errors="ignore")
    labs = list(dict.fromkeys(html.unescape(l) for l in re.findall(r'aria-label="([^"]{40,1500})"', s) if "flight with" in l))
    t = re.search(r"<title>(.*?)</title>", s)
    m = re.search(r"Prices are currently (low|typical|high)", s)
    return dict(title=html.unescape(t.group(1)) if t else "", level=m.group(1) if m else None, labels=labs, size=len(s))
for i, x in enumerate(U):
    k = " ".join([str(i)] + x[:5])
    if k in data and data[k]["labels"]: continue
    res = fetch(x[5])
    if not res["labels"]:
        time.sleep(2); res = fetch(x[5])
    res["url"] = x[5]; data[k] = res
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=0))
    print(k, len(res["labels"]), res["size"], res["level"], flush=True)
    time.sleep(0.65)
print("done", len(data), "empty", sum(1 for v in data.values() if not v["labels"]))
