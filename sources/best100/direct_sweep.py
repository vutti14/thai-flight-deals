#!/usr/bin/env python3
"""Verify nonstop service BKK/DMK -> destination with Google Flights (curl, one-way, nonstop only, economy).
Two sample dates. Saves raw/direct-labels.json."""
import subprocess, re, html, json, time, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
OUT = ROOT / "raw/direct-labels.json"
data = json.loads(OUT.read_text()) if OUT.exists() else {}
CODES = sys.argv[1].split(",")
DATES = ["2027-01-20", "2027-01-23"]
def url(code, d):
    return subprocess.check_output(["node", str(ROOT.parent/"gba/tfs_gba.js"), "BKK,DMK", code.replace("+", ","), d, "-", "1"]).decode().strip()
def fetch(u):
    r = subprocess.run(["curl", "-sL", "--max-time", "30", "-A", UA, "-H", "Accept-Language: en-US,en;q=0.9", "-b", "CONSENT=YES+", u], capture_output=True)
    s = r.stdout.decode(errors="ignore")
    return list(dict.fromkeys(html.unescape(l) for l in re.findall(r'aria-label="([^"]{40,1500})"', s) if "flight with" in l or "Nonstop" in l))
for c in CODES:
    for d in DATES:
        k = f"{c} {d}"
        if k in data and data[k]["labels"]: continue
        u = url(c, d); labs = fetch(u)
        if not labs: time.sleep(2); labs = fetch(u)
        data[k] = {"url": u, "labels": labs}
        OUT.write_text(json.dumps(data, ensure_ascii=False, indent=0))
        print(k, len(labs), flush=True); time.sleep(0.7)
