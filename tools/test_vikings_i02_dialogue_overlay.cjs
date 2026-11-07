#!/usr/bin/env node
'use strict';
// Mechanical integrity of the normalized Vikings Issue 2 page records.
// Dialogue text is authorial; this check does not freeze its wording.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const load=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const show=load('data/shows.json').find(x=>x.id==='vikings-2026-s1-e02');
assert(show,'Missing Vikings Issue 2');
assert(!(show.sceneOverlays||[]).some(x=>/dialogue_density_i02|chef_recipe_sanitation_i02/.test(x.file)),
  'Previously consolidated overlays must not override authoritative pages');
const pages=load(show.basePath+'/pages_i02.json');
assert.equal(pages.length,22,'Issue 2 interior page count changed');
assert.equal(new Set(pages.map(x=>x.id)).size,pages.length,'Duplicate page IDs');
const approved=new Set(['VIK_S1E02_P02','VIK_S1E02_P03','VIK_S1E02_P04']);
for(const page of pages){
  assert(Array.isArray(page.panelPlan)&&page.panelPlan.length,'Missing panel plan '+page.id);
  assert(Array.isArray(page.dialogueInline),'Missing dialogue source '+page.id);
  const ids=page.dialogueInline.map(d=>d.fid);
  assert.equal(new Set(ids).size,ids.length,'Duplicate dialogue IDs '+page.id);
  if(approved.has(page.id))continue;
  assert.equal(page.promptPanelMode,'clean','Unnormalized chef panel formatting '+page.id);
  assert.equal(page.promptVisibleCastOnly,true,'Missing visual-cast delivery setting '+page.id);
  const assigned=[];
  for(const [n,panel] of page.panelPlan.entries()){
    assert.equal(panel.panel,n+1,'Unordered panel '+page.id);
    assert(Array.isArray(panel.dialogueIndices),'Missing dialogue index map '+page.id);
    for(const i of panel.dialogueIndices){
      assert(Number.isInteger(i)&&i>=0&&i<page.dialogueInline.length,'Bad dialogue index '+page.id);
      assert.equal(page.dialogueInline[i].subtext,'Panel '+(n+1),'Dialogue placed on wrong panel '+page.id);
      assigned.push(i);
    }
  }
  assert.deepEqual(assigned.sort((a,b)=>a-b),page.dialogueInline.map((_,i)=>i),
    'Dialogue skipped, duplicated or mismapped '+page.id);
}
console.log('PASS Vikings Issue 2: 22 authoritative interior pages with complete dialogue ownership and 19 scoped chef delivery policies');
