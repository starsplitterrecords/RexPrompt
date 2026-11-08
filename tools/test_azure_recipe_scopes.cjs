#!/usr/bin/env node
'use strict';
// Azure Reach: scoped chef delivery from current authoritative page records.
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),read=f=>fs.readFileSync(path.join(root,f),'utf8'),json=f=>JSON.parse(read(f));
const html=read('index.html'),a=html.indexOf('const SHOW_MANIFEST='),b=html.indexOf('function safeFilePart(',a),ctx=vm.createContext({});
assert(a>=0&&b>a,'Assembler source missing');
vm.runInContext(html.slice(a,b)+';globalThis.api={assembleScene,pageAssembly,validatePageLayout};',ctx);
const {assembleScene:assemble,pageAssembly,validatePageLayout:validate}=ctx.api;
const shows=json('data/shows.json'),base='data/shows/azure-reach-s1/',store={};
for(const s of ['characters','dialogue','settings','regions','factions','direction'])store[s+'.json']=json(base+s+'.json');
let scoped=0;
for(let n=2;n<=6;n++){
 const show=shows.find(x=>x.id==='azure-reach-s1-e0'+n);assert(show,'Missing issue '+n);
 const pages=show.sceneOverlays.filter(x=>/^encoded\/pages_e0/.test(x.file)).flatMap(x=>JSON.parse(zlib.gunzipSync(Buffer.from(read(base+x.file).trim(),'base64')).toString('utf8')));
 for(const [index,page] of pages.entries()){
  if(!page.promptSuppress&&!page.promptCharacterMode&&!page.promptSettingMode)continue;
  scoped++;pageAssembly(page,show);if(page.pageLayout)validate(page);
  const out=assemble(page,{...store,__show:show},index);
  assert(out.includes('[PANEL PLAN]'),'Missing story panels '+page.id);
  for(const d of page.dialogueInline||[])assert(out.includes(d.text),'Dialogue lost '+page.id);
  if(page.promptSuppress?.includes('summary'))assert(!out.includes(page.summary),'Suppression ignored '+page.id);
  if(page.promptSettingMode==='label')assert(out.includes(store['settings.json'][page.setting].name),'Location label missing '+page.id);
 }
}
console.log('PASS Azure Reach: '+scoped+' normalized page-scoped production recipes assembled');
