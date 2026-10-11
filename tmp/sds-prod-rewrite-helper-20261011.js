(function(){
const ALPHA="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
function from64(s){let a=[],v=0,n=0;for(let c of s.replace(/\s/g,"")){if(c==="=")break;let k=ALPHA.indexOf(c);if(k<0)continue;v=(v<<6)|k;n+=6;if(n>=8){n-=8;a.push(v>>n&255)}}return a}
function to64(a){let s="";for(let i=0;i<a.length;i+=3){let x=a[i]<<16|(a[i+1]||0)<<8|(a[i+2]||0);s+=ALPHA[x>>>18&63]+ALPHA[x>>>12&63]+(i+1<a.length?ALPHA[x>>>6&63]:"=")+(i+2<a.length?ALPHA[x&63]:"=")}return s}
function decodeUTF8(a){let s="";for(let i=0;i<a.length;){let x=a[i++];if(x<128){s+=String.fromCharCode(x);continue}let n=x<224?1:x<240?2:3,cp=x&((1<<(6-n))-1);for(let k=0;k<n;k++)cp=(cp<<6)|(a[i++]&63);s+=String.fromCodePoint(cp)}return s}
function encodeUTF8(s){let a=[];for(let c of s){let k=c.codePointAt(0);if(k<128)a.push(k);else if(k<2048)a.push(192|k>>6,128|k&63);else if(k<65536)a.push(224|k>>12,128|(k>>6)&63,128|k&63);else a.push(240|k>>18,128|(k>>12)&63,128|(k>>6)&63,128|k&63)}return a}
function inflateGzip(a){
let pos=10,buf=0,bits=0,out=[];
if(a[0]!==31||a[1]!==139||a[2]!==8)throw Error("not gzip");
if(a[3]!==0)throw Error("unsupported gzip flags");
function get(n){while(bits<n){if(pos>=a.length)throw Error("truncated gzip");buf|=a[pos++]<<bits;bits+=8}let x=buf&((1<<n)-1);buf>>>=n;bits-=n;return x}
function huff(ls){let cnt=new Array(16).fill(0),next=new Array(16).fill(0),map=new Map(),code=0,max=0;for(let n of ls)if(n){cnt[n]++;if(n>max)max=n}for(let n=1;n<=15;n++){code=(code+cnt[n-1])*2;next[n]=code}for(let sym=0;sym<ls.length;sym++){let n=ls[sym];if(!n)continue;let c=next[n]++,rev=0;for(let k=0;k<n;k++){rev=(rev<<1)|(c&1);c>>>=1}map.set((1<<n)|rev,sym)}return ()=>{let n=0,c=0;while(++n<=max){c|=get(1)<<(n-1);let y=map.get((1<<n)|c);if(y!==undefined)return y}throw Error("invalid huffman "+pos)}}
const LB=[3,4,5,6,7,8,9,10,11,13,15,17,19,23,27,31,35,43,51,59,67,83,99,115,131,163,195,227,258],LE=[0,0,0,0,0,0,0,0,1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,0],DB=[1,2,3,4,5,7,9,13,17,25,33,49,65,97,129,193,257,385,513,769,1025,1537,2049,3073,4097,6145,8193,12289,16385,24577],DE=[0,0,0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,11,12,12,13,13];
let last=0;do{last=get(1);let typ=get(2),lit,dist;
if(typ===0){let rem=bits%8;if(rem)get(rem);let len=get(16),inv=get(16);if((len^inv)!==65535)throw Error("stored len");for(let i=0;i<len;i++)out.push(get(8));continue}
if(typ===1){lit=huff(Array.from({length:288},(_,i)=>i<144?8:i<256?9:i<280?7:8));dist=huff(Array(32).fill(5))}
else if(typ===2){let hlit=get(5)+257,hdist=get(5)+1,hclen=get(4)+4,order=[16,17,18,0,8,7,9,6,10,5,11,4,12,3,13,2,14,1,15],cl=Array(19).fill(0);for(let i=0;i<hclen;i++)cl[order[i]]=get(3);let ch=huff(cl),lens=[];while(lens.length<hlit+hdist){let c=ch();if(c<=15)lens.push(c);else{let repeat=c===16?get(2)+3:c===17?get(3)+3:get(7)+11,fill=c===16?lens[lens.length-1]:0;for(let i=0;i<repeat;i++)lens.push(fill)}}lit=huff(lens.slice(0,hlit));dist=huff(lens.slice(hlit))}
else throw Error("bad deflate type");
while(true){let sym=lit();if(sym<256){out.push(sym);continue}if(sym===256)break;let j=sym-257;if(j<0||j>=LB.length)throw Error("bad lit");let len=LB[j]+get(LE[j]),k=dist(),dd=DB[k]+get(DE[k]);if(dd>out.length)throw Error("bad dist");for(let i=0;i<len;i++)out.push(out[out.length-dd]);}
}while(!last);return out;
}
function gunzip64(s){return decodeUTF8(inflateGzip(from64(s)))}
function gzip64(s){let a=encodeUTF8(s),b=[31,139,8,0,0,0,0,0,0,3],crc=0xffffffff;for(let x of a){crc^=x;for(let j=0;j<8;j++)crc=crc&1?(crc>>>1)^0xedb88320:crc>>>1}crc^=0xffffffff;for(let i=0;i<a.length;){let n=Math.min(65000,a.length-i);b.push(i+n===a.length?1:0,n&255,n>>>8&255,~n&255,(~n)>>>8&255,...a.slice(i,i+n));i+=n}for(let j=0;j<4;j++)b.push(crc>>>j*8&255);for(let j=0;j<4;j++)b.push((a.length>>>0)>>>j*8&255);return to64(b)}
const names={Astra:["Astra Vega","@sds.Astra"],Mira:["Mira Klare","@sds.Mira"],Jax:["Jax Orien","@sds.Jax"],Noola:["Noola Vaneel","@sds.Noola"],Zib:["Zib “Sgotcha” Diaz","@sds.Zib"],Glorp:["Glorp","@sds.Glorp"],Kreeb:["Kreeb","@sds.Kreeb"],Pixa:["Pixa","@sds.Pixa"],Brick:["Brick Talos","@sds.Brick"],Liaison:["Operations Liaison","@sds.Liaison"],Station:["Station System","@sds.Station"]};
function dialogue(k,n,text){let v=names[k];if(!v)throw Error("unknown speaker "+k);return {handle:v[1],speaker:v[0],text,subtext:"Panel "+n}}
function apply(pages,recipe,issue){let seen=new Set();for(let p of pages){let n=p.page||Number(p.id?.match(/P(\d+)$/)?.[1]),entries=recipe[n];if(!entries)throw Error("missing rewrite "+issue+"/"+n);seen.add(n);let casts=new Set((p.charactersInline||[]).map(x=>x.handle));for(let k of p.characters||[]){let key=k.replace(/^SDS_/,"");if(names[key])casts.add(names[key][1]);}let max=p.panelCount||p.panelPlan.length;p.dialogueInline=entries.map(x=>{let [pn,k,tx]=x;if(pn<1||pn>max)throw Error("panel out of range "+issue+"/"+n+" "+pn);let z=dialogue(k,pn,tx);if(!casts.has(z.handle))throw Error("speaker not cast "+issue+"/"+n+" "+k);return z});p.dialogueSource="Season 1 relationship-first production rewrite 2026-10-11";}return pages}
return {gunzip64,gzip64,dialogue,apply,names}
})()