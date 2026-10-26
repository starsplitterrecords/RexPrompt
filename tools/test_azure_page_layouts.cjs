#!/usr/bin/env node
'use strict';
// Azure Reach Phase B: mechanical proof that layouts attach to existing
// story pages without altering released or approved artwork or story content.
const fs=require('node:fs');
const path=require('node:path');
const zlib=require('node:zlib');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const read=f=>fs.readFileSync(path.join(root,f),'utf8');
const json=f=>JSON.parse(read(f));
const manifest=json('data/shows.json');
const allShows=manifest.filter(s=>/^azure-reach-s1(?:-e0[2-6])?$/.test(s.id));
assert.equal(allShows.length,6);
const drafts=json('production/drafts/manifest.json').drafts;
const approved=new Set(Object.values(drafts).filter(x=>x.seriesId==='azure-reach'&&x.status==='approved-production-draft').map(x=>x.recipeId));
const publicSeries=json('data/shows/azure-reach-s1/covers.json');
assert(publicSeries.some(c=>c.id==='AZR_S1E01_COVER'),'Published first-issue cover missing');
const html=read('index.html'),start=html.indexOf('const SHOW_MANIFEST='),end=html.indexOf('function safeFilePart(',start);
assert(start>=0&&end>start,'Live assembler not available');
const sandbox=vm.createContext({});
vm.runInContext(html.slice(start,end)+';globalThis.editorial={assembleScene,validatePageLayout,pageLayoutWarnings};',sandbox);
const {assembleScene:assemble,validatePageLayout:validate,pageLayoutWarnings:warn}=sandbox.editorial;
const base='data/shows/azure-reach-s1';
const store={};
for(const f of ['characters','dialogue','settings','regions','factions','direction'])store[f+'.json']=json(base+'/'+f+'.json');
function decoded(file,encoding){
 if(encoding==='gzip-base64')return JSON.parse(zlib.gunzipSync(Buffer.from(read(base+'/'+file).trim(),'base64')).toString('utf8'));
 return json(base+'/'+file);
}
function extractedPages(show){
 const result=[];
 for(const overlay of show.sceneOverlays||[]){
  if(overlay.file.includes('/pages_e0')||/^encoded\/pages_e0/.test(overlay.file)){
   const value=decoded(overlay.file,overlay.encoding);
   assert(Array.isArray(value),'Malformed authored page payload '+overlay.file);
   result.push(...value);
  }
 }
 return result;
}
const combined=new Set(),categories=new Set();
// Pages P09/P10 were approved later, after their layout overlays already existed.
// The original protected nine were approved *before* this composition rollout.
const originalProtected=new Set(['AZR_S1E02_P01','AZR_S1E02_P02','AZR_S1E02_P03','AZR_S1E02_P04','AZR_S1E02_P05','AZR_S1E02_P06','AZR_S1E02_P07','AZR_S1E02_P08','AZR_S1E02_P11']);
const expectedApproved=new Set([...originalProtected,'AZR_S1E02_P09','AZR_S1E02_P10']);
assert.deepEqual([...approved].sort(),[...expectedApproved].sort(),'Approved page roster changed; review before modifying');
let authored=0,warnings=0;const perIssue={};
for(let n=1;n<=6;n++){
 const issue='e'+String(n).padStart(2,'0'),show=allShows.find(s=>s.id===(n===1?'azure-reach-s1':'azure-reach-s1-'+issue));
 assert(show,'Missing issue '+issue);
 const pages=extractedPages(show);
 assert.equal(pages.length,22,issue+' script length changed');
 assert.equal(new Set(pages.map(p=>p.id)).size,22,issue+' duplicate script IDs');
 if(n===1){
  assert(!show.sceneOverlays.some(o=>/page_layouts_/.test(o.file)),'Released Issue 1 should not be changed');
  assert(pages.every(p=>p.pageLayout===undefined),'Published page gained new unapproved layout');
  perIssue[issue]={pages:pages.length,scoped:0};
  continue;
 }
 const file='editorial/page_layouts_'+issue+'.json';
 const overlays=show.sceneOverlays||[];
 const ix=overlays.findIndex(o=>o.file===file);
 assert(ix>=0,'Missing registered layout overlay '+issue);
 assert(overlays[ix].mergeById,'Layout overlay must use mergeById');
 assert(ix===overlays.length-1,'Layout overlay must come after all story data '+issue);
 const scope=json(base+'/'+file),pageIds=new Set(pages.map(p=>p.id));
 assert.equal(scope.length,new Set(scope.map(o=>o.id)).size,'Duplicate layout scope '+issue);
 const byId=new Map(scope.map(x=>[x.id,x]));
 for(const id of byId.keys())assert(pageIds.has(id),'Layout target not found in source '+id);
 let scoped=0,skipped=0;
 for(let i=0;i<pages.length;i++){
  const page=pages[i],profile=byId.get(page.id),locked=originalProtected.has(page.id);
  if(locked){
   assert(!profile,'Approved production draft must remain untouched '+page.id);
   skipped++;
  }else assert(profile,'Unapproved Azure production page lacks layout '+page.id);
  if(!profile)continue;
  assert.deepEqual(Object.keys(profile).sort(),['id','pageLayout'],'Scope may only add pageLayout to '+page.id);
  const joined={...page,...profile};
  assert.equal(profile.id,page.id);
  assert.equal(validate(joined),profile.pageLayout);
  assert.equal(profile.pageLayout.panels.length,page.panelPlan.length,'Unbalanced panel hierarchy '+page.id);
  const context={...store,__show:show};
  const before=assemble(page,context,i),after=assemble(joined,context,i);
  const p='\n[PANEL PLAN]';
  assert(after.includes('[PAGE COMPOSITION]'),'Missing emitted composition '+page.id);
  assert(after.indexOf('[PAGE COMPOSITION]')<after.indexOf('[PANEL PLAN]'),'Layout order '+page.id);
  assert.equal(before.split(p)[0],after.split('\n[PAGE COMPOSITION]')[0],'Upstream recipe changed '+page.id);
  assert.equal(before.slice(before.indexOf(p)),after.slice(after.indexOf(p)),'Panel/dialogue/continuity changed '+page.id);
  for(const d of page.dialogueInline||[])assert(after.includes(d.text),'Missing dialogue '+page.id);
  assert(!combined.has(page.id),'Duplicate page scope across issues '+page.id);
  combined.add(page.id);categories.add(profile.pageLayout.composition);authored++;scoped++;
  warnings+=warn(joined).length;
 }
 perIssue[issue]={pages:22,scoped,approvedSkipped:skipped};
}
assert.equal(authored,101,'Expected exactly 101 non-locked Azure pages with new pageLayout');
assert(categories.size>=7,'Expected page-architecture diversity across Azure Reach');
console.log('PASS Azure Reach: '+authored+' validated page-specific compositions, '+categories.size+' architectures, no missing script content');
console.log('PASS release lock: 22 published Issue 1 pages and '+approved.size+' approved Issue 2 drafts not modified');
console.log('PASS page counts unchanged: '+JSON.stringify(perIssue));
console.log('INFO non-blocking layout density advisories: '+warnings);
