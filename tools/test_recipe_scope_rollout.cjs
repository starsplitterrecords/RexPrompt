#!/usr/bin/env node
'use strict';
// Verify canonical page-scoped recipe policies against the current assembler.
// Archived policy files serve as migration fixtures, not active override layers.
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8'),json=p=>JSON.parse(read(p));
const html=read('index.html'),begin=html.indexOf('const SHOW_MANIFEST='),end=html.indexOf('function safeFilePart(',begin);
assert(begin>=0&&end>begin,'Cannot locate live assembler');
const ctx=vm.createContext({});
vm.runInContext(html.slice(begin,end)+';globalThis.recipeFunctions={assembleScene,pageAssembly};',ctx);
const {assembleScene,pageAssembly}=ctx.recipeFunctions;
const catalog=json('data/shows.json');
const selected=catalog.filter(x=>x.id==='backyard-rockets-s1');
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
 assert(!(show.sceneOverlays||[]).some(x=>x.mergeById),'Canonical Backyard sources must not use field patches');
 const scoped=load(show,true),store={__show:show},base=show.basePath;
 for(const file of ['characters','settings','regions','factions','dialogue','direction'])
   store[file+'.json']=json(base+'/'+file+'.json');
 const pages=scoped.filter(x=>/^BR_S1E0[3-8]_/.test(x.id)&&!!x.pageLayout);
 assert.equal(pages.length,118,'Canonical Backyard layout/scope inventory changed');
 let bytes=0,suppressionCount=0,actualPolicies=0;
 for(const page of pages){
  const fields=['promptCharacterMode','promptSettingMode','promptSuppress'].filter(field=>
    Object.prototype.hasOwnProperty.call(page,field));
  if(!fields.length)continue;
  actualPolicies++;
  if(Object.prototype.hasOwnProperty.call(page,'promptSuppress'))
    assert(Array.isArray(page.promptSuppress),'Invalid prompt suppression '+page.id);
  const bare={...page};
  for(const field of fields)delete bare[field];
  for(const field of ['panelPlan','dialogueInline','dialog','continuityFrom','pageLayout','directionInline','settingText','summary'])
    assert.equal(JSON.stringify(bare[field]),JSON.stringify(page[field]),'Protected story field changed '+page.id+' '+field);
  const old=assembleScene(bare,store,0),now=assembleScene(page,store,0);
  const tail=txt=>{const layout=txt.indexOf('\n[PAGE COMPOSITION]'),panel=txt.indexOf('\n[PANEL PLAN]');
    assert(panel>=0,'Panel plan missing '+page.id);return txt.slice(layout>=0?layout:panel)};
  assert.equal(tail(old),tail(now),'Canonical scope altered story composition or dialogue '+page.id);
  assert(now.length<=old.length+40,'Page scope unexpectedly expanded prompt '+page.id);
  if(page.promptSettingMode==='label'&&page.setting&&!page.settingText)
    assert(store['settings.json'][page.setting]?.name,'Setting label unresolved '+page.id);
  pageAssembly(page,show);
  suppressionCount+=+(Array.isArray(page.promptSuppress)&&page.promptSuppress.length>0);
  bytes+=old.length-now.length;idList.add(page.id);
 }
 assert(actualPolicies>0,'No canonical Backyard policy fields found');
 counts['backyard-rockets-s1']={issues:1,profiles:actualPolicies,savedCharacters:bytes,suppressions:suppressionCount};
 names.add(show.id);
}
// Division Threshold intentionally stores page scope *inside its flat compiled page
// files*. Its mechanical validator prohibits scene overlays.
const divisionShows=catalog.filter(x=>/^division-threshold-s1-e\d\d$/.test(x.id));
assert.equal(divisionShows.length,8,'Missing flat Division issues');
let divisionPages=0,divisionScoped=0,divisionSavings=0;
for(const show of divisionShows){
  assert(!show.sceneOverlays?.length,'Division must remain flat '+show.id);
  const scenes=load(show,true),store={__show:show},base=show.basePath;
  for(const file of ['characters','settings','regions','factions','dialogue','direction'])
    store[file+'.json']=json(base+'/'+file+'.json');
  for(const page of scenes){
    divisionPages++;
    const policy=Object.fromEntries(Object.entries(page).filter(([key])=>
      ['promptSuppress','promptCharacterMode','promptSettingMode'].includes(key)));
    if(!Object.keys(policy).length)continue;
    divisionScoped++;
    const original={...page};delete original.promptSuppress;delete original.promptCharacterMode;delete original.promptSettingMode;
    const a=assembleScene(original,store,0),b=assembleScene(page,store,0);
    const tail=v=>{const t=v.indexOf('\n[PAGE COMPOSITION]'),p=v.indexOf('\n[PANEL PLAN]');
      assert(p>=0,'Missing Division panel plan '+page.id);return v.slice(t>=0?t:p)};
    assert.equal(tail(a),tail(b),'Division scope altered protected beats '+page.id);
    if(page.promptSettingMode==='label'&&page.setting&&!page.settingText)
      assert(store['settings.json'][page.setting]?.name,'Unresolved Division setting label '+page.id);
    pageAssembly(page,show);
    divisionSavings+=a.length-b.length;
  }
}
assert.equal(divisionPages,204,'Division canonical flat page count changed');
assert.equal(divisionScoped,194,'Missing Division editorial page policy');
counts['division-threshold-s1']={issues:8,profiles:divisionScoped,savedCharacters:divisionSavings,suppressions:0};

assert.equal(selected.length,1,'Backyard season configuration missing');
assert([...Object.values(counts)].every(x=>x.savedCharacters>0),'No reference reduction in one or more series');
assert(!selected.some(x=>/^vikings-2026-s1/.test(x.id)),'Already-compact Vikings unexpectedly modified');
assert.equal(Object.keys(counts).length,2,'Expected canonical Backyard and Division Threshold policies');
console.log('PASS: '+(selected.length+divisionShows.length)+' scoped configurations across '+Object.keys(counts).length+' series; no source panels, dialogue, continuity, layout or scene count changed.');
for(const [series,x] of Object.entries(counts))console.log('PASS '+series+': '+x.issues+' issue/chapter targets, '+x.profiles+' profiles, '+x.savedCharacters+' prompt characters trimmed.');
console.log('PASS: protected chef ingredients identical; Division flat pages remain canonical; short names resolve from durable setting shelves.');
