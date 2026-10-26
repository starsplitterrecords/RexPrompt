#!/usr/bin/env node
'use strict';
/* Functional Keeper tests use original committed source images from EVERY series
 * with Keeper entries. Upload and reload are simulated without changing canon. */
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),crypto=require('node:crypto'),cp=require('node:child_process');
const K=require('../reference-keeper-contract.js');
const root=path.resolve(__dirname,'..');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const manifest=read('production/references/reference-keeper-manifest.json'),shows=read('data/shows.json');
const entries=Object.values(manifest.references);
const series=[...new Set(entries.map(x=>x.seriesId))].sort();
const ids=K.canonicalSeries(shows).map(s=>s.id);
assert(series.length>=6,'Existing six-series Keeper inventory must not shrink without review');
for(const sid of series)assert(ids.includes(sid),'Current Keeper series must be registered: '+sid);
const report=K.checkManifest(manifest,shows);
assert.deepEqual(report.errors,[],'All existing Keeper records must be structurally valid');
let passed=0;
const sha=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const refDir=fs.mkdtempSync(path.join(os.tmpdir(),'keeper-portfolio-'));
try{
 for(const sid of series){
   const representatives=entries.filter(x=>x.seriesId===sid);
   assert(representatives.length,'Missing representative '+sid);
   const byCategory=[...new Set(representatives.map(x=>x.type))];
   for(const category of byCategory){
     const ref=representatives.find(x=>x.type===category);
     const disk=fs.readFileSync(path.join(root,ref.image));
     assert.equal(K.sniff(disk),ref.mimeType,'MIME '+ref.id);
     const resultDir=path.join(refDir,String(passed));fs.mkdirSync(resultDir);
     const env={...process.env,ASSET_KIND:'reference',ASSET_KEY:ref.id,READBACK_OUTPUT:resultDir};
     const raw=cp.execFileSync(process.execPath,[path.join(root,'tools/prepare_img_readback.cjs')],{env,cwd:root,encoding:'utf8'});
     const summary=JSON.parse(raw.trim()),copy=fs.readFileSync(path.join(resultDir,summary.assetFilename));
     assert.equal(summary.repoPath,ref.image);
     assert.equal(summary.seriesId,sid);
     assert.equal(summary.mimeType,ref.mimeType);
     assert.equal(summary.sha256,sha(disk));
     assert.equal(sha(copy),sha(disk),'Readback must preserve exact original bytes: '+ref.id);
     const upload=K.planIntake({manifest,shows,seriesId:sid,type:category,
       name:'Portfolio Upload Test '+passed,fileName:'test.'+(ref.mimeType==='image/jpeg'?'jpg':ref.mimeType.split('/')[1]),
       mimeType:ref.mimeType,bytes:new Uint8Array(disk),now:'2026-10-25T00:00:00.000Z'});
     assert.equal(upload.entry.seriesId,sid);
     assert.equal(upload.entry.type,category);
     assert.deepEqual(upload.bytes,new Uint8Array(disk));
     const updated=JSON.parse(JSON.stringify(manifest));
     updated.references[upload.entry.id]=upload.entry; // manifest update
     const reload=JSON.parse(JSON.stringify(updated)); // cross-session reload
     assert.equal(K.selectEntries(reload,{seriesId:sid,type:category,query:'portfolio upload'}).length,1,
       'Search, category and series filters must resolve uploaded item after reload');
     assert.equal(K.selectEntries(reload,{seriesId:'nonexistent',query:'portfolio upload'}).length,0);
     assert(K.selectEntries(manifest,{seriesId:sid,type:category,query:ref.name.slice(0,3)}).some(x=>x.id===ref.id),
       'Current manifest reference searchable by name: '+ref.id);
     assert.throws(()=>K.planIntake({...upload,manifest:updated,shows,seriesId:sid,type:category,name:upload.entry.name,
       fileName:upload.entry.sourceFilename,mimeType:ref.mimeType,bytes:new Uint8Array(disk)}),/already exists|Duplicate/);
     const replaced=K.planIntake({manifest:updated,shows,seriesId:sid,type:category,
       name:upload.entry.name,fileName:upload.entry.sourceFilename,mimeType:ref.mimeType,
       bytes:new Uint8Array(disk),replaceId:upload.entry.id});
     assert.equal(replaced.entry.id,upload.entry.id);
     assert.equal(replaced.image,upload.image);
     assert.deepEqual(K.checkManifest(updated,shows).errors,[]);
     passed++;
   }
 }
 const png=entries.find(x=>x.mimeType==='image/png'),jpg=entries.find(x=>x.mimeType==='image/jpeg');
 assert(png&&jpg,'Expect original PNG and JPEG references');
 const original=fs.readFileSync(path.join(root,png.image));
 const args={manifest,shows,seriesId:png.seriesId,type:png.type,name:'Keeper Invalid Test',fileName:'keeper-invalid.png',
   mimeType:'image/png',bytes:new Uint8Array(original)};
 assert.throws(()=>K.planIntake({...args,seriesId:'unregistered'}),/Unknown canonical series/);
 assert.throws(()=>K.planIntake({...args,type:'invalid'}),/Unknown reference category/);
 assert.throws(()=>K.planIntake({...args,mimeType:'image/jpeg'}),/does not match/);
 assert.throws(()=>K.planIntake({...args,bytes:new Uint8Array(Buffer.from('fake-image'))}),/Invalid or unsupported/);
 assert.throws(()=>K.planIntake({...args,fileName:'traversal/attack.png'}),/Invalid original filename/);
 assert.throws(()=>K.planIntake({...args,fileName:'wrong.jpg'}),/extension/);
 const broken=JSON.parse(JSON.stringify(manifest));
 const sample=entries[0];
 broken.references[sample.id].seriesId='wrong-series';
 assert(K.checkManifest(broken,shows).errors.length>0,'Reject stale series associations');
 const doubled=JSON.parse(JSON.stringify(manifest));
 doubled.references['test::character::duplicate']={...sample,id:'test::character::duplicate'};
 assert(K.checkManifest(doubled,shows).errors.length>0,'Reject duplicate file paths and stale keys');
 const malformed='production/references/division-threshold/assets/page-language/dt-e001-p05-production-example.jpg';
 assert(!entries.some(x=>x.image===malformed||x.seriesId==='division-threshold'&&/checkpoint.?9/i.test(x.name)),
   'Known malformed Checkpoint 9 image must stay out of Keeper');
 console.log(JSON.stringify({seriesTested:series,categoriesTested:passed,
   uploadedIntoTemporaryManifests:passed,exactByteReadbacks:passed,
   currentKeeperEntries:entries.length,malformedCheckpoint9Excluded:true},null,2));
}finally{fs.rmSync(refDir,{recursive:true,force:true})}
