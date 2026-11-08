#!/usr/bin/env node
'use strict';
// Validate canonical Sunforge page layouts and exact authored ingredients, without external patch files.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8'),json=p=>JSON.parse(read(p));
const html=read('index.html'),a=html.indexOf('const SHOW_MANIFEST='),b=html.indexOf('function safeFilePart(',a);
assert(a>=0&&b>a,'Live assembler missing');
const sandbox=vm.createContext({});
vm.runInContext(html.slice(a,b)+';globalThis.api={assembleScene,validatePageLayout};',sandbox);
const {assembleScene,validatePageLayout}=sandbox.api;
const shows=json('data/shows.json'),catalog=json('data/shows/sunforge-outlaw-s1/series.json');
const base='data/shows/sunforge-outlaw-s1',store={};
for(const item of ['characters','dialogue','settings','regions','factions','direction'])store[item+'.json']=json(base+'/'+item+'.json');
let pages=0,panels=0,lettering=0;const compositions=new Set();
for(let issue=1;issue<=12;issue++){
 const n=String(issue).padStart(2,'0'),id='sunforge-outlaw-s1-e'+n;
 const show=shows.find(x=>x.id===id);assert(show,'Missing '+id);
 assert(!(show.sceneOverlays||[]).some(x=>x.mergeById),'Field overlay reintroduced '+id);
 assert((show.sceneOverlays||[]).some(x=>x.file==='pages_e'+n+'.json'),'Missing canonical issue source '+id);
 const all=json(base+'/pages_e'+n+'.json'),story=all.filter(x=>new RegExp('^SUN_S1E'+n+'_P\\d\\d$').test(x.id));
 assert(story.length>=20,'Insufficient authored pages '+id);
 store.__show=show;
 for(const [i,page] of story.entries()){
  assert(page.pageLayout,'Canonical page layout missing '+page.id);
  assert.equal(validatePageLayout(page),page.pageLayout,'Invalid canonical layout '+page.id);
  assert.equal(page.pageLayout.panels.length,page.panelPlan.length,'Panel hierarchy mismatch '+page.id);
  assert(Array.isArray(page.promptSuppress),'Missing canonical suppression scope '+page.id);
  assert(['cast','full','none'].includes(page.promptCharacterMode),'Unknown character mode '+page.id);
  const bare={...page};delete bare.pageLayout;
  const before=assembleScene(bare,store,i),after=assembleScene(page,store,i);
  const old=before.indexOf('\n[PANEL PLAN]'),layout=after.indexOf('\n[PAGE COMPOSITION]'),now=after.indexOf('\n[PANEL PLAN]');
  assert(old>=0&&layout>=0&&now>layout,'Layout delivery order changed '+page.id);
  assert.equal(before.slice(0,old),after.slice(0,layout),'Canonical ingredients changed '+page.id);
  assert.equal(before.slice(old),after.slice(now),'Panel/dialogue content changed '+page.id);
  for(const line of page.dialogueInline||[])assert(after.includes(line.text),'Lost exact lettering '+page.id);
  compositions.add(page.pageLayout.composition);
  pages++;panels+=page.panelPlan.length;lettering+=(page.dialogueInline||[]).length;
 }
 for(const unit of all.filter(x=>!new RegExp('^SUN_S1E'+n+'_P\\d\\d$').test(x.id)))
   assert(!unit.pageLayout,'Editorial unit incorrectly gained story panel layout '+unit.id);
}
assert.equal(pages,catalog.sourceBoundary.pages,'Sunforge story inventory drift');
assert.equal(panels,1073,'Sunforge authored panel count changed');
assert.equal(lettering,1388,'Sunforge authored dialogue inventory changed');
assert(compositions.size>=7,'Sunforge composition variety lost');
console.log('PASS Sunforge '+pages+' canonical page layouts, '+panels+' scripted panels, '+lettering+' dialogue entries, '+compositions.size+' architectures; no field overlays.');
