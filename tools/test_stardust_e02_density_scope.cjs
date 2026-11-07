#!/usr/bin/env node
'use strict';
// Existing Stardust Issue 2 density/source integrity check (normalized source).
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),zlib=require('node:zlib'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8'),json=p=>JSON.parse(read(p));
const show=json('data/shows.json').find(x=>x.id==='stardust-station-e02');
assert(show,'Missing Stardust Issue 2');
const base=show.basePath,encoded=show.sceneOverlays.filter(x=>x.encoding==='gzip-base64');
const scenes=encoded.flatMap(x=>JSON.parse(zlib.gunzipSync(Buffer.from(read(base+'/'+x.file).trim(),'base64')).toString('utf8')));
assert.equal(scenes.length,22,'Issue count changed');
assert.equal(new Set(scenes.map(x=>x.id)).size,22,'Duplicate source page IDs');
const html=read('index.html'),start=html.indexOf('const SHOW_MANIFEST='),end=html.indexOf('function safeFilePart(',start),ctx=vm.createContext({});
assert(start>=0&&end>start,'Assembler unavailable');
vm.runInContext(html.slice(start,end)+';globalThis.build=assembleScene;',ctx);
const store={__show:show};for(const x of ['characters','settings','regions','factions','direction','dialogue'])store[x+'.json']=json(base+'/'+x+'.json');
let dialogueCount=0;
for(const [i,page] of scenes.entries()){
  assert.equal(page.id,'SDS_S1E02_P'+String(i+1).padStart(2,'0'),'Page ordering drift');
  assert.equal(page.panelCount,page.panelPlan.length,'Panel count drift '+page.id);
  const cast=new Set((page.charactersInline||[]).map(x=>x.handle));
  for(const d of page.dialogueInline||[]){
    const match=String(d.subtext||'').match(/^Panel\s+(\d+)$/i);
    assert(match&&Number(match[1])>=1&&Number(match[1])<=page.panelPlan.length,'Dialogue panel mismatch '+page.id);
    assert(d.text?.trim(),'Empty dialogue '+page.id);
    if(d.handle?.startsWith('@'))assert(cast.has(d.handle),'Speaker not in page cast '+page.id);
    dialogueCount++;
  }
  const out=ctx.build(page,store,i);
  assert(out.includes('[PANEL PLAN]')&&out.includes('[DIALOGUE]'),'Chef output missing story sections '+page.id);
  for(const panel of page.panelPlan)assert(out.includes(panel.text),'Lost authored action '+page.id);
  for(const line of page.dialogueInline||[])assert(out.includes(line.text),'Lost authored dialogue '+page.id);
  assert.equal(page.promptCharacterMode,'cast','Missing original page scoping '+page.id);
}
console.log('PASS Stardust I02: 22 normalized authoritative story pages, '+dialogueCount+' dialogue items delivered');
