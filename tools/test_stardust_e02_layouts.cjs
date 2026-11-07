#!/usr/bin/env node
'use strict';
// Stardust Issue 2: existing layout delivery check against normalized page sources.
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8'),json=p=>JSON.parse(read(p));
const show=json('data/shows.json').find(x=>x.id==='stardust-station-e02');
assert(show,'Missing Stardust Issue 2');
const base=show.basePath;
const pages=show.sceneOverlays.filter(x=>x.encoding==='gzip-base64').flatMap(x=>JSON.parse(zlib.gunzipSync(Buffer.from(read(base+'/'+x.file).trim(),'base64')).toString('utf8')));
assert.equal(pages.length,22);
assert.equal(new Set(pages.map(x=>x.id)).size,pages.length,'Duplicate authored page');
const html=read('index.html'),a=html.indexOf('const SHOW_MANIFEST='),b=html.indexOf('function safeFilePart(',a),context=vm.createContext({});
assert(a>=0&&b>a,'Assembler code unavailable');
vm.runInContext(html.slice(a,b)+';globalThis.exportsForCheck={assembleScene,validatePageLayout};',context);
const {assembleScene:assemble,validatePageLayout:validate}=context.exportsForCheck;
const store={__show:show};for(const f of ['characters','dialogue','settings','regions','factions','direction'])store[f+'.json']=json(base+'/'+f+'.json');
let withInsets=0;
for(const [i,page] of pages.entries()){
  assert(page.pageLayout,'Missing authoritative page layout '+page.id);
  validate(page);
  assert.equal(page.pageLayout.panels.length,page.panelPlan.length,'Layout does not match panel plan '+page.id);
  const without=assemble({...page,pageLayout:undefined},store,i);
  const withLayout=assemble(page,store,i);
  assert(!without.includes('[PAGE COMPOSITION]')&&withLayout.includes('[PAGE COMPOSITION]'),'Layout delivery missing '+page.id);
  assert(withLayout.indexOf('[PAGE COMPOSITION]')<withLayout.indexOf('[PANEL PLAN]'),'Wrong layout order '+page.id);
  assert.equal(withLayout.slice(withLayout.indexOf('\n[PANEL PLAN]')),without.slice(without.indexOf('\n[PANEL PLAN]')),'Composition modified story or dialogue '+page.id);
  for(const line of page.dialogueInline||[])assert(withLayout.includes(line.text),'Missing dialogue '+page.id);
  withInsets+=page.pageLayout.panels.filter(p=>p.role==='inset').length;
}
console.log('PASS Stardust I02: 22 authoritative composed page recipes, '+withInsets+' insets; exact panel/dialogue delivery preserved');
