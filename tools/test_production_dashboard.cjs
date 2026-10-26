'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),os=require('node:os'),path=require('node:path'),cp=require('node:child_process');
const {build}=require('../production-dashboard-core.js');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const tmp=path.join(os.tmpdir(),'rex-portfolio-audit-'+process.pid+'.json');
let inventory;
try{
 const p=cp.spawnSync(process.execPath,['tools/audit_all_series_production.cjs','--out',tmp],{encoding:'utf8',maxBuffer:12*1024*1024});
 assert.equal(p.status,0,'assembler source audit failed: '+p.stderr.slice(-5000));
 inventory=read(tmp);
}finally{fs.rmSync(tmp,{force:true})}
const qualityOut=path.join(os.tmpdir(),'rex-portfolio-image-'+process.pid+'.json');
let native;
try{
 const p=cp.spawnSync(process.execPath,['tools/build_portfolio_source_quality.cjs','--out',qualityOut],{encoding:'utf8',maxBuffer:12*1024*1024});
 assert.equal(p.status,0,'raster source audit failed: '+p.stdout+' '+p.stderr);
 native=read(qualityOut);
}finally{fs.rmSync(qualityOut,{force:true})}
const storedQuality=read('production/portfolio-source-quality.json');
assert.deepEqual(storedQuality,native,'Native source-quality snapshot is stale; regenerate from approved originals');
const snapshot=read('production/portfolio-recipe-inventory.json');
assert.deepEqual(snapshot,inventory,'Cached portfolio recipe IDs are stale; regenerate from assembler-aware source audit');
const shows=read('data/shows.json'),draftManifest=read('production/drafts/manifest.json'),
 refs=read('production/references/reference-keeper-manifest.json'),books=read('production/book-manifests.json'),
 released=read('production/released-links.json'),quality=read('production/portfolio-quality-evidence.json');
const visionsMetadata={
 'rex-fleet':{releases:[{issueNumber:1,publicationType:'E',catalogId:'REX-E001-2026-001',title:'Green Corridor',externalLink:'/issues/rex-fleet/issue-01/rex-fleet-issue-01-green-corridor.pdf'}]},
 'azure-reach':{releases:[{issueNumber:1,publicationType:'E',catalogId:'AZR-E001-2026-002',title:'Sea Turtle Thursdays',externalLink:'/issues/azure-reach/issue-01/book.pdf'}]},
 'vikings-2026':{releases:[{issueNumber:1,publicationType:'E',catalogId:'VIK-E001-2026-001',title:'Issue 01',externalLink:'/issues/vikings-2026/issue-01/book.pdf'}]},
 'stardust-station':{releases:[{issueNumber:1,publicationType:'E',catalogId:'SDS-E001-2026-001',title:'Mandatory Proximity',externalLink:'/issues/stardust-station/issue-01/book.pdf'}]},
 'backyard-rockets':{releases:[{issueNumber:1,publicationType:'E',catalogId:'BYR-E001-2026-001',title:'Issue 01',externalLink:'/issues/backyard-rockets/issue-01/book.pdf'},{issueNumber:2,publicationType:'E',catalogId:'BYR-E002-2026-002',title:'Issues 01–02 combined',externalLink:'/issues/backyard-rockets/issue-02/book.pdf'}]}
};
const model=build({shows,inventory,draftManifest,referenceManifest:refs,books,releasedLinks:released,qualityEvidence:quality,sourceQuality:native,visionsMetadata});
assert.equal(model.totals.registeredConfigurations,shows.length);
assert.equal(model.totals.approvedDraftManifestEntries,Object.keys(draftManifest.drafts).length);
assert.equal(model.totals.keeperReferences,Object.keys(refs.references).length);
assert(model.totals.distinctAssembledUnits>shows.length*4,'Recipe units should not equal configurations');
assert.equal(model.series.length,new Set(shows.map(x=>x.seriesId||x.basePath.split('/').at(-1).replace(/-s1$/,''))).size,'Every registered series represented');
const row=(s,id)=>model.rows.find(x=>x.seriesId===s&&x.issueId===id);
const rf1=row('rex-fleet','rex-fleet-i01'),rf2=row('rex-fleet','rex-fleet-i02'),rf3=row('rex-fleet','rex-fleet-i03');
assert.equal(rf1.denominator,22);assert.equal(rf1.denominatorSource,'curated-book');
assert.equal(rf2.denominator,24);
assert.equal(model.totals.sourceImagesAudited,Object.keys(draftManifest.drafts).length);
assert.equal(rf1.sourceQualitySummary.audited,22);
assert.equal(rf1.units.find(x=>x.recipeId==='RF_I01_P18').sourceQualityObservation.width,2400);
assert.equal(rf1.mastering,'native-review-required');
assert.equal(rf3.denominator,35);
assert.equal(rf3.approvedIndexed,30);
assert.deepEqual(rf3.units.filter(x=>x.inBook&&x.draftState!=='approved-draft-indexed').map(x=>x.recipeId),
 ['RF_I03_P28','RF_I03_P29','RF_I03_P30','RF_I03_EDITOR_ENDMATTER','RF_I03_EDITOR_CLOSE']);
assert(rf3.units.find(x=>x.recipeId==='RF_I03_EDITOR_ENDMATTER').recovery,'Preserved editorial source must be visible');
assert(rf3.units.some(x=>x.recipeId==='RF_I03_EDITOR_CLOSE'&&x.recovery),'Unmastered teaser source must remain visible');
assert.equal(rf1.published,'collected-edition-recorded');assert.equal(rf1.mastering,'native-review-required','Published book may still require native source review');
assert.equal(rf2.published,'no-matching-edition-record');
assert.equal(rf3.exported,'unverified');
const vk=row('vikings-2026','vikings-2026-s1-e02');
assert(vk&&vk.units.some(x=>x.recipeId==='VIK_S1E02_P01'),'Cover recipe required');
assert.equal(vk.denominator,23);
const sd=row('stardust-station','stardust-station-e02');
assert.equal(sd.denominator,25);
assert.equal(row('stardust-station','stardust-station').published,'collected-edition-recorded','Issue 1 published despite unsuffixed configuration ID');
assert(sd.units.some(x=>x.recipeId==='SDS_S1E02_TEASER'));
const az=model.rows.find(x=>x.seriesId==='azure-reach'&&x.issueId==='azure-reach-s1');
assert(az?.denominator>0,'Azure available assembled units must supply denominator');
assert.equal(az.denominatorSource,'curated-book');
assert.equal(az.denominator,25);
const az3=row('azure-reach','azure-reach-s1-e03');assert.equal(az3.denominator,25);assert.equal(az3.assembledCount,24,'Registered Azure Issue 3 should contain actual assembled recipes');
const excluded=shows.filter(x=>x.id!=='azure-reach-s1-e03');
const adjusted={...inventory,counts:{...inventory.counts,registeredConfigurations:excluded.length},configurations:inventory.configurations.filter(x=>x.showId!=='azure-reach-s1-e03')};
const synthetic=build({shows:excluded,inventory:adjusted,draftManifest,referenceManifest:refs,books,releasedLinks:released,qualityEvidence:quality,sourceQuality:native,visionsMetadata});
const bookOnly=synthetic.rows.find(x=>x.seriesId==='azure-reach'&&x.issueId==='azure-reach-s1-e03');
assert(bookOnly&&bookOnly.assembledCount===null,'Curated book without show must retain unknown recipe inventory');
assert.equal(bookOnly.denominator,25,'Book-only issue preserves exact complete-book requirements');
assert.equal(bookOnly.notIndexedCount,25,'Book-only issue must retain exact unindexed slots');
assert(az.units.some(x=>x.draftState!=='approved-draft-indexed'),'Unindexed means not stored here, not never generated');
const low=model.rows.find(x=>x.seriesId==='low-tide-signal');
assert(low?.denominator>0&&low.approvedIndexed===0,'Zero-draft registered series must be shown');
assert(low.units.every(x=>x.draftState==='not-indexed-in-RexPrompt'));
const back=model.rows.filter(x=>x.seriesId==='backyard-rockets');
assert(back.length>1,'Combined season must drill down to issues');
assert(back.some(x=>x.issueNumber===1&&x.releases.length),'Released issue must appear even with no draft manifest');
assert(back.some(x=>x.issueNumber===2&&x.releases.length),'Combined second edition must not disappear');
assert(model.rows.every(x=>x.mastering!=='mastered'),'Do not infer mastering approval');
assert(model.rows.every(x=>x.denominatorSource==='curated-book'||x.denominatorSource==='assembled-recipes'||x.denominatorSource==='no-assembled-configuration'));
for(const s of model.series){assert(s.distinctRecipeUnits>=0);assert(s.keeper.total>=0)}
assert.throws(()=>build({shows:shows.slice(1),inventory,draftManifest,referenceManifest:refs,books,releasedLinks:released}),/disagrees/);
console.log('PASS portfolio source snapshot freshness, all '+shows.length+' configurations, '+model.series.length+' series, '+model.totals.distinctAssembledUnits+' distinct recipes, five-page Rex gap, issue-specific books and published editions');
