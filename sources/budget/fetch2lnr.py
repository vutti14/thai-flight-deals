import json,re,html,subprocess,time,os
TH=set("HDY KBV KKC UTH CEI CNX NAW CJM LPT LOE KOP NST NNT PHS HKT UNN ROI SNO BFV URT TST UBP MAQ NTG_ HHQ UTP".split())
r=json.load(open('src/2lnr_routes.json'))
pairs=sorted({(o,d) for a in r for o,d,n,h in r[a] if d not in TH})
print(len(pairs))
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126 Safari/537.36"
def get(slug):
    fn=f'src/routes/{slug}.html'
    if not os.path.exists(fn) or os.path.getsize(fn)<5000:
        subprocess.run(["curl","-sL","-A",UA,f"https://2lnr.com/routes/{slug}","-o",fn]); time.sleep(0.4)
    return open(fn,errors='ignore').read()
def parse(s):
    rows=re.findall(r'<tr[^>]*>(.*?)</tr>',s,flags=re.S)
    out=[]
    for row in rows:
        c=[html.unescape(re.sub(r'<[^>]+>','',x)).strip() for x in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>',row,flags=re.S)]
        if len(c)>=6 and re.match(r'\w{3}, \w{3} \d+',c[0]): out.append(c)
    m=re.search(r'([\d.]+) Nonstop flights a week',re.sub(r'<[^>]+>',' ',s))
    conf=re.search(r'Schedule last confirmed ([A-Za-z]+ \d+, \d{4})',s)
    return out,(m.group(1) if m else None),(conf.group(1) if conf else None)
res={}
for o,d in pairs:
    ob=parse(get(f"{o.lower()}-{d.lower()}")); rt=parse(get(f"{d.lower()}-{o.lower()}"))
    res[f"{o}-{d}"]=dict(out=ob[0],out_wk=ob[1],ret=rt[0],ret_wk=rt[1],confirmed=ob[2])
    print(o,d,ob[1],len(ob[0]),rt[1],len(rt[0]),flush=True)
json.dump(res,open('src/2lnr_sched.json','w'),indent=1,ensure_ascii=False)
