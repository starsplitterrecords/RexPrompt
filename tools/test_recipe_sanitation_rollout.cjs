#!/usr/bin/env node
'use strict';
// Current Stardust page-scoping delivery, using the production assembler.
// The source already includes the accepted issue-specific display policies.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8'),load=p=>JSON.parse(read(p));
const html=read('index.html'),start=html.indexOf('const SHOW_MANIFEST='),end=html.indexOf('function safeFilePart(',start);
assert(start>=0&&end>start,'Canonical assembler unavailable');
const ctx=vm.createContext({});
vm.runInContext(html.slice(start,end)+';globalThis.build=assembleScene;',ctx);
const assemble=ctx.build,shows=load('data/shows.json'),base='data/shows/stardust-station',shelf={};
for(const x of ['characters','dialogue','settings','regions','factions','direction'])
  shelf[x+'.json']=load(base+'/'+x+'.json');
let pagesTotal=0;
for(let n=4;n<=10;n++){
 const suffix=String(n).padStart(2,'0'),show=shows.find(x=>x.id==='stardust-station-e'+suffix);
 assert(show,'Missing Stardust issue '+suffix);
 assert(!(show.sceneOverlays||[]).some(x=>/page_assembly_profiles_e|pages_e\d\d_density_pass|visual_cast_e/.test(x.file)),
   'Consolidated Issue '+suffix+' overlays remain active');
 const pages=load(base+'/pages_e'+suffix+'.json');
 assert.equal(new Set(pages.map(x=>x.id)).size,pages.length,'Duplicate page '+suffix);
 for(const [i,page] of pages.entries()){
   assert(Array.isArray(page.panelPlan)&&page.panelPlan.length,'Missing authored panels '+page.id);
   const assembled=assemble(page,{...shelf,__show:show},i);
   assert(assembled.includes('[PANEL PLAN]'),'Panels omitted '+page.id);
   if(page.promptSuppress?.includes('summary'))
     assert(!assembled.includes(page.summary),'Suppressed summary emitted '+page.id);
   for(const line of page.dialogueInline||[])if(line.text)
     assert(assembled.includes(line.text),'Authored dialogue omitted '+page.id);
   for(const panel of page.panelPlan||[]){
     const text=typeof panel==='string'?panel:panel.text||panel.action||panel.summary;
     if(text)assert(assembled.includes(text),'Authored panel action omitted '+page.id);
   }
   if(page.promptSettingMode==='label'){
     const place=shelf['settings.json'][page.setting];
     assert(place?.name&&assembled.includes(place.name),'Location label omitted '+page.id);
   }
   pagesTotal++;
 }
}
assert.equal(pagesTotal,153,'Stardust Issues 4–10 issue inventory changed');
console.log('PASS Stardust Issues 4–10: '+pagesTotal+' authoritative page sources, scoped production delivery and all scripted lines retained');
