(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.RexProductionDashboard=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
function assertData(s){if(!s||typeof s!=='object')throw Error('Missing dashboard source');}
function deriveSeries(show){
  if(show.seriesId)return show.seriesId;
  const path=String(show.basePath||'');
  return path.split('/').at(-1)?.replace(/-s1$/,'')||'unclassified';
}
function build({shows,draftManifest,referenceManifest,books,releasedLinks,visionsMetadata={}}){
  if(!Array.isArray(shows))throw Error('Missing live shows registry');
  [draftManifest,referenceManifest,books,releasedLinks].forEach(assertData);
  const drafts=Object.values(draftManifest.drafts||{});
  const refs=Object.values(referenceManifest.references||{});
  const bookMap=books.issues||{},links=releasedLinks.links||{};
  const series=new Map();
  function ensure(id){if(!series.has(id))series.set(id,{id,registeredConfigurations:0,draftUnits:0,referenceUnits:0,linkedCanonUnits:0,issues:[],publishedMetadata:'unknown',publishedEditions:0});return series.get(id)}
  const rows=[],activeKeys=new Set();
  for(const show of shows){
    const seriesId=deriveSeries(show);ensure(seriesId).registeredConfigurations++;
    const issueId=show.id;
    const key=seriesId+'::'+issueId,book=bookMap[key];
    const entries=drafts.filter(x=>x.seriesId===seriesId&&x.issueId===issueId);
    if(book||entries.length){
      const approved=new Set(entries.filter(x=>x.status==='approved-production-draft'&&x.image).map(x=>x.recipeId));
      const missing=book?.units.filter(id=>!approved.has(id))||null;
      const row={seriesId,issueId,name:show.name||issueId,approved:approved.size,required:book?.units.length??null,
        missing,assetsComplete:book?missing.length===0:null,mastering:'unverified',publishing:'unverified',
        registry:'registered',draftIds:entries.map(x=>x.recipeId)};
      rows.push(row);ensure(seriesId).issues.push(row);activeKeys.add(key);
    }
  }
  for(const [key,book] of Object.entries(bookMap)){
    if(activeKeys.has(key))continue;
    const id=book.seriesId;const entries=drafts.filter(x=>x.seriesId===id&&x.issueId===book.issueId);
    const approved=new Set(entries.map(x=>x.recipeId));
    const missing=book.units.filter(x=>!approved.has(x));
    const row={seriesId:id,issueId:book.issueId,name:book.issueId,approved:approved.size,required:book.units.length,
      missing,assetsComplete:missing.length===0,mastering:'unverified',publishing:'unverified',registry:'book manifest',draftIds:entries.map(x=>x.recipeId)};
    rows.push(row);ensure(id).issues.push(row);activeKeys.add(key);
  }
  for(const v of drafts){
    ensure(v.seriesId).draftUnits++;
    const key=v.seriesId+'::'+v.issueId;
    if(activeKeys.has(key))continue;
    let row=rows.find(x=>x.seriesId===v.seriesId&&x.issueId===v.issueId);
    if(!row){
      row={seriesId:v.seriesId,issueId:v.issueId,name:v.issueId,approved:0,required:null,missing:null,assetsComplete:null,
        mastering:'unverified',publishing:'unverified',registry:'draft manifest only',draftIds:[]};
      rows.push(row);ensure(v.seriesId).issues.push(row);
    }
    row.approved++;row.draftIds.push(v.recipeId);
  }
  for(const r of refs)ensure(r.seriesId).referenceUnits++;
  for(const key of Object.keys(links)){const id=key.split('::')[0];ensure(id).linkedCanonUnits++}
  for(const [id,state] of Object.entries(visionsMetadata)){
    const s=ensure(id);
    if(state===null||state.error){s.publishedMetadata='unavailable';continue}
    s.publishedMetadata='loaded';
    s.publishedEditions=(state.releases||[]).filter(r=>r.publicationType==='E').length;
  }
  rows.sort((a,b)=>a.seriesId.localeCompare(b.seriesId)||a.issueId.localeCompare(b.issueId));
  return {totals:{registeredConfigurations:shows.length,drafts:drafts.length,references:refs.length,completeBooks:rows.filter(x=>x.required!==null&&x.assetsComplete).length,
    bookInventoryCount:rows.filter(x=>x.required!==null).length,knownMissing:rows.flatMap(x=>x.missing||[]).length},
    series:[...series.values()].sort((a,b)=>a.id.localeCompare(b.id)),rows};
}
return {build,deriveSeries};
});