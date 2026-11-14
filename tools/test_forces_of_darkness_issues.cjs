#!/usr/bin/env node
'use strict';
// Validate one Forces of Darkness series and two distinct issue selectors against the live assembler.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const json=p=>JSON.parse(read(p));
const html=read('index.html'),from=html.indexOf('const SHOW_MANIFEST='),to=html.indexOf('function safeFilePart(',from);
assert(from>=0&&to>from,'Live browser assembler not found');
const ctx=vm.createContext({});
vm.runInContext(html.slice(from,to)+';globalThis.__fod={expandIssues,canonicalIssueList,assembleScene};',ctx);
const {expandIssues,canonicalIssueList,assembleScene}=ctx.__fod;
const allShows=json('data/shows.json'),fodShows=allShows.filter(s=>s.seriesId==='forces-of-darkness-llc');
assert.equal(fodShows.length,1,'Forces of Darkness must be ONE top-level series/show entry');
const fod=fodShows[0];
assert.equal(fod.id,'forces-of-darkness-llc');
assert.equal(fod.name,'The Forces of Darkness, LLC.');
assert.equal(fod.issues?.length,2,'Expected two nested issues');
const issueChoices=Array.from(canonicalIssueList(Array.from(allShows.flatMap(expandIssues)))).filter(i=>i.seriesId==='forces-of-darkness-llc');
assert.equal(issueChoices.length,2,'Issue selector must expose exactly Issue 1 and Issue 2');
assert.equal(new Set(issueChoices.map(i=>i.issueId)).size,2,'Issue IDs must be distinct');
const shelfNames=['blocking','characters','dialogue','direction','factions','lighting','mood','negatives','regions','settings'];
const sourceIDs=new Set();let assembled=0;
for(let n=1;n<=2;n++){
 const issue=issueChoices.find(x=>x.issueLabel==='Issue '+n);
 assert(issue,'Missing Issue '+n);
 assert.equal(issue.scenesFiles.length,1,'Issue '+n+' must load only its own recipe source');
 const filename='strips_v'+String(n).padStart(2,'0')+'.json';
 assert.equal(issue.scenesFiles[0],filename);
 const pages=json('data/shows/forces-of-darkness-llc/'+filename);
 assert.equal(pages.length,25,'Issue '+n+' must have 25 scripts');
 const store={__show:issue};
 for(const shelf of shelfNames)store[shelf+'.json']=json('data/shows/forces-of-darkness-llc/'+shelf+'.json');
 for(let p=0;p<pages.length;p++){
  const script=pages[p];
  assert.equal(script.issue,n,'Script assigned wrong issue: '+script.id);
  assert.equal(script.page,p+1,'Wrong issue-local strip index: '+script.id);
  assert.match(script.id,new RegExp('^FOD_V0'+n+'_S\\d{2}$'));
  assert(!sourceIDs.has(script.id),'Duplicate script ID: '+script.id);sourceIDs.add(script.id);
  assert.equal(script.panelPlan.length,3,'Not three panels: '+script.id);
  assert(Array.isArray(script.dialogueInline)&&script.dialogueInline.length,'Missing dialogue: '+script.id);
  const mapped=script.panelPlan.flatMap(x=>x.dialogueIndices||[]);
  assert.equal(mapped.length,script.dialogueInline.length,'Missing balloon assignment: '+script.id);
  assert.equal(new Set(mapped).size,script.dialogueInline.length,'Duplicate balloon assignment: '+script.id);
  const prompt=assembleScene(script,store,p);
  assert(prompt.includes(script.id),'Assembler omitted ID: '+script.id);
  assert(prompt.includes('[PANEL PLAN]'),'Missing panel plan: '+script.id);
  for(const panel of script.panelPlan)assert(prompt.includes(panel.action),'Dropped panel action: '+script.id);
  for(const line of script.dialogueInline)assert(prompt.includes(line.text),'Dropped spoken words: '+script.id);
  assembled++;
 }
}
assert.equal(assembled,50);
console.log('PASS: ONE Forces of Darkness series; two issue choices, 25 separate strips per issue, 50 full recipes assembled with panel/dialogue preservation');
