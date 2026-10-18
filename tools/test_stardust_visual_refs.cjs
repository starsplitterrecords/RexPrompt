#!/usr/bin/env node
'use strict';
// Ensure the reference handles sent to the image model describe visible cast,
// never merely dialogue participants or a blanket series roster.
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
assert(start>=0&&end>start);
const ctx=vm.createContext({});
vm.runInContext(html.slice(start,end)+';globalThis.exposed={assembleScene,visibleCharacterHandles};',ctx);
const {assembleScene:assemble,visibleCharacterHandles:visual}=ctx.exposed;
const allShows=load('data/shows.json');
const all=allShows.filter(s=>/^stardust-station(?:-e\d+)?$/.test(s.id));
assert.equal(all.length,10);
const characters=load('data/shows/stardust-station/characters.json');
const store={};
for(const f of ['characters','settings','regions','factions','direction','dialogue'])
  store[f+'.json']=load('data/shows/stardust-station/'+f+'.json');
function normalize(data){if(Array.isArray(data))return data;if(Array.isArray(data?.pages))return data.pages;return Object.entries(data||{}).map(([id,v])=>({id,...v}))}
function readOverlay(base,ov){const file=read(base+'/'+ov.file);return normalize(ov.encoding==='gzip-base64'
  ?JSON.parse(zlib.gunzipSync(Buffer.from(file.trim(),'base64')).toString('utf8'))
  :JSON.parse(file))}
function merge(pages,incoming){const updates=new Map(incoming.map(x=>[x.id,x]));const ids=new Set(pages.map(x=>x.id));return pages.map(x=>({...x,...(updates.get(x.id)||{})})).concat(incoming.filter(x=>!ids.has(x.id)))}
function loadIssue(show){
  const base=show.basePath;
  let pages=normalize(load(base+'/'+show.scenesFile));
  for(const ov of show.sceneOverlays||[]){
    const incoming=readOverlay(base,ov);
    if(ov.mergeById)pages=merge(pages,incoming);
    else if(ov.afterId){const i=pages.findIndex(p=>p.id===ov.afterId);pages.splice(i<0?pages.length:i+1,0,...incoming)}
    else pages.push(...incoming);
  }
  for(const ov of show.dialogueOverlays||[]){
    const changes=new Map(readOverlay(base,ov).map(x=>[x.id,x]));
    pages=pages.map(p=>{const q=changes.get(p.id);return q?{...p,dialogueInline:q.dialogueInline||q.sceneDialogue||p.dialogueInline}:p});
  }
  return pages;
}
function actualRefs(prompt){return prompt.split('\n').filter(line=>/^@sds\.[A-Za-z][A-Za-z0-9_-]*$/.test(line))}
const count={pages:0,characters:0,factionSectionsEliminated:0,offscreenProtected:0};
let curatedPages=0,curatedExcluded=0;
for(const ep of ['04','05','06','07','08','09']){
  const suffix='editorial/visual_cast_e'+ep+'.json';
  const show=allShows.find(x=>x.id==='stardust-station-e'+ep);
  const registration=show.sceneOverlays.filter(x=>x.file===suffix);
  assert.equal(registration.length,1,'Missing unique visual-cast overlay E'+ep);
  assert.equal(registration[0].mergeById,true);
  assert.equal(registration[0].strict,true);
  const authored=load('data/shows/stardust-station/pages_e'+ep+'.json');
  const patches=load('data/shows/stardust-station/'+suffix);
  for(const patch of patches){
    assert.deepEqual(Object.keys(patch).sort(),['id','promptVisibleCharacters']);
    const page=authored.find(p=>p.id===patch.id);
    assert(page,'Visual-cast overlay references unknown page '+patch.id);
    assert(patch.promptVisibleCharacters.length>0,'Unexpected empty frame cast '+patch.id);
    assert(patch.promptVisibleCharacters.every(x=>page.characters.includes(x)),
      'Visual-cast overlay invented a character '+patch.id);
    assert(patch.promptVisibleCharacters.length<page.characters.length,
      'Visual-cast overlay must actually omit an unpictured role '+patch.id);
    curatedPages++;curatedExcluded+=page.characters.length-patch.promptVisibleCharacters.length;
  }
}
assert.equal(curatedPages,13,'Missing reviewed visible-cast overrides');
assert.equal(curatedExcluded,15,'Unexpected change to excluded off-frame visual references');
for(const show of all){
  assert.equal(show.promptVisibleCastOnly,true,show.id+' does not opt in to precise references');
  assert.equal(show.omitRoutineFactions,true,show.id+' still includes routine factions');
  store.__show=show;
  const pages=loadIssue(show);
  const interior=pages.filter(p=>/^SDS_S1E\d{2}_P\d{2}$/.test(p.id||''));
  assert(interior.length>=20,show.id+' interior pages missing: '+interior.length);
  for(let i=0;i<pages.length;i++){
    const page=pages[i],text=assemble(page,store,i);
    assert(!text.includes('\n[CAST]\n')&&!text.includes('\n[CHARACTERS]\n'),'Duplicate cast roster: '+page.id);
    assert(!text.includes('\n[FACTIONS]\n'),'Routine faction emitted: '+page.id);
    const refs=actualRefs(text),expected=Array.from(visual(page,characters));
    assert.deepEqual(refs,expected,'Wrong visible character references on '+page.id);
    assert.equal((text.match(/@sds\.[A-Za-z][A-Za-z0-9_-]*/g)||[]).length,expected.length,
      'Dialogue or another field added unexpected image references on '+page.id);
    for(const line of page.dialogueInline||[]){
      assert(text.includes('"'+line.text+'"'),'Literal dialogue text lost: '+page.id);
      if(line.handle?.startsWith('@')&&!expected.includes(line.handle)){
        assert(!text.includes(line.handle),'Offscreen speaker introduced visual reference: '+page.id);
        count.offscreenProtected++;
      }
    }
    if(interior.includes(page)){count.pages++;count.characters+=expected.length}
    if(page.factions?.length)count.factionSectionsEliminated++;
  }
}
const show=all[3],page=loadIssue(show).find(p=>p.id==='SDS_S1E04_P01');
assert(page);
store.__show=show;
const offPanel={...page,promptVisibleCharacters:['SDS_Zib'],dialogueInline:[
  ...page.dialogueInline,
  {handle:'@sds.Astra',speaker:'Astra Vega',text:'A test line from off-panel',subtext:'Off-panel'}
]};
const result=assemble(offPanel,store,0);
assert.deepEqual(actualRefs(result),['@sds.Zib']);
assert(result.includes('Astra Vega says "A test line from off-panel"'),'Speaker must remain intelligible');
assert(!result.includes('@sds.Astra'),'Off-panel character must not become reference');
assert.throws(()=>assemble({...page,promptVisibleCharacters:['SDS_Unknown']},store,0),/Unknown visible character/);
assert.throws(()=>assemble({...page,promptVisibleCharacters:'SDS_Zib'},store,0),/must be an array/);
const factionText=assemble({...page,factions:['SDS_StarTrust'],promptIncludeFactions:true},store,0);
assert(factionText.includes('[FACTIONS]'),'A relevant faction may be explicitly requested');
const old={...show,promptVisibleCastOnly:false,omitRoutineFactions:false};
store.__show=old;
const oldPrompt=assemble(page,store,0);
assert(oldPrompt.includes('[CAST]')||oldPrompt.includes('[CHARACTERS]'),'Test must prove legacy recipe exists');
console.log('PASS: Stardust '+all.length+' issues, '+count.pages+' interior pages, '+count.characters+
  ' relevant image handles, '+count.factionSectionsEliminated+' redundant faction sections suppressed, '+count.offscreenProtected+' dialogue-only speakers excluded; '+curatedExcluded+' curated exclusions across '+curatedPages+' pages');
console.log('PASS: explicit art-cast override, off-panel speaker, faction opt-in, and legacy non-Stardust compatibility');
