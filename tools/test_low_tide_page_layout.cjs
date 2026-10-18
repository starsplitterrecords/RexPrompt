#!/usr/bin/env node
'use strict';
// End-to-end Low Tide Signal phase B test: all 178 scripted story pages and
// 14 editorial framing pages, with canonical assembler and actual overlay order.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),zlib=require('node:zlib'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const json=p=>JSON.parse(read(p));
const html=read('index.html'),begin=html.indexOf('const SHOW_MANIFEST='),end=html.indexOf('function safeFilePart(',begin);
assert(begin>=0&&end>begin,'Canonical RexPrompt assembler not located');
const scope=vm.createContext({});
vm.runInContext(html.slice(begin,end)+';globalThis.api={assembleScene,validatePageLayout,formatPageLayout};',scope);
const {assembleScene:assemble,validatePageLayout:validate}=scope.api;
const catalog=json('data/shows.json'),base='data/shows/low-tide-signal';
function unpack(overlay){
 const raw=read(base+'/'+overlay.file);
 return overlay.encoding==='gzip-base64'?JSON.parse(zlib.gunzipSync(Buffer.from(raw.trim(),'base64')).toString('utf8')):JSON.parse(raw);
}
const stores={};const required=['characters','settings','regions','factions','direction','dialogue'];
for(const key of required)stores[key+'.json']=json(base+'/'+key+'.json');
const allProfiles=[],ids=new Set(),reports=[];
let totalStory=0,totalFraming=0,compositionModes=new Set(),insetPages=0;
for(let chapter=1;chapter<=7;chapter++){
 const chapterId='low-tide-signal-c'+String(chapter).padStart(2,'0'),show=catalog.find(x=>x.id===chapterId);
 assert(show,'Missing chapter configuration '+chapterId);
 const files=show.sceneOverlays||[],last=files.at(-1);
 const profilePath='editorial/page_layouts_c'+String(chapter).padStart(2,'0')+'.json';
 assert.equal(last.file,profilePath,'Layout must be the final story overlay before optional dialogue overlays');
 assert(last.mergeById&&last.strict,'Layout overlay must be a strict merge-by-id registration');
 const incoming=json(base+'/'+profilePath),chapterIds=new Set(),prev=new Map(),added=new Set();
 let originals=[];
 for(const overlay of files.slice(0,-1)){
   const chunk=unpack(overlay);
   if(overlay.mergeById){
     const map=new Map(chunk.map(x=>[x.id,x]));
     originals=originals.map(page=>({...page,...(map.get(page.id)||{})}));
   }else originals.push(...chunk);
 }
 originals=originals.filter(x=>new RegExp(show.includeIdPattern).test(x.id));
 assert.equal(new Set(originals.map(x=>x.id)).size,originals.length,'Repeated story ID in chapter '+chapter);
 assert.equal(incoming.length,originals.length,'Every authored page needs exactly one layout in chapter '+chapter);
 const profiles=new Map(incoming.map(x=>[x.id,x]));
 assert.equal(profiles.size,incoming.length,'Duplicate layout profile in chapter '+chapter);
 for(const page of originals){
   assert(!ids.has(page.id),'Duplicate profile across chapters: '+page.id);
   ids.add(page.id);
   const entry=profiles.get(page.id);
   assert(entry,'Missing page layout '+page.id);
   assert.deepEqual(Object.keys(entry).sort(),['id','pageLayout'],'The overlay may only author id/pageLayout: '+page.id);
   const result={...page,...entry};
   assert.equal(validate(result),entry.pageLayout,'Invalid layout for '+page.id);
   const original=assemble(page,{...stores,__show:show},0);
   const composed=assemble(result,{...stores,__show:show},0);
   assert(!original.includes('[PAGE COMPOSITION]'),'Baseline page must remain uncomposed '+page.id);
   const header=original.indexOf('\n[PANEL PLAN]'),newHeader=composed.indexOf('\n[PAGE COMPOSITION]'),newPlan=composed.indexOf('\n[PANEL PLAN]');
   assert(header>=0&&newHeader>=0&&newPlan>newHeader,'Layout not emitted before panel plan '+page.id);
   assert.equal(composed.slice(0,newHeader),original.slice(0,header),'Original recipe prefix changed '+page.id);
   assert.equal(composed.slice(newPlan),original.slice(header),'Original panel plan and all subsequent recipe data changed '+page.id);
   assert(composed.includes('Visual priority: '+entry.pageLayout.visualPriority),'Chef missing page-specific priority '+page.id);
   for(const line of page.dialogueInline||[])assert(composed.includes(line.text),'Lost dialogue '+page.id+': '+line.text);
   for(const assignment of entry.pageLayout.panels)assert(composed.includes('Panel '+assignment.panel+':'),'Unaddressed scripted panel '+page.id);
   compositionModes.add(entry.pageLayout.composition);
   if(entry.pageLayout.composition==='splash-with-insets')insetPages++;
   if(page.id.includes('EDITOR_'))totalFraming++;
   else totalStory++;
   chapterIds.add(page.id);
   allProfiles.push(entry);
 }
 for(const entry of incoming)assert(chapterIds.has(entry.id),'Orphaned layout profile '+entry.id);
 reports.push('chapter '+chapter+': '+originals.length+' pages, '+new Set(incoming.map(x=>x.pageLayout.composition)).size+' distinct layout types');
}
assert.equal(totalStory,178,'Expected 178 story pages, without pagination changes');
assert.equal(totalFraming,14,'Expected 14 editorial framing pages');
assert.equal(allProfiles.length,192,'Full series layout audit missing pages');
assert(compositionModes.size>=7,'Expected broad expressive layout palette');
assert(insetPages>=4,'Expected multiple deliberate inset compositions');
for(const entry of allProfiles)if(entry.id.includes('EDITOR_')){
 assert.equal(entry.pageLayout.composition,'splash','Editorial framing should remain a single full-page composition');
 assert(entry.pageLayout.negativeSpace?.length,'Editorial framing needs full-copy negative space');
}
console.log('PASS Low Tide Phase B: '+totalStory+' story pages + '+totalFraming+' editorial pages = '+allProfiles.length);
console.log('PASS Layout types: '+[...compositionModes].sort().join(', ')+'; inset compositions: '+insetPages);
console.log('PASS Every panel ref, dialogue, continuity, source recipe prefix and sequence unchanged');
console.log(reports.join('\n'));
