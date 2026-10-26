#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),os=require('node:os'),path=require('node:path'),assert=require('node:assert/strict'),cp=require('node:child_process'),crypto=require('node:crypto');
const cases=[['draft','azure-reach::azure-reach-s1-e02::AZR_S1E02_P09'],['draft','rex-fleet::rex-fleet-i01::RF_I01_P18'],['reference','division-threshold::character::axiom'],['reference','echoes-forgotten-war::character::modern-theo']];
for(const [kind,key] of cases){
 const out=fs.mkdtempSync(path.join(os.tmpdir(),'rex-img-'));
 try{
  const env={...process.env,ASSET_KIND:kind,ASSET_KEY:key,READBACK_OUTPUT:out};
  const data=JSON.parse(cp.execFileSync(process.execPath,['tools/prepare_img_readback.cjs'],{env,encoding:'utf8'}).trim());
  const m=JSON.parse(fs.readFileSync(kind==='draft'?'production/drafts/manifest.json':'production/references/reference-keeper-manifest.json','utf8'));
  const original=fs.readFileSync((kind==='draft'?m.drafts:m.references)[key].image),copy=fs.readFileSync(path.join(out,data.assetFilename));
  assert.ok(original.equals(copy),'Readback altered image '+key);
  assert.equal(data.gitBlobSha,crypto.createHash('sha1').update('blob '+original.length+'\0').update(original).digest('hex'));
  assert.equal(JSON.parse(fs.readFileSync(path.join(out,'readback.json'),'utf8')).sha256,data.sha256);
  console.log('PASS exact readback '+key);
 }finally{fs.rmSync(out,{recursive:true,force:true})}
}
for(const [kind,key] of [['draft','missing::issue::page'],['reference','bad/path']]){
 const out=fs.mkdtempSync(path.join(os.tmpdir(),'rex-reject-'));
 try{
  const bad=cp.spawnSync(process.execPath,['tools/prepare_img_readback.cjs'],{env:{...process.env,ASSET_KIND:kind,ASSET_KEY:key,READBACK_OUTPUT:out},encoding:'utf8'});
  assert.notEqual(bad.status,0,'Invalid asset not rejected');
  assert.equal(fs.readdirSync(out).length,0);
 }finally{fs.rmSync(out,{recursive:true,force:true})}
}
console.log('PASS image readback, integrity, and invalid-key rejection');