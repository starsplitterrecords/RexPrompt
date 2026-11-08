#!/usr/bin/env node
'use strict';
// Issue 1 canonical Sunforge composition regression.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8'),json=p=>JSON.parse(read(p));
const html=read('index.html'),start=html.indexOf('const SHOW_MANIFEST='),end=html.indexOf('function safeFilePart(',start);
assert(start>=0&&end>start,'Live assembler missing');
const context=vm.createContext({});
vm.runInContext(html.slice(start,end)+';globalThis.api={assembleScene,validatePageLayout};',context);
const {assembleScene,validatePageLayout}=context.api;
const show=json('data/shows.json').find(x=>x.id==='sunforge-outlaw-s1-e01');
assert(show,'Sunforge issue missing');
assert(!(show.sceneOverlays||[]).some(x=>x.mergeById),'No field overlays permitted');
const source=json(show.basePath+'/pages_e01.json');
const story=source.filter(x=>/^SUN_S1E01_P\d{2}$/.test(x.id));
assert.equal(story.length,22,'Unexpected issue story size');
assert.equal(source.length,24,'Editorial bookends changed');
const store={__show:show};
for(const item of ['characters','dialogue','settings','regions','factions','direction'])store[item+'.json']=json(show.basePath+'/'+item+'.json');
let panels=0,lettering=0;const compositions=new Set();
for(const [i,page] of story.entries()){
 assert(page.pageLayout,'Canonical layout missing '+page.id);
 assert.equal(validatePageLayout(page),page.pageLayout);
 const bare={...page};delete bare.pageLayout;
 const before=assembleScene(bare,store,i),after=assembleScene(page,store,i);
 assert(!before.includes('[PAGE COMPOSITION]'));
 assert.equal((after.match(/\[PAGE COMPOSITION\]/g)||[]).length,1,'Duplicate layout '+page.id);
 const old=before.indexOf('\n[PANEL PLAN]'),layout=after.indexOf('\n[PAGE COMPOSITION]'),now=after.indexOf('\n[PANEL PLAN]');
 assert(old>=0&&layout>=0&&now>layout);
 assert.equal(before.slice(0,old),after.slice(0,layout),'Pre-panel ingredients changed '+page.id);
 assert.equal(before.slice(old),after.slice(now),'Script altered '+page.id);
 for(const d of page.dialogueInline||[]){assert(after.includes(d.text),'Lost exact dialogue '+page.id);lettering++;}
 assert.equal(page.pageLayout.panels.length,page.panelPlan.length);
 panels+=page.panelPlan.length;compositions.add(page.pageLayout.composition);
}
for(const item of source.filter(x=>!/^SUN_S1E01_P\d{2}$/.test(x.id)))
 assert(!item.pageLayout,'Editorial bookend cannot receive story panel layout '+item.id);
console.log('PASS Sunforge Issue 1 canonical layouts: 22 pages, '+panels+' panels, '+lettering+' dialogue lines, '+compositions.size+' compositions.');
