#!/usr/bin/env node
'use strict';
// Canonical Sunforge source audit: historic layout/scope files are read-only migration fixtures.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8'),load=p=>JSON.parse(read(p));
const html=read('index.html'),from=html.indexOf('const SHOW_MANIFEST='),to=html.indexOf('function safeFilePart(',from);
assert(from>=0&&to>from,'Live assembler missing');
const sandbox=vm.createContext({});
vm.runInContext(html.slice(from,to)+';globalThis.api={assembleScene,validatePageLayout};',sandbox);
const {assembleScene:assemble,validatePageLayout:validate}=sandbox.api;
const shows=load('data/shows.json'),catalog=load('data/shows/sunforge-outlaw-s1/series.json');
const base='data/shows/sunforge-outlaw-s1',store={};
for(const item of ['characters','dialogue','settings','regions','factions','direction'])store[item+'.json']=load(base+'/'+item+'.json');
let pages=0,panels=0,lettering=0;
const compositions=new Set();
for(let issue=1;issue<=12;issue++){
 const n=String(issue).padStart(2,'0'),id='sunforge-outlaw-s1-e'+n;
 const show=shows.find(s=>s.id===id);assert(show,'Missing '+id);
 assert(!(show.sceneOverlays||[]).some(x=>x.mergeById),'Sunforge must not depend on field overlays '+id);
 const storyPath='pages_e'+n+'.json';
 assert((show.sceneOverlays||[]).some(x=>x.file===storyPath),'Canonical issue file not registered '+id);
 const script=load(base+'/'+storyPath),story=script.filter(p=>new RegExp('^SUN_S1E'+n+'_P\\d{2}$').test(p.id));
 const layout=load(base+'/editorial/page_layouts_e'+n+'.json');
 const scope=load(base+'/editorial/page_assembly_e'+n+'.json');
 const layouts=new Map(layout.map(p=>[p.id,p])),scopes=new Map(scope.map(p=>[p.id,p]));
 assert.equal(layouts.size,layout.length,'Duplicate archived layout IDs '+id);
 assert.equal(scopes.size,scope.length,'Duplicate archived scope IDs '+id);
 assert.equal(story.length,layout.length,'Layout footprint changed '+id);
 assert.equal(story.length,scope.length,'Scope footprint changed '+id);
 store.__show=show;
 for(const [j,page] of story.entries()){
  const l=layouts.get(page.id),s=scopes.get(page.id);
  assert(l&&s,'Missing canonical fields for '+page.id);
  assert.deepEqual(page.pageLayout,l.pageLayout,'Layout not embedded in source '+page.id);
  for(const [key,value] of Object.entries(s))if(key!=='id')
    assert.deepEqual(page[key],value,'Assembly scope not embedded in source '+page.id+' '+key);
  assert.equal(validate(page),page.pageLayout,'Invalid embedded page layout '+page.id);
  const bare={...page};delete bare.pageLayout;
  const before=assemble(bare,store,j),after=assemble(page,store,j);
  const oldMarker=before.indexOf('\n[PANEL PLAN]'),layoutMarker=after.indexOf('\n[PAGE COMPOSITION]'),newMarker=after.indexOf('\n[PANEL PLAN]');
  assert(oldMarker>=0&&layoutMarker>=0&&newMarker>layoutMarker,'Assembly sections missing '+page.id);
  assert.equal(before.slice(0,oldMarker),after.slice(0,layoutMarker),'Ingredient prefix changed '+page.id);
  assert.equal(before.slice(oldMarker),after.slice(newMarker),'Story/dialogue changed '+page.id);
  assert.equal((after.match(/\[PAGE COMPOSITION\]/g)||[]).length,1,'Duplicate layout block '+page.id);
  for(const line of page.dialogueInline||[])assert(after.includes(line.text),'Omitted exact lettering '+page.id);
  assert.equal(page.pageLayout.panels.length,page.panelPlan.length,'Panel mismatch '+page.id);
  pages++;panels+=page.panelPlan.length;lettering+=(page.dialogueInline||[]).length;
  compositions.add(page.pageLayout.composition);
 }
 for(const unit of script.filter(p=>!new RegExp('^SUN_S1E'+n+'_P\\d{2}$').test(p.id)))
  assert(unit.pageLayout===undefined,'Editorial unit incorrectly acquired story panel layout '+unit.id);
}
assert.equal(pages,catalog.sourceBoundary.pages,'Series source boundary drift');
console.log('PASS Sunforge canonical: '+pages+' pages, '+panels+' panels, '+lettering+' lettering items; '+compositions.size+' composition types; no active field overlays.');
