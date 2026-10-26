#!/usr/bin/env node
'use strict';
// Exhaustive non-destructive audit of every current approved draft and Keeper image.
const fs=require('node:fs'),os=require('node:os'),path=require('node:path'),crypto=require('node:crypto'),cp=require('node:child_process'),assert=require('node:assert/strict');
const drafts=JSON.parse(fs.readFileSync('production/drafts/manifest.json','utf8')).drafts;
const keeper=JSON.parse(fs.readFileSync('production/references/reference-keeper-manifest.json','utf8')).references;
// Exception applies only to one exactly identified pre-existing corrupted original;
 // never converts the source into a readable image and never changes its manifest.
const KNOWN_UNREADABLE={
 'vikings-2026::vikings-2026-s1-e01::VIK_S1I01_P09':'9962326c108115d7a6bd7107d4a6cef58b238b29262bfb14e7e4ab269442d023'
};
const out=fs.mkdtempSync(path.join(os.tmpdir(),'rex-all-originals-'));
const stats={draft:0,reference:0,bytes:0,series:{},formats:{}},failed=[],blocked=[];
try{
 for(const [kind,manifest] of [['draft',drafts],['reference',keeper]]){
  for(const [key,entry] of Object.entries(manifest)){
   fs.rmSync(path.join(out,'one'),{recursive:true,force:true});
   const result=cp.spawnSync(process.execPath,['tools/prepare_img_readback.cjs'],{
    env:{...process.env,ASSET_KIND:kind,ASSET_KEY:key,READBACK_OUTPUT:path.join(out,'one')},
    encoding:'utf8',maxBuffer:500000});
   if(result.status!==0){
    const raw=fs.readFileSync(entry.image);
    const decoded=cp.spawnSync('python3',['-c',
      'from PIL import Image; import sys; im=Image.open(sys.argv[1]); print("Pillow format",im.format,"size",im.size); im.load(); print("Pillow full decode OK")',entry.image],{encoding:'utf8'});
    console.error('SOURCE FORENSICS '+JSON.stringify({key,sha256:crypto.createHash('sha256').update(raw).digest('hex'),bytes:raw.length,
      tailHex:raw.subarray(-32).toString('hex'),pillowStatus:decoded.status,pillowOutput:decoded.stdout.trim(),pillowError:decoded.stderr.trim().slice(0,200)}));
    const hash=crypto.createHash('sha256').update(raw).digest('hex');
    if(process.argv.includes('--allow-exact-known-blocker')&&KNOWN_UNREADABLE[key]===hash){
      blocked.push({key,sha256:hash,reason:'Pre-existing corrupt approved source; readback correctly rejected'});
      console.error('BLOCKED, NOT RETRIEVED '+key+' '+hash);
    }else failed.push(key+': '+result.stderr.trim().slice(0,300));
    continue
   }
   try{
    const meta=JSON.parse(fs.readFileSync(path.join(out,'one/readback.json')));
    const copy=fs.readFileSync(path.join(out,'one',meta.assetFilename)),original=fs.readFileSync(entry.image);
    assert.ok(copy.equals(original),'bytes changed');
    assert.equal(meta.sha256,crypto.createHash('sha256').update(original).digest('hex'));
    assert.equal(meta.gitBlobSha,crypto.createHash('sha1').update('blob '+copy.length+'\0').update(copy).digest('hex'));
    const loaded=cp.spawnSync('python3',['-c','from PIL import Image; import sys; im=Image.open(sys.argv[1]); im.load(); assert im.size[0]>0 and im.size[1]>0',path.join(out,'one',meta.assetFilename)],{encoding:'utf8'});
    assert.equal(loaded.status,0,loaded.stderr);
    stats[kind]++;stats.bytes+=copy.length;
    stats.series[entry.seriesId]=(stats.series[entry.seriesId]??0)+1;
    stats.formats[entry.mimeType]=(stats.formats[entry.mimeType]??0)+1;
   }catch(e){failed.push(key+': '+e.message)}
  }
 }
 console.log('PORTFOLIO TOTALS '+JSON.stringify(stats));
 console.log('KNOWN SOURCE BLOCKERS '+JSON.stringify(blocked));
 for(const x of failed)console.error('FAIL '+x);
 if(failed.length)throw Error(failed.length+' manifest-authorized assets failed full original readback/pixel decode');
 assert.equal(stats.draft+blocked.length,Object.keys(drafts).length);
 assert.equal(stats.reference,Object.keys(keeper).length);
 if(blocked.length){
  console.log('PASS every readable source; BLOCKED '+blocked.length+' known-corrupt approved source(s). No false pass: strict mode fails and canonical retrieval rejects.');
 }else console.log('PASS every manifest-authorized draft and Keeper asset, exact original bytes and decodable native pixels');
 if(blocked.length&&process.argv.includes('--strict'))throw Error('Strict full-portfolio readiness blocked by '+blocked.length+' corrupt approved source(s)');
}finally{fs.rmSync(out,{recursive:true,force:true})}
