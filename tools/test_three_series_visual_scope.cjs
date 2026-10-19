#!/usr/bin/env node
'use strict';
// Full-issue visual reference regression for Shattering, Division Threshold,
// and Echoes of the Forgotten War. Tests the live browser assembler, not a mock.
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const json=p=>JSON.parse(read(p));
const html=read('index.html');
const from=html.indexOf('const SHOW_MANIFEST='),to=html.indexOf('function safeFilePart(',from);
assert(from>=0&&to>from,'Browser assembler not found');
const ctx=vm.createContext({});
vm.runInContext(html.slice(from,to)+';globalThis.testing={assembleScene,visibleCharacterHandles};',ctx);
const {assembleScene:assemble,visibleCharacterHandles:visible}=ctx.testing;
const series=new Set(['shattering','division-threshold','echoes-forgotten-war']);
const shows=json('data/shows.json').filter(s=>series.has(s.seriesId));
assert.equal(shows.length,33,'Unexpected count of targeted show configurations');
const cache=new Map();
const get=(p)=>{if(!cache.has(p))cache.set(p,json(p));return cache.get(p)};
const normalize=raw=>Array.isArray(raw)?raw:Array.isArray(raw?.pages)?raw.pages:Object.entries(raw).map(([id,scene])=>({id,...scene}));
function scenes(show){
  const base=show.basePath;
  const files=show.scenesFiles?.length?show.scenesFiles:[show.scenesFile||'scenes.json'];
  let pages=files.flatMap(f=>normalize(get(base+'/'+f)));
  for(const o of show.sceneOverlays||[]){
    const patch=normalize(get(base+'/'+o.file));
    if(o.includeIds?.length){ /* Current targeted overlays have no includeIds. */ }
    if(o.mergeById){
      const byId=new Map(patch.map(x=>[x.id,x]));
      assert.equal(byId.size,patch.length,'Duplicate overlay IDs: '+o.file);
      if(o.strict)for(const p of patch)assert(pages.some(x=>x.id===p.id),'Orphan strict page overlay '+p.id);
      pages=pages.map(p=>({...p,...(byId.get(p.id)||{})}));
      for(const p of patch)if(!pages.some(x=>x.id===p.id))pages.push(p);
    }else pages=pages.concat(patch);
  }
  for(const o of show.dialogueOverlays||[]){
    const byId=new Map(normalize(get(base+'/'+o.file)).map(p=>[p.id,p]));
    pages=pages.map(p=>{const edit=byId.get(p.id);return edit?{...p,dialogueInline:edit.dialogueInline||edit.sceneDialogue||p.dialogueInline}:p});
  }
  if(show.includeIdPattern){const re=new RegExp(show.includeIdPattern);pages=pages.filter(x=>re.test(x.id||''))}
  return pages;
}
function store(show){
  const base=show.basePath;
  const out={__show:show};
  for(const shelf of ['characters','dialogue','settings','regions','factions','direction'])
    out[shelf+'.json']=get(base+'/'+shelf+'.json');
  return out;
}
const totals={shattering:0,'division-threshold':0,'echoes-forgotten-war':0};
const factionHidden={shattering:0,'division-threshold':0};
let visibleReferences=0,lines=0,corrected=0;
const tags=text=>text.split('\n').filter(x=>/^@[A-Za-z0-9_.-]+$/.test(x));
const panelSection=text=>{
 const m=text.match(/(?:^|\n)\[PANEL PLAN\]\n([\s\S]*?)(?=\n\[[A-Z][A-Z /_-]*\]\n|$)/);
 return m?.[1]||'';
};
for(const show of shows){
 assert.equal(show.promptVisibleCastOnly,true,'Missing visible-only reference policy '+show.id);
 const cover=/cover/i.test(show.id);
 const shouldHideFactions=(show.seriesId==='shattering'&&!cover)||(show.seriesId==='division-threshold'&&!cover);
 if(shouldHideFactions)assert.equal(show.omitRoutineFactions,true,'Missing faction scoping '+show.id);
 const shelf=store(show),pages=scenes(show);
 assert(pages.length>0,'No assembled pages for '+show.id);
 for(let i=0;i<pages.length;i++){
  const page=pages[i];
  const assembled=assemble(page,shelf,i);
  const expected=Array.from(visible(page,shelf['characters.json']));
  assert.deepEqual(tags(assembled),expected,'Wrong visual reference handles for '+page.id);
  assert(!assembled.includes('\n[CAST]\n')&&!assembled.includes('\n[CHARACTERS]\n'),
    'Duplicate cast block in '+page.id);
  const factionWanted=!shouldHideFactions&&page.factions?.some(k=>shelf['factions.json'][k]);
  if(shouldHideFactions&&page.promptIncludeFactions!==true){
    assert(!assembled.includes('\n[FACTIONS]\n'),'Routine factions leaked '+page.id);
    if(page.factions?.length)factionHidden[show.seriesId]++;
  }
  if(factionWanted)assert(assembled.includes('\n[FACTIONS]\n'),
    'Cover-specific faction language lost on '+page.id);
  // Dialogue speaker IDs are not separate visual tags; authored words never change.
  for(const d of page.dialogueInline||[]){
    assert(assembled.includes('"'+(d.text||'')+'"'),'Dialogue changed or omitted '+page.id);
    if(typeof d.handle==='string'&&d.handle.startsWith('@')){
      const resolved=Object.values(shelf['characters.json']).find(c=>c?.handle===d.handle);
      assert(resolved,'Unresolved dialogue speaker handle '+d.handle+' on '+page.id);
      assert(assembled.includes(resolved.name),'Speaker name absent '+page.id);
      assert(!assembled.includes(d.handle+' says "'),'Dialogue handle leaked as reference '+page.id);
      lines++;
    }
  }
  const legacyPage={...page};
  delete legacyPage.promptVisibleCharacters; // Legacy output had no visual-cast override contract.
  const previous=assemble(legacyPage,{...shelf,__show:{...show,promptVisibleCastOnly:false,omitRoutineFactions:false}},i);
  assert.equal(panelSection(assembled),panelSection(previous),'Scripted panel plan changed '+page.id);
  if(page.pageLayout)assert(assembled.includes('[PAGE COMPOSITION]'),'Existing layout lost '+page.id);
  totals[show.seriesId]++;
  visibleReferences+=expected.length;
  if(page.promptVisibleCharacters!==undefined)corrected++;
 }
}
assert.equal(corrected,4,'Expected four reviewed Shattering visual cast exceptions');
assert.equal(totals.shattering,150,'Shattering must cover 144 interiors plus 6 covers');
assert.equal(totals['division-threshold'],228,'Division Threshold must cover all 204 interiors plus editorial/cover pages');
assert(totals['echoes-forgotten-war']>=149,'Echoes issue content missing');
console.log('PASS: '+JSON.stringify(totals)+' pages; '+visibleReferences+
 ' precise visual references, '+JSON.stringify(factionHidden)+' repeated faction sections removed.');
console.log('PASS: '+lines+' named dialogue speakers preserved; 4 curated exclusions; cover faction visuals, panel plans, layouts and story unchanged.');
