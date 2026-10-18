#!/usr/bin/env node
'use strict';
// Mechanical integrity of a targeted editorial density revision.
// Do not freeze jokes, exact lines, panel descriptions, or story decisions.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),zlib=require('node:zlib'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const load=p=>JSON.parse(read(p));
const show=load('data/shows.json').find(x=>x.id==='stardust-station-e02');
assert(show,'Missing Stardust Issue 2');
const base=show.basePath;
const encoded=show.sceneOverlays.filter(x=>x.encoding==='gzip-base64');
let scenes=encoded.flatMap(x=>JSON.parse(zlib.gunzipSync(Buffer.from(read(base+'/'+x.file).trim(),'base64')).toString('utf8')));
assert.equal(scenes.length,22,'Story issue must stay 22 pages');
assert.equal(new Set(scenes.map(x=>x.id)).size,22,'Duplicate source page');
const originals=new Map(scenes.map(p=>[p.id,p]));
function overlay(name){
  const meta=show.sceneOverlays.find(x=>x.file===name);
  assert(meta&&meta.mergeById&&meta.strict,'Expected strict page overlay '+name);
  const entries=load(base+'/'+name);
  assert.equal(new Set(entries.map(x=>x.id)).size,entries.length,'Duplicate overlay page');
  for(const patch of entries)assert(originals.has(patch.id),'Orphan overlay '+patch.id);
  return entries;
}
const storyName='editorial/pages_e02_p02_story_thread.json',densityName='editorial/pages_e02_density_pass.json',
  profileName='editorial/page_assembly_profiles_e02.json';
const order=show.sceneOverlays.map(x=>x.file);
assert(order.indexOf(storyName)<order.indexOf(densityName)&&order.indexOf(densityName)<order.indexOf(profileName),
  'Editorial density changes must follow story corrections and precede assembly profiles');
const story=overlay(storyName),density=overlay(densityName),profile=overlay(profileName);
assert.equal(density.length,4,'Unexpected density overlay coverage');
for(const patches of [story,density,profile]){
  const byId=new Map(patches.map(x=>[x.id,x]));
  scenes=scenes.map(scene=>({...scene,...(byId.get(scene.id)||{})}));
}
const dialogue=load(base+'/editorial/dialogue_cleanup_e02.json');
const byId=new Map(dialogue.map(x=>[x.id,x]));
assert.equal(byId.size,dialogue.length,'Duplicate dialogue patch');
scenes=scenes.map(x=>{
  const d=byId.get(x.id);
  return d?{...x,dialogueInline:d.dialogueInline||d.sceneDialogue}:x;
});
const html=read('index.html'),begin=html.indexOf('const SHOW_MANIFEST='),end=html.indexOf('function safeFilePart(',begin);
assert(begin>=0&&end>begin,'Cannot find canonical assembler');
const context=vm.createContext({});
vm.runInContext(html.slice(begin,end)+';globalThis.assembleForCheck=assembleScene;',context);
const store={__show:show};
for(const shelf of ['characters','settings','regions','factions','direction','dialogue'])store[shelf+'.json']=load(base+'/'+shelf+'.json');
let dialogueCount=0,wordCount=0;
for(const [i,page] of scenes.entries()){
  const orig=originals.get(page.id);
  assert(orig,'Unexpected production page '+page.id);
  assert.equal(page.panelPlan.length,orig.panelPlan.length,'Panel count changed '+page.id);
  assert.equal(page.panelCount,page.panelPlan.length,'Stored panelCount drift '+page.id);
  assert.equal(page.id,'SDS_S1E02_P'+String(i+1).padStart(2,'0'),'Page ID/order drift');
  const handles=new Set((page.charactersInline||[]).map(x=>x.handle));
  for(const d of page.dialogueInline||[]){
    const match=String(d.subtext||'').trim().match(/^Panel\s+(\d+)$/i);
    assert(match,'Unassigned dialogue panel '+page.id);
    const n=Number(match[1]);
    assert(n>=1&&n<=page.panelPlan.length,'Dialogue references nonexistent panel '+page.id);
    assert(typeof d.text==='string'&&d.text.trim(),'Blank dialogue '+page.id);
    if(d.handle?.startsWith('@'))assert(handles.has(d.handle),'Speaking character omitted from the cast '+page.id+': '+d.handle);
    dialogueCount++;
    wordCount+=d.text.trim().split(/\s+/).length;
  }
  const assembled=context.assembleForCheck(page,store,i);
  assert(assembled.includes('[PANEL PLAN]')&&assembled.includes('[DIALOGUE]'),'Missing compiled story sections '+page.id);
  for(const panel of page.panelPlan)assert(assembled.includes(panel.text),'Missing authored panel '+page.id);
  for(const line of page.dialogueInline||[])assert(assembled.includes(line.text),'Missing authored dialogue '+page.id);
  if(page.continuityFrom)assert(assembled.includes('[CONTINUITY]'),'Lost continuity '+page.id);
  assert.equal(page.promptCharacterMode,'cast','Lost page scoping '+page.id);
}
console.log('PASS: Stardust Issue 2',scenes.length,'story pages,',dialogueCount,'dialogue entries,',wordCount,'spoken words; page IDs, cast attribution, panel order, dialogue placement and assembler fidelity intact.');
