/* RexPrompt dialogue editor: edits the effective, normalized page source. */
(()=>{
'use strict';
const REPO='starsplitterrecords/RexPrompt',BRANCH='main',API='https://api.github.com/repos/'+REPO;
const own=(o,k)=>Object.prototype.hasOwnProperty.call(o||{},k);
const clone=o=>JSON.parse(JSON.stringify(o));
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const $=(selector,root=document)=>root.querySelector(selector);
const el=(tag,attrs={},text)=>{const n=document.createElement(tag);for(const [k,v] of Object.entries(attrs)){if(k==='class')n.className=v;else if(k==='type'||k==='title'||k==='placeholder'||k==='aria-label')n.setAttribute(k,v);else n[k]=v}if(text!==undefined)n.textContent=text;return n};
const pathFor=(base,file)=>String(base||'data').replace(/\/$/,'')+'/'+file;
function findRecord(doc,id){
  if(Array.isArray(doc))return doc.find(item=>item&&item.id===id)||null;
  if(Array.isArray(doc?.pages))return doc.pages.find(item=>item&&item.id===id)||null;
  if(doc&&typeof doc==='object'){
    if(doc[id]&&typeof doc[id]==='object')return doc[id];
    for(const value of Object.values(doc))if(value&&typeof value==='object'&&value.id===id)return value;
  }
  return null;
}
function sourceEntries(raw){if(Array.isArray(raw))return raw;if(Array.isArray(raw?.pages))return raw.pages;return Object.entries(raw||{}).map(([id,v])=>({id,...v}))}
function encoded(file,encoding){return encoding==='gzip-base64'||/\.json\.gzb64$/i.test(file)}
async function sourceDocument(base,file,encoding){const path=pathFor(base,file);return {path,file,encoding:encoded(file,encoding)?'gzip-base64':null,doc:await loadEncodedJson(path,encoded(file,encoding)?'gzip-base64':null)}}
async function locateSource(show,scene){
  const id=scene.id,base=show.basePath||'data';
  const files=Array.isArray(show.scenesFiles)?show.scenesFiles:[show.scenesFile||'scenes.json'];
  let dialogue=null,panel=null;
  for(const file of files){
    const entry=await sourceDocument(base,file,null);
    if(findRecord(entry.doc,id)){
      if(dialogue)throw Error('More than one base source defines this page. Resolve the duplicate before editing.');
      dialogue={...entry,kind:'page'};panel={...entry,kind:'page'};
    }
  }
  for(const overlay of show.sceneOverlays||[]){
    if(overlay.includeIds?.length&&!overlay.includeIds.includes(id))continue;
    if(overlay.excludeIds?.includes(id))continue;
    const entry=await sourceDocument(base,overlay.file,overlay.encoding);
    const patch=findRecord(entry.doc,id);
    if(!patch)continue;
    if(overlay.mergeById){
      if(own(patch,'dialogueInline')||own(patch,'sceneDialogue')||own(patch,'dialog'))
        dialogue={...entry,kind:'overlay-patch'};
      if(own(patch,'panelPlan'))panel={...entry,kind:'overlay-patch'};
    }else{
      dialogue={...entry,kind:'page'};
      panel={...entry,kind:'page'};
    }
  }
  for(const overlay of show.dialogueOverlays||[]){
    const entry=await sourceDocument(base,overlay.file,overlay.encoding);
    if(findRecord(entry.doc,id))dialogue={...entry,kind:'dialogue-overlay'};
  }
  if(!dialogue)throw Error('No writable source record could be found for this page.');
  if(dialogue.kind!=='page')throw Error('This page still receives dialogue from an overriding layer. Normalize that dialogue into its page source before editing.');
  const raw=findRecord(dialogue.doc,id);
  if(!raw)throw Error('The source page cannot be located within '+dialogue.path+'.');
  if(!same(raw.dialogueInline||[],scene.dialogueInline||[]))
    throw Error('The live dialogue does not match its page source. A remaining override must be consolidated before editing.');
  if(!Array.isArray(scene.dialogueInline)&&Array.isArray(scene.dialog)&&scene.dialog.length)
    throw Error('This page uses shared dialogue IDs rather than normalized inline dialogue. Normalize it before editing.');
  return {dialogue,panel,samePanelSource:panel?.path===dialogue.path&&panel?.kind==='page'};
}
function inferPanel(scene,index){
  for(const [i,p] of (scene.panelPlan||[]).entries())if(p&&typeof p==='object'&&Array.isArray(p.dialogueIndices)&&p.dialogueIndices.includes(index))return i+1;
  const match=String(scene.dialogueInline?.[index]?.subtext||'').trim().match(/^Panel\s+(\d+)$/i);
  return match?Number(match[1]):null;
}
function initialRows(scene){
  return (scene.dialogueInline||[]).map((d,i)=>({
    key:i+1,original:clone(d),speaker:String(d.speaker||''),handle:String(d.handle||''),
    text:String(d.text||''),note:/^Panel\s+\d+$/i.test(String(d.subtext||'').trim())?'':String(d.subtext||''),
    panel:inferPanel(scene,i)
  }));
}
function draftPage(scene,rows){
  const next=clone(scene),panelPlan=next.panelPlan||[];
  const indexed=panelPlan.some(p=>p&&typeof p==='object'&&Array.isArray(p.dialogueIndices));
  next.dialogueInline=rows.map((row,i)=>{
    if(!row.text.trim())throw Error('Dialogue line '+(i+1)+' has no text.');
    if(!row.speaker.trim()&&!row.handle.trim())throw Error('Dialogue line '+(i+1)+' needs a speaker or handle.');
    if(row.panel!==null&&(!Number.isInteger(row.panel)||row.panel<1||row.panel>panelPlan.length))
      throw Error('Dialogue line '+(i+1)+' has a panel outside this page.');
    const d=clone(row.original);
    if(row.speaker.trim())d.speaker=row.speaker.trim();else delete d.speaker;
    if(row.handle.trim())d.handle=row.handle.trim();else delete d.handle;
    d.text=row.text;
    if(indexed){
      if(row.note.trim())d.subtext=row.note;else if(row.panel!==null)d.subtext='Panel '+row.panel;else delete d.subtext;
    }else{
      if(row.panel!==null&&row.note.trim())
        throw Error('Line '+(i+1)+' has authored subtext as well as a panel assignment. The current page format cannot store both without a structured panel map; preserve the subtext and normalize panel ownership first.');
      if(row.panel!==null)d.subtext='Panel '+row.panel;
      else if(row.note.trim())d.subtext=row.note;
      else delete d.subtext;
    }
    return d;
  });
  if(indexed){
    next.panelPlan=panelPlan.map((p,i)=>({...p,dialogueIndices:rows.flatMap((r,j)=>r.panel===i+1?[j]:[])}));
    if(rows.some(r=>r.panel===null)&&next.promptPanelMode==='clean')
      throw Error('Every dialogue line needs panel ownership for this page’s clean-panel mode.');
  }
  return next;
}
function bytesBase64(bytes){
  let str='';for(let i=0;i<bytes.length;i+=0x8000)str+=String.fromCharCode(...bytes.subarray(i,i+0x8000));return btoa(str);
}
function base64Bytes(s){return Uint8Array.from(atob(String(s||'').replace(/\s+/g,'')),c=>c.charCodeAt(0))}
async function decodeText(text,encoding){
  if(encoding!=='gzip-base64')return JSON.parse(text);
  if(typeof DecompressionStream==='undefined')throw Error('Browser gzip support is required to edit this encoded source.');
  const stream=new Blob([base64Bytes(text)]).stream().pipeThrough(new DecompressionStream('gzip'));
  return JSON.parse(await new Response(stream).text());
}
async function encodeText(doc,encoding){
  const text=JSON.stringify(doc,null,2)+'\n';
  if(encoding!=='gzip-base64')return text;
  if(typeof CompressionStream==='undefined')throw Error('Browser gzip support is required to save this encoded source.');
  const stream=new Blob([new TextEncoder().encode(text)]).stream().pipeThrough(new CompressionStream('gzip'));
  return bytesBase64(new Uint8Array(await new Response(stream).arrayBuffer()))+'\n';
}
async function github(token,path,options={}){
  const url=API+'/contents/'+path.split('/').map(encodeURIComponent).join('/');
  const res=await fetch(url,{method:options.method||'GET',cache:'no-store',
    headers:{Accept:'application/vnd.github+json',Authorization:'Bearer '+token,'X-GitHub-Api-Version':'2022-11-28',...(options.body?{'Content-Type':'application/json'}:{})},
    body:options.body?JSON.stringify(options.body):undefined});
  let data;try{data=await res.json()}catch{data={}}
  if(!res.ok)throw Error((data.message||'GitHub request failed')+' (HTTP '+res.status+')');
  return data;
}
async function saveToGithub(source,scene,draft,token){
  const path=source.dialogue.path,encoding=source.dialogue.encoding;
  return window.RexPromptGithubWrites.run(async()=>{
    const latest=await github(token,path);
    if(latest.type!=='file'||!latest.sha||!latest.content)throw Error('GitHub did not return a writable source file.');
    const original=await decodeText(new TextDecoder().decode(base64Bytes(latest.content)),encoding);
    const page=findRecord(original,scene.id);
    if(!page)throw Error('Page is no longer in its source file. Refresh before editing.');
    if(!same(page.dialogueInline||[],scene.dialogueInline||[]))
      throw Error('Dialogue changed on GitHub after this page was loaded. Refresh before editing to avoid overwriting another revision.');
    const changedPanels=!same(scene.panelPlan||[],draft.panelPlan||[]);
    if(changedPanels){
      if(!source.samePanelSource)throw Error('Panel assignments are owned by another source layer. Normalize the panel plan before saving its assignments.');
      if(!same(page.panelPlan||[],scene.panelPlan||[]))
        throw Error('Panel plan changed on GitHub. Refresh to avoid overwriting another revision.');
      page.panelPlan=clone(draft.panelPlan);
    }
    page.dialogueInline=clone(draft.dialogueInline);
    const updated=await encodeText(original,encoding);
    const put=await github(token,path,{method:'PUT',body:{
      message:'Edit '+scene.id+' dialogue in authoritative production source',
      content:bytesBase64(new TextEncoder().encode(updated)),
      sha:latest.sha,branch:BRANCH
    }});
    if(!put.commit?.sha)throw Error('GitHub did not confirm a commit.');
    return put.commit.sha;
  });
}
function makeInput(type,value,onChange,placeholder){
  const input=el(type==='textarea'?'textarea':'input',type==='textarea'?{}:{type:'text'});
  input.value=value??'';
  if(placeholder)input.placeholder=placeholder;
  input.addEventListener('input',()=>onChange(input.value));
  return input;
}
function field(label,node,cls=''){const wrapper=el('label',{class:cls});wrapper.append(el('span',{},label),node);return wrapper}
function lineButtons(row,model,render){
  const actions=el('div',{class:'rp-dialogue-line-actions'});
  for(const [name,title,action] of [
    ['↑','Move up',()=>{const i=model.rows.indexOf(row);if(i>0)[model.rows[i-1],model.rows[i]]=[model.rows[i],model.rows[i-1]]}],
    ['↓','Move down',()=>{const i=model.rows.indexOf(row);if(i<model.rows.length-1)[model.rows[i+1],model.rows[i]]=[model.rows[i],model.rows[i+1]]}],
    ['×','Remove line',()=>{model.rows=model.rows.filter(r=>r!==row)}]
  ]){
    const b=el('button',{type:'button',title,'aria-label':title},name);
    b.addEventListener('click',()=>{action();render()});actions.append(b);
  }
  return actions;
}
function mount({button,getContext,onSaved,compile}){
  if(!button)throw Error('Dialogue editor button missing.');
  const modal=el('div',{class:'rp-dialogue-modal',hidden:true});
  modal.innerHTML='<section class="rp-dialogue-dialog" role="dialog" aria-modal="true" aria-labelledby="rpDialogueTitle">'+
    '<header class="rp-dialogue-header"><div class="rp-dialogue-title"><h2 id="rpDialogueTitle">Design Dialogue Editor</h2><div class="rp-dialogue-subtitle"></div></div><button type="button" class="rp-dialogue-close" aria-label="Close editor">Close</button></header>'+
    '<div class="rp-dialogue-body"><nav class="rp-dialogue-tabs" role="tablist" aria-label="Dialogue presentation"><button type="button" data-tab="page" role="tab" aria-selected="true">Page Dialogue</button><button type="button" data-tab="script" role="tab" aria-selected="false">Scene Script</button></nav><div class="rp-dialogue-toolbar"><button type="button" class="rp-dialogue-add">+ Add line</button><p>Edits preserve authored text and ordering unless you change them.</p></div><div class="rp-dialogue-lines"></div><details class="rp-dialogue-preview"><summary>Compare assembled prompts before saving</summary><div class="rp-dialogue-preview-columns"><section><h4>Current</h4><pre class="rp-dialogue-before"></pre></section><section><h4>Edited</h4><pre class="rp-dialogue-after"></pre></section></div></details></div>'+
    '<footer class="rp-dialogue-footer"><span class="rp-dialogue-status" role="status"></span><input class="rp-dialogue-token-input" type="password" autocomplete="off" placeholder="GitHub token (this tab only)" hidden><button type="button" class="rp-dialogue-token-set" hidden>Use token</button><button type="button" class="rp-dialogue-revert">Revert changes</button><button type="button" class="rp-dialogue-save">Save to GitHub</button></footer></section>';
  document.body.append(modal);
  const status=$('.rp-dialogue-status',modal),list=$('.rp-dialogue-lines',modal),saveBtn=$('.rp-dialogue-save',modal);
  const tabBtns=[...modal.querySelectorAll('[data-tab]')];
  let model=null,formerFocus=null,busy=false,nextKey=10000;
  function message(text,error=false){status.textContent=text;status.classList.toggle('rp-dialogue-error',error)}
  function changes(){
    if(!model)return null;
    const next=draftPage(model.scene,model.rows);
    return {draft:next,changed:!same(next.dialogueInline||[],model.scene.dialogueInline||[])||!same(next.panelPlan||[],model.scene.panelPlan||[])};
  }
  function preview(){
    if(!model)return;
    try{
      const edit=changes();
      const baseline=compile(model.scene);
      const proposed=compile(edit.draft);
      $('.rp-dialogue-before',modal).textContent=baseline;
      $('.rp-dialogue-after',modal).textContent=proposed;
      message(edit.changed?'Unsaved edits — review and save to GitHub.':'No changes.');
      saveBtn.disabled=!edit.changed||busy||!model.source;
    }catch(err){
      $('.rp-dialogue-after',modal).textContent=err.message;
      message('Cannot compile edited dialogue: '+err.message,true);
      saveBtn.disabled=true;
    }
  }
  function update(){if(!busy)preview()}
  function pageLine(row){
    const wrapper=el('div',{class:'rp-dialogue-line'});
    const panel=makeInput('text',row.panel===null?'':String(row.panel),v=>{row.panel=v.trim()===''?null:Number(v);update()},'—');
    wrapper.append(field('Panel',panel));
    wrapper.append(field('Speaker',makeInput('text',row.speaker,v=>{row.speaker=v;update()},'CAPTION or character')));
    wrapper.append(field('Handle',makeInput('text',row.handle,v=>{row.handle=v;update()},'@... (optional)')));
    wrapper.append(field('Exact dialogue',makeInput('textarea',row.text,v=>{row.text=v;update()},'Dialogue or caption')));
    wrapper.append(field('Subtext / direction',makeInput('textarea',row.note,v=>{row.note=v;update()},'Existing authored subtext'),'rp-dialogue-note'));
    wrapper.append(lineButtons(row,model,render));return wrapper;
  }
  function scriptLine(row){
    const wrapper=el('div',{class:'rp-dialogue-script-line'});
    const meta=el('div');
    meta.append(field('Speaker',makeInput('text',row.speaker||row.handle,v=>{if(row.speaker)row.speaker=v;else row.handle=v;update()},'Speaker'),'rp-dialogue-speaker'));
    const panel=makeInput('text',row.panel===null?'':String(row.panel),v=>{row.panel=v.trim()===''?null:Number(v);update()},'—');
    meta.append(field('Panel',panel,'rp-dialogue-script-panel'));
    const fields=el('div',{class:'rp-dialogue-script-fields'});
    fields.append(field('Line',makeInput('textarea',row.text,v=>{row.text=v;update()})));
    if(row.note)fields.append(field('Direction',makeInput('textarea',row.note,v=>{row.note=v;update()}),'rp-dialogue-script-notes'));
    wrapper.append(meta,fields);return wrapper;
  }
  function render(){
    if(!model)return;
    tabBtns.forEach(btn=>btn.setAttribute('aria-selected',String(btn.dataset.tab===model.tab)));
    list.replaceChildren();
    if(!model.rows.length)list.append(el('p',{class:'rp-dialogue-empty'},'This production page has no dialogue lines. Add a line only if it is intended.'));
    for(const row of model.rows)list.append(model.tab==='page'?pageLine(row):scriptLine(row));
    preview();
  }
  function close(){
    if(busy)return;
    if(model){try{if(changes()?.changed&&!confirm('Discard unsaved dialogue edits?'))return}catch{if(!confirm('Discard unsaved dialogue edits?'))return}}
    modal.hidden=true;document.body.classList.remove('rp-dialogue-open');model=null;
    formerFocus?.focus();
  }
  $('.rp-dialogue-close',modal).onclick=close;
  modal.addEventListener('mousedown',event=>{if(event.target===modal)close()});
  document.addEventListener('keydown',event=>{if(!modal.hidden&&event.key==='Escape'){event.preventDefault();close()}});
  tabBtns.forEach(btn=>btn.onclick=()=>{if(model){model.tab=btn.dataset.tab;render()}});
  $('.rp-dialogue-add',modal).onclick=()=>{
    if(!model)return;
    model.rows.push({key:nextKey++,original:{},speaker:'CAPTION',handle:'',text:'',note:'',panel:null});
    render();list.lastElementChild?.scrollIntoView({block:'nearest'});
  };
  $('.rp-dialogue-revert',modal).onclick=()=>{if(model&&!busy){model.rows=initialRows(model.scene);render()}};
  const tokenInput=$('.rp-dialogue-token-input',modal),tokenSet=$('.rp-dialogue-token-set',modal);
  tokenSet.onclick=()=>{try{window.RexPromptGithubAuth.setToken(tokenInput.value);tokenInput.value='';tokenInput.hidden=tokenSet.hidden=true;message('GitHub token active for this browser tab.')}catch(err){message(err.message,true)}};
  function syncAuth(){const absent=!window.RexPromptGithubAuth.getToken();tokenInput.hidden=tokenSet.hidden=!absent}
  window.addEventListener('rexprompt:github-auth-change',syncAuth);
  button.onclick=async()=>{
    const context=getContext();
    if(!context?.scene)return;
    model={scene:clone(context.scene),rows:initialRows(context.scene),tab:'page',source:null,id:context.scene.id};
    formerFocus=document.activeElement;modal.hidden=false;document.body.classList.add('rp-dialogue-open');
    $('.rp-dialogue-subtitle',modal).textContent=(context.show?.seriesName||context.show?.name||'')+' · '+context.scene.id;
    syncAuth();saveBtn.disabled=true;message('Locating the current source record…');
    render();saveBtn.disabled=true;
    try{
      model.source=await locateSource(context.show,context.scene);
      message('Editing authoritative source: '+model.source.dialogue.path);
      preview();
    }catch(err){model.source=null;saveBtn.disabled=true;message(err.message,true)}
    $('.rp-dialogue-close',modal).focus();
  };
  saveBtn.onclick=async()=>{
    if(!model||busy||!model.source)return;
    const token=window.RexPromptGithubAuth.getToken();
    if(!token){syncAuth();tokenInput.focus();message('Enter a GitHub token for this browser tab before saving.',true);return}
    let result;try{result=changes();if(!result.changed)return;compile(result.draft)}catch(err){message(err.message,true);return}
    const live=getContext();if(live.scene?.id!==model.id){message('The selected page changed. Reopen this editor before saving.',true);return}
    busy=true;saveBtn.disabled=true;message('Saving to canonical GitHub page source…');
    try{
      const sha=await saveToGithub(model.source,model.scene,result.draft,token);
      await onSaved(result.draft);
      model.scene=clone(result.draft);model.rows=initialRows(model.scene);
      render();message('Saved in GitHub commit '+sha.slice(0,10)+'. GitHub Pages may need a moment to publish the update.');
    }catch(err){message('Save failed: '+err.message,true)}finally{busy=false;previewStatusAfterSave();}
  };
  function previewStatusAfterSave(){
    if(!model)return;
    try{saveBtn.disabled=!changes().changed||!model.source}catch{saveBtn.disabled=true}
  }
}
window.RexPromptDialogueEditor=Object.freeze({mount,findRecord,inferPanel,draftPage});
})();
