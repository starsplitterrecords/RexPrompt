#!/usr/bin/env node
'use strict';
// Low Tide Signal: verify current authored page layouts survive compilation
// across all 7 chapters. No narrative style or pacing quotas.
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8'),json=p=>JSON.parse(read(p));
const html=read('index.html'),a=html.indexOf('const SHOW_MANIFEST='),b=html.indexOf('function safeFilePart(',a);
assert(a>=0&&b>a,'Assembler unavailable');
const sandbox=vm.createContext({});
vm.runInContext(html.slice(a,b)+';globalThis.api={assembleScene,validatePageLayout};',sandbox);
const {assembleScene:assemble,validatePageLayout:validate}=sandbox.api;
const shows=json('data/shows.json'),base='data/shows/low-tide-signal',store={};
for(const f of ['characters','dialogue','settings','regions','factions','direction'])
 store[f+'.json']=json(base+'/'+f+'.json');
function readOverlay(o){const text=read(base+'/'+o.file);return o.encoding==='gzip-base64'
 ?JSON.parse(zlib.gunzipSync(Buffer.from(text.trim(),'base64')).toString('utf8')):JSON.parse(text)}
let stories=0,framing=0,all=0;
const seen=new Set();
for(let chapter=1;chapter<=7;chapter++){
 const id='low-tide-signal-c'+String(chapter).padStart(2,'0'),show=shows.find(x=>x.id===id);
 assert(show,'Missing chapter '+id);
 const overlays=show.sceneOverlays||[];
 if(chapter<=3)assert(overlays.length===3,'Normalized page source must not reapply layout overlays '+id);
 let pages=json(base+'/'+(show.scenesFile||'pages_base.json'));
 for(const layer of overlays){
   const incoming=readOverlay(layer);
   if(layer.mergeById){
     const byId=new Map(incoming.map(x=>[x.id,x]));
     pages=pages.map(x=>byId.has(x.id)?{...x,...byId.get(x.id)}:x);
   }else pages.push(...incoming);
 }
 pages=pages.filter(x=>new RegExp(show.includeIdPattern).test(x.id));
 assert.equal(new Set(pages.map(x=>x.id)).size,pages.length,'Duplicate page IDs '+id);
 for(const [i,page] of pages.entries()){
   assert(!seen.has(page.id),'Duplicate chapter page '+page.id);seen.add(page.id);
   assert(page.pageLayout,'Composed page missing '+page.id);
   validate(page);
   assert.equal(page.pageLayout.panels?.length,page.panelPlan?.length,'Layout panel count mismatch '+page.id);
   const out=assemble(page,{...store,__show:show},i);
   assert(out.includes('[PAGE COMPOSITION]')&&out.includes('[PANEL PLAN]'),'Layout or panel plan omitted '+page.id);
   for(const line of page.dialogueInline||[])if(line.text)
     assert(out.includes(line.text),'Authored dialogue omitted '+page.id);
   if(page.id.includes('EDITOR_'))framing++;else stories++;
   all++;
 }
}
assert.equal(stories,178,'Story inventory changed');
assert.equal(framing,14,'Editorial framing inventory changed');
console.log('PASS Low Tide: '+all+' current composed pages ('+stories+' story, '+framing+
 ') across 7 chapters, all panel plans, layouts and authored dialogue delivered');
