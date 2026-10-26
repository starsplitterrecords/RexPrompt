'use strict';
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib'),assert=require('node:assert/strict');
const {inventory,build,seriesId,expand}=require('../production-dashboard-core.js');
function local(p,encoding){const b=fs.readFileSync(path.resolve(p));return JSON.parse(encoding==='gzip-base64'?zlib.gunzipSync(Buffer.from(b.toString('utf8').replace(/\s+/g,''),'base64')).toString('utf8'):b.toString('utf8'))}
(async()=>{
 const shows=local('data/shows.json'),books=local('production/book-manifests.json'),exportCoverage=local('production/book-export-coverage.json'),crossAudit=local('production/audits/visual_review_2026-10-25.json'),draft=local('production/drafts/manifest.json'),keepers=local('production/references/reference-keeper-manifest.json'),links=local('production/released-links.json'),qa=local('production/dashboard-source-quality.json'),recovery=local('production/dashboard-recovery-candidates.json');
 let count=0;const assembled=await inventory(shows,async(p,encoding)=>local(p,encoding),{onProgress:()=>count++});
 assert(assembled.length>=shows.length,'Cannot drop configured views');
 assert.equal(count,assembled.length,'Every expanded config must be inspected');
 const broken=assembled.filter(x=>x.sourceStatus!=='available');assert.deepEqual(broken.map(x=>[x.show.id,x.error]),[],'All current source packages must be readable and assembled');
 const out=build({shows,inventories:assembled,approvalManifest:draft,keeperManifest:keepers,bookManifest:books,releasedLinks:links,findings:[...qa.findings,...crossAudit.findings.map(x=>({seriesId:x.seriesId,issueId:x.issueId,recipeId:x.recipeId,kind:x.type,severity:x.severity,observation:x.observation,gate:x.requiredCorrection,evidence:x.sourceEvidence?.[0]}))],recovery:recovery.candidates,exportCoverage});
 assert.equal(out.summary.registryConfigurations,shows.length,'Show configuration is not a page count');
 assert.equal(out.summary.approvedDraftManifestEntries,Object.keys(draft.drafts).length);
 assert.equal(out.summary.keeperManifestEntries,Object.keys(keepers.references).length);
 assert(Object.keys(books.issues).length>=74,'Curated complete-book inventory must include newer portfolio audit');
 assert.equal(out.summary.unavailableConfigRows,0,'Never silently count unreadable recipes');
 assert(out.summary.assembledRecipeAssignments>out.summary.registryConfigurations*3,'Portfolio includes individual page recipes');
 const row=(s,id)=>out.rows.find(x=>x.seriesId===s&&x.issueId===id);
 for(const [id,n] of [['rex-fleet-i01',22],['rex-fleet-i02',24],['rex-fleet-i03',35]]){
  const x=row('rex-fleet',id);assert(x);assert.equal(x.requiredRecipes,n,'Curated full book inventory '+id);assert.equal(x.availableRecipes,n,'Assembler includes editorial, cover and story units '+id);assert.equal(x.additionalCuratedMissingFromAssembler.length,0);
 }
 assert.equal(row('rex-fleet','rex-fleet-i01').approvedDrafts,22);
 assert(row('rex-fleet','rex-fleet-i01').qualityFindings.some(x=>x.observation.includes('Ilyra Venn')),'Source-verified published canon disagreement must be carried into issue drilldown');
 assert(out.series.some(x=>x.id==='backyard-rockets'&&x.qualityFindings.some(f=>f.observation.includes('The Note')||f.observation.includes('editorial'))),'Cross-series provenance findings cannot be silently omitted');
 assert.equal(row('rex-fleet','rex-fleet-i02').approvedDrafts,24);
 const third=row('rex-fleet','rex-fleet-i03');
 assert.equal(third.approvedDrafts,30);
 assert.equal(third.exporterEvidence.status,'blocked-missing-images');
 assert.deepEqual(third.knownMissingApprovalIds,['RF_I03_P28','RF_I03_P29','RF_I03_P30','RF_I03_EDITOR_ENDMATTER','RF_I03_EDITOR_CLOSE']);
 assert.equal(row('rex-fleet','rex-fleet-i01').exporterEvidence.status,'complete-draft-export-supported');
 assert.equal(out.summary.sourceBackedExporterCoverage['complete-draft-export-supported'],3);
 assert.deepEqual(third.recipes.filter(x=>x.draftState!=='approved').map(x=>x.id),['RF_I03_P28','RF_I03_P29','RF_I03_P30','RF_I03_EDITOR_ENDMATTER','RF_I03_EDITOR_CLOSE']);
 assert.equal(third.unresolvedRecovery,5);
 const vik=row('vikings-2026','vikings-2026-s1-e02');assert(vik&&vik.requiredBasis==='curated-book'&&vik.recipeIds.includes('VIK_S1E02_P01'));
 const st=row('stardust-station','stardust-station-e02');assert(st&&st.requiredBasis==='curated-book'&&st.recipeIds.some(x=>x.endsWith('TEASER')));
 const azure=row('azure-reach','azure-reach-s1-e02');assert(azure&&azure.requiredBasis==='curated-book'&&azure.requiredRecipes===25&&azure.availableRecipes===24&&azure.approvedDrafts===11);
 assert(azure.externalSourceUnits.some(x=>x.sourceConfigurations.length),'Azure Issue 2 cover is sourced by another registered selector');
 assert.equal(azure.unavailableBookSourceIds.length,0,'Curated cover must not be labeled unavailable because it lives on a sibling cover shelf');
 assert.equal(st.requiredRecipes,25,'Stardust editorial/cover/teaser book denominator');
 assert(st.externalSourceUnits.some(x=>x.sourceConfigurations.length),'Stardust book cover source must be linked');
 assert.equal(st.unavailableBookSourceIds.length,0);
 assert(out.series.some(x=>x.id==='low-tide-signal'&&x.approvedDrafts===0&&x.recipeInventory>100));
 assert(out.series.some(x=>x.id==='echoes-forgotten-war'&&x.keeperRefs>=17));
 assert(out.series.some(x=>x.id==='division-threshold'&&x.approvedDrafts===0));
 assert(out.series.find(x=>x.id==='division-threshold').unresolvedRecoveryCandidates>=1,'Series-level unresolved sources cannot be dropped');
 assert(out.series.find(x=>x.id==='stardust-station').unresolvedRecoveryCandidates>=1,'Unverified Noola Library source remains a candidate');
 const released=build({shows,inventories:assembled,approvalManifest:draft,keeperManifest:keepers,bookManifest:books,releasedLinks:links,findings:qa.findings,recovery:recovery.candidates,releaseMetadata:{'rex-fleet':{releases:[{publicationType:'E',issueNumber:1,catalogId:'REX-E001-test',externalLink:'/issues/rex-fleet/issue-01/rex-fleet.pdf'}]}}});
 assert.equal(released.rows.find(x=>x.seriesId==='rex-fleet'&&x.issueId==='rex-fleet-i01').release.state,'published-record');
 assert.equal(released.rows.find(x=>x.seriesId==='rex-fleet'&&x.issueId==='rex-fleet-i01').export,'exported-pdf-record');
 assert.equal(released.rows.find(x=>x.seriesId==='rex-fleet'&&x.issueId==='rex-fleet-i02').release.state,'no-matching-edition','Do not publish working issue from sibling release');
 assert.equal(released.rows.find(x=>x.seriesId==='rex-fleet'&&x.issueId==='rex-fleet-i02').export,'unknown');
 assert(released.rows.find(x=>x.seriesId==='rex-fleet'&&x.issueId==='rex-fleet-i01').recipes.every(x=>x.mastering==='unknown'),'Published status must never back-fill artist mastering');
 assert(assembled.some(x=>x.show.id==='backyard-rockets-s1-issue-3'),'Multi-issue configuration must expand');
 assert(assembled.some(x=>x.show.id==='echoes-forgotten-war-s1-issue-8'),'Echoes season splits by issue');
 for(const x of out.rows){if(x.approvedDrafts===0)assert(!x.assetGate,'Zero drafts are not a completed book');assert.equal(x.mastering,'unknown');assert.equal(x.export,'unknown');}
 const sourceSets=new Map();
 for(const x of out.rows){const name=x.seriesId+'::'+x.issueId;if(sourceSets.has(name))console.warn('Duplicate configured issue ID across views: '+name);sourceSets.set(name,x)}
 console.log('PASSED '+JSON.stringify({registry:out.summary.registryConfigurations,expanded:out.summary.expandedConfigurations,individualRecipeAssignments:out.summary.assembledRecipeAssignments,series:out.summary.distinctSeries,approved:out.summary.approvedDraftManifestEntries,keeper:out.summary.keeperManifestEntries,examples:out.rows.filter(x=>['rex-fleet-i01','rex-fleet-i02','rex-fleet-i03','azure-reach-s1-e02','stardust-station-e02','vikings-2026-s1-e02'].includes(x.issueId)).map(x=>({issue:x.issueId,recipes:x.availableRecipes,required:x.requiredRecipes,approved:x.approvedDrafts,source:x.sourceStatus}))}));
})().catch(e=>{console.error(e.stack);process.exitCode=1});