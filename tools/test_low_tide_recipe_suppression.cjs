#!/usr/bin/env node
'use strict';
// Tests data scoping, not dramatic choices. Authored page content is immutable.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),zlib=require('node:zlib');
const root=path.resolve(__dirname,'..');
const read=f=>fs.readFileSync(path.join(root,f),'utf8'),json=f=>JSON.parse(read(f));
const html=read('index.html'),start=html.indexOf('const SHOW_MANIFEST='),end=html.indexOf('function safeFilePart(',start);
assert(start>=0&&end>start,'Current RexPrompt assembler unavailable');
const scope=vm.createContext({});
vm.runInContext(html.slice(start,end)+';globalThis.api={assembleScene,validatePageLayout,applyOverlay,applyDialogueOverlay,normalizeOverlay};',scope);
const {assembleScene:assemble,validatePageLayout:valid,applyOverlay,applyDialogueOverlay,normalizeOverlay}=scope.api;
const shows=json('data/shows.json'),totals={pages:0,scoped:0,summary:0,cast:0,settings:0,fullCast:0,saved:0},reports=[];
function unpack(file,encoding){
 const data=read(file);
 return encoding==='gzip-base64'?JSON.parse(zlib.gunzipSync(Buffer.from(data.trim(),'base64')).toString('utf8')):JSON.parse(data);
}
function clean(obj){return JSON.parse(JSON.stringify(obj));}
function withoutAssemblyFields(p){
 const copy=clean(p);delete copy.promptSuppress;delete copy.promptCharacterMode;delete copy.promptSettingMode;return copy;
}
function verify(show){
 const base=show.basePath,configFile=base+'/assembler.json',config={...(fs.existsSync(path.join(root,configFile))?json(configFile):{}),...show};
 const profilePath=(config.sceneOverlays||[]).find(x=>/page_assembly_profiles_(?:c|e)\d\d\.json$/.test(x.file));
 assert(profilePath,'Missing assembly profile for '+show.id);
 assert(profilePath.mergeById&&profilePath.strict,'Assembly profiles must be strict ID merges: '+show.id);
 const originalProfile=normalizeOverlay(unpack(base+'/'+profilePath.file,profilePath.encoding));
 assert.equal(new Set(originalProfile.map(x=>x.id)).size,originalProfile.length,'Duplicate profile IDs');
 const ids=new Set(originalProfile.map(x=>x.id));
 let stages=[];
 const shelfFiles=['characters','settings','regions','factions','direction','dialogue'];
 const store={__show:config};
 for(const f of shelfFiles)store[f+'.json']=json(base+'/'+f+'.json');
 const files=Array.isArray(config.scenesFiles)?config.scenesFiles:[config.scenesFile||'scenes.json'];
 for(const file of files)stages.push(...normalizeOverlay(unpack(base+'/'+file)));
 let pre=null,post=null;
 for(const overlay of config.sceneOverlays||[]){
   if(overlay.file===profilePath.file)pre=stages.map(clean);
   const incoming=normalizeOverlay(unpack(base+'/'+overlay.file,overlay.encoding));
   stages=applyOverlay(stages,incoming,overlay);
   if(overlay.file===profilePath.file)post=stages.map(clean);
 }
 // Additional layout overlays after the profiles must be retained for comparison.
 const active=stages.filter(p=>new RegExp(config.includeIdPattern).test(p.id));
 if(config.dialogueOverlays?.length){
  let final=active;
  for(const overlay of config.dialogueOverlays){
   const incoming=normalizeOverlay(unpack(base+'/'+overlay.file,overlay.encoding));
   final=applyDialogueOverlay(final,incoming);
  }
  stages=final;
 }else stages=active;
 assert(pre&&post,'Profile was not applied');
 const preMap=new Map(pre.map(p=>[p.id,p])),postMap=new Map(post.map(p=>[p.id,p]));
 const profMap=new Map(originalProfile.map(p=>[p.id,p]));
 assert(ids.size<=stages.length,'Too many page profiles in '+show.id);
 for(const id of ids)assert(stages.some(p=>p.id===id),'Orphaned profile '+id);
 let saved=0,scoped=0;
 for(const page of stages){
   if(!ids.has(page.id))continue; // The issue's editorial opener/teaser retains its existing recipe.
   const prior=preMap.get(page.id),effective=postMap.get(page.id),profile=profMap.get(page.id);
   assert(prior&&effective,'Incomplete page overlay '+page.id);
   const validKeys=['id','promptSuppress','promptCharacterMode','promptSettingMode'];
   for(const key of Object.keys(profile))assert(validKeys.includes(key),'Unauthorised story mutation key '+key+' on '+page.id);
   assert.deepEqual(withoutAssemblyFields(effective),withoutAssemblyFields(prior),'Source page or dialogue mutated on '+page.id);
   if(page.pageLayout)valid(page);
   // Compare the canonical chef output with profiles enabled vs disabled,
   // after all remaining overlays (including authored layout and dialogue) are applied.
   const original={...page};
   for(const k of ['promptSuppress','promptCharacterMode','promptSettingMode']){
      if(Object.prototype.hasOwnProperty.call(prior,k))original[k]=prior[k];else delete original[k];
   }
   const before=assemble(original,store,0),after=assemble(page,store,0);
   const cut=page.pageLayout?'\n[PAGE COMPOSITION]':'\n[PANEL PLAN]';
   const beforeIdx=before.indexOf(cut),afterIdx=after.indexOf(cut);
   assert(beforeIdx>=0&&afterIdx>=0,'Missing authored panel recipe '+page.id);
   assert.equal(after.slice(afterIdx),before.slice(beforeIdx),'Changed page layout, scripted panels, dialogue or continuity '+page.id);
   assert(after.length<=before.length,'Expanded chef recipe when reducing context '+page.id);
   saved+=before.length-after.length;
   if(page.promptSuppress?.includes('summary')){
      assert(page.pageLayout,'Never omit a summary without an alternative composition authority: '+page.id);
      assert(page.panelPlan?.length,'Never omit unique dramatic action: '+page.id);
      totals.summary++;
   }
   if(page.promptCharacterMode==='cast')totals.cast++;
   if(page.promptCharacterMode==='full')totals.fullCast++;
   if(page.promptSettingMode==='label')totals.settings++;
   scoped++;totals.pages++;
 }
 totals.scoped+=scoped;totals.saved+=saved;
 reports.push(show.id+': '+scoped+' pages, '+saved+' repeated chef characters removed');
}
for(let c=1;c<=7;c++)verify(shows.find(s=>s.id==='low-tide-signal-c'+String(c).padStart(2,'0')));
assert(totals.pages>=192,'Incomplete Low Tide chapter rollout');
assert(totals.saved>10000,'No meaningful decluttering in assembled recipes');
console.log('PASS Low Tide recipe suppression: '+JSON.stringify(totals));
console.log(reports.join('\n'));
