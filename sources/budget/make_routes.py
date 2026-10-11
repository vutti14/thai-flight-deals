"""Build budget/routes.json + routes.md: LCC nonstop route matrix from Bangkok (DMK/BKK), Oct 2026 - Apr 2027.
Inputs: src/2lnr_routes.json, src/2lnr_sched.json (2LNR schedule pages fetched 11 Oct 2026), manual seasonal notes below
(AeroRoutes / airline newsroom / TRAICY / Khaosod), optional probe.json (Google Flights live check, Dec 2026 dates)."""
import json, re, collections, datetime as dt, os, html
OUR = {"FD":"Thai AirAsia","XJ":"Thai AirAsia X","AK":"AirAsia (Malaysia)","Z2":"AirAsia Philippines","QZ":"Indonesia AirAsia",
       "VZ":"Thai Vietjet","VJ":"VietJet Air","SL":"Thai Lion Air","DD":"Nok Air","OD":"Batik Air Malaysia","ID":"Batik Air (Indonesia)"}
TH = set("HDY KBV KKC UTH CEI CNX NAW CJM LPT LOE KOP NST NNT PHS HKT UNN ROI SNO BFV URT TST UBP MAQ HHQ UTP".split())
TG = set("KMG BLR PVG PEK CCU DEL BOM MAA SGN HAN HYD CAN RGN TFU XMN DAD HKG KIX NGO NRT HND FUK".split())
CITY = {  # code: (city EN, city TH, country, region)
 "PVG":("Shanghai","เซี่ยงไฮ้","China","china"),"CAN":("Guangzhou","กวางโจว","China","china"),"SZX":("Shenzhen","เซินเจิ้น","China","china"),
 "TFU":("Chengdu (Tianfu)","เฉิงตู","China","china"),"CKG":("Chongqing","ฉงชิ่ง","China","china"),"KMG":("Kunming","คุนหมิง","China","china"),
 "HGH":("Hangzhou","หางโจว","China","china"),"CSX":("Changsha","ฉางซา","China","china"),"WUH":("Wuhan","อู่ฮั่น","China","china"),
 "XIY":("Xi'an","ซีอาน","China","china"),"CGO":("Zhengzhou","เจิ้งโจว","China","china"),"TSN":("Tianjin","เทียนจิน","China","china"),
 "TAO":("Qingdao","ชิงเต่า","China","china"),"YNT":("Yantai","เยียนไถ","China","china"),"ENH":("Enshi","เอินซือ","China","china"),
 "WUX":("Wuxi","อู๋ซี","China","china"),"DSN":("Ordos","ออร์ดอส","China","china"),"DYG":("Zhangjiajie","จางเจียเจี้ย","China","china"),
 "PKX":("Beijing (Daxing)","ปักกิ่ง","China","china"),"NTG":("Nantong","หนานทง","China","china"),"HRB":("Harbin","ฮาร์บิน","China","china"),
 "HKG":("Hong Kong","ฮ่องกง","Hong Kong","hk-mo"),"MFM":("Macau","มาเก๊า","Macau","hk-mo"),
 "TPE":("Taipei","ไทเป","Taiwan","taiwan"),"KHH":("Kaohsiung","เกาสง","Taiwan","taiwan"),
 "NRT":("Tokyo (Narita)","โตเกียว","Japan","japan"),"KIX":("Osaka (Kansai)","โอซาก้า","Japan","japan"),"NGO":("Nagoya","นาโงย่า","Japan","japan"),
 "CTS":("Sapporo","ซัปโปโร","Japan","japan"),"FUK":("Fukuoka","ฟุกุโอกะ","Japan","japan"),"OKA":("Okinawa","โอกินาวา","Japan","japan"),
 "ICN":("Seoul (Incheon)","โซล","South Korea","korea"),
 "HAN":("Hanoi","ฮานอย","Vietnam","vietnam"),"SGN":("Ho Chi Minh City","โฮจิมินห์","Vietnam","vietnam"),"DAD":("Da Nang","ดานัง","Vietnam","vietnam"),
 "CXR":("Nha Trang (Cam Ranh)","ญาจาง","Vietnam","vietnam"),"PQC":("Phu Quoc","ฟูก๊วก","Vietnam","vietnam"),
 "DEL":("Delhi","เดลี","India","india"),"BOM":("Mumbai","มุมไบ","India","india"),"CCU":("Kolkata","โกลกาตา","India","india"),
 "MAA":("Chennai","เจนไน","India","india"),"BLR":("Bengaluru","เบงกาลูรู","India","india"),"HYD":("Hyderabad","ไฮเดอราบาด","India","india"),
 "COK":("Kochi","โคชิ","India","india"),"AMD":("Ahmedabad","อาเมดาบัด","India","india"),"JAI":("Jaipur","ชัยปุระ","India","india"),
 "GAY":("Bodh Gaya","พุทธคยา","India","india"),"LKO":("Lucknow","ลัคเนา","India","india"),"GAU":("Guwahati","กูวาหาติ","India","india"),
 "ATQ":("Amritsar","อมฤตสาร์","India","india"),
 "RGN":("Yangon","ย่างกุ้ง","Myanmar","myanmar"),
 "SIN":("Singapore","สิงคโปร์","Singapore","asean"),"KUL":("Kuala Lumpur","กัวลาลัมเปอร์","Malaysia","asean"),"PEN":("Penang","ปีนัง","Malaysia","asean"),
 "JHB":("Johor Bahru","ยะโฮร์บาห์รู","Malaysia","asean"),"SZB":("Kuala Lumpur (Subang)","กัวลาลัมเปอร์ (ซูบัง)","Malaysia","asean"),
 "CGK":("Jakarta","จาการ์ตา","Indonesia","asean"),"DPS":("Bali (Denpasar)","บาหลี","Indonesia","asean"),"SUB":("Surabaya","สุราบายา","Indonesia","asean"),
 "KNO":("Medan","เมดาน","Indonesia","asean"),"MNL":("Manila","มะนิลา","Philippines","asean"),
 "KTI":("Phnom Penh (Techo)","พนมเปญ","Cambodia","asean"),"SAI":("Siem Reap (Angkor)","เสียมราฐ","Cambodia","asean"),
 "VTE":("Vientiane","เวียงจันทน์","Laos","asean"),"LPQ":("Luang Prabang","หลวงพระบาง","Laos","asean"),
 "KTM":("Kathmandu","กาฐมาณฑุ","Nepal","other"),"CMB":("Colombo","โคลัมโบ","Sri Lanka","other"),"MLE":("Male","มาเล่","Maldives","other"),
 "ALA":("Almaty","อัลมาตี","Kazakhstan","other"),"RUH":("Riyadh","ริยาด","Saudi Arabia","other"),
}
S = {  # sources
 "2lnr":"2LNR schedule data (route pages 2lnr.com/routes/<org>-<dst>, schedule dated 4 Oct 2026, fetched 11 Oct 2026)",
 "aa_news":"https://newsroom.airasia.com/news/airasia-gears-up-for-high-season-with-major-international-expansion (22 Sep 2026)",
 "ar_fd4q":"https://www.aeroroutes.com/eng/260923-fdnw26int (23 Sep 2026)",
 "ar_xjhrb":"https://www.aeroroutes.com/eng/260929-xjnw26hrb (29 Sep 2026)",
 "tr_cts":"https://en.traicy.com/posts/2026082839472/ (Aug 2026)",
 "tr_ngo":"https://en.traicy.com/posts/2026091740140/ (17 Sep 2026)",
 "tr_fdfuk":"https://en.traicy.com/posts/2026082139200/",
 "tr_vzfuk":"https://en.traicy.com/posts/2026093040658/ (30 Sep 2026)",
 "kh_icn":"https://www.khaosodenglish.com/news/transpo/2026/09/16/thai-airasia-to-end-don-mueang-incheon-route-after-12-years/ (16 Sep 2026)",
 "ar_slin":"https://www.aeroroutes.com/eng/261007-sl2h26in (7 Oct 2026)",
 "ar_slicn":"https://www.aeroroutes.com/eng/260813-slnw26icn (13 Aug 2026)",
 "ar_slnrt":"https://www.aeroroutes.com/eng/260728-slnw26nrt (27 Jul 2026)",
 "ar_slns":"https://www.aeroroutes.com/eng/260525-slns26int (25 May 2026)",
 "ar_thns":"https://www.aeroroutes.com/eng/260722-thns26 (22 Jul 2026)",
 "ar_vznrt":"https://www.aeroroutes.com/eng/260528-vznw26nrt (28 May 2026)",
 "ar_vzkix":"https://www.aeroroutes.com/eng/260814-vjnw26kix (14 Aug 2026)",
 "ar_vzkul":"https://www.aeroroutes.com/eng/260603-vz4q26kul (3 Jun 2026)",
 "ar_vzhan":"https://www.aeroroutes.com/eng/260605-vz4q26han (5 Jun 2026)",
 "ar_vz1q":"https://www.aeroroutes.com/eng/260202-vz1q267m8 (2 Feb 2026)",
 "ttw_vzicn":"https://www.travelandtourworld.com/news/article/thai-vietjet-air-introduces-737-max-8-on-bangkokseoul-service/",
 "ar_vjred":"https://www.aeroroutes.com/eng/261002-vjnov26int (2 Oct 2026)",
 "ar_dd":"https://www.aeroroutes.com/eng/260811-dd4q26int (11 Aug 2026)",
 "wiki_dmk":"https://en.wikipedia.org/wiki/Don_Mueang_International_Airport (airlines & destinations, read 11 Oct 2026)",
 "wiki_bkk":"https://en.wikipedia.org/wiki/Suvarnabhumi_Airport (airlines & destinations, read 11 Oct 2026)",
 "bp_china":"https://www.bangkokpost.com/business/general/3324390/airasia-cuts-some-china-routes-amid-competition (23 Sep 2026)",
 "gf_probe":"Google Flights live results (curl of server-rendered search, Dec 10/14 2026 sample dates, run 11 Oct 2026)",
}
# manual overrides: (dst, carrier) -> dict(status, note, src, wk, times)
M = {
 ("KUL","FD"):dict(status="resumes",start="2026-10-25",wk=7,note="Resumes 25 Oct 2026, 1 daily A320",src=["ar_fd4q","aa_news"]),
 ("AMD","FD"):dict(status="resumes",start="2026-11-06",wk=4,note="Resumes 6 Nov 2026, 4/wk A320neo",src=["ar_fd4q","aa_news"]),
 ("HYD","FD"):dict(status="resumes",start="2026-11-16",wk=4,note="Resumes 16 Nov 2026, 4/wk A320",src=["ar_fd4q","aa_news"]),
 ("GAU","FD"):dict(status="resumes",start="2026-11-16",wk=4,note="Resumes 16 Nov 2026, 4/wk",src=["ar_fd4q"]),
 ("LKO","FD"):dict(status="resumes",start="2026-11-16",wk=4,note="Resumes 16 Nov 2026, 4/wk A320neo",src=["ar_fd4q"]),
 ("JAI","FD"):dict(status="resumes",start="2026-11-17",wk=4,note="Resumes 17 Nov 2026, 4/wk A320neo",src=["ar_fd4q"]),
 ("GAY","FD"):dict(status="seasonal",start="2026-10-25",note="Winter-seasonal (pilgrim season) from 25 Oct 2026",src=["aa_news"]),
 ("ICN","FD"):dict(status="ended",end="2026-10-24",note="Thai AirAsia ends DMK–Incheon after 24 Oct 2026 (until further notice) — no FD Korea in Nov–Apr",src=["kh_icn"]),
 ("HKG","FD"):dict(status="not_operating",note="FD HKG cancelled from 11 May 2026; no flights in current schedule data, no resumption found",src=["ar_thns","2lnr"]),
 ("FUK","FD"):dict(note="Daily since 22 Sep 2026",src=["tr_fdfuk","2lnr"]),
 ("CTS","XJ"):dict(wk="4 (Oct–Nov) → 7 (1 Dec–27 Mar)",note="XJ622 DMK 01:55→11:05 Tue/Thu/Sat/Sun to 30 Nov, daily 1 Dec 2026–27 Mar 2027, A330; to 29 Apr 2027",src=["tr_cts","aa_news"]),
 ("NGO","XJ"):dict(wk=4,note="XJ638 DMK 00:45→08:50 Mon/Wed/Fri/Sun, A330, 2 Oct 2026–26 Mar 2027 (typically suspended in summer)",src=["tr_ngo"]),
 ("NRT","XJ"):dict(note="Up to 21/wk in Q4 2026",src=["aa_news","2lnr"]),
 ("KIX","XJ"):dict(note="Up to 14/wk in Q4 2026",src=["aa_news","2lnr"]),
 ("DEL","XJ"):dict(wk=4,note="4/wk",src=["aa_news","2lnr"]),
 ("ALA","XJ"):dict(wk=4,note="4/wk",src=["aa_news","2lnr"]),
 ("HRB","XJ"):dict(status="charter",start="2026-12-15",end="2027-01-24",wk=6,times_out=["18:05→01:00+1"],times_ret=["02:15→07:45"],
                  note="Scheduled charter 15 Dec 2026–24 Jan 2027, 6/wk, XJ750/751, A330-300",src=["ar_xjhrb"]),
 ("RUH","XJ"):dict(status="not_operating",note="Suspended",src=["wiki_dmk","2lnr"]),
 ("AMD","SL"):dict(status="suspended",start="2026-12-17",wk=4,note="Suspended since 13 Sep 2026; tentative resumption 17 Dec 2026 (4/wk) — may change",src=["ar_slin"]),
 ("BLR","SL"):dict(status="suspended",start="2026-12-18",wk=4,note="Suspended; tentative resumption 18 Dec 2026 (4/wk)",src=["ar_slin"]),
 ("MAA","SL"):dict(status="suspended",start="2026-12-17",wk=4,note="Suspended since 21 Jun 2026; tentative 17 Dec 2026 (4/wk)",src=["ar_slin"]),
 ("DEL","SL"):dict(status="suspended",start="2026-12-18",wk=4,note="Suspended since 20 Jun 2026; tentative 18 Dec 2026 (4/wk)",src=["ar_slin"]),
 ("COK","SL"):dict(status="suspended",start="2026-12-17",wk=7,note="Suspended since 15 Sep 2026; tentative 17 Dec 2026 (daily)",src=["ar_slin"]),
 ("CCU","SL"):dict(status="suspended",start="2026-12-19",wk=4,note="Suspended since 15 Sep 2026; tentative 19 Dec 2026 (4/wk)",src=["ar_slin"]),
 ("BOM","SL"):dict(status="suspended",start="2026-12-17",wk=7,note="Suspended since 13 Sep 2026; tentative 17 Dec 2026 (daily)",src=["ar_slin"]),
 ("ATQ","SL"):dict(status="not_operating",note="Suspended since 26 May 2026, no resumption date filed",src=["ar_slin"]),
 ("ICN","SL"):dict(status="tentative",start="2026-12-01",wk=7,times_out=["03:15→10:55"],times_ret=["13:35→17:20"],
                  note="Tentatively resumes 1 Dec 2026 daily (SL352/353, 737-900ER) but reservations NOT open as of Aug 2026 — treat as unconfirmed",src=["ar_slicn"]),
 ("NRT","SL"):dict(status="not_nonstop",note="Operated DMK–Taipei–Narita (tag flight, 5/wk from 25 Oct 2026) — not nonstop",src=["ar_slnrt"]),
 ("OKA","SL"):dict(status="not_nonstop",note="Operated DMK–Taipei–Okinawa (4/wk from 26 Oct 2026) — not nonstop",src=["ar_slnrt"]),
 ("KIX","SL"):dict(status="not_nonstop",note="Operated via Taipei (tag) — not nonstop; not in current schedule data",src=["ar_slns"]),
 ("NGO","SL"):dict(status="not_nonstop",note="Operated via Taipei (tag) — not nonstop; not in current schedule data",src=["ar_slns"]),
 ("SUB","SL"):dict(status="not_operating",note="Suspended 2 Jun–1 Oct 2026; no flights in current schedule data",src=["ar_thns","2lnr"]),
 ("NRT","VZ"):dict(wk=11,times_out=["09:30→17:30 (x246)","23:55→07:55+1"],times_ret=["08:55→14:30","18:30→00:05+1 (x246)"],
                  note="11/wk from 6 Nov 2026 (VZ832 daytime x Tue/Thu/Sat + VZ830 red-eye daily), 737 MAX 8",src=["ar_vznrt"]),
 ("KIX","VZ"):dict(wk=7,times_out=["00:25→07:55"],times_ret=["08:55→13:30"],note="Daily from 13 Nov 2026 (was 4/wk), VZ820 red-eye, 737 MAX 8",src=["ar_vzkix"]),
 ("KUL","VZ"):dict(wk=7,times_out=["11:00→14:10"],times_ret=["15:15→16:30"],note="New, daily from 9 Oct 2026, 737 MAX 8",src=["ar_vzkul"]),
 ("HAN","VZ"):dict(wk=7,times_out=["09:25→11:15"],times_ret=["12:05→14:05"],note="New, daily from 5 Oct 2026 (winter times shown), 737 MAX 8",src=["ar_vzhan"]),
 ("FUK","VZ"):dict(status="resumes",start="2026-10-25",wk=4,note="Resumes 25 Oct 2026, 4/wk",src=["tr_vzfuk"]),
 ("ICN","VZ"):dict(wk=7,note="Daily (temporarily 4/wk 15–24 Oct 2026), 737 MAX 8",src=["ttw_vzicn","2lnr"]),
 ("MFM","VZ"):dict(status="charter",note="Scheduled charter in early 2026; not in current schedule data — verify",src=["ar_vz1q","2lnr"]),
 ("PKX","VZ"):dict(status="not_operating",note="Listed by 2LNR but no flights in next-7-day schedule — verify",src=["2lnr"]),
 ("WUX","VZ"):dict(status="charter",note="Charter-type (VZ 3xxx); no flights in next-7-day schedule",src=["2lnr"]),
 ("DSN","VZ"):dict(status="charter",note="Charter-type; no flights in next-7-day schedule",src=["2lnr"]),
 ("DYG","VZ"):dict(status="charter",note="Charter-type; inbound only in schedule data",src=["2lnr"]),
 ("SGN","VJ"):dict(wk="21 (25 Oct–6 Dec) → 28",note="VietJet (Vietnam) 4 daily, cut to 3 daily 25 Oct–6 Dec 2026",src=["ar_vjred","2lnr"]),
 ("HYD","DD"):dict(wk=4,times_out=["21:35→23:45"],times_ret=["00:45→05:45"],note="Resumed 14 Oct 2026, 4/wk 737-800 (DD958/959) through Mar 2027",src=["ar_dd"]),
 ("CGK","QZ"):dict(status="not_operating",note="Listed but no flights in schedule data",src=["2lnr"]),
}
CHARTER_NUM = re.compile(r"^(VZ|DD) 3\d{3}$")
R = json.load(open("src/2lnr_routes.json")); SCH = json.load(open("src/2lnr_sched.json"))
PROBE = json.load(open("src/probe-googleflights-2026-10-11.json")) if os.path.exists("src/probe-googleflights-2026-10-11.json") else {}
def d_(s):
    m = dt.datetime.strptime(s.split()[1], "%b").month
    return dt.date(2026 if m >= 7 else 2027, m, int(s.split()[2]))
DOW = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
def carrier_sched(rows, code):
    rows = [c for c in rows if c[1].split()[0] == code]
    if not rows: return None
    allds = sorted({d_(c[0]) for c in rows})
    times = collections.OrderedDict()
    for c in sorted(rows, key=lambda c: c[3]):
        times.setdefault(c[3], (c[1], c[4]))
    return dict(rows=rows, dows=sorted({d.weekday() for d in allds}), times=times, first=str(allds[0]))
def wk_est(v, code):
    rows = v["out"]; ds = sorted({d_(c[0]) for c in rows}); span = (ds[-1] - ds[0]).days + 1
    n = sum(1 for c in rows if c[1].split()[0] == code)
    return round(n * 7 / max(span, 7)), span < 7
def hhmm(t):  # "8:10 PM" -> "20:10"
    t = t.replace("\u202f", " "); h, m = map(int, re.match(r"(\d+):(\d+)", t).groups()); pm = "PM" in t
    return f"{(h % 12) + (12 if pm else 0):02d}:{m:02d}"
gf = collections.defaultdict(lambda: collections.defaultdict(lambda: {"times": set(), "priced": False, "seen": False}))
NAME2 = {"Thai AirAsia":"FD","Thai AirAsia X":"XJ","Thai Vietjet Air":"VZ","Vietjet":"VJ","Thai Lion Air":"SL","Nok Air":"DD",
         "AirAsia":"AK","Batik Air":"OD","Batik Air Malaysia":"OD","AirAsia Philippines":"Z2","Indonesia AirAsia":"QZ","Batik Air Indonesia":"ID"}
for k, v in PROBE.items():
    dst = k.split()[0]
    for f in v["flights"]:
        if f["stops"] != "Nonstop": continue
        names = [n.strip() for n in re.split(r",| and ", f["al"]) if n.strip()]
        code = NAME2.get(names[0]); org = "DMK" if "Don Mueang" in f["frm"] else "BKK"
        if not code: continue
        g = gf[(dst, code)][org]; g["seen"] = True; g["times"].add(hhmm(f["dep"])); g["priced"] |= bool(f["price"])
probed = {k.split()[0] for k in PROBE}
routes = {}
for a, lst in R.items():
    code = a.upper()
    for org, dst, name, href in lst:
        if dst in TH or code not in OUR: continue
        v = SCH.get(f"{org}-{dst}", {"out": [], "ret": []})
        ob = carrier_sched(v["out"], code); rb = carrier_sched(v["ret"], code)
        m = M.get((dst, code), {})
        e = dict(carrier=code, airline=OUR[code], origin=org, status=m.get("status", "operating" if ob else "not_in_schedule"))
        if ob:
            wk, trunc = wk_est(v, code)
            e["per_week"] = m.get("wk", wk)
            if trunc and "wk" not in m: e["per_week_note"] = "approx (schedule table truncated on busy route)"
            e["days"] = "daily" if len(ob["dows"]) == 7 else "/".join(DOW[i] for i in ob["dows"])
            if "wk" not in m and len(ob["dows"]) < 7: e["per_week"] = max(e["per_week"], len(ob["dows"]))
            if trunc:   # busy multi-carrier route: 2LNR table covers <7 calendar days, weekday pattern unknown
                e["days"] = e["ret_days_tmp"] = None
            if isinstance(m.get("wk"), int) and m["wk"] >= 7: e["days"] = "daily"
            e["flights"] = sorted({t[0] for t in ob["times"].values()})
            e["out_times"] = m.get("times_out", [f"{t}→{a2}" for t, (fl, a2) in ob["times"].items()])
            e["ret_times"] = m.get("times_ret", [f"{t}→{a2}" for t, (fl, a2) in rb["times"].items()] if rb else [])
            e["ret_days"] = ("daily" if rb and len(rb["dows"]) == 7 else "/".join(DOW[i] for i in rb["dows"])) if rb else None
            if e.get("ret_days_tmp", 1) is None or e["days"] == "daily": e["ret_days"] = e["days"]
            e.pop("ret_days_tmp", None)
            if all(CHARTER_NUM.match(f) for f in e["flights"]) and e["status"] == "operating": e["status"] = "charter"
        else:
            if "wk" in m: e["per_week"] = m["wk"]
            if "times_out" in m: e["out_times"] = m["times_out"]; e["ret_times"] = m.get("times_ret", [])
        for f in ("start", "end"):
            if f in m: e[f] = m[f]
        e["note"] = m.get("note", "")
        e["sources"] = [S[s] for s in (m.get("src") or ["2lnr"])]
        if "2lnr" not in (m.get("src") or ["2lnr"]): e["sources"].append(S["2lnr"])
        fam = {"VJ": ["VJ", "VZ"], "VZ": ["VZ", "VJ"], "OD": ["OD", "ID"], "ID": ["ID", "OD"]}.get(code, [code])
        g = None
        for fc in fam:
            g = gf.get((dst, fc), {}).get(org)
            if g and g["seen"]: break
        if dst in probed:
            e["google_flights"] = ({"listed": True, "priced": g["priced"], "dec_dep_times": sorted(g["times"])} if g and g["seen"]
                                   else {"listed": False})
        if e["status"] == "charter" and e.get("google_flights", {}).get("priced"):
            e["status"] = "operating"; e["note"] = (e["note"] + " " if e["note"] else "") + "Charter-style flight number (VZ 3xxx) but sold publicly — priced on Google Flights Dec 2026."
        elif e["status"] == "charter" and not e["note"]:
            e["note"] = "Charter-style flight number (3xxx); may be sold mainly via tour agents — verify on airline site."
        routes.setdefault(dst, []).append(e)
# HRB (XJ charter) not in 2LNR yet
routes.setdefault("HRB", []).append(dict(carrier="XJ", airline=OUR["XJ"], origin="DMK", status="charter", per_week=6,
    days="6/wk", flights=["XJ 750"], out_times=M[("HRB","XJ")]["times_out"], ret_times=M[("HRB","XJ")]["times_ret"],
    start="2026-12-15", end="2027-01-24", note=M[("HRB","XJ")]["note"], sources=[S["ar_xjhrb"]]))
USABLE = {"operating", "resumes", "seasonal", "suspended", "tentative", "charter"}
out = []
for dst, cs in routes.items():
    if dst not in CITY: continue
    en, th, country, region = CITY[dst]
    good = [c for c in cs if c["status"] in {"operating", "resumes", "seasonal"}]
    out.append(dict(code=dst, city=en, city_th=th, country=country, region=region, in_tg_dashboard=dst in TG or (dst == "NRT" and True),
                    origins=sorted({c["origin"] for c in good}), carriers_nonstop=sorted({c["carrier"] for c in good}),
                    total_per_week_approx=sum(c["per_week"] for c in good if isinstance(c.get("per_week"), int)),
                    carriers=sorted(cs, key=lambda c: (c["status"] not in USABLE, c["carrier"]))))
ORDER = ["china","hk-mo","taiwan","japan","korea","vietnam","india","myanmar","asean","other"]
out.sort(key=lambda r: (ORDER.index(r["region"]), -len(r["carriers_nonstop"]), -r["total_per_week_approx"], r["code"]))
no_lcc = {"XMN":"Xiamen — no in-scope LCC nonstop (only Xiamen Air / Spring Airlines etc.); TG flies from 25 Oct 2026",
          "PEK":"Beijing — no in-scope LCC nonstop operating (VZ PKX listed but no flights scheduled; FD/SL PKX not in schedule data)",
          "HND":"Tokyo Haneda — no LCC; use NRT (XJ, VZ)", "PUS":"Busan — no in-scope LCC nonstop found",
          "MDL":"Mandalay — no in-scope LCC nonstop found", "BOM/MAA/BLR/COK/CCU/DEL via SL":"Thai Lion India: suspended until mid-Dec 2026 (tentative)"}
meta = dict(title="Budget-airline (LCC) nonstop route matrix from Bangkok", window="Oct 2026 – Apr 2027", built="2026-10-11",
            carriers_in_scope=OUR, scope_note="Nonstop from DMK or BKK only. Thai domestic excluded. Times local; schedule tables are Oct 2026 (pre-winter) unless a note gives winter times; frequencies estimated from 2LNR next-7-service-days table.",
            status_legend={"operating":"in current schedule","resumes":"resumes on start date","seasonal":"winter-seasonal","suspended":"currently suspended; tentative restart on start date",
                           "tentative":"filed but not bookable yet","charter":"scheduled charter / charter-type flight numbers (often sold via tour agents)","ended":"ends before window",
                           "not_nonstop":"same-plane via another city","not_operating":"listed somewhere but no flights scheduled","not_in_schedule":"listed by 2LNR, no flights in next 7 service days"},
            google_flights_finding="Google Flights shows Thai AirAsia / AirAsia X schedules but 'Total price is unavailable' (no fares) in our checks; Thai Vietjet/VietJet are priced; Thai Lion Air appears only on some routes (e.g. HGH priced) and is missing on others (e.g. PVG). A fare sweep via Google Flights therefore covers VZ/VJ (+ some SL) prices; FD/XJ/SL fares need airasia.com / lionairthai.com (or an OTA) for exact prices.",
            no_lcc_nonstop=no_lcc, sources=S)
json.dump(dict(meta=meta, routes=out), open("routes.json", "w"), ensure_ascii=False, indent=1)
# markdown
L = [f"# {meta['title']} ({meta['window']})", "", f"Built {meta['built']} (Asia/Bangkok). {meta['scope_note']}", "",
     "**Google Flights coverage:** " + meta["google_flights_finding"], "",
     "Status: " + "; ".join(f"`{k}` = {v}" for k, v in meta["status_legend"].items()), ""]
RN = {"china":"China","hk-mo":"Hong Kong & Macau","taiwan":"Taiwan","japan":"Japan","korea":"South Korea","vietnam":"Vietnam","india":"India","myanmar":"Myanmar","asean":"ASEAN","other":"Other (outside main scope)"}
for reg in ORDER:
    rs = [r for r in out if r["region"] == reg]
    if not rs: continue
    L += [f"## {RN[reg]}", "", "| City | Airport | LCC nonstop (Nov–Apr) | From | ~/wk | Typical dep BKK→ / ←return | Notes |", "|---|---|---|---|---|---|---|"]
    for r in rs:
        for c in r["carriers"]:
            if c["status"] in ("not_in_schedule",) and not c.get("note"): continue
            gfx = c.get("google_flights")
            gnote = "" if not gfx else (" · GF: priced" if gfx.get("priced") else (" · GF: listed, no price" if gfx.get("listed") else " · GF: not listed"))
            if gfx and gfx.get("dec_dep_times"): gnote += " (Dec dep " + ", ".join(gfx["dec_dep_times"]) + ")"
            L.append(f"| {r['city']} {'★' if r['in_tg_dashboard'] else ''} | {r['code']} | {c['carrier']} {c['airline']} ({c['status']}) | {c['origin']} | {c.get('per_week','–')}{(' '+c['days']) if c.get('days') and c['days']!='daily' else (' daily' if c.get('days')=='daily' else '')} | {', '.join(c.get('out_times',[]) or ['–'])} / {', '.join(c.get('ret_times',[]) or ['–'])} | {c['note']}{gnote} |")
    L.append("")
L += ["★ = also on the Thai Airways dashboard.", "", "## No in-scope LCC nonstop", ""] + [f"- **{k}**: {v}" for k, v in no_lcc.items()]
L += ["", "## Sources", ""] + [f"- {k}: {v}" for k, v in S.items()]
open("routes.md", "w").write("\n".join(L) + "\n")
print(len(out), "cities;", sum(len(r["carriers"]) for r in out), "carrier-routes")
for r in out: print(r["code"], r["origins"], r["carriers_nonstop"], r["total_per_week_approx"])
