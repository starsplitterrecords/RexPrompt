#!/usr/bin/env node
'use strict';
// Test the production assembler against real scripted pages and synthetic,
// non-production page-layout assignments. No creative script data is changed.
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const load=file=>JSON.parse(fs.readFileSync(path.join(root,file),'utf8'));
const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
const from=html.indexOf('const SHOW_MANIFEST='),to=html.indexOf('function safeFilePart(',from);
assert(from>=0&&to>from,'Canonical assembler unavailable');
const sandbox=vm.createContext({});
vm.runInContext(html.slice(from,to)+';globalThis.exportsForTest={assembleScene,validatePageLayout,formatPageLayout,pageLayoutWarnings};',sandbox);
const {assembleScene:assemble,validatePageLayout:validate,formatPageLayout:format,pageLayoutWarnings:warnings}=sandbox.exportsForTest;
const fixtures=load('tools/fixtures/page_layout_cases.json');
assert.equal(fixtures.length,5,'Expected five distinct editorial prototypes');
assert.equal(new Set(fixtures.map(x=>x.pageLayout.composition)).size,5,'Prototypes must show five distinct architectures');
const showData=load('data/shows.json');
function showFor(sample){
  const entry=showData.find(x=>x.basePath==='data/shows/'+sample.series);
  assert(entry,'Missing production series '+sample.series);
  return entry;
}
function storeFor(sample){
  const base='data/shows/'+sample.series;
  const store={__show:showFor(sample)};
  for(const item of ['characters','dialogue','settings','regions','factions','direction']){
    store[item+'.json']=load(base+'/'+item+'.json');
  }
  return store;
}
function sourcePage(sample){
  const page=load('data/shows/'+sample.series+'/'+sample.file).find(p=>p.id===sample.id);
  assert(page,'Missing source page '+sample.id);
  return page;
}
for(const [i,example] of fixtures.entries()){
  const base=sourcePage(example),store=storeFor(example);
  const scene={...base,pageLayout:example.pageLayout};
  const original=assemble(base,store,i),revised=assemble(scene,store,i);
  assert.equal(validate(scene),example.pageLayout,'Layout validator did not return authored data');
  assert.equal(original.includes('[PAGE COMPOSITION]'),false,'Unconfigured pages must retain old assembly');
  assert(revised.includes('[PAGE COMPOSITION]\nArchitecture: '+example.pageLayout.composition.replaceAll('-',' ')),
    'Missing architecture in assembled recipe for '+example.id);
  assert.equal((revised.match(/\[PAGE COMPOSITION\]/g)||[]).length,1,'Duplicate layout block');
  assert(revised.indexOf('[PAGE COMPOSITION]')<revised.indexOf('[PANEL PLAN]'),'Layout must precede panel plan');
  assert.equal(revised.split('\n[PAGE COMPOSITION]')[0],original.split('\n[PANEL PLAN]')[0],
    'Unexpected changes to earlier ingredients on '+example.id);
  assert.equal(revised.slice(revised.indexOf('\n[PANEL PLAN]')),original.slice(original.indexOf('\n[PANEL PLAN]')),
    'Scripted panel plan, dialogue, and downstream context changed on '+example.id);
  for(const item of base.dialogueInline||[])assert(revised.includes(item.text),'Missing line '+item.text);
  for(let n=1;n<=base.panelPlan.length;n++)assert(revised.includes('Panel '+n+':'),'Missing layout assignment '+n);
  assert(!original.includes('Reading flow: '+example.pageLayout.readingFlow),'Composition leaked to legacy page');
}
const caseFile=fixtures.find(x=>x.id==='VIK_S1E02_P07');
const scripted=sourcePage(caseFile),store=storeFor(caseFile);
assert(warnings(scripted).some(x=>x.includes('18 dialogue/caption items')),
  'Vikings crowded bodega must surface a non-destructive density advisory');
const baseline=assemble(scripted,store,0);
assert(!baseline.includes('Editorial density advisories'),'Warnings must not be added to chef recipe');
const base=sourcePage(fixtures[1]),good=fixtures[1].pageLayout,scene={...base,pageLayout:good};
const bad=(patch)=>({...scene,pageLayout:{...good,...patch}});
const expectBad=object=>assert.throws(()=>assemble(object,store,0),/Invalid pageLayout/);
expectBad(bad({composition:'random-default-grid'}));
expectBad(bad({visualPriority:' '}));
expectBad(bad({readingFlow:' '}));
expectBad(bad({panels:good.panels.slice(1)}));
expectBad(bad({panels:[...good.panels.slice(0,-1),good.panels[0]]}));
expectBad(bad({panels:good.panels.map((p,i)=>i===0?{...p,panel:42}:p)}));
expectBad(bad({primaryPanel:42}));
expectBad(bad({primaryPanel:5}));
expectBad(bad({panels:good.panels.map((p,i)=>i===0?{...p,role:'spectacular'}:p)}));
expectBad(bad({panels:good.panels.map((p,i)=>i===0?{...p,scale:'enormous'}:p)}));
expectBad(bad({panels:good.panels.map((p,i)=>i===1?{...p,role:'inset',insetOf:4}:p)}));
expectBad(bad({panels:good.panels.map((p,i)=>i===1?{...p,insetOf:1}:p)}));
expectBad(bad({negativeSpace:[{where:'blank'}]}));
expectBad(bad({lettering:{reservedZone:'top'}}));
expectBad(bad({unknown:'unexpected'}));
expectBad(bad({composition:'splash'})); // Multi-panel page cannot become a single splash.
expectBad({...scene,panelPlan:[]});
assert.throws(()=>assemble({...scene,promptSuppress:['pageLayout']},store,0),/Invalid or protected prompt suppression/); // Layout is protected.
console.log('PASS: 5 distinctive page compositions, legacy compatibility, unchanged script, strict layout validation, density advisory');
