(function(root,factory){
 const api=factory();
 if(typeof module==='object'&&module.exports)module.exports=api;
 else root.RexProductionDashboard=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const key=(s,i,r)=>s+'::'+i+(r?'::'+r:'');
const indexed=(map,field)=>new Map(Object.values(map||{}).map(x=>[x[field],x]));
const distinct=a=>[...new Set(a)];
const nullish=x=>x===undefined||x===null;
function issueNumber(s){
 let m=String(s||'').match(/\bIssue\s*(\d{1,2})\b/i)||String(s||'').match(/(?:^|[-_])(?:issue[-_]?|i)(\d{1,2})(?:$|[-_])/i);
 if(!m)m=String(s||'').match(/(?:^|[-_])(?:S\d+E|E)(\d{2})(?:$|[-_])/i);
 return m?Number(m[1]):null;
}
function partition(row){
 const ids=Array.isArray(row.recipeIds)?row.recipeIds:[];
 const codes=ids.map(id=>(String(id).match(/[_-]S\d+E(\d{2})(?:[_-]|$)/i)||[])[1]||null);
 const unique=distinct(codes.filter(Boolean));
 if(unique.length<=1)return [{...row,issueNumber:issueNumber(row.issueId)||issueNumber(row.showId)||issueNumber(row.issueLabel)||(!nullish(unique[0])?Number(unique[0]):null),parentConfiguration:row.showId}];
 const groups=new Map();
 for(let i=0;i<ids.length;i++){const c=codes[i]||'unassigned';if(!groups.has(c))groups.set(c,[]);groups.get(c).push(ids[i])}
 return [...groups].map(([code,recipeIds])=>({...row,issueId:row.showId+'-issue-'+code,episodeGroup:code,issueNumber:code==='unassigned'?null:Number(code),
  parentConfiguration:row.showId,recipeIds,registeredUnits:recipeIds.length,
  approvedRecipeIds:(row.approvedRecipeIds||[]).filter(id=>recipeIds.includes(id)),approvedUnits:(row.approvedRecipeIds||[]).filter(id=>recipeIds.includes(id)).length}));
}
function build({shows,inventory,draftManifest,referenceManifest,books,releasedLinks,qualityEvidence={},sourceQuality={},visionsMetadata={}}){
 if(!Array.isArray(shows)||!Array.isArray(inventory?.configurations))throw Error('Assembler-backed portfolio inventory is required');
 if(inventory.counts?.registeredConfigurations!==shows.length)throw Error('Portfolio snapshot disagrees with registered configuration count');
 const configIds=new Set(shows.map(s=>s.id));
 const repeated=inventory.configurations.filter(x=>!configIds.has(x.showId));
 if(repeated.length)throw Error('Inventory references nonexistent configuration '+repeated[0].showId);
 const manifest=draftManifest?.drafts||{},keepers=referenceManifest?.references||{},bookList=books?.issues||{},links=releasedLinks?.links||{};
 const byDraft=new Map(Object.entries(manifest));
 const issueDrafts=new Map(),referenceCounts=new Map(),releaseLinks=new Map();
 for(const [k,x] of Object.entries(manifest)){const id=key(x.seriesId,x.issueId);if(!issueDrafts.has(id))issueDrafts.set(id,[]);issueDrafts.get(id).push({...x,manifestKey:k})}
 for(const x of Object.values(keepers)){if(!referenceCounts.has(x.seriesId))referenceCounts.set(x.seriesId,{total:0,types:{}});const z=referenceCounts.get(x.seriesId);z.total++;z.types[x.type]=(z.types[x.type]||0)+1}
 for(const [k,x] of Object.entries(links)){if(!releaseLinks.has(k))releaseLinks.set(k,[]);releaseLinks.get(k).push(...(x.images||[]))}
 const sourceFindings=qualityEvidence.sourceQuality||[],recoveryCandidates=qualityEvidence.recoveryCandidates||[];
 const imageFacts=sourceQuality.images||{};
 const explicitMastering=qualityEvidence.mastering||[],explicitExports=qualityEvidence.exported||[];
 const rows=[],series=new Map(),auditIssues=inventory.errors||[];
 function ensure(s){if(!series.has(s))series.set(s,{id:s,configurationCount:0,recipeIds:new Set(),approvedDraftKeys:new Set(),keeper:referenceCounts.get(s)||{total:0,types:{}},rows:[],released:visionsMetadata[s]?.releases?.filter(x=>x.publicationType==='E')||[],releaseMetadata:visionsMetadata[s]?.error?'unavailable':visionsMetadata[s]?'available':'not-configured'});return series.get(s)}
 for(const c of shows)ensure(c.seriesId||String(c.basePath||'').split('/').at(-1).replace(/-s1$/,'')).configurationCount++;
 const seenPairs=new Set();
 for(const report of inventory.configurations){
  for(const c of partition(report)){
   const sid=c.seriesId,iid=c.issueId,group=ensure(sid),originalIssue=c.parentConfiguration||c.showId;
   const recipeIds=distinct(c.recipeIds||[]);
   const namedBook=bookList[key(sid,iid)]||bookList[key(sid,originalIssue)]||null;
   const requiredIds=namedBook?namedBook.units:recipeIds;
   const source=namedBook?'curated-book':'assembled-recipes';
   const approvedIds=recipeIds.filter(id=>byDraft.get(key(sid,originalIssue,id))?.status==='approved-production-draft');
   const verifiedUnitSet=new Set(requiredIds);
   const extraBookUnits=namedBook?requiredIds.filter(id=>!recipeIds.includes(id)):[];
   const allIds=distinct([...requiredIds,...recipeIds]);
   const issueCandidates=recoveryCandidates.filter(x=>x.seriesId===sid&&(x.issueId===iid||x.issueId===originalIssue));
   const metadata=visionsMetadata[sid];
   const exactRelease=(metadata?.releases||[]).filter(x=>x.publicationType==='E'&&Number.isInteger(x.issueNumber)&&c.issueNumber!==null&&c.issueNumber===x.issueNumber);
   const quality=sourceFindings.filter(x=>x.seriesId===sid&&(x.issueId===iid||x.issueId===originalIssue));
   const mastered=explicitMastering.find(x=>x.seriesId===sid&&(x.issueId===iid||x.issueId===originalIssue)&&x.status==='mastered'&&x.evidence);
   const exported=explicitExports.find(x=>x.seriesId===sid&&(x.issueId===iid||x.issueId===originalIssue)&&x.status==='exported'&&x.evidence);
   const units=allIds.map(id=>{
    const draft=byDraft.get(key(sid,originalIssue,id))||byDraft.get(key(sid,iid,id));
    const candidate=issueCandidates.find(x=>x.recipeId===id)||null;
    const images=releaseLinks.get(key(sid,originalIssue,id))||releaseLinks.get(key(sid,iid,id))||[];
    const state=draft?.status==='approved-production-draft'?'approved-draft-indexed':candidate?'recovery-candidate':'not-indexed-in-RexPrompt';
    const sourceQualityObservation=draft?imageFacts[key(sid,originalIssue,id)]||imageFacts[key(sid,iid,id)]||null:null;
    return {recipeId:id,inRecipe:recipeIds.includes(id),inBook:!!namedBook&&verifiedUnitSet.has(id),draftState:state,
      imagePath:draft?.image||null,sourceQuality:quality.map(x=>x.classification),sourceQualityObservation,recovery:candidate,releaseLinks:images,
      confidence:draft?'recorded manifest approval; separate artistic QC unknown':candidate?'recovery lead, no verified approved original':'unknown outside RexPrompt'};
   });
   const approved=units.filter(x=>x.draftState==='approved-draft-indexed').length;
   const factUnits=units.filter(x=>x.sourceQualityObservation);
   const sourceQualitySummary={audited:factUnits.length,profileUnspecified:factUnits.filter(x=>x.sourceQualityObservation.colorProfile==='unspecified').length,
     shortEdgeUnder2000:factUnits.filter(x=>Math.min(x.sourceQualityObservation.width,x.sourceQualityObservation.height)<2000).length};
   const unmatched=units.filter(x=>x.draftState!=='approved-draft-indexed');
   const sourceValid=recipeIds.length>0&&!auditIssues.some(e=>e.startsWith(c.showId+':'));
   const row={seriesId:sid,issueId:iid,configurationId:originalIssue,issueNumber:c.issueNumber,issueLabel:c.episodeGroup?'Issue '+c.episodeGroup:((shows.find(x=>x.id===originalIssue)||{}).issueLabel||c.name||iid),
    denominator:requiredIds.length,denominatorSource:source,assembledCount:recipeIds.length,approvedIndexed:approved,notIndexedCount:unmatched.length,
    keeperCoverage:group.keeper,bookKnown:!!namedBook,exporterReadiness:namedBook?(unmatched.filter(x=>x.inBook).length?'blocked-on-approved-drafts':'inventory-complete-not-mastered'):'book-inventory-unavailable',
    quality:quality.length?quality:[{classification:'unknown',summary:'No issue-scoped artistic/native mastering assessment has been registered.'}],sourceQualitySummary,
    mastering:mastered?'mastered':quality.some(x=>x.mastered===false)?'native-review-required':'unverified',exported:exported?'exported':exactRelease.some(x=>x.externalLink)?'published-PDF-recorded':'unverified',
    published:exactRelease.length?'collected-edition-recorded':metadata?.error?'source-unavailable':metadata?'no-matching-edition-record':'unknown-release-source',
    releases:exactRelease,sourceHealthy:sourceValid,sourceFiles:c.sourceFiles||[],sourceOverlays:c.sourceOverlays||[],
    units,recoveryCandidates:issueCandidates,extraBookUnits,invalid:!sourceValid,linkedUnits:units.filter(x=>x.releaseLinks.length).length};
   rows.push(row);group.rows.push(row);
   for(const id of recipeIds)group.recipeIds.add(id);
   for(const v of units)if(v.draftState==='approved-draft-indexed')group.approvedDraftKeys.add(key(sid,originalIssue,v.recipeId));
   seenPairs.add(key(sid,originalIssue));
  }
 }
 // Curated books without a registered executable assembler configuration still count as scoped
 // book inventories. They must not disappear merely because no draft image has ever been indexed.
 for(const [bookKey,book] of Object.entries(bookList)){
  if(rows.some(x=>x.seriesId===book.seriesId&&x.issueId===book.issueId))continue;
  const sid=book.seriesId,iid=book.issueId,g=ensure(sid);
  const evidence=visionsMetadata[sid];
  const n=issueNumber(iid);
  const releases=(evidence?.releases||[]).filter(x=>x.publicationType==='E'&&Number.isInteger(x.issueNumber)&&n===x.issueNumber);
  const quality=sourceFindings.filter(x=>x.seriesId===sid&&x.issueId===iid);
  const candidates=recoveryCandidates.filter(x=>x.seriesId===sid&&x.issueId===iid);
  const ids=distinct(book.units||[]),units=ids.map(id=>{
   const draft=byDraft.get(key(sid,iid,id)),candidate=candidates.find(x=>x.recipeId===id)||null;
   return {recipeId:id,inRecipe:false,inBook:true,draftState:draft?.status==='approved-production-draft'?'approved-draft-indexed':candidate?'recovery-candidate':'not-indexed-in-RexPrompt',
     imagePath:draft?.image||null,sourceQualityObservation:imageFacts[key(sid,iid,id)]||null,
     recovery:candidate,releaseLinks:releaseLinks.get(key(sid,iid,id))||[],confidence:draft?'approved draft mapping; artistic QC unknown':candidate?'unresolved recovery evidence':'other storage unknown'};
  });
  const facts=units.filter(x=>x.sourceQualityObservation),approved=units.filter(x=>x.draftState==='approved-draft-indexed').length;
  const row={seriesId:sid,issueId:iid,configurationId:null,issueNumber:n,issueLabel:'Curated book '+iid,denominator:ids.length,denominatorSource:'curated-book',
   assembledCount:null,approvedIndexed:approved,notIndexedCount:units.length-approved,keeperCoverage:g.keeper,bookKnown:true,
   exporterReadiness:approved===ids.length?'inventory-complete-not-mastered':'blocked-on-approved-drafts',
   quality:quality.length?quality:[{classification:'unknown',summary:'No mastering assessment registered'}],
   sourceQualitySummary:{audited:facts.length,profileUnspecified:facts.filter(x=>x.sourceQualityObservation.colorProfile==='unspecified').length,
    shortEdgeUnder2000:facts.filter(x=>Math.min(x.sourceQualityObservation.width,x.sourceQualityObservation.height)<2000).length},
   mastering:quality.some(x=>x.mastered===false)?'native-review-required':'unverified',exported:releases.some(x=>x.externalLink)?'published-PDF-recorded':'unverified',
   published:releases.length?'collected-edition-recorded':evidence?.error?'source-unavailable':evidence?'no-matching-edition-record':'unknown-release-source',
   releases,sourceHealthy:false,sourceFiles:[],sourceOverlays:[],units,recoveryCandidates:candidates,extraBookUnits:ids,
   invalid:true,linkedUnits:units.filter(x=>x.releaseLinks.length).length};
  rows.push(row);g.rows.push(row);seenPairs.add(bookKey);
  for(const u of units)if(u.draftState==='approved-draft-indexed')g.approvedDraftKeys.add(key(sid,iid,u.recipeId));
 }
 for(const [sidIssue,items] of issueDrafts){
  if(seenPairs.has(sidIssue))continue;
  const first=items[0],g=ensure(first.seriesId);
  const units=items.map(x=>({recipeId:x.recipeId,inRecipe:false,inBook:false,draftState:x.status==='approved-production-draft'?'approved-draft-indexed':x.status,imagePath:x.image,recovery:null,releaseLinks:releaseLinks.get(key(x.seriesId,x.issueId,x.recipeId))||[]}));
  const r={seriesId:first.seriesId,issueId:first.issueId,configurationId:null,issueNumber:issueNumber(first.issueId),issueLabel:first.issueId,
    denominator:null,denominatorSource:'no-assembled-configuration',assembledCount:null,approvedIndexed:units.length,notIndexedCount:null,
    keeperCoverage:g.keeper,bookKnown:false,exporterReadiness:'book-inventory-unavailable',
    quality:[],sourceQualitySummary:{audited:0,profileUnspecified:0,shortEdgeUnder2000:0},mastering:'unverified',exported:'unverified',published:'unknown',releases:[],sourceHealthy:false,
    sourceFiles:[],sourceOverlays:[],units,recoveryCandidates:[],extraBookUnits:[],invalid:true,linkedUnits:units.filter(x=>x.releaseLinks.length).length};
  rows.push(r);g.rows.push(r);for(const x of units)g.approvedDraftKeys.add(key(first.seriesId,first.issueId,x.recipeId));
 }
 for(const [sid,b] of Object.entries(visionsMetadata))if(b&&!b.error)ensure(sid);
 const perSeries=[...series.values()].map(x=>({id:x.id,configurationCount:x.configurationCount,distinctRecipeUnits:x.recipeIds.size,approvedDraftUnits:x.approvedDraftKeys.size,
   keeper:x.keeper,linkedUnits:x.rows.reduce((n,r)=>n+r.linkedUnits,0),publishedEditions:x.released,
   releaseMetadata:x.releaseMetadata,issueCount:x.rows.length}));
 const compiledUnique=new Set([...series].flatMap(([sid,x])=>[...x.recipeIds].map(id=>sid+'::'+id)));
 rows.sort((a,b)=>a.seriesId.localeCompare(b.seriesId)||(a.issueNumber??999)-(b.issueNumber??999)||a.issueId.localeCompare(b.issueId));
 const totals={registeredConfigurations:shows.length,distinctSeries:perSeries.length,distinctAssembledUnits:compiledUnique.size,approvedDraftManifestEntries:Object.keys(manifest).length,
  keeperReferences:Object.keys(keepers).length,sourceImagesAudited:sourceQuality.examined||0,configurationRecipeOccurrences:inventory.counts.registeredRecipeUnitsAcrossConfigurations,
  knownBookGaps:rows.filter(x=>x.bookKnown).reduce((n,x)=>n+x.units.filter(u=>u.inBook&&u.draftState!=='approved-draft-indexed').length,0),
  unresolvedCandidates:recoveryCandidates.length};
 return {totals,series:perSeries.sort((a,b)=>a.id.localeCompare(b.id)),rows,evidence:{auditErrors:auditIssues,auditWarnings:inventory.warnings||[],
  inventorySource:inventory.generatedFrom,qualitySource:sourceQuality.method||'Not available',qualityIntegrityIssues:sourceQuality.issues||[],recoveryCandidates:recoveryCandidates.length,qualityFindings:sourceFindings.length}};
}
return {build,issueNumber,partition};
});