#!/usr/bin/env node
'use strict';
// Azure Reach existing layout check, now against normalized encoded page sources.
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),read=f=>fs.readFileSync(path.join(root,f),'utf8'),json=f=>JSON.parse(read(f));
const base='data/shows/azure-reach-s1/',shows=json('data/shows.json'),html=read('index.html'),a=html.indexOf('const SHOW_MANIFEST='),b=html.indexOf('function safeFilePart(',a),ctx=vm.createContext({});
assert(a>=0&&b>a,'Assembler source absent');
vm.runInContext(html.slice(a,b)+';globalThis.api={assembleScene,validatePageLayout};',ctx);
const {assembleScene:assemble,validatePageLayout:validate}=ctx.api,store={};
for(const s of ['characters','dialogue','settings','regions','factions','direction'])store[s+'.json']=json(base+s+'.json');
let layouts=0;
for(let i=1;i<=6;i++){
 const show=shows.find(s=>s.id===(i===1?'azure-reach-s1':'azure-reach-s1-e0'+i));assert(show,'Missing issue '+i);
 const pages=show.sceneOverlays.filter(x=>/^encoded\/pages_e0/.test(x.file)).flatMap(x=>JSON.parse(zlib.gunzipSync(Buffer.from(read(base+x.file).trim(),'base64')).toString('utf8')));
 assert.equal(pages.length,22,'Page count '+i);
 for(const [index,page] of pages.entries()){
  if(!page.pageLayout)continue;
  validate(page);layouts++;
  assert.equal(page.pageLayout.panels.length,page.panelPlan.length,'Unbalanced page composition '+page.id);
  const output=assemble(page,{...store,__show:show},index);
  assert(output.indexOf('[PAGE COMPOSITION]')>=0&&output.indexOf('[PAGE COMPOSITION]')<output.indexOf('[PANEL PLAN]'),'Page composition not sent before story '+page.id);
  for(const d of page.dialogueInline||[])assert(output.includes(d.text),'Dialogue omitted '+page.id);
 }
}
console.log('PASS Azure Reach: '+layouts+' normalized page compositions assembled and matched to authored panel plans');
