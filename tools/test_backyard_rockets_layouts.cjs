#!/usr/bin/env node
'use strict';
// Validate phase-B composition overlays using the live RexPrompt assembler.
// The original episode scripts remain immutable source: layouts may never alter dialogue, panel beats or order.
const fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const json=p=>JSON.parse(read(p));
const shows=json('data/shows.json'),show=shows.find(x=>x.id==='backyard-rockets-s1');
assert(show,'Missing Backyard Rockets season');
const core=read('index.html'),start=core.indexOf('const SHOW_MANIFEST='),end=core.indexOf('function safeFilePart(',start);
assert(start>=0&&end>start,'Cannot locate production assembler');
const context=vm.createContext({});
vm.runInContext(core.slice(start,end)+';globalThis.production={assembleScene,validatePageLayout};',context);
const {assembleScene:assemble,validatePageLayout:validate}=context.production;
const store={__show:show};
for(const f of ['characters','dialogue','settings','regions','factions','direction'])
  store[f+'.json']=json(show.basePath+'/'+f+'.json');
function originalEpisode(ep){
 const encoded=show.sceneOverlays.find(x=>x.file.startsWith('encoded/scenes_e'+String(ep).padStart(2,'0')+'_'));
 assert(encoded&&encoded.encoding==='gzip-base64','Missing compressed episode '+ep);
 return JSON.parse(zlib.gunzipSync(Buffer.from(read(show.basePath+'/'+encoded.file).trim(),'base64')).toString('utf8'));
}
const allLayouts=new Set(),architectures=new Map();let total=0,sourcePanels=0;
for(let ep=3;ep<=8;ep++){
 const tag=String(ep).padStart(2,'0');
 const src=originalEpisode(ep),name='editorial_page_layouts_e'+tag+'.json';
 const layoutEntry=show.sceneOverlays.findIndex(x=>x.file===name);
 const sourceEntry=show.sceneOverlays.findIndex(x=>x.encoding==='gzip-base64'&&x.file.includes('scenes_e'+tag+'_'));
 assert(sourceEntry>=0&&layoutEntry===sourceEntry+1,'Layout must follow its episode source: E'+tag);
 assert(show.sceneOverlays[layoutEntry].mergeById&&show.sceneOverlays[layoutEntry].strict,'Layout overlay must strict merge');
 const data=json(show.basePath+'/'+name);
 assert.equal(data.length,src.length,'Missing layout profiles for E'+tag);
 const index=new Map(data.map(x=>[x.id,x]));
 assert.equal(index.size,src.length,'Duplicate layout ids for E'+tag);
 let chars=0,panels=0;
 for(const [i,original] of src.entries()){
   const profile=index.get(original.id);
   assert(profile,'Missing layout for '+original.id);
   assert.deepEqual(Object.keys(profile).sort(),['id','pageLayout'],'Overlay must contain layout only: '+original.id);
   assert(!allLayouts.has(original.id),'Duplicate source ID '+original.id);
   allLayouts.add(original.id);
   const active={...original,pageLayout:profile.pageLayout};
   assert.equal(validate(active),profile.pageLayout);
   const before=assemble(original,store,i),after=assemble(active,store,i);
   const panelMarker='\n[PANEL PLAN]';
   assert(before.includes(panelMarker),'No original panel plan '+original.id);
   assert.equal(after.slice(after.indexOf(panelMarker)),before.slice(before.indexOf(panelMarker)),
       'Layout altered original panel plan/dialogue/direction '+original.id);
   assert.equal(after.slice(0,after.indexOf('\n[PAGE COMPOSITION]')),before.slice(0,before.indexOf(panelMarker)),
       'Layout altered recipe before panel plan '+original.id);
   assert(after.includes('Visual priority: '+profile.pageLayout.visualPriority),'Missing page-specific art direction');
   assert.equal((after.match(/\[PAGE COMPOSITION\]/g)||[]).length,1,'More than one composition block');
   assert.deepEqual(profile.pageLayout.panels.map(p=>p.panel).sort((a,b)=>a-b),
       original.panelPlan.map((_,j)=>j+1),'Changed number/order of authored panels');
   for(const line of original.dialogueInline||[])assert(after.includes(line.text),'Lost dialogue '+original.id);
   const composition=profile.pageLayout.composition;
   architectures.set(composition,(architectures.get(composition)||0)+1);
   panels+=original.panelPlan.length;
   chars+=after.length-before.length;
   total++;sourcePanels+=original.panelPlan.length;
 }
 console.log('PASS E'+tag+': '+src.length+' art-directed pages, '+panels+' original panel beats, '+chars+' composition characters');
}
// Published Issues 1 and 2 cannot be inadvertently re-laid out as part of this pass.
for(const ep of [1,2]){
 const src=originalEpisode(ep);
 for(const page of src)assert(!allLayouts.has(page.id)&&page.pageLayout===undefined,
   'Released E'+ep+' source changed by a layout profile');
 const overlay=show.sceneOverlays.filter(x=>x.file.includes('editorial_page_layouts_e0'+ep+'.json'));
 assert.equal(overlay.length,0,'Published issue unexpectedly received a page-layout overlay');
}
assert.equal(total,118,'Expected 118 non-published interior pages from six issues');
assert(sourcePanels>500,'Too few original panel beats covered');
assert(architectures.size>=7,'Insufficient variety in authored composition architectures');
console.log('PASS: '+total+' interior pages; '+sourcePanels+' original beats; '+architectures.size+' artistic architecture forms.');
console.log('Composition mix: '+JSON.stringify(Object.fromEntries(architectures)));
console.log('PASS: published Issues 1–2 and all editorial splash/open-close pages unchanged.');
