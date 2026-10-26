#!/usr/bin/env node
'use strict';
// Byte-exact, manifest-authorized export; never changes approved source art.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const kind=process.env.ASSET_KIND||'',key=process.env.ASSET_KEY||'';
if(!['draft','reference'].includes(kind))throw Error('Invalid asset kind');
if(!key||key.length>500||!/^[A-Za-z0-9_.:-]+$/.test(key))throw Error('Invalid asset key');
const manifestFile=kind==='draft'?'production/drafts/manifest.json':'production/references/reference-keeper-manifest.json';
const m=JSON.parse(fs.readFileSync(manifestFile,'utf8'));
const entry=kind==='draft'?m.drafts?.[key]:m.references?.[key];
if(!entry)throw Error('Asset missing from authoritative manifest: '+key);
if(kind==='draft'&&(entry.status!=='approved-production-draft'||key!==[entry.seriesId,entry.issueId,entry.recipeId].join('::')))throw Error('Draft is not approved');
if(kind==='reference'&&key!==entry.id)throw Error('Reference key mismatch');
const root=path.resolve(kind==='draft'?'production/drafts':'production/references');
const file=path.resolve(entry.image||'');
if(!file.startsWith(root+path.sep)||!fs.existsSync(file)||!fs.statSync(file).isFile())throw Error('Unsafe or missing source image');
if(!fs.realpathSync(file).startsWith(fs.realpathSync(root)+path.sep))throw Error('Source path resolves outside canonical storage');
if(kind==='draft'&&!entry.image.startsWith('production/drafts/'+entry.seriesId+'/'+entry.issueId+'/'))throw Error('Unexpected draft storage');
if(kind==='reference'&&!entry.image.startsWith('production/references/'+entry.seriesId+'/keeper/'+entry.type+'/'))throw Error('Unexpected reference storage');
const bytes=fs.readFileSync(file);
if(bytes.length<24||bytes.length>50*1024*1024)throw Error('Invalid image byte count');
const png=bytes.toString('hex',0,8)==='89504e470d0a1a0a';
const jpg=bytes[0]===255&&bytes[1]===216&&bytes[bytes.length-2]===255&&bytes[bytes.length-1]===217;
const webp=bytes.toString('ascii',0,4)==='RIFF'&&bytes.toString('ascii',8,12)==='WEBP'&&
 bytes.readUInt32LE(4)===bytes.length-8&&['VP8 ','VP8L','VP8X'].includes(bytes.toString('ascii',12,16));
if(png){
 if(bytes.toString('ascii',12,16)!=='IHDR'||bytes.readUInt32BE(8)!==13||!bytes.readUInt32BE(16)||!bytes.readUInt32BE(20))throw Error('Invalid PNG IHDR');
 // Check every PNG chunk boundary and CRC, not just an 8-byte magic signature.
 const table=Array.from({length:256},(_,n)=>{for(let i=0;i<8;i++)n=n&1?0xedb88320^(n>>>1):n>>>1;return n>>>0});
 let pos=8,seenIEND=false;
 while(pos<bytes.length){
  if(pos+12>bytes.length)throw Error('Truncated PNG chunk');
  const length=bytes.readUInt32BE(pos),end=pos+12+length;
  if(end>bytes.length)throw Error('PNG chunk exceeds source bounds');
  let crc=0xffffffff;
  for(let i=pos+4;i<pos+8+length;i++)crc=table[(crc^bytes[i])&255]^(crc>>>8);
  if(((crc^0xffffffff)>>>0)!==bytes.readUInt32BE(pos+8+length))throw Error('PNG CRC mismatch');
  const type=bytes.toString('ascii',pos+4,pos+8);pos=end;
  if(type==='IEND'){if(length!==0||pos!==bytes.length)throw Error('Malformed PNG IEND');seenIEND=true;break}
 }
 if(!seenIEND)throw Error('PNG IEND missing');
}
const mime=png?'image/png':jpg?'image/jpeg':webp?'image/webp':null;
if(!mime||mime!==entry.mimeType)throw Error('Signature and MIME type disagree');
const ext=path.extname(file).toLowerCase();
if(!({ 'image/png':['.png'],'image/jpeg':['.jpg','.jpeg'],'image/webp':['.webp']}[mime]||[]).includes(ext))throw Error('Image extension/MIME mismatch');
const sha256=crypto.createHash('sha256').update(bytes).digest('hex');
if(entry.sha256&&entry.sha256.toLowerCase()!==sha256)throw Error('Approved image checksum mismatch');
const out=path.resolve(process.env.READBACK_OUTPUT||'readback');
fs.mkdirSync(out,{recursive:true});
const filename='original.'+(png?'png':jpg?'jpg':'webp');
fs.writeFileSync(path.join(out,filename),bytes,{flag:'wx'});
const result={kind,key,seriesId:entry.seriesId,repoPath:entry.image,mimeType:mime,bytes:bytes.length,sha256,sourceRevision:process.env.GITHUB_SHA||null,pixelInspectionVerified:false,gitBlobSha:crypto.createHash('sha1').update('blob '+bytes.length+'\0').update(bytes).digest('hex'),assetFilename:filename};
fs.writeFileSync(path.join(out,'readback.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify(result));