#!/usr/bin/env node
'use strict';
// RexPrompt Sunforge sanitation regression: original story shelves remain authoritative.
// The chef receives shorter references and zero duplicated exact dialogue where opted in.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const json=p=>JSON.parse(read(p));
const html=read('index.html'),start=html.indexOf('const SHOW_MANIFEST='),end=html.indexOf('function safeFilePart(',start);
assert(start>=0&&end>start,'Live assembler unavailable');
const ctx=vm.createContext({});
vm.runInContext(html.slice(start,end)+';globalThis.testApi={assembleScene,preparePanelLettering,validatePageLayout};',ctx);
const {assembleScene:assemble,preparePanelLettering,validatePageLayout}=ctx.testApi;
const catalog=json('data/shows.json'),prefix='data/shows/sunforge-outlaw-s1/';
const store={};for(const f of ['characters','settings','regions','direction','factions','dialogue'])store[f+'.json']=json(prefix+f+'.json');
const section=(txt,header)=>{const hit=txt.indexOf('\n['+header+']\n');if(hit<0)return null;const rest=txt.slice(hit+header.length+4),next=rest.search(/\n\[[A-Z][A-Z _/]*\]\n/);return (next<0?rest:rest.slice(0,next)).trim()};
let pages=0,oldSize=0,newSize=0,dialogue=0,panels=0,scopedSummary=0,scopedDirection=0,castCompacted=0,settingCompacted=0,indexedPages=0;
for(let issue=1;issue<=12;issue++){
 const n=String(issue).padStart(2,'0'),id='sunforge-outlaw-s1-e'+n;
 const show=catalog.find(x=>x.id===id);assert(show,'No show '+id);
 const source=json(prefix+'pages_e'+n+'.json');
 const stories=source.filter(x=>new RegExp('^SUN_S1E'+n+'_P\\d\\d$').test(x.id));
 const layouts=json(prefix+'editorial/page_layouts_e'+n+'.json');
 const profiles=json(prefix+'editorial/page_assembly_e'+n+'.json');
 assert.equal(profiles.length,stories.length,'Missing sanitation records '+id);
 const keys=new Set(profiles.map(x=>x.id));
 assert.equal(keys.size,stories.length,'Duplicate profile '+id);
 assert(stories.every(x=>keys.has(x.id)),'Orphan/missing sanitation profile '+id);
 const li=show.sceneOverlays.findIndex(x=>x.file==='editorial/page_layouts_e'+n+'.json');
 const pi=show.sceneOverlays.findIndex(x=>x.file==='editorial/page_assembly_e'+n+'.json');
 assert(pi>li&&show.sceneOverlays[pi].mergeById&&show.sceneOverlays[pi].strict,'Sanitation must merge after pageLayout '+id);
 store.__show=show;
 for(let i=0;i<stories.length;i++){
   const page=stories[i],layout=layouts.find(x=>x.id===page.id),profile=profiles.find(x=>x.id===page.id);
   assert(layout,'Missing pageLayout '+page.id);
   assert.deepEqual(Object.keys(profile).filter(k=>k!=='id'&&k!=='setting').sort(),
     (issue===2||issue===3?['promptCharacterMode','promptPanelLetteringMode','promptSettingMode','promptSuppress']:['promptCharacterMode','promptSettingMode','promptSuppress']).sort(),
     'Unexpected sanitation fields '+page.id);
   for(const f of ['panelPlan','dialogueInline','summary','characters','direction','pageLayout'])
     assert(!(f in profile),'Sanitation overlay must not rewrite story '+page.id+' field '+f);
   const baseline={...page,...layout},clean={...baseline,...profile};
   validatePageLayout(clean);
   const before=assemble(baseline,store,i),after=assemble(clean,store,i);
   assert(after.includes(show.generationLine),'Production brief disappeared '+page.id);
   assert.equal(section(before,'PAGE COMPOSITION'),section(after,'PAGE COMPOSITION'),'Layout changed '+page.id);
   assert(section(after,'PANEL PLAN')!==null&&section(after,'DIALOGUE')!==null,'Missing script section '+page.id);
   assert(!after.includes('[REGION]'),'Generic region boilerplate leaked '+page.id);
   for(const d of page.dialogueInline||[]){assert(after.includes(d.text),'Lost exact dialogue '+page.id);dialogue++;}
   if(profile.promptSuppress.includes('summary'))assert(!after.includes(page.summary),'Summary suppression failed '+page.id);
   if(profile.promptSuppress.includes('direction'))assert(section(after,'DIRECTION')===null,'Direction suppression failed '+page.id);
   else if(page.direction?.length||page.directionInline?.length)assert(section(after,'DIRECTION')!==null,'Necessary direction lost '+page.id);
   const canonicalSetting=store['settings.json'][clean.setting];
   if(profile.promptSettingMode==='label'&&canonicalSetting?.text){
     assert(!after.includes(canonicalSetting.text),'Expanded recurring setting leaked '+page.id);settingCompacted++;
   }else if(canonicalSetting?.text)assert(after.includes(canonicalSetting.text),'Establishing setting lost '+page.id);
   if(profile.promptCharacterMode==='cast'){
     assert(!after.includes('[CAST]')&&!after.includes('[CHARACTERS]'),'Duplicate cast prose leaked '+page.id);
     const visualRefs=after.split('\n').filter(x=>/^@sun\./.test(x)||x.includes(' — Visual: '));
     assert.equal(visualRefs.length,(page.characters||[]).length,'Visible-only character reference count changed '+page.id);
     castCompacted++;
   }
   if(profile.promptPanelLetteringMode==='indexed'){
     const mapping=preparePanelLettering(clean);
     assert(mapping&&mapping.byDialogue.length===page.dialogueInline.length,'Incomplete dialogue placement '+page.id);
     assert(!after.includes('EXACT SCRIPTED LETTERING:'),'Redundant lettering remains '+page.id);
     for(const panel of page.panelPlan){
       const visual=panel.text.split('EXACT SCRIPTED LETTERING:')[0].trim();
       assert(after.includes(visual),'Lost visual panel instructions '+page.id);
     }
     const display=section(after,'DIALOGUE');
     for(let d=0;d<mapping.byDialogue.length;d++)
       assert(display.includes('Panel '+mapping.byDialogue[d]+' — '),'Lost lettering ownership '+page.id+' item '+(d+1));
     indexedPages++;
   }else assert.equal(section(before,'PANEL PLAN'),section(after,'PANEL PLAN'),'Unexpected panel edit '+page.id);
   scopedSummary+=+profile.promptSuppress.includes('summary');
   scopedDirection+=+profile.promptSuppress.includes('direction');
   oldSize+=before.length;newSize+=after.length;pages++;panels+=page.panelPlan.length;
 }
 const nonstories=source.filter(x=>!new RegExp('^SUN_S1E'+n+'_P\\d\\d$').test(x.id));
 for(const item of nonstories)assert(!keys.has(item.id),'Editorial/cover unit must not be overwritten '+item.id);
}
assert.equal(pages,260,'Season inventory changed');
assert.equal(dialogue,1388,'Canonical lettering inventory changed');
assert.equal(panels,1073,'Canonical panel inventory changed');
assert.equal(indexedPages,40,'Source-specific exact-lettering cleanup should remain opt-in');
const pct=((oldSize-newSize)*100/oldSize).toFixed(1);
assert(oldSize>newSize,'Prompts were not decluttered');
const corrected=json(prefix+'editorial/page_assembly_e03.json').find(x=>x.id==='SUN_S1E03_P01');
assert.equal(corrected.setting,'sunfields','The road approach must not inherit Mirage Club location');
// Deliberate corruption must fail loudly, never silently move or drop a balloon.
const rawSample=json(prefix+'pages_e02.json').find(p=>p.id==='SUN_S1E02_P01');
const opts={...rawSample,promptPanelLetteringMode:'indexed'};
assert.throws(()=>preparePanelLettering({...opts,dialogueInline:[{...opts.dialogueInline[0],speaker:'Wrong person'},...opts.dialogueInline.slice(1)]}),/differs from canonical/);
assert.throws(()=>preparePanelLettering({...opts,dialogueInline:[{...opts.dialogueInline[0],text:'Wrong exact text'},...opts.dialogueInline.slice(1)]}),/differs from canonical/);
assert.throws(()=>preparePanelLettering({...opts,dialogueInline:[...opts.dialogueInline,{speaker:'CAPTION',text:'Unmapped extra item'}]}),/Unmapped dialogueInline/);
assert.throws(()=>preparePanelLettering({...opts,promptPanelLetteringMode:'guess'}),/Invalid promptPanelLetteringMode/);
console.log('PASS Sunforge sanitation: '+pages+' pages; original '+panels+' panel beats and '+dialogue+' dialogue items preserved.');
console.log('PASS '+indexedPages+' duplicate-lettering pages retain exact speech and panel ownership.');
console.log('Chef recipe characters: '+oldSize+' => '+newSize+' ('+pct+'% reduction, '+(oldSize-newSize)+' characters removed).');
console.log('Profiles: '+castCompacted+' cast compactions, '+settingCompacted+' setting label references, '+scopedSummary+' summary suppressions, '+scopedDirection+' direction suppressions.');
