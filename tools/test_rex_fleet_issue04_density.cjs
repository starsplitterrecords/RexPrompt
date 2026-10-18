#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const load=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const shows=load('data/shows.json');
const show=shows.find(s=>s.id==='rex-fleet-i04');
assert(show,'Issue 4 not registered');
const base=show.basePath;
const text=fs.readFileSync(path.join(root,base,'encoded/pages_i04.json.gzb64'),'utf8');
const originals=JSON.parse(zlib.gunzipSync(Buffer.from(text.trim(),'base64')).toString('utf8'));
const overlayName='issue_04_dialogue_density_overlay.json';
const revisions=load(base+'/'+overlayName);
const registered=show.sceneOverlays.filter(x=>x.file===overlayName);
assert.equal(registered.length,1,'Unique Issue 4 overlay registration expected');
assert(registered[0].mergeById,'Dialogue overlay must merge by page ID');
assert.equal(new Set(revisions.map(x=>x.id)).size,revisions.length,'Duplicate page patches');
const ids=new Set(originals.map(x=>x.id));
assert(revisions.every(x=>ids.has(x.id)),'Revision references a missing page');
assert(revisions.every(x=>Object.keys(x).every(k=>['id','dialogueInline','panelPlan'].includes(k))),
  'Unexpected production data mutated by editorial overlay');
const overrides=new Map(revisions.map(x=>[x.id,x]));
const pages=originals.map(x=>({...x,...(overrides.get(x.id)||{})}));
assert.equal(pages.length,originals.length,'Issue length changed');
for(let i=0;i<pages.length;i++){
 const old=originals[i],page=pages[i];
 assert.equal(page.id,old.id,'Page order or ID altered');
 assert.equal(page.panelPlan?.length,old.panelPlan?.length,'Panel count altered on '+page.id);
 if(!overrides.has(page.id))assert.deepEqual(page,old,'Untouched page changed');
 const dialogue=page.dialogueInline||[];
 let previous=0;
 for(const line of dialogue){
  assert(line?.text?.trim()&&line.handle&&line.speaker,'Incomplete dialogue record '+page.id);
  const m=String(line.subtext||'').match(/^Panel (\d+)$/);
  assert(m,'Explicit panel mapping missing '+page.id);
  const number=Number(m[1]);
  assert(number>=1&&number<=page.panelPlan.length,'Invalid dialogue panel '+page.id);
  assert(number>=previous,'Backtracking lettering sequence on '+page.id);
  previous=number;
 }
}
const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
const start=html.indexOf('const SHOW_MANIFEST='),end=html.indexOf('function safeFilePart(',start);
assert(start>=0&&end>start,'Current RexPrompt assembler unavailable');
const sandbox=vm.createContext({});
vm.runInContext(html.slice(start,end)+';globalThis.assemble=assembleScene;',sandbox);
const store={__show:show};
for(const s of ['characters','dialogue','settings','regions','factions','direction'])store[s+'.json']=load(base+'/'+s+'.json');
for(let i=0;i<pages.length;i++){
 const page=pages[i],rendered=sandbox.assemble(page,store,i);
 const old=originals[i],oldRendered=sandbox.assemble(old,store,i);
 assert(rendered.includes('[PANEL PLAN]'),'Missing panel plan '+page.id);
 for(const p of page.panelPlan){
  const text=typeof p==='string'?p:p.text||p.name||p.summary||JSON.stringify(p);
  assert(rendered.includes(text),'Missing authored panel '+page.id);
 }
 for(const d of page.dialogueInline||[])assert(rendered.includes(d.text),'Missing dialogue '+page.id);
 if(!overrides.has(page.id))assert.equal(rendered,oldRendered,'Unchanged recipe drift '+page.id);
 if(overrides.has(page.id)){
  assert.equal(page.charactersInline.length,old.charactersInline.length,'Characters altered '+page.id);
  assert.equal(page.summary,old.summary,'Story summary altered '+page.id);
  assert.equal(page.settingText,old.settingText,'Setting altered '+page.id);
  assert.equal(page.directionInline.length,old.directionInline.length,'Direction altered '+page.id);
 }
}
const changed=revisions.map(x=>x.id).join(', ');
console.log('PASS Rex Fleet Issue 4: '+pages.length+' interior pages assembled, '+revisions.length+' scoped revisions ('+changed+'), ordered lettering, intact panel counts and untouched recipes');
