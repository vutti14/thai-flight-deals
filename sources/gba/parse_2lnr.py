import re,html,json,glob,collections
out={}
for f in sorted(glob.glob('src/2lnr-*.html')):
    r=f.split('2lnr-')[1][:-5].upper()
    s=open(f).read()
    t=re.sub(r'<script.*?</script>|<style.*?</style>','',s,flags=re.S)
    t=html.unescape(re.sub(r'<[^>]+>',' | ',t));t=re.sub(r'(\s*\|\s*)+',' | ',t)
    m=re.search(r'\| ([^|]*?) fl(?:y|ies) nonstop between [^|]*?roughly (\d+) times? a week',t)
    sm=re.search(r'Showing the first (\d+) of (\d+) scheduled .*? across (\d+) days with service',t)
    rows=re.findall(r'\| ((?:Mon|Tue|Wed|Thu|Fri|Sat|Sun), \w+ \d+) \| ([A-Z0-9]{2} \d+) \| ([^|]+?) \| (\d\d:\d\d) \| (\d\d:\d\d) \| ([^|]+?) \| ([^|]+?) (?=\|)',t)
    conf=re.search(r'Schedule last confirmed \| (\w+ \d+, \d{4})',t)
    nores='no nonstop' in t.lower() or not rows
    out[r]=dict(summary=m.group(1).strip() if m else None,per_week=int(m.group(2)) if m else None,
      shown=(sm.groups() if sm else None),confirmed=conf.group(1) if conf else None,
      rows=[dict(date=a,flt=b,al=c.strip(),dep=d,arr=e,dur=g,ac=h.strip()) for a,b,c,d,e,g,h in rows])
    print(r,out[r]['per_week'],out[r]['shown'],len(rows),'|',out[r]['summary'])
json.dump(out,open('src/2lnr_parsed.json','w'),indent=1)
