(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.RexProductionDashboard=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const key=(s,i,r)=>[s,i,r].join('::');
function seriesId(show){return show.seriesId||String(show.seriesName||show.name?.split(' — ')[0]||show.id).toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'')}
function issueNum(show){let match=String(show.issueLabel||show.name||'').match(/(?:issue|chapter)\s+0*(\d+)/i);if(match)return Number(match[1]);match=String(show.id||'').match(/(?:-i|-e|-c)0*(\d+)(?:$|-issue)/i);return match?Number(match[1]):null}
function normalize(raw){if(Array.isArray(raw))return raw;if(Array.isArray(raw?.pages))return raw.pages;return Object.entries(raw||{}).map(([id,x])=>({id,...x}))}
function episode(x){if(x?.episode)return x.episode;let m=String(x?.id||'').match(/^RF_(S1E\d{2})_/);return m?.[1]||null}
function applyOverlay(scenes,incoming,overlay){
 if(overlay.mergeById){const changes=new Map(incoming.filter(x=>x?.id).map(x=>[x.id,x])),seen=new Set();
 const patched=scenes.map(x=>{if(!changes.has(x.id))return x;seen.add(x.id);return {...x,...changes.get(x.id)}});
 for(const x of incoming)if(x?.id&&!seen.has(x.id)&&!scenes.some(y=>y.id===x.id))patched.push(x);
 return patched;}
 const ids=overlay.replaceEpisodes|| (overlay.replaceEpisode?[overlay.replaceEpisode]:[]);
 if(ids.length){const targets=new Set(ids),first=scenes.findIndex(x=>targets.has(episode(x)));if(first>=0){const at=scenes.slice(0,first).filter(x=>!targets.has(episode(x))).length;const kept=scenes.filter(x=>!targets.has(episode(x)));return kept.slice(0,at).concat(incoming,kept.slice(at))}}
 if(overlay.afterId){const i=scenes.findIndex(x=>x.id===overlay.afterId);const at=i<0?scenes.length:i+1;return scenes.slice(0,at).concat(incoming,scenes.slice(at))}
 return scenes.concat(incoming);
}
function fileIssue(source){const s=typeof source==='string'?source:source?.replaceEpisode||source?.file||'';const m=String(s).match(/(?:S\d+E|[_-]e)(\d{2})/i);return m?Number(m[1]):null}
function expand(show){
 const files=show.scenesFiles?.length?show.scenesFiles:[show.scenesFile||'scenes.json'];
 const explicit=show.issueLabel||String(show.name||'').match(/(?:Issue\s+\d+(?:\s+—\s+.*)?)/i)?.[0]||String(show.name||'').match(/(Chapters?\s+[^—]+)/i)?.[0]||null;
 const numbers=new Set();files.forEach(x=>{const n=fileIssue(x);if(n)numbers.add(n)});(show.sceneOverlays||[]).forEach(x=>{const n=fileIssue(x);if(n)numbers.add(n)});
 const wrap=x=>({...x,seriesId:seriesId(x),issueId:x.id});
 if(explicit||numbers.size<=1)return [wrap(show)];
 return [...numbers].sort((a,b)=>a-b).map(n=>wrap({...show,id:show.id+'-issue-'+n,
 scenesFiles:files.filter(f=>fileIssue(f)===null||fileIssue(f)===n),scenesFile:undefined,
 sceneOverlays:(show.sceneOverlays||[]).filter(x=>fileIssue(x)===n),
 dialogueOverlays:(show.dialogueOverlays||[]).filter(x=>fileIssue(x)===n),issueLabel:'Issue '+n}));
}
async function assemble(show,read){
 const base=show.basePath||'data',file=(p)=>base.replace(/\/$/,'')+'/'+p;
 let cfg={};
 try{cfg=await read(file(show.packageConfigFile||'assembler.json'))}catch(e){if(!/404|ENOENT|not found/i.test(String(e)))throw e}
 const c={...cfg,...show},files=Array.isArray(c.scenesFiles)?c.scenesFiles:[c.scenesFile||'scenes.json'];
 let scenes=(await Promise.all(files.map(f=>read(file(f))))).flatMap(normalize);
 if(c.excludeSceneIds?.length){const excluded=new Set(c.excludeSceneIds);scenes=scenes.filter(x=>!excluded.has(x.id))}
 for(const o of c.sceneOverlays||[]){
  let data=normalize(await read(file(o.file),o.encoding));
  if(o.includeIds?.length){const selected=new Set(o.includeIds);data=data.filter(x=>selected.has(x.id))}
  if(o.excludeIds?.length){const excluded=new Set(o.excludeIds);data=data.filter(x=>!excluded.has(x.id))}
  scenes=applyOverlay(scenes,data,o)
 }
 if(c.includeIdPattern){const re=new RegExp(c.includeIdPattern);scenes=scenes.filter(x=>re.test(String(x?.id||'')))}
 const ids=scenes.map(x=>x?.id).filter(Boolean);
 if(ids.length!==scenes.length)throw Error('Assembled scene missing recipe id');
 if(new Set(ids).size!==ids.length)throw Error('Duplicate assembled recipe ID in '+show.issueId+': '+ids.filter((x,i)=>ids.indexOf(x)!==i).join(','));
 return ids;
}
async function inventory(shows,read,{concurrency=8,onProgress=()=>{}}={}){
 if(!Array.isArray(shows))throw Error('Expected shows registry');
 const configured=shows.flatMap(expand),items=Array(configured.length);let index=0,completed=0;
 async function worker(){while(index<configured.length){const i=index++,show=configured[i];try{const recipeIds=await assemble(show,read);items[i]={show,recipeIds,sourceStatus:'available',error:null}}catch(e){items[i]={show,recipeIds:[],sourceStatus:'unavailable',error:String(e.message||e)}}onProgress(++completed,configured.length)}}
 await Promise.all(Array.from({length:Math.min(concurrency,configured.length)},worker));
 return items;
}
function releaseNumber(row){return issueNum(row.show)}
function build({inventories,shows,approvalManifest,keeperManifest,bookManifest,releasedLinks,releaseMetadata={},releaseFailures={},findings=[],recovery=[],exportCoverage=null}){
 const drafts=approvalManifest?.drafts||{},refs=keeperManifest?.references||{},books=bookManifest?.issues||{},links=releasedLinks?.links||{};
 const seriesMap=new Map(),rows=[],rowMap=new Map(),sourceIndex=new Map();
 const exporterBySelector=new Map((exportCoverage?.entries||[]).map(x=>[x.selectorId,x]));
 for(const item of inventories||[])if(item.sourceStatus==='available'){
  const sid=item.show.seriesId||seriesId(item.show);
  for(const recipeId of item.recipeIds||[]){const lookup=sid+'::'+recipeId;if(!sourceIndex.has(lookup))sourceIndex.set(lookup,new Set());sourceIndex.get(lookup).add(item.show.id)}
 }
 function group(id){if(!seriesMap.has(id))seriesMap.set(id,{id,configurationCount:0,issueCount:0,recipeInventory:0,uniqueRecipes:0,approvedDrafts:0,keeperRefs:0,knownMissingIndexedFiles:0,unindexedRecipeUnits:0,unresolvedRecoveryCandidates:0,releasedEditions:0,releaseEvidence:'unknown',qualityFindings:[],issues:[]});return seriesMap.get(id)}
 for(const s of shows||[])group(seriesId(s)).configurationCount++;
 const countBySeries=new Map();
 for(const [id,r] of Object.entries(refs))group(r.seriesId).keeperRefs++;
 for(const row of inventories||[]){
  const show=row.show,sid=show.seriesId||seriesId(show),iid=show.issueId||show.id,groupObj=group(sid),lookup=sid+'::'+iid,book=books[lookup];
  const assembled=row.recipeIds||[],required=book?.units||assembled,ids=[...new Set([...required,...assembled])];
  const missingFromRecipe=book?book.units.filter(id=>!assembled.includes(id)):[];
  const externalSourceUnits=missingFromRecipe.map(recipeId=>({recipeId,sourceConfigurations:[...(sourceIndex.get(sid+'::'+recipeId)||[])]}));
  const unavailableBookSourceIds=externalSourceUnits.filter(x=>!x.sourceConfigurations.length).map(x=>x.recipeId);
  const recipes=ids.map(recipeId=>{
   const idx=key(sid,iid,recipeId),draft=drafts[idx],linked=links[idx]?.images||[],candidate=recovery.find(x=>x.seriesId===sid&&x.issueId===iid&&x.recipeId===recipeId)||null;
   let state=draft?.status==='approved-production-draft'&&draft.image?'approved':candidate?.stage==='generated'?'generated':row.sourceStatus==='unavailable'?'unavailable':'not-indexed';
   const quality=findings.filter(x=>x.seriesId===sid&&(x.issueId===iid||!x.issueId||(issueNum({id:x.issueId})!==null&&issueNum({id:x.issueId})===issueNum(show)))&&(x.recipeId===recipeId||!x.recipeId));
   return {id:recipeId,indexKey:idx,assembled:assembled.includes(recipeId),sourceConfigurations:[...(sourceIndex.get(sid+'::'+recipeId)||[])],bookRequired:book?book.units.includes(recipeId):null,draftState:state,approved:state==='approved',sourceImage:draft?.image||null,sourceQuality:quality,mastering:'unknown',export:'unknown',publication:linked.length?'linked-released-canon':'unknown',releasedImageLinks:linked,
   recovery:candidate?{state:candidate.stage,source:candidate.source||null,note:candidate.note||null}:null};
  });
  const evidence=releaseMetadata[sid],releases=(evidence?.releases||[]).filter(x=>x.publicationType==='E'),n=releaseNumber(row);
  const matches=n===null?[]:releases.filter(x=>x.issueNumber===n);
  const knownImageNotIndexed=recipes.filter(x=>x.draftState==='not-indexed').length;
  const knownCuratedMissing=recipes.filter(x=>!x.assembled&&x.bookRequired===true).map(x=>x.id);
  const approved=recipes.filter(x=>x.approved).length;
  const unresolved=recipes.filter(x=>x.recovery&&x.recovery.state!=='recovered').length;
  const issueRecovery=recovery.filter(x=>x.seriesId===sid&&x.issueId===iid&&x.recipeId===null);
  let isComplete=null;if(row.sourceStatus==='available')isComplete=required.every(id=>recipes.some(x=>x.id===id&&x.approved))&&!unavailableBookSourceIds.length;
  const exporterEvidence=exporterBySelector.get(show.id)||null;
  const exporter=exporterEvidence?(exporterEvidence.status==='complete-draft-export-supported'?'approved-image inventory complete; export not verified':exporterEvidence.status==='blocked-missing-images'?'blocked: '+exporterEvidence.missingImageCount+' required approved mappings absent':exporterEvidence.status==='not-a-book'?'not an issue book':'uncurated book inventory'):(book?(isComplete?'asset-gate-passed; export unverified':'blocked; curated required units not fully approved'):'unavailable: no curated complete-book inventory');
  const edition=matches.length?{state:'published-record',catalogIds:matches.map(x=>x.catalogId),pdfPaths:matches.map(x=>x.externalLink).filter(Boolean),source:'StarSplitterVisions series metadata'}:
    evidence?{state:'no-matching-edition',source:'StarSplitterVisions series metadata'}:
    releaseFailures[sid]?{state:'unavailable',error:releaseFailures[sid]}:{state:'unknown'};
  const out={seriesId:sid,issueId:iid,name:show.name,issueNumber:n,configurationId:show.id,sourceStatus:row.sourceStatus,error:row.error||null,availableRecipes:assembled.length,requiredRecipes:row.sourceStatus==='available'?required.length:null,requiredBasis:book?'curated-book':row.sourceStatus==='available'?'assembled-recipe-set':'unavailable',additionalCuratedMissingFromAssembler:missingFromRecipe,externalSourceUnits,unavailableBookSourceIds,approvedDrafts:approved,notIndexed:knownImageNotIndexed,unresolvedRecovery:unresolved,assetGate:isComplete,exporter,exporterEvidence,knownMissingApprovalIds:exporterEvidence?.missingImageIds||[],mastering:'unknown',export:edition.pdfPaths?.length?'exported-pdf-record':'unknown',release:edition,keeperRefs:groupObj.keeperRefs,knownCuratedMissing,issueRecovery,recipeIds:ids,recipes,qualityFindings:findings.filter(x=>x.seriesId===sid&&(x.issueId===iid||!x.issueId||(issueNum({id:x.issueId})!==null&&issueNum({id:x.issueId})===issueNum(show)))),category:/cover/i.test(show.id)&&!book?'cover-shelf':'production'};
  rows.push(out);rowMap.set(lookup,out);groupObj.issues.push(out);groupObj.issueCount++;groupObj.recipeInventory+=assembled.length;groupObj.approvedDrafts+=approved;groupObj.unindexedRecipeUnits+=knownImageNotIndexed;groupObj.unresolvedRecoveryCandidates+=unresolved+issueRecovery.length;
  const union=countBySeries.get(sid)||new Set();assembled.forEach(x=>union.add(x));countBySeries.set(sid,union);
 }
 for(const [idx,draft] of Object.entries(drafts)){const target=rowMap.get(draft.seriesId+'::'+draft.issueId);if(!target||!target.recipeIds.includes(draft.recipeId)){const g=group(draft.seriesId);g.qualityFindings.push({kind:'orphan-approval',severity:'needs-reconciliation',observation:'Approval index '+idx+' is not found in assembled recipe inventory; do not count as ready until mapped'})}}
 for(const f of findings)group(f.seriesId).qualityFindings.push(f);
 for(const x of recovery.filter(x=>!x.issueId)){const sg=group(x.seriesId);sg.unresolvedRecoveryCandidates++;sg.qualityFindings.push({kind:'unresolved historical recovery',observation:x.note,source:x.source,severity:'unverified'})}
 for(const [id,sg] of seriesMap){sg.uniqueRecipes=countBySeries.get(id)?.size||0;const data=releaseMetadata[id];sg.releasedEditions=(data?.releases||[]).filter(x=>x.publicationType==='E').length;sg.releaseEvidence=data?'loaded':releaseFailures[id]?'unavailable':'unknown';}
 const warnings=[];
 for(const r of rows){if(r.sourceStatus!=='available')warnings.push(r.issueId+': '+r.error);if(r.unavailableBookSourceIds.length)warnings.push(r.issueId+': curated book unit has no source in any registered configuration: '+r.unavailableBookSourceIds.join(','))}
 return {summary:{registryConfigurations:shows.length,expandedConfigurations:inventories.length,assembledRecipeAssignments:rows.reduce((a,x)=>a+x.availableRecipes,0),distinctSeries:seriesMap.size,approvedDraftManifestEntries:Object.keys(drafts).length,keeperManifestEntries:Object.keys(refs).length,curatedBookCount:Object.keys(books).length,sourceBackedExporterCoverage:exportCoverage?.statuses||null,unavailableConfigRows:rows.filter(x=>x.sourceStatus==='unavailable').length},series:[...seriesMap.values()].sort((a,b)=>a.id.localeCompare(b.id)),rows,warnings};
}
return {seriesId,expand,assemble,inventory,build,issueNum,normalize,applyOverlay};
});