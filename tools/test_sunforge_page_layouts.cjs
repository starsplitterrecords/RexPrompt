#!/usr/bin/env node
'use strict';
// Issue 1 canonical source-layout audit; archived overlay is a comparison fixture only.
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8'),json=p=>JSON.parse(read(p));
const source=read('index.html'),start=source.indexOf('const SHOW_MANIFEST='),end=source.indexOf('function safeFilePart(',start);
assert(start>=0&&end>start,'Could not locate live RexPrompt assembler');
const sandbox=vm.createContext({});
vm.runInContext(source.slice(start,end)+';globalThis.r={assembleScene,validatePageLayout};',sandbox);
const {assembleScene:assemble,validatePageLayout:validate}=sandbox.r;
const show=json('data/shows.json').find(x=>x.id==='sunforge-outlaw-s1-e01');
assert(show,'Sunforge Issue 1 show registration missing');
assert(!(show.sceneOverlays||[]).some(x=>x.mergeById),'Sunforge Issue 1 must have no active field overlays');
const base=show.basePath,script=json(base+'/pages_e01.json'),archive=json(base+'/editorial/page_layouts_e01.json');
const story=script.filter(x=>/^SUN_S1E01_P\d{2}$/.test(x.id)),layouts=new Map(archive.map(x=>[x.id,x]));
assert.equal(story.length,22,'Unexpected Sunforge Issue 1 story count');
assert.equal(script.length,24,'Editorial opening and closing must remain');
assert.equal(layouts.size,22,'Archived layout inventory changed');
const data={__show:show};
for(const f of ['characters','dialogue','settings','regions','factions','direction'])data[f+'.json']=json(base+'/'+f+'.json');
let panels=0,lettering=0;const styles=new Set();
for(const [i,page] of story.entries()){
 const profile=layouts.get(page.id);
 assert(profile,'Missing archived layout '+page.id);
 assert.deepEqual(page.pageLayout,profile.pageLayout,'Page layout not embedded in authoritative source '+page.id);
 assert.equal(validate(page),page.pageLayout,'Invalid page layout '+page.id);
 const noLayout={...page};delete noLayout.pageLayout;
 const before=assemble(noLayout,data,i),after=assemble(page,data,i);
 assert(!before.includes('[PAGE COMPOSITION]'),'Uncomposed page should omit composition');
 assert.equal((after.match(/\[PAGE COMPOSITION\]/g)||[]).length,1,'Composition emitted more than once');
 assert(after.indexOf('[PAGE COMPOSITION]')<after.indexOf('[PANEL PLAN]'),'Composition must precede panel plan');
 assert.equal(before.slice(0,before.indexOf('\n[PANEL PLAN]')),
   after.slice(0,after.indexOf('\n[PAGE COMPOSITION]')),'Ingredients changed '+page.id);
 assert.equal(before.slice(before.indexOf('\n[PANEL PLAN]')),
   after.slice(after.indexOf('\n[PANEL PLAN]')),'Script changed '+page.id);
 for(const d of page.dialogueInline||[]){assert(after.includes(d.text),'Dialogue lost '+page.id);lettering++;}
 assert.equal(page.pageLayout.panels.length,page.panelPlan.length,'Panel count changed');
 panels+=page.panelPlan.length;styles.add(page.pageLayout.composition);
}
for(const x of script.filter(p=>!/^SUN_S1E01_P\d{2}$/.test(p.id)))
 assert(!x.pageLayout,'Editorial item incorrectly acquired story layout '+x.id);
console.log('PASS canonical Sunforge Issue 1: '+story.length+' layouts, '+panels+' panels, '+lettering+' lines; '+styles.size+' composition types.');
