#!/usr/bin/env node
'use strict';
// Existing Rex Fleet source-to-chef check against authoritative page records.
// Tests delivery, not whether creative writing conforms to a particular formula.
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib'),vm=require('node:vm');
const root=path.resolve(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8'),json=p=>JSON.parse(read(p));
const shows=json('data/shows.json'),base='data/shows/rex-fleet-s1',html=read('index.html');
const start=html.indexOf('const SHOW_MANIFEST='),end=html.indexOf('function safeFilePart(',start);
assert(start>=0&&end>start,'Canonical assembler unavailable');
const context=vm.createContext({});
vm.runInContext(html.slice(start,end)+';globalThis.assemble=assembleScene;',context);
const assemble=context.assemble,store={};
for(const n of ['characters','dialogue','settings','regions','factions','direction'])
  store[n+'.json']=json(base+'/'+n+'.json');
function loadLayer(o){
 const text=read(base+'/'+o.file);
 const items=o.encoding==='gzip-base64'
   ?JSON.parse(zlib.gunzipSync(Buffer.from(text.trim(),'base64')).toString('utf8'))
   :JSON.parse(text);
 const ids=o.includeIds?new Set(o.includeIds):null,excluded=o.excludeIds?new Set(o.excludeIds):null;
 return items.filter(x=>(!ids||ids.has(x.id))&&(!excluded||!excluded.has(x.id)));
}
let stories=0,specials=0,assembled=0;
for(let n=1;n<=12;n++){
 const id='rex-fleet-i'+String(n).padStart(2,'0'),show=shows.find(x=>x.id===id);
 assert(show,'Missing registered issue '+id);
 assert(!(show.sceneOverlays||[]).some(x=>/page_layout_i\d\d\.json|page_assembly_scope_i\d\d\.json/.test(x.file)),
   'Consolidated page scopes are still registered as overlays '+id);
 let pages=json(base+'/'+(show.scenesFile||'pages_base.json'));
 for(const layer of show.sceneOverlays||[]){
   const updates=loadLayer(layer);
   if(layer.mergeById){
     const byId=new Map(updates.map(x=>[x.id,x]));
     pages=pages.map(x=>byId.has(x.id)?{...x,...byId.get(x.id)}:x);
     if(layer.strict)assert(updates.every(x=>pages.some(p=>p.id===x.id)),'Missing strict page ID '+id);
   }else if(layer.afterId){
     const i=pages.findIndex(x=>x.id===layer.afterId);
     pages.splice(i<0?pages.length:i+1,0,...updates);
   }else pages.push(...updates);
 }
 pages=pages.filter(x=>new RegExp(show.includeIdPattern).test(x.id));
 assert.equal(new Set(pages.map(x=>x.id)).size,pages.length,'Duplicate assembled page '+id);
 for(const [index,page] of pages.entries()){
   const story=/^RF_I\d\d_P\d\d$/.test(page.id);
   if(story){
     stories++;
     assert(page.pageLayout&&Array.isArray(page.promptSuppress)&&page.promptVisibleCastOnly===true,
       'Previously accepted page production metadata lost '+page.id);
     assert.equal(page.pageLayout.panels?.length,page.panelPlan?.length,'Page composition drift '+page.id);
   }else specials++;
   const out=assemble(page,{...store,__show:show},index);
   assert(out.includes('[PANEL PLAN]'),'Lost panel plan '+page.id);
   if(page.pageLayout)assert(out.includes('[PAGE COMPOSITION]'),'Missing page composition '+page.id);
   for(const line of page.dialogueInline||[])if(line.text)
     assert(out.includes(line.text),'Authored dialogue omitted '+page.id);
   assembled++;
 }
}
assert(stories>250&&specials>0,'Unexpected Rex Fleet page inventory');
console.log('PASS Rex Fleet normalization: '+assembled+' assembled units across 12 issues; '+stories+
  ' authoritative story pages and '+specials+' special pages; complete dialogue and composition delivery');
