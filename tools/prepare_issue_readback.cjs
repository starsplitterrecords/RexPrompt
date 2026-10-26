#!/usr/bin/env node
'use strict';
// Package existing approved original images in exact book order. No image transforms.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),cp=require('node:child_process');
const series=process.env.SERIES_ID||'rex-fleet',issue=process.env.ISSUE_ID||'rex-fleet-i01';
const allowIncomplete=process.env.ALLOW_INCOMPLETE==='true';
if(!/^[a-z0-9-]+$/.test(series)||!/^[a-z0-9-]+$/.test(issue))throw Error('Invalid series or issue ID');
const books=JSON.parse(fs.readFileSync('production/book-manifests.json','utf8')).issues;
const book=books[[series,issue].join('::')];
if(!book||book.seriesId!==series||book.issueId!==issue)throw Error('No validated complete-book inventory');
const drafts=JSON.parse(fs.readFileSync('production/drafts/manifest.json','utf8')).drafts;
if(!Array.isArray(book.units)||!book.units.length||new Set(book.units).size!==book.units.length)throw Error('Invalid or duplicate book slots');
const out=process.env.ISSUE_READBACK_OUTPUT||'issue-readback';
const preflightMissing=book.units.filter(id=>!drafts[[series,issue,id].join('::')]||drafts[[series,issue,id].join('::')].status!=='approved-production-draft');
if(preflightMissing.length&&!allowIncomplete)throw Error('Incomplete issue: missing approved image(s): '+preflightMissing.join(', '));
fs.mkdirSync(out,{recursive:true});
fs.mkdirSync(path.join(out,'pages'),{recursive:true});
const collected=[],missing=[];
for(let i=0;i<book.units.length;i++){
 const id=book.units[i],key=[series,issue,id].join('::');
 const entry=drafts[key];
 if(!entry||entry.status!=='approved-production-draft'||!entry.image){missing.push({page:i+1,id});continue}
 const temp=path.join(out,'one');
 fs.rmSync(temp,{recursive:true,force:true});
 cp.execFileSync(process.execPath,['tools/prepare_img_readback.cjs'],{
   env:{...process.env,ASSET_KIND:'draft',ASSET_KEY:key,READBACK_OUTPUT:temp},stdio:'pipe'});
 const prov=JSON.parse(fs.readFileSync(path.join(temp,'readback.json'),'utf8'));
 const ext=path.extname(prov.assetFilename);
 const basename=String(i+1).padStart(3,'0')+'_'+id+ext;
 const src=path.join(temp,prov.assetFilename),target=path.join(out,'pages',basename);
 fs.copyFileSync(src,target);
 const bytes=fs.readFileSync(target);
 if(crypto.createHash('sha256').update(bytes).digest('hex')!==prov.sha256)throw Error('Issue copy checksum mismatch '+id);
 if(crypto.createHash('sha1').update('blob '+bytes.length+'\0').update(bytes).digest('hex')!==prov.gitBlobSha)throw Error('Issue source Git blob mismatch '+id);
 collected.push({bookPage:i+1,recipeId:id,originalPath:entry.image,file:'pages/'+basename,
  mimeType:prov.mimeType,bytes:bytes.length,sha256:prov.sha256,gitBlobSha:prov.gitBlobSha});
 fs.rmSync(temp,{recursive:true,force:true});
}
if(missing.length&&!allowIncomplete)throw Error('Issue is missing approved images: '+missing.map(x=>x.id).join(', '));
const report={schemaVersion:1,seriesId:series,issueId:issue,expected:book.units.length,approved:collected.length,expectedOrder:book.units,reviewOnly:missing.length>0,pixelInspectionVerified:false,
 missing,complete:missing.length===0,sourceRevision:process.env.GITHUB_SHA||'',orderPolicy:book.orderPolicy,
 status:'original-source-artifact-transport-only',pages:collected};
fs.writeFileSync(path.join(out,'issue-readback.json'),JSON.stringify(report,null,2)+'\n');
console.log('Issue source readback '+collected.length+'/'+book.units.length+' approved original files; '+missing.length+' missing');
