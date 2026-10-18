#!/usr/bin/env node
'use strict';
// Issue-wide Sunforge layout audit. The unmodified script stays authoritative.
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const assert=require('node:assert/strict');
const root=path.join(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8'),json=p=>JSON.parse(read(p));
const source=read('index.html'),start=source.indexOf('const SHOW_MANIFEST='),end=source.indexOf('function safeFilePart(',start);
assert(start>=0&&end>start,'Could not locate live RexPrompt assembler');
const sandbox=vm.createContext({});
vm.runInContext(source.slice(start,end)+';globalThis.r={assembleScene,validatePageLayout};',sandbox);
const {assembleScene:assemble,validatePageLayout:validate}=sandbox.r;
const show=json('data/shows.json').find(x=>x.id==='sunforge-outlaw-s1-e01');
assert(show,'Sunforge Issue 1 show registration missing');
const overlayFile='editorial/page_layouts_e01.json',overlays=show.sceneOverlays||[];
const storyIndex=overlays.findIndex(x=>x.file==='pages_e01.json'),layoutIndex=overlays.findIndex(x=>x.file===overlayFile);
assert(layoutIndex>storyIndex,'Layout overlay must follow canonical story data');
assert.equal(overlays[layoutIndex].mergeById,true,'Layout requires mergeById');
assert.equal(overlays[layoutIndex].strict,true,'Layout requires strict overlay intent');
const base=show.basePath,script=json(base+'/pages_e01.json'),layoutRecords=json(base+'/'+overlayFile);
const storyPages=script.filter(x=>/^SUN_S1E01_P\d{2}$/.test(x.id));
assert.equal(storyPages.length,22,'Unexpected Sunforge Issue 1 script size');
assert.equal(script.length,24,'Editorial opening and closing should be preserved');
assert.equal(layoutRecords.length,storyPages.length,'Every story page needs a layout');
const profiles=new Map(layoutRecords.map(x=>[x.id,x]));
assert.equal(profiles.size,storyPages.length,'Duplicate layout IDs');
for(const x of layoutRecords){
 assert.deepEqual(Object.keys(x).sort(),['id','pageLayout'],'Layout overlay must not rewrite script fields');
 assert(storyPages.some(p=>p.id===x.id),'Unknown story page '+x.id);
}
assert(script.every(x=>!x.pageLayout),'Page layouts must live in editorial overlay, not old story source');
const data={__show:show};
for(const file of ['characters','dialogue','settings','regions','factions','direction'])
  data[file+'.json']=json(base+'/'+file+'.json');
const used=new Set();let dialogueCount=0,panelsCount=0;
for(let i=0;i<storyPages.length;i++){
 const page=storyPages[i],profile=profiles.get(page.id);
 assert(profile,'Unprofiled story page '+page.id);
 const compiled={...page,...profile};
 assert.equal(validate(compiled),profile.pageLayout,'Page layout not preserved');
 const before=assemble(page,data,i),after=assemble(compiled,data,i);
 assert(!before.includes('[PAGE COMPOSITION]'),'Unprofiled page must be backward-compatible');
 assert.equal((after.match(/\[PAGE COMPOSITION\]/g)||[]).length,1,'Composition block must appear exactly once');
 assert(after.indexOf('[PAGE COMPOSITION]')<after.indexOf('[PANEL PLAN]'),'Composition must precede panel plan');
 assert.equal(before.slice(0,before.indexOf('\n[PANEL PLAN]')),
              after.slice(0,after.indexOf('\n[PAGE COMPOSITION]')),'Original recipe prefix changed: '+page.id);
 assert.equal(before.slice(before.indexOf('\n[PANEL PLAN]')),
              after.slice(after.indexOf('\n[PANEL PLAN]')),'Authoritative story content changed: '+page.id);
 for(const line of page.dialogueInline||[]){
  assert(after.includes(line.text),'Missing scripted dialogue on '+page.id);
  dialogueCount++;
 }
 assert.equal(profile.pageLayout.panels.length,page.panelPlan.length,'Panel count changed');
 panelsCount+=page.panelPlan.length;
 used.add(profile.pageLayout.composition);
}
for(const p of script.filter(x=>!/^SUN_S1E01_P\d{2}$/.test(x.id))){
 assert(!profiles.has(p.id),'Editorial cover/teaser instruction should not be decomposed into panels');
}
// Composition choices remain editorially changeable. Record diversity for review,
// but only fail on broken story/structure, not on a subjective layout pattern.
assert.equal(profiles.size,22,'Layout inventory changed unexpectedly');
console.log('PASS Sunforge Issue 1: '+storyPages.length+' layouts, '+panelsCount+' panels and '+dialogueCount+' dialogue items preserved; '+used.size+' composition architectures; no new pages');
