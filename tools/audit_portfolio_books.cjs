#!/usr/bin/env node
'use strict';
/**
 * Portfolio-wide source audit for complete-book manifests.
 * Read-only by default. --write refreshes source-verified inventories and
 * a complete registry coverage report. --check rejects stale committed data.
 * Does not infer or invent missing production units.
 */
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const ROOT=path.resolve(__dirname,'..');
const SHOWS=JSON.parse(fs.readFileSync(path.join(ROOT,'data/shows.json'),'utf8'));
const BOOK_PATH=path.join(ROOT,'production/book-manifests.json');
const AUDIT_PATH=path.join(ROOT,'production/book-export-coverage.json');
const HUMAN_PATH=path.join(ROOT,'production/PORTFOLIO_BOOK_EXPORT_COVERAGE.md');
const STRUCT_PATH=path.join(ROOT,'production/issue-structure.json');
const CURRENT=JSON.parse(fs.readFileSync(BOOK_PATH,'utf8'));
const DRAFTS=JSON.parse(fs.readFileSync(path.join(ROOT,'production/drafts/manifest.json'),'utf8')).drafts;
const cache=new Map(),issues={},issueStructures={},rows=[],diagnostics=[];
const isShelf=s=>s.unitLabel==='COVER'||s.unitLabel==='EDITORIAL PAGE'||/cover shelf/i.test(s.issueLabel||'')||/cover shelf/i.test(s.name||'');
function pathOf(show,file){
 const base=show.basePath||'data';
 const rel=base==='data'?path.join(base,file):path.join(base,file);
 const full=path.resolve(ROOT,rel);
 if(!full.startsWith(ROOT+path.sep))throw Error('unsafe show source path '+rel);
 return full;
}
function load(full){
 if(cache.has(full))return cache.get(full);
 if(!fs.existsSync(full))throw Error('missing recipe file: '+path.relative(ROOT,full));
 let raw=fs.readFileSync(full,'utf8'),parsed;
 if(full.endsWith('.gzb64'))parsed=JSON.parse(zlib.gunzipSync(Buffer.from(raw.trim(),'base64')).toString('utf8'));
 else parsed=JSON.parse(raw);
 if(!Array.isArray(parsed))throw Error('non-array recipe source: '+path.relative(ROOT,full));
 if(parsed.some(x=>!x||typeof x.id!=='string'))throw Error('invalid recipe ID: '+path.relative(ROOT,full));
 cache.set(full,parsed);
 return parsed;
}
function fromSpec(show,spec){
 const file=typeof spec==='string'?spec:spec.file;
 if(!file)throw Error('empty source overlay '+show.id);
 let a=load(pathOf(show,file));
 if(typeof spec==='object'&&spec.includeIds)a=a.filter(x=>spec.includeIds.includes(x.id));
 if(typeof spec==='object'&&spec.includeIdPattern){const re=new RegExp(spec.includeIdPattern);a=a.filter(x=>re.test(x.id));}
 return a;
}
function select(show){
 const entries=[];
 const loadList=[...(show.scenesFiles||[]),...(show.scenesFile?[show.scenesFile]:[])];
 for(const file of loadList)entries.push(...fromSpec(show,file));
 for(const overlay of show.sceneOverlays||[]){if(!overlay.mergeById)entries.push(...fromSpec(show,overlay));}
 const regex=show.includeIdPattern?new RegExp(show.includeIdPattern):null;
 const selected=entries.filter(x=>!regex||regex.test(x.id));
 const found=new Set(),out=[];
 for(const e of selected){if(found.has(e.id))throw Error('duplicate source unit '+show.id+' '+e.id);found.add(e.id);out.push(e.id);}
 return out;
}
function seriesOf(show){
 if(show.seriesId)return show.seriesId;
 const base=(show.basePath||'').split('/').at(-1);
 if(base==='stardust-station')return base;
 if(base==='azure-reach-s1')return 'azure-reach';
 if(base==='vikings-2026-s1')return 'vikings-2026';
 if(base==='backyard-rockets-s1')return 'backyard-rockets';
 if(base==='sunforge-outlaw-s1')return 'sunforge-outlaw';
 return base||null;
}
function findSupplement(show,pattern){
 const result=[];
 const local=pathOf(show,'covers.json');
 if(fs.existsSync(local))result.push(...load(local).map(x=>x.id));
 for(const shelf of SHOWS.filter(s=>s.unitLabel==='COVER'&&seriesOf(s)===seriesOf(show))){
   try{result.push(...select(shelf));}catch(e){diagnostics.push({selectorId:shelf.id,errors:['cover-shelf-unreadable:'+e.message]});}
 }
 return [...new Set(result)].filter(id=>pattern.test(id));
}
function groupOf(id){
 const match=id.match(/^(EFW_S1E|BR_S1E)(\d{2})_/);
 return match?match[1]+match[2]:null;
}
function supplement(show,selected){
 const series=seriesOf(show);
 const example=selected[0]||'';
 let cover=null,front=null,back=null,structuralRisk=[];
 if(series==='shattering'){const m=example.match(/^(SHAT_I\d\d)_/);if(m)cover=m[1]+'_COVER';}
 if(series==='low-tide-signal'){const m=example.match(/^(LTS_C\d\d)_/);if(m)cover=m[1]+'_COVER';}
 if(series==='azure-reach'){const m=example.match(/^(AZR_S1E\d\d)_/);if(m)cover=m[1]+'_COVER';}
 if(series==='stardust-station'){const m=example.match(/^(SDS_S1E\d\d)_/);if(m)cover=m[1]+'_COVER';}
 if(series==='rex-fleet-academy-between-beacons'){cover='RFA_BB_I01_COVER';}
 if(series==='division-threshold'){const m=example.match(/^(DT_E\d{3})_/);if(m){cover=m[1]+'_COVER';front=m[1]+'_INTRO';back=m[1]+'_TEASER';}}
 let before=[],after=[];
 if(cover&&!selected.includes(cover)){
   const names=findSupplement(show,/COVER$/);
   if(names.includes(cover))before.push(cover);
   else structuralRisk.push('referenced-cover-not-found:'+cover);
 }
 if(front&&!selected.includes(front)){
   const file=pathOf(show,'editorial_pages.json');
   if(fs.existsSync(file)&&load(file).some(x=>x.id===front))before.push(front);
   else structuralRisk.push('editorial-intro-not-found:'+front);
 }
 if(back&&!selected.includes(back)){
   const file=pathOf(show,'editorial_pages.json');
   if(fs.existsSync(file)&&load(file).some(x=>x.id===back))after.push(back);
   else structuralRisk.push('editorial-teaser-not-found:'+back);
 }
 return {units:[...before,...selected,...after],risks:structuralRisk};
}
// Production role evidence is derived from registered source units, never invented pages.
function sourceRecords(show,ids){
 const wanted=new Set(ids),found=new Map();
 const specs=[...(show.scenesFiles||[]),...(show.scenesFile?[show.scenesFile]:[]),
   ...(show.sceneOverlays||[]).filter(o=>!o.mergeById)];
 for(const spec of specs)for(const item of fromSpec(show,spec)){
   if(wanted.has(item.id)&&!found.has(item.id))found.set(item.id,item);
 }
 return found;
}
function roleOf(id,record,index,total){
 const kind=String(record?.pageKind||'').toLowerCase(),title=String(record?.title||''),summary=String(record?.summary||'');
 if(/_COVER$|_COVER_PAGE$/.test(id))return ['cover','source-id'];
 if(kind==='cover')return ['cover','source-page-kind'];
 if(/^Issue\s+\d+\s+Cover\b/i.test(title))return ['cover','source-title'];
 if(/_CAST$/.test(id)||kind==='cast')return ['cast','source-id-or-page-kind'];
 if(/_EDITOR_ENDMATTER$/.test(id))return ['end-matter','source-id'];
 if(/_DOC_[A-Z0-9]+$/.test(id))return ['interstitial-document','source-id'];
 if(/_EDITOR_V8_OPEN_[0-9A-Z]+$|_EDITOR_OPEN$|_EDITOR_INTRO$|_INTRO$|_EDITOR$/.test(id))return ['opening-editorial','source-id'];
 if(/_EDITOR_NEXT$|_EDITOR_TEASER$|_TEASER$/.test(id))return ['teaser','source-id'];
 if(/_EDITOR_CLOSE$|_EDITOR_OUTRO$|_CLOSING$/.test(id))return ['closing-editorial','source-id'];
 if(kind==='municipal-editorial'||/\b(?:Editor Intro|From the Editor)\b/i.test(title))return ['opening-editorial','source-page-kind-or-title'];
 if(kind==='closing-editorial')return ['closing-editorial','source-page-kind'];
 if(index===total-1&&(/^(Next:|Next Course\b)/i.test(title)||/Will Return/i.test(title)||/^Closing (?:Academy )?teaser\b/i.test(summary)))return ['teaser','source-final-title-or-summary'];
 if(index===total-1&&/^Editorial closing splash/i.test(summary))return ['closing-editorial','source-final-summary'];
 if(index===0&&/^Opening (?:Academy )?splash/i.test(summary))return ['opening-splash','source-first-summary'];
 if(index===0&&/^Title splash/i.test(summary))return ['title-splash','source-first-summary'];
 return null;
}
function recordStructure(show,issueId,units,bookState,options={}){
 const key=[seriesOf(show),issueId].join('::');
 const records=sourceRecords(show,units),specialUnits=[];
 for(let i=0;i<units.length;i++){
  const role=roleOf(units[i],records.get(units[i]),i,units.length);
  if(role)specialUnits.push({unitId:units[i],position:i+1,role:role[0],evidence:role[1]});
 }
 const coverInOrder=specialUnits.some(u=>u.role==='cover'&&u.position===1);
 const coverCandidates=options.coverCandidates||[];
 issueStructures[key]={seriesId:seriesOf(show),issueId,issueLabel:options.issueLabel||show.issueLabel||show.name,
  sourceSelectorId:show.id,selectorRegistered:options.selectorRegistered!==false,
  readingOrder:bookState,sourceUnitCount:units.length,
  specialUnits,coverStatus:coverInOrder?'ordered':coverCandidates.length?'available-in-separate-shelf':'not-established',
  ...(coverCandidates.length?{separateCoverCandidates:coverCandidates}:{})};
}

function countApproved(series,issue,units){
 const approved=[],missing=[],invalid=[],corrupt=[];
 for(const id of units){
  const entry=DRAFTS[[series,issue,id].join('::')];
  if(!entry){missing.push(id);continue;}
  if(entry.status!=='approved-production-draft'||!entry.image){invalid.push(id);continue;}
  const image=path.resolve(ROOT,entry.image),approvedDir=path.resolve(ROOT,'production/drafts');
  if(!image.startsWith(approvedDir+path.sep)||!fs.existsSync(image)||!fs.statSync(image).isFile()){
    corrupt.push({id,reason:'approved-binary-unavailable'});continue;
  }
  const bytes=fs.readFileSync(image);
  if(bytes.subarray(0,40).toString().startsWith('version https://git-lfs.github.com')){
    corrupt.push({id,reason:'git-lfs-pointer-not-image'});continue;
  }
  const sig=bytes.subarray(0,8).equals(Buffer.from('89504e470d0a1a0a','hex'))?'image/png':
    bytes.length>=3&&bytes.subarray(0,3).equals(Buffer.from('ffd8ff','hex'))?'image/jpeg':
    bytes.toString('ascii',0,4)==='RIFF'&&bytes.toString('ascii',8,12)==='WEBP'?'image/webp':null;
  if(sig!==entry.mimeType){corrupt.push({id,reason:'MIME-or-signature-mismatch'});continue;}
  const hash=crypto.createHash('sha256').update(bytes).digest('hex');
  if(entry.sha256&&hash!==entry.sha256.toLowerCase()){
    corrupt.push({id,reason:'SHA-256-mismatch'});continue;
  }
  approved.push(id);
 }
 return {approvedCount:approved.length,missingImages:missing,unapprovedImages:invalid,
   corruptImages:corrupt,missingCount:missing.length+invalid.length+corrupt.length};
}
function structureCheck(units){
 const errs=[];
 if(!units.length)errs.push('no-production-units');
 if(units.length!==new Set(units).size)errs.push('duplicate-production-units');
 const covers=units.filter(x=>/(?:_COVER|_COVER_PAGE)$/.test(x));
 if(covers.length>1)errs.push('multiple-covers');
 if(covers.length&&units[0]!==covers[0])errs.push('cover-not-first');
 const pages=units.filter(x=>/_P\d+$/.test(x));
 if(pages.length>1){const nums=pages.map(x=>Number(x.match(/_P(\d+)$/)[1]));for(let i=1;i<nums.length;i++)if(nums[i]!==nums[i-1]+1){errs.push('nonconsecutive-story-pages');break;}}
 return errs;
}
for(const show of SHOWS){
 if(isShelf(show)){rows.push({selectorId:show.id,kind:'auxiliary-shelf',seriesId:seriesOf(show),status:'not-a-book'});continue;}
 if(show.unitLabel==='SCENE'){rows.push({selectorId:show.id,kind:'non-comic-scene',seriesId:seriesOf(show),status:'not-a-book'});continue;}
 const seriesId=seriesOf(show),issueId=show.id;
 let selected;
 try{selected=select(show);}catch(e){rows.push({selectorId:issueId,seriesId,kind:'issue-or-season-selector',status:'uncurated',reason:'source-unreadable',detail:String(e.message)});continue;}
 if(!selected.length){rows.push({selectorId:issueId,seriesId,kind:'issue-or-season-selector',status:'uncurated',reason:'no-source-units'});continue;}
 const groups=[...new Set(selected.map(groupOf).filter(Boolean))];
 if(groups.length>1){
   const subissues=groups.map(group=>{
     const actual=selected.filter(id=>groupOf(id)===group);
     const prefix=group+'_COVER',coverCandidates=findSupplement(show,/_COVER$/).filter(id=>id===prefix);
     const derivedId=show.id+'-e'+group.slice(-2);
     recordStructure(show,derivedId,actual,'source-order-only',{
       selectorRegistered:false,issueLabel:'Episode '+Number(group.slice(-2)),coverCandidates});
     return {sourceGroup:group,sourceUnitCount:actual.length,
       firstUnit:actual[0],lastUnit:actual.at(-1),
       issueSelectorRegistered:false,
       status:'uncurated',reason:'season-selector-not-split-into-issue-inventories'};
   });
   rows.push({selectorId:issueId,seriesId,kind:'multi-issue-season-selector',status:'uncurated',
     reason:'season-combines-multiple-issues',groupCount:groups.length,groups,subissues,sourceUnitCount:selected.length});
   continue;
 }
 const cur=CURRENT.issues[[seriesId,issueId].join('::')];
 const sup=supplement(show,selected);
 const proposed=sup.units;
 const errs=[...sup.risks,...structureCheck(proposed)];
 const coverPresent=proposed.some(x=>/(?:_COVER|_COVER_PAGE)$/.test(x))||(
 seriesId==='vikings-2026'&&proposed[0]&&/_P01$/.test(proposed[0]));
 // No cover or other defined book-start marker: source pages alone don't
 // establish that this is a complete published BOOK. Keep them uncurated.
 if(!coverPresent)errs.push('book-cover-not-established');
 if(cur){
   const missingFromProposal=proposed.filter(x=>!cur.units.includes(x));
   const phantom=cur.units.filter(x=>!proposed.includes(x));
   if(missingFromProposal.length||phantom.length)errs.push('existing-manifest-source-mismatch');
   if(!errs.length)issues[[seriesId,issueId].join('::')]=cur;
 }else if(!errs.length){
   issues[[seriesId,issueId].join('::')]={
     seriesId,issueId,orderPolicy:'source-verified-series-specific-reading-order',
     sourceShowId:show.id,units:proposed
   };
 }
 const book=issues[[seriesId,issueId].join('::')];
 recordStructure(show,issueId,book?.units||proposed,book?'curated-complete-book':'source-order-only');
 const counts=countApproved(seriesId,issueId,book?.units||proposed);
 rows.push({selectorId:issueId,seriesId,kind:'issue',status:!book?'uncurated':counts.missingCount?'blocked-missing-images':'complete-draft-export-supported',
   expectedUnits:book?.units.length||proposed.length,approvedImages:counts.approvedCount,missingImageCount:counts.missingCount,
   missingImageIds:counts.missingImages,unapprovedImageIds:counts.unapprovedImages,corruptImageIds:counts.corruptImages,
   reason:errs.length?errs.join(', '):counts.missingCount?'missing-approved-images':null,
   inventorySource:cur?'preexisting-verified':book?'derived-from-registered-source':'candidate-needs-curation',
   sourceShowId:show.id});
 if(errs.length)diagnostics.push({selectorId:show.id,errors:errs});
}
for(const [key,value] of Object.entries(CURRENT.issues)){
 if(!issues[key]&&!rows.some(r=>[r.seriesId,r.selectorId].join('::')===key)){
  diagnostics.push({selectorId:key,errors:['orphan-manifest-no-selector']});
 }
}
const report={schemaVersion:1,registrySelectors:SHOWS.length,
  issuesWithManifest:Object.keys(issues).length,
  sourceAudit:'registered show sources, including gzip-base64 overlays and separate cover/editorial shelves',
  statuses:Object.fromEntries([...new Set(rows.map(r=>r.status))].sort().map(s=>[s,rows.filter(r=>r.status===s).length])),
  entries:rows,diagnostics};
const manifest={...CURRENT,issues:Object.fromEntries(Object.entries(issues).sort(([a],[b])=>a.localeCompare(b)))};
const structure={schemaVersion:1,description:'Source-supported page roles and issue reading order. Source-order-only is not a verified complete book.',
  issues:Object.fromEntries(Object.entries(issueStructures).sort(([a],[b])=>a.localeCompare(b)))};
const normalized=x=>JSON.stringify(x,null,2)+'\n';
function markdown(){
 const lines=['# Visions complete-book export portfolio audit','','Generated from live registered source recipes, curated inventories and exact approved binaries. This is **export coverage, not mastering or release approval**.','','## Summary','','- Registered selectors: '+report.registrySelectors+' (includes shelves and non-comic selectors)','- Curated complete-book inventories: '+report.issuesWithManifest,'- Full approved draft coverage: '+(report.statuses['complete-draft-export-supported']||0),'- Curated but missing approved images: '+(report.statuses['blocked-missing-images']||0),'- Uncurated issue/season selectors: '+(report.statuses.uncurated||0),'- Auxiliary selectors not representing books: '+(report.statuses['not-a-book']||0),'','## Individual issue inventories','','| Series | Registered selector | Inventory | Approved / expected | Blocking reason |','|---|---|---|---:|---|'];
 for(const r of rows.filter(x=>x.status!=='not-a-book')){
   const expected=r.expectedUnits??'?',approved=r.approvedImages??0;
   const reason=(r.reason||'—').replace(/\|/g,'/');
   lines.push('| '+r.seriesId+' | '+r.selectorId+' | '+r.status+' | '+approved+' / '+expected+' | '+reason+' |');
   for(const part of r.subissues||[])lines.push('| '+r.seriesId+' | '+part.sourceGroup+' (not separately registered) | uncurated subissue | 0 / '+part.sourceUnitCount+' | '+part.reason+' |');
 }
 lines.push('','The machine-readable `production/book-export-coverage.json` contains the exact missing IDs and source provenance for every selector. No unknown cover, cast, editorial or teaser is invented. A manifest-backed and fully approved issue supports a review export; a mastered and approved release is a separate editorial/production gate.','','Generated by `node tools/audit_portfolio_books.cjs --write`.');return lines.join('\n')+'\n';
}
if(process.argv.includes('--write')){
 fs.writeFileSync(BOOK_PATH,normalized(manifest));
 fs.writeFileSync(AUDIT_PATH,normalized(report));
 fs.writeFileSync(HUMAN_PATH,markdown());
 fs.writeFileSync(STRUCT_PATH,normalized(structure));
}else if(process.argv.includes('--check')){
 assert.equal(fs.readFileSync(BOOK_PATH,'utf8'),normalized(manifest),'Complete-book inventory out of sync with registered source');
 assert.equal(fs.readFileSync(AUDIT_PATH,'utf8'),normalized(report),'Portfolio coverage audit out of sync with registered source');
 assert.equal(fs.readFileSync(HUMAN_PATH,'utf8'),markdown(),'Portfolio human coverage report out of sync');
 assert.equal(fs.readFileSync(STRUCT_PATH,'utf8'),normalized(structure),'Issue structural roles out of sync');
}
console.log('AUDIT_SUMMARY '+JSON.stringify({registered:report.registrySelectors,manifests:report.issuesWithManifest,statuses:report.statuses,issues:rows.filter(x=>x.kind==='issue').length}));
for(const r of rows)console.log('AUDIT_ISSUE '+JSON.stringify({selector:r.selectorId,series:r.seriesId,status:r.status,expected:r.expectedUnits,approved:r.approvedImages,missing:r.missingImageCount,reason:r.reason}));
if(process.argv.includes('--strict')){
 const bad=rows.filter(r=>r.status==='uncurated');
 if(bad.length)process.exitCode=1;
}
