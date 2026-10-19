#!/usr/bin/env node
'use strict';
// Azure Reach: verify page-by-page, story-preserving chef-context sanitation.
// Authoritative compressed scenes and approved published/production art remain untouched.
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8'),json=p=>JSON.parse(read(p));
const shows=json('data/shows.json'),drafts=json('production/drafts/manifest.json').drafts,settings=json('data/shows/azure-reach-s1/settings.json');
const approved=new Set(Object.values(drafts).filter(d=>d.seriesId==='azure-reach'&&d.status==='approved-production-draft').map(d=>d.recipeId));
assert.equal(approved.size,9,'Approved roster changed; review locks explicitly');
const html=read('index.html'),start=html.indexOf('const SHOW_MANIFEST='),end=html.indexOf('function safeFilePart(',start);
assert(start>=0&&end>start,'Canonical browser assembler source unavailable');
const sandbox=vm.createContext({});
vm.runInContext(html.slice(start,end)+';globalThis.chef={assembleScene,pageAssembly,validatePageLayout};',sandbox);
const {assembleScene:assemble,pageAssembly,validatePageLayout:validate}=sandbox.chef;
const base='data/shows/azure-reach-s1';
const store={};
for(const f of ['characters','dialogue','settings','regions','factions','direction'])store[f+'.json']=json(base+'/'+f+'.json');
function decoded(o){
 const file=read(base+'/'+o.file).trim();
 return o.encoding==='gzip-base64'?JSON.parse(zlib.gunzipSync(Buffer.from(file,'base64')).toString('utf8')):JSON.parse(file);
}
function storyPages(show){
 return show.sceneOverlays.filter(x=>/^encoded\/pages_e0/.test(x.file)).flatMap(o=>decoded(o));
}
function section(prompt,name){
 const marker='\n['+name+']',index=prompt.indexOf(marker);
 if(index<0)return null;
 const tail=prompt.slice(index+marker.length),next=tail.search(/\n\[[A-Z][A-Z _&/-]*\]/);
 return (next>=0?tail.slice(0,next):tail).trim();
}
let total=0,removed=0,changedDirection=0,removedInline=0,compact=0,full=0,removedSummaries=0;
for(let number=1;number<=6;number++){
 const issue='e0'+number,id=number===1?'azure-reach-s1':'azure-reach-s1-'+issue;
 const show=shows.find(x=>x.id===id);assert(show,'Missing Azure '+issue);
 const pages=storyPages(show);assert.equal(pages.length,22,'Unexpected comic length '+issue);
 assert.equal(new Set(pages.map(p=>p.id)).size,22,'Duplicate story IDs '+issue);
 const overlays=show.sceneOverlays||[];
 if(number===1){assert(!overlays.some(o=>/page_recipe_scopes_/.test(o.file)),'Published Issue 1 received sanitation overlay');continue;}
 const fname='editorial/page_recipe_scopes_'+issue+'.json';
 const pos=overlays.findIndex(o=>o.file===fname),layout=overlays.findIndex(o=>o.file==='editorial/page_layouts_'+issue+'.json');
 assert(pos>=0&&layout===pos+1,'Suppression must load directly before layout on '+issue);
 assert(overlays[pos].mergeById&&overlays[pos].strict,'Strict ID merge missing '+issue);
 const scopes=json(base+'/'+fname),compositions=json(base+'/editorial/page_layouts_'+issue+'.json');
 const map=new Map(scopes.map(p=>[p.id,p])),layoutMap=new Map(compositions.map(p=>[p.id,p]));
 assert.equal(scopes.length,number===2?13:22,'Missing scope records '+issue);
 assert.equal(scopes.length,map.size,'Duplicate scope IDs '+issue);
 const sourceIds=new Set(pages.map(p=>p.id));
 assert([...map.keys()].every(x=>sourceIds.has(x)),'Orphan scope '+issue);
 const seenSettings=new Set();
 let issueBefore=0,issueAfter=0,issueCount=0;
 for(let index=0;index<pages.length;index++){
  const p=pages[index],patch=map.get(p.id),lay=layoutMap.get(p.id);
  if(approved.has(p.id)){assert(!patch,'Approved art page modified '+p.id);continue;}
  assert(patch&&lay,'Missing page scope or layout '+p.id);
  for(const key of Object.keys(patch))assert(['id','promptCharacterMode','promptSettingMode','promptSuppress','direction','directionInline'].includes(key),'Extraneous production patch '+key+' on '+p.id);
  assert.equal(patch.id,p.id);
  assert.equal(patch.promptSettingMode==='full'||patch.promptSettingMode==='label',true,'Invalid setting mode');
  assert.equal(patch.promptCharacterMode==='full'||patch.promptCharacterMode==='cast',true,'Invalid cast mode');
  assert(patch.promptSuppress.includes('region')&&patch.promptSuppress.includes('factions'),'Persistent boilerplate leaked '+p.id);
  assert(!patch.promptSuppress.some(x=>['production','setting','characters','direction','continuity'].includes(x)),'Protected essential section suppressed '+p.id);
  if(!seenSettings.has(p.setting))assert.equal(patch.promptSettingMode,'full','First location description lost '+p.id);
  seenSettings.add(p.setting);
  if(patch.promptSettingMode==='label'){
   const label=settings[p.setting]?.name;
   assert(typeof label==='string'&&label.trim()&&!label.startsWith('AZR_'),'Unrenderable setting label '+p.id);
   compact++;
  }else full++;
  const beforeScene={...p,...lay},afterScene={...beforeScene,...patch};
  validate(afterScene);pageAssembly(afterScene,show);
  const context={...store,__show:show};
  const before=assemble(beforeScene,context,index),after=assemble(afterScene,context,index);
  for(const key of ['PAGE COMPOSITION','PANEL PLAN','DIALOGUE','CONTINUITY'])
   assert.equal(section(after,key),section(before,key),key+' changed on '+p.id);
  for(const line of p.dialogueInline||[])assert(after.includes(line.text),'Scripted line omitted on '+p.id);
  assert(section(after,'SETTING')!==null,'Location lost '+p.id);
   assert(!after.includes('[CAST]')&&!after.includes('[CHARACTERS]'),'Duplicate cast prose leaked '+p.id);
   const refs=after.split('\n').filter(x=>/^@azr\.[A-Za-z0-9_-]+$/.test(x));
   const expected=(p.characters||[]).map(id=>store['characters.json'][id]?.handle).filter(Boolean);
   assert.deepEqual(refs,expected,'Page-specific art references lost or duplicated '+p.id);
  assert(!after.includes('[FACTIONS]')&&!after.includes('[REGION]'),'Unnecessary shelf repetition on '+p.id);
  if(patch.promptSuppress.includes('summary')){removedSummaries++;assert(!after.includes(p.summary),'Redundant summary leaked '+p.id);}
  assert(!patch.direction.includes('AZR_PRODUCTION_CORE')&&!patch.direction.includes('AZR_LETTERING'),'Repeated generic direction leaked '+p.id);
  assert(patch.direction.every(x=>p.direction?.includes(x)),'Unapproved direction key added to '+p.id);
  if(patch.directionInline!==undefined){
   assert.deepEqual(patch.directionInline,[],'Direction cleanup must only remove redundant inline instructions');
   assert.equal(p.directionInline?.length,1,'Non-trivial direction stripped '+p.id);
   removedInline++;
  }
  if(patch.direction.length!==p.direction.length)changedDirection++;
  assert(after.length<before.length,'Scope made recipe longer '+p.id);
  issueBefore+=before.length;issueAfter+=after.length;issueCount++;total++;
 }
 assert.equal(issueCount,number===2?13:22,'Unexpected issue scoped count '+issue);
 removed+=issueBefore-issueAfter;
 console.log('PASS Azure '+issue+': '+issueCount+' scoped pages, saved '+(issueBefore-issueAfter)+' prompt characters; exact layout, panels, dialogue and continuity preserved');
}
assert.equal(total,101);
assert(compact>=20&&full>=35,'Location reference planning missing');
assert(changedDirection>=95,'Repeated generic direction not removed broadly');
assert(removedSummaries>=60,'Redundant prose suppression incomplete');
assert(removed>30000,'No meaningful issue-wide prompt decluttering');
console.log('PASS Azure recipe sanitation: '+total+' pages, '+removed+' saved prompt characters, '+compact+' compact settings, '+full+' detailed settings, '+removedSummaries+' summaries suppressed, '+changedDirection+' repeated direction groups trimmed, '+removedInline+' redundant inline directions removed');
console.log('PASS: 22 published Issue 1 pages and 9 approved Issue 2 drafts excluded; issue lengths and authored story data unchanged');
