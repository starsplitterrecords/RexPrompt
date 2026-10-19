#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8'),json=p=>JSON.parse(read(p));
const html=read('index.html'),start=html.indexOf('const SHOW_MANIFEST='),end=html.indexOf('function safeFilePart(',start);
assert(start>=0&&end>start);const context=vm.createContext({});
vm.runInContext(html.slice(start,end)+';globalThis.api={assembleScene,visibleCharacterHandles};',context);
const {assembleScene,visibleCharacterHandles}=context.api, all=json('data/shows.json');
const shipIds=['rex-fleet-stormwell-archive-i01','rex-fleet-glass-horizon-i01',
 'rex-fleet-aegis-vigil-i01','rex-fleet-ghostwind-arrow-i01',
 'rex-fleet-slip-knife-i01','rex-fleet-crimson-warden-i01'];
function normalize(raw){return Array.isArray(raw)?raw:(raw?.pages||Object.entries(raw||{}).map(([id,x])=>({id,...x})))}
function loadPages(show){
 let pages=normalize(json(show.basePath+'/'+show.scenesFile));
 for(const ov of show.sceneOverlays||[]){
  const incoming=normalize(json(show.basePath+'/'+ov.file));
  if(ov.mergeById){
   const keyed=new Map(incoming.map(x=>[x.id,x]));
   if(ov.strict)for(const id of keyed.keys())assert(pages.some(x=>x.id===id),'Unmatched strict ship overlay '+id);
   const seen=new Set();
   pages=pages.map(p=>{const patch=keyed.get(p.id);if(patch){seen.add(p.id);return {...p,...patch}}return p});
   if(!ov.strict)pages.push(...incoming.filter(p=>!seen.has(p.id)&&!pages.some(x=>x.id===p.id)));
  }else pages.push(...incoming);
 }
 if(show.includeIdPattern)pages=pages.filter(p=>new RegExp(show.includeIdPattern).test(p.id));
 return pages;
}
function section(text,key){
 const prefix='\n['+key+']\n',pos=text.indexOf(prefix);if(pos<0)return null;
 const rest=text.slice(pos+prefix.length),m=rest.search(/\n\[[A-Z][A-Z /_-]*\]\n/);
 return m<0?rest:rest.slice(0,m);
}
let pagesTotal=0,baseFactionPages=0,keptFactionPages=0,handles=0,offPanel=0;
for(const id of shipIds){
 const show=all.find(x=>x.id===id);assert(show,'Missing ship '+id);
 assert.equal(show.promptVisibleCastOnly,true,'Ship missing visible cast scoping '+id);
 assert.equal(show.omitRoutineFactions,true,'Ship missing faction scoping '+id);
 const base=show.basePath,store={__show:show};
 for(const shelf of ['characters','dialogue','settings','regions','factions','direction'])
  store[shelf+'.json']=json(base+'/'+shelf+'.json');
 const exceptionEntries=(show.sceneOverlays||[]).filter(x=>/visual_faction_pages_i01/.test(x.file));
 if(id==='rex-fleet-glass-horizon-i01')assert.equal(exceptionEntries.length,0,'Glass Horizon has no faction data');
 else assert.equal(exceptionEntries.length,1,'Expected one faction exceptions shelf '+id);
 const exceptions=exceptionEntries.length?json(base+'/'+exceptionEntries[0].file):[];
 const retained=new Set(exceptions.map(x=>x.id));
 assert.equal(retained.size,exceptions.length,'Duplicate ship exception ID');
 const pages=loadPages(show);assert(pages.length>=22,'Unexpected issue size '+id);
 let localCount=0;
 for(const [i,p] of pages.entries()){
  const txt=assembleScene(p,store,i),expected=Array.from(visibleCharacterHandles(p,store['characters.json']));
  const refs=txt.split('\n').filter(s=>s.startsWith('@'));
  assert.deepEqual(refs,expected,'Wrong page visual cast '+p.id);
  assert(!txt.includes('\n[CAST]\n')&&!txt.includes('\n[CHARACTERS]\n'),'Duplicate cast on '+p.id);
  const needsFactions=retained.has(p.id)&&!!p.factions?.length;
  assert.equal(txt.includes('\n[FACTIONS]\n'),needsFactions,'Missing or excess faction description '+p.id);
  if(needsFactions)keptFactionPages++;
  if(p.factions?.length)baseFactionPages++;
  const panelText=section(txt,'PANEL PLAN');
  for(const panel of p.panelPlan||[]){
   const entry=typeof panel==='string'?panel:(panel.text||panel.name||panel.summary||JSON.stringify(panel));
   assert(panelText?.includes(entry),'Scripted panel lost '+p.id);
  }
  for(const line of p.dialogueInline||[]){
   assert(txt.includes('"'+(line.text||'')+'"'),'Scripted dialogue changed '+p.id);
   if(line.handle?.startsWith('@')&&!expected.includes(line.handle)){
    assert(!txt.includes(line.handle),'Unpictured dialogue speaker leaked into reference tags '+p.id);
    offPanel++;
   }
  }
  handles+=refs.length;localCount++;
 }
 assert(exceptions.every(x=>pages.some(p=>p.id===x.id&&p.promptIncludeFactions===true)),'Exception overlay not applied '+id);
 pagesTotal+=localCount;console.log('PASS '+id+': '+localCount+' pages; visible cast only, selective faction visuals');
}
assert(baseFactionPages>keptFactionPages,'Repeated faction prose was not reduced');
// Thunderbreak already has explicit page-scoped visual-cast contracts. Do not blanket-change them.
const thunder=all.filter(x=>/^rex-fleet-i\d{2}$/.test(x.id));
assert.equal(thunder.length,12,'Expected twelve Thunderbreak issues');
for(const show of thunder){
 assert.equal(show.promptVisibleCastOnly,undefined,'Do not overwrite established Thunderbreak page-level cast decisions');
 assert.equal(show.omitRoutineFactions,undefined,'Do not replace existing Thunderbreak faction policies');
 const id=show.id.match(/i(\d{2})$/)[1];
 const shelf=json('data/shows/rex-fleet-s1/editorial/page_assembly_scope_i'+id+'.json');
 assert(shelf.length>=12,'Thunderbreak page scopes missing '+show.id);
 assert(shelf.every(p=>p.promptVisibleCastOnly===true),'Existing visible-cast scope compromised '+show.id);
}
console.log('PASS Fleet ships: '+shipIds.length+' spin-off issues / '+pagesTotal+' pages / '+handles+' visible references; '+keptFactionPages+' of '+baseFactionPages+' authored faction pages preserved as essential; '+offPanel+' off-panel speakers excluded. Thunderbreak: 12 issue policies unchanged.');
