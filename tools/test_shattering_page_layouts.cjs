#!/usr/bin/env node
'use strict';
// Validate Shattering's 132 canonical authored page compositions without patch-layer fixtures.
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8'),json=p=>JSON.parse(read(p));
const html=read('index.html'),a=html.indexOf('const SHOW_MANIFEST='),b=html.indexOf('function safeFilePart(',a);
assert(a>=0&&b>a,'Assembler unavailable');
const context=vm.createContext({});
vm.runInContext(html.slice(a,b)+';globalThis.api={assembleScene,validatePageLayout};',context);
const {assembleScene,validatePageLayout}=context.api;
const shows=json('data/shows.json'),base='data/shows/shattering';
const store={};for(const f of ['characters','dialogue','settings','regions','factions','direction'])store[f+'.json']=json('data/'+f+'.json');
let count=0,lettering=0;const compositions=new Set();
for(let issue=1;issue<=6;issue++){
 const n=String(issue).padStart(2,'0'),show=shows.find(x=>x.id==='shattering-i'+n);
 assert(show,'Missing Shattering issue '+n);
 assert(!(show.sceneOverlays||[]).some(x=>x.mergeById),'Unexpected page-field overlay '+n);
 const pages=json(base+'/pages_i'+n+'.json');
 assert.equal(pages.length,24,'Page count changed '+n);
 const ids=new Set(pages.map(p=>p.id));assert.equal(ids.size,pages.length,'Duplicate page IDs '+n);
 store.__show=show;
 for(const [i,page] of pages.entries()){
  const noLayout={...page};delete noLayout.pageLayout;
  const before=assembleScene(noLayout,store,i),after=assembleScene(page,store,i);
  if(i===0||i===23){
   assert(!page.pageLayout,'Editorial bookend acquired story panel layout '+page.id);
   assert.equal(before,after,'Editorial bookend changed '+page.id);
   continue;
  }
  assert(page.pageLayout,'Missing canonical story page layout '+page.id);
  assert.equal(validatePageLayout(page),page.pageLayout,'Malformed layout '+page.id);
  assert.equal(page.pageLayout.panels.length,page.panelPlan.length,'Panel count mismatch '+page.id);
  const old=before.indexOf('\n[PANEL PLAN]'),layout=after.indexOf('\n[PAGE COMPOSITION]'),now=after.indexOf('\n[PANEL PLAN]');
  assert(old>=0&&layout>=0&&now>layout,'Page composition placement failed '+page.id);
  assert.equal(after.slice(0,layout),before.slice(0,old),'Pre-panel ingredients changed '+page.id);
  assert.equal(after.slice(now),before.slice(old),'Story and dialogue altered '+page.id);
  assert.equal((after.match(/\[PAGE COMPOSITION\]/g)||[]).length,1,'Duplicate layout '+page.id);
  for(const [j,panel] of page.panelPlan.entries()){
   assert(after.includes(panel),'Scripted panel lost '+page.id);
   assert(after.includes('Panel '+(j+1)+':'),'Composition lost panel assignment '+page.id);
  }
  for(const line of page.dialogueInline||[]){assert(after.includes(line.text),'Exact dialogue lost '+page.id);lettering++;}
  compositions.add(page.pageLayout.composition);count++;
 }
}
assert.equal(count,132,'Shattering story layout count changed');
assert(compositions.size>=7,'Composition variety lost');
console.log('PASS Shattering: '+count+' canonical page layouts, 12 editorial bookends, '+lettering+' exact dialogue items, '+compositions.size+' composition types.');
