#!/usr/bin/env node
'use strict';
// Echoes editorial layout contract: exact story preservation across all 149
// page recipes, including editorial bookends and eight issue-scoped overlays.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const root=path.resolve(__dirname,'..');
const json=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const showList=json('data/shows.json');
const base='data/shows/echoes-forgotten-war-s1';
const show=showList.find(s=>s.id==='echoes-forgotten-war-s1');
assert(show,'Echoes show missing');
const assembly=fs.readFileSync(path.join(root,'index.html'),'utf8');
const begin=assembly.indexOf('const SHOW_MANIFEST='),end=assembly.indexOf('function safeFilePart(',begin);
assert(begin>=0&&end>begin,'RexPrompt assembler unavailable');
const context=vm.createContext({});
vm.runInContext(assembly.slice(begin,end)+';globalThis.editorTest={assembleScene,validatePageLayout,expandIssues,mergeById,pageLayoutWarnings}',context);
const {assembleScene,validatePageLayout,expandIssues,mergeById,pageLayoutWarnings}=context.editorTest;
const issueShows=expandIssues(show);
assert.equal(issueShows.length,8,'Echoes must expand into eight issues');
const config=json(base+'/assembler.json');
const store={__show:{...config,...show}};
for(const shelf of ['characters','settings','regions','factions','direction','dialogue'])store[shelf+'.json']=json(base+'/'+shelf+'.json');
const expectedCounts=[23,18,17,18,18,17,18,20];
const allIds=new Set(),architectures={},stageWarnings=[];
let counted=0,letterCount=0;
for(let issue=1;issue<=8;issue++){
 const suffix=String(issue).padStart(2,'0');
 const issueShow=issueShows[issue-1];
 assert.equal(issueShow.scenesFiles.length,1,'Unexpected issue file count '+suffix);
 assert.equal(issueShow.scenesFiles[0],'scenes_e'+suffix+'.json');
 assert.equal(issueShow.sceneOverlays.length,2,'Expected exactly layout and scoping overlays '+suffix);
 assert.equal(issueShow.sceneOverlays[0].file,'editorial/page_layouts_e'+suffix+'.json');
 assert.equal(issueShow.sceneOverlays[0].mergeById,true);
 assert.equal(issueShow.sceneOverlays[0].strict,true);
 assert.equal(issueShow.sceneOverlays[1].file,'editorial/page_recipe_scope_e'+suffix+'.json');
 assert.equal(issueShow.sceneOverlays[1].mergeById,true);
 assert.equal(issueShow.sceneOverlays[1].strict,true);
 const source=json(base+'/scenes_e'+suffix+'.json'),patches=json(base+'/editorial/page_layouts_e'+suffix+'.json');
 assert.equal(source.length,expectedCounts[issue-1],'Source issue count drift '+suffix);
 assert.equal(patches.length,source.length,'Layout inventory mismatch '+suffix);
 assert.equal(new Set(patches.map(x=>x.id)).size,source.length,'Duplicate layout ID '+suffix);
 assert.deepEqual(patches.map(x=>x.id),source.map(x=>x.id),'Layout overlay order mismatch '+suffix);
 for(const patch of patches)assert.deepEqual(Object.keys(patch).sort(),['id','pageLayout'],'Unexpected script mutation in layout overlay '+patch.id);
 const scopes=json(base+'/editorial/page_recipe_scope_e'+suffix+'.json');
 assert.equal(new Set(scopes.map(x=>x.id)).size,scopes.length,'Duplicate recipe-scope ID '+suffix);
 const sourceIds=new Set(source.map(x=>x.id));
 for(const p of scopes){
   assert(sourceIds.has(p.id),'Out-of-issue scope '+p.id);
   assert.deepEqual(Object.keys(p).sort(),['id','promptCharacterMode'],'Scope overlay modified story data '+p.id);
   assert.equal(p.promptCharacterMode,'cast','Unsupported Echoes character scope '+p.id);
 }
 const effective=mergeById(mergeById(source,patches),scopes);
 assert.equal(effective.length,source.length,'Overlay appended new story units '+suffix);
 for(let i=0;i<source.length;i++){
  const original=source[i],page=effective[i],layout=page.pageLayout;
  assert.equal(original.id,page.id);
  assert(!original.pageLayout,'Layout data belongs in the authoritative overlay, not duplicate story fields '+page.id);
  assert.equal(validatePageLayout(page),layout,'Invalid layout for '+page.id);
  assert.equal(layout.panels.length,original.panelPlan.length,'Panel count mismatch '+page.id);
  const originalOutput=assembleScene(original,store,i),layoutOutput=assembleScene(page,store,i);
  assert(!originalOutput.includes('[PAGE COMPOSITION]'),'Unprofiled page gained composition '+page.id);
  assert(layoutOutput.includes('[PAGE COMPOSITION]'),'Missing compiled composition '+page.id);
  const added=layoutOutput.indexOf('\n[PAGE COMPOSITION]');
  const retained=layoutOutput.indexOf('\n[PANEL PLAN]',added);
  const oldPanel=originalOutput.indexOf('\n[PANEL PLAN]');
  assert(added>=0&&retained>added&&oldPanel>=0,'Assembler layout order failed '+page.id);
  const storyWithLayout=assembleScene({...original,pageLayout:layout},store,i);
  // Echoes now uses one visible-character handle per authored figure, not a
  // duplicated compact/full cast roster. Off-panel dialogue keeps speaker names.
  assert(!layoutOutput.includes('[CAST]')&&!layoutOutput.includes('[CHARACTERS]'),
    'Duplicate character block on '+page.id);
  assert(!storyWithLayout.includes('[CAST]')&&!storyWithLayout.includes('[CHARACTERS]'),
    'Unscoped character block on '+page.id);
  const visibleTags=layoutOutput.split('\n').filter(x=>/^@ech\.[A-Za-z0-9_-]+$/.test(x));
  const expectedTags=(page.characters||[]).map(id=>store['characters.json'][id]?.handle);
  assert.deepEqual(visibleTags,expectedTags,'Incorrect Echoes page visual cast '+page.id);
  assert.equal(layoutOutput.slice(retained),originalOutput.slice(oldPanel),'Script/dialogue/continuity changed '+page.id);
  for(const line of original.dialogueInline||[])assert(layoutOutput.includes(line.text),'Missing scripted lettering '+page.id);
  if(page.id.includes('_EDITOR_')){
   assert.equal(layout.composition,'splash','Editorial page not full splash '+page.id);
   assert.equal(original.panelPlan.length,1,'Editorial panel count unexpectedly changed '+page.id);
  }else{
   const dir=original.directionInline||[];
   assert(dir.every(x=>!x.text?.startsWith('PAGE VISUAL CONTEXT — Ancient-history page: broader compositions')),'Repeated generic directing not sanitized '+page.id);
   assert(dir.every(x=>!x.text?.includes('PAGE ARCHITECTURE —')),'Contradictory old layout code '+page.id);
  }
  if(page.id==='EFW_S1E03_S05'){
   assert.equal(layout.composition,'splash-with-insets');
   assert.equal(layout.panels[1].insetOf,1);
   assert.equal(layout.panels[1].scale,'medium','Dialogue inset would be too small');
  }
  const warnings=pageLayoutWarnings(page);
  if(warnings.length)stageWarnings.push(page.id+': '+warnings.join('; '));
  letterCount+=(page.dialogueInline||[]).length;
  architectures[layout.composition]=(architectures[layout.composition]||0)+1;
  assert(!allIds.has(page.id),'Duplicate across issues '+page.id);
  allIds.add(page.id);counted++;
 }
}
assert.equal(counted,149,'Unexpected season page count');
assert.equal(allIds.size,149,'Duplicate page identities');
assert(Object.keys(architectures).length>=7,'Insufficient range of art architectures');
assert.equal(architectures.splash,16,'Editorial splash count drift');
assert(architectures['splash-with-insets']>=2,'Missing supported substantial inset designs');
console.log('PASS Echoes layouts: '+counted+' production pages across eight issues / '+letterCount+' lettering items retained');
console.log('Composition distribution: '+JSON.stringify(architectures));
console.log('Density warnings (advisory; no scripted changes): '+stageWarnings.length+' affected pages');
