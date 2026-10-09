(()=>{'use strict';
const C={owner:'starsplitterrecords',repo:'RexPrompt',branch:'main',manifest:'production/references/reference-keeper-manifest.json',root:'production/references',api:'https://api.github.com',types:['character','setting','vehicle','item'],mime:['image/jpeg','image/png','image/webp'],max:50*1024*1024};
const S={manifest:{schemaVersion:1,references:{}},series:[],ui:null,pending:null};
const $=s=>document.querySelector(s), safe=v=>String(v||'item').toLowerCase().replace(/[^a-z0-9._-]+/g,'-').replace(/^-+|-+$/g,'')||'item', title=v=>String(v||'').replace(/(^|[-_\s])([a-z])/g,(_,a,b)=>a+b.toUpperCase());
function ext(f){return f.type==='image/jpeg'?'jpg':f.type==='image/png'?'png':f.type==='image/webp'?'webp':''} function b64(bytes){let s='';for(let i=0;i<bytes.length;i+=32768)s+=String.fromCharCode(...bytes.subarray(i,Math.min(i+32768,bytes.length)));return btoa(s)} function utf8(v){const x=atob(String(v||'').replace(/\s+/g,''));return new TextDecoder().decode(Uint8Array.from(x,c=>c.charCodeAt(0)))}
function inject(){const st=document.createElement('style');st.textContent='.mode-switch{display:flex;gap:6px;flex-wrap:wrap}.mode-switch button{margin:0;padding:9px 13px;font-size:.88rem}.mode-switch button[aria-pressed=true]{font-weight:700;border-width:2px}#assemblerMode[hidden],#referenceKeeperMode[hidden]{display:none!important}.keeper{max-width:1180px}.keeper p{color:var(--muted)}.keeper-controls,.keeper-upload{display:grid;grid-template-columns:repeat(3,minmax(180px,1fr));gap:12px;margin-bottom:14px}.keeper-upload{padding:14px;border:1px solid var(--border);border-radius:8px;background:var(--surface-soft)}.keeper label{display:block;color:var(--muted);font-size:.82rem;margin-bottom:5px}.keeper input,.keeper select{box-sizing:border-box;width:100%;min-width:0;margin:0;padding:9px;background:var(--control-bg);color:var(--control-fg);border:1px solid var(--border);border-radius:4px}.keeper-actions{display:flex;gap:8px;flex-wrap:wrap}.keeper-actions button,.keeper-card button{margin:0;padding:9px 12px;font-size:.86rem}.keeper-status{color:var(--muted);font-size:.85rem;min-height:1.2em}.keeper-token{grid-column:1/-1;padding:10px;border:1px solid var(--border);border-radius:5px;background:var(--bg)}.keeper-token-row{display:flex;gap:8px}.keeper-token-row input{flex:1}.keeper-groups h5{text-transform:capitalize}.keeper-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px}.keeper-card{padding:10px;border:1px solid var(--border);border-radius:8px;background:var(--surface-soft)}.keeper-card img{width:100%;height:210px;object-fit:contain;background:var(--surface);border:1px solid var(--border);border-radius:5px}.keeper-card img{cursor:zoom-in}.keeper-card img:focus-visible{outline:3px solid var(--accent);outline-offset:3px}.keeper-lightbox{position:fixed;inset:0;z-index:10000;display:flex;align-items:center;justify-content:center;padding:50px 24px 24px;box-sizing:border-box;background:rgba(0,0,0,.91)}.keeper-lightbox[hidden]{display:none!important}.keeper-lightbox img{max-width:100%;max-height:100%;width:auto;height:auto;object-fit:contain}.keeper-lightbox-close{position:absolute;top:10px;right:16px;padding:6px 12px!important;font-size:1.65rem!important;background:#202832!important;color:#fff!important;border:1px solid #76808a!important;border-radius:6px;cursor:pointer}.keeper-lightbox-caption{position:absolute;bottom:6px;left:50%;transform:translateX(-50%);color:#fff;font-size:.82rem;background:rgba(0,0,0,.65);padding:3px 8px;border-radius:4px;pointer-events:none}.keeper-name{font-weight:700;margin:8px 0 3px}.keeper-meta{font-size:.74rem;color:var(--muted);overflow-wrap:anywhere;margin-bottom:8px}@media(max-width:760px){.keeper-controls,.keeper-upload{grid-template-columns:1fr}.keeper-token{grid-column:auto}}';document.head.appendChild(st)}
async function load(path,fallback){try{const r=await fetch(path+(path.includes('?')?'&':'?')+'v='+Date.now(),{cache:'no-store'});if(r.status===404)return fallback;if(!r.ok)throw Error('HTTP '+r.status);return await r.json()}catch(e){console.warn('Reference Keeper',e);return fallback}}
async function gh(token,path,o={}){const r=await fetch(C.api+path,{method:o.method||'GET',headers:{Accept:'application/vnd.github+json',Authorization:'Bearer '+token,'X-GitHub-Api-Version':'2022-11-28',...(o.body?{'Content-Type':'application/json'}:{})},body:o.body?JSON.stringify(o.body):undefined});if(o.allow404&&r.status===404)return null;let p=null;try{p=await r.json()}catch{}if(!r.ok)throw Error(p?.message||'GitHub API '+r.status);return p}
async function latest(token){const p=await gh(token,'/repos/'+C.owner+'/'+C.repo+'/contents/'+C.manifest+'?ref='+encodeURIComponent(C.branch),{allow404:true});if(!p)return {schemaVersion:1,references:{}};const m=JSON.parse(utf8(p.content));m.references=m.references||{};return m}
function seriesFrom(shows){const m=new Map;function add(name){name=String(name||'').split(' — ')[0].replace(/\s+Covers?$/i,'').trim();const id=safe(name);if(name&&!m.has(id))m.set(id,{id,name})}(Array.isArray(shows)?shows:[]).forEach(x=>add(x.seriesName||x.name||x.id));Object.values(S.manifest.references||{}).forEach(x=>add(x?.seriesName||x?.seriesId));return [...m.values()].sort((a,b)=>a.name.localeCompare(b.name))}
function setMode(mode){const k=mode==='keeper';$('#assemblerMode').hidden=k;$('#referenceKeeperMode').hidden=!k;$('#assemblerModeBtn').setAttribute('aria-pressed',String(!k));$('#referenceKeeperModeBtn').setAttribute('aria-pressed',String(k));$('#appTitle').textContent=k?'RexPrompt Reference Keeper':'RexPrompt Assembler';document.title=$('#appTitle').textContent;localStorage.setItem('rexprompt.mode',k?'keeper':'assembler');if(k)render()}
function token(){return sessionStorage.getItem('rexprompt.githubToken')} function syncToken(){S.ui.forget.hidden=!token()} function askToken(fn){if(token())return void fn();S.pending=fn;S.ui.tokenBox.hidden=false;S.ui.tokenInput.focus()} function saveToken(){const t=S.ui.tokenInput.value.trim();if(!t)return;sessionStorage.setItem('rexprompt.githubToken',t);S.ui.tokenInput.value='';S.ui.tokenBox.hidden=true;syncToken();const fn=S.pending;S.pending=null;if(fn)void fn()}
function ui(){const h=$('#referenceKeeperMode');h.innerHTML='<div class="keeper"><p>Storage-only visual references in GitHub. They are not assembled into RexPrompt recipes and do not publish to StarSplitterVisions.</p><div class="keeper-controls"><div><label>Series</label><select id="keeperSeries"></select></div><div><label>View</label><select id="keeperView"><option value="all">All types</option>'+C.types.map(t=>'<option>'+title(t)+'</option>').join('')+'</select></div><div></div></div><div class="keeper-upload"><div><label>Reference name</label><input id="keeperName" maxlength="120" placeholder="Carrie, DTI Office, Thunderbreak"></div><div><label>Type</label><select id="keeperType">'+C.types.map(t=>'<option value="'+t+'">'+title(t)+'</option>').join('')+'</select></div><div><label>Image</label><input id="keeperFile" type="file" accept="image/jpeg,image/png,image/webp"></div><div class="keeper-actions"><button id="keeperStore">Store Reference</button><button id="keeperForget">Forget GitHub Token</button></div><div id="keeperStatus" class="keeper-status"></div><div id="keeperToken" class="keeper-token" hidden><label>GitHub fine-grained token · Contents: Read and write · stored only for this browser tab</label><div class="keeper-token-row"><input id="keeperTokenInput" type="password" autocomplete="off" placeholder="github_pat_…"><button id="keeperUseToken">Use Token</button><button id="keeperCancelToken">Cancel</button></div></div></div><div id="keeperCount" class="keeper-status"></div><div id="keeperGroups" class="keeper-groups"></div></div>';
 const u=S.ui={series:$('#keeperSeries'),view:$('#keeperView'),name:$('#keeperName'),type:$('#keeperType'),file:$('#keeperFile'),store:$('#keeperStore'),forget:$('#keeperForget'),status:$('#keeperStatus'),tokenBox:$('#keeperToken'),tokenInput:$('#keeperTokenInput'),groups:$('#keeperGroups'),count:$('#keeperCount')};u.file.onchange=()=>{if(u.file.files?.[0]&&!u.name.value.trim())u.name.value=u.file.files[0].name.replace(/\.[^.]+$/,'').replace(/[_-]+/g,' ')};u.store.onclick=()=>askToken(store);u.forget.onclick=()=>{sessionStorage.removeItem('rexprompt.githubToken');syncToken();u.status.textContent='GitHub token forgotten for this tab.'};$('#keeperUseToken').onclick=saveToken;$('#keeperCancelToken').onclick=()=>{S.pending=null;u.tokenBox.hidden=true};u.tokenInput.onkeydown=e=>{if(e.key==='Enter'){e.preventDefault();saveToken()}};u.series.onchange=()=>{localStorage.setItem('rexprompt.keeperSeries',u.series.value);render()};u.view.onchange=render;return u}
function populate(){S.ui.series.innerHTML='';S.series.forEach(x=>{const o=document.createElement('option');o.value=x.id;o.textContent=x.name;S.ui.series.append(o)});const saved=localStorage.getItem('rexprompt.keeperSeries');if(S.series.some(x=>x.id===saved))S.ui.series.value=saved}
function imgUrl(e){return 'https://raw.githubusercontent.com/'+C.owner+'/'+C.repo+'/'+C.branch+'/'+e.image+'?v='+encodeURIComponent(e.updatedAt||Date.now())} function validate(f){return !f?'Choose an image.':!C.mime.includes(f.type)?'Use JPEG, PNG, or WebP.':f.size>C.max?'Image is larger than 50 MB.':''}
function openLightbox(e){let box=$('#keeperLightbox');if(!box){box=document.createElement('div');box.id='keeperLightbox';box.className='keeper-lightbox';box.hidden=true;box.setAttribute('role','dialog');box.setAttribute('aria-modal','true');box.setAttribute('aria-label','Reference image preview');box.innerHTML='<button type="button" class="keeper-lightbox-close" aria-label="Close preview">×</button><img alt=""><div class="keeper-lightbox-caption"></div>';document.body.append(box);box.querySelector('button').onclick=closeLightbox;box.addEventListener('click',ev=>{if(ev.target===box)closeLightbox()});document.addEventListener('keydown',ev=>{if(ev.key==='Escape'&&!box.hidden)closeLightbox()})}S.previousFocus=document.activeElement;box.querySelector('img').src=imgUrl(e);box.querySelector('img').alt=e.name+' reference';box.querySelector('.keeper-lightbox-caption').textContent=e.name;box.hidden=false;box.querySelector('button').focus()}function closeLightbox(){const box=$('#keeperLightbox');if(box)box.hidden=true;if(S.previousFocus?.isConnected)S.previousFocus.focus();S.previousFocus=null}
function render(){if(!S.ui)return;let a=Object.values(S.manifest.references||{}).filter(x=>x.seriesId===S.ui.series.value);const v=S.ui.view.value.toLowerCase();if(v!=='all')a=a.filter(x=>x.type===v);a.sort((x,y)=>(x.type+x.name).localeCompare(y.type+y.name));S.ui.count.textContent=a.length+' stored reference'+(a.length===1?'':'s');S.ui.groups.innerHTML='';if(!a.length){S.ui.groups.textContent='No stored references for this selection.';return}const types=v==='all'?C.types:[v];types.forEach(t=>{const items=a.filter(x=>x.type===t);if(!items.length)return;const sec=document.createElement('section');sec.innerHTML='<h5>'+title(t)+'s</h5><div class="keeper-grid"></div>';const g=sec.querySelector('.keeper-grid');items.forEach(e=>{const c=document.createElement('article');c.className='keeper-card';c.innerHTML='<img alt=""><div class="keeper-name"></div><div class="keeper-meta"></div><div class="keeper-actions"><button class="replace">Replace</button><button class="delete">Delete</button><input class="pick" type="file" accept="image/jpeg,image/png,image/webp" hidden></div>';c.querySelector('img').src=imgUrl(e);c.querySelector('img').alt=e.name+' reference';c.querySelector('img').tabIndex=0;c.querySelector('img').setAttribute('role','button');c.querySelector('img').setAttribute('aria-label','Enlarge '+e.name);c.querySelector('img').onclick=()=>openLightbox(e);c.querySelector('img').onkeydown=ev=>{if(ev.key==='Enter'||ev.key===' '){ev.preventDefault();openLightbox(e)}};c.querySelector('.keeper-name').textContent=e.name;c.querySelector('.keeper-meta').textContent=title(e.type)+' · '+e.image;const pick=c.querySelector('.pick');c.querySelector('.replace').onclick=()=>pick.click();pick.onchange=()=>{const f=pick.files?.[0];pick.value='';if(f)askToken(()=>replace(e,f))};c.querySelector('.delete').onclick=()=>askToken(()=>remove(e));g.append(c)});S.ui.groups.append(sec)})}

// Keep all changes to the manifest on a single local write lane. Concurrent browser
// tabs / external writers are handled by replaying the operation on the newest HEAD.
let writeLane=Promise.resolve();
function queueWrite(task){
  const next=writeLane.then(task);
  writeLane=next.catch(()=>{});
  return next;
}
function retryableConflict(error){
  return /not a fast.forward|reference update failed|update.*ref|conflict|409|422/i.test(String(error?.message||error));
}
async function transact(change){
  const t=token();
  if(!t)throw Error('GitHub token is required.');
  const prefix='/repos/'+C.owner+'/'+C.repo;
  for(let attempt=0;attempt<4;attempt++){
    try{
      const ref=await gh(t,prefix+'/git/ref/heads/'+encodeURIComponent(C.branch));
      const head=ref.object.sha;
      const [commit,payload]=await Promise.all([
        gh(t,prefix+'/git/commits/'+head),
        gh(t,prefix+'/contents/'+C.manifest+'?ref='+encodeURIComponent(head),{allow404:true})
      ]);
      const manifest=payload?JSON.parse(utf8(payload.content)):{schemaVersion:1,references:{}};
      manifest.references=manifest.references||{};
      const outcome=await change({token:t,manifest,head,prefix});
      const blob=await gh(t,prefix+'/git/blobs',{method:'POST',body:{content:JSON.stringify(manifest,null,2)+'\n',encoding:'utf-8'}});
      const tree=await gh(t,prefix+'/git/trees',{method:'POST',body:{base_tree:commit.tree.sha,tree:[...outcome.tree,{path:C.manifest,mode:'100644',type:'blob',sha:blob.sha}]}});
      const next=await gh(t,prefix+'/git/commits',{method:'POST',body:{message:outcome.message,tree:tree.sha,parents:[head]}});
      await gh(t,prefix+'/git/refs/heads/'+encodeURIComponent(C.branch),{method:'PATCH',body:{sha:next.sha,force:false}});
      S.manifest=manifest;
      return next.sha;
    }catch(error){
      if(attempt===3||!retryableConflict(error))throw error;
      S.ui.status.textContent='GitHub changed during save. Retrying '+(attempt+1)+'/3…';
    }
  }
}
async function write(entry,file,old){
  const path=C.root+'/'+safe(entry.seriesId)+'/keeper/'+safe(entry.type)+'/'+safe(entry.name)+'.'+ext(file);
  const bytes=new Uint8Array(await file.arrayBuffer());
  const imageBlob=await gh(token(),'/repos/'+C.owner+'/'+C.repo+'/git/blobs',{method:'POST',body:{content:b64(bytes),encoding:'base64'}});
  return queueWrite(()=>transact(async({manifest})=>{
    const existing=manifest.references[entry.id];
    if(!old&&existing)throw Error('Reference already exists. Use Replace.');
    if(old&&!existing)throw Error('Reference no longer exists. Refresh the page.');
    const final={...entry,image:path,mimeType:file.type,sourceFilename:file.name,updatedAt:new Date().toISOString()};
    manifest.references[entry.id]=final;
    const tree=[{path,mode:'100644',type:'blob',sha:imageBlob.sha}];
    if(existing?.image&&existing.image!==path)tree.push({path:existing.image,mode:'100644',type:'blob',sha:null});
    return {tree,message:(old?'Replace':'Store')+' reference '+entry.seriesId+' / '+entry.type+' / '+entry.name};
  }));
}
async function store(){const u=S.ui,f=u.file.files?.[0],err=validate(f);if(err)return void(u.status.textContent=err);const name=u.name.value.trim(),type=u.type.value,sid=u.series.value,series=S.series.find(x=>x.id===sid);if(!name)return void(u.status.textContent='Enter a reference name.');const id=safe(sid)+'::'+safe(type)+'::'+safe(name);if(S.manifest.references[id])return void(u.status.textContent='That reference already exists. Use Replace on its card.');if(!confirm('Store '+name+' as a '+type+' reference for '+(series?.name||sid)+'?'))return;u.store.disabled=true;u.status.textContent='Storing reference…';try{const sha=await write({id,seriesId:sid,seriesName:series?.name||sid,type,name},f);u.status.textContent='Stored. Git commit '+sha.slice(0,7)+'.';u.file.value='';u.name.value='';render()}catch(e){u.status.textContent='Upload failed: '+e.message}finally{u.store.disabled=false;syncToken()}}
async function replace(e,f){const err=validate(f);if(err)return void(S.ui.status.textContent=err);if(!confirm('Replace the stored image for '+e.name+'?'))return;S.ui.status.textContent='Replacing reference…';try{const sha=await write({id:e.id,seriesId:e.seriesId,seriesName:e.seriesName,type:e.type,name:e.name},f,e);S.ui.status.textContent='Replaced. Git commit '+sha.slice(0,7)+'.';render()}catch(x){S.ui.status.textContent='Replace failed: '+x.message}finally{syncToken()}}
async function remove(e){
  if(!confirm('Delete '+e.name+' from Reference Keeper?'))return;
  S.ui.status.textContent='Deleting reference…';
  try{
    const sha=await queueWrite(()=>transact(async({manifest})=>{
      const current=manifest.references[e.id];
      if(!current)throw Error('Reference no longer exists. Refresh the page.');
      delete manifest.references[e.id];
      return {tree:[{path:current.image,mode:'100644',type:'blob',sha:null}],message:'Delete reference '+e.seriesId+' / '+e.type+' / '+e.name};
    }));
    S.ui.status.textContent='Deleted. Git commit '+sha.slice(0,7)+'.';
    render();
  }catch(x){S.ui.status.textContent='Delete failed: '+x.message}
  finally{syncToken()}
}
async function start(){inject();S.ui=ui();const [shows,m]=await Promise.all([load('data/shows.json',[]),load(C.manifest,{schemaVersion:1,references:{}})]);S.manifest={schemaVersion:1,references:{},...m,references:m.references||{}};S.series=seriesFrom(shows);populate();syncToken();$('#assemblerModeBtn').onclick=()=>setMode('assembler');$('#referenceKeeperModeBtn').onclick=()=>setMode('keeper');setMode(localStorage.getItem('rexprompt.mode')==='keeper'?'keeper':'assembler')}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>void start());else void start();})();
