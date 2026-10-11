import subprocess,re,html,json,time,os
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
DATES=["2026-11-17","2026-11-20","2026-11-22","2027-01-16","2027-03-06","2027-04-13"]
CITIES=["HKG","CAN","SZX","MFM"]
EXTRA={"HKG":["CX","TG","UO","HX,HB"],"CAN":["CZ"],"SZX":["CZ,ZH"],"MFM":[]}
F="src/probe-gf-oneway.json"; out=json.load(open(F)) if os.path.exists(F) else {}
R=r'(?:From (\d+) Thai baht|Total price is unavailable).*?(Nonstop|\d+ stops?) flight with (.+?)\. Leaves (.+?) at (\d+:\d+\s[AP]M) on .*? arrives at (.+?) at (\d+:\d+\s[AP]M)'
def get(o,d,date,al):
    u=subprocess.check_output(["node","tfs_gba.js",o,d,date,"-","1",al]+([] if al else [])).decode().strip() if al else subprocess.check_output(["node","tfs_gba.js",o,d,date,"-","1"]).decode().strip()
    s=subprocess.run(["curl","-sL","-A",UA,"-H","Accept-Language: en-US,en","-b","CONSENT=YES+",u],capture_output=True).stdout.decode(errors="ignore")
    labs=list(dict.fromkeys(html.unescape(l) for l in re.findall(r'aria-label="([^"]{40,800})"',s) if 'flight with' in l))
    fl=[]
    for l in labs:
        m=re.search(R,l)
        if m: fl.append(dict(price=m.group(1),stops=m.group(2),al=m.group(3),frm=m.group(4),dep=m.group(5),to=m.group(6),arr=m.group(7),next='+1' in l or bool(re.search(r'arrives at .*? on (\w+day), (\w+ \d+)',l) and re.search(r'Leaves .*? on (\w+day)',l).group(1)!=re.search(r'arrives at .*? on (\w+day)',l).group(1))))
    return u,fl
for date in DATES:
  for c in CITIES:
    for (o,d) in [("BKK",c),("DMK",c),(c,"BKK"),(c,"DMK")]:
      for al in [""]+(EXTRA[c] if "BKK" in (o,d) else []):
        k=f"{o}-{d} {date} {al or 'ALL'}"
        if k in out: continue
        u,fl=get(o,d,date,al); out[k]=dict(url=u,flights=fl)
        print(k,len(fl),flush=True); json.dump(out,open(F,"w"),indent=1); time.sleep(0.6)
