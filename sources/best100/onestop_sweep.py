#!/usr/bin/env python3
"""Google Flights (curl) one-way, max 1 stop, from BKK+DMK: keep itinerary labels. -> raw/onestop-<code>.json
usage: onestop_sweep.py SYX 2026-12-10,2027-01-14,..."""
import subprocess, re, html, json, time, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
code = sys.argv[1]; dates = sys.argv[2].split(","); out = {}
for d in dates:
    u = subprocess.check_output(["node", str(ROOT / "tfs_1stop.js"), "BKK,DMK", code, d, "-", "1"]).decode().strip()
    s = subprocess.run(["curl", "-sL", "--max-time", "30", "-A", UA, "-H", "Accept-Language: en-US,en;q=0.9", "-b", "CONSENT=YES+", u], capture_output=True).stdout.decode(errors="ignore")
    labs = list(dict.fromkeys(html.unescape(l) for l in re.findall(r'aria-label="([^"]{40,2000})"', s) if "flight with" in l))
    out[d] = {"url": u, "labels": labs}; print(code, d, len(labs), flush=True); time.sleep(1)
(ROOT / f"raw/onestop-{code}.json").write_text(json.dumps(out, ensure_ascii=False, indent=0))
