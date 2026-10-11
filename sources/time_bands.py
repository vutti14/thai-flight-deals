"""Shared time bands for all dashboards. Source of truth: time_bands.json (same folder).
js_snippet() -> JS defining TB (bands) + helpers + CSS, injected into each page at the /*__BANDS__*/ placeholder.
Python helpers band_of()/rating() for routine runs and raw-note writing."""
import json, pathlib
B = json.loads((pathlib.Path(__file__).resolve().parent / "time_bands.json").read_text())
def _m(t): h, m = map(int, t.split(":")); return h * 60 + m
def _in(b, mins):
    a, z = _m(b["from"]), _m(b["to"])
    return a <= mins <= z if a <= z else (mins >= a or mins <= z)
def band_of(direction, hhmm):
    """direction 'out' | 'back'; returns the band dict for a departure time 'HH:MM'."""
    m = _m(hhmm)
    return next(b for b in B[direction] if _in(b, m))
def rating(direction, hhmm): return band_of(direction, hhmm)["label"]
JS = r"""
const TB=__TB__;
const tbMin=t=>{const m=String(t||"").match(/(\d{1,2}):(\d\d)/);return m?+m[1]*60+ +m[2]:null};
function tbBand(dir,t){const m=tbMin(t);if(m==null)return null;return TB[dir].find(b=>{const a=tbMin(b.from),z=tbMin(b.to);return a<=z?(m>=a&&m<=z):(m>=a||m<=z)})}
const TBSEL={out:new Set(TB.out.map(b=>b.id)),back:new Set(TB.back.map(b=>b.id))};
const tbOk=(dir,t)=>{const b=tbBand(dir,t);return !b||TBSEL[dir].has(b.id)};
const tbAll=dir=>TBSEL[dir].size===TB[dir].length;
const tbActive=()=>!tbAll("out")||!tbAll("back");
const tbRank=b=>b?TB.tones[b.tone].rank:9;
const tbGood=(dir,b)=>!!b&&TB.good_times[dir].includes(b.tone);
function tbBadge(dir,t,extra){const b=tbBand(dir,t);if(!b)return "";return `<span class="tbb tb-${b.tone}" title="${dir==="out"?"ขาไป":"ขากลับ"}ออก ${b.from}–${b.to}${extra?" · "+extra:""}">${dir==="out"?"ไป":"กลับ"} ${b.label}${extra?` <small>${extra}</small>`:""}</span>`}
function tbChips(el,dir,onchange){el.innerHTML=`<span class="tbn">${dir==="out"?"ขาไป":"ขากลับ"}</span>`+TB[dir].map(b=>`<button type="button" class="tbc tb-${b.tone} ${TBSEL[dir].has(b.id)?"on":""}" data-tb="${b.id}" aria-pressed="${TBSEL[dir].has(b.id)}"><b>${b.label}</b> ${b.from}–${b.to}</button>`).join("");
 el.onclick=e=>{const c=e.target.closest("[data-tb]");if(!c)return;const id=c.dataset.tb;if(TBSEL[dir].has(id))TBSEL[dir].delete(id);else TBSEL[dir].add(id);onchange()}}
function tbFromHash(h){["out","back"].forEach(dir=>{const k=dir==="out"?"ob":"bb";if(h.get(k)!=null){const v=h.get(k).split(",").filter(Boolean);TBSEL[dir]=new Set(TB[dir].map(b=>b.id).filter(id=>v.includes(id)))}});
 Object.entries(TB.legacy_params).forEach(([k,v])=>{if(h.get(k)==="1")Object.entries(v).forEach(([dir,ids])=>{if(h.get(dir==="out"?"ob":"bb")==null)ids.forEach(id=>TBSEL[dir].delete(id))})})}
function tbToHash(h){["out","back"].forEach(dir=>{if(!tbAll(dir))h.set(dir==="out"?"ob":"bb",[...TBSEL[dir]].join(","))})}
function tbLegend(){return ["out","back"].map(dir=>`<span>${dir==="out"?"ขาไป":"ขากลับ"}: ${TB[dir].map(b=>`<span class="tbb tb-${b.tone}">${b.label}</span> ${b.from}–${b.to}`).join(" ")}</span>`).join("")}
(function(){const css=Object.entries(TB.tones).map(([k,c])=>`.tb-${k}{background:${c.bg};color:${c.fg};border-color:${c.bd}}`).join("")+
 `.tbb{display:inline-flex;align-items:center;gap:3px;font-size:11.5px;font-weight:600;padding:1px 7px;border-radius:999px;white-space:nowrap;line-height:1.5;border:1px solid transparent}.tbb small{font-weight:400;font-size:10.5px;opacity:.85}`+
 `.tbrow{display:flex;gap:6px;overflow-x:auto;scrollbar-width:none;align-items:center;max-width:100%;padding:2px 0}.tbrow::-webkit-scrollbar{display:none}`+
 `.tbn{flex:none;font:500 13.5px 'Kanit',sans-serif;color:inherit;opacity:.85;min-width:46px}`+
 `.tbc{flex:none;border:1px solid;border-radius:999px;padding:0 12px;min-height:38px;cursor:pointer;font-size:13px;white-space:nowrap;display:inline-flex;align-items:center;gap:5px;font-family:inherit}`+
 `.tbc b{font-weight:700}.tbc:not(.on){background:#fff!important;color:#8a8494!important;border-color:#ddd8e4!important;text-decoration:line-through;text-decoration-color:rgba(0,0,0,.35)}`+
 `.tbc.on::before{content:"✓";font-weight:700}`;
 const s=document.createElement("style");s.textContent=css;document.head.appendChild(s)})();
"""
def js_snippet():
    data = {k: B[k] for k in ("out", "back", "tones", "good_times", "legacy_params")}
    return JS.replace("__TB__", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
if __name__ == "__main__":
    for d, t in [("out", "04:59"), ("out", "05:00"), ("out", "23:00"), ("back", "00:30"), ("back", "12:59"), ("back", "18:00"), ("back", "23:59")]:
        print(d, t, rating(d, t))
