#!/usr/bin/env node
'use strict';
// Reconcile the Low Tide creative-dialogue overlay with live page compositions.
// This is a mechanical integrity test, not a creative wording or quota validator.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),zlib=require('node:zlib'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),base='data/shows/low-tide-signal';
const read=p=>fs.readFileSync(path.join(root,p),'utf8'),json=p=>JSON.parse(read(p));
const src=read('index.html'),begin=src.indexOf('const SHOW_MANIFEST='),end=src.indexOf('function safeFilePart(',begin);
assert(begin>=0&&end>begin,'Current canonical assembler unavailable');
const scope=vm.createContext({});
vm.runInContext(src.slice(begin,end)+';globalThis.api={assembleScene,applyDialogueOverlay,normalizeOverlay,validatePageLayout,pageLayoutWarnings};',scope);
const {assembleScene:assemble,applyDialogueOverlay:patchDialogue,normalizeOverlay:normalize,validatePageLayout:validate,pageLayoutWarnings:warnings}=scope.api;
const showConfigs=json('data/shows.json'),packageConfig=json(base+'/assembler.json'),rawOverlay=json(base+'/dialogue.json'),characters=json(base+'/characters.json');
const leadNames=new Map(Object.entries(characters).map(([key,character])=>[character.name,key]));
assert(Array.isArray(packageConfig.dialogueOverlays)&&packageConfig.dialogueOverlays.length===1);
assert.equal(packageConfig.dialogueOverlays[0].file,'dialogue.json','Dialogue must use a separate package-level overlay, after scene layout overlays');
assert(packageConfig.dialogueOverlays[0].strict,'Dialogue overlay declared strict');
const incoming=normalize(rawOverlay);
assert.equal(incoming.length,Object.keys(rawOverlay).length,'Invalid overlay normalization');
assert.equal(new Set(incoming.map(x=>x.id)).size,incoming.length,'Duplicate dialogue overlay IDs');
const byId=new Map(incoming.map(x=>[x.id,x]));
const registry=new Map(),store={};
for(const name of ['characters','settings','regions','factions','direction','dialogue'])
 store[name+'.json']=json(base+'/'+name+'.json');
let storyPages=0,framing=0,editedPages=0,changedPages=0,advisories=0,maximumLines=0;
function unpack(overlay){
 const raw=read(base+'/'+overlay.file);
 return overlay.encoding==='gzip-base64'?JSON.parse(zlib.gunzipSync(Buffer.from(raw.trim(),'base64')).toString('utf8')):JSON.parse(raw);
}
function withoutDialogue(recipe){
 const marker='\n[DIALOGUE]\n',at=recipe.indexOf(marker);
 if(at<0)return recipe;
 const rest=recipe.slice(at+marker.length),next=rest.search(/\n\[[A-Z][A-Z0-9 /_&-]*\]\n/);
 return recipe.slice(0,at)+(next<0?'':rest.slice(next));
}
for(let chapter=1;chapter<=7;chapter++){
 const chapterId='low-tide-signal-c'+String(chapter).padStart(2,'0');
 const show=showConfigs.find(s=>s.id===chapterId);
 assert(show,'Missing chapter '+chapterId);
 assert(!show.dialogueOverlays,'Chapter must inherit dialogue overlay from package config');
 const assembledShow={...packageConfig,...show};
 let pages=json(base+'/'+(show.scenesFile||'pages_base.json'));
 for(const layer of show.sceneOverlays||[]){
  const data=unpack(layer);
  if(!layer.mergeById){pages.push(...data);continue}
  const byPatch=new Map(data.map(x=>[x.id,x]));
  pages=pages.map(p=>({...p,...(byPatch.get(p.id)||{})}));
 }
 pages=pages.filter(p=>new RegExp(show.includeIdPattern).test(p.id));
 assert.equal(new Set(pages.map(p=>p.id)).size,pages.length,'Duplicate authored page IDs for '+chapterId);
 const layered=patchDialogue(pages,incoming);
 assert.equal(layered.length,pages.length,'Dialogue changed page inventory');
 for(let i=0;i<pages.length;i++){
  const original=pages[i],page=layered[i],update=byId.get(page.id);
  assert(!registry.has(page.id),'Duplicate chapter page '+page.id);
  registry.set(page.id,page);
  assert.equal(page.id,original.id);
  assert.deepEqual(page.panelPlan,original.panelPlan,'Dialogue pass changed scripted panels: '+page.id);
  assert.deepEqual(page.pageLayout,original.pageLayout,'Dialogue pass changed visual hierarchy: '+page.id);
  validate(page);
  const before=assemble(original,{...store,__show:assembledShow},i),after=assemble(page,{...store,__show:assembledShow},i);
  assert.equal(withoutDialogue(after),withoutDialogue(before),'Non-dialogue recipe changed on '+page.id);
  if(update){
   assert.deepEqual(Object.keys(update).sort(),['dialogueInline','dialogueSource','id'],'Overlay has unauthorized story fields on '+page.id);
   assert.equal(page.dialogueSource,update.dialogueSource);
   assert.equal(page.dialogueInline.length,update.dialogueInline.length);
   for(const line of update.dialogueInline){
    assert(typeof line.speaker==='string'&&line.speaker.trim()&&typeof line.text==='string'&&line.text.trim(),
      'Missing speaker or text on '+page.id);
    const castId=leadNames.get(line.speaker);
    if(castId)assert(page.characters?.includes(castId),'Uncast recurring speaker '+line.speaker+' on '+page.id);
    assert(after.includes(line.text),'New dialogue is not in assembled recipe for '+page.id);
   }
   maximumLines=Math.max(maximumLines,update.dialogueInline.length);
   editedPages++;
   if(JSON.stringify(original.dialogueInline)!==JSON.stringify(update.dialogueInline))changedPages++;
   advisories+=warnings(page).length;
  }else assert.deepEqual(page.dialogueInline,original.dialogueInline,'Unlisted dialogue unexpectedly overwritten '+page.id);
  if(/_EDITOR_/.test(page.id))framing++;else storyPages++;
 }
}
assert.equal(storyPages,178,'The seven chapters should retain 178 story pages');
assert.equal(framing,14,'Framing pages must not change');
assert.equal(editedPages,incoming.length,'Orphan dialogue overlay (missing from configured story)');
assert(changedPages>0,'No visible creative dialogue changes');
assert.equal(registry.size,192,'Story/framing inventory differs from authored series');
console.log('PASS Low Tide dialogue: '+editedPages+' overlays resolved, '+changedPages+' changed vs current source, '+storyPages+' story + '+framing+' editorial pages');
console.log('PASS Original page plans, page layouts, non-dialogue chef ingredients, cast and dialogue ownership unchanged');
console.log('INFO Highest overlay lettering items per page: '+maximumLines+'; advisory warnings: '+advisories);
