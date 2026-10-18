#!/usr/bin/env node
'use strict';
// Regression coverage for the browser's canonical page assembler.
// The test runs the actual inline assembler functions rather than a duplicate implementation.
const fs=require('node:fs');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const path=require('node:path');
const root=path.resolve(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const load=p=>JSON.parse(read(p));
const html=read('index.html');
const start=html.indexOf('const SHOW_MANIFEST=');
const end=html.indexOf('function safeFilePart(',start);
assert(start>=0&&end>start,'Could not locate assembler source in index.html');
const context=vm.createContext({});
vm.runInContext(html.slice(start,end)+';globalThis.__assemble=assembleScene;globalThis.__profile=pageAssembly;',context);
const assemble=context.__assemble;
function store(slug,opts={}){
  const base='data/shows/'+slug+'/';
  const out={__show:opts};
  for(const name of ['characters','dialogue','settings','regions','factions','direction']){
    out[name+'.json']=load(base+name+'.json');
  }
  return out;
}
function page(slug,file,id){
  const hit=load('data/shows/'+slug+'/'+file).find(item=>item.id===id);
  assert(hit,'Missing page '+id);return hit;
}
function linesKept(recipe,text){
  for(const line of recipe.dialogueInline||[])assert(text.includes(line.text),'Dropped scripted dialogue: '+line.text);
}
function panelsKept(recipe,text){
  for(const panel of recipe.panelPlan||[]){
    const line=typeof panel==='string'?panel:panel.text||panel.name||panel.summary||JSON.stringify(panel);
    assert(text.includes(line),'Dropped panel instruction');
  }
}
// Vikings: an apartment visual note in a bodega recipe is deliberately not sent to the chef.
const vikStore=store('vikings-2026-s1',{unitLabel:'PAGE',compactCharacters:true,compactDialogue:true,compactContinuity:true,omitSummary:true,omitCameoHandles:true,generationLine:'Viking art direction'});
const bodega=page('vikings-2026-s1','pages_i02.json','VIK_S1E02_P07');
const vb=assemble(bodega,vikStore,0);
assert(vb.includes('Recurring Bushwick neighborhood bodega'));
assert(!vb.includes('LANDFALL VISUAL STATE: Apartment 5B'));
assert(!vb.includes('[DIRECTION]'));
assert(vb.includes('[PANEL PLAN]')&&vb.includes('[DIALOGUE]'));
linesKept(bodega,vb);panelsKept(bodega,vb);
assert.equal(bodega.dialogueInline.length,18);
const apartment=page('vikings-2026-s1','pages_i02.json','VIK_S1E02_P04');
const va=assemble(apartment,vikStore,0);
assert(!va.includes('[SETTING]'));
assert(va.includes('Bushwick studio apartment 5B')); // still in panel action/location
linesKept(apartment,va);panelsKept(apartment,va);
// Stardust: names only and no duplicated summary; setting and action remain.
const sdsStore=store('stardust-station',{unitLabel:'PAGE',generationLine:'Stardust art direction'});
for(const id of ['SDS_S1E04_P01','SDS_S1E04_P02','SDS_S1E04_P03']){
  const p=page('stardust-station','pages_e04.json',id);
  const result=assemble(p,sdsStore,0);
  assert(!result.includes(p.summary));
  assert(result.includes('[CAST]')&&!result.includes('[CHARACTERS]'));
  assert(result.includes('[SETTING]'));
  if(id==='SDS_S1E04_P02'){
    const setting=sdsStore['settings.json'][p.setting];
    assert(result.includes(setting.name),'Repeat location label missing');
    assert(!result.includes(setting.text),'Repeated setting prose was not trimmed');
  }
  linesKept(p,result);panelsKept(p,result);
}
// Legacy pages retain full descriptions until explicitly configured.
const unchanged=page('stardust-station','pages_e04.json','SDS_S1E04_P04');
const legacy=assemble(unchanged,sdsStore,0);
assert(legacy.includes(unchanged.summary));
assert(legacy.includes('[CHARACTERS]'));
linesKept(unchanged,legacy);
// Rex Fleet: suppress only detailed recurring setting text, not the visible location.
const rexStore=store('rex-fleet-s1',{unitLabel:'PAGE',generationLine:'Rex art direction'});
const bridge=page('rex-fleet-s1','pages_i02.json','RF_I02_P04');
const r=assemble(bridge,rexStore,0);
assert(r.includes('[SETTING]\n'));
assert(!r.includes('[SETTING CONTINUITY]'));
assert(r.includes('[CAST]')&&!r.includes('[CHARACTERS]'));
linesKept(bridge,r);panelsKept(bridge,r);
// Never allow suppression labels to silently remove story action or dialogue.
const forced={...bridge,promptSuppress:['summary','production','characters']};
const forcedText=assemble(forced,rexStore,0);
assert(forcedText.includes('[PANEL PLAN]')&&forcedText.includes('[DIALOGUE]'));
linesKept(forced,forcedText);panelsKept(forced,forcedText);
assert(!forcedText.includes('[CAST]')&&!forcedText.includes('[CHARACTERS]'));
for(const forbidden of ['dialogue','panelPlan','continuity']){
  assert.throws(()=>assemble({...bridge,promptSuppress:[forbidden]},rexStore,0),/Invalid or protected prompt suppression/);
}
assert.throws(()=>assemble({...unchanged,promptSuppress:['setting']},sdsStore,0),/Cannot suppress setting without explicit location/);
assert.throws(()=>assemble({...bridge,promptCharacterMode:'mystery'},rexStore,0),/Invalid promptCharacterMode/);
assert.throws(()=>assemble({...bridge,promptSettingMode:'mystery'},rexStore,0),/Invalid promptSettingMode/);
assert(html.includes('prompt-suppress.js?v=20261018-data-profile-1'));
console.log('PASS: page-scoped recipe assembly, protected story beats, legacy behavior, and three series fixtures');
