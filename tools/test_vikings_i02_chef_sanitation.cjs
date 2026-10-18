#!/usr/bin/env node
'use strict';
// Canonical-assembler regression test. Sanitation changes only what reaches the
// image chef, never the original authored panels, lettering, identity or canon.
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const load=p=>JSON.parse(read(p));
const html=read('index.html'),start=html.indexOf('const SHOW_MANIFEST='),end=html.indexOf('function safeFilePart(',start);
assert(start>=0&&end>start,'Assembler source not found');
const ctx=vm.createContext({});
vm.runInContext(html.slice(start,end)+';globalThis.sanitizer={assembleScene,prepareCleanPanelPlan,mergeById};',ctx);
const {assembleScene:assemble,mergeById:merge}=ctx.sanitizer;
const shows=load('data/shows.json'),show=shows.find(x=>x.id==='vikings-2026-s1-e02');
assert(show,'Missing Issue 2');
const prefix=show.basePath+'/';
const base=load(prefix+'pages_i02.json');
const dialogue=load(prefix+'editorial/dialogue_density_i02.json');
const policyPath='editorial/chef_recipe_sanitation_i02.json';
const scopes=load(prefix+policyPath);
assert.equal(show.sceneOverlays.at(-1)?.file,policyPath,'Sanitation must run after dialogue and layouts');
assert(show.sceneOverlays.at(-1)?.mergeById&&show.sceneOverlays.at(-1)?.strict,
  'Registered sanitation must be a strict ID overlay');
assert.equal(scopes.length,19,'Expected 19 audited unapproved interior pages');
assert.equal(new Set(scopes.map(x=>x.id)).size,scopes.length,'Duplicate sanitation IDs');
const allowed=new Set(['id','promptPanelMode','promptSuppress','directionInline','pageLayout','promptVisibleCharacters','promptVisibleCastOnly']);
for(const p of scopes){
  assert(Object.keys(p).every(key=>allowed.has(key)),'Sanitation patch attempted story mutation: '+p.id);
  assert.equal(p.promptPanelMode,'clean','Unconfigured sanitation mode: '+p.id);
  assert.equal(p.promptVisibleCastOnly,true,'Page must opt into shared visual-reference scoping '+p.id);
  assert(!['VIK_S1E02_P02','VIK_S1E02_P03','VIK_S1E02_P04'].includes(p.id),
    'Approved artwork recipe unexpectedly changed: '+p.id);
}
const authored=merge(base,dialogue);
const clean=merge(authored,scopes);
assert.equal(clean.length,base.length,'Lost/created production pages');
assert.equal(clean.length,22,'Unexpected Issue 2 length');
const store={__show:show};
for(const name of ['characters','dialogue','settings','regions','factions','direction'])
  store[name+'.json']=load(prefix+name+'.json');
function section(src,heading){
  const start=src.indexOf('\n['+heading+']\n');
  if(start<0)return null;
  const body=src.slice(start+heading.length+4);
  const end=body.search(/\n\[[A-Z][A-Z0-9 /_-]*\]\n/);
  return (end<0?body:body.slice(0,end)).trim();
}
let inputChars=0,outputChars=0,cleanCount=0;
for(let i=0;i<clean.length;i++){
  const original=authored[i],scene=clean[i];
  assert.equal(scene.id,original.id,'Identity/order changed');
  assert.deepEqual(scene.dialogueInline,original.dialogueInline,'Dialogue source changed: '+scene.id);
  assert.deepEqual(scene.panelPlan,original.panelPlan,'Panel data changed: '+scene.id);
  assert.equal(scene.continuityFrom,original.continuityFrom,'Continuity changed: '+scene.id);
  assert.equal(scene.settingText,original.settingText,'Setting changed: '+scene.id);
  const before=assemble(original,store,i),after=assemble(scene,store,i);
  inputChars+=before.length;outputChars+=after.length;
  assert.equal(section(after,'DIALOGUE'),section(before,'DIALOGUE'),
    'Exact dialogue, order, panel attribution or speakers changed: '+scene.id);
  assert.equal(section(after,'CONTINUITY'),section(before,'CONTINUITY'),
    'Continuity lost: '+scene.id);
  if(i<3){assert.equal(after,before,'Approved page changed: '+scene.id);continue}
  cleanCount++;
  assert(after.includes('[PANEL PLAN]\nPanel 1'),'No clean formatted panel plan '+scene.id);
  assert(!section(after,'PANEL PLAN').includes('"dialogueIndices"'),
    'Machine serialization leaked to chef: '+scene.id);
  for(const [n,panel] of scene.panelPlan.entries()){
    assert(after.includes(panel.action),'Lost action '+scene.id+' panel '+(n+1));
    assert(after.includes('Panel '+(n+1)),'Lost panel reference '+scene.id);
  }
  const unique=new Set(scene.panelPlan.map(p=>p.location).filter(Boolean));
  for(const place of unique)assert(after.includes(place),'Dropped distinct location '+place+' '+scene.id);
  for(const line of scene.dialogueInline)assert(after.includes(line.text),'Lost dialogue '+scene.id);
  // The visual reference set uses the shared Stardust/other-series mechanism.
  // Dialogue speakers remain intelligible even when not rendered as people.
  assert(!after.includes('\n[CAST]\n')&&!after.includes('\n[CHARACTERS]\n'),
    'Duplicate textual cast roster leaked '+scene.id);
  const refs=after.split('\n').filter(line=>/^@vik\.[A-Za-z][A-Za-z0-9_-]*$/.test(line));
  const intended=scene.promptVisibleCharacters||
    original.charactersInline.map(x=>x.handle);
  assert.deepEqual(refs,intended,'Wrong canonical visual reference handles '+scene.id);
  if(scene.promptVisibleCharacters!==undefined){
    const known=new Set(original.charactersInline.map(x=>x.handle));
    assert(intended.every(h=>known.has(h)),'Visual references invented a new character '+scene.id);
    const speakerHandles=new Set(scene.dialogueInline.map(x=>x.handle).filter(Boolean));
    for(const h of speakerHandles)
      assert(intended.includes(h),'Curated featured cast omitted visible dialogue participant '+scene.id+': '+h);
  }
  if(scene.pageLayout!==undefined){
    assert(after.includes('[PAGE COMPOSITION]'),'Layout omitted '+scene.id);
    assert(after.includes(scene.pageLayout.visualPriority),'Visual intent omitted '+scene.id);
  }
  if(i>3)assert(!after.includes('LANDFALL VISUAL STATE:')||
    ['VIK_S1E02_P08','VIK_S1E02_P22'].includes(scene.id),
    'Repeated apartment boilerplate leaked '+scene.id);
}
assert.equal(cleanCount,19);
for(const id of ['VIK_S1E02_P11','VIK_S1E02_P17','VIK_S1E02_P18','VIK_S1E02_P19']){
  const p=clean.find(x=>x.id===id);
  assert(p.promptSuppress?.includes('direction'),'Missed repeated scene direction '+id);
  assert(!assemble(p,store,0).includes('LANDFALL VISUAL STATE:'),'Duplicate note leaked '+id);
}
const key=clean.find(x=>x.id==='VIK_S1E02_P16');
assert.equal(key.directionInline.length,1,'Unique brass key reference lost or repeated boilerplate survived');
assert(assemble(key,store,0).includes('scratched brass apartment key'),'Key continuity instruction lost');
const bodega=clean.find(x=>x.id==='VIK_S1E02_P07');
assert(bodega.pageLayout.panels[2].placement.includes('refuses good metal'));
assert(bodega.pageLayout.panels[3].placement.includes('card payment'));
assert(!bodega.pageLayout.panels[3].placement.includes('payment refusal'));
function fail(invalid,diagnostic){
  assert.throws(()=>assemble(invalid,store,0),diagnostic,'Sanitizer should fail closed');
}
const first=clean.find(x=>x.id==='VIK_S1E02_P05');
assert.equal(scopes.filter(x=>x.promptVisibleCharacters).length,10,
  'Expected ten audited featured visual-cast trims');
fail({...first,promptVisibleCharacters:'@vik.Carrie'},/must be an array/);
fail({...first,promptVisibleCharacters:['@vik.Nobody']},/Unknown visible character/);
fail({...first,promptVisibleCastOnly:false},/requires visible-cast-only mode/);
fail({...first,promptPanelMode:'unknown'},/Invalid promptPanelMode/);
fail({...first,panelPlan:first.panelPlan.map((x,i)=>i===1?{...x,panel:77}:x)},/ordered numbered panels/);
fail({...first,panelPlan:first.panelPlan.map((x,i)=>i===0?{...x,foo:'bar'}:x)},/Unrecognized panel field/);
fail({...first,panelPlan:first.panelPlan.map((x,i)=>i===0?{...x,dialogueIndices:[0]}:x)},/Invalid or duplicated dialogue index|Dialogue panel mapping conflicts/);
fail({...first,panelPlan:first.panelPlan.map((x,i)=>i===1?{...x,dialogueIndices:[]}:x)},/Unmapped dialogue items/);
fail({...first,dialogueInline:first.dialogueInline.map((x,i)=>i===0?{...x,subtext:'Panel 5'}:x)},/Dialogue panel mapping conflicts/);
assert(inputChars-outputChars>9500,'Expected substantial reduction in repeated scaffolding');
console.log('PASS Vikings Issue 2 chef sanitation: '+cleanCount+' opted-in pages, all 22 retained, approved 2–4 byte-identical');
console.log('PASS no lost actions, locations, dialogue, speakers, panel order, layout, or continuity; '+(inputChars-outputChars)+' prompt characters removed');
