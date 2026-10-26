#!/usr/bin/env node
'use strict';
// Read-only all-canonical-production image-completeness scan.
// Complements signature-only checks; never changes draft approval or image bytes.
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..');
const drafts=JSON.parse(fs.readFileSync(path.join(root,'production/drafts/manifest.json'),'utf8')).drafts;
const keeper=JSON.parse(fs.readFileSync(path.join(root,'production/references/reference-keeper-manifest.json'),'utf8')).references;
const errors=[],rows=[];const strict=process.argv.includes('--strict');
const signature=Buffer.from([137,80,78,71,13,10,26,10]);
function testPNG(b){
 if(b.length<45||!b.subarray(0,8).equals(signature))return {ok:false,reason:'PNG signature invalid'};
 let at=8,ihdr=null,foundEnd=false;
 while(at+12<=b.length){
  const n=b.readUInt32BE(at),tag=b.toString('ascii',at+4,at+8);
  if(n>b.length-at-12)return {ok:false,reason:'PNG '+tag+' chunk extends past end of source'};
  if(at===8){if(tag!=='IHDR'||n!==13)return {ok:false,reason:'invalid IHDR chunk'};ihdr=[b.readUInt32BE(at+8),b.readUInt32BE(at+12)];}
  at+=12+n;
  if(tag==='IEND'){foundEnd=true;if(n!==0)return {ok:false,reason:'IEND length nonzero'};break}
 }
 if(!foundEnd)return {ok:false,reason:'PNG missing complete IEND chunk'};
 if(at!==b.length)return {ok:false,reason:'Unexpected trailing bytes after PNG IEND'};
 if(!ihdr||ihdr.some(x=>x<1))return {ok:false,reason:'Invalid PNG dimensions'};
 return {ok:true,dimensions:ihdr};
}
function testJPEG(b){
 if(b.length<6||!b.subarray(0,3).equals(Buffer.from([255,216,255])))return {ok:false,reason:'JPEG invalid SOI'};
 if(b[b.length-2]!==255||b[b.length-1]!==217)return {ok:false,reason:'JPEG missing final EOI marker'};
 return {ok:true};
}
function verify(kind,key,entry){
 const file=entry.image,mime=entry.mimeType||'';
 if(!file||file.includes('..')||file.startsWith('/')){errors.push({kind,key,path:file,reason:'invalid manifest image path'});return}
 const p=path.join(root,file),suffix=path.extname(file).toLowerCase();
 if(!fs.existsSync(p)){errors.push({kind,key,path:file,reason:'missing stored image'});return}
 const b=fs.readFileSync(p);
 let result;
 if(mime==='image/png'&&suffix==='.png')result=testPNG(b);
 else if(mime==='image/jpeg'&&['.jpg','.jpeg'].includes(suffix))result=testJPEG(b);
 else result={ok:false,reason:'unhandled MIME/extension '+mime+' '+suffix};
 const row={kind,key,path:file,bytes:b.length,passed:result.ok,reason:result.reason||null,dimensions:result.dimensions||null};
 rows.push(row);
 if(!result.ok)errors.push(row);
}
for(const [k,v] of Object.entries(drafts))verify('draft',k,v);
for(const [k,v] of Object.entries(keeper))verify('reference',k,v);
const summary={draftRecords:Object.keys(drafts).length,referenceRecords:Object.keys(keeper).length,checked:rows.length,invalid:errors.length,byKind:{draft:rows.filter(x=>x.kind==='draft').length,reference:rows.filter(x=>x.kind==='reference').length}};
console.log('CANONICAL SOURCE IMAGE COMPLETENESS '+JSON.stringify(summary));
for(const e of errors)console.error('CORRUPT IMAGE '+JSON.stringify(e));
console.log('Boundary: this verifies a complete PNG chunk chain and JPEG EOI, not image interpretation, rendering fidelity, exact source resolution, or approval.');
if(process.argv.includes('--json'))fs.writeFileSync('canonical-source-image-completeness.json',JSON.stringify({summary,errors,files:rows},null,2)+'\n');
if(strict&&errors.length)process.exitCode=1;
