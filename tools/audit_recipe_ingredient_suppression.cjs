#!/usr/bin/env node
'use strict';
// Read-only inventory of the final current RexPrompt recipes and their real assembler output.
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib'),vm=require('node:vm');
const root=path.resolve(__dirname,'..'),dest='reports/recipe-suppression/2026-11-07';
const read=p=>fs.readFileSync(path.join(root,p),'utf8'),json=p=>JSON.parse(read(p)),exists=p=>fs.existsSync(path.join(root,p));
const html=read('index.html'),start=html.indexOf('const SHOW_MANIFEST='),end=html.indexOf('function safeFilePart(',start);
if(start<0||end<start)throw Error('Cannot locate canonical assembler');
const ctx=vm.createContext({});
vm.runInContext(html.slice(start,end)+';globalThis.audit={assembleScene,pageAssembly,normalizeScenes,normalizeOverlay,applyOverlay,applyDialogueOverlay};',ctx);
const {assembleScene,pageAssembly,normalizeScenes,normalizeOverlay,applyOverlay,applyDialogueOverlay}=ctx.audit;
const shows=json('data/shows.json'),occurrences=[],unique=new Map(),errors=[],cache=new Map(),shelves=new Map();
const names=['summary','production','setting','settingContinuity','region','factions','characters','direction'];
const esc=x=>String(x??'').replace(/\|/g,'/').replace(/\r?\n/g,' ').slice(0,220);
const csv=x=>'"'+String(x??'').replace(/"/g,'""')+'"';
function file(base,f,encoding){
 const p=path.posix.join(base,f),key=p+':'+encoding;
 if(cache.has(key))return cache.get(key);
 const raw=read(p),obj=encoding==='gzip-base64'?JSON.parse(zlib.gunzipSync(Buffer.from(raw.replace(/\s/g,''),'base64')).toString()):JSON.parse(raw);
 cache.set(key,obj);return obj;
}
function shelf(base){
 if(shelves.has(base))return shelves.get(base);
 const o={};
 for(const n of ['characters','settings','regions','factions','direction','dialogue']){
   const p=path.posix.join(base,n+'.json');o[n+'.json']=exists(p)?json(p):{};
 }
 shelves.set(base,o);return o;
}
function getShow(show){
 const base=show.basePath||'data',cfg=path.posix.join(base,show.packageConfigFile||'assembler.json');
 const conf={...(exists(cfg)?json(cfg):{}),...show};
 const files=Array.isArray(conf.scenesFiles)?conf.scenesFiles:[conf.scenesFile||'scenes.json'];
 const provenance=new Map();
 let pages=[];
 for(const f of files){const v=normalizeScenes(file(base,f));pages.push(...v);for(const p of v)provenance.set(p.id,[f]);}
 if(conf.excludeSceneIds?.length){const ex=new Set(conf.excludeSceneIds);pages=pages.filter(p=>!ex.has(p.id));}
 for(const o of conf.sceneOverlays||[]){
   let v=normalizeOverlay(file(base,o.file,o.encoding));
   if(o.includeIds?.length){const ids=new Set(o.includeIds);v=v.filter(p=>ids.has(p.id));}
   if(o.excludeIds?.length){const ids=new Set(o.excludeIds);v=v.filter(p=>!ids.has(p.id));}
   for(const p of v)provenance.set(p.id,(provenance.get(p.id)||[]).concat(o.file));
   pages=applyOverlay(pages,v,o);
 }
 for(const o of conf.dialogueOverlays||[]){
   const v=normalizeOverlay(file(base,o.file,o.encoding));pages=applyDialogueOverlay(pages,v);
   for(const p of v)if(provenance.has(p.id))provenance.get(p.id).push(o.file);
 }
 if(conf.includeIdPattern){const re=new RegExp(conf.includeIdPattern);pages=pages.filter(p=>re.test(p.id||''));}
 return {base,conf,pages,provenance};
}
function issue(s,c){
 const m=String(s.id||'').match(/(?:^|_)(S\d+E\d{2}|I\d{2}|C\d{2}|E\d{2})(?:_|$)/);
 return m?m[1]:s.episode||c.issueLabel||c.seasonLabel||c.id;
}
function scan(p,c,refs,prev,i,provenance){
 const suppression=Array.isArray(p.promptSuppress)?p.promptSuppress:[];
 let text='',error='',flags=[];
 try{pageAssembly(p,c);text=assembleScene(p,{...refs,__show:c},i)}
 catch(e){error=String(e.message||e);flags.push('ASSEMBLY_ERROR')}
 const has=(key)=>text.includes('\n['+key+']\n');
 const visible=p.promptVisibleCastOnly===undefined?!!c.promptVisibleCastOnly:!!p.promptVisibleCastOnly;
 const charMode=suppression.includes('characters')?'none':(p.promptCharacterMode||(c.compactCharacters?'cast':'full'));
 const settingMode=p.promptSettingMode||'full';
 const panelMode=p.promptPanelMode||c.promptPanelMode||'original';
 const dialogueMode=p.promptDialogueMode||c.promptDialogueMode||'original';
 const cast=!!((p.characters||[]).length||(p.charactersInline||[]).length);
 const present={
 summary:!!p.summary,production:!!c.generationLine,setting:!!(p.settingText||p.setting),
 settingContinuity:!!(p.settingText&&p.setting),region:!!(p.regionText||p.region),
 factions:!!(p.factions||[]).length,characters:cast,direction:!!((p.direction||[]).length||(p.directionInline||[]).length)
 };
 const emitted={summary:!!p.summary&&!!text&&text.includes(p.summary.trim())&&!c.omitSummary&&!suppression.includes('summary'),
 production:!!c.generationLine&&!!text&&text.includes(c.generationLine)&&!suppression.includes('production'),
 setting:has('SETTING'),settingContinuity:has('SETTING CONTINUITY'),region:has('REGION'),
 factions:has('FACTIONS'),characters:has('CHARACTERS')||has('CAST'),direction:has('DIRECTION')};
 const status={};
 for(const k of names){
   if(error){status[k]=present[k]?'UNVERIFIED':'N/A';continue;}
   if(!present[k])status[k]='N/A';
   else if(k==='characters'&&visible&&charMode!=='none')status[k]=text.indexOf('\n=== ')>0?'VISUAL-REFS':'VISUAL-REFS?';
   else if(emitted[k])status[k]='ON';
   else if(suppression.includes(k))status[k]='OFF-page';
   else if(k==='summary'&&c.omitSummary)status[k]='OFF-config';
   else if(k==='factions'&&c.omitRoutineFactions&&!p.promptIncludeFactions)status[k]='OFF-config';
   else if(k==='characters'&&charMode==='none')status[k]='OFF-character-mode';
   else status[k]='OFF-other';
 }
 if(!error){
  if(p.panelPlan?.length&&!has('PANEL PLAN'))flags.push('PANEL_NOT_EMITTED');
  if((p.dialogueInline?.length||p.dialog?.length)&&!has('DIALOGUE'))flags.push('DIALOGUE_NOT_EMITTED');
  if(p.continuityFrom&&!has('CONTINUITY'))flags.push('CONTINUITY_NOT_EMITTED');
  if(cast&&charMode==='none'&&visible)flags.push('VISUAL_CAST_SUPPRESSED');
  if(!visible&&cast&&charMode==='full'){
    if(!p.promptCharacterMode)flags.push('FULL_CAST_BY_DEFAULT');
    if(prev&&(p.characters||[]).join('|')===(prev.characters||[]).join('|')&&(p.characters||[]).length)flags.push('REPEATED_FULL_CAST');
  }
  if(prev&&p.setting&&p.setting===prev.setting&&settingMode==='full'){
    if(status.setting==='ON'&&!p.settingText)flags.push('REPEATED_FULL_SETTING');
    if(status.settingContinuity==='ON')flags.push('REPEATED_SETTING_CONTINUITY');
  }
  if(status.summary==='ON'&&/^Primary composition:|^The page (shows|depicts)|^This page (shows|depicts)/i.test(p.summary||''))flags.push('TEMPLATE_SUMMARY');
  if(status.summary==='ON'&&prev?.summary&&p.summary.trim()===prev.summary.trim())flags.push('DUPLICATE_SUMMARY');
 }
 const own=['promptSuppress','promptCharacterMode','promptSettingMode','promptVisibleCastOnly','promptPanelMode','promptDialogueMode'].filter(k=>Object.prototype.hasOwnProperty.call(p,k));
 return {seriesId:c.seriesId||'(unknown)',seriesName:c.seriesName||c.name,
 issue:issue(p,c),unit:p.id||'(missing)',config:c.id,provenance:(provenance||[]).join('; '),
 explicit:own.length?'PAGE':'CONFIG/DEFAULT',own:own.join('; '),
 suppression:suppression.join('; '),charMode,
 charOrigin:p.promptCharacterMode?'PAGE':c.compactCharacters?'CONFIG':'DEFAULT',
 settingMode,settingOrigin:p.promptSettingMode?'PAGE':'DEFAULT',
 visible:visible?'yes':'no',visibleOrigin:p.promptVisibleCastOnly!==undefined?'PAGE':c.promptVisibleCastOnly!==undefined?'CONFIG':'DEFAULT',
 panelMode,dialogueMode,status,hasPanels:!!p.panelPlan?.length,hasDialogue:!!(p.dialogueInline?.length||p.dialog?.length),
 hasContinuity:!!p.continuityFrom,rawSummary:esc(p.summary||''),flags,error,chars:text.length};
}
for(const show of shows){
 try{
   const {base,conf,pages,provenance}=getShow(show),refs=shelf(base);
   let prev=null;
   pages.forEach((p,i)=>{
     const row=scan(p,conf,refs,prev,i,provenance.get(p.id));occurrences.push(row);prev=p;
     const key=row.seriesId+'::'+row.unit;
     if(!unique.has(key))unique.set(key,{...row,configs:[row.config]});
     else{
       const target=unique.get(key);
       target.configs.push(row.config);
       if(JSON.stringify(target.status)!==JSON.stringify(row.status)||target.suppression!==row.suppression)
         target.flags.push('CROSS_CONFIGURATION_CONFLICT');
     }
   });
 }catch(e){errors.push(show.id+': '+String(e.stack||e).slice(0,1000))}
}
const units=[...unique.values()].sort((a,b)=>a.seriesId.localeCompare(b.seriesId)||a.issue.localeCompare(b.issue,undefined,{numeric:true})||a.unit.localeCompare(b.unit,undefined,{numeric:true}));
const sid=[...new Set(units.map(x=>x.seriesId))].sort();
const dir=path.join(root,dest);fs.mkdirSync(dir,{recursive:true});
const columns=['seriesId','seriesName','issue','unit','config','provenance','explicit','own','suppression','charMode','charOrigin','settingMode','settingOrigin','visible','visibleOrigin','panelMode','dialogueMode',...names.map(x=>'section_'+x),'hasPanels','hasDialogue','hasContinuity','rawSummary','flags','error'];
const allcsv=[columns.join(',')];
for(const r of occurrences){
 const row={...r,...Object.fromEntries(names.map(x=>['section_'+x,r.status[x]])),flags:r.flags.join('; ')};
 allcsv.push(columns.map(k=>csv(row[k])).join(','));
}
fs.writeFileSync(path.join(dir,'all-configurations.csv'),allcsv.join('\n')+'\n');
function count(rows){const f={};for(const r of rows)for(const k of r.flags)f[k]=(f[k]||0)+1;return {units:rows.length,issues:new Set(rows.map(x=>x.issue)).size,explicit:rows.filter(x=>x.own.includes('promptSuppress')).length,suppressed:rows.filter(x=>x.suppression).length,default:rows.filter(x=>x.explicit!=='PAGE').length,flags:f};}
const main=[
 '# RexPrompt — All-series, issue-by-issue, page-by-page ingredient suppression audit','',
 'Source: current RexPrompt repository, AFTER applying all configured scene and dialogue overlays, including compressed sources. Assembled output uses the actual pageAssembly and assembleScene functions from index.html. No creative source or suppression setting changed.','',
 'Interpretation: PAGE means authored per-page setting; CONFIG means series/configuration inheritance; DEFAULT means assembler fallback. An empty promptSuppress means no page-specific suppression, NOT proof that the section is emitted. No ingredient content is different from an actively suppressed ingredient.','',
 'Flags identify candidates, not editorial findings or permission to suppress. Repeated setting descriptions across separate generation calls are often NECESSARY for continuity; they are not duplication inside a page prompt. Full content and neighboring beats require review before changing any page. Full Performance is separate from Rex Fleet.','',
 '## Coverage','',
 '- '+shows.length+' registered configurations; '+occurrences.length+' configured appearances; '+units.length+' unique series/unit pairs; '+sid.length+' distinct production series.',
 '- '+errors.length+' source loading failures; '+units.filter(x=>x.error).length+' assembly failures.',
 '',
 '## Results by series','',
 '| Series | Issues | Unique units | Explicit suppression list | Nonempty suppression | Entirely inherited page policy | Flagged units | Detailed audit |',
 '|---|---:|---:|---:|---:|---:|---:|---|'
];
const stats=[];
for(const seriesId of sid){
 const rows=units.filter(x=>x.seriesId===seriesId),c=count(rows),name=rows[0].seriesName;
 stats.push({seriesId,seriesName:name,...c});
 main.push('| '+esc(name)+' | '+c.issues+' | '+c.units+' | '+c.explicit+' | '+c.suppressed+' | '+c.default+' | '+rows.filter(x=>x.flags.length).length+' | [Every page]('+seriesId+'.md) |');
 const d=['# '+name+' — ingredient suppression by issue and page','',
 'Assembler output inspected after every registered overlay. The report is observational; flagged repetitions are candidates, not automatic approval to suppress.','',
 'Legend: N/A = ingredient absent in source; ON = emitted; OFF-page = suppressed in page; OFF-config = omitted by configuration; VISUAL-REFS = character handles emitted without roster prose. Character / setting origins P, C, D below are page, configuration, and assembler default.',''];
 for(const issue of [...new Set(rows.map(r=>r.issue))]){
   const rr=rows.filter(x=>x.issue===issue);
   d.push('## '+issue+' — '+rr.length+' units','','| Unit | Explicit suppressions | Character + setting + visual reference settings | Ingredient output | Review flags |',
     '|---|---|---|---|---|');
   for(const r of rr){
     const cp='character '+r.charMode+' ('+r.charOrigin+') · setting '+r.settingMode+' ('+r.settingOrigin+') · visible-only '+r.visible+' ('+r.visibleOrigin+')';
     const markers=names.map(k=>k+':'+r.status[k]).join(', ');
     d.push('| '+esc(r.unit)+' | '+esc(r.suppression||'∅')+' | '+esc(cp)+' | '+esc(markers)+' | '+esc(r.flags.join(', ')||'—')+' |');
   }
   d.push('');
 }
 d.push('## Traceback','','All configuration appearances and exact source/overlay paths are in [the full CSV](all-configurations.csv). A row with no flag is not a creative/visual quality approval.','');
 fs.writeFileSync(path.join(dir,seriesId+'.md'),d.join('\n')+'\n');
}
main.push('','## Flag explanation','',
 '- ASSEMBLY_ERROR / PANEL_NOT_EMITTED / DIALOGUE_NOT_EMITTED / CONTINUITY_NOT_EMITTED: verify assembler correctness; page does not have a validated complete output.',
 '- VISUAL_CAST_SUPPRESSED: explicitly suppressed cast despite visible-only character references; inspect visual reference sufficiency.',
 '- FULL_CAST_BY_DEFAULT / REPEATED_FULL_CAST: full-character prose is implicit or repeated, potentially unnecessary alongside established identities.',
 '- REPEATED_FULL_SETTING / REPEATED_SETTING_CONTINUITY: adjacent independently generated pages share environmental detail. Usually valid for continuity; review only for stale, internally duplicated or disproportionate text.',
 '- TEMPLATE_SUMMARY / DUPLICATE_SUMMARY: repeated or formulaic summary may duplicate actual panel/action writing.',
 '- CROSS_CONFIGURATION_CONFLICT: same unit resolves differently across production configurations; investigate before making policy assumptions.',
 '',
 '## Verification and caveats','',
 '- Exact entry paths for each page/scene/cast unit are included in the CSV; all units are listed in the series pages.',
 '- The report assesses effective ingredient delivery and obvious duplication. It cannot declare a suppression artistically appropriate without reading the distinctive content and adjacent context.',
 '- No approved artwork, dialogue, story, released canon, or suppression configuration is edited.',
 '',
 '## Errors','',...(errors.length?errors.map(s=>'- '+esc(s)):['None.']));
fs.writeFileSync(path.join(dir,'README.md'),main.join('\n')+'\n');
fs.writeFileSync(path.join(dir,'summary.json'),JSON.stringify({shows:shows.length,occurrences:occurrences.length,uniqueUnits:units.length,series:sid.length,stats,errors},null,2)+'\n');
console.log(JSON.stringify({configs:shows.length,occurrences:occurrences.length,unique:units.length,series:sid.length,stats,errors}));
if(errors.length)process.exitCode=2;
