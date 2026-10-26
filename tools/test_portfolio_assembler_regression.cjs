#!/usr/bin/env node
'use strict';
// Portfolio regression: exercise the LIVE browser loader and assembler, not a duplicate model.
// Structural pass is NOT approval of rendered pixels, visual identity, balloon tails or publication.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict'),zlib=require('node:zlib'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const json=p=>JSON.parse(read(p));
const exists=p=>fs.existsSync(path.join(root,p));
const html=read('index.html'),first=html.indexOf('const SHOW_MANIFEST='),last=html.indexOf('function safeFilePart(',first);
assert(first>=0&&last>first,'Could not extract current production assembler');
const catalogs=json('data/shows.json'),approved=json('production/drafts/manifest.json').drafts;
const report={baseCommit:process.env.GITHUB_SHA||null,configurations:catalogs.length,loadedConfigurations:0,assembledRecipes:0,sourceFormats:{array:0,object:0,encodedGzipBase64:0,overlayMerge:0,overlayReplace:0,overlayAppend:0,dialogueOverlay:0,scopedCastConfigurations:0},series:{},issues:[],failures:[],historicalExceptions:[],risks:{highDensity:[],ambiguousDialogueMapping:[],unresolvedSpeaker:[],panelMetadataDiscrepancies:[]},mutationCases:{},approved:{records:Object.keys(approved).length,resolved:0,unresolved:[]},issueRegistration:{expandedIssues:0,identities:[],duplicateIds:[]},untested:['Image pixels and rendered character likeness','Physical balloon tails and text appearance','Rendered panel reading order and geometry','True print resolution and issue-wide mastering','Intentionality of creative dialogue and continuity','User approval beyond manifest status']};
const sandbox=vm.createContext({fetch:async p=>{
 const relative=String(p);
 if(relative.startsWith('/')||relative.includes('..'))throw Error('Unsafe load path '+relative);
 const f=path.join(root,relative);
 if(!fs.existsSync(f))return {ok:false,status:404,json:async()=>null,text:async()=>''};
 return {ok:true,status:200,json:async()=>json(relative),text:async()=>read(relative)};
},Blob,Response,DecompressionStream,atob});
vm.runInContext(html.slice(first,last)+';globalThis.api={loadShow,assembleScene,pageAssembly,validatePageLayout,pageLayoutWarnings,visibleCharacterHandles,applyOverlay,applyDialogueOverlay,prepareCleanPanelPlan,preparePanelLettering,expandIssues,normalizeScenes,normalizeOverlay};',sandbox);
const api=sandbox.api;
function recordFailure(code,show,scene,reason){report.failures.push({code,show,scene,reason:String(reason).slice(0,500)})}
const asJson=value=>JSON.stringify(value);
const formatType=value=>Array.isArray(value)?'array':'object';
function addFormat(show){
 const base=show.basePath||'data',configPath=base+'/'+(show.packageConfigFile||'assembler.json');
 const cfg={...(exists(configPath)?json(configPath):{}),...show};
 const sources=Array.isArray(cfg.scenesFiles)?cfg.scenesFiles:[cfg.scenesFile||'scenes.json'];
 for(const source of sources){const raw=json(base+'/'+source);report.sourceFormats[formatType(raw)]++}
 for(const o of cfg.sceneOverlays||[]){
  if(o.encoding==='gzip-base64'){
   report.sourceFormats.encodedGzipBase64++;
   const raw=read(base+'/'+o.file).trim();
   assert(Array.isArray(JSON.parse(zlib.gunzipSync(Buffer.from(raw,'base64')).toString('utf8'))),'Encoded overlay must decode to page list '+show.id);
  }
  if(o.mergeById)report.sourceFormats.overlayMerge++;
  else if(o.replaceEpisode||o.replaceEpisodes)report.sourceFormats.overlayReplace++;
  else report.sourceFormats.overlayAppend++;
 }
 report.sourceFormats.dialogueOverlay+=(cfg.dialogueOverlays||[]).length;
 if(cfg.promptVisibleCastOnly)report.sourceFormats.scopedCastConfigurations++;
}
const lockfile=json('tools/fixtures/approved-draft-blob-locks.json');
assert.equal(lockfile.schemaVersion,1,'Invalid approved art byte-lock schema');
const knownKeys=new Set(Object.keys(lockfile.records));
for(const [id,draft] of Object.entries(approved)){
 const lock=lockfile.records[id];
 if(!lock){throw Error('New approved draft not byte-locked: '+id+' (run explicit approved-asset baseline update)')}
 if(lock.image!==draft.image)throw Error('Protected approved draft moved without lock review: '+id);
 const data=fs.readFileSync(path.join(root,draft.image));
 const actual=crypto.createHash('sha1').update('blob '+data.length+'\0').update(data).digest('hex');
 if(actual!==lock.gitBlobSha)throw Error('Protected approved artwork bytes changed: '+id+' '+draft.image);
 knownKeys.delete(id);
}
assert.equal(knownKeys.size,0,'Stale removed approved page locks: '+[...knownKeys].slice(0,5).join(', '));
const displayedLines=scene=>{
 const result=[];
 for(const d of scene.dialogueInline||[])if(typeof d.text==='string')result.push(d.text);
 return result;
};
function checkScene(show,store,scene,index){
 const before=asJson(scene),result=api.assembleScene(scene,store,index);
 assert.equal(asJson(scene),before,'Assembler mutated canonical scene');
 assert(result.includes('=== '+(store.__show.unitLabel||'SCENE')+': '+scene.id+' ==='),'Recipe id not emitted');
 if(scene.panelPlan?.length)assert(result.includes('[PANEL PLAN]'),'Scripted panels omitted');
 if(scene.dialogueInline?.length){assert(result.includes('[DIALOGUE]'),'Dialogue section omitted');for(const line of displayedLines(scene))assert(result.includes(line),'Dialogue text silently dropped: '+line);}
 else if(scene.dialog?.length){for(const id of scene.dialog){const d=store['dialogue.json']?.[id];if(d?.text)assert(result.includes(d.text),'Legacy referenced dialogue dropped: '+id)}}
 if(scene.pageLayout){api.validatePageLayout(scene);assert(result.includes('[PAGE COMPOSITION]'),'Page layout not emitted');assert(result.indexOf('[PAGE COMPOSITION]')<result.indexOf('[PANEL PLAN]'),'Layout must precede scripted panels');}
 const scope=api.pageAssembly(scene,store.__show);
 const visible=scene.promptVisibleCastOnly===undefined?!!store.__show.promptVisibleCastOnly:scene.promptVisibleCastOnly;
 if(visible){
  const expected=scope.characterMode==='none'?[]:Array.from(api.visibleCharacterHandles(scene,store['characters.json']));
  const prefix=result.split(/(?:\n)?=== /)[0].trim();
  const actual=prefix?prefix.split('\n').map(s=>s.trim()).filter(Boolean):[];
  assert.deepEqual(actual,expected,'Visible-reference scope does not equal selected cast');
  assert(!result.includes('\n[CHARACTERS]\n')&&!result.includes('\n[CAST]\n'),'Visible mode includes duplicate cast prose');
 }
 const lines=scene.dialogueInline||[];
 if(lines.length&&scene.panelPlan?.length){
   const indexPanels=scene.panelPlan.some(x=>Array.isArray(x?.dialogueIndices));
   const assigned=new Map();
   if(indexPanels){
    for(const [pi,p] of scene.panelPlan.entries())for(const idx of p?.dialogueIndices||[]){
      if(!Number.isInteger(idx)||idx<0||idx>=lines.length){recordFailure('OUT_OF_RANGE_DIALOGUE_INDEX',show.id,scene.id,'Panel '+(pi+1)+' index '+idx);continue}
      if(assigned.has(idx))recordFailure('MULTIPLE_DIALOGUE_OWNERS',show.id,scene.id,'Line '+idx+' mapped to panels '+assigned.get(idx)+' and '+(pi+1));
      assigned.set(idx,pi+1);
    }
    const missing=lines.map((_,i)=>i).filter(i=>!assigned.has(i));
    if(missing.length)report.risks.ambiguousDialogueMapping.push({show:show.id,recipe:scene.id,unmapped:missing.length,reason:'Index mapping incomplete'});
    for(let i=0;i<lines.length;i++){
      const expected=String(lines[i].subtext||'').match(/^Panel\s+(\d+)$/i);
      if(expected&&assigned.has(i)&&Number(expected[1])!==assigned.get(i))recordFailure('SPEAKER_PANEL_CONFLICT',show.id,scene.id,'Line '+i+' belongs to '+assigned.get(i)+' while subtext says '+expected[1]);
    }
   }else if(lines.length>=6&&!lines.every(d=>/^Panel\s+\d+$/i.test(String(d.subtext||''))))report.risks.ambiguousDialogueMapping.push({show:show.id,recipe:scene.id,reason:'No explicit map for all dialogue lines'});
 }
 if(Number.isInteger(scene.panelCount)&&Array.isArray(scene.panelPlan)&&scene.panelCount!==scene.panelPlan.length){
  const detail={show:show.id,recipe:scene.id,declared:scene.panelCount,panels:scene.panelPlan.length};
  report.risks.panelMetadataDiscrepancies.push(detail);
  if(show.id==='azure-reach-s1'&&scene.id==='AZR_S1E01_P03'&&scene.panelCount===10&&scene.panelPlan.length===5)
    report.historicalExceptions.push({...detail,reason:'Published Azure Reach I01 P03 has older panelCount metadata; existing source is not rewritten.'});
}
const chars=store['characters.json']||{};
for(const line of scene.dialogueInline||[]){
 const token=line.handle;
 if(typeof token!=='string'||!token.startsWith('@'))continue;
 if(!Object.values(chars).some(v=>v?.handle===token||(v?.aliases||[]).includes(token)))report.risks.unresolvedSpeaker.push({show:show.id,recipe:scene.id,handle:token});
}
const warnings=api.pageLayoutWarnings(scene);
 if(warnings.length)report.risks.highDensity.push({show:show.id,recipe:scene.id,warnings:[...warnings]});
 report.assembledRecipes++;
 return result;
}
function mutation(name,fn){try{fn();report.mutationCases[name]='PASS'}catch(e){report.mutationCases[name]='FAIL: '+e.message;recordFailure('MUTATION_REGRESSION',name,'',e.message)}}
function expectedFailure(fn,needle){let threw=false;try{fn()}catch(e){threw=true;assert(String(e.message).includes(needle),'Expected '+needle+' but got '+e.message)}assert(threw,'Expected failure '+needle)}
async function main(){
 assert(catalogs.length>0,'No registered configurations');
 const assembled=new Set(),selected=new Map(),foundFormats=new Set(),expandedIds=new Set();
 for(const config of catalogs){
  const issues=api.expandIssues(config);
  assert(Array.isArray(issues)&&issues.length>0,'Show has no expansion '+config.id);
  report.issueRegistration.expandedIssues+=issues.length;
  for(const issue of issues){
   const id=issue.issueId;
   if(!id||expandedIds.has(id)){report.issueRegistration.duplicateIds.push(id);recordFailure('DUPLICATE_ISSUE_REGISTRATION',config.id,id,'expandIssues generated missing/duplicate issueId')}
   expandedIds.add(id);
   report.issueRegistration.identities.push({from:config.id,issueId:id,issueLabel:issue.issueLabel});
  }
 }
 
 for(const show of catalogs){
  let store;
  try{addFormat(show);store=await api.loadShow(show);assert(store.__scenes.length>0,'No registered production units');report.loadedConfigurations++}
  catch(e){recordFailure('LOAD_SHOW',show.id,'',e.message);continue}
  const scenes=store.__scenes,ids=new Set(),series=show.seriesId||store.__show.seriesId||path.posix.basename(show.basePath||show.id).replace(/-s1$/,'');
  if(!report.series[series])report.series[series]={configurations:0,units:0,assembled:0};
  report.series[series].configurations++;
  report.series[series].units+=scenes.length;
  const entry={id:show.id,seriesId:series,sourceFormat:Array.isArray(store.__show.scenesFiles)?'multi-source':'single-source',recipes:scenes.length,assembled:0,highDensity:0,layoutCount:0,scopedCastCount:0,dialogueCount:0,riskCount:0};
  for(const [i,scene] of scenes.entries()){
    if(typeof scene?.id!=='string'||!scene.id)recordFailure('MISSING_RECIPE_ID',show.id,'','Scene '+i);
    if(ids.has(scene.id))recordFailure('DUPLICATE_RECIPE_ID',show.id,scene.id,'Repeated within assembled configuration');
    ids.add(scene.id);
    assembled.add(series+'::'+scene.id);
    try{checkScene(show,store,scene,i);entry.assembled++;report.series[series].assembled++}
    catch(e){recordFailure('ASSEMBLY',show.id,scene.id,e.message)}
    if(scene.pageLayout)entry.layoutCount++;
    if(scene.dialogueInline?.length||scene.dialog?.length)entry.dialogueCount++;
    if(scene.promptVisibleCastOnly??store.__show.promptVisibleCastOnly)entry.scopedCastCount++;
  }
  entry.highDensity=report.risks.highDensity.filter(x=>x.show===show.id).length;
  entry.riskCount=report.risks.ambiguousDialogueMapping.filter(x=>x.show===show.id).length;
  report.issues.push(entry);
  if(!selected.has(series))selected.set(series,{show,store,scenes});
 }
 for(const [key,draft] of Object.entries(approved)){
   if(assembled.has(draft.seriesId+'::'+draft.recipeId))report.approved.resolved++;
   else report.approved.unresolved.push({key,recipeId:draft.recipeId});
 }
 const baseline=json('tools/fixtures/portfolio-untriaged-risks.json');
 assert.equal(baseline.schemaVersion,1,'Risk register requires schemaVersion 1');
 for(const [category,items,key] of [['density',report.risks.highDensity,'show'],['ambiguity',report.risks.ambiguousDialogueMapping,'show'],['speakers',report.risks.unresolvedSpeaker,'show']]){
   const prior=new Set(baseline[category]||[]);
   for(const risk of items){
     const id=risk.show+'::'+risk.recipe+(category==='speakers'?'::'+risk.handle:'');
     if(!prior.has(id))recordFailure('NEW_UNREVIEWED_'+category.toUpperCase(),risk.show,risk.recipe,'New risk not present in the untriaged legacy inventory: '+id);
   }
 }
 for(const risk of report.risks.panelMetadataDiscrepancies){
   if(!(risk.show==='azure-reach-s1'&&risk.recipe==='AZR_S1E01_P03'&&risk.declared===10&&risk.panels===5))
     recordFailure('UNEXPECTED_PANEL_COUNT_MISMATCH',risk.show,risk.recipe,'New or changed panel metadata mismatch');
 }
 if(report.approved.unresolved.length)recordFailure('APPROVED_RECIPE_LOST','portfolio','',report.approved.unresolved.map(x=>x.key).slice(0,6).join(', '));
 assert.equal(report.loadedConfigurations,catalogs.length,'Not all configurations loaded');
 assert.equal(report.issues.length,catalogs.length,'Not all configured issue rows processed');
 const sample=selected.get('vikings-2026')||[...selected.values()][0];
 mutation('map-shaped-scene-input',()=>{const x=api.normalizeScenes({PAGE_A:{summary:'one'},PAGE_B:{summary:'two'}});assert.equal(x.length,2);assert.equal(x[0].id,'PAGE_A');assert.equal(x[1].summary,'two')});
 mutation('pages-wrapper-overlay-input',()=>{const x=api.normalizeOverlay({pages:[{id:'A',summary:'first'}]});assert.equal(x.length,1);assert.equal(x[0].id,'A')});
 mutation('episode-replacement-order',()=>{const before=[{id:'old1',episode:'S1E01'},{id:'old2',episode:'S1E01'},{id:'middle',episode:'S1E02'}];const out=api.applyOverlay(before,[{id:'new1',episode:'S1E01'}],{replaceEpisode:'S1E01'});assert.deepEqual(out.map(x=>x.id),['new1','middle']);assert.equal(before.length,3)});
 mutation('overlay-insertion-after-id',()=>{const out=api.applyOverlay([{id:'A'},{id:'B'}],[{id:'C'}],{afterId:'A'});assert.deepEqual(out.map(x=>x.id),['A','C','B'])});
 mutation('strict-overlay-rejects-orphan',()=>expectedFailure(()=>api.applyOverlay([{id:'A',summary:'keep'}],[{id:'B',summary:'insert'}],{mergeById:true,strict:true,file:'negative.json'}),'Orphan strict'));
 mutation('strict-overlay-rejects-duplicate-id',()=>expectedFailure(()=>api.applyOverlay([{id:'A'}],[{id:'A',summary:'one'},{id:'A',summary:'two'}],{mergeById:true,strict:true,file:'negative.json'}),'Duplicate strict'));
 mutation('strict-overlay-preserves-original',()=>{const src=[{id:'A',summary:'keep',panelPlan:['one']}],before=asJson(src),out=api.applyOverlay(src,[{id:'A',promptSettingMode:'label'}],{mergeById:true,strict:true});assert.equal(out.length,1);assert.deepEqual(out[0].panelPlan,['one']);assert.equal(out[0].summary,'keep');assert.equal(asJson(src),before)});
 mutation('unsafe-prompt-suppression',()=>expectedFailure(()=>api.pageAssembly({id:'synthetic',promptSuppress:['dialogue']},{}),'Invalid or protected prompt suppression'));
 mutation('bad-layout-panel-reference',()=>expectedFailure(()=>api.validatePageLayout({id:'synthetic',panelPlan:['panel1'],pageLayout:{composition:'grid',visualPriority:'a',readingFlow:'a',panels:[{panel:2,role:'dominant',scale:'large',placement:'a'}]}}),'invalid 1-based panel reference'));
 mutation('incorrect-balloon-panel-ownership',()=>{const fixture={id:'mutation-dialogue',panelPlan:[{panel:1,action:'A',dialogueIndices:[0]},{panel:2,action:'B',dialogueIndices:[]}],dialogueInline:[{speaker:'A',text:'Hello',subtext:'Panel 2'}]};expectedFailure(()=>api.prepareCleanPanelPlan(fixture),'conflicts with authored subtext')});
 mutation('wrong-panel-lettering-speaker',()=>{const fixture={id:'mutation-lettering',promptPanelLetteringMode:'indexed',panelPlan:['Close-up. EXACT SCRIPTED LETTERING: ALICE: “Hello”'],dialogueInline:[{speaker:'BOB',text:'Hello'}]};expectedFailure(()=>api.preparePanelLettering(fixture),'differs from canonical dialogueInline')});
 mutation('dense-dialogue-warning-without-rewrite',()=>{const fixture={id:'dense',panelPlan:Array.from({length:3},(_,i)=>({panel:i+1,action:'beat',dialogueIndices:i===0?Array.from({length:16},(_,n)=>n):[]})),dialogueInline:Array.from({length:16},(_,i)=>({speaker:'A',text:'These lines are deliberately dense and must remain authoritative '+i}))};const original=asJson(fixture),warnings=api.pageLayoutWarnings(fixture);assert(warnings.length>0);assert.equal(original,asJson(fixture))});
 mutation('unrecognized-visible-reference',()=>{const original=sample.scenes.find(p=>p.characters?.length||p.charactersInline?.length);assert(original,'No sample page with characters');const source={...original,promptVisibleCharacters:['no-such-identity'],promptVisibleCastOnly:true};expectedFailure(()=>api.visibleCharacterHandles(source,sample.store['characters.json']),'Unknown visible character')});
 mutation('empty-visible-reference-overrides-inherited-cast',()=>{const original=sample.scenes.find(p=>p.characters?.length||p.charactersInline?.length);assert(original);const scene={...original,promptVisibleCharacters:[],promptVisibleCastOnly:true};const r=api.assembleScene(scene,{...sample.store,__show:{...sample.store.__show,promptVisibleCastOnly:true}},0);assert(r.startsWith('=== '),'Suppressed refs still leaked into prompt')});
 mutation('setting-suppression-requires-panel-locations',()=>expectedFailure(()=>api.pageAssembly({id:'bad-setting',setting:'ROOM',promptSuppress:['setting'],panelPlan:['Somewhere']},{}),'Cannot suppress setting'));
 mutation('indexed-dialogue-invalid-mapping',()=>{const fixture={id:'bad-index',panelPlan:[{panel:1,action:'One',dialogueIndices:[2]}],dialogueInline:[{speaker:'A',text:'Hi'}]};expectedFailure(()=>api.prepareCleanPanelPlan(fixture),'Invalid or duplicated dialogue index')});
 console.log('PORTFOLIO REGRESSION SUMMARY '+JSON.stringify({configurations:report.configurations,loaded:report.loadedConfigurations,recipesAssembled:report.assembledRecipes,expandedIssueRegistrations:report.issueRegistration.expandedIssues,sourceFormats:report.sourceFormats,approved:report.approved,mutationCases:report.mutationCases,failures:report.failures.length,risks:{highDensity:report.risks.highDensity.length,ambiguousDialogueMapping:report.risks.ambiguousDialogueMapping.length,unresolvedSpeaker:report.risks.unresolvedSpeaker.length,panelMetadataDiscrepancies:report.risks.panelMetadataDiscrepancies.length},historicalExceptions:report.historicalExceptions}));
 for(const e of report.failures.slice(0,100))console.error('FAIL '+JSON.stringify(e));
 for(const e of report.approved.unresolved.slice(0,30))console.error('APPROVED MISSING '+JSON.stringify(e));
 console.log('REGRESSION COVERAGE '+JSON.stringify(report.issues.map(x=>({id:x.id,assembled:x.assembled,recipes:x.recipes,highDensity:x.highDensity,riskCount:x.riskCount}))));
 console.log('PORTFOLIO_RISK_IDS '+JSON.stringify({density:report.risks.highDensity.map(x=>x.show+'::'+x.recipe),ambiguity:report.risks.ambiguousDialogueMapping.map(x=>x.show+'::'+x.recipe),speakers:report.risks.unresolvedSpeaker.map(x=>x.show+'::'+x.recipe+'::'+x.handle)}));
 console.log('LIMITATION: mechanically assembled prompts do not verify rendered image content, balloon tails, canon, or final book.');
 const file=process.argv.includes('--out')?process.argv[process.argv.indexOf('--out')+1]:null;
 if(file){fs.mkdirSync(path.dirname(path.resolve(file)),{recursive:true});fs.writeFileSync(file,JSON.stringify(report,null,2)+'\n')}
 if(report.failures.length||Object.values(report.mutationCases).some(x=>x!=='PASS'))process.exitCode=1;
}
main().catch(e=>{console.error(e.stack);process.exitCode=1});
