// Deterministic gzip-base64 JSON transport for RexPrompt's existing encoded page files.
// Supports stored and Huffman-compressed DEFLATE on read; produces portable stored-block gzip on write.
const codec=(()=>{
 const ABC="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
 function b64d(s){let x=0,b=0,r=[];for(const c of s.trim()){if(c==="=")break;const k=ABC.indexOf(c);if(k<0)continue;x=x<<6|k;b+=6;if(b>=8){b-=8;r.push(x>>>b&255)}}return r}
 function b64e(a){let s="";for(let i=0;i<a.length;i+=3){let v=a[i]<<16|(a[i+1]||0)<<8|(a[i+2]||0);s+=ABC[v>>>18&63]+ABC[v>>>12&63]+(i+1<a.length?ABC[v>>>6&63]:"=")+(i+2<a.length?ABC[v&63]:"=")}return s}
 function utf(a){let s="";for(let i=0;i<a.length;){let c=a[i++],v=c;if(c>=240)v=(c&7)<<18|(a[i++]&63)<<12|(a[i++]&63)<<6|a[i++]&63;else if(c>=224)v=(c&15)<<12|(a[i++]&63)<<6|a[i++]&63;else if(c>=192)v=(c&31)<<6|a[i++]&63;s+=String.fromCodePoint(v)}return s}
 function bytes(s){let a=[];for(const ch of s){const n=ch.codePointAt(0);if(n<128)a.push(n);else if(n<2048)a.push(192|n>>6,128|n&63);else if(n<65536)a.push(224|n>>12,128|(n>>6)&63,128|n&63);else a.push(240|n>>18,128|(n>>12)&63,128|(n>>6)&63,128|n&63)}return a}
 function crc(a){let c=-1;for(const b of a){c^=b;for(let j=0;j<8;j++)c=c>>>1^((c&1)?0xedb88320:0)}return(~c)>>>0}
 function huff(lengths){const count=Array(16).fill(0),next=Array(16).fill(0),tables=Array.from({length:16},()=>new Map());for(const n of lengths)if(n)count[n]++;let code=0;for(let bits=1;bits<=15;bits++){code=(code+count[bits-1])*2;next[bits]=code}for(let sym=0;sym<lengths.length;sym++){let len=lengths[sym];if(!len)continue;let x=next[len]++,rev=0;for(let k=0;k<len;k++)rev=rev<<1|(x>>k&1);tables[len].set(rev,sym)}return br=>{let bits=0;for(let len=1;len<=15;len++){bits|=br.read(1)<<(len-1);const s=tables[len].get(bits);if(s!==undefined)return s}throw Error("Invalid Huffman symbol")}}
 function decode(s){const a=b64d(s);if(a[0]!==31||a[1]!==139||a[2]!==8)throw Error("Invalid gzip header");let at=10,flag=a[3];if(flag&4){let n=a[at]|a[at+1]<<8;at+=2+n}if(flag&8)while(a[at++]);if(flag&16)while(a[at++]);if(flag&2)at+=2;
 const br={pos:at*8,read(n){let v=0;for(let i=0;i<n;i++){if(this.pos>=a.length*8)throw Error("Deflate EOF");v|=(a[this.pos>>>3]>>>(this.pos&7)&1)<<i;this.pos++}return v},align(){this.pos=(this.pos+7)&~7}};
 const out=[],lb=[3,4,5,6,7,8,9,10,11,13,15,17,19,23,27,31,35,43,51,59,67,83,99,115,131,163,195,227,258],le=[0,0,0,0,0,0,0,0,1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,0],db=[1,2,3,4,5,7,9,13,17,25,33,49,65,97,129,193,257,385,513,769,1025,1537,2049,3073,4097,6145,8193,12289,16385,24577];
 let final=0;while(!final){final=br.read(1);const type=br.read(2);if(type===0){br.align();const n=br.read(16),nn=br.read(16);if((n^nn)!==65535)throw Error("Stored block length mismatch");for(let i=0;i<n;i++)out.push(br.read(8));continue}
 let lit,dist;if(type===1){lit=huff(Array.from({length:288},(_,i)=>i<=143?8:i<=255?9:i<=279?7:8));dist=huff(Array(32).fill(5))}
 else if(type===2){let nl=br.read(5)+257,nd=br.read(5)+1,nc=br.read(4)+4,order=[16,17,18,0,8,7,9,6,10,5,11,4,12,3,13,2,14,1,15],cl=Array(19).fill(0);for(let i=0;i<nc;i++)cl[order[i]]=br.read(3);const readCode=huff(cl),lengths=[];while(lengths.length<nl+nd){let sym=readCode(br);if(sym<=15)lengths.push(sym);else if(sym===16){let repeat=br.read(2)+3,prev=lengths.at(-1);if(prev===undefined)throw Error("Uninitialized repeat");while(repeat--)lengths.push(prev)}else if(sym===17){let repeat=br.read(3)+3;while(repeat--)lengths.push(0)}else if(sym===18){let repeat=br.read(7)+11;while(repeat--)lengths.push(0)}}lit=huff(lengths.slice(0,nl));dist=huff(lengths.slice(nl,nl+nd))}
 else throw Error("Reserved DEFLATE type");
 while(true){const sym=lit(br);if(sym<256){out.push(sym);continue}if(sym===256)break;const k=sym-257;if(k<0||k>=lb.length)throw Error("Invalid length symbol");let len=lb[k]+br.read(le[k]),d=dist(br);if(d>=db.length)throw Error("Invalid distance code");let distance=db[d]+br.read(d<4?0:Math.floor(d/2)-1);if(distance<=0||distance>out.length)throw Error("Invalid backreference");for(let i=0;i<len;i++)out.push(out[out.length-distance])}
 }
 const n=br.pos+7>>3,expected=a[n]|a[n+1]<<8|a[n+2]<<16|a[n+3]<<24,size=(a[n+4]|a[n+5]<<8|a[n+6]<<16|a[n+7]<<24)>>>0;
 if(out.length!==size||crc(out)!==(expected>>>0))throw Error("Gzip CRC/size mismatch");
 return JSON.parse(utf(out));
 }
 function encode(obj){let raw=bytes(JSON.stringify(obj)),out=[31,139,8,0,0,0,0,0,0,3],p=0;while(p<raw.length){let n=Math.min(65535,raw.length-p);out.push(p+n===raw.length?1:0,n&255,n>>8,~n&255,~n>>8&255,...raw.slice(p,p+n));p+=n}if(!raw.length)out.push(1,0,0,255,255);const checksum=crc(raw);for(let k=0;k<4;k++)out.push(checksum>>>k*8&255);for(let k=0;k<4;k++)out.push(raw.length>>>k*8&255);return b64e(out)}
 function fold(scenes,patches){const map=new Map(patches.map(x=>[x.id,x])),known=new Set(scenes.map(x=>x.id));if(map.size!==patches.length||patches.some(x=>!known.has(x.id)))throw Error("Missing or duplicate strict page patch");return scenes.map(s=>map.has(s.id)?{...s,...map.get(s.id)}:s)}
 function dialogue(scenes,patches){const map=new Map(patches.map(x=>[x.id,x]));return scenes.map(s=>{const p=map.get(s.id),lines=p?.dialogueInline||p?.sceneDialogue;return Array.isArray(lines)?{...s,dialogueInline:lines,dialogueSource:p.dialogueSource||"scene-dialogue overlay"}:s})}
 return {decode,encode,fold,dialogue};
})();
