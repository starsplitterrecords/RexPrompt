#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8'),json=p=>JSON.parse(read(p));
const html=read('index.html'),from=html.indexOf('const SHOW_MANIFEST='),to=html.indexOf('function safeFilePart(',from);
assert(from>=0&&to>from,'Cannot access production assembler');
const ctx=vm.createContext({});
vm.runInContext(html.slice(from,to)+';globalThis.fod={expandIssues,canonicalIssueList,assembleScene};',ctx);
const {expandIssues,canonicalIssueList,assembleScene}=ctx.fod;
const shows=json('data/shows.json'),f=shows.filter(s=>s.seriesId==='forces-of-darkness-llc');
assert.equal(f.length,1,'One top-level series entry only');
const parent=f[0];
assert.equal(parent.id,'forces-of-darkness-llc');
assert.equal(parent.issues?.length,8,'Eight nested issue definitions required');
assert.equal(parent.scenesFiles.length,8,'Eight inventory sources required');
const choices=Array.from(canonicalIssueList(Array.from(shows.flatMap(expandIssues)))).filter(s=>s.seriesId==='forces-of-darkness-llc');
assert.equal(choices.length,8,'One series / eight separately selectable issue choices');
const originIds=new Set(),titles=new Set(),ids=new Set();
const shelfNames=['characters','settings','regions','factions','dialogue','direction'];
const base='data/shows/forces-of-darkness-llc/';
let total=0,historicTitleAdaptations=0,newCandidates=0,dialogue=0;
for(let n=1;n<=8;n++){
 const issue=choices.find(s=>s.issueLabel==='Issue '+n);
 assert(issue,'Missing issue '+n);
 assert.equal(issue.issueId,'forces-of-darkness-llc-v'+String(n).padStart(2,'0'));
 assert.equal(issue.scenesFiles?.length,1,'Issue must load one specific source');
 const filename='strips_v'+String(n).padStart(2,'0')+'.json';
 assert.equal(issue.scenesFiles[0],filename);
 const pages=json(base+filename);
 assert.equal(pages.length,25,'Every issue contains 25 independent strips');
 const settings=new Set(),cast=new Set();
 const shelf={__show:issue};for(const name of shelfNames)shelf[name+'.json']=json(base+name+'.json');
 for(let i=0;i<pages.length;i++){
  const page=pages[i];
  assert.equal(page.id,'FOD_V'+String(n).padStart(2,'0')+'_S'+String(i+1).padStart(2,'0'));
  assert.equal(page.issue,n);assert.equal(page.page,i+1);
  assert(!ids.has(page.id),'Duplicate recipe ID '+page.id);ids.add(page.id);
  const title=page.title.toLowerCase().trim();assert(!titles.has(title),'Duplicate joke title '+title);titles.add(title);
  settings.add(page.setting);page.characters.forEach(c=>cast.add(c));
  assert(page.characters.length>0&&page.characters.every(c=>shelf['characters.json'][c]),'Unknown cast '+page.id);
  assert(shelf['settings.json'][page.setting],'Unknown setting '+page.id);
  assert.equal(page.panelPlan?.length,3,'Three panels required '+page.id);
  assert(page.dialogueInline?.length>=3,'Insufficient dialogue '+page.id);
  const refs=page.panelPlan.flatMap(p=>p.dialogueIndices||[]);
  assert.equal(refs.length,page.dialogueInline.length,'Unassigned balloon '+page.id);
  assert.equal(new Set(refs).size,refs.length,'Duplicate dialogue mapping '+page.id);
  for(let k=0;k<refs.length;k++)assert(refs.includes(k),'Unmapped dialogue '+page.id+': '+k);
  assert.equal(page.status,'selected-draft');
  if(page.originStripNumber){assert(!originIds.has(page.originStripNumber),'Duplicate historic origin '+page.originStripNumber);originIds.add(page.originStripNumber)}
  if(n>=3){assert.equal(page.editorialStatus,'sharpened-unapproved');if(page.sourceStatus==='historical-title-only-new-dialogue'){historicTitleAdaptations++;assert(Number.isInteger(page.originStripNumber))}else{assert.equal(page.sourceStatus,'new-series-premise-candidate');assert.equal(page.originStripNumber,undefined);newCandidates++}}
  const txt=assembleScene(page,shelf,i);
  assert(txt.includes(page.id),'Assembler lost ID '+page.id);
  assert(txt.includes('[PANEL PLAN]')&&txt.includes('[DIALOGUE]'),'Assembler lost story sections '+page.id);
  for(const panel of page.panelPlan)assert(txt.includes(panel.action),'Assembler lost visual action '+page.id);
  for(const d of page.dialogueInline){assert(txt.includes(d.text),'Assembler lost dialogue '+page.id);dialogue++}
  total++;
 }
 if(n>=3){assert(settings.size>=8,'Too few settings Issue '+n);assert(cast.size>=10,'Too few characters Issue '+n)}
}
assert.equal(total,200);assert.equal(historicTitleAdaptations,22);assert.equal(newCandidates,128);
const ledger=json(base+'historical_intake_275.json');
assert.equal(ledger.originals.length,275);
assert.equal(ledger.counts.threePanelScripts,200);
console.log('PASS: ONE Forces of Darkness series, EIGHT issues, 200 uniquely assembled strips, '+dialogue+' retained dialogue lines; 22 historic-title adaptations, 128 clearly marked new candidates.');
