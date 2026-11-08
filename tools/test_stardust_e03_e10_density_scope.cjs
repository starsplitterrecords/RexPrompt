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
const summary=[];
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
  assert(!overlays.some(o=>o.mergeById),'Stardust issue must use canonical page fields '+id);
  const pages=sourcePages;
  data.__show=show;
  let lines=0;
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

  }
  summary.push({ep,pages:pages.length,lines});
}
console.log('PASS: Stardust E03-E10 issue-wide density integrity');
for(const issue of summary)console.log('Issue '+issue.ep+': '+issue.pages+' canonical pages, '+issue.lines+' dialogue entries compiled');
console.log('TOTAL: '+summary.reduce((n,x)=>n+x.pages,0)+' pages; no page IDs, scene order, scripted panel counts, or dialogue lost');
