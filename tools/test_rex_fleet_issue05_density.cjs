#!/usr/bin/env node
'use strict';
// Existing Rex Fleet Issue 05 production integrity check, normalized-source edition.
// Validate recipe mechanics without freezing creative wording or resurrecting overlays.
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8'),load=p=>JSON.parse(read(p));
const show=load('data/shows.json').find(x=>x.id==='rex-fleet-i05');
assert(show,'Issue 05 not registered');
assert(!(show.sceneOverlays||[]).some(x=>/issue_05_/.test(x.file)),
 'Consolidated story patches must not remain in the live recipe load path');
const base=show.basePath;
const original=JSON.parse(zlib.gunzipSync(Buffer.from(read(base+'/encoded/pages_i05.json.gzb64').trim(),'base64')).toString('utf8'));
const pages=original;
assert.equal(pages.length,21,'Issue 05 authoritative page count changed');
assert.equal(new Set(pages.map(x=>x.id)).size,pages.length,'Duplicate source page IDs');
const source=read('index.html'),a=source.indexOf('const SHOW_MANIFEST='),b=source.indexOf('function safeFilePart(',a);
assert(a>=0&&b>a,'Canonical assembler extraction unavailable');
const context=vm.createContext({});
vm.runInContext(source.slice(a,b)+';globalThis.build=assembleScene;',context);
const store={__show:show};
for(const f of ['characters','dialogue','settings','regions','factions','direction'])store[f+'.json']=load(base+'/'+f+'.json');
let lines=0;
for(const [index,page] of pages.entries()){
  assert(Array.isArray(page.panelPlan)&&page.panelPlan.length,'Missing scripted panels '+page.id);
  if(page.pageLayout)assert.equal(page.pageLayout.panels.length,page.panelPlan.length,'Page layout panel mismatch '+page.id);
  for(const line of page.dialogueInline||[]){
    assert(line.text?.trim()&&line.speaker&&line.handle,'Incomplete dialogue '+page.id);
    const match=String(line.subtext||'').match(/^Panel (\d+)$/);
    assert(match&&Number(match[1])>=1&&Number(match[1])<=page.panelPlan.length,'Wrong dialogue panel '+page.id);
    lines++;
  }
  const output=context.build(page,store,index);
  assert(output.includes('[PANEL PLAN]'),'Missing assembled panel plan '+page.id);
  for(const action of page.panelPlan){
    const text=typeof action==='string'?action:action.action||action.text||action.summary;
    if(text?.trim())assert(output.includes(text),'Panel action not delivered '+page.id);
  }
  for(const line of page.dialogueInline||[])assert(output.includes(line.text),'Authored dialogue not delivered '+page.id);
}
console.log('PASS Rex Fleet I05: '+pages.length+' normalized interior pages assembled; '+lines+' authored dialogue records delivered');
