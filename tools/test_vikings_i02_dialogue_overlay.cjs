#!/usr/bin/env node
'use strict';
// Mechanical integrity check for the Vikings Issue 2 dialogue pass.
// This does not freeze creative wording or prescribe a dramatic beat.
const fs=require('node:fs');
const path=require('node:path');
const assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const shows=read('data/shows.json');
const show=shows.find(s=>s.id==='vikings-2026-s1-e02');
assert(show,'Missing active Vikings Issue 2 show');
const location='editorial/dialogue_density_i02.json';
assert(show.sceneOverlays?.some(o=>o.file===location&&o.mergeById),'Dialogue changes are not in the active recipe load path');
const base=read(show.basePath+'/pages_i02.json');
const patches=read(show.basePath+'/'+location);
assert.equal(new Set(patches.map(p=>p.id)).size,patches.length,'Duplicate overlay IDs');
const baseById=new Map(base.map(p=>[p.id,p]));
assert.equal(baseById.size,base.length,'Duplicate base page IDs');
const approved=new Set(['VIK_S1E02_P02','VIK_S1E02_P03','VIK_S1E02_P04']);
let beforeLines=0,afterLines=0,beforeWords=0,afterWords=0;
const words=s=>(String(s||'').trim().match(/\S+/g)||[]).length;
for(const patch of patches){
  const original=baseById.get(patch.id);
  assert(original,'Orphan overlay page '+patch.id);
  assert(!approved.has(patch.id),'Approved artwork script must not be silently modified: '+patch.id);
  assert.deepEqual(Object.keys(patch).sort(),['dialogueInline','id','panelPlan'].sort(),
    'Patch must not change page identity/setting/continuity or composition metadata');
  assert.equal(patch.panelPlan.length,original.panelPlan.length,'Panel count changed: '+patch.id);
  assert(patch.dialogueInline.length>0&&patch.dialogueInline.length<=original.dialogueInline.length,'Invalid edited dialogue list: '+patch.id);
  assert.equal(new Set(patch.dialogueInline.map(d=>d.fid)).size,patch.dialogueInline.length,'Duplicate dialogue IDs '+patch.id);
  const byFid=new Map(original.dialogueInline.map(d=>[d.fid,d]));
  const referenced=[];
  for(let n=0;n<patch.panelPlan.length;n++){
    const panel=patch.panelPlan[n],baseline=original.panelPlan[n];
    assert.equal(panel.panel,baseline.panel,'Panel ID changed: '+patch.id);
    assert.equal(panel.shotType,baseline.shotType,'Shot type changed: '+patch.id);
    assert.equal(panel.location,baseline.location,'Location changed: '+patch.id);
    assert(Array.isArray(panel.dialogueIndices),'Missing dialogue map: '+patch.id);
    for(const index of panel.dialogueIndices){
      assert(Number.isInteger(index)&&index>=0&&index<patch.dialogueInline.length,'Invalid dialogue index: '+patch.id);
      const line=patch.dialogueInline[index];
      assert.equal(line.subtext,'Panel '+(n+1),'Line mapped to wrong panel: '+patch.id);
      referenced.push(index);
    }
  }
  assert.deepEqual(referenced.sort((a,b)=>a-b),patch.dialogueInline.map((_,i)=>i),'Orphan, duplicate or missing line: '+patch.id);
  for(const line of patch.dialogueInline){
    const prior=byFid.get(line.fid);
    assert(prior,'Inserted identity masquerading as old dialogue line: '+line.fid);
    assert.equal(line.handle,prior.handle,'Speaker changed: '+line.fid);
    assert.equal(line.subtext,prior.subtext,'Dialogue ownership changed: '+line.fid);
    assert(typeof line.text==='string'&&line.text.trim(),'Blank dialogue: '+line.fid);
  }
  // Updated panel descriptions are allowed only to reconcile the bodega
  // transaction's action with the same-panel dialogue ownership.
  if(patch.id!=='VIK_S1E02_P07'){
    for(let n=0;n<patch.panelPlan.length;n++)assert.equal(patch.panelPlan[n].action,original.panelPlan[n].action,'Unexpected action rewrite: '+patch.id);
  }else{
    for(let n=0;n<patch.panelPlan.length;n++)if(n!==2&&n!==3)
      assert.equal(patch.panelPlan[n].action,original.panelPlan[n].action,'Unexpected bodega action rewrite: '+patch.id);
  }
  beforeLines+=original.dialogueInline.length;afterLines+=patch.dialogueInline.length;
  beforeWords+=original.dialogueInline.reduce((n,d)=>n+words(d.text),0);
  afterWords+=patch.dialogueInline.reduce((n,d)=>n+words(d.text),0);
}
assert.equal(base.length,22,'Issue 2 interior page count changed');
console.log('PASS Vikings Issue 2 dialogue-overlay integrity: '+patches.length+' pages; '+base.length+' total interior pages; approved P02–P04 untouched');
console.log('Edited pages dialogue: '+beforeLines+' → '+afterLines+' items; '+beforeWords+' → '+afterWords+' words (report only; no hard-coded creative thresholds)');
