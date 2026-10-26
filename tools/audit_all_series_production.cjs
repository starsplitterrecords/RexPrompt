#!/usr/bin/env node
'use strict';
// All-series production inventory from current RexPrompt configuration.
// Read-only. "Missing approved draft" is NOT proof artwork never existed in IMG,
// StarSplitterVisions, or other source-of-truth storage.
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const json=p=>JSON.parse(read(p));
const exists=p=>fs.existsSync(path.join(root,p));
const shows=json('data/shows.json');
const drafts=json('production/drafts/manifest.json').drafts;
const refs=json('production/references/reference-keeper-manifest.json').references;
const books=json('production/book-manifests.json').issues;
const released=json('production/released-links.json').links;
const visualSources=json('production/visual-sources.json').series;
const errors=[],warnings=[],rows=[],series=new Map();
assert(Array.isArray(shows),'data/shows.json must contain the registered show list');
function seriesId(show){
 if(show.seriesId)return show.seriesId;
 const base=path.basename(show.basePath||'');
 return base.replace(/-s1$/,'')||String(show.id).replace(/-(?:e\d\d|i\d\d|covers?)$/,'');
}
function normalizeScenes(value){
 if(Array.isArray(value))return value;
 return Object.entries(value||{}).map(([id,v])=>({id,...v}));
}
function normalizeOverlay(value){
 if(Array.isArray(value))return value;
 if(Array.isArray(value?.pages))return value.pages;
 return normalizeScenes(value);
}
function decode(base,filename,encoding){
 const p=path.posix.join(base,filename);
 if(!exists(p))throw Error('Missing recipe source '+p);
 if(encoding==='gzip-base64')return JSON.parse(zlib.gunzipSync(Buffer.from(read(p).trim(),'base64')).toString('utf8'));
 if(encoding&&encoding!=='json')throw Error('Unsupported source encoding '+encoding+' '+p);
 return json(p);
}
function sceneEpisode(s){
 if(s?.episode)return s.episode;
 const m=String(s?.id||'').match(/^RF_(S1E\d{2})_/);
 return m?m[1]:null;
}
function mergeById(scenes,incoming,overlay,showId){
 const updates=new Map(incoming.filter(x=>x?.id).map(x=>[x.id,x]));
 const seen=new Set();
 const merged=scenes.map(scene=>{const patch=updates.get(scene.id);
  if(!patch)return scene;
  seen.add(scene.id);
  return {...scene,...patch};
 });
 for(const p of incoming){
  if(!p?.id||seen.has(p.id)||scenes.some(s=>s.id===p.id))continue;
  if(overlay.strict)errors.push(showId+': strict overlay '+overlay.file+' has orphan recipe '+p.id);
  merged.push(p);
 }
 return merged;
}
function overlayScenes(scenes,incoming,overlay,showId){
 if(overlay.mergeById)return mergeById(scenes,incoming,overlay,showId);
 const targets=overlay.replaceEpisodes?.length?overlay.replaceEpisodes:(overlay.replaceEpisode?[overlay.replaceEpisode]:[]);
 if(targets.length){
  const set=new Set(targets),first=scenes.findIndex(s=>set.has(sceneEpisode(s)));
  if(first>=0){
   const at=scenes.slice(0,first).filter(s=>!set.has(sceneEpisode(s))).length;
   const kept=scenes.filter(s=>!set.has(sceneEpisode(s)));
   return kept.slice(0,at).concat(incoming,kept.slice(at));
  }
 }
 if(overlay.afterId){
  const index=scenes.findIndex(s=>s.id===overlay.afterId),at=index>=0?index+1:scenes.length;
  return scenes.slice(0,at).concat(incoming,scenes.slice(at));
 }
 return scenes.concat(incoming);
}
function loadShow(show){
 const base=show.basePath||'data';
 const packageFile=path.posix.join(base,show.packageConfigFile||'assembler.json');
 const pkg=exists(packageFile)?json(packageFile):{};
 const conf={...pkg,...show};
 const files=Array.isArray(conf.scenesFiles)?conf.scenesFiles:[conf.scenesFile||'scenes.json'];
 let scenes=files.flatMap(f=>normalizeScenes(decode(base,f)));
 if(conf.excludeSceneIds?.length){
  const exclude=new Set(conf.excludeSceneIds);
  scenes=scenes.filter(s=>!exclude.has(s.id));
 }
 for(const o of conf.sceneOverlays||[]){
  let incoming=normalizeOverlay(decode(base,o.file,o.encoding));
  if(o.includeIds?.length){const ids=new Set(o.includeIds);incoming=incoming.filter(s=>ids.has(s.id))}
  if(o.excludeIds?.length){const ids=new Set(o.excludeIds);incoming=incoming.filter(s=>!ids.has(s.id))}
  scenes=overlayScenes(scenes,incoming,o,show.id);
 }
 for(const o of conf.dialogueOverlays||[]){
  const patches=normalizeOverlay(decode(base,o.file,o.encoding));
  const byId=new Map(patches.filter(x=>x?.id).map(x=>[x.id,x]));
  scenes=scenes.map(s=>{const p=byId.get(s.id);if(!p)return s;
   const dialogue=p.dialogueInline||p.sceneDialogue;
   if(!Array.isArray(dialogue))return s;
   return {...s,dialogueInline:dialogue,dialogueSource:p.dialogueSource||'scene-dialogue overlay'};
  });
 }
 if(conf.includeIdPattern){
  const re=new RegExp(conf.includeIdPattern);
  scenes=scenes.filter(s=>re.test(String(s?.id||'')));
 }
 return scenes;
}
const approvalByIssue=new Map();
for(const [key,d] of Object.entries(drafts)){
 const issue=d.seriesId+'::'+d.issueId;
 if(!approvalByIssue.has(issue))approvalByIssue.set(issue,new Map());
 const m=approvalByIssue.get(issue);
 if(m.has(d.recipeId))errors.push('Duplicate approved recipe identity '+key);
 m.set(d.recipeId,d);
}
const keeperCounts={};
for(const r of Object.values(refs)){
 const s=r.seriesId||'(unknown)';
 if(!keeperCounts[s])keeperCounts[s]={total:0,character:0,setting:0,vehicle:0,item:0};
 keeperCounts[s].total++;
 if(keeperCounts[s][r.type]!==undefined)keeperCounts[s][r.type]++;
}
const releasedCounts={};
for(const k of Object.keys(released)){
 const sid=k.split('::')[0];
 releasedCounts[sid]=(releasedCounts[sid]||0)+1;
}
let aggregateUnits=0,aggregateCovered=0;
const sceneOwners=new Map();
for(const show of shows){
 let scenes;
 try{scenes=loadShow(show)}
 catch(e){errors.push(show.id+': cannot load registered recipes: '+e.message);continue}
 const sid=seriesId(show),issueId=show.issueId||show.id,issueKey=sid+'::'+issueId;
 const keys=new Set(),blank=[];
 for(const s of scenes){
  if(!s?.id||typeof s.id!=='string'){blank.push(s);continue}
  if(keys.has(s.id))errors.push(show.id+': duplicate recipe '+s.id);
  keys.add(s.id);
  const globalId=sid+'::'+s.id;
  const owner=sceneOwners.get(globalId);
  if(owner&&owner!==issueId)warnings.push('Recipe '+globalId+' appears in '+owner+' and '+issueId);
  else sceneOwners.set(globalId,issueId);
 }
 if(blank.length)errors.push(show.id+': '+blank.length+' scenes lack recipe IDs');
 if(!scenes.length)warnings.push(show.id+': registered configuration assembles zero recipes');
 const approved=approvalByIssue.get(issueKey)||new Map();
 let covered=0;
 for(const id of keys){if(approved.has(id))covered++}
 const extra=[...approved.keys()].filter(k=>!keys.has(k));
 if(extra.length)warnings.push(show.id+': '+extra.length+' approved draft IDs not in its assembled recipe list: '+extra.slice(0,5).join(', '));
 const row={showId:show.id,seriesId:sid,issueId,unitLabel:show.unitLabel||null,
  registeredUnits:keys.size,approvedUnits:covered,notInApprovedDraftManifest:Math.max(0,keys.size-covered),
  canonicalSource:'RexPrompt registered recipe',draftAuthority:'RexPrompt approved-draft manifest',
  examplesMissing:[...keys].filter(k=>!approved.has(k)).slice(0,8)};
 rows.push(row);
 aggregateUnits+=keys.size;aggregateCovered+=covered;
 if(!series.has(sid))series.set(sid,{seriesId:sid,registeredConfigurations:0,registeredUnits:0,approvedUnits:0,
  keeperReferences:keeperCounts[sid]?.total||0,releaseLinkRecords:releasedCounts[sid]||0,
  hasVisualSource:!!visualSources[sid],configurations:[]});
 const value=series.get(sid);value.registeredConfigurations++;value.registeredUnits+=row.registeredUnits;value.approvedUnits+=covered;
 value.configurations.push({showId:show.id,registeredUnits:row.registeredUnits,approvedUnits:covered});
}
const booksReport=[];
for(const [id,book] of Object.entries(books)){
 const units=book.units||[];
 const recorded=approvalByIssue.get(id)||new Map();
 const missing=units.filter(u=>!recorded.has(u));
 booksReport.push({key:id,expectedUnits:units.length,approvedUnits:units.length-missing.length,missingUnits:missing});
}
const report={
 generatedFrom:'RexPrompt manifests and loaded recipe sources; no image-pixel or IMG chat inspection',
 counts:{registeredConfigurations:shows.length,loadedConfigurations:rows.length,
  distinctSeries:series.size,registeredRecipeUnitsAcrossConfigurations:aggregateUnits,
  matchedApprovedUnitsAcrossConfigurations:aggregateCovered,
  approvedDraftRecords:Object.keys(drafts).length,keeperReferenceRecords:Object.keys(refs).length,
  releasedLinkRecords:Object.keys(released).length,completeBookInventories:Object.keys(books).length},
 series:[...series.values()].sort((a,b)=>a.seriesId.localeCompare(b.seriesId)),
 configurations:rows,books:booksReport,errors,warnings
};
const reportPath=process.argv.includes('--out')?process.argv[process.argv.indexOf('--out')+1]:null;
if(reportPath){
 fs.mkdirSync(path.dirname(reportPath),{recursive:true});
 fs.writeFileSync(reportPath,JSON.stringify(report,null,2)+'\n');
}
console.log('ALL-SERIES PRODUCTION INVENTORY: '+JSON.stringify(report.counts));
for(const x of report.series)console.log('SERIES '+x.seriesId+': '+x.registeredConfigurations+' registered configs / '+x.registeredUnits+' recipe units / '+x.approvedUnits+' matching draft records / '+x.keeperReferences+' Keeper assets / '+x.releaseLinkRecords+' RexPrompt release links');
for(const x of booksReport)console.log('BOOK '+x.key+': '+x.approvedUnits+'/'+x.expectedUnits+' approved; missing '+JSON.stringify(x.missingUnits));
for(const e of errors)console.error('ERROR '+e);
for(const e of warnings)console.log('WARN '+e);
console.log('BOUNDARY: approved draft count is NOT an estimate of created IMG artwork, released canon, visual continuity, lettering quality, or print-ready mastering.');
if(errors.length)process.exitCode=1;
