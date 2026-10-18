#!/usr/bin/env node
'use strict';
// Verify every new page-scope recipe profile against the *current* RexPrompt assembler.
// This compares each issue with and without the page-scoping overlay while keeping
// all authored story, dialogue, page-layout and other editorial overlays identical.
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8'),json=p=>JSON.parse(read(p));
const html=read('index.html'),begin=html.indexOf('const SHOW_MANIFEST='),end=html.indexOf('function safeFilePart(',begin);
assert(begin>=0&&end>begin,'Cannot locate live assembler');
const ctx=vm.createContext({});
vm.runInContext(html.slice(begin,end)+';globalThis.recipeFunctions={assembleScene,pageAssembly};',ctx);
const {assembleScene,pageAssembly}=ctx.recipeFunctions;
const catalog=json('data/shows.json');
const policyFile=f=>/^(editorial_recipe_scope_|editorial\/recipe_scope_)/.test(f||'');
const selected=catalog.filter(x=>x.sceneOverlays?.some(o=>policyFile(o.file)));
function decode(base,file,encoding){const p=base+'/'+file;
  return encoding==='gzip-base64'?JSON.parse(zlib.gunzipSync(Buffer.from(read(p).trim(),'base64')).toString('utf8')):json(p)}
function normalize(raw){if(Array.isArray(raw))return raw;if(Array.isArray(raw?.pages))return raw.pages;return Object.entries(raw||{}).map(([id,scene])=>({id,...scene}))}
function sceneEpisode(s){if(s?.episode)return s.episode;const m=String(s?.id||'').match(/^RF_(S1E\d{2})_/);return m?m[1]:null}
function overlay(scenes,incoming,o){
 if(o.mergeById){const patches=new Map(incoming.map(x=>[x.id,x]));return scenes.map(s=>patches.has(s.id)?{...s,...patches.get(s.id)}:s)}
 const t=o.replaceEpisodes?.length?o.replaceEpisodes:o.replaceEpisode?[o.replaceEpisode]:[];
 if(t.length){const set=new Set(t),first=scenes.findIndex(s=>set.has(sceneEpisode(s)));
  if(first>=0){const pos=scenes.slice(0,first).filter(s=>!set.has(sceneEpisode(s))).length;
    const keep=scenes.filter(s=>!set.has(sceneEpisode(s)));return keep.slice(0,pos).concat(incoming,keep.slice(pos));}}
 if(o.afterId){const pos=scenes.findIndex(s=>s.id===o.afterId);return scenes.slice(0,pos<0?scenes.length:pos+1).concat(incoming,scenes.slice(pos<0?scenes.length:pos+1))}
 return scenes.concat(incoming);
}
function load(show,applyScope){
 const base=show.basePath,files=show.scenesFiles?.length?show.scenesFiles:[show.scenesFile||'scenes.json'];
 let scenes=files.flatMap(f=>normalize(decode(base,f)));
 if(show.excludeSceneIds?.length){const x=new Set(show.excludeSceneIds);scenes=scenes.filter(p=>!x.has(p.id))}
 for(const x of show.sceneOverlays||[]){
   if(policyFile(x.file)&&!applyScope)continue;
   let items=normalize(decode(base,x.file,x.encoding));
   if(x.includeIds?.length){const set=new Set(x.includeIds);items=items.filter(v=>set.has(v.id))}
   if(x.excludeIds?.length){const set=new Set(x.excludeIds);items=items.filter(v=>!set.has(v.id))}
   scenes=overlay(scenes,items,x);
 }
 for(const x of show.dialogueOverlays||[]){
   const items=normalize(decode(base,x.file,x.encoding));
   const patches=new Map(items.map(a=>[a.id,a]));
   scenes=scenes.map(s=>{const d=patches.get(s.id);return d&&(d.dialogueInline||d.sceneDialogue)?{...s,dialogueInline:d.dialogueInline||d.sceneDialogue,dialogueSource:d.dialogueSource||'scene-dialogue overlay'}:s});
 }
 if(show.includeIdPattern){const re=new RegExp(show.includeIdPattern);scenes=scenes.filter(x=>re.test(String(x.id||'')))}
 return scenes;
}
const names=new Set(),idList=new Set(),counts={};
for(const show of selected){
 const base=show.basePath,source=load(show,false),scoped=load(show,true);
 assert.equal(source.length,scoped.length,'Scene count changed on '+show.id);
 const before=new Map(source.map(x=>[x.id,x])),after=new Map(scoped.map(x=>[x.id,x]));
 assert.equal(before.size,source.length,'Duplicate base scene id '+show.id);
 assert.equal(after.size,scoped.length,'Duplicate scoped scene id '+show.id);
 const store={__show:show};
 for(const file of ['characters','settings','regions','factions','dialogue','direction'])
   store[file+'.json']=json(base+'/'+file+'.json');
 let pages=0,bytes=0,suppressionCount=0;
 for(const entry of show.sceneOverlays.filter(x=>policyFile(x.file))){
   assert(entry.mergeById&&entry.strict,'Scope overlay must be strict ID merge '+show.id);
   const policies=normalize(decode(base,entry.file,entry.encoding));
   const unique=new Set();
   for(const item of policies){
     assert(item.id&&!unique.has(item.id),'Duplicate scope id '+entry.file);unique.add(item.id);
     const fields=Object.keys(item);
     assert(fields.every(x=>['id','promptSuppress','promptCharacterMode','promptSettingMode'].includes(x)),'Scope introduced a story or layout field '+item.id);
     assert(before.has(item.id)&&after.has(item.id),'Orphan scope record '+item.id);
     const a=before.get(item.id),b=after.get(item.id);
     assert.deepEqual(Object.keys(a).filter(x=>!fields.includes(x)).sort(),Object.keys(b).filter(x=>!fields.includes(x)).sort(),
       'A story ingredient key changed '+item.id);
     for(const f of ['panelPlan','dialogueInline','dialog','continuityFrom','pageLayout','directionInline','settingText','summary']){
       assert.equal(JSON.stringify(a[f]),JSON.stringify(b[f]),'Changed protected authored field '+item.id+' '+f);
     }
     const old=assembleScene(a,store,0),now=assembleScene(b,store,0);
     function protectedTail(txt){const first=txt.indexOf('\n[PAGE COMPOSITION]');const panel=txt.indexOf('\n[PANEL PLAN]');const pos=first>=0?first:panel;assert(pos>=0,'Missing panel plan '+item.id);return txt.slice(pos)}
     assert.equal(protectedTail(old),protectedTail(now),'Assembly changed protected story/layout/dialogue '+item.id);
     assert(now.length<=old.length+40,'Policy unexpectedly expanded prompt '+item.id);
     if(item.promptSettingMode==='label'&&b.setting&&!b.settingText)assert(store['settings.json'][b.setting]?.name,'Human-readable setting label missing '+item.id);
     pageAssembly(b,show);
     if(item.promptSuppress?.length)suppressionCount++;
     bytes+=old.length-now.length;pages++;
     idList.add(item.id);
   }
 }
 const group=show.id.replace(/(?:-e\d\d|-i\d\d|-c\d\d|-issue-\d+)$/,'');
 if(!counts[group])counts[group]={issues:0,profiles:0,savedCharacters:0,suppressions:0};
 counts[group].issues++;counts[group].profiles+=pages;counts[group].savedCharacters+=bytes;counts[group].suppressions+=suppressionCount;
 names.add(show.id);
}
assert.equal(selected.length,15,'Unexpected previously unfinished issue/chapter coverage');
assert([...Object.values(counts)].every(x=>x.savedCharacters>0),'No reference reduction in one or more series');
assert(!selected.some(x=>/^vikings-2026-s1/.test(x.id)),'Already-compact Vikings unexpectedly modified');
assert.equal(Object.keys(counts).length,3,'Expected only Rockets, Division Threshold, Stardust Issue 3');
console.log('PASS: '+selected.length+' scoped issue/chapter configurations across '+Object.keys(counts).length+' series; no source panels, dialogue, continuity, layout or scene count changed.');
for(const [series,x] of Object.entries(counts))console.log('PASS '+series+': '+x.issues+' issue/chapter targets, '+x.profiles+' profiles, '+x.savedCharacters+' prompt characters trimmed.');
console.log('PASS: source scripts immutable, protected chef ingredients identical; short names resolve from durable setting shelves.');
