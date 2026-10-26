(()=>{
'use strict';
const $=id=>document.getElementById(id);
const local=async(path)=>{const r=await fetch(path,{cache:'no-store'});if(!r.ok)throw Error(path+': HTTP '+r.status);return r.json()};
function node(tag,attrs={},value){const n=document.createElement(tag);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,v);if(value!==undefined)n.textContent=String(value);return n;}
async function load(){
 $('status').textContent='Reading the current production manifests…';
 const [shows,draftManifest,referenceManifest,books,releasedLinks,visuals]=await Promise.all([
  local('data/shows.json'),local('production/drafts/manifest.json'),local('production/references/reference-keeper-manifest.json'),
  local('production/book-manifests.json'),local('production/released-links.json'),local('production/visual-sources.json')
 ]);
 const visionsMetadata={};
 const names=Object.entries(visuals.series||{});
 await Promise.all(names.map(async([id,v])=>{
  if(!v.visionsSlug)return;
  try{
   const url='https://raw.githubusercontent.com/starsplitterrecords/StarSplitterVisions/main/sites/visions/src/content/series/'+encodeURIComponent(v.visionsSlug)+'.json';
   const r=await fetch(url,{cache:'no-store'});if(!r.ok)throw Error('HTTP '+r.status);
   visionsMetadata[id]=await r.json();
  }catch(e){visionsMetadata[id]={error:String(e)}}
 }));
 return window.RexProductionDashboard.build({shows,draftManifest,referenceManifest,books,releasedLinks,visionsMetadata});
}
function draw(model){
 $('status').textContent='Source: current RexPrompt manifests; released metadata is separately loaded from StarSplitterVisions where available. No visual approval is inferred.';
 const stats=[['Registered production units',model.totals.registeredUnits],['Approved draft mappings',model.totals.drafts],['Keeper references',model.totals.references],['Complete book inventories',model.totals.completeBooks+' / '+model.totals.bookInventoryCount],['Known book gaps',model.totals.knownMissing]];
 const area=$('stats');area.replaceChildren();for(const [label,value] of stats){let b=node('div',{class:'metric'});b.append(node('div',{class:'metric-value'},value),node('div',{class:'muted'},label));area.append(b)}
 const filter=$('seriesFilter');filter.replaceChildren(node('option',{value:''},'All series'));
 for(const x of model.series)filter.append(node('option',{value:x.id},x.id));
 const search=$('search');
 function render(){
  const value=filter.value,query=search.value.trim().toLowerCase();
  const out=$('rows');out.replaceChildren();
  const items=model.rows.filter(x=>(!value||x.seriesId===value)&&(!query||(x.issueId+' '+x.seriesId+' '+x.name).toLowerCase().includes(query)));
  for(const x of items){
   const tr=node('tr');const basic=[x.seriesId,x.issueId,x.approved+(x.required===null?' / ?':' / '+x.required),
    x.assetsComplete===null?'Unknown denominator':x.assetsComplete?'All mapped':'Missing '+x.missing.length,'Not audited','Not release-validated'];
   for(const value of basic)tr.append(node('td',{},value));
   const td=node('td');const det=node('details');det.append(node('summary',{},'Inspect source state'));
   const list=x.missing?.length?x.missing.join(', '):x.assetsComplete?'No inventory gaps':'No complete-book manifest; missing pages cannot be established';
   det.append(node('p',{},'Missing: '+list),node('p',{},'Draft IDs: '+(x.draftIds.join(', ')||'none')));
   td.append(det);tr.append(td);out.append(tr)
  }
  $('count').textContent=items.length+' issue/package rows. "Complete" refers only to the approved-draft inventory, not print/master approval.';
  const covered=$('seriesRows');covered.replaceChildren();
  for(const x of model.series.filter(x=>!value||x.id===value)){
   const tr=node('tr');
   for(const v of [x.id,x.registeredUnits,x.draftUnits,x.referenceUnits,x.linkedCanonUnits,x.publishedMetadata==='loaded'?x.publishedEditions+' collected release records':x.publishedMetadata==='unavailable'?'Unreachable':'Not queried'])tr.append(node('td',{},v));
   covered.append(tr);
  }
 }
 filter.onchange=render;search.oninput=render;render();
}
load().then(draw).catch(e=>{$('status').textContent='Dashboard data load failed: '+e.message;$('status').className='error'});
})();