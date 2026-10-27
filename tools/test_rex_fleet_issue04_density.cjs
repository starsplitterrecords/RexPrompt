#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const load=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const base='data/shows/rex-fleet-s1';
const show=load('data/shows.json').find(s=>s.id==='rex-fleet-i04');
assert(show,'Issue 4 registered');
const entries=show.sceneOverlays;
const rewriteName='issue_04_character_dialogue_rewrite.json';
const correction='issue_04_thunderbreak_command_correction.json';
const rewriteIndex=entries.findIndex(x=>x.file===rewriteName);
const correctionIndex=entries.findIndex(x=>x.file===correction);
const layoutIndex=entries.findIndex(x=>x.file==='page_layout_i04.json');
assert(rewriteIndex>correctionIndex&&correctionIndex>=0,'Rewrite must follow Deka authority correction');
assert(layoutIndex>rewriteIndex,'Page layout must follow story rewrite');
assert(entries[rewriteIndex].mergeById&&entries[rewriteIndex].strict,'Strict ID-merged story overlay required');
assert(!entries.some(x=>x.file==='issue_04_dialogue_density_overlay.json'),'Old dialogue overlay must not be applied after consolidated rewrite');
const data=fs.readFileSync(path.join(root,base,'encoded/pages_i04.json.gzb64'),'utf8');
const originals=JSON.parse(zlib.gunzipSync(Buffer.from(data.trim(),'base64')).toString('utf8'));
const corrections=load(base+'/'+correction);
const revisions=load(base+'/'+rewriteName);
const layouts=load(base+'/page_layout_i04.json');
assert.equal(originals.length,31);
assert.equal(revisions.length,31,'Every story page must be rewritten');
assert.equal(new Set(revisions.map(x=>x.id)).size,31,'Duplicate rewrite IDs');
const ids=originals.map(x=>x.id);
assert.deepEqual(revisions.map(x=>x.id),ids,'Rewritten page IDs must match original order');
const correctionById=new Map(corrections.map(x=>[x.id,x]));
const layoutById=new Map(layouts.map(x=>[x.id,x]));
const pages=originals.map(p=>({...p,...(correctionById.get(p.id)||{}),...revisions.find(x=>x.id===p.id),...(layoutById.get(p.id)||{})}));
assert.equal(pages.length,31);
let lines=0;
for(let i=0;i<pages.length;i++){
 const p=pages[i],o=originals[i],rev=revisions[i];
 assert(p.summary&&p.panelPlan?.length>0,'Missing full scene '+p.id);
 assert.equal(p.panelPlan.length,o.panelPlan.length,'Revised panel count / inherited layout mismatch '+p.id);
 assert.equal(p.pageLayout.panels.length,p.panelPlan.length,'Visual layout panel count mismatch '+p.id);
 assert(p.settingText,'Missing setting '+p.id);
 let prior=0;
 for(const d of p.dialogueInline||[]){
  assert(d.text?.trim()&&d.handle&&d.speaker,'Incomplete spoken line '+p.id);
  const m=String(d.subtext).match(/^Panel (\d+)$/);
  assert(m,'Explicit speaker panel assignment required '+p.id);
  const n=Number(m[1]);
  assert(n>=1&&n<=p.panelPlan.length&&n>=prior,'Balloon ownership out of order '+p.id);
  prior=n;lines++;
 }
 assert(!p.dialogueInline?.some(d=>d.speaker==='Venn'),'Venn remains absent under tribunal removal');
}
assert(lines>=200,'Character dialogue rewrite did not materially expand conversations');
assert(pages.filter(p=>!p.dialogueInline.length).map(p=>p.id).join(',')==='RF_I04_P28,RF_I04_P31','Preserve silent Pike turn and final montage');
for(const n of [4,5,14,19,21,23]){
 const p=pages[n-1];
 assert((p.charactersInline||[]).every(c=>!c.name?.includes('Ella Venn')),'Venn must not command '+p.id);
}
for(const n of [4,5,19,21])assert(pages[n-1].dialogueInline.some(d=>d.speaker==='Deka'),'Deka command required page '+n);
assert(/radiator/i.test(pages[20].summary),'Gravefire lasting damage preserved');
assert(/grain pallet/i.test(pages[19].summary),'Relief cargo loss preserved');
assert(/without authorization|unauthorized|disobey|independently/i.test(pages[18].summary+' '+pages[18].panelPlan.join(' ')),'Junior Fleet rescue must be an independent choice');
assert(/crop domes/i.test(pages[24].summary),'Billie rejects agricultural dependency strike');
const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
const start=html.indexOf('const SHOW_MANIFEST='),end=html.indexOf('function safeFilePart(',start);
assert(start>=0&&end>start,'Current assembler unavailable');
const sandbox=vm.createContext({});
vm.runInContext(html.slice(start,end)+';globalThis.assemble=assembleScene;',sandbox);
const store={__show:show};
for(const f of ['characters','dialogue','settings','regions','factions','direction'])store[f+'.json']=load(base+'/'+f+'.json');
for(let i=0;i<pages.length;i++){
 const rendered=sandbox.assemble(pages[i],store,i);
 assert(rendered.includes('[PANEL PLAN]')&&rendered.includes('[PAGE COMPOSITION]'),'Missing assembled page '+pages[i].id);
 for(const d of pages[i].dialogueInline||[])assert(rendered.includes(d.text),'Missing authored line '+pages[i].id+': '+d.text);
 assert(!rendered.includes('Invalid pageLayout'),'Bad layout '+pages[i].id);
}
console.log('PASS Rex Fleet Issue 4: 31 rewritten assembled story pages; '+lines+' mapped spoken lines; Deka command and rescue continuity; 2 intentional silent pages.');
