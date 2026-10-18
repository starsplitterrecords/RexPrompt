#!/usr/bin/env node
'use strict';
// Validate issue-scoped chef decluttering without losing artistic or story data.
// Reuses the live RexPrompt assembler rather than a parallel rendering algorithm.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const root=path.resolve(__dirname,'..');
const load=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const src=fs.readFileSync(path.join(root,'index.html'),'utf8');
const from=src.indexOf('const SHOW_MANIFEST='),to=src.indexOf('function safeFilePart(',from);
assert(from>=0&&to>from,'Canonical assembler unavailable');
const vmCtx=vm.createContext({});
vm.runInContext(src.slice(from,to)+';globalThis.__test={assembleScene,mergeById};',vmCtx);
const {assembleScene,mergeById}=vmCtx.__test;
const manifest=load('data/shows.json'),base='data/shows/stardust-station';
const store={__show:null};
for(const n of ['characters','settings','regions','factions','direction','dialogue'])store[n+'.json']=load(base+'/'+n+'.json');
let count=0,cast=0,summary=0,places=0,added=0;
for(let issue=4;issue<=10;issue++){
  const suffix=String(issue).padStart(2,'0');
  const show=manifest.find(x=>x.id==='stardust-station-e'+suffix);
  assert(show,'Missing issue '+suffix);
  const file='editorial/page_assembly_profiles_e'+suffix+'.json';
  const active=show.sceneOverlays.filter(x=>x.file===file);
  assert.equal(active.length,1,'Missing/duplicate registered profile '+suffix);
  assert.equal(active[0].mergeById,true,'Profiles must merge by ID '+suffix);
  assert.equal(active[0].strict,true,'Profiles must be strict '+suffix);
  const pages=load(base+'/pages_e'+suffix+'.json'),profiles=load(base+'/'+file);
  assert.equal(new Set(pages.map(x=>x.id)).size,pages.length,'Duplicate source page '+suffix);
  assert.equal(new Set(profiles.map(x=>x.id)).size,profiles.length,'Duplicate scoping profile '+suffix);
  const pageIds=new Set(pages.map(x=>x.id));
  for(const patch of profiles){
    assert(pageIds.has(patch.id),'Unknown scope target '+patch.id);
    assert(Object.keys(patch).every(x=>['id','promptSuppress','promptCharacterMode','promptSettingMode'].includes(x)),
      'Prompt profile attempted story mutation '+patch.id);
    if(patch.promptSuppress)assert.deepEqual(Array.from(patch.promptSuppress),['summary'],'Only formulaic summaries may be suppressed '+patch.id);
    if(patch.promptCharacterMode)assert.equal(patch.promptCharacterMode,'cast');
    if(patch.promptSettingMode)assert.equal(patch.promptSettingMode,'label');
  }
  const profiled=mergeById(pages,profiles);
  assert.equal(profiled.length,pages.length,'Unexpected additional page '+suffix);
  store.__show=show;
  for(let i=0;i<pages.length;i++){
    const original=pages[i],page=profiled[i],id=original.id;
    assert.equal(page.id,id);
    assert(original.summary.startsWith('Primary composition: '),'Unique summary cannot be suppressed '+id);
    assert(page.promptSuppress?.includes('summary'),'Formulaic summary leaked into recipe '+id);
    const before=assembleScene(original,store,i),after=assembleScene(page,store,i);
    assert(!after.includes(original.summary),'Formulaic page summary still assembled '+id);
    const panelBefore=before.indexOf('\n[PANEL PLAN]'),panelAfter=after.indexOf('\n[PANEL PLAN]');
    assert(panelBefore>=0&&panelAfter>=0,'Missing scripted panels '+id);
    assert.equal(after.slice(panelAfter),before.slice(panelBefore),'Panel/dialogue/continuity modified '+id);
    for(const line of original.dialogueInline||[])assert(after.includes(line.text),'Lost exact dialogue '+id);
    if(page.promptCharacterMode==='cast'){
      assert(after.includes('[CAST]'),'Compact cast not emitted '+id);
      assert(!after.includes('[CHARACTERS]'),'Full recurring character prose leaked '+id);
      cast++;
    }else{
      // First actual introduction and explicit legacy page profile stay full.
      if(original.characters?.length)assert(after.includes('[CHARACTERS]'),'Missing approved full character introduction '+id);
    }
    if(page.promptSettingMode==='label'){
      assert(i>0&&pages[i-1].setting===page.setting,'Compact location not adjacent/re-established '+id);
      const setting=store['settings.json'][page.setting];
      assert(setting&&after.includes(setting.name),'Missing setting name '+id);
      assert(!after.includes(setting.text),'Repeated full location prose leaked '+id);
      places++;
    }
    added+=before.length-after.length;summary++;count++;
  }
}
assert.equal(count,153,'Unexpected Stardust Issue 4-10 interior count');
assert(summary>=149,'Expected all formulaic summaries suppressed');
assert(cast>=125,'Too few confirmed recurring cast references compacted');
assert(places>=70,'Expected adjacent repeated locations to become labels');
assert(added>10000,'No meaningful recipe reduction');
console.log('PASS Stardust Issues 4–10 '+count+' pages, '+summary+' formulaic summaries suppressed, '+cast+' compact casts, '+places+' compact recurring locations; '+added+' characters removed from assembled recipes');
