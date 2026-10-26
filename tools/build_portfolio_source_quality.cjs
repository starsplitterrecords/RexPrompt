#!/usr/bin/env node
'use strict';
// Snapshot of observed approved raster file geometry, not a print or artistic certification.
const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process');
const original=JSON.parse(fs.readFileSync('production/drafts/manifest.json','utf8')).drafts;
const processResult=cp.spawnSync(process.execPath,['tools/audit_issue_mastering.cjs','--json'],{encoding:'utf8',maxBuffer:12*1024*1024});
if(!processResult.stdout)throw Error('Mastering preflight did not return raster facts: '+processResult.stderr);
const facts=JSON.parse(processResult.stdout);
const findings={schemaVersion:1,method:'Direct binary signature and intrinsic pixel/header readback via tools/audit_issue_mastering.cjs; no image recompression, enlargement, artistic approval or color grade.',
  expectedRecords:Object.keys(original).length,examined:facts.decoded,issues:[],
  images:{}};
for(const x of facts.images){
 const entry=original[x.id];
 if(!entry||entry.image!==x.image)throw Error('Source quality metadata does not match approved manifest '+x.id);
 findings.images[x.id]={width:x.width,height:x.height,mimeType:x.type,colorProfile:x.colorProfile,bytes:x.bytes,sha256:x.sha256,
    source:'tools/audit_issue_mastering.cjs'};
}
for(const e of facts.errors)if(!e.includes('missing required book unit'))findings.issues.push({severity:'error',message:e});
if(facts.decoded!==Object.keys(original).length)findings.issues.push({severity:'error',message:'Not all approved draft binaries could be inspected'});
if(process.argv.includes('--out')){
 const idx=process.argv.indexOf('--out'),out=process.argv[idx+1];if(!out)throw Error('Missing output path');
 fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,JSON.stringify(findings,null,2)+'\n');
}
if(process.argv.includes('--emit-base64')){
 const raw=Buffer.from(JSON.stringify(findings)).toString('base64');
 for(let i=0;i<raw.length;i+=4096)console.log('PORTFOLIO_QUALITY_CHUNK:'+String(i/4096).padStart(4,'0')+':'+raw.slice(i,i+4096));
 console.log('PORTFOLIO_QUALITY_COMPLETE:'+Math.ceil(raw.length/4096));
}
console.log('PORTFOLIO QUALITY: '+findings.examined+'/'+findings.expectedRecords+' original binaries inspected, '+findings.issues.length+' integrity issues; print/color approval not asserted.');
if(findings.issues.length)process.exitCode=1;