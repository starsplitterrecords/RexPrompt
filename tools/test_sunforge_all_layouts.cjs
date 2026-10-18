#!/usr/bin/env node
'use strict';
// Mechanical audit only: layout metadata may change, but authored story is untouched.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const read=relative=>fs.readFileSync(path.join(root,relative),'utf8');
const load=relative=>JSON.parse(read(relative));
const html=read('index.html');
const from=html.indexOf('const SHOW_MANIFEST='),to=html.indexOf('function safeFilePart(',from);
assert(from>=0&&to>from,'Live assembler missing');
const sandbox=vm.createContext({});
vm.runInContext(html.slice(from,to)+';globalThis.api={assembleScene,validatePageLayout};',sandbox);
const {assembleScene:assemble,validatePageLayout:validate}=sandbox.api;
const shows=load('data/shows.json');
const catalog=load('data/shows/sunforge-outlaw-s1/series.json');
const base='data/shows/sunforge-outlaw-s1';
const store={};
for(const item of ['characters','dialogue','settings','regions','factions','direction'])store[item+'.json']=load(base+'/'+item+'.json');
let pages=0,panels=0,lettering=0;
const compositions=new Set();
for(let issue=1;issue<=12;issue++){
  const number=String(issue).padStart(2,'0'),id='sunforge-outlaw-s1-e'+number;
  const show=shows.find(s=>s.id===id);assert(show,'Missing '+id);
  const pagePath='pages_e'+number+'.json',layoutPath='editorial/page_layouts_e'+number+'.json';
  const storyIndex=show.sceneOverlays.findIndex(x=>x.file===pagePath);
  const layoutIndex=show.sceneOverlays.findIndex(x=>x.file===layoutPath);
  assert(layoutIndex>storyIndex,'Layout must load after story for '+id);
  const registered=show.sceneOverlays[layoutIndex];
  assert(registered.mergeById&&registered.strict,'Layout must merge by ID for '+id);
  const script=load(base+'/'+pagePath);
  const canonical=script.filter(p=>new RegExp('^SUN_S1E'+number+'_P\\d{2}$').test(p.id));
  const overlays=load(base+'/'+layoutPath);
  const ids=new Set(overlays.map(p=>p.id));
  assert.equal(overlays.length,canonical.length,'Incomplete profile count '+id);
  assert.equal(ids.size,canonical.length,'Duplicate overlay IDs '+id);
  assert(canonical.every(p=>ids.has(p.id)),'Missing overlay page '+id);
  assert(overlays.every(p=>Object.keys(p).sort().join(',')==='id,pageLayout'),'Overlay must not rewrite story '+id);
  store.__show=show;
  for(const [j,page] of canonical.entries()){
    const patch=overlays.find(p=>p.id===page.id),combined={...page,...patch};
    assert.equal(validate(combined),patch.pageLayout,'Invalid page layout '+page.id);
    const before=assemble(page,store,j),after=assemble(combined,store,j);
    const oldMarker=before.indexOf('\n[PANEL PLAN]'),layoutMarker=after.indexOf('\n[PAGE COMPOSITION]'),newMarker=after.indexOf('\n[PANEL PLAN]');
    assert(oldMarker>=0&&layoutMarker>=0&&newMarker>layoutMarker,'Assembly sections missing '+page.id);
    assert.equal(before.slice(0,oldMarker),after.slice(0,layoutMarker),'Modified ingredient prefix '+page.id);
    assert.equal(before.slice(oldMarker),after.slice(newMarker),'Modified story/dialogue after layout '+page.id);
    for(const line of page.dialogueInline||[])assert(after.includes(line.text),'Omitted exact lettering '+page.id);
    assert.equal(patch.pageLayout.panels.length,page.panelPlan.length,'Mismatched panel assignment '+page.id);
    pages++;panels+=page.panelPlan.length;lettering+=(page.dialogueInline||[]).length;
    compositions.add(patch.pageLayout.composition);
  }
  for(const unit of script.filter(p=>!new RegExp('^SUN_S1E'+number+'_P\\d{2}$').test(p.id)))
    assert(!ids.has(unit.id),'Editorial opener, teaser or closing incorrectly re-laid out '+unit.id);
}
assert.equal(pages,catalog.sourceBoundary.pages,'Series source boundary must reflect current writing');
console.log('PASS Sunforge '+pages+' story pages, '+panels+' original panels, '+lettering+' lettering items; '+compositions.size+' composition types; all story bytes preserved outside composition section');
