#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8'),json=p=>JSON.parse(read(p));
const html=read('index.html'),a=html.indexOf('const SHOW_MANIFEST='),b=html.indexOf('function safeFilePart(',a);
assert(a>=0&&b>a);const context=vm.createContext({});
vm.runInContext(html.slice(a,b)+';globalThis.exportsForTest={assembleScene,visibleCharacterHandles};',context);
const {assembleScene,visibleCharacterHandles}=context.exportsForTest;
const shows=json('data/shows.json').filter(s=>/^(rex-fleet-academy-(?!.*cover)|rfa-reach-resolve-i01)/.test(s.id)&&s.scenesFile);
assert.equal(shows.length,7,'Seven registered Academy story issues expected');
const normalize=raw=>Array.isArray(raw)?raw:(raw?.pages||Object.entries(raw||{}).map(([id,p])=>({id,...p})));
function loadPages(show){
 const dir=show.basePath,pages=normalize(json(dir+'/'+show.scenesFile));
 let current=pages;
 for(const ov of show.sceneOverlays||[]){
  const incoming=normalize(json(dir+'/'+ov.file));
  if(ov.mergeById){
   const keys=new Map(incoming.map(p=>[p.id,p])),seen=new Set();
   if(ov.strict)for(const id of keys.keys())assert(current.some(p=>p.id===id),'Orphan strict overlay '+id);
   current=current.map(p=>{const x=keys.get(p.id);if(x){seen.add(p.id);return {...p,...x}}return p});
   if(!ov.strict)current.push(...incoming.filter(p=>!seen.has(p.id)&&!current.some(x=>x.id===p.id)));
  }else current.push(...incoming);
 }
 if(show.includeIdPattern)current=current.filter(p=>new RegExp(show.includeIdPattern).test(p.id));
 return current;
}
function section(text,key){
 const prefix='\n['+key+']\n',start=text.indexOf(prefix);
 if(start<0)return null;const rest=text.slice(start+prefix.length),m=rest.search(/\n\[[A-Z][A-Z /_-]*\]\n/);
 return m<0?rest:rest.slice(0,m);
}
let total=0,factioned=0,baselineFactions=0,refs=0,speakerOnly=0;
for(const show of shows){
 assert.equal(show.promptVisibleCastOnly,true,show.id+' has no visual cast mode');
 assert.equal(show.omitRoutineFactions,true,show.id+' has no faction suppression');
 const filenames=(show.sceneOverlays||[]).filter(x=>/visual_faction_pages_i01/.test(x.file));
 assert.equal(filenames.length,1,'Missing page-local exception data '+show.id);
 const exceptions=json(show.basePath+'/'+filenames[0].file);
 assert(exceptions.length>=1,show.id+' must retain essential faction visual context');
 const expectedExceptionIds=new Set(exceptions.map(x=>x.id));
 assert.equal(expectedExceptionIds.size,exceptions.length);
 const store={__show:show};
 for(const file of ['characters','dialogue','settings','regions','factions','direction'])store[file+'.json']=json(show.basePath+'/'+file+'.json');
 const pages=loadPages(show);
 assert(pages.length>=22,'Unexpected Academy issue size '+show.id);
 let local=0;
 for(const [i,p] of pages.entries()){
  const text=assembleScene(p,store,i);
  assert(!text.includes('\n[CAST]\n')&&!text.includes('\n[CHARACTERS]\n'),'Duplicated roster '+p.id);
  const expected=Array.from(visibleCharacterHandles(p,store['characters.json']));
  const present=text.split('\n').filter(s=>s.startsWith('@'));
  assert.deepEqual(present,expected,'Incorrect visual references '+p.id);
  for(const line of p.dialogueInline||[]){
   assert(text.includes('"'+(line.text||'')+'"'),'Missing scripted line '+p.id);
   if(line.handle&&line.handle.startsWith('@')&&!expected.includes(line.handle)){
    assert(!text.includes(line.handle),'Dialogue-only handle leaked into image refs '+p.id);
    speakerOnly++;
   }
  }
  const rendered=section(text,'PANEL PLAN'),source=(p.panelPlan||[]).map(x=>typeof x==='string'?x:(x.text||x.name||x.summary||JSON.stringify(x)));
  for(const panel of source)assert(rendered?.includes(panel),'Lost panel text '+p.id);
  const shouldHave=expectedExceptionIds.has(p.id)&&!!p.factions?.length;
  assert.equal(text.includes('\n[FACTIONS]\n'),shouldHave,'Faction scoping incorrect '+p.id);
  if(shouldHave)factioned++;
  if(p.factions?.length)baselineFactions++;
  local++;refs+=expected.length;
 }
 assert(exceptions.every(x=>pages.some(p=>p.id===x.id&&p.promptIncludeFactions===true)),'Unapplied faction exceptions '+show.id);
 total+=local;console.log('PASS '+show.id+': '+local+' pages, only cited cast and intentional factions');
}
assert(baselineFactions>factioned,'Faction scoping must substantially reduce repeated prose');
console.log('PASS Academy: '+shows.length+' issues / '+total+' pages / '+refs+' visible identities; '+factioned+' necessary faction contexts retained of '+baselineFactions+' authored, '+speakerOnly+' dialogue-only speakers excluded; all scripted lettering and panels preserved');
