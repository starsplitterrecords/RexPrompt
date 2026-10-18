#!/usr/bin/env node
'use strict';
// Shattering layout compilation regression: verify 132 authored story-page compositions
// while keeping all six issues' story content, dialogue, panel order, and bookends intact.
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const load=p=>JSON.parse(read(p));
const html=read('index.html');
const start=html.indexOf('const SHOW_MANIFEST=');
const end=html.indexOf('function safeFilePart(',start);
assert(start>=0&&end>start,'Cannot find canonical assembler in index.html');
const context=vm.createContext({});
vm.runInContext(html.slice(start,end)+';globalThis.testApi={assembleScene,validatePageLayout,applyOverlay};',context);
const {assembleScene,validatePageLayout,applyOverlay}=context.testApi;
const shows=load('data/shows.json');
const dataStore={};
for(const shelf of ['characters','dialogue','settings','regions','factions','direction'])
  dataStore[shelf+'.json']=load('data/'+shelf+'.json');
let total=0,renderGrowth=0;
const compositionKinds=new Set();
for(let issue=1;issue<=6;issue++){
  const number=String(issue).padStart(2,'0'),show=shows.find(s=>s.id==='shattering-i'+number);
  assert(show,'Missing Shattering show '+number);
  const book=load('data/shows/shattering/pages_i'+number+'.json');
  const file='shows/shattering/page_layouts_i'+number+'.json';
  const rules=load('data/'+file);
  assert.equal(book.length,24,'Issue '+number+' page count changed');
  assert.equal(rules.length,22,'Issue '+number+' must have 22 story layout assignments');
  const ids=new Set(rules.map(r=>r.id));
  assert.equal(ids.size,22,'Duplicate layout assignment in Issue '+number);
  assert.deepEqual([...ids],[...book.slice(1,23).map(p=>p.id)],'Layout IDs must follow exact story page sequence');
  const reg=(show.sceneOverlays||[]).find(o=>o.file===file);
  assert(reg&&reg.mergeById&&reg.strict,'Shattering layout overlay is not registered as a strict merge for Issue '+number);
  const compiled=applyOverlay(book,rules,reg);
  assert.equal(compiled.length,24,'Layout overlay unexpectedly changed issue page count');
  const store={...dataStore,__show:show};
  for(let k=0;k<book.length;k++){
    const source=book[k],page=compiled[k];
    assert.equal(page.id,source.id,'Page order changed');
    assert.deepEqual(page.panelPlan,source.panelPlan,'Scripted panel plan changed on '+page.id);
    assert.deepEqual(page.dialogueInline,source.dialogueInline,'Scripted dialogue changed on '+page.id);
    assert.equal(page.summary,source.summary,'Story summary changed on '+page.id);
    assert.equal(page.continuityFrom,source.continuityFrom,'Continuation pointer changed on '+page.id);
    const before=assembleScene(source,store,k);
    const after=assembleScene(page,store,k);
    if(k===0||k===23){
      assert.equal(after,before,'Existing editorial full-page splash changed on '+page.id);
      assert.equal(page.pageLayout,undefined,'Do not lay out the editorial bookend as story panels');
      continue;
    }
    assert.deepEqual(Object.keys(rules[k-1]),['id','pageLayout'],'Layout overlay must not alter story data');
    assert(page.pageLayout,'No authored pageLayout on '+page.id);
    validatePageLayout(page);
    compositionKinds.add(page.pageLayout.composition);
    const compositionMarker='\n[PAGE COMPOSITION]';
    const planMarker='\n[PANEL PLAN]';
    const a=after.indexOf(compositionMarker),p=after.indexOf(planMarker);
    const b=before.indexOf(planMarker);
    assert(a>=0&&p>a&&b>=0,'Composed layout must be emitted before panel plan '+page.id);
    assert.equal(after.slice(0,a),before.slice(0,b),'Pre-panel ingredients changed '+page.id);
    assert.equal(after.slice(p),before.slice(b),'Script, lettering or following recipe sections changed '+page.id);
    assert.equal((after.match(/\[PAGE COMPOSITION\]/g)||[]).length,1,'Duplicate layout block '+page.id);
    for(const [j,panel] of page.panelPlan.entries()){
      assert(after.includes(panel),'Missing source panel '+page.id+' '+(j+1));
      assert(after.includes('Panel '+(j+1)+':'),'Missing layout reference '+page.id+' '+(j+1));
    }
    for(const d of page.dialogueInline||[])assert(after.includes(d.text),'Missing dialogue from '+page.id);
    const panels=page.pageLayout.panels;
    assert.equal(new Set(panels.map(p=>p.panel)).size,source.panelPlan.length,'Panel hierarchy does not cover page '+page.id);
    total++;renderGrowth+=after.length-before.length;
  }
}
assert.equal(total,132,'Unexpected story layout count');
assert(compositionKinds.size>=7,'Expected deliberate range of supported architectures');
console.log('PASS Shattering: '+total+' story page layouts, 12 unmodified editorial splashes, all original dialogue and panel plans intact.');
console.log('PASS Assembler emits unique composition blocks across '+compositionKinds.size+' architecture types; +'+renderGrowth+' chef instruction characters.');
