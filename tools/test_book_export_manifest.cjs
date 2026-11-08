'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),cp=require('node:child_process');
const shows=JSON.parse(fs.readFileSync('data/shows.json','utf8')),inv=JSON.parse(fs.readFileSync('production/book-manifests.json','utf8')),coverage=JSON.parse(fs.readFileSync('production/book-export-coverage.json','utf8')),drafts=JSON.parse(fs.readFileSync('production/drafts/manifest.json','utf8')).drafts,exporter=fs.readFileSync('issue-publishing.js','utf8');
const structure=JSON.parse(fs.readFileSync('production/issue-structure.json','utf8'));
const structures=Object.values(structure.issues);
const curated=structures.filter(x=>x.readingOrder==='curated-complete-book');
const derived=structures.filter(x=>!x.selectorRegistered);
assert.equal(curated.length,Object.keys(inv.issues).length,'Every curated book must have an issue structure');
const seasonAggregates=coverage.entries.filter(x=>x.kind==='multi-issue-season-selector');
assert.equal(derived.length,seasonAggregates.reduce((n,row)=>n+row.subissues.filter(x=>!x.issueSelectorRegistered).length,0),
 'Virtual season issues must be omitted when real issue selectors exist');
for(const season of seasonAggregates){
 for(const part of season.subissues){
  if(!part.issueSelectorRegistered)continue;
  const episode=season.selectorId+'-e'+part.sourceGroup.slice(-2);
  const key=season.seriesId+'::'+episode;
  assert.ok(structure.issues[key]?.selectorRegistered,'Registered episode missing source-backed issue structure '+key);
  assert.ok(inv.issues[key],'Registered episode missing curated book order '+key);
  assert.equal(inv.issues[key].units[0],part.sourceGroup+'_COVER','Cover must lead episode '+key);
 }
}
for(const issue of structures){
 assert.equal(issue.sourceUnitCount>0,true,'Empty issue structure '+issue.issueId);
 const ids=issue.specialUnits.map(x=>x.unitId);
 assert.equal(new Set(ids).size,ids.length,'Duplicate special unit '+issue.issueId);
 if(issue.coverStatus==='ordered')assert.ok(issue.specialUnits.some(x=>x.role==='cover'&&x.position===1),'Unverified cover order '+issue.issueId);
 if(issue.coverStatus==='available-in-separate-shelf')assert.ok(issue.separateCoverCandidates?.length,'Unavailable cover candidate '+issue.issueId);
 if(issue.readingOrder==='curated-complete-book')assert.equal(issue.coverStatus,'ordered','Curated issue must establish a cover '+issue.issueId);
}
const registered=new Set(shows.map(s=>s.id));
assert.equal(structure.schemaVersion,1);

assert.equal(inv.schemaVersion,1);
assert.equal(coverage.registrySelectors,shows.length);
assert.equal(coverage.entries.length,shows.length);
assert.equal(coverage.issuesWithManifest,Object.keys(inv.issues).length);
assert.equal(new Set(coverage.entries.map(r=>r.selectorId)).size,shows.length);
for(const [key,book] of Object.entries(inv.issues)){
 assert.equal(key,book.seriesId+'::'+book.issueId);
 assert.ok(registered.has(book.issueId),'Unregistered issue '+key);
 assert.ok(Array.isArray(book.units)&&book.units.length,'Empty issue '+key);
 assert.equal(new Set(book.units).size,book.units.length,'Duplicate units '+key);
 const editorial=structure.issues[key];
 assert.ok(editorial,'Issue role inventory missing '+key);
 assert.equal(editorial.readingOrder,'curated-complete-book','Explicit curated status required '+key);
 assert.equal(editorial.sourceUnitCount,book.units.length,'Different source and editorial lengths '+key);
 for(const role of editorial.specialUnits){
  assert.equal(book.units[role.position-1],role.unitId,'Incorrect role position '+key+' '+role.unitId);
  assert.match(role.role,/^(cover|cast|opening-editorial|closing-editorial|teaser|end-matter|interstitial-document|opening-splash|title-splash)$/);
 }
 const covers=editorial.specialUnits.filter(x=>x.role==='cover');
 assert.equal(covers.length,1,'Every curated book has one evidenced cover '+key);
 assert.equal(covers[0].position,1,'Cover must be first '+key);
 const row=coverage.entries.find(e=>e.selectorId===book.issueId);
 assert.ok(row&&row.status!=='uncurated','Curated inventory must have coverage '+key);
 assert.equal(row.expectedUnits,book.units.length);
 assert.ok(row.approvedImages<=book.units.filter(id=>drafts[[book.seriesId,book.issueId,id].join('::')]?.status==='approved-production-draft').length,'Binary integrity cannot increase approved count');
 assert.equal(row.approvedImages+row.missingImageCount,book.units.length,'Every required unit must be counted as passing or blocked');
 const story=book.units.filter(x=>/_P\d+$/.test(x));
 for(let i=1;i<story.length;i++)assert.equal(+story[i].match(/_P(\d+)$/)[1],+story[i-1].match(/_P(\d+)$/)[1]+1,key+' story order '+story[i]);
}
assert.equal(Object.values(coverage.statuses).reduce((a,b)=>a+b,0),shows.length);
const ex=(series,issue)=>inv.issues[series+'::'+issue];
assert.deepEqual(ex('rex-fleet','rex-fleet-i02').units.slice(0,3),['RF_I02_COVER','RF_I02_EDITOR_OPEN','RF_I02_CAST']);
assert.deepEqual(ex('rex-fleet','rex-fleet-i03').units.slice(-2),['RF_I03_EDITOR_ENDMATTER','RF_I03_EDITOR_CLOSE']);
assert.equal(ex('vikings-2026','vikings-2026-s1-e02').units[0],'VIK_S1E02_P01');
assert.deepEqual(ex('stardust-station','stardust-station-e02').units.slice(0,2),['SDS_S1E02_COVER','SDS_S1E02_EDITOR']);
assert.equal(ex('stardust-station','stardust-station-e02').units.at(-1),'SDS_S1E02_TEASER');
function role(series,issue,id){return structure.issues[series+'::'+issue]?.specialUnits.find(x=>x.unitId===id)?.role||null}
assert.equal(role('vikings-2026','vikings-2026-s1-e01','VIK_S1I01_P01'),'cover');
assert.equal(role('vikings-2026','vikings-2026-s1-e01','VIK_S1I01_P02'),'opening-editorial');
assert.equal(role('vikings-2026','vikings-2026-s1-e01','VIK_S1I01_P18'),'closing-editorial');
for(let i=2;i<=12;i++){
 const issue='vikings-2026-s1-e'+String(i).padStart(2,'0');
 const key='VIK_S1E'+String(i).padStart(2,'0');
 assert.equal(role('vikings-2026',issue,key+'_P01'),'cover',issue+' embedded cover');
 assert.equal(role('vikings-2026',issue,key+'_P02'),'opening-editorial',issue+' embedded intro');
 const latest=inv.issues['vikings-2026::'+issue].units.at(-1);
 assert.ok(['teaser','closing-editorial'].includes(role('vikings-2026',issue,latest)),issue+' closing unit');
}
assert.equal(role('rex-fleet','rex-fleet-i02','RF_I02_CAST'),'cast');
assert.equal(role('rex-fleet','rex-fleet-i02','RF_I02_EDITOR_ENDMATTER'),'end-matter');
assert.equal(role('rex-fleet-academy-between-beacons','rex-fleet-academy-between-beacons-i01','RFA_BB_I01_P01'),'opening-editorial');
const fp=structure.issues['rex-fleet-full-performance::rex-fleet-full-performance-i01'];
assert.ok(fp&&fp.readingOrder==='source-order-only'&&fp.coverStatus==='not-established');
assert.equal(fp.specialUnits.filter(x=>x.role==='opening-editorial').length,7);
assert.equal(role('rex-fleet-full-performance','rex-fleet-full-performance-i01','RFFP_I01_CAST'),'cast');
for(let i=1;i<=12;i++){
 const num=String(i).padStart(2,'0'),issue='rex-fleet-full-performance-i'+num;
 assert.equal(inv.issues['rex-fleet-full-performance::'+issue].units[0],'RFFP_I'+num+'_COVER','Full Performance issue cover '+num);
}
for(const selector of ['rex-fleet-academy-anomalies-i01','rfa-reach-resolve-i01','rex-fleet-stormwell-archive-i01','rex-fleet-glass-horizon-i01','rex-fleet-academy-navigating-mirrorfold-i01','rex-fleet-academy-doctrine-many-crowns-i01','rex-fleet-academy-core-worlds-i01','rex-fleet-academy-physics-lattice-i01','rex-fleet-aegis-vigil-i01','rex-fleet-ghostwind-arrow-i01','rex-fleet-slip-knife-i01','rex-fleet-crimson-warden-i01']){
 const book=Object.values(inv.issues).find(b=>b.issueId===selector);
 assert.ok(book&&book.units[0].endsWith('_COVER'),'Missing distinct story-front cover '+selector);
}
for(const [series,prefix] of [['backyard-rockets','backyard-rockets-s1'],['echoes-forgotten-war','echoes-forgotten-war-s1']]){
 for(let i=1;i<=8;i++){
  const id=series+'::'+prefix+'-e'+String(i).padStart(2,'0');
  const entry=structure.issues[id];
  assert.ok(entry&&!entry.selectorRegistered&&entry.readingOrder==='source-order-only',id);
  assert.equal(entry.specialUnits[0].role,'opening-editorial');
  assert.equal(entry.specialUnits.at(-1).role,'closing-editorial');
 }
}
assert.equal(structure.issues['echoes-forgotten-war::echoes-forgotten-war-s1-e01'].coverStatus,'available-in-separate-shelf');
assert.match(exporter,/const ordered=book\?\.units\|\|sel\.recipeIds/);
assert.match(exporter,/issueIncludeCast/);
assert.match(exporter,/omittedOptionalUnits:p.omittedCast/);

assert.match(exporter,/-INCOMPLETE-DRAFT/);
assert.match(exporter,/-UNVERIFIED-BOOK-DRAFT/);
assert.match(exporter,/book-export-manifest\.json/);
assert.match(exporter,/if\(!p\.book\)throw Error\('Release blocked/);
assert.match(exporter,/MISSING_APPROVED_PAGES\.txt/);
const audit=cp.spawnSync(process.execPath,['tools/audit_portfolio_books.cjs','--check'],{encoding:'utf8'});
assert.equal(audit.status,0,'Source audit mismatch:\n'+audit.stderr+'\n'+audit.stdout.slice(0,2000));
console.log('PASS '+shows.length+' selectors audited, '+Object.keys(inv.issues).length+' book inventories: '+JSON.stringify(coverage.statuses));
