#!/usr/bin/env node
'use strict';
// Azure Reach: validate effective dialogue delivery from authoritative encoded pages.
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),read=f=>fs.readFileSync(path.join(root,f),'utf8'),json=f=>JSON.parse(read(f));
const shows=json('data/shows.json'),base='data/shows/azure-reach-s1/',html=read('index.html'),a=html.indexOf('const SHOW_MANIFEST='),b=html.indexOf('function safeFilePart(',a),ctx=vm.createContext({});
assert(a>=0&&b>a,'Assembler extraction missing');
vm.runInContext(html.slice(a,b)+';globalThis.make=assembleScene;',ctx);
const store={};for(const x of ['characters','dialogue','settings','regions','factions','direction'])store[x+'.json']=json(base+x+'.json');
let count=0,lines=0;
for(let n=1;n<=6;n++){
 const id=n===1?'azure-reach-s1':'azure-reach-s1-e0'+n,show=shows.find(x=>x.id===id);assert(show,'Missing Azure issue '+n);
 const pages=show.sceneOverlays.filter(x=>/^encoded\/pages_e0/.test(x.file)).flatMap(x=>JSON.parse(zlib.gunzipSync(Buffer.from(read(base+x.file).trim(),'base64')).toString('utf8')));
 assert.equal(pages.length,22,'Issue count changed '+n);
 if(n>1)assert(!show.dialogueOverlays?.some(x=>/dialogue_c_e0/.test(x.file)),'Legacy dialogue overlay still active '+n);
 for(const [i,page] of pages.entries()){
  const out=ctx.make(page,{...store,__show:show},i);
  assert(out.includes('[PANEL PLAN]'),'Missing panel plan '+page.id);
  for(const d of page.dialogueInline||[]){
    assert(d.text?.trim(),'Blank dialogue '+page.id);
    const m=String(d.subtext||'').match(/^Panel (\d+)$/);
    if(m)assert(Number(m[1])>=1&&Number(m[1])<=page.panelPlan.length,'Invalid dialogue owner '+page.id);
    assert(out.includes(d.text),'Missing authored text '+page.id);
    lines++;
  }
  count++;
 }
}
console.log('PASS Azure Reach: '+count+' authoritative story pages, '+lines+' dialogue items delivered without reapplying overlays');
