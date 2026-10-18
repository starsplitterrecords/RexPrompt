#!/usr/bin/env node
'use strict';
// Mechanical compilation and source-preservation checks for Stardust Issues 3–10.
// Deliberately do not freeze creative sentences, jokes, or dramatic choices.
const fs=require('node:fs');
const vm=require('node:vm');
const zlib=require('node:zlib');
const path=require('node:path');
const assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const read=file=>fs.readFileSync(path.join(root,file),'utf8');
const load=file=>JSON.parse(read(file));
const shows=load('data/shows.json');
const source=read('index.html');
const first=source.indexOf('const SHOW_MANIFEST=');
const last=source.indexOf('function safeFilePart(',first);
assert(first>=0&&last>first,'Current RexPrompt assembler not found');
const context=vm.createContext({});
vm.runInContext(source.slice(first,last)+';globalThis.compile=assembleScene;',context);
const compile=context.compile;
const seriesBase='data/shows/stardust-station';
const data={};
for(const shelf of ['characters','dialogue','settings','regions','factions','direction'])data[shelf+'.json']=load(seriesBase+'/'+shelf+'.json');
const expectedChanged={3:1,4:4,5:2,6:3,7:4,8:3,9:4,10:4};
const summary=[];
const makeMap=(items,name)=>{assert(Array.isArray(items),name+' not an array');const map=new Map(items.map(x=>[x.id,x]));assert.equal(map.size,items.length,'Duplicate entries in '+name);return map};
for(let ep=3;ep<=10;ep++){
  const id='stardust-station-e'+String(ep).padStart(2,'0');
  const show=shows.find(x=>x.id===id);
  assert(show,'Missing show '+id);
  const overlays=show.sceneOverlays||[];
  const sourcePages=ep===3
    ?overlays.filter(o=>o.encoding==='gzip-base64').flatMap(o=>
      JSON.parse(zlib.gunzipSync(Buffer.from(read(show.basePath+'/'+o.file).trim(),'base64')).toString('utf8')))
    :load(seriesBase+'/pages_e'+String(ep).padStart(2,'0')+'.json');
  const expected=ep===5?21:22;
  assert.equal(sourcePages.length,expected,id+' page count changed');
  assert.equal(new Set(sourcePages.map(p=>p.id)).size,expected,'Duplicate source page id '+id);
  const densityPath='editorial/pages_e'+String(ep).padStart(2,'0')+'_density_pass.json';
  const densityIdx=overlays.findIndex(x=>x.file===densityPath);
  assert(densityIdx>=0&&overlays[densityIdx].mergeById&&overlays[densityIdx].strict,
    'Missing strict editorial overlay '+id);
  const density=load(seriesBase+'/'+densityPath);
  const edited=makeMap(density,densityPath);
  assert.equal(edited.size,expectedChanged[ep],'Unexpected edit count '+id);
  let pages=sourcePages.map(x=>({...x}));
  for(const overlay of overlays.slice(0)){
    if(!overlay.mergeById)continue;
    const patches=load(seriesBase+'/'+overlay.file);
    const byId=makeMap(patches,overlay.file);
    for(const target of byId.keys())assert(pages.some(p=>p.id===target),
      'Unknown overlay page '+target+' in '+overlay.file);
    pages=pages.map(p=>({...p,...(byId.get(p.id)||{})}));
  }
  const dlgName='editorial/dialogue_cleanup_e'+String(ep).padStart(2,'0')+'.json';
  const d=makeMap(load(seriesBase+'/'+dlgName),dlgName);
  pages=pages.map(p=>{const edit=d.get(p.id);return edit?{...p,dialogueInline:edit.dialogueInline||edit.sceneDialogue}:p});
  data.__show=show;
  let lines=0;
  const changedIds=[];
  for(let i=0;i<pages.length;i++){
    const p=pages[i],base=sourcePages[i];
    const expectedId='SDS_S1E'+String(ep).padStart(2,'0')+'_P'+String(i+1).padStart(2,'0');
    assert.equal(p.id,expectedId,'Page order drift '+id);
    assert(Array.isArray(p.panelPlan)&&p.panelPlan.length>0,'Missing panel plan '+p.id);
    assert.equal(p.panelPlan.length,base.panelPlan.length,'Panel count drift '+p.id);
    if(typeof p.panelCount==='number')assert.equal(p.panelCount,p.panelPlan.length,'Stored panel count drift '+p.id);
    const chef=compile(p,data,i);
    assert(chef.includes('[PANEL PLAN]')&&chef.includes('[DIALOGUE]'),'Required chef sections missing '+p.id);
    for(const panel of p.panelPlan)assert(chef.includes(panel.text),'Panel missing from assembly '+p.id);
    const dialogue=p.dialogueInline||[];
    for(const d of dialogue){
      const m=String(d.subtext||'').match(/^Panel\s+(\d+)$/i);
      assert(m,'Unassigned line '+p.id+': '+d.text);
      assert(Number(m[1])>=1&&Number(m[1])<=p.panelPlan.length,'Dialogue panel out of range '+p.id);
      assert(d.text&&d.text.trim(),'Blank dialogue '+p.id);
      assert(chef.includes(d.text),'Dialogue lost in compilation '+p.id+': '+d.text);
      lines++;
    }
    if(p.continuityFrom)assert(chef.includes('[CONTINUITY]'),'Dropped continuity '+p.id);
    if(p.pageLayout)assert(chef.includes('[PAGE COMPOSITION]'),'Lost approved page layout '+p.id);
    const delta=edited.get(p.id);
    if(delta){
      changedIds.push(p.id);
      assert.equal(delta.panelPlan.length,base.panelPlan.length,'Edited panel count drift '+p.id);
      assert.deepEqual(Object.keys(delta).sort(),(delta.summary?['id','panelPlan','summary']:['id','panelPlan']),
        'Density overlay carries unrelated production data '+p.id);
      for(let n=0;n<delta.panelPlan.length;n++){
        assert(delta.panelPlan[n].text.startsWith('PANEL '+(n+1)+' —'),'Invalid sequential panel label '+p.id);
      }
    }
  }
  assert.equal(changedIds.length,expectedChanged[ep],'Unexpected editorial coverage '+id);
  summary.push({ep,pages:pages.length,changed:edited.size,lines});
}
console.log('PASS: Stardust E03-E10 issue-wide density integrity');
for(const issue of summary)console.log('Issue '+issue.ep+': '+issue.pages+' pages, '+issue.changed+' scene repairs, '+issue.lines+' dialogue entries compiled');
console.log('TOTAL: '+summary.reduce((n,x)=>n+x.pages,0)+' pages; '+summary.reduce((n,x)=>n+x.changed,0)+' focused repairs; no page IDs, scene order, scripted panel counts, or dialogue lost');
