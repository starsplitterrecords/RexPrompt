#!/usr/bin/env node
'use strict';
// Canonical Low Tide dialogue audit. Historical edits are in Git, not an override shelf.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),zlib=require('node:zlib'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),base='data/shows/low-tide-signal';
const read=p=>fs.readFileSync(path.join(root,p),'utf8'),json=p=>JSON.parse(read(p));
assert(!fs.existsSync(path.join(root,base,'assembler.json')),'Retired package-level dialogue override configuration returned');
assert.deepEqual(json(base+'/dialogue.json'),{},'Low Tide compatibility shelf must not duplicate authored page dialogue');
const html=read('index.html'),start=html.indexOf('const SHOW_MANIFEST='),end=html.indexOf('function safeFilePart(',start);
assert(start>=0&&end>start,'Live assembler missing');
const ctx=vm.createContext({});
vm.runInContext(html.slice(start,end)+';globalThis.api={assembleScene,validatePageLayout,pageLayoutWarnings};',ctx);
const {assembleScene,validatePageLayout,pageLayoutWarnings}=ctx.api;
const shows=json('data/shows.json'),store={};
for(const f of ['characters','settings','regions','factions','direction','dialogue'])store[f+'.json']=json(base+'/'+f+'.json');
function unpack(o){
 const text=read(base+'/'+o.file);
 return o.encoding==='gzip-base64'?JSON.parse(zlib.gunzipSync(Buffer.from(text.trim(),'base64')).toString('utf8')):JSON.parse(text);
}
let pages=0,story=0,framing=0,normalized=0,lines=0;const ids=new Set();
for(let n=1;n<=7;n++){
 const id='low-tide-signal-c'+String(n).padStart(2,'0'),show=shows.find(s=>s.id===id);
 assert(show,'Missing Low Tide chapter '+id);
 assert(!(show.dialogueOverlays||[]).length,'Active dialogue overlay on '+id);
 assert(!(show.sceneOverlays||[]).some(x=>x.mergeById),'Field patch on '+id);
 let all=json(base+'/'+(show.scenesFile||'pages_base.json'));
 for(const o of show.sceneOverlays||[]){assert(!o.mergeById,'Overlapping production file '+id);all.push(...unpack(o));}
 all=all.filter(x=>new RegExp(show.includeIdPattern).test(x.id));
 const showStore={...store,__show:show};
 for(const [i,page] of all.entries()){
  assert(!ids.has(page.id),'Duplicate page '+page.id);ids.add(page.id);
  assert(page.pageLayout&&page.panelPlan?.length,'Missing canonical composition '+page.id);
  validatePageLayout(page);
  assert(Array.isArray(page.dialogueInline),'Dialogue not normalized inline '+page.id);
  const prompt=assembleScene(page,showStore,i);
  for(const d of page.dialogueInline){assert(d.text&&d.speaker,'Missing canonical dialogue attribution on '+page.id);
   assert(prompt.includes(d.text),'Canonical spoken line omitted '+page.id);lines++;}
  if(page.dialogueSource==='Low Tide Signal creative writing pass')normalized++;
  if(/_EDITOR_/.test(page.id))framing++;else story++;
  pages++;
  pageLayoutWarnings(page);
 }
}
assert.equal(pages,192,'Canonical page inventory changed');
assert.equal(story,178,'Low Tide story inventory changed');
assert.equal(framing,14,'Low Tide editorial inventory changed');
assert.equal(normalized,153,'Creative dialogue normalization inventory changed');
console.log('PASS Low Tide canonical dialogue: '+normalized+' normalized pages, '+lines+' scripted lines across '+story+' story and '+framing+' editorial pages; no dialogue overlays.');
