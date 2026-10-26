#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),path=require('node:path'),os=require('node:os');
const {execFileSync}=require('node:child_process');
const root=path.resolve(__dirname,'..');
const source=fs.mkdtempSync(path.join(os.tmpdir(),'c3-sources-'));
const inventoryPath=path.join(source,'inventory.json');
execFileSync(process.execPath,[path.join(root,'tools/audit_all_series_production.cjs'),'--out',inventoryPath],{encoding:'utf8',maxBuffer:8*1024*1024});
const inventory=JSON.parse(fs.readFileSync(inventoryPath,'utf8'));
const visual=JSON.parse(fs.readFileSync(path.join(root,'production/audits/visual_review_2026-10-25.json'),'utf8'));
const draft=JSON.parse(fs.readFileSync(path.join(root,'production/drafts/manifest.json'),'utf8')).drafts;
const keeper=JSON.parse(fs.readFileSync(path.join(root,'production/references/reference-keeper-manifest.json'),'utf8')).references;
if(inventory.errors.length)throw Error('Underlying production inventory is invalid.');
if(inventory.configurations.length!==inventory.counts.loadedConfigurations)throw Error('Incomplete production configuration roster.');
const keeperBySeries={};
for(const v of Object.values(keeper))(keeperBySeries[v.seriesId]??=[]).push(v.id);
const draftByIssue={};
for(const v of Object.values(draft))(draftByIssue[v.seriesId+'::'+v.issueId]??=[]).push(v.recipeId);
const books=new Map(inventory.books.map(x=>[x.key,x]));
const findings=visual.findings.map(x=>({...x,sourceReviewed:true,artModified:false}));
// Only the three issues with established active approved-production recovery frontiers
// are actionable recovery findings. Other expected book units are production backlog,
// not defects and not proof their original IMG renders are missing.
const activeRecoveryIssues=new Set([
 'rex-fleet::rex-fleet-i03',
 'vikings-2026::vikings-2026-s1-e02',
 'stardust-station::stardust-station-e02'
]);
const unapprovedBookBacklog=[];
for(const b of inventory.books){
 const sep=b.key.indexOf('::'),seriesId=b.key.slice(0,sep),issueId=b.key.slice(sep+2);
 if(!activeRecoveryIssues.has(b.key)){
  for(const recipeId of b.missingUnits)unapprovedBookBacklog.push({seriesId,issueId,recipeId,status:'NOT_APPROVED_IN_REXPROMPT; NOT A DEFECT; OTHER SOURCE ART UNKNOWN'});
  continue;
 }
 for(const recipeId of b.missingUnits)findings.push({
  id:'BOOK-GAP::'+b.key+'::'+recipeId,type:'missing-approved-draft-record',
  severity:'P1-recovery-gate',seriesId,issueId,recipeId,
  observation:'Full-book inventory expects this unit; current approved-draft manifest has no entry. Historical IMG output may still exist.',
  requiredCorrection:'Recover original approved image and explicit approval evidence. Do not fabricate, regenerate, or mark approved during this audit.',
  sourceEvidence:['https://github.com/starsplitterrecords/RexPrompt/blob/main/production/book-manifests.json','https://github.com/starsplitterrecords/RexPrompt/blob/main/production/drafts/manifest.json'],
  sourceReviewed:true,artModified:false
 });
}
const issues=inventory.configurations.map(c=>{
 const samples=visual.inspectedReleasedPages.filter(x=>x.seriesId===c.seriesId);
 const scoped=findings.filter(f=>f.seriesId===c.seriesId&&(f.issueId===c.issueId||(c.showId==='backyard-rockets-s1'&&f.issueId?.startsWith('backyard-rockets-s1-'))));
 const book=books.get(c.seriesId+'::'+c.issueId)||null;
 return {...c,approvedDraftRecipeIds:draftByIssue[c.seriesId+'::'+c.issueId]||[],
 referenceIds:keeperBySeries[c.seriesId]||[],bookInventory:book,
 visualReview:c.seriesId==='sun-comes-through-musical'?'not-applicable-musical':samples.length?'sampled-released-only':'not-inspected',
 sampledPublishedIssues:samples.map(x=>({issue:x.issue,pages:x.pages,limitations:x.limitations})),
 relatedFindingIds:scoped.map(x=>x.id),completeVisualPass:false};
});
const report={
 schemaVersion:1,generatedAt:new Date().toISOString(),
 authority:'RexPrompt scripts/manifest; released StarSplitterVisions as immutable visual canon',
 disclaimer:'Absent RexPrompt draft records do not prove generated art is absent from historical IMG or published archives. Technical validation does not constitute creative approval.',
 counts:{...inventory.counts,sourceVerifiedActiveRecoveryGaps:findings.filter(x=>x.type==='missing-approved-draft-record').length,
  notYetApprovedBookUnits:unapprovedBookBacklog.length,
 publishedPagePaths:157,publishedEditions:6,actuallyInspectedReleasedPixels:visual.inspectedReleasedPages.reduce((n,x)=>n+x.pages.length,0)},
 series:inventory.series,issues,bookIssues:inventory.books,unapprovedBookBacklog,findings,
 inspectedReleasedPages:visual.inspectedReleasedPages,
 readbackLimitations:visual.pixelReadback,nonDefects:visual.verifiedNonDefects,
 mechanicalWarnings:inventory.warnings,mechanicalErrors:inventory.errors
};
const a=process.argv.indexOf('--output-dir');
const out=a>=0?path.resolve(process.argv[a+1]):path.join(source,'output');
fs.mkdirSync(out,{recursive:true});
fs.writeFileSync(path.join(out,'cross-series-production-quality-register.json'),JSON.stringify(report,null,2)+'\n');
const csv=v=>'"'+String(v??'').replace(/"/g,'""').replace(/\r?\n/g,' ')+'"';
const fields=['seriesId','showId','issueId','registeredUnits','approvedUnits','notInApprovedDraftManifest','visualReview','bookGaps','keeperReferences','exampleMissingRecipeIds'];
const lines=[fields.join(',')];
for(const row of issues)lines.push([row.seriesId,row.showId,row.issueId,row.registeredUnits,row.approvedUnits,row.notInApprovedDraftManifest,row.visualReview,row.bookInventory?.missingUnits?.length??'not-inventoried',row.referenceIds.length,row.examplesMissing?.join(' ')].map(csv).join(','));
fs.writeFileSync(path.join(out,'126-registered-production-configurations.csv'),lines.join('\n')+'\n');
const dfields=['id','severity','type','seriesId','issueId','recipeId','observation','requiredCorrection','sourceEvidence'];
const defect=[dfields.join(',')];
for(const f of findings)defect.push(dfields.map(k=>csv(Array.isArray(f[k])?f[k].join(' ; '):f[k])).join(','));
fs.writeFileSync(path.join(out,'defects-and-recovery-units.csv'),defect.join('\n')+'\n');
const md=['# Cross-series production and recovery register','','This report is generated from RexPrompt main. Creative pixels are only sample-inspected. No image is changed.','','| Series | Registered configuration | Units | Approved draft entries | Explicit book gaps | Pixel inspection |','| --- | --- | ---: | ---: | --- | --- |'];
for(const v of issues)md.push('| '+[v.seriesId,v.showId,v.registeredUnits,v.approvedUnits,v.bookInventory?v.bookInventory.missingUnits.length:'not inventoried',v.visualReview].join(' | ')+' |');
md.push('','## Page-/recipe-scoped findings');
for(const f of findings)md.push('- '+f.id+' / '+f.seriesId+' / '+f.issueId+' / '+f.recipeId+' / '+f.severity+' — '+f.observation+' Required: '+f.requiredCorrection);
md.push('','## Visual and approval limitations','','- '+visual.pixelReadback.approvedDrafts,'- '+visual.pixelReadback.keeper,'- '+visual.pixelReadback.historicalImg);
fs.writeFileSync(path.join(out,'126-issue-defect-and-continuity-register.md'),md.join('\n')+'\n');
console.log('C3 QUALITY REGISTER COUNTS '+JSON.stringify(report.counts));
console.log('ALL REGISTERED ISSUES '+issues.length+', TRACKED FINDINGS/RECOVERY GAPS '+findings.length);
console.log('PIXELS INSPECTED '+report.counts.actuallyInspectedReleasedPixels+' / 157 RELEASED PAGE PATHS');
console.log('OUT '+out);
