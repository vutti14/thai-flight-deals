// Google Flights tfs builder for GBA sweeps: no airline filter, nonstop (f5=0), 1 adult, cabin 1=economy 3=business,
// round trip (f19=1) or one-way (f19=2). Origin can be multi-airport (BKK,DMK). Same encoding as budget/tfs_lcc.js (verified 11 Oct 2026).
function v(n){const o=[];while(n>127){o.push((n&0x7f)|0x80);n>>>=7;}o.push(n&0x7f);return Buffer.from(o);}
function tag(f,w){return v((f<<3)|w);}
function vf(f,n){return Buffer.concat([tag(f,0),v(n)]);}
function sf(f,s){const b=Buffer.from(s);return Buffer.concat([tag(f,2),v(b.length),b]);}
function mf(f,b){return Buffer.concat([tag(f,2),v(b.length),b]);}
const airport=c=>Buffer.concat([vf(1,1),sf(2,c)]);
// win=[h0,h1]: leg fields f8/f9 = earliest/latest departure hour (inclusive). Verified live 11 Oct 2026: f8=6,f9=10 on BKK-HKG 17 Nov
// returned only 07:30/08:00/10:30; f8=18,f9=23 on HKG-BKK returned only 18:55-23:35 departures.
const leg=(date,from,to,al=[],win=null)=>Buffer.concat([sf(2,date),vf(5,0),...al.map(a=>sf(6,a)),...(win?[vf(8,win[0]),vf(9,win[1])]:[]),...from.map(c=>mf(13,airport(c))),...to.map(c=>mf(14,airport(c)))]);
function tfs(orig,dest,dep,ret,cabin,al=[],wOut=null,wBack=null){
  const legs=[mf(3,leg(dep,orig,dest,al,wOut))]; if(ret) legs.push(mf(3,leg(ret,dest,orig,al,wBack)));
  const p=[vf(2,0),...legs,vf(8,1),vf(9,cabin),vf(19,ret?1:2)];
  return Buffer.concat(p).toString("base64").replace(/\+/g,"-").replace(/\//g,"_").replace(/=+$/,"");
}
const url=(o,d,a,b,cab,al=[],wo=null,wb=null)=>`https://www.google.com/travel/flights/search?tfs=${tfs(o,d,a,b,cab,al,wo,wb)}&curr=THB&hl=en`;
module.exports={tfs,url};
if(require.main===module){const [o,d,a,b,c,al]=process.argv.slice(2);console.log(url(o.split(","),d.split(","),a,b==="-"?null:b,+(c||1),al?al.split(","):[]));}
