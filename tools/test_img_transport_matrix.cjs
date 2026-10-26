#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),os=require('node:os'),path=require('node:path'),cp=require('node:child_process'),crypto=require('node:crypto');
const ROOT=path.resolve(__dirname,'..');
const drafts=JSON.parse(fs.readFileSync(path.join(ROOT,'production/drafts/manifest.json'),'utf8')).drafts;
const references=JSON.parse(fs.readFileSync(path.join(ROOT,'production/references/reference-keeper-manifest.json'),'utf8')).references;
const issueBooks=JSON.parse(fs.readFileSync(path.join(ROOT,'production/book-manifests.json'),'utf8')).issues;
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const blob=b=>crypto.createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex');
const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'rex-img-matrix-'));
function run(script,env={},cwd=ROOT){return cp.spawnSync(process.execPath,[script],{cwd,env:{...process.env,...env},encoding:'utf8',maxBuffer:6*1024*1024})}
function checkPixels(filename){const p=cp.spawnSync('python3',['-c','from PIL import Image; import sys; im=Image.open(sys.argv[1]); im.load(); assert im.width>0 and im.height>0; print(im.format, im.size)',filename],{encoding:'utf8'});assert.equal(p.status,0,p.stderr)}
function sample(kind,key){
 const dir=fs.mkdtempSync(path.join(tmp,'one-'));
 const result=run('tools/prepare_img_readback.cjs',{ASSET_KIND:kind,ASSET_KEY:key,READBACK_OUTPUT:dir,GITHUB_SHA:'a'.repeat(40)});
 assert.equal(result.status,0,key+': '+result.stderr);
 const m=JSON.parse(fs.readFileSync(path.join(dir,'readback.json')));
 const entry=(kind==='draft'?drafts:references)[key],src=fs.readFileSync(path.join(ROOT,entry.image)),out=fs.readFileSync(path.join(dir,m.assetFilename));
 assert.ok(src.equals(out),'Original bytes changed: '+key);
 assert.equal(m.sha256,sha(src));assert.equal(m.gitBlobSha,blob(src));assert.equal(m.sourceRevision,'a'.repeat(40));
 assert.equal(m.pixelInspectionVerified,false);assert.equal(m.repoPath,entry.image);
 assert.equal(m.mimeType,entry.mimeType);checkPixels(path.join(dir,m.assetFilename));
 console.log('PASS '+kind+' '+key+' '+m.mimeType+' ('+src.length+' bytes, source decoded)');
}
try{
 const kinds=[['draft',drafts],['reference',references]];
 for(const [kind,items] of kinds){
  const tested=new Set();
  for(const [key,entry] of Object.entries(items)){
   const tag=entry.seriesId+'::'+entry.mimeType;
   if(!tested.has(tag)){sample(kind,key);tested.add(tag)}
  }
 }
 function book(series,issue,partial=false){
  const folder=fs.mkdtempSync(path.join(tmp,'issue-'));
  const r=run('tools/prepare_issue_readback.cjs',{SERIES_ID:series,ISSUE_ID:issue,ALLOW_INCOMPLETE:partial?'true':'false',ISSUE_READBACK_OUTPUT:folder,GITHUB_SHA:'b'.repeat(40)});
  assert.equal(r.status,0,r.stderr);
  const report=JSON.parse(fs.readFileSync(path.join(folder,'issue-readback.json')));
  const slots=issueBooks[series+'::'+issue].units;
  assert.deepEqual(report.expectedOrder,slots);
  assert.equal(report.expected,slots.length);assert.equal(report.complete,!partial);
  assert.equal(report.reviewOnly,partial);assert.equal(report.sourceRevision,'b'.repeat(40));
  assert.equal(report.pixelInspectionVerified,false);
  assert.equal(report.approved+report.missing.length,slots.length);
  for(const page of report.pages){
   const original=fs.readFileSync(path.join(ROOT,page.originalPath)),copy=fs.readFileSync(path.join(folder,page.file));
   assert.equal(slots[page.bookPage-1],page.recipeId);
   assert.ok(original.equals(copy));assert.equal(sha(copy),page.sha256);assert.equal(blob(copy),page.gitBlobSha);
   checkPixels(path.join(folder,page.file));
  }
  console.log('PASS book '+series+'::'+issue+' '+report.approved+'/'+report.expected+' native originals in order');
 }
 book('rex-fleet','rex-fleet-i01');
 // Incomplete issue is a *review-only* bundle with explicit missing-page inventory.
 book('vikings-2026','vikings-2026-s1-e02',true);
 book('stardust-station','stardust-station-e02',true);
 const reject=run('tools/prepare_issue_readback.cjs',{SERIES_ID:'rex-fleet',ISSUE_ID:'rex-fleet-i03',ISSUE_READBACK_OUTPUT:path.join(tmp,'issue-rejected')});
 assert.notEqual(reject.status,0,'Incomplete issue incorrectly succeeded');assert.ok(/Incomplete issue/.test(reject.stderr));
 assert.ok(!fs.existsSync(path.join(tmp,'issue-rejected')),'Disallowed incomplete issue left partial output');
 console.log('PASS incomplete issue fails closed before copying bytes');
 // Isolated manifest fixtures: verify corrupt binary, bad MIME, wrong hash, unapproved status and symlink escape.
 const sandbox=path.join(tmp,'sandbox');fs.mkdirSync(path.join(sandbox,'tools'),{recursive:true});
 fs.copyFileSync(path.join(ROOT,'tools/prepare_img_readback.cjs'),path.join(sandbox,'tools/prepare_img_readback.cjs'));
 const base='production/drafts/fixture/fixture-i01',imagePath=base+'/fixture_p01.png',key='fixture::fixture-i01::FIXTURE_P01';
 fs.mkdirSync(path.join(sandbox,base),{recursive:true});
 const canonical=fs.readFileSync(path.join(ROOT,Object.values(drafts).find(e=>e.mimeType==='image/png').image));
 function fixture(bytes,overrides={},image=imagePath){
  fs.writeFileSync(path.join(sandbox,imagePath),bytes);
  const item={seriesId:'fixture',issueId:'fixture-i01',recipeId:'FIXTURE_P01',status:'approved-production-draft',image,mimeType:'image/png',sha256:sha(bytes),...overrides};
  fs.writeFileSync(path.join(sandbox,'production/drafts/manifest.json'),JSON.stringify({schemaVersion:1,drafts:{[key]:item}}));
  return run('tools/prepare_img_readback.cjs',{ASSET_KIND:'draft',ASSET_KEY:key,READBACK_OUTPUT:path.join(sandbox,'output')},sandbox);
 }
 let ok=fixture(canonical);assert.equal(ok.status,0,ok.stderr);
 fs.rmSync(path.join(sandbox,'output'),{recursive:true,force:true});
 const broken=Buffer.from(canonical);broken[100]^=255;
 let bad=fixture(broken);assert.notEqual(bad.status,0,'Corrupt PNG CRC incorrectly accepted');
 assert.match(bad.stderr,/PNG CRC mismatch|PNG chunk/);
 assert.ok(!fs.existsSync(path.join(sandbox,'output')),'Corruption produced readback artifact');
 bad=fixture(canonical,{sha256:'f'.repeat(64)});assert.notEqual(bad.status,0,'Wrong digest accepted');
 bad=fixture(canonical,{mimeType:'image/jpeg'});assert.notEqual(bad.status,0,'MIME mismatch accepted');
 bad=fixture(canonical,{status:'rejected'});assert.notEqual(bad.status,0,'Rejected art accepted');
 // Symlink in parent directory, not just a symlink at the image path.
 const alias=path.join(sandbox,'production/drafts/fixture/fixture-i01');
 fs.renameSync(alias,alias+'-real');fs.symlinkSync(alias+'-real',alias,'dir');
 bad=run('tools/prepare_img_readback.cjs',{ASSET_KIND:'draft',ASSET_KEY:key,READBACK_OUTPUT:path.join(sandbox,'output')},sandbox);
 assert.notEqual(bad.status,0,'Parent-directory symlink was allowed');
 console.log('PASS negative fixtures: corrupt PNG, mismatched digest/MIME, rejected page, symlinked storage');
 // Format capability test: isolated original WebP and JPEG images, created solely for the test.
 fs.rmSync(alias,{force:true});fs.renameSync(alias+'-real',alias);
 for(const format of ['WEBP','JPEG']){
  const ext=format==='WEBP'?'.webp':'.jpg',mime='image/'+(format==='WEBP'?'webp':'jpeg');
  const dest=path.join(sandbox,base,'fixture_p01'+ext);
  const made=cp.spawnSync('python3',['-c',
   'from PIL import Image; import sys; Image.new("RGB",(10,8),(20,75,130)).save(sys.argv[1],format=sys.argv[2])',dest,format],{encoding:'utf8'});
  assert.equal(made.status,0,made.stderr);
  const bb=fs.readFileSync(dest);
  const ent={seriesId:'fixture',issueId:'fixture-i01',recipeId:'FIXTURE_P01',status:'approved-production-draft',image:base+'/fixture_p01'+ext,mimeType:mime,sha256:sha(bb)};
  fs.writeFileSync(path.join(sandbox,'production/drafts/manifest.json'),JSON.stringify({schemaVersion:1,drafts:{[key]:ent}}));
  fs.rmSync(path.join(sandbox,'output'),{recursive:true,force:true});
  const got=run('tools/prepare_img_readback.cjs',{ASSET_KIND:'draft',ASSET_KEY:key,READBACK_OUTPUT:path.join(sandbox,'output')},sandbox);
  assert.equal(got.status,0,got.stderr);assert.ok(fs.readFileSync(path.join(sandbox,'output','original'+ext)).equals(bb));
  checkPixels(dest);
  console.log('PASS isolated '+format+' exact image readback');
 }
 console.log('PASS universal IMG readback matrix');
}finally{fs.rmSync(tmp,{recursive:true,force:true})}
