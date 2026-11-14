#!/usr/bin/env node
'use strict';
// Read-only: join the live assembler regression results to the exact registered units.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const reg=read(process.argv[2]||'portfolio-regression-report.json');
const inv=read(process.argv[3]||'production/portfolio-recipe-inventory.json');
const shows=read('data/shows.json'),out=process.argv[4]||'assembler-integrity-survey';
fs.mkdirSync(out,{recursive:true});
const configs=new Map(shows.map(x=>[x.id,x])), checks=new Map(reg.issues.map(x=>[x.id,x]));
const findings=new Map(), k=(s,u)=>s+'::'+u;
function add(s,u,category,severity,detail){const id=k(s,u),a=findings.get(id)||[];if(!a.some(x=>x.category===category&&x.detail===detail))a.push({category,severity,detail});findings.set(id,a)}
const structural=new Set(['ASSEMBLY','LOAD_SHOW','MISSING_RECIPE_ID','DUPLICATE_RECIPE_ID','OUT_OF_RANGE_DIALOGUE_INDEX','MULTIPLE_DIALOGUE_OWNERS','SPEAKER_PANEL_CONFLICT','UNEXPECTED_PANEL_COUNT_MISMATCH']);
for(const f of reg.failures)if(structural.has(f.code))add(f.show,f.scene||'',f.code,['ASSEMBLY','LOAD_SHOW'].includes(f.code)?'BLOCKER':'STRUCTURAL',f.reason);
for(const [field,category,format] of [
 ['highDensity','DENSITY_WARNING',x=>(x.warnings||[]).join(' | ')],
 ['ambiguousDialogueMapping','DIALOGUE_PANEL_AMBIGUITY',x=>x.reason+(x.unmapped?' ('+x.unmapped+' unmapped)':'')],
 ['unresolvedSpeaker','UNRESOLVED_SPEAKER_HANDLE',x=>x.handle],
 ['panelMetadataDiscrepancies','PANEL_COUNT_MISMATCH',x=>'Declared '+x.declared+' vs actual '+x.panels]
])for(const x of reg.risks[field]||[])add(x.show,x.recipe,category,'DIAGNOSTIC',format(x));
const unreviewed=new Map();
for(const f of reg.failures)if(f.code.startsWith('NEW_UNREVIEWED_'))unreviewed.set(k(f.show,f.scene),(unreviewed.get(k(f.show,f.scene))||0)+1);
const pages=[],issues=[],seriesMap=new Map(),details=[];
function series(s,name){if(!seriesMap.has(s))seriesMap.set(s,{seriesId:s,seriesName:name,configurations:0,units:0,assembled:0,blocked:0,structural:0,flagged:0,unreviewed:0});return seriesMap.get(s)}
for(const row of inv.configurations){
 const show=configs.get(row.showId);
 assert(show&&checks.has(row.showId),'Missing show/loaded regression row '+row.showId);
 const group=series(row.seriesId,show.seriesName||row.seriesId);
 group.configurations++;
 const issue={seriesId:row.seriesId,seriesName:group.seriesName,issueId:row.issueId,issueLabel:row.issueLabel,configuration:row.showId,units:0,assembled:0,blocked:0,structural:0,flagged:0,unreviewed:0,firstBlockers:[],firstDiagnostics:[],sourceFiles:row.sourceFiles,sourceOverlays:row.sourceOverlays};
 const approved=new Set(row.approvedRecipeIds);
 for(const unit of row.recipeIds){
  const flags=findings.get(k(row.showId,unit))||[];
  const blocked=flags.some(f=>f.severity==='BLOCKER'),struct=flags.some(f=>f.severity==='STRUCTURAL'),diagnostic=flags.some(f=>f.severity==='DIAGNOSTIC');
  const status=blocked?'ASSEMBLY_BLOCKER':struct?'STRUCTURAL_DEFECT':diagnostic?'READABLE_WITH_DIAGNOSTICS':'READABLE';
  const unreview=unreviewed.get(k(row.showId,unit))||0;
  const p={seriesId:row.seriesId,seriesName:group.seriesName,issueId:row.issueId,issueLabel:row.issueLabel,configuration:row.showId,unitId:unit,status,approvedDraftIndexed:approved.has(unit),unitLabel:row.unitLabel,findings:flags,unreviewed:unreview,sourceFiles:row.sourceFiles,sourceOverlays:row.sourceOverlays};
  pages.push(p);group.units++;issue.units++;group.unreviewed+=unreview;issue.unreviewed+=unreview;
  if(blocked){group.blocked++;issue.blocked++;if(issue.firstBlockers.length<8)issue.firstBlockers.push(unit)}
  else{group.assembled++;issue.assembled++}
  if(struct){group.structural++;issue.structural++}
  if(diagnostic){group.flagged++;issue.flagged++;if(issue.firstDiagnostics.length<8)issue.firstDiagnostics.push(unit)}
  for(const f of flags)details.push({seriesId:row.seriesId,issueId:row.issueId,configuration:row.showId,unitId:unit,status,...f});
 }
 issues.push(issue);
}
assert.equal(pages.length,inv.counts.registeredRecipeUnitsAcrossConfigurations,'Unit count mismatch');
assert.equal(issues.length,shows.length,'Configuration count mismatch');
assert.equal(pages.filter(p=>p.status!=='ASSEMBLY_BLOCKER').length,reg.assembledRecipes,'Live assembler count mismatch');
const seriesRows=[...seriesMap.values()].sort((a,b)=>a.seriesName.localeCompare(b.seriesName));
issues.sort((a,b)=>a.seriesName.localeCompare(b.seriesName)||a.configuration.localeCompare(b.configuration));
const byCategory={};for(const f of details)byCategory[f.category]=(byCategory[f.category]||0)+1;
const byRegression={};for(const f of reg.failures)byRegression[f.code]=(byRegression[f.code]||0)+1;
const summary={timestamp:new Date().toISOString(),commit:reg.baseCommit||process.env.GITHUB_SHA||null,configurations:shows.length,series:seriesRows.length,unitOccurrences:pages.length,assembled:reg.assembledRecipes,assemblyBlockers:pages.filter(p=>p.status==='ASSEMBLY_BLOCKER').length,structuralDefectUnits:pages.filter(p=>p.status==='STRUCTURAL_DEFECT').length,flaggedUnits:pages.filter(p=>p.findings.some(f=>f.severity==='DIAGNOSTIC')).length,byCategory,regressionFailureRecords:reg.failures.length,byRegression,approved:reg.approved,historicalExceptions:reg.historicalExceptions,limitations:reg.untested};
const quote=v=>'"'+String(v==null?'':typeof v==='object'?JSON.stringify(v):v).replace(/"/g,'""').replace(/\r?\n/g,' ')+'"';
function csv(file,headers,rows){fs.writeFileSync(path.join(out,file),[headers.map(quote).join(','),...rows.map(r=>r.map(quote).join(','))].join('\n')+'\n')}
csv('page-by-page.csv',['Series','Series title','Issue','Issue label','Configuration','Page / unit','Assembly status','Approved draft indexed','Unit label','Finding codes','Exact diagnostic','New unreviewed risk records','Source files','Overlays'],pages.map(p=>[p.seriesId,p.seriesName,p.issueId,p.issueLabel,p.configuration,p.unitId,p.status,p.approvedDraftIndexed,p.unitLabel,p.findings.map(f=>f.category).join(' | '),p.findings.map(f=>f.detail).join(' | '),p.unreviewed,p.sourceFiles.join(' | '),p.sourceOverlays.map(x=>x.file).join(' | ')]));
csv('issue-by-issue.csv',['Series','Title','Issue','Issue label','Configuration','Units','Assembled','Blocked','Structural defects','Flagged','Unreviewed risks','First blockers','First flagged','Source files','Overlays'],issues.map(p=>[p.seriesId,p.seriesName,p.issueId,p.issueLabel,p.configuration,p.units,p.assembled,p.blocked,p.structural,p.flagged,p.unreviewed,p.firstBlockers.join(' | '),p.firstDiagnostics.join(' | '),p.sourceFiles.join(' | '),p.sourceOverlays.map(x=>x.file).join(' | ')]));
csv('series-by-series.csv',['Series','Title','Configurations','Units','Assembled','Blocked','Structural defects','Flagged','Unreviewed risks'],seriesRows.map(p=>[p.seriesId,p.seriesName,p.configurations,p.units,p.assembled,p.blocked,p.structural,p.flagged,p.unreviewed]));
csv('findings.csv',['Series','Issue','Configuration','Page / unit','Status','Category','Severity','Exact diagnostic'],details.map(f=>[f.seriesId,f.issueId,f.configuration,f.unitId,f.status,f.category,f.severity,f.detail]));
fs.writeFileSync(path.join(out,'full-audit.json'),JSON.stringify({summary,series:seriesRows,issues,pages,findings:details},null,2)+'\n');
const md=['# RexPrompt assembler readability survey','','Source commit: '+summary.commit,'Generated: '+summary.timestamp,'','## Coverage','- '+summary.series+' series / '+summary.configurations+' configurations / '+summary.unitOccurrences+' production-unit occurrences','- '+summary.assembled+' successfully assembled / '+summary.assemblyBlockers+' blocked','- '+summary.flaggedUnits+' units have at least one nonfatal diagnostic; findings may overlap','','## Series','| Series | Configs | Units | Assembly blockers | Diagnostic-flagged units |','|---|---:|---:|---:|---:|',...seriesRows.map(x=>'| '+x.seriesName+' | '+x.configurations+' | '+x.units+' | '+x.blocked+' | '+x.flagged+' |'),'','## Issues','| Series | Issue | Units | Blocked | Flagged | First affected units |','|---|---|---:|---:|---:|---|',...issues.map(x=>'| '+x.seriesName+' | '+x.issueLabel+' ('+x.configuration+') | '+x.units+' | '+x.blocked+' | '+x.flagged+' | '+(x.firstBlockers.length?x.firstBlockers.join(', '):x.firstDiagnostics.slice(0,3).join(', '))+' |'),'','## Interpretation','The pages CSV enumerates every assembled unit and its exact configuration and source files. Assembly blockers actually failed the live assembler. Diagnostic warnings indicate potential issues but are not failures.','Unit can mean comic page, scene, cover, cast page, or editorial material. Overlapping configurations are counted separately.','The survey does not judge image pixels, true lettering, dramatic quality, or editorial approval.'];
fs.writeFileSync(path.join(out,'SUMMARY.md'),md.join('\n')+'\n');
console.log('ASSEMBLER_SURVEY_COMPLETE '+JSON.stringify(summary));
