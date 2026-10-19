#!/usr/bin/env node
'use strict';
// Checks the actual browser assembler and all registered stories/covers in four series.
// Full writing remains intact; only generation-time visual reference scope changes.
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib'),vm=require('node:vm');
const root=path.resolve(__dirname,'..'),read=f=>fs.readFileSync(path.join(root,f),'utf8'),json=f=>JSON.parse(read(f));
const html=read('index.html'),from=html.indexOf('const SHOW_MANIFEST='),to=html.indexOf('function safeFilePart(',from);
assert(from>=0&&to>from,'Cannot inspect canonical assembler');
const ctx=vm.createContext({});
vm.runInContext(html.slice(from,to)+';globalThis.api={assembleScene,visibleCharacterHandles,pageAssembly,applyOverlay,applyDialogueOverlay,normalizeOverlay};',ctx);
const {assembleScene:assemble,visibleCharacterHandles:visible,pageAssembly,applyOverlay,applyDialogueOverlay,normalizeOverlay}=ctx.api;
const catalog=json('data/shows.json');
const prefixes=['azure-reach','low-tide-signal','sunforge-outlaw','vikings-2026'];
const counts=Object.fromEntries(prefixes.map(x=>[x,{shows:0,pages:0,characters:0,visualDescriptions:0,factionsSkipped:0,dialogueItems:0}]));
const load=(f,encoding)=>encoding==='gzip-base64'
  ?JSON.parse(zlib.gunzipSync(Buffer.from(read(f).trim(),'base64')).toString('utf8'))
  :json(f);
const shelves=new Map();
function store(base){if(!shelves.has(base)){const s={};for(const key of ['characters','settings','regions','factions','direction','dialogue'])s[key+'.json']=json(base+'/'+key+'.json');shelves.set(base,s)}return shelves.get(base)}
function pagesFor(show){
 const base=show.basePath,configPath=base+'/'+(show.packageConfigFile||'assembler.json');
 const config={...(fs.existsSync(path.join(root,configPath))?json(configPath):{}),...show};
 const files=Array.isArray(config.scenesFiles)?config.scenesFiles:[config.scenesFile||'scenes.json'];
 let pages=files.flatMap(f=>normalizeOverlay(load(base+'/'+f)));
 if(config.excludeSceneIds?.length){const excluded=new Set(config.excludeSceneIds);pages=pages.filter(p=>!excluded.has(p.id))}
 for(const overlay of config.sceneOverlays||[]){
   let incoming=normalizeOverlay(load(base+'/'+overlay.file,overlay.encoding));
   if(overlay.includeIds?.length){const allow=new Set(overlay.includeIds);incoming=incoming.filter(x=>allow.has(x.id))}
   if(overlay.excludeIds?.length){const remove=new Set(overlay.excludeIds);incoming=incoming.filter(x=>!remove.has(x.id))}
   pages=applyOverlay(pages,incoming,overlay);
 }
 for(const overlay of config.dialogueOverlays||[])
   pages=applyDialogueOverlay(pages,normalizeOverlay(load(base+'/'+overlay.file,overlay.encoding)));
 if(config.includeIdPattern){const re=new RegExp(config.includeIdPattern);pages=pages.filter(p=>re.test(p.id||''))}
 return {pages,config};
}
for(const show of catalog){
 const prefix=prefixes.find(x=>show.id.startsWith(x));if(!prefix)continue;
 const c=counts[prefix];c.shows++;
 assert.equal(show.promptVisibleCastOnly,true,'Missing visible cast scoping for '+show.id);
 assert.equal(show.omitRoutineFactions,true,'Missing faction scoping for '+show.id);
 const {pages,config}=pagesFor(show),data={...store(show.basePath),__show:config};
 assert(pages.length>0,'No pages loaded for '+show.id);
 for(let index=0;index<pages.length;index++){
   const p=pages[index],text=assemble(p,data,index),mode=pageAssembly(p,config).characterMode;
   if(p.promptVisibleCastOnly===false)continue; // Explicit authored opt-out.
   const expected=mode==='none'?[]:Array.from(visible(p,data['characters.json']));
   const pos=text.indexOf('\n=== ');
   const actual=pos<0?[]:text.slice(0,pos).split('\n').map(x=>x.trim()).filter(Boolean);
   assert.deepEqual(actual,expected,'Visual reference list disagrees with page cast on '+p.id);
   assert.equal(new Set(actual).size,actual.length,'Duplicate visual character '+p.id);
   assert(!text.includes('\n[CAST]\n')&&!text.includes('\n[CHARACTERS]\n'),'Duplicate cast prose on '+p.id);
   if(!p.promptIncludeFactions)assert(!text.includes('\n[FACTIONS]\n'),'Unnecessary faction text on '+p.id);
   if(p.factions?.length&&!p.promptIncludeFactions)c.factionsSkipped++;
   if(p.panelPlan?.length)assert(text.includes('\n[PANEL PLAN]\n'),'Lost panels on '+p.id);
   for(const d of p.dialogueInline||[]){
     assert(text.includes('"'+d.text+'"'),'Dialogue text omitted '+p.id);
     c.dialogueItems++;
   }
   for(const key of p.dialog||[]){
     const d=data['dialogue.json'][key];if(d){assert(text.includes('"'+d.text+'"'),'Legacy dialogue text omitted '+p.id);c.dialogueItems++;}
   }
   c.characters+=actual.length;
   c.visualDescriptions+=actual.filter(x=>x.includes(' — Visual: ')).length;
   c.pages++;
 }
}
for(const [prefix,c] of Object.entries(counts))assert(c.pages>0&&c.shows>=6,'Missing series coverage '+prefix);
const lts=catalog.find(s=>s.id==='low-tide-signal-c01'),lt=pagesFor(lts).pages.find(p=>p.characters?.length);
assert(lt,'Missing Low Tide example character page');
const ltsStore={...store(lts.basePath),__show:lts};
const ltsRecipe=assemble(lt,ltsStore,0);
assert(ltsRecipe.includes(' — Visual: '),'Low Tide cannot lose visual identity before approved image handles exist');
const sun=catalog.find(s=>s.id==='sunforge-outlaw-s1-e01');
const sunPages=pagesFor(sun).pages;
const sansHandle=sunPages.find(p=>(p.characters||[]).some(id=>!store(sun.basePath)['characters.json'][id]?.handle));
if(sansHandle){
 const recipe=assemble(sansHandle,{...store(sun.basePath),__show:sun},0);
 assert(recipe.includes(' — Visual: '),'Sunforge minor character requires visual identity');
}
const vik=catalog.find(s=>s.id==='vikings-2026-s1-e03');
const sample=pagesFor(vik).pages.find(p=>p.charactersInline?.length);
assert(sample,'Missing Viking inline-cast page');
const testScene={...sample,promptVisibleCharacters:[]};
const empty=assemble(testScene,{...store(vik.basePath),__show:vik},0);
assert(!empty.startsWith('@vik.'),'Empty visible cast must suppress visual references');
assert.throws(()=>assemble({...sample,promptVisibleCharacters:['not-an-identity']},{...store(vik.basePath),__show:vik},0),/Unknown visible character/);
console.log('PASS Four series visible-only reference mode (all registered issues and covers):');
for(const [name,c] of Object.entries(counts))console.log(name+': '+JSON.stringify(c));
console.log('PASS Low Tide/Sunforge text-only visual identity fallback; off-panel override; no changed script dialogue');
