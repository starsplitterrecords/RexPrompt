(()=>{
'use strict';
const $=id=>document.getElementById(id);
const get=async p=>{const r=await fetch(p,{cache:'no-store'});if(!r.ok)throw Error(p+': HTTP '+r.status);return r.json()};
const el=(tag,text,cls)=>{const x=document.createElement(tag);if(text!==undefined)x.textContent=String(text);if(cls)x.className=cls;return x};
function chip(label,type){const c=el('span',label,'chip '+(type||''));return c}
const td=(row,txt)=>{const c=el('td',txt);row.append(c);return c};
const tableRow=(values)=>{let r=el('tr');values.forEach(x=>td(r,x));return r};
function showLink(url,label){
 if(!url)return el('span',label||'Unknown','muted');
 const a=el('a',label||url);a.href=url;a.target='_blank';a.rel='noopener noreferrer';return a;
}
function githubFile(p){return 'https://github.com/starsplitterrecords/RexPrompt/blob/main/'+p.split('/').map(encodeURIComponent).join('/')}
function draw(m){
 $('loadState').textContent='All 126 registered configurations reconciled against assembler-produced recipe IDs, approved drafts and curated books. Released metadata is independently queried; unknown states are not treated as missing artwork.';
 const cards=[
 ['Registered configurations',m.totals.registeredConfigurations],
 ['Distinct assembled recipes',m.totals.distinctAssembledUnits],
 ['Approved draft records',m.totals.approvedDraftManifestEntries],
 ['Keeper references',m.totals.keeperReferences],
 ['Source images audited',m.totals.sourceImagesAudited],
 ['Unindexed book units',m.totals.knownBookGaps],
 ['Recorded recovery leads',m.totals.unresolvedCandidates],
 ['C3 visual findings',m.totals.visualFindings]
 ];
 $('metrics').replaceChildren(...cards.map(([t,v])=>{const box=el('div',undefined,'metric');box.append(el('strong',v),el('small',t));return box}));
 const seriesFilter=$('seriesFilter'),query=$('query'),qualityFilter=$('qualityFilter');
 seriesFilter.replaceChildren(el('option','All series'));
 seriesFilter.firstElementChild.value='';
 m.series.forEach(s=>{let option=el('option',s.id);option.value=s.id;seriesFilter.append(option)});
 const summary=$('seriesList'),issueRows=$('issueRows'),audit=$('audit');
 audit.textContent=m.evidence.auditErrors.length?'Assembler audit errors: '+m.evidence.auditErrors.join(' · '):
  'Assembler audit: no reported errors. '+m.evidence.auditWarnings.length+' informational warnings. Mastering and artwork quality require separate evidence.';
 function render(){
  const f=seriesFilter.value,q=query.value.trim().toLowerCase(),flag=qualityFilter.value;
  summary.replaceChildren();
  for(const s of m.series.filter(x=>!f||x.id===f)){
   const row=tableRow([s.id,s.configurationCount,s.distinctRecipeUnits,s.approvedDraftUnits,s.keeper.total,s.linkedUnits]);
   const release=el('td');
   release.append(chip(s.releaseMetadata==='available'?s.publishedEditions.length+' edition(s)':s.releaseMetadata==='unavailable'?'Metadata unavailable':'Not configured',s.releaseMetadata==='available'?'ok':'neutral'));
   row.append(release);summary.append(row);
  }
  issueRows.replaceChildren();
  const list=m.rows.filter(r=>(!f||r.seriesId===f)&&(!q||
   [r.seriesId,r.issueId,r.configurationId,...r.units.map(x=>x.recipeId)].some(x=>String(x||'').toLowerCase().includes(q)))&&(
    flag==='all'||(flag==='gaps'&&r.units.some(u=>u.draftState!=='approved-draft-indexed'))||
    (flag==='recovery'&&r.recoveryCandidates.length)||(flag==='published'&&r.releases.length)||(flag==='quality'&&r.quality.some(x=>x.classification!=='unknown'))));
  $('resultCount').textContent=list.length+' production issue/configuration rows. Configuration and assembled-recipe totals are not interchangeable.';
  for(const r of list){
   const tr=el('tr');
   td(tr,r.seriesId);let name=el('td');name.append(el('b',r.issueLabel),el('small',r.issueId,'muted'));tr.append(name);
   td(tr,r.assembledCount===null?'Unavailable':r.assembledCount);
   const den=el('td');den.append(el('b',r.denominator===null?'Unknown':r.denominator),el('small',r.denominatorSource==='curated-book'?'Complete book inventory':r.denominatorSource==='assembled-recipes'?'Assembled recipe inventory':'Unresolved source','muted'));tr.append(den);
   const ap=el('td');ap.append(chip(r.approvedIndexed+' indexed',r.approvedIndexed?'ok':'neutral'));tr.append(ap);
   td(tr,r.notIndexedCount===null?'Unknown':r.notIndexedCount+' unindexed');
   td(tr,r.keeperCoverage.total+' Keeper');
   td(tr,r.visualFindings?.length||0);
   const mastering=el('td');mastering.append(chip(r.mastering,r.mastering==='mastered'?'ok':'neutral'));tr.append(mastering);
   const exp=el('td');exp.append(chip(r.exporterReadiness,r.exporterReadiness==='inventory-complete-not-mastered'?'warn':'neutral'));tr.append(exp);
   const rel=el('td');rel.append(chip(r.published,r.releases.length?'ok':'neutral'));tr.append(rel);
   const detail=el('td');
   const d=el('details'),head=el('summary','Inspect exact IDs');
   d.append(head);
   const intro=el('p','Unindexed here is not evidence that the image was never generated or is absent from other storage. Approved draft records are not artistic, mastering, or export certification.','muted');
   d.append(intro);
   if(!r.sourceHealthy)d.append(el('p','Recipe inventory has source warnings or no assembled IDs; investigate before relying on its denominator.','warning'));
   if(r.sourceQualitySummary?.audited){d.append(el('p','Binary source facts: '+r.sourceQualitySummary.audited+' files examined; '+r.sourceQualitySummary.profileUnspecified+' with unspecified color profile; '+r.sourceQualitySummary.shortEdgeUnder2000+' with a native short edge below 2,000 pixels. These are observations, not a universal print standard.','muted'))}
   if(r.quality.length){const qblock=el('div');qblock.append(el('b','Source-quality findings: '));for(const item of r.quality)qblock.append(el('p',item.summary+' ('+item.source+')','muted'));d.append(qblock)}
   if(r.recoveryCandidates.length){d.append(el('b','Recovery candidates'));const ul=el('ul');r.recoveryCandidates.forEach(x=>ul.append(el('li',x.recipeId+' — '+x.status+': '+x.note)));d.append(ul)}
   if(r.exportEvidence){
    d.append(el('p','B3 exporter audit: '+r.exportEvidence.status+(r.exportEvidence.reason?' · '+r.exportEvidence.reason:''),'muted'))
   }
   if(r.visualFindings?.length){
    d.append(el('b','Scoped C3 visual / released-canon findings'));
    const ul=el('ul');
    for(const finding of r.visualFindings){
      const li=el('li',finding.id+' ['+finding.severity+']: '+finding.observation+' Required review: '+finding.requiredCorrection);
      for(const url of finding.sourceEvidence||[]){li.append(document.createTextNode(' '),showLink(url,'Source'))}
      ul.append(li);
    }
    d.append(ul);
   }
   if(r.releases.length){const pub=el('p');pub.append(el('b','Authoritative collected edition: '));r.releases.forEach(x=>{pub.append(showLink('https://star-splitter-visions.vercel.app'+x.externalLink,x.catalogId+' · '+x.title));pub.append(document.createTextNode(' '))});d.append(pub)}
   if(r.sourceFiles.length){const src=el('p');src.append(el('b','Sources: '));r.sourceFiles.forEach((p,i)=>{if(i)src.append(document.createTextNode(' · '));src.append(showLink(githubFile(p),p.split('/').at(-1))) });d.append(src)}
   const table=el('table',undefined,'units');const thead=el('thead'),hr=tableRow(['Exact recipe ID','Assembly','Draft record','Recovery','Release link']);thead.append(hr);table.append(thead);
   const tb=el('tbody');
   r.units.forEach(u=>{const item=el('tr');td(item,u.recipeId);td(item,u.inBook?'Book + '+(u.inRecipe?'recipe':'editorial/extra'):u.inRecipe?'Recipe':'Unresolved');
     const status=el('td');status.append(chip(u.draftState,u.draftState==='approved-draft-indexed'?'ok':u.recovery?'warn':'neutral'));
     if(u.imagePath){status.append(el('small',' ', 'muted'),showLink(githubFile(u.imagePath),'source image'))}
     item.append(status);if(u.sourceQualityObservation){const z=u.sourceQualityObservation;status.append(el('small',z.width+'×'+z.height+' · '+z.colorProfile+' · '+z.mimeType,'muted'))}td(item,u.recovery?u.recovery.status:'Not recorded');const link=el('td');if(u.releaseLinks?.length){u.releaseLinks.forEach(x=>{link.append(showLink('https://star-splitter-visions.vercel.app'+x.path,x.label||'Released image'));link.append(document.createTextNode(' '))})}else link.textContent='Not linked';item.append(link);tb.append(item)});
   table.append(tb);let wrap=el('div',undefined,'scroll');wrap.append(table);d.append(wrap);detail.append(d);tr.append(detail);issueRows.append(tr);
  }
 }
 seriesFilter.onchange=render;query.oninput=render;qualityFilter.onchange=render;render();
}
async function load(){
 const inputs=await Promise.all([get('data/shows.json'),get('production/portfolio-recipe-inventory.json'),get('production/drafts/manifest.json'),get('production/references/reference-keeper-manifest.json'),get('production/book-manifests.json'),get('production/released-links.json'),get('production/portfolio-quality-evidence.json'),get('production/visual-sources.json'),get('production/portfolio-source-quality.json'),get('production/audits/visual_review_2026-10-25.json'),get('production/book-export-coverage.json')]);
 const [shows,inventory,draftManifest,referenceManifest,books,releasedLinks,qualityEvidence,visuals,sourceQuality,visualAudit,exportCoverage]=inputs;
 const release={};
 await Promise.all(Object.entries(visuals.series||{}).map(async([sid,v])=>{
  if(!v.visionsSlug)return;
  const url='https://raw.githubusercontent.com/starsplitterrecords/StarSplitterVisions/main/sites/visions/src/content/series/'+encodeURIComponent(v.visionsSlug)+'.json';
  try{release[sid]=await (async()=>{const r=await fetch(url,{cache:'no-store'});if(!r.ok)throw Error('HTTP '+r.status);return r.json()})()}catch(e){release[sid]={error:String(e)}}
 }));
 return window.RexProductionDashboard.build({shows,inventory,draftManifest,referenceManifest,books,releasedLinks,qualityEvidence,sourceQuality,visualAudit,exportCoverage,visionsMetadata:release});
}
load().then(draw).catch(e=>{$('loadState').textContent='Portfolio data could not be verified: '+e.message;$('loadState').className='error'});
})();