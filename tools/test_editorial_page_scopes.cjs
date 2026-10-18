#!/usr/bin/env node
'use strict';
// Verify editorial page-scoped chef profiles against complete issue story assets.
// This test reads the active RexPrompt assembler, compressed Stardust source pages,
// current story/dialogue overlays, and the committed per-page assembly profiles.
const fs=require('node:fs');
const vm=require('node:vm');
const zlib=require('node:zlib');
const path=require('node:path');
const assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const load=p=>JSON.parse(read(p));
const html=read('index.html');
const start=html.indexOf('const SHOW_MANIFEST='),end=html.indexOf('function safeFilePart(',start);
assert(start>=0&&end>start,'Assembler source not found');
const vmContext=vm.createContext({});
vm.runInContext(html.slice(start,end)+';globalThis.testAssembler=assembleScene;',vmContext);
const assemble=vmContext.testAssembler;
const shows=load('data/shows.json');
function showById(id){const show=shows.find(s=>s.id===id);assert(show,'Missing show '+id);return show}
function store(show){
  const data={__show:show};
  for(const f of ['characters','dialogue','settings','regions','factions','direction'])
    data[f+'.json']=load(show.basePath+'/'+f+'.json');
  return data;
}
function section(str,name){
  const marker='\n['+name+']\n',idx=str.indexOf(marker);
  if(idx<0)return null;
  const after=str.slice(idx+marker.length),next=after.search(/\n\[[A-Z][A-Z0-9 /_&-]*\]\n/);
  return (next<0?after:after.slice(0,next)).trim();
}
function checkStory(page,text){
  assert(section(text,'PANEL PLAN')!==null,page.id+' lost panel plan');
  assert(section(text,'DIALOGUE')!==null,page.id+' lost dialogue');
  for(const line of page.dialogueInline||[])
    assert(text.includes(line.text),page.id+' omitted dialogue '+line.text);
  for(const panel of page.panelPlan||[]){
    const p=typeof panel==='string'?panel:panel.text||panel.name||panel.summary||JSON.stringify(panel);
    assert(text.includes(p),page.id+' omitted panel direction');
  }
  if(page.continuityFrom)assert(section(text,'CONTINUITY')!==null,page.id+' lost continuity');
}
// Vikings Issue 2: repeated first-night apartment condition belongs on select
// establishing/return/condition pages, not every close-up or the bodega/hallway.
const vikShow=showById('vikings-2026-s1-e02');
const vikStore=store(vikShow);
const vikPages=load('data/shows/vikings-2026-s1/pages_i02.json');
assert.equal(vikPages.length,22,'Unexpected Vikings issue count');
const reducedIds=['VIK_S1E02_P05','VIK_S1E02_P06','VIK_S1E02_P09',
  'VIK_S1E02_P10','VIK_S1E02_P12','VIK_S1E02_P13',
  'VIK_S1E02_P14','VIK_S1E02_P15','VIK_S1E02_P20','VIK_S1E02_P21'];
for(let i=0;i<vikPages.length;i++){
  const page=vikPages[i],chef=assemble(page,vikStore,i);
  checkStory(page,chef);
  if(reducedIds.includes(page.id)){
    assert(page.promptSuppress?.includes('direction'),'Missing stored Vikings suppression '+page.id);
    assert(page.directionInline?.[0]?.text?.startsWith('LANDFALL VISUAL STATE:'),
      'Suppressed unique direction on '+page.id);
    assert(!chef.includes('LANDFALL VISUAL STATE:'),'Apartment boilerplate leaked on '+page.id);
    const before=assemble({...page,promptSuppress:(page.promptSuppress||[]).filter(x=>x!=='direction')},vikStore,i);
    assert.equal(section(before,'DIALOGUE'),section(chef,'DIALOGUE'));
    assert.equal(section(before,'PANEL PLAN'),section(chef,'PANEL PLAN'));
  }
}
for(const id of ['VIK_S1E02_P03','VIK_S1E02_P04','VIK_S1E02_P08',
                 'VIK_S1E02_P11','VIK_S1E02_P17','VIK_S1E02_P19','VIK_S1E02_P22']){
  const p=vikPages.find(x=>x.id===id);
  assert(assemble(p,vikStore,0).includes('LANDFALL VISUAL STATE:'),'Lost establishing/state reminder '+id);
}
const bodega=vikPages.find(x=>x.id==='VIK_S1E02_P07');
assert(!assemble(bodega,vikStore,0).includes('LANDFALL VISUAL STATE:'));
assert.equal(bodega.dialogueInline.length,18,'Bodega writing modified during assembly pass');
// Stardust Issue 2: preserve the compressed writing exactly and attach a
// separate profile overlay after the current story overlay.
const sdsShow=showById('stardust-station-e02');
const sdsStore=store(sdsShow);
const overlays=sdsShow.sceneOverlays;
const profileFile='editorial/page_assembly_profiles_e02.json';
const profileIdx=overlays.findIndex(x=>x.file===profileFile);
const storyIdx=overlays.findIndex(x=>x.file==='editorial/pages_e02_p02_story_thread.json');
assert(profileIdx>storyIdx&&overlays[profileIdx].mergeById&&overlays[profileIdx].strict,
  'Page assembly profiles must be a strict merge after authored story corrections');
let scenes=overlays.filter(x=>x.encoding==='gzip-base64').flatMap(x=>{
  const body=read(sdsShow.basePath+'/'+x.file).trim();
  return JSON.parse(zlib.gunzipSync(Buffer.from(body,'base64')).toString('utf8'));
});
assert.equal(scenes.length,22,'Unexpected Stardust interior count');
const story=load(sdsShow.basePath+'/editorial/pages_e02_p02_story_thread.json');
const patches=new Map(story.map(x=>[x.id,x]));
scenes=scenes.map(x=>({...x,...(patches.get(x.id)||{})}));
const profiles=load(sdsShow.basePath+'/'+profileFile);
assert.equal(profiles.length,22,'Every Stardust interior needs an editorial profile');
const profById=new Map(profiles.map(x=>[x.id,x]));
assert.equal(profById.size,22,'Duplicate Stardust editorial profile');
assert([...profById.keys()].every(id=>scenes.some(p=>p.id===id)),'Orphan Stardust profile');
assert(scenes.every(p=>profById.has(p.id)),'Unprofiled Stardust interior');
const dialogue=load(sdsShow.basePath+'/editorial/dialogue_cleanup_e02.json');
const dialogueById=new Map(dialogue.map(x=>[x.id,x]));
let saved=0;
for(let i=0;i<scenes.length;i++){
  const p=scenes[i],d=dialogueById.get(p.id);
  const storyPage={...p,...(d?{dialogueInline:d.dialogueInline||d.sceneDialogue}: {})};
  const page={...storyPage,...profById.get(p.id)};
  assert.equal(page.promptCharacterMode,'cast','Wrong Stardust cast scope '+page.id);
  const before=assemble(storyPage,sdsStore,i),after=assemble(page,sdsStore,i);
  checkStory(page,after);
  assert.equal(section(before,'PANEL PLAN'),section(after,'PANEL PLAN'),'Panel changed '+page.id);
  assert.equal(section(before,'DIALOGUE'),section(after,'DIALOGUE'),'Dialogue changed '+page.id);
  assert.equal(section(before,'CONTINUITY'),section(after,'CONTINUITY'),'Continuity changed '+page.id);
  assert(after.includes('[CAST]')&&!after.includes('[CHARACTERS]'),'Expected concise cast '+page.id);
  const n=Number(page.id.match(/P(\d+)$/)?.[1]);
  if(n===1||n===20){
    assert(!page.promptSettingMode,'Unexpected location compaction on establishing/return page '+page.id);
    assert(after.includes(sdsStore['settings.json'][page.setting].text),'Missing location visual description '+page.id);
  }else{
    assert.equal(page.promptSettingMode,'label','Missing short recurring-location reference '+page.id);
    assert(after.includes(sdsStore['settings.json'][page.setting].name),'Missing setting label '+page.id);
    assert(!after.includes(sdsStore['settings.json'][page.setting].text),'Expanded location still present '+page.id);
  }
  if(page.promptSuppress?.includes('summary'))assert(!after.includes(page.summary),'Redundant summary still included '+page.id);
  else assert(after.includes(page.summary),'Necessary dramatic context missing '+page.id);
  saved+=before.length-after.length;
}
assert(saved>5000,'Expected a meaningful reduction in repeated reference material');
console.log('PASS Vikings Issue 2: 22 pages, 10 targeted new suppressed directions, no lost story');
console.log('PASS Stardust Issue 2: 22 pages, 22 editorial profiles, '+saved+' repeated prompt characters removed, no lost story');
