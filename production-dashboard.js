(()=>{
'use strict';
const $=x=>document.getElementById(x),C=window.RexProductionDashboard;
const el=(tag,t,cl)=>{const n=document.createElement(tag);if(t!==undefined)n.textContent=String(t);if(cl)n.className=cl;return n};
const td=x=>{const n=el('td');n.append(x instanceof Node?x:document.createTextNode(String(x)));return n};
const cache=new Map();
async function source(p,encoding){const k=p+'::'+(encoding||'json');if(!cache.has(k))cache.set(k,(async()=>{const r=await fetch(p,{cache:'no-cache'});if(!r.ok)throw Error('HTTP '+r.status+' '+p);if(encoding==='gzip-base64'){if(!window.DecompressionStream)throw Error('Browser cannot decode gzip-base64 source');const text=(await r.text()).replace(/\s+/g,''),bytes=Uint8Array.from(atob(text),x=>x.charCodeAt(0));return JSON.parse(await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).text())}return r.json()})());return cache.get(k)}
async function gather(){
 const [shows,approvalManifest,keeperManifest,bookManifest,releasedLinks,quality,recovery,visual,exportCoverage,crossAudit]=await Promise.all(['data/shows.json','production/drafts/manifest.json','production/references/reference-keeper-manifest.json','production/book-manifests.json','production/released-links.json','production/dashboard-source-quality.json','production/dashboard-recovery-candidates.json','production/visual-sources.json','production/book-export-coverage.json','production/audits/visual_review_2026-10-25.json'].map(p=>source(p)));
 const releaseMetadata={},releaseFailures={};
 await Promise.all(Object.entries(visual.series||{}).map(async([id,v])=>{if(!v.visionsSlug)return;try{const r=await fetch(visual.visionsSeriesRawBase+'/'+v.visionsSlug+'.json',{cache:'no-cache'});if(!r.ok)throw Error('HTTP '+r.status);releaseMetadata[id]=await r.json()}catch(e){releaseFailures[id]=String(e)}}));
 const inventories=await C.inventory(shows,source,{concurrency:9,onProgress:(a,b)=>{if(a===b||a%5===0)$('status').textContent='Assembling original scripts and overlays: '+a+' / '+b}});
 const audited=(crossAudit.findings||[]).map(x=>({seriesId:x.seriesId,issueId:x.issueId,recipeId:x.recipeId,kind:x.type,severity:x.severity,observation:x.observation,gate:x.requiredCorrection,evidence:x.sourceEvidence?.[0],findingId:x.id}));
 return C.build({shows,inventories,approvalManifest,keeperManifest,bookManifest,releasedLinks,releaseMetadata,releaseFailures,findings:[...quality.findings,...audited],recovery:recovery.candidates,exportCoverage});
}
function field(parent,name,value){const p=el('p');p.append(el('strong',name+': '),document.createTextNode(String(value)));parent.append(p)}
function ref(url,label){const a=el('a',label);a.href=url;a.target='_blank';a.rel='noopener noreferrer';return a}
function detail(row){
 const area=el('div',undefined,'drill');
 field(area,'Source config',row.configurationId);
 field(area,'Effective recipe inventory',row.availableRecipes+' individual IDs from assembled sources');
 field(area,'Required denominator',row.requiredRecipes===null?'unavailable':row.requiredRecipes+' / '+row.requiredBasis);
 field(area,'Book units loaded in sibling configurations',row.externalSourceUnits.filter(x=>x.sourceConfigurations.length).map(x=>x.recipeId+' → '+x.sourceConfigurations.join(', ')).join('; ')||'none');field(area,'Book units unavailable in every registered source',row.unavailableBookSourceIds.join(', ')||'none');
 field(area,'Mastering evidence','unknown; approvals do not establish master quality');
 field(area,'Exporter',row.exporter);field(area,'Required book units lacking approved image mappings',row.knownMissingApprovalIds.join(', ')||'none');field(area,'Exported artifact evidence',row.export);
 field(area,'Release evidence',row.release.state+(row.release.catalogIds?.length?' '+row.release.catalogIds.join(', '):''));
 if(row.error)field(area,'Source error',row.error);
 for(const f of row.qualityFindings){let p=el('p',f.severity+' — '+f.observation+' '+f.gate+' ');if(f.evidence)p.append(ref(f.evidence,'Evidence'));area.append(p)}
 const table=el('table'),thead=el('thead'),th=el('tr');
 for(const t of ['Exact recipe ID','Assembler','IMG approval','Source quality','Recovery candidate','Released-link evidence'])th.append(el('th',t));thead.append(th);table.append(thead);
 const body=el('tbody');
 for(const recipe of row.recipes){const tr=el('tr'),approval=el('div');
  approval.append(el('span',recipe.draftState));
  if(recipe.sourceImage){approval.append(el('div'));approval.append(ref('https://github.com/starsplitterrecords/RexPrompt/blob/main/'+recipe.sourceImage,'Original draft file'))}
  const quality=recipe.sourceQuality?.length?recipe.sourceQuality.map(x=>x.kind+' / '+x.severity).join('; '):'unknown';
  tr.append(td(el('code',recipe.id)),td(recipe.assembled?'available in issue':recipe.sourceConfigurations?.length?'available via '+recipe.sourceConfigurations.join(', '):'curated but source unavailable'),td(approval),td(quality),td(recipe.recovery?recipe.recovery.state+' — '+recipe.recovery.note:'no evidenced candidate'),td(recipe.releasedImageLinks?.length?'released image link':'unknown; no exact source mapping'));
  body.append(tr)
 }
 table.append(body);area.append(table);return area;
}
function display(m){
 $('status').textContent='Exact recipe inventory assembled from RexPrompt; released metadata retrieved separately. Artistic mastering is not inferred.';
 const stats=[['Registered show configurations',m.summary.registryConfigurations],['Expanded configurations',m.summary.expandedConfigurations],['Individual recipe assignments',m.summary.assembledRecipeAssignments],['Approved draft records',m.summary.approvedDraftManifestEntries],['Keeper references',m.summary.keeperManifestEntries],['Unavailable source configurations',m.summary.unavailableConfigRows]];
 for(const [k,v] of stats){const x=el('div',undefined,'metric');x.append(el('div',v,'metric-value'),el('div',k,'muted'));$('stats').append(x)}
 const select=$('seriesFilter');const all=el('option','All series');all.value='';select.append(all);
 for(const s of m.series){const x=el('option',s.id);x.value=s.id;select.append(x)}
 function render(){
  const val=select.value,q=$('search').value.toLowerCase().trim(),issues=$('rows'),series=$('seriesRows'),attention=$('attentionOnly').checked;
  issues.replaceChildren();series.replaceChildren();
  const rows=m.rows.filter(x=>(!val||x.seriesId===val)&&(!q||[x.seriesId,x.issueId,x.name,...x.recipeIds].some(z=>String(z).toLowerCase().includes(q)))&&(!attention||x.sourceStatus!=='available'||x.notIndexed||x.unresolvedRecovery||x.qualityFindings.length));
  $('count').textContent=rows.length+' of '+m.rows.length+' exact issue/collection configuration records';
  for(const r of rows){
   const tr=el('tr'),exp=el('details');exp.append(el('summary','Inspect recipe IDs'));
   exp.addEventListener('toggle',()=>{if(exp.open&&exp.children.length===1)exp.append(detail(r))});
   tr.append(...[r.seriesId,r.issueId,r.availableRecipes+' / '+(r.requiredRecipes??'unavailable'),r.approvedDrafts,r.notIndexed,r.unresolvedRecovery,r.qualityFindings.length||'unknown',r.mastering,r.exporter,r.export,r.release.state].map(td),td(exp));issues.append(tr)
  }
  for(const s of m.series.filter(x=>!val||x.id===val)){
   const tr=el('tr');tr.append(...[s.id,s.configurationCount,s.issueCount,s.recipeInventory,s.uniqueRecipes,s.approvedDrafts,s.keeperRefs,s.unresolvedRecoveryCandidates,s.releaseEvidence==='loaded'?s.releasedEditions+' publication records':s.releaseEvidence,s.qualityFindings.length||'unknown'].map(td));series.append(tr)
  }
 }
 select.onchange=render;$('search').oninput=render;$('attentionOnly').onchange=render;render();
 if(m.warnings.length){const d=el('details');d.append(el('summary',m.warnings.length+' source assembly warnings'));const ul=el('ul');m.warnings.forEach(x=>ul.append(el('li',x)));d.append(ul);$('warnings').append(d)}
}
gather().then(display).catch(e=>{$('status').textContent='Portfolio unavailable: '+e.message;$('status').className='error'});
})();