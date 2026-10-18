#!/usr/bin/env node
'use strict';
// Issue-wide Phase B regression: apply current authored story, dialogue,
// prompt scoping and layout overlays, then ensure the chef script is unchanged.
const fs=require('node:fs');
const vm=require('node:vm');
const zlib=require('node:zlib');
const path=require('node:path');
const assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const load=p=>JSON.parse(read(p));
const shows=load('data/shows.json');
const show=shows.find(x=>x.id==='stardust-station-e02');
assert(show,'Stardust Issue 2 is not registered');
const base=show.basePath;
const pathFor=name=>base+'/'+name;
const html=read('index.html');
const from=html.indexOf('const SHOW_MANIFEST='),to=html.indexOf('function safeFilePart(',from);
assert(from>=0&&to>from,'Assembler not found');
const ctx=vm.createContext({});
vm.runInContext(html.slice(from,to)+';globalThis.testExports={assembleScene,validatePageLayout};',ctx);
const {assembleScene:assemble,validatePageLayout:validate}=ctx.testExports;
const data={__show:show};
for(const shelf of ['characters','dialogue','settings','regions','factions','direction'])
  data[shelf+'.json']=load(pathFor(shelf+'.json'));
const overlays=show.sceneOverlays||[];
const layoutName='editorial/page_layouts_e02.json';
const profilesName='editorial/page_assembly_profiles_e02.json';
const storyName='editorial/pages_e02_p02_story_thread.json';
const layoutIdx=overlays.findIndex(x=>x.file===layoutName);
const profilesIdx=overlays.findIndex(x=>x.file===profilesName);
const storyIdx=overlays.findIndex(x=>x.file===storyName);
assert(layoutIdx>profilesIdx&&profilesIdx>storyIdx,
  'Layouts must be applied after approved story corrections and existing assembly scopes');
assert(overlays[layoutIdx].strict&&overlays[layoutIdx].mergeById,
  'Layout overlay must strictly match canonical page IDs');
let pages=overlays.filter(x=>x.encoding==='gzip-base64').flatMap(x=>
  JSON.parse(zlib.gunzipSync(Buffer.from(read(pathFor(x.file)).trim(),'base64')).toString('utf8')));
assert.equal(pages.length,22,'Scripted page count changed');
for(const name of [storyName,profilesName]){
  const patches=load(pathFor(name));
  const ids=new Map(patches.map(x=>[x.id,x]));
  assert.equal(ids.size,patches.length,'Duplicate overlay ID: '+name);
  for(const id of ids.keys())assert(pages.some(x=>x.id===id),'Orphan overlay entry '+id);
  pages=pages.map(x=>({...x,...(ids.get(x.id)||{})}));
}
const dialogue=new Map(load(pathFor('editorial/dialogue_cleanup_e02.json')).map(x=>[x.id,x]));
const finalBeforeLayout=pages.map(x=>{
  const d=dialogue.get(x.id);
  return {...x,...(d?{dialogueInline:d.dialogueInline||d.sceneDialogue}: {})};
});
const layouts=load(pathFor(layoutName));
assert.equal(layouts.length,22,'Every interior page requires a layout');
assert.equal(new Set(layouts.map(x=>x.id)).size,22,'Duplicate layout IDs');
const byId=new Map(layouts.map(x=>[x.id,x]));
assert(finalBeforeLayout.every(x=>byId.has(x.id)),'Unplanned story page');
assert([...byId.keys()].every(id=>finalBeforeLayout.some(p=>p.id===id)),'Orphan planned layout');
const architectures=new Set();
let extraCharacters=0,insets=0;
for(let i=0;i<finalBeforeLayout.length;i++){
  const basePage=finalBeforeLayout[i],patch=byId.get(basePage.id);
  assert.deepEqual(Object.keys(patch).sort(),['id','pageLayout'],'Overlay must contain layout only');
  const page={...basePage,...patch};
  validate(page);
  architectures.add(page.pageLayout.composition);
  insets+=page.pageLayout.panels.filter(p=>p.role==='inset').length;
  assert.equal(page.pageLayout.panels.length,basePage.panelPlan.length,
    'Layout must not drop or invent panels: '+basePage.id);
  const before=assemble(basePage,data,i),after=assemble(page,data,i);
  assert(!before.includes('[PAGE COMPOSITION]'),'Unplanned baseline should not include layout');
  assert(after.includes('[PAGE COMPOSITION]'),'Layout not emitted to chef for '+page.id);
  assert(after.indexOf('[PAGE COMPOSITION]')<after.indexOf('[PANEL PLAN]'),
    'Visual hierarchy must precede scripted panel plan on '+page.id);
  const tail=text=>text.slice(text.indexOf('\n[PANEL PLAN]'));
  assert.equal(tail(after),tail(before),'Panel plan/dialogue/continuity changed: '+page.id);
  const pre=text=>text.slice(0,text.indexOf('\n[PANEL PLAN]'));
  assert(pre(after).startsWith(pre(before)),
    'Changed content before the layout block: '+page.id);
  for(const line of basePage.dialogueInline||[])
    assert(after.includes(line.text),'Dropped literal dialogue '+basePage.id);
  extraCharacters+=after.length-before.length;
}
assert(architectures.size>=5,'Issue must have distinct compositions for dramatic reasons');
assert(insets>=2,'Inset production path was not exercised');
const p02=finalBeforeLayout.find(p=>p.id==='SDS_S1E02_P02');
assert.equal(p02.panelPlan.length,6);
assert.equal(p02.dialogueInline.length,10,'The dense bodega-equivalent Stardust scene was rewritten');
const p22=finalBeforeLayout.find(p=>p.id==='SDS_S1E02_P22');
assert.equal(p22.panelPlan.length,5);
console.log('PASS: 22 Stardust Issue 2 layouts; '+architectures.size+
  ' artistic architectures; '+insets+' insets; all panel plans, dialogue, and continuity intact; '+
  extraCharacters+' characters of purposeful composition direction emitted to chef');
