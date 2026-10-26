#!/usr/bin/env node
'use strict';
// Mechanical regression gate for editorial pageLayout on Rex Fleet and Vikings Issue 2.
// Checks production assembler and authored page data without freezing creative dialogue.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.join(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8'),load=p=>JSON.parse(read(p));
const html=read('index.html'),start=html.indexOf('const SHOW_MANIFEST='),end=html.indexOf('function safeFilePart(',start);
assert(start>=0&&end>start,'Missing canonical RexPrompt assembly source');
const context=vm.createContext({});
vm.runInContext(html.slice(start,end)+';globalThis.pageTest={assembleScene,validatePageLayout,pageLayoutWarnings};',context);
const {assembleScene:assemble,validatePageLayout:validate,pageLayoutWarnings}=context.pageTest;
const shows=load('data/shows.json');
const targets=[
{show:'rex-fleet-i02',file:'data/shows/rex-fleet-s1/pages_i02.json',overlay:'data/shows/rex-fleet-s1/page_layout_i02.json'},
{show:'vikings-2026-s1-e02',file:'data/shows/vikings-2026-s1/pages_i02.json'}
];
function store(show){const value={__show:show};for(const name of ['characters','settings','factions','regions','direction','dialogue'])value[name+'.json']=load(show.basePath+'/'+name+'.json');return value}
for(const target of targets){
const show=shows.find(x=>x.id===target.show);assert(show,'Missing show '+target.show);
const rawPages=load(target.file),s=store(show),names=new Set();
let pages=rawPages;
if(target.overlay){
  // The current strict merge overlay is the sole authority for curated compositions.
  const descriptor=(show.sceneOverlays||[]).find(o=>show.basePath+'/'+o.file===target.overlay);
  assert(descriptor?.mergeById&&descriptor?.strict,'Layout must remain an ID-strict overlay');
  const overlays=load(target.overlay),byId=new Map(overlays.map(o=>[o.id,o]));
  assert.equal(overlays.length,rawPages.length,'Missing Rex Issue 2 layout');
  assert.equal(byId.size,overlays.length,'Duplicate Rex Issue 2 layout ID');
  assert(rawPages.every(p=>!Object.hasOwn(p,'pageLayout')),'Redundant layout embedded in story page');
  for(const item of overlays){
    assert.deepEqual(Object.keys(item).sort(),['id','pageLayout'],'Overlay must not modify story content '+item.id);
  }
  pages=rawPages.map(p=>{
    const profile=byId.get(p.id);
    assert(profile,'Orphaned or missing Rex Issue 2 layout '+p.id);
    return {...p,pageLayout:profile.pageLayout};
  });
}
assert(pages.length>0,'Empty issue '+target.show);
for(const [i,page] of pages.entries()){
  assert(page.id&&!names.has(page.id),'Missing/duplicate page identity '+page.id);names.add(page.id);
  if(!page.pageLayout){
    assert(target.show==='vikings-2026-s1-e02'&&['VIK_S1E02_P02','VIK_S1E02_P03','VIK_S1E02_P04'].includes(page.id),
      'Missing authored layout on an unapproved page '+page.id);
    continue;
  }
  const layout=validate(page);assert(layout,'Rejected composition on '+page.id);
  const original={...page};delete original.pageLayout;
  const before=assemble(original,s,i),after=assemble(page,s,i);
  const panelStart='\n[PANEL PLAN]',layoutStart='\n[PAGE COMPOSITION]';
  assert(before.includes(panelStart),'Missing scripted panel plan '+page.id);
  assert(after.includes(layoutStart),'Missing emitted layout '+page.id);
  assert(after.indexOf(layoutStart)<after.indexOf(panelStart),'Layout emitted too late '+page.id);
  assert.equal((after.match(/\[PAGE COMPOSITION\]/g)||[]).length,1,'Duplicate layout '+page.id);
  assert.equal(after.slice(0,after.indexOf(layoutStart)),before.slice(0,before.indexOf(panelStart)),
    'Earlier recipe ingredient changed '+page.id);
  assert.equal(after.slice(after.indexOf(panelStart)),before.slice(before.indexOf(panelStart)),
    'Script, dialogue, continuity, or later ingredient changed '+page.id);
  for(const d of page.dialogueInline||[])assert(after.includes(d.text),'Missing exact scripted dialogue '+page.id);
  for(const panel of page.panelPlan||[]){
    const v=typeof panel==='string'?panel:panel.action||panel.text||panel.name||panel.summary||JSON.stringify(panel);
    assert(after.includes(v),'Missing scripted panel beat '+page.id);
  }
  if(page.continuityFrom)assert(after.includes('[CONTINUITY]'),'Missing continuation '+page.id);
  assert(!after.includes('Editorial density advisories'), 'Warning should not leak into chef '+page.id);
  // Warnings may exist, but their output is advisory and may not modify the recipe.
  assert(Array.isArray(pageLayoutWarnings(page)),'Density analysis must return a list');
}
console.log('PASS '+target.show+': '+pages.length+' authored layouts, panel and dialogue order preserved in actual chef assembly');
}
