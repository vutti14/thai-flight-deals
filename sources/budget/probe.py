import subprocess,re,html,json,time,sys,os
GROUPS={"AA":"FD,XJ","VJ":"VZ,VJ","SL":"SL","OT":"DD,AK,Z2,QZ,D7,OD,ID"}
DEST="PVG PKX PEK CAN SZX TFU CKG KMG HGH XMN CSX WUH XIY NKG CGO TSN SWA NGB SYX KWL HRB TAO DLC KWE NNG HAK HKG MFM TPE KHH NRT HND KIX NGO CTS FUK OKA ICN PUS HAN SGN DAD CXR PQC HPH DEL BOM CCU MAA BLR HYD COK AMD JAI GAY LKO GAU ATQ VNS BWA KTM CMB MLE RGN MDL SIN KUL PEN JHB BKI CGK DPS SUB KNO MNL CEB CRK PNH KTI SAI VTE LPQ ALA".split()
DATES=[("2026-12-10","2026-12-13"),("2026-12-14","2026-12-17")]
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
out={}
if os.path.exists('probe.json'): out=json.load(open('probe.json'))
for d in DEST:
  for (a,b) in DATES:
   for g,AL in GROUPS.items():
    k=f"{d} {a} {g}"
    if k in out: continue
    u=subprocess.check_output(["node","tfs_lcc.js","DMK,BKK",d,a,b,AL]).decode().strip()
    s=subprocess.run(["curl","-sL","-A",UA,"-H","Accept-Language: en-US,en","-b","CONSENT=YES+",u],capture_output=True).stdout.decode(errors="ignore")
    t=re.findall(r'<title>(.*?)</title>',s)
    labs=[html.unescape(l) for l in re.findall(r'aria-label="([^"]{40,700})"',s) if 'flight with' in l]
    fl=[]
    for l in dict.fromkeys(labs):
      m=re.search(r'(?:From (\d+) Thai baht|Total price is unavailable).*?(Nonstop|\d+ stops?) flight with (.+?)\. Leaves (.+?) at (\d+:\d+\s[AP]M) on .*? arrives at (.+?) at (\d+:\d+\s[AP]M)',l)
      if m: fl.append(dict(price=m.group(1),stops=m.group(2),al=m.group(3),frm=m.group(4),dep=m.group(5),to=m.group(6),arr=m.group(7)))
    out[k]=dict(title=t[0] if t else None,n=len(fl),flights=fl,size=len(s))
    print(k,out[k]['title'],len(fl),sum(f['stops']=='Nonstop' for f in fl),flush=True)
    json.dump(out,open('probe.json','w'),indent=1)
    time.sleep(0.8)
