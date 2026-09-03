(()=>{
'use strict';

const CONFIG={
  owner:'starsplitterrecords',
  repo:'RexPrompt',
  branch:'main',
  draftManifestPath:'production/drafts/manifest.json',
  releasedLinksPath:'production/released-links.json',
  visualSourcesPath:'production/visual-sources.json',
  apiBase:'https://api.github.com',
  maxUploadBytes:50*1024*1024,
  acceptedTypes:new Set(['image/jpeg','image/png','image/webp'])
};

const state={draftManifest:{schemaVersion:1,drafts:{}},releasedLinks:{schemaVersion:1,links:{}},sources:null,visionsCache:new Map(),ui:null,refreshNonce:0};

function injectStyles(){
  const style=document.createElement('style');
  style.textContent=`
  .visual-workspace{margin:8px 0 22px;padding:16px;border:1px solid var(--border);border-radius:8px;background:var(--surface-soft)}
  .visual-workspace-title{display:flex;align-items:baseline;justify-content:space-between;gap:12px;flex-wrap:wrap;margin:0 0 12px}
  .visual-workspace-title h4{margin:0;font-size:1.05rem}.visual-workspace-title span{color:var(--muted);font-size:.82rem}
  .visual-grid{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(260px,.85fr);gap:16px;align-items:start}
  .visual-card{border:1px solid var(--border);border-radius:7px;background:var(--bg);padding:12px;min-width:0}
  .visual-card.draft-card{border-width:2px}.visual-card h5{margin:0 0 8px;font-size:.92rem;letter-spacing:.02em}
  .visual-badge{display:inline-block;border:1px solid var(--border);border-radius:999px;padding:3px 8px;font-size:.72rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase;margin-bottom:8px}
  .visual-badge.draft{border-style:dashed}.visual-badge.canon{border-style:solid}
  .visual-empty{color:var(--muted);font-size:.9rem;padding:18px 4px}
  .visual-image-wrap{position:relative;background:var(--surface);border:1px solid var(--border);border-radius:5px;overflow:hidden}
  .visual-image-wrap img{display:block;width:100%;height:auto;max-height:68vh;object-fit:contain;background:var(--surface)}
  .visual-watermark{position:absolute;left:10px;bottom:10px;padding:5px 8px;border-radius:4px;background:rgba(0,0,0,.72);color:#fff;font-weight:800;font-size:.72rem;letter-spacing:.08em;pointer-events:none}
  .visual-meta{margin-top:8px;color:var(--muted);font-size:.8rem;overflow-wrap:anywhere}
  .visual-actions{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}.visual-actions button{font-size:.88rem;padding:9px 12px;margin:0}
  .visual-actions .secondary{background:var(--surface-soft)}
  .visual-upload-status{margin-top:8px;font-size:.82rem;color:var(--muted)}
  .visual-canon-list{display:grid;gap:10px}.visual-canon-item .visual-meta{margin-top:5px}
  .visual-state-note{margin-top:10px;font-size:.82rem;color:var(--muted)}
  @media(max-width:850px){.visual-grid{grid-template-columns:1fr}.visual-image-wrap img{max-height:none}}
  `;
  document.head.appendChild(style);
}

function normalizeJson(value,fallback){return value&&typeof value==='object'?value:fallback}
async function loadOptionalJson(path,fallback){
  try{
    const sep=path.includes('?')?'&':'?';
    const r=await fetch(path+sep+'v='+Date.now(),{cache:'no-store'});
    if(r.status===404)return fallback;
    if(!r.ok)throw new Error('HTTP '+r.status);
    return normalizeJson(await r.json(),fallback);
  }catch(err){
    console.warn('RexPrompt visuals: unable to load '+path,err);
    return fallback;
  }
}

function safePart(value){return String(value||'item').toLowerCase().replace(/[^a-z0-9._-]+/g,'-').replace(/^-+|-+$/g,'')||'item'}
function currentSelection(){
  const showSel=document.getElementById('showSel'),issueSel=document.getElementById('issueSel'),sceneSel=document.getElementById('sceneSel'),status=document.getElementById('status');
  if(!showSel||!issueSel||!sceneSel)return null;
  const option=sceneSel.options[sceneSel.selectedIndex];
  if(!option)return null;
  const baseLabel=option.dataset.visualBaseLabel||option.textContent||'';
  const recipeId=(option.dataset.recipeId||baseLabel.split(' - ')[0]).trim();
  const index=Number(option.value);
  return {
    seriesId:showSel.value,
    seriesName:showSel.options[showSel.selectedIndex]?.textContent||showSel.value,
    issueId:issueSel.value,
    issueLabel:issueSel.options[issueSel.selectedIndex]?.textContent||issueSel.value,
    recipeId,
    recipeIndex:Number.isFinite(index)?index:null,
    unitIsPage:/\bpages?\b/i.test(status?.textContent||''),
    recipeCount:sceneSel.options.length
  };
}
function visualKey(sel){return [sel.seriesId,sel.issueId,sel.recipeId].join('::')}
function parseIssueNumber(label){const m=String(label||'').match(/\bIssue\s*0*(\d+)\b/i);return m?Number(m[1]):null}
function withCacheBust(path,stamp){const sep=path.includes('?')?'&':'?';return path+sep+'v='+encodeURIComponent(stamp||Date.now())}
function draftImageUrl(entry){if(entry.commitSha)return 'https://raw.githubusercontent.com/'+CONFIG.owner+'/'+CONFIG.repo+'/'+entry.commitSha+'/'+entry.image;return withCacheBust(entry.image,entry.updatedAt)}

function createUi(){
  const anchor=document.getElementById('status');
  if(!anchor)return null;
  const section=document.createElement('section');
  section.id='visualWorkspace';section.className='visual-workspace';
  section.innerHTML=`
    <div class="visual-workspace-title"><h4>Production visuals</h4><span>RexPrompt drafts are mutable production data. Visions is released canon.</span></div>
    <div class="visual-grid">
      <div class="visual-card draft-card">
        <div class="visual-badge draft">Approved production draft · not released</div>
        <div id="draftBody" class="visual-empty">No approved production draft stored for this unit.</div>
        <div class="visual-actions">
          <button id="uploadDraftBtn" type="button">Upload Approved Draft</button>
          <button id="forgetGithubTokenBtn" type="button" class="secondary" hidden>Forget GitHub Token</button>
          <input id="draftFileInput" type="file" accept="image/jpeg,image/png,image/webp" hidden>
        </div>
        <div id="draftUploadStatus" class="visual-upload-status"></div>
      </div>
      <div class="visual-card canon-card">
        <div class="visual-badge canon">Released canon · StarSplitterVisions</div>
        <div id="canonBody" class="visual-empty">No released canon image mapped for this unit.</div>
      </div>
    </div>
    <div id="visualStateNote" class="visual-state-note"></div>`;
  anchor.insertAdjacentElement('afterend',section);
  const ui={
    section,
    draftBody:section.querySelector('#draftBody'),canonBody:section.querySelector('#canonBody'),uploadBtn:section.querySelector('#uploadDraftBtn'),fileInput:section.querySelector('#draftFileInput'),uploadStatus:section.querySelector('#draftUploadStatus'),forgetTokenBtn:section.querySelector('#forgetGithubTokenBtn'),stateNote:section.querySelector('#visualStateNote')
  };
  ui.uploadBtn.addEventListener('click',()=>ui.fileInput.click());
  ui.fileInput.addEventListener('change',()=>{const file=ui.fileInput.files?.[0];ui.fileInput.value='';if(file)void uploadApprovedDraft(file)});
  ui.forgetTokenBtn.addEventListener('click',()=>{sessionStorage.removeItem('rexprompt.githubToken');syncTokenButton();ui.uploadStatus.textContent='GitHub token forgotten for this tab.'});
  state.ui=ui;syncTokenButton();return ui;
}
function syncTokenButton(){if(state.ui)state.ui.forgetTokenBtn.hidden=!sessionStorage.getItem('rexprompt.githubToken')}

function setDraftBody(sel,entry){
  const ui=state.ui;if(!ui)return;
  if(!entry){
    ui.draftBody.className='visual-empty';ui.draftBody.textContent='No approved production draft stored for this unit.';ui.uploadBtn.textContent='Upload Approved Draft';return;
  }
  const src=draftImageUrl(entry);
  ui.draftBody.className='';ui.draftBody.innerHTML='';
  const wrap=document.createElement('div');wrap.className='visual-image-wrap';
  const img=document.createElement('img');img.src=src;img.alt='Approved production draft for '+sel.recipeId;img.loading='eager';
  const watermark=document.createElement('div');watermark.className='visual-watermark';watermark.textContent='DRAFT · NOT RELEASED';
  wrap.append(img,watermark);ui.draftBody.appendChild(wrap);
  const meta=document.createElement('div');meta.className='visual-meta';meta.textContent=sel.recipeId+' · '+(entry.updatedAt?'stored '+new Date(entry.updatedAt).toLocaleString():'approved production draft');ui.draftBody.appendChild(meta);
  ui.uploadBtn.textContent='Replace Approved Draft';
}
function renderCanonItems(sel,items){
  const ui=state.ui;if(!ui)return;
  if(!items.length){ui.canonBody.className='visual-empty';ui.canonBody.textContent='No released canon image mapped for this unit.';return}
  ui.canonBody.className='visual-canon-list';ui.canonBody.innerHTML='';
  items.forEach((item,i)=>{
    const box=document.createElement('div');box.className='visual-canon-item';
    const wrap=document.createElement('div');wrap.className='visual-image-wrap';
    const img=document.createElement('img');img.src=item.url;img.alt='Released canon reference '+(i+1)+' for '+sel.recipeId;img.loading='lazy';wrap.appendChild(img);box.appendChild(wrap);
    const meta=document.createElement('div');meta.className='visual-meta';meta.textContent=item.label||'Released canon';box.appendChild(meta);ui.canonBody.appendChild(box);
  });
}

async function loadVisionsSeries(sel){
  const source=state.sources?.series?.[sel.seriesId];
  if(!source?.visionsSlug)return null;
  if(state.visionsCache.has(source.visionsSlug))return state.visionsCache.get(source.visionsSlug);
  const base=state.sources.visionsSeriesRawBase?.replace(/\/$/,'');
  if(!base)return null;
  const promise=fetch(base+'/'+encodeURIComponent(source.visionsSlug)+'.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error('Visions metadata HTTP '+r.status);return r.json()}).catch(err=>{console.warn('RexPrompt visuals: Visions metadata unavailable',err);return null});
  state.visionsCache.set(source.visionsSlug,promise);return promise;
}
function explicitCanon(sel){
  const raw=state.releasedLinks?.links?.[visualKey(sel)];
  if(!raw)return [];
  const items=Array.isArray(raw)?raw:(Array.isArray(raw.images)?raw.images:[raw]);
  const siteBase=(state.sources?.visionsSiteBase||'').replace(/\/$/,'');
  return items.map(item=>{
    const path=typeof item==='string'?item:item.path||item.image||item.url;
    if(!path)return null;
    const url=/^https?:\/\//i.test(path)?path:siteBase+('/'+String(path).replace(/^\//,''));
    return {url,label:typeof item==='string'?'Released canon':item.label||'Released canon'};
  }).filter(Boolean);
}
async function automaticPageSet(sel){
  if(!sel.unitIsPage)return null;
  const data=await loadVisionsSeries(sel);if(!data)return null;
  const issueNo=parseIssueNumber(sel.issueLabel);if(!issueNo)return null;
  const issueToken='/issue-'+String(issueNo).padStart(2,'0')+'/';
  const pages=(data.dailyPages||[]).filter(p=>String(p.image||'').includes(issueToken));
  if(pages.length!==sel.recipeCount)return null;
  return {pages,siteBase:(state.sources?.visionsSiteBase||'').replace(/\/$/,'')};
}
function automaticPageCanon(sel,pageSet){
  if(!pageSet||sel.recipeIndex===null)return [];
  const page=pageSet.pages.find(p=>Number(p.pageNumber)===sel.recipeIndex+1)||pageSet.pages[sel.recipeIndex];if(!page?.image)return [];
  return [{url:pageSet.siteBase+page.image,label:'Released canon · '+sel.issueLabel+' · Page '+page.pageNumber+(page.releaseDate?' · '+page.releaseDate:'')}];
}

function decorateSceneOptions(sel,canonMode=false){
  const sceneSel=document.getElementById('sceneSel');if(!sceneSel)return;
  const issueNo=parseIssueNumber(sel.issueLabel),autoCanon=canonMode&&sel.unitIsPage&&issueNo;
  for(const option of sceneSel.options){
    if(!option.dataset.visualBaseLabel)option.dataset.visualBaseLabel=option.textContent||'';
    const recipeId=(option.dataset.recipeId||option.dataset.visualBaseLabel.split(' - ')[0]).trim();option.dataset.recipeId=recipeId;
    const probe={...sel,recipeId,recipeIndex:Number(option.value)};const key=visualKey(probe);
    const hasDraft=Boolean(state.draftManifest?.drafts?.[key]);
    const hasExplicit=Boolean(state.releasedLinks?.links?.[key]);
    const tags=[];if(hasDraft)tags.push('[DRAFT]');if(hasExplicit||autoCanon)tags.push('[CANON]');
    option.textContent=option.dataset.visualBaseLabel+(tags.length?' '+tags.join(' '):'');
  }
}

async function refreshVisuals(){
  const ui=state.ui,sel=currentSelection();if(!ui||!sel)return;
  const nonce=++state.refreshNonce;ui.uploadStatus.textContent='';
  const entry=state.draftManifest?.drafts?.[visualKey(sel)]||null;setDraftBody(sel,entry);
  const explicit=explicitCanon(sel),pageSet=explicit.length?null:await automaticPageSet(sel),canon=explicit.length?explicit:automaticPageCanon(sel,pageSet);if(nonce!==state.refreshNonce)return;renderCanonItems(sel,canon);
  decorateSceneOptions(sel,Boolean(pageSet));
  const bits=[];if(entry)bits.push('approved draft stored');if(canon.length)bits.push('released canon available');ui.stateNote.textContent=bits.length?('Production state: '+bits.join(' · ')):'Production state: no approved draft or mapped released canon for this unit.';
}

function requestToken(){
  let token=sessionStorage.getItem('rexprompt.githubToken');if(token)return token;
  token=window.prompt('Enter a GitHub fine-grained token with Contents: Read and write access to starsplitterrecords/RexPrompt. It is stored only for this browser tab.');
  if(!token)return null;token=token.trim();if(!token)return null;sessionStorage.setItem('rexprompt.githubToken',token);syncTokenButton();return token;
}
async function gh(token,path,{method='GET',body=null,allow404=false}={}){
  const r=await fetch(CONFIG.apiBase+path,{method,headers:{'Accept':'application/vnd.github+json','Authorization':'Bearer '+token,'X-GitHub-Api-Version':'2022-11-28',...(body?{'Content-Type':'application/json'}:{})},body:body?JSON.stringify(body):undefined});
  if(allow404&&r.status===404)return null;
  let payload=null;try{payload=await r.json()}catch{}
  if(!r.ok)throw new Error((payload&&payload.message)||('GitHub API '+r.status));return payload;
}
function bytesToBase64(bytes){let out='',chunk=0x8000;for(let i=0;i<bytes.length;i+=chunk)out+=String.fromCharCode(...bytes.subarray(i,Math.min(i+chunk,bytes.length)));return btoa(out)}
function decodeBase64Utf8(value){const binary=atob(String(value||'').replace(/\s+/g,'')),bytes=Uint8Array.from(binary,c=>c.charCodeAt(0));return new TextDecoder().decode(bytes)}
function extensionFor(file){if(file.type==='image/jpeg')return 'jpg';if(file.type==='image/png')return 'png';if(file.type==='image/webp')return 'webp';return ''}
async function latestDraftManifest(token){
  const path='/repos/'+CONFIG.owner+'/'+CONFIG.repo+'/contents/'+CONFIG.draftManifestPath+'?ref='+encodeURIComponent(CONFIG.branch),payload=await gh(token,path,{allow404:true});
  if(!payload)return {schemaVersion:1,drafts:{}};
  const parsed=JSON.parse(decodeBase64Utf8(payload.content));if(!parsed.drafts||typeof parsed.drafts!=='object')parsed.drafts={};return parsed;
}
async function uploadApprovedDraft(file){
  const ui=state.ui,sel=currentSelection();if(!ui||!sel)return;
  if(!CONFIG.acceptedTypes.has(file.type)){ui.uploadStatus.textContent='Upload failed: use JPEG, PNG, or WebP.';return}
  if(file.size>CONFIG.maxUploadBytes){ui.uploadStatus.textContent='Upload failed: image is larger than 50 MB.';return}
  const verb=state.draftManifest?.drafts?.[visualKey(sel)]?'replace':'store';
  if(!window.confirm('Explicitly '+verb+' the approved production draft for '+sel.recipeId+' in RexPrompt? This does not publish anything to Visions.'))return;
  const token=requestToken();if(!token){ui.uploadStatus.textContent='Upload cancelled: no GitHub token supplied.';return}
  ui.uploadBtn.disabled=true;ui.uploadStatus.textContent='Storing approved draft in RexPrompt…';
  try{
    const refPath='/repos/'+CONFIG.owner+'/'+CONFIG.repo+'/git/ref/heads/'+encodeURIComponent(CONFIG.branch),ref=await gh(token,refPath),headSha=ref.object.sha;
    const commit=await gh(token,'/repos/'+CONFIG.owner+'/'+CONFIG.repo+'/git/commits/'+headSha),manifest=await latestDraftManifest(token),key=visualKey(sel),old=manifest.drafts[key]||null,ext=extensionFor(file);
    const imagePath='production/drafts/'+safePart(sel.seriesId)+'/'+safePart(sel.issueId)+'/'+safePart(sel.recipeId)+'.'+ext;
    const bytes=new Uint8Array(await file.arrayBuffer()),imageBlob=await gh(token,'/repos/'+CONFIG.owner+'/'+CONFIG.repo+'/git/blobs',{method:'POST',body:{content:bytesToBase64(bytes),encoding:'base64'}});
    const updatedAt=new Date().toISOString();manifest.schemaVersion=1;manifest.drafts[key]={seriesId:sel.seriesId,issueId:sel.issueId,recipeId:sel.recipeId,status:'approved-production-draft',image:imagePath,mimeType:file.type,updatedAt};
    const manifestBlob=await gh(token,'/repos/'+CONFIG.owner+'/'+CONFIG.repo+'/git/blobs',{method:'POST',body:{content:JSON.stringify(manifest,null,2)+'\n',encoding:'utf-8'}});
    const tree=[{path:imagePath,mode:'100644',type:'blob',sha:imageBlob.sha},{path:CONFIG.draftManifestPath,mode:'100644',type:'blob',sha:manifestBlob.sha}];
    if(old?.image&&old.image!==imagePath)tree.push({path:old.image,mode:'100644',type:'blob',sha:null});
    const newTree=await gh(token,'/repos/'+CONFIG.owner+'/'+CONFIG.repo+'/git/trees',{method:'POST',body:{base_tree:commit.tree.sha,tree}}),newCommit=await gh(token,'/repos/'+CONFIG.owner+'/'+CONFIG.repo+'/git/commits',{method:'POST',body:{message:'Store approved production draft '+sel.recipeId,tree:newTree.sha,parents:[headSha]}});
    await gh(token,'/repos/'+CONFIG.owner+'/'+CONFIG.repo+'/git/refs/heads/'+encodeURIComponent(CONFIG.branch),{method:'PATCH',body:{sha:newCommit.sha,force:false}});
    manifest.drafts[key].commitSha=newCommit.sha;state.draftManifest=manifest;ui.uploadStatus.textContent='Approved draft stored. Git commit '+newCommit.sha.slice(0,7)+'.';await refreshVisuals();
  }catch(err){ui.uploadStatus.textContent='Upload failed: '+(err instanceof Error?err.message:String(err));}
  finally{ui.uploadBtn.disabled=false;syncTokenButton()}
}

async function loadState(){
  const [drafts,released,sources]=await Promise.all([
    loadOptionalJson(CONFIG.draftManifestPath,{schemaVersion:1,drafts:{}}),
    loadOptionalJson(CONFIG.releasedLinksPath,{schemaVersion:1,links:{}}),
    loadOptionalJson(CONFIG.visualSourcesPath,{schemaVersion:1,series:{}})
  ]);
  state.draftManifest={schemaVersion:1,drafts:{},...drafts,drafts:drafts.drafts||{}};
  state.releasedLinks={schemaVersion:1,links:{},...released,links:released.links||{}};
  state.sources=sources||{schemaVersion:1,series:{}};
}
function bindRefreshEvents(){
  ['showSel','issueSel','sceneSel'].forEach(id=>document.getElementById(id)?.addEventListener('change',()=>setTimeout(()=>void refreshVisuals(),0)));
  const sceneSel=document.getElementById('sceneSel');if(sceneSel)new MutationObserver(()=>setTimeout(()=>void refreshVisuals(),0)).observe(sceneSel,{childList:true});
  document.getElementById('commitBtn')?.addEventListener('click',()=>setTimeout(()=>void refreshVisuals(),0));
}

async function start(){injectStyles();createUi();bindRefreshEvents();await loadState();await refreshVisuals()}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>void start());else void start();
})();
