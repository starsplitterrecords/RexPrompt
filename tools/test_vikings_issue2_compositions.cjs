#!/usr/bin/env node
'use strict';
// Mechanical regression: Vikings Issue 2 layouts may not replace script,
// invent panels, reorder dialogue or rewrite approved production pages.
const fs=require('node:fs');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const path=require('node:path');
const root=path.resolve(__dirname,'..');
const pageFile='data/shows/vikings-2026-s1/pages_i02.json';
const pages=JSON.parse(fs.readFileSync(path.join(root,pageFile),'utf8'));
const ids=new Set(pages.map(p=>p.id));
assert.equal(ids.size,22,'Unexpected duplicate Vikings page ID');
const approved=new Set(['VIK_S1E02_P02','VIK_S1E02_P03','VIK_S1E02_P04']);
assert.equal(pages.length,22,'Vikings interior page count changed');
assert(pages.every((p,i)=>p.id==='VIK_S1E02_P'+String(i+2).padStart(2,'0')),'Page order changed');
for(const page of pages)if(approved.has(page.id))assert(!page.pageLayout,'Approved page must not be relaid out: '+page.id);
const expected=pages.filter(p=>!approved.has(p.id));
assert.equal(expected.length,19);
const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
const start=html.indexOf('const SHOW_MANIFEST='),end=html.indexOf('function safeFilePart(',start);
assert(start>=0&&end>start,'Cannot load canonical browser assembler');
const context=vm.createContext({});
vm.runInContext(html.slice(start,end)+
 ';globalThis.layoutApi={validatePageLayout:typeof validatePageLayout==="function"?validatePageLayout:null,assembleScene};',context);
const api=context.layoutApi;
assert.equal(typeof api.validatePageLayout,'function',
 'BLOCKED: page-layout architecture was explicitly reverted on main. Restore or replace Phase A before merging authored Vikings layouts.');
const show=JSON.parse(fs.readFileSync(path.join(root,'data/shows.json'),'utf8')).find(s=>s.id==='vikings-2026-s1-e02');
assert(show,'Vikings Issue 2 show config missing');
const storage={__show:show};
for(const shelf of ['characters','settings','dialogue','direction','regions','factions']){
  storage[shelf+'.json']=JSON.parse(fs.readFileSync(path.join(root,'data/shows/vikings-2026-s1',shelf+'.json'),'utf8'));
}
for(const [i,p] of pages.entries()){
 if(!p.pageLayout)continue;
 const layout=api.validatePageLayout(p);
 assert.equal(layout.panels.length,p.panelPlan.length,'Incomplete panel hierarchy '+p.id);
 const unconfigured={...p};delete unconfigured.pageLayout;
 const original=api.assembleScene(unconfigured,storage,i),assembled=api.assembleScene(p,storage,i);
 assert(assembled.includes('[PAGE COMPOSITION]'),'Composer failed to emit layout '+p.id);
 assert(assembled.indexOf('[PAGE COMPOSITION]')<assembled.indexOf('[PANEL PLAN]'),'Incorrect section order '+p.id);
 assert.equal(assembled.slice(assembled.indexOf('\n[PANEL PLAN]')),
              original.slice(original.indexOf('\n[PANEL PLAN]')),
              'Composition changed script or dialogue '+p.id);
}
const compositions=new Set(expected.map(p=>p.pageLayout?.composition));
assert(compositions.size>=6,'Insufficient visual range across the issue');
console.log('PASS Vikings II: 19 unapproved-page layouts, three approved pages protected, all scripted beats preserved');
