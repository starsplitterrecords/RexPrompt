(()=>{
'use strict';

const SECTIONS=[
  {id:'setting',label:'Setting',header:'SETTING'},
  {id:'region',label:'Region',header:'REGION'},
  {id:'factions',label:'Factions',header:'FACTIONS'},
  {id:'characters',label:'Characters',header:'CHARACTERS'},
  {id:'continuity',label:'Continuity',header:'CONTINUITY'},
  {id:'direction',label:'Direction',header:'DIRECTION'}
];
const VALID=new Set(SECTIONS.map(x=>x.id));
const STORAGE_PREFIX='rexprompt.promptSuppress::';
const defaultsByKey=new Map();
let panel=null;
let syncQueued=false;

function normalizeList(value){
  if(!Array.isArray(value))return [];
  return [...new Set(value.map(x=>String(x||'').trim().toLowerCase()).filter(x=>VALID.has(x)))];
}
function contextKey(seriesId,issueId,recipeId){
  return [seriesId||'series',issueId||'issue',recipeId||'recipe'].join('::');
}
function sceneContext(scene,targetStore){
  const show=targetStore?.__show||{};
  const seriesId=show.seriesId||String(show.seriesName||show.name||'series').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
  const issueId=show.issueId||show.id||show.issueLabel||'issue';
  const recipeId=scene?.id||'recipe';
  return {seriesId,issueId,recipeId,key:contextKey(seriesId,issueId,recipeId)};
}
function domContext(){
  const showSel=document.getElementById('showSel'),issueSel=document.getElementById('issueSel'),sceneSel=document.getElementById('sceneSel');
  const option=sceneSel?.options?.[sceneSel.selectedIndex];
  if(!showSel||!issueSel||!option)return null;
  const base=option.dataset.recipeId||option.dataset.visualBaseLabel||option.textContent||'';
  const recipeId=String(base).split(' - ')[0].replace(/\s+\[(?:DRAFT|CANON)\].*$/,'').trim();
  return {seriesId:showSel.value,issueId:issueSel.value,recipeId,key:contextKey(showSel.value,issueSel.value,recipeId)};
}
function readOverride(key){
  const raw=localStorage.getItem(STORAGE_PREFIX+key);
  if(raw===null)return null;
  try{return normalizeList(JSON.parse(raw))}catch{localStorage.removeItem(STORAGE_PREFIX+key);return null}
}
function effectiveList(key){
  const override=readOverride(key);
  return override===null?(defaultsByKey.get(key)||[]):override;
}
function writeOverride(key,list){localStorage.setItem(STORAGE_PREFIX+key,JSON.stringify(normalizeList(list)))}
function clearOverride(key){localStorage.removeItem(STORAGE_PREFIX+key)}
function escapeRe(value){return String(value).replace(/[.*+?^${}()|[\]\\]/g,'\\$&')}
function stripSection(text,header){
  const re=new RegExp('(?:^|\\n)\\['+escapeRe(header)+'\\]\\n[\\s\\S]*?(?=\\n\\[[A-Z][A-Z0-9 /_&-]*\\]\\n|$)','g');
  return String(text||'').replace(re,'').replace(/\n{3,}/g,'\n\n').trim();
}
function queueSync(){
  if(syncQueued)return;syncQueued=true;
  setTimeout(()=>{syncQueued=false;syncUi()},0);
}
function installAssemblerWrapper(){
  if(window.__rexPromptPromptSuppressWrapped)return true;
  const base=window.assembleScene;
  if(typeof base!=='function')return false;
  window.assembleScene=function(scene,targetStore,index,options){
    const ctx=sceneContext(scene,targetStore);
    defaultsByKey.set(ctx.key,normalizeList(scene?.promptSuppress));
    let text=base.call(this,scene,targetStore,index,options);
    const suppress=effectiveList(ctx.key);
    for(const id of suppress){
      const section=SECTIONS.find(x=>x.id===id);
      if(section)text=stripSection(text,section.header);
    }
    queueSync();
    return text;
  };
  window.__rexPromptPromptSuppressWrapped=true;
  return true;
}
function injectStyles(){
  if(document.getElementById('promptSuppressStyles'))return;
  const style=document.createElement('style');style.id='promptSuppressStyles';
  style.textContent=`.prompt-suppress{margin:8px 0 14px;padding:10px 12px;border:1px solid var(--border);border-radius:6px;background:var(--surface-soft)}.prompt-suppress-title{font-size:.88rem;font-weight:700;margin-bottom:7px}.prompt-suppress-options{display:flex;flex-wrap:wrap;gap:7px 14px}.prompt-suppress-options label{display:inline-flex;align-items:center;gap:5px;font-size:.84rem}.prompt-suppress-options input{margin:0}.prompt-suppress-foot{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-top:8px;color:var(--muted);font-size:.76rem}.prompt-suppress-reset{font-size:.76rem;padding:5px 8px;margin:0}`;
  document.head.appendChild(style);
}
function createPanel(){
  if(panel)return panel;
  const sceneSel=document.getElementById('sceneSel');if(!sceneSel)return null;
  injectStyles();
  const el=document.createElement('div');el.id='promptSuppressPanel';el.className='prompt-suppress';
  el.innerHTML='<div class="prompt-suppress-title">Suppress from assembled recipe</div><div class="prompt-suppress-options">'+SECTIONS.map(x=>'<label><input type="checkbox" data-prompt-suppress="'+x.id+'"> '+x.label+'</label>').join('')+'</div><div class="prompt-suppress-foot"><button type="button" class="prompt-suppress-reset">Reset page</button><span>Saved per page in this browser. Reset returns to any page-data promptSuppress default.</span></div>';
  const block=sceneSel.closest('.block')||sceneSel.parentElement;block.insertAdjacentElement('afterend',el);
  el.querySelectorAll('[data-prompt-suppress]').forEach(input=>input.addEventListener('change',()=>{
    const ctx=domContext();if(!ctx)return;
    const selected=[...el.querySelectorAll('[data-prompt-suppress]:checked')].map(x=>x.dataset.promptSuppress);
    writeOverride(ctx.key,selected);
    document.getElementById('buildBtn')?.click();
    syncUi();
  }));
  el.querySelector('.prompt-suppress-reset').addEventListener('click',()=>{
    const ctx=domContext();if(!ctx)return;
    clearOverride(ctx.key);document.getElementById('buildBtn')?.click();syncUi();
  });
  panel=el;return el;
}
function syncUi(){
  const el=createPanel(),ctx=domContext();if(!el||!ctx)return;
  const active=new Set(effectiveList(ctx.key));
  el.querySelectorAll('[data-prompt-suppress]').forEach(input=>{input.checked=active.has(input.dataset.promptSuppress)});
  const reset=el.querySelector('.prompt-suppress-reset');if(reset)reset.disabled=readOverride(ctx.key)===null;
}
function installUiListeners(){
  const ids=['showSel','issueSel','sceneSel'];
  ids.forEach(id=>document.getElementById(id)?.addEventListener('change',()=>setTimeout(syncUi,0)));
  const sceneSel=document.getElementById('sceneSel');
  if(sceneSel)new MutationObserver(()=>setTimeout(syncUi,0)).observe(sceneSel,{childList:true,subtree:true});
}
function start(){
  const tryWrap=()=>{if(!installAssemblerWrapper())setTimeout(tryWrap,25);else{createPanel();installUiListeners();syncUi();setTimeout(()=>document.getElementById('buildBtn')?.click(),50)}};
  tryWrap();
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});else start();
})();
