#!/usr/bin/env node
'use strict';
// Azure Reach Phase C: dialogue ownership and density, against the authored compressed source.
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const load=p=>JSON.parse(read(p));
const shows=load('data/shows.json');
const drafts=load('production/drafts/manifest.json').drafts;
const approved=new Set(Object.values(drafts).filter(x=>x.seriesId==='azure-reach'&&x.status==='approved-production-draft').map(x=>x.recipeId));
assert.equal(approved.size,9,'Approved art inventory changed; review locks before proceeding');
const base='data/shows/azure-reach-s1/';
function decode(overlay){
 const raw=read(base+overlay.file);
 return overlay.encoding==='gzip-base64'?
   JSON.parse(zlib.gunzipSync(Buffer.from(raw.trim(),'base64')).toString('utf8')):JSON.parse(raw);
}
function pages(show){return show.sceneOverlays.filter(o=>/^encoded\/pages_e0/.test(o.file)).flatMap(decode)}
const html=read('index.html'),start=html.indexOf('const SHOW_MANIFEST='),end=html.indexOf('function safeFilePart(',start);
const sandbox=vm.createContext({});
vm.runInContext(html.slice(start,end)+';globalThis.__test={assembleScene,validatePageLayout};',sandbox);
const {assembleScene:assemble,validatePageLayout:validate}=sandbox.__test;
const store={};
for(const name of ['characters','dialogue','settings','regions','factions','direction'])store[name+'.json']=load(base+name+'.json');
const allowedChanges={
 AZR_S1E03_P01:[1],AZR_S1E03_P02:[3],AZR_S1E03_P13:[5],
 AZR_S1E03_P17:[4],AZR_S1E04_P11:[0],AZR_S1E05_P04:[1],
 AZR_S1E05_P14:[3],AZR_S1E05_P18:[6],AZR_S1E06_P03:[6],
 AZR_S1E06_P08:[2]
};
const expectedCount={2:4,3:9,4:8,5:6,6:7};
let totalPages=0,updatedLines=0,deletedLines=0,attributed=0,savedWords=0;
function block(text,name){
 const begin=text.indexOf('\n['+name+']');if(begin<0)return null;
 const rest=text.slice(begin),next=rest.slice(2).search(/\n\[[A-Z][A-Z _/-]*\]/);
 return next<0?rest:rest.slice(0,next+2);
}
for(let n=1;n<=6;n++){
 const show=shows.find(s=>s.id===(n===1?'azure-reach-s1':'azure-reach-s1-e0'+n));
 assert(show,'Missing show '+n);
 const authored=pages(show);
 assert.equal(authored.length,22,'Issue '+n+' page count changed');
 if(n===1){assert(!show.dialogueOverlays?.some(o=>/dialogue_c_/.test(o.file)),'Released issue 1 modified');continue}
 const target='editorial/dialogue_c_e0'+n+'.json';
 const descriptor=(show.dialogueOverlays||[]).find(x=>x.file===target);
 assert(descriptor,'Phase C overlay is not registered '+n);
 const patches=decode(descriptor),byId=new Map(patches.map(x=>[x.id,x]));
 assert.equal(patches.length,expectedCount[n],'Unexpected edited-page count in Issue '+n);
 assert.equal(byId.size,patches.length,'Duplicate editorial page ID in Issue '+n);
 const srcById=new Map(authored.map(x=>[x.id,x]));
 assert([...byId.keys()].every(x=>srcById.has(x)),'Unknown page in editorial overlay '+n);
 const scope=new Map(load(base+'editorial/page_recipe_scopes_e0'+n+'.json').map(x=>[x.id,x]));
 const layouts=new Map(load(base+'editorial/page_layouts_e0'+n+'.json').map(x=>[x.id,x]));
 for(const p of authored){
  const patch=byId.get(p.id);
  if(approved.has(p.id)){assert(!patch,'Approved production page was modified '+p.id);continue}
  if(!patch)continue;totalPages++;
  assert.deepEqual(Object.keys(patch).sort(),['dialogueInline','dialogueSource','id'],'Dialogue-only overlay scope exceeded '+p.id);
  assert.equal(patch.id,p.id);
  const original=p.dialogueInline||[],final=patch.dialogueInline;
  assert(Array.isArray(final)&&final.length>0,'Missing dialogue on '+p.id);
  const deletion=p.id==='AZR_S1E06_P20'?1:0;
  assert.equal(original.length-final.length,deletion,'Unexpected balloon deletion on '+p.id);
  for(const d of final)assert(!/^\s*$/.test(d.text),'Blank dialogue balloon on '+p.id);
  let prev=0;
  for(let i=0;i<final.length;i++){
   const a=original[i],b=final[i],match=String(b.subtext||'').match(/^Panel ([1-9]\d*)$/);
   assert(match,'Missing explicit balloon-panel assignment '+p.id+' line '+i);
   const panel=Number(match[1]);
   assert(panel>=prev&&panel<=p.panelPlan.length,'Broken panel order/reader flow '+p.id+' line '+i);
   prev=panel;attributed++;
   assert.equal(b.handle,a.handle,'Speaker handle moved '+p.id+' #'+i);
   assert.equal(b.speaker,a.speaker,'Dialogue speaker changed '+p.id+' #'+i);
   const keys=Object.keys(a).filter(x=>x!=='subtext').sort(),other=Object.keys(b).filter(x=>x!=='subtext').sort();
   assert.deepEqual(other,keys,'Unknown dialogue fields changed '+p.id+' #'+i);
   const allowed=(allowedChanges[p.id]||[]).includes(i);
   if(b.text!==a.text){assert(allowed,'Unreviewed dialogue rewrite '+p.id+' #'+i);updatedLines++;}
   else assert(!allowed,'Expected editorial rewrite missing '+p.id+' #'+i);
  }
  if(deletion){
   assert.equal(original.at(-1).handle,'@azr.Sponsor','Unexpected deleted speaker');
   assert.equal(original.at(-1).text,'Congratulations.','Unexpected deleted statement');
   deletedLines++;
  }
  const combined={...p,...scope.get(p.id),...layouts.get(p.id)};
  const newScene={...combined,dialogueInline:final};
  validate(newScene);
  const before=assemble(combined,{...store,__show:show},0);
  const after=assemble(newScene,{...store,__show:show},0);
  for(const field of ['SETTING','PAGE COMPOSITION','PANEL PLAN','CONTINUITY','DIRECTION']){
   assert.equal(block(after,field),block(before,field),'Non-dialogue assembled ingredient changed: '+p.id+' '+field);
  }
  assert(after.includes('[DIALOGUE]'),'Chef dialogue missing '+p.id);
  for(const d of final)assert(after.includes(d.text),'Balloon dropped by assembler '+p.id+': '+d.text);
  const wordcount=lines=>lines.reduce((v,d)=>v+(String(d.text||'').trim().match(/\S+/g)||[]).length,0);
  savedWords+=wordcount(original)-wordcount(final);
 }
 console.log('PASS Azure Issue '+n+': '+patches.length+' story-specific pages, exact panel references, original art/layout and character handles protected');
}
assert.equal(totalPages,34);
assert.equal(updatedLines,10,'Unexpected number of reviewed voice revisions');
assert.equal(deletedLines,1,'Unexpected dialogue deletion');
assert(attributed>180,'Too few balloon placements');
console.log('PASS Azure Phase C: '+totalPages+' pages with explicit balloon placement; '+attributed+' assigned dialogue balloons; '+updatedLines+' selective voice rewrites, '+deletedLines+' dispensable balloon removed, '+savedWords+' fewer spoken words');
console.log('PASS all issue lengths unchanged, all approved/released pages excluded, authored panel and composition directions unchanged');
