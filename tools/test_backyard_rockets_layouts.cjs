#!/usr/bin/env node
'use strict';
// Validate the 118 canonical Backyard Rockets episode page layouts; no retired layout fixtures.
const fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8'),json=p=>JSON.parse(read(p));
const show=json('data/shows.json').find(x=>x.id==='backyard-rockets-s1');
assert(show,'Backyard Rockets season missing');
assert(!(show.sceneOverlays||[]).some(x=>x.mergeById),'Active field patch not allowed');
const html=read('index.html'),start=html.indexOf('const SHOW_MANIFEST='),end=html.indexOf('function safeFilePart(',start);
assert(start>=0&&end>start,'Live assembler missing');
const sandbox=vm.createContext({});
vm.runInContext(html.slice(start,end)+';globalThis.api={assembleScene,validatePageLayout};',sandbox);
const {assembleScene,validatePageLayout}=sandbox.api,store={__show:show};
for(const f of ['characters','dialogue','settings','regions','factions','direction'])store[f+'.json']=json(show.basePath+'/'+f+'.json');
function episode(n){
 const tag=String(n).padStart(2,'0');
 const o=(show.sceneOverlays||[]).find(x=>x.encoding==='gzip-base64'&&x.file.includes('scenes_e'+tag+'_'));
 assert(o,'Missing canonical compressed episode '+tag);
 return JSON.parse(zlib.gunzipSync(Buffer.from(read(show.basePath+'/'+o.file).trim(),'base64')).toString('utf8'));
}
let total=0,sourcePanels=0;const kinds=new Map(),ids=new Set();
for(let ep=3;ep<=8;ep++){
 const pages=episode(ep);
 for(const [i,page] of pages.entries()){
  assert(page.pageLayout,'Canonical page layout missing '+page.id);
  assert(!ids.has(page.id),'Duplicate episode page '+page.id);ids.add(page.id);
  assert.equal(validatePageLayout(page),page.pageLayout);
  assert.equal(page.pageLayout.panels.length,page.panelPlan.length,'Panel hierarchy changed '+page.id);
  assert(Array.isArray(page.promptSuppress),'Missing canonical page recipe scope '+page.id);
  const bare={...page};delete bare.pageLayout;
  const before=assembleScene(bare,store,i),after=assembleScene(page,store,i);
  const old=before.indexOf('\n[PANEL PLAN]'),layout=after.indexOf('\n[PAGE COMPOSITION]'),now=after.indexOf('\n[PANEL PLAN]');
  assert(old>=0&&layout>=0&&now>layout,'Layout placement changed '+page.id);
  assert.equal(after.slice(0,layout),before.slice(0,old),'Recipe prefix changed '+page.id);
  assert.equal(after.slice(now),before.slice(old),'Scripted panel/dialogue tail changed '+page.id);
  assert.equal((after.match(/\[PAGE COMPOSITION\]/g)||[]).length,1,'Duplicate layout '+page.id);
  for(const d of page.dialogueInline||[])assert(after.includes(d.text),'Lost exact lettering '+page.id);
  kinds.set(page.pageLayout.composition,(kinds.get(page.pageLayout.composition)||0)+1);
  total++;sourcePanels+=page.panelPlan.length;
 }
}
for(const ep of [1,2])for(const page of episode(ep))
 assert(!page.pageLayout&&!ids.has(page.id),'Published Backyard issue changed by page-layout migration '+page.id);
assert.equal(total,118,'Non-published interior page inventory changed');
assert(sourcePanels>500,'Original panel beats missing');
assert(kinds.size>=7,'Insufficient editorial composition variety');
console.log('PASS Backyard Rockets: '+total+' canonical layouts, '+sourcePanels+' panels, '+kinds.size+' architectures, published Issues 1–2 unchanged.');
