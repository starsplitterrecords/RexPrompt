#!/usr/bin/env node
'use strict';
// Rex Fleet ingredient scoping: check effective assembler output across every
// released, approved, and unreleased page without freezing creative writing.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const zlib=require('node:zlib');
const vm=require('node:vm');
const root=path.resolve(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const json=p=>JSON.parse(read(p));
const manifest=json('data/shows.json');
const base='data/shows/rex-fleet-s1';
const html=read('index.html');
const start=html.indexOf('const SHOW_MANIFEST='),stop=html.indexOf('function safeFilePart(',start);
assert(start>=0&&stop>start,'Live assembler not found');
const scope={};
vm.runInNewContext(html.slice(start,stop)+';globalThis.scoping={assembleScene,pageAssembly,visibleCharacterHandles};',scope);
const {assembleScene:assemble,pageAssembly,visibleCharacterHandles}=scope.scoping;
const catalogs={};
for(const name of ['blocking','characters','dialogue','direction','factions','lighting','mood','negatives','regions','settings']){
  catalogs[name+'.json']=json(base+'/'+name+'.json');
}
function loadOverlay(item){
  const filename=base+'/'+item.file;
  const incoming=item.encoding==='gzip-base64'
    ?JSON.parse(zlib.gunzipSync(Buffer.from(read(filename).replace(/\s+/g,''),'base64')).toString('utf8'))
    :json(filename);
  assert(Array.isArray(incoming),'Malformed overlay '+filename);
  if(item.includeIds)return incoming.filter(p=>item.includeIds.includes(p.id));
  if(item.excludeIds)return incoming.filter(p=>!item.excludeIds.includes(p.id));
  return incoming;
}
function combine(pages,item){
  const incoming=loadOverlay(item);
  if(!item.mergeById)return pages.concat(incoming);
  const update=new Map(incoming.map(x=>[x.id,x])),seen=new Set();
  const merged=pages.map(x=>{
    const change=update.get(x.id);
    if(!change)return x;
    seen.add(x.id);
    return {...x,...change};
  });
  for(const obj of incoming){
    if(!seen.has(obj.id)){
      if(item.strict)throw new Error('Missing strict merge target: '+obj.id);
      merged.push(obj);
    }
  }
  return merged;
}
function section(text,name){
  const marker='\n['+name+']';
  const start=text.indexOf(marker);
  if(start<0)return null;
  const after=text.slice(start+marker.length).trimStart();
  const idx=after.search(/\n\[[A-Z][A-Z0-9 /&_-]*\]\n/);
  return (idx<0?after:after.slice(0,idx)).trim();
}
let total=0,stories=0,reductions=0,cast=0,full=0,setting=0,region=0,factions=0,unmodifiedSpecial=0;
const report=[];
for(let n=1;n<=12;n++){
  const id='rex-fleet-i'+String(n).padStart(2,'0');
  const show=manifest.find(s=>s.id===id);
  assert(show,'Missing issue '+id);
  const marker='editorial/page_assembly_scope_i'+String(n).padStart(2,'0')+'.json';
  const idx=show.sceneOverlays.findIndex(ov=>ov.file===marker);
  assert.equal(idx,show.sceneOverlays.length-1,'Page-scoped data must be final strict overlay for '+id);
  assert(show.sceneOverlays[idx].mergeById&&show.sceneOverlays[idx].strict,'Strict merge-by-ID required');
  const profile=loadOverlay(show.sceneOverlays[idx]);
  let pages=json(base+'/'+show.scenesFile);
  for(const ov of show.sceneOverlays.slice(0,-1))pages=combine(pages,ov);
  const profiles=new Map(profile.map(p=>[p.id,p]));
  assert.equal(profiles.size,profile.length,'Repeated scope id in '+id);
  const interiors=pages.filter(p=>/^RF_I\d\d_P\d\d$/.test(p.id));
  assert.equal(profile.length,interiors.length,'All and only interior pages need explicit profiles for '+id);
  assert(interiors.every(p=>profiles.has(p.id)),'Unscoped story page in '+id);
  let issueSaved=0;
  const data={...catalogs,__show:show};
  for(let i=0;i<pages.length;i++){
    const original=pages[i],edit=profiles.get(original.id);
    const post=edit?{...original,...edit}:original;
    const before=assemble(original,data,i),after=assemble(post,data,i);
    total++;
    if(!edit){
      unmodifiedSpecial++;
      assert.equal(after,before,'Cover/editorial changed: '+original.id);
      continue;
    }
    stories++;
    assert.deepEqual(Object.keys(edit).sort(),
      edit.promptCharacterMode?['id','promptCharacterMode','promptSuppress','promptVisibleCastOnly']:['id','promptSuppress','promptVisibleCastOnly'],
      'Scope overlay must contain assembly fields only');
    assert(Array.isArray(edit.promptSuppress),'Missing explicit suppression list '+post.id);
    assert.equal(edit.promptVisibleCastOnly,true,'Interior page must enable visible-only references '+post.id);
    assert(new Set(edit.promptSuppress).size===edit.promptSuppress.length,'Repeated suppression '+post.id);
    const prior=original.promptSuppress||[];
    for(const key of prior)assert(edit.promptSuppress.includes(key),'Prior approved suppression lost '+post.id+': '+key);
    if(original.promptCharacterMode)assert.equal(edit.promptCharacterMode,original.promptCharacterMode,'Prior approved character detail scope changed '+post.id);
    for(const key of ['panelPlan','dialogueInline','dialog','continuityFrom','pageLayout','summary','settingText','setting','regionText','region','factions','charactersInline','directionInline','status','issue','page'])
      assert.deepEqual(post[key],original[key],'Source ingredient mutated: '+post.id+' '+key);
    pageAssembly(post,show); // also reject illegitimate setting/section suppression
    for(const name of ['PANEL PLAN','CONTINUITY','PAGE COMPOSITION','DIRECTION','SETTING']){
      assert.equal(section(after,name),section(before,name),'Protected or intentionally retained section altered: '+post.id+' '+name);
    }
    assert(after.includes(show.generationLine),'Production brief removed on '+post.id);
    for(const line of post.dialogueInline||[])assert(after.includes('"'+line.text+'"'),'Lost scripted dialogue on '+post.id);
    assert.equal(!!section(after,'DIALOGUE'),!!section(before,'DIALOGUE'),'Dialogue section missing on '+post.id);
    const references=after.split('\n').filter(x=>/^@starsplit\.[A-Za-z0-9._-]+$/.test(x));
    const visible=Array.from(visibleCharacterHandles(post,catalogs['characters.json']));
    assert.deepEqual(references,visible,'Incorrect visible character reference handles '+post.id);
    assert(section(after,'CAST')===null&&section(after,'CHARACTERS')===null,'Duplicate cast prose on '+post.id);
    if(original.summary)assert(after.includes(original.summary.trim()),'Story summary lost '+post.id);
    if(edit.promptCharacterMode==='cast'){
      cast++;
      assert(section(after,'CAST')===null,'Duplicate cast names emitted '+post.id);
    }else if(edit.promptCharacterMode==='full'){
      full++;
      assert(section(after,'CHARACTERS')===null,'Full visual character descriptions duplicated '+post.id);
    }
    if(edit.promptSuppress.includes('settingContinuity')){
      setting++;
      assert(section(after,'SETTING CONTINUITY')===null,'Setting shelf leaked '+post.id);
    }
    if(edit.promptSuppress.includes('region')){
      region++;
      assert(section(after,'REGION')===null,'Region shelf leaked '+post.id);
    }
    if(edit.promptSuppress.includes('factions')){
      factions++;
      assert(section(after,'FACTIONS')===null,'Faction shelf leaked '+post.id);
    }
    issueSaved+=before.length-after.length;
  }
  assert(issueSaved>0,'No effective decluttering in '+id);
  reductions+=issueSaved;
  report.push({issue:n,story:interiors.length,savedCharacters:issueSaved});
}
assert(stories>250,'Expected full mainline scope rollout');
assert(unmodifiedSpecial===35,'Cover/editorial pages unexpectedly modified');
assert(reductions>15000,'Scope changes too small to be useful');
console.log('PASS Rex Fleet page-scoped recipe sanitation: '+total+' assembled pages; '+stories+' interiors, '+unmodifiedSpecial+' unchanged covers/editorials');
console.log('PASS Unchanged dialogue, panels, continuities, layout, summary, setting and production line');
console.log('PASS '+cast+' previously cast-scoped pages, '+full+' previously full-identity pages now reduced to visible-only handles; '+setting+' setting-continuity suppressions, '+region+' repeated region suppressions, '+factions+' repeated faction suppressions');
console.log('PASS '+reductions+' repeated characters omitted across issue recipes');
for(const row of report)console.log('Issue '+String(row.issue).padStart(2,'0')+': '+row.story+' interiors, '+row.savedCharacters+' characters trimmed');
