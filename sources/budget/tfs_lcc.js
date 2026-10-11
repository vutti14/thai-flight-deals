// Google Flights tfs builder for LCC sweeps (economy, 1 adult, round trip).
// Leg message: f2 date, f5 max stops (0 = nonstop only), f6 airline code (repeated once per airline),
// f13 origin airport(s) (repeated = multi-airport, e.g. DMK+BKK), f14 destination airport(s).
// Top level: f2=0, f3 legs, f8=1 adult, f9 cabin (1 economy), f19=1 round trip. Verified 11 Oct 2026 by decoding a working TG URL
// and by live checks (airline filter, multi-airport origin, nonstop filter).
function v(n){const o=[];while(n>127){o.push((n&0x7f)|0x80);n>>>=7;}o.push(n&0x7f);return Buffer.from(o);}
function tag(f,w){return v((f<<3)|w);}
function vf(f,n){return Buffer.concat([tag(f,0),v(n)]);}
function sf(f,s){const b=Buffer.from(s);return Buffer.concat([tag(f,2),v(b.length),b]);}
function mf(f,b){return Buffer.concat([tag(f,2),v(b.length),b]);}
const airport=c=>Buffer.concat([vf(1,1),sf(2,c)]);
const leg=(date,from,to,al,ns)=>Buffer.concat([sf(2,date),...(ns?[vf(5,0)]:[]),...al.map(a=>sf(6,a)),...from.map(c=>mf(13,airport(c))),...to.map(c=>mf(14,airport(c)))]);
function tfs(orig,dest,dep,ret,al,ns=true){
  const p=[vf(2,0),mf(3,leg(dep,orig,dest,al,ns)),mf(3,leg(ret,dest,orig,al,ns)),vf(8,1),vf(9,1),vf(19,1)];
  return Buffer.concat(p).toString("base64").replace(/\+/g,"-").replace(/\//g,"_").replace(/=+$/,"");
}
const url=(o,d,a,b,al,ns=true)=>`https://www.google.com/travel/flights/search?tfs=${tfs(o,d,a,b,al,ns)}&curr=THB&hl=en`;
module.exports={tfs,url};
if(require.main===module){const [o,d,a,b,al]=process.argv.slice(2);console.log(url(o.split(","),d.split(","),a,b,al.split(",")));}
