(()=>{
'use strict';
const R='starsplitterrecords',DRAFTS='production/drafts/manifest.json',VISIONS='StarSplitterVisions';
let busy=false;
const byId=id=>document.getElementById(id);
const pad=n=>String(n).padStart(2,'0');
const pad3=n=>String(n).padStart(3,'0');
const namePart=s=>String(s).toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
const api=(repo,path)=>'https://api.github.com/repos/'+R+'/'+repo+'/'+path;
function report(s){byId('issuePackageStatus').textContent=s}
function selection(){const a=byId('showSel'),b=byId('issueSel'),c=byId('sceneSel');return {seriesId:a.value,issueId:b.value,seriesName:a.selectedOptions[0]?.textContent||a.value,issueLabel:b.selectedOptions[0]?.textContent||b.value,recipeIds:[...c.options].map(x=>(x.dataset.recipeId||x.dataset.visualBaseLabel||x.textContent).split(' - ')[0].replace(/\s+\[(DRAFT|CANON)\]/g,'').trim())}}
function issueNo(sel){const m=sel.issueLabel.match(/Issue\s*0*(\d+)/i)||sel.issueId.match(/(?:e|issue-)(\d+)$/i);if(!m)throw Error('Cannot determine issue number.');return Number(m[1])}
function slug(sel){return namePart(sel.seriesId)+'-issue-'+pad(issueNo(sel))}
function bytesToB64(bytes){let s='';for(let i=0;i<bytes.length;i+=0x8000)s+=String.fromCharCode(...bytes.subarray(i,i+0x8000));return btoa(s)}
function b64ToBytes(s){const t=atob(s.replace(/\s/g,''));return Uint8Array.from(t,c=>c.charCodeAt(0))}
async function request(url,{token,method='GET',body,allow404=false}={}){const r=await fetch(url,{cache:'no-store',method,headers:{Accept:'application/vnd.github+json',...(token?{Authorization:'Bearer '+token,'X-GitHub-Api-Version':'2022-11-28'}:{}),...(body?{'Content-Type':'application/json'}:{})},body:body?JSON.stringify(body):undefined});if(allow404&&r.status===404)return null;if(!r.ok){let msg='HTTP '+r.status;try{msg=(await r.json()).message||msg}catch{}throw Error(msg)}return r.json()}
async function content(repo,path,token){const x=await request(api(repo,'contents/'+path+'?ref=main'),{token,allow404:true});return x?JSON.parse(new TextDecoder().decode(b64ToBytes(x.content))):null}
async function getManifest(){const r=await fetch(DRAFTS+'?v='+Date.now(),{cache:'no-store'});if(!r.ok)throw Error('Could not read draft manifest');return r.json()}
async function prepare(){const sel=selection(),manifest=await getManifest();if(!sel.recipeIds.length)throw Error('Issue has no production pages');const pages=sel.recipeIds.map((recipeId,i)=>({recipeId,page:i+1,entry:manifest.drafts?.[[sel.seriesId,sel.issueId,recipeId].join('::')]}));const approved=pages.filter(p=>p.entry?.status==='approved-production-draft'&&p.entry.image);if(!approved.length)throw Error('There are no approved draft images for this issue');return {sel,pages,approved,missing:pages.filter(p=>!approved.includes(p))}}
async function downloadImages(pages){const result=[];for(const p of pages){report('Reading page '+p.page+' of '+pages.length+'…');const url='https://raw.githubusercontent.com/'+R+'/RexPrompt/main/'+p.entry.image;let response=await fetch(url,{cache:'no-store'});if(!response.ok)throw Error('Cannot retrieve '+p.recipeId+' ('+response.status+')');const bytes=new Uint8Array(await response.arrayBuffer());const type=p.entry.mimeType||({'png':'image/png','jpg':'image/jpeg','webp':'image/webp'})[p.entry.image.split('.').pop()]||'image/png';result.push({...p,bytes,type,ext:type==='image/jpeg'?'jpg':type==='image/webp'?'webp':'png'})}return result}

async function jpeg(bytes,type){const bitmap=await createImageBitmap(new Blob([bytes],{type}));try{const canvas=document.createElement('canvas');canvas.width=bitmap.width;canvas.height=bitmap.height;const ctx=canvas.getContext('2d');ctx.fillStyle='white';ctx.fillRect(0,0,canvas.width,canvas.height);ctx.drawImage(bitmap,0,0);const b=await new Promise((res,rej)=>canvas.toBlob(x=>x?res(x):rej(Error('JPEG conversion failed')),'image/jpeg',.94));return {bytes:new Uint8Array(await b.arrayBuffer()),width:bitmap.width,height:bitmap.height}}finally{bitmap.close()}}
const utf8=s=>new TextEncoder().encode(s);
function concatenate(parts){const size=parts.reduce((n,p)=>n+p.length,0),result=new Uint8Array(size);let at=0;for(const part of parts){result.set(part,at);at+=part.length}return result}
function makePdf(images){
  const parts=[utf8('%PDF-1.4\n%\xE2\xE3\xCF\xD3\n')],offsets=[0],kids=[],count=2+images.length*3;
  let position=parts[0].length;
  function add(data){parts.push(data);position+=data.length}
  function object(id,body){offsets[id]=position;add(utf8(id+' 0 obj\n'));add(body instanceof Uint8Array?body:utf8(body));add(utf8('\nendobj\n'))}
  object(1,'<< /Type /Catalog /Pages 2 0 R >>');
  for(let i=0;i<images.length;i++)kids.push((3+i*3)+' 0 R');
  object(2,'<< /Type /Pages /Kids ['+kids.join(' ')+'] /Count '+images.length+' >>');
  for(let i=0;i<images.length;i++){
    const im=images[i],pageId=3+i*3,imgId=pageId+1,contentId=pageId+2;
    const w=+(im.jpg.width*72/300).toFixed(3),h=+(im.jpg.height*72/300).toFixed(3);
    object(pageId,'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 '+w+' '+h+'] /Resources << /XObject << /Im0 '+imgId+' 0 R >> >> /Contents '+contentId+' 0 R >>');
    object(imgId,concatenate([utf8('<< /Type /XObject /Subtype /Image /Width '+im.jpg.width+' /Height '+im.jpg.height+' /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length '+im.jpg.bytes.length+' >>\nstream\n'),im.jpg.bytes,utf8('\nendstream')]));
    const commands=utf8('q\n'+w+' 0 0 '+h+' 0 0 cm\n/Im0 Do\nQ\n');
    object(contentId,concatenate([utf8('<< /Length '+commands.length+' >>\nstream\n'),commands,utf8('endstream')]));
  }
  const xref=position;add(utf8('xref\n0 '+(count+1)+'\n0000000000 65535 f \n'));
  for(let i=1;i<=count;i++)add(utf8(String(offsets[i]).padStart(10,'0')+' 00000 n \n'));
  add(utf8('trailer\n<< /Size '+(count+1)+' /Root 1 0 R >>\nstartxref\n'+xref+'\n%%EOF\n'));
  return concatenate(parts)
}
async function createPdf(images){const converted=[];for(const im of images){report('Compiling PDF page '+im.page+' of '+images.length+'…');const jpg=await jpeg(im.bytes,im.type);converted.push({...im,jpg})}return {pdf:makePdf(converted),converted}}
const crcTable=Array.from({length:256},(_,i)=>{let c=i;for(let j=0;j<8;j++)c=c&1?(0xEDB88320^(c>>>1)):(c>>>1);return c>>>0});
function crc32(bytes){let c=0xFFFFFFFF;for(const b of bytes)c=crcTable[(c^b)&255]^(c>>>8);return (c^0xFFFFFFFF)>>>0}
function u16(d,v,o){d.setUint16(o,v,true)}
function u32(d,v,o){d.setUint32(o,v>>>0,true)}
function makeZip(files){const chunks=[],central=[];let position=0;for(const f of files){const name=utf8(f.name),data=f.bytes,crc=crc32(data),local=new Uint8Array(30+name.length),lv=new DataView(local.buffer);
u32(lv,0x04034b50,0);u16(lv,20,4);u16(lv,0x0800,6);u32(lv,crc,14);u32(lv,data.length,18);u32(lv,data.length,22);u16(lv,name.length,26);local.set(name,30);
chunks.push(local,data);
const header=new Uint8Array(46+name.length),v=new DataView(header.buffer);
u32(v,0x02014b50,0);u16(v,20,4);u16(v,20,6);u16(v,0x0800,8);u32(v,crc,16);u32(v,data.length,20);u32(v,data.length,24);u16(v,name.length,28);u32(v,position,42);header.set(name,46);central.push(header);position+=local.length+data.length}
const directory=concatenate(central),end=new Uint8Array(22),v=new DataView(end.buffer);u32(v,0x06054b50,0);u16(v,files.length,8);u16(v,files.length,10);u32(v,directory.length,12);u32(v,position,16);return concatenate([...chunks,directory,end])}
function download(name,bytes,mime){const u=URL.createObjectURL(new Blob([bytes],{type:mime})),a=document.createElement('a');a.href=u;a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(u),10000)}
function noteMissing(p){return p.missing.length?' ('+p.missing.length+' missing pages omitted: '+p.missing.map(x=>x.recipeId).join(', ')+')':''}
async function build(kind){const p=await prepare();const images=await downloadImages(p.approved);const {pdf}=await createPdf(images),stem=slug(p.sel);if(kind==='pdf'){download(stem+'.pdf',pdf,'application/pdf');report('PDF downloaded: '+images.length+' approved pages'+noteMissing(p));return}const files=[{name:stem+'.pdf',bytes:pdf},...images.map(im=>({name:stem+'/page-'+pad3(im.page)+'.'+im.ext,bytes:im.bytes}))];const bytes=makeZip(files);download(stem+'.zip',bytes,'application/zip');report('ZIP downloaded: '+images.length+' original images and PDF'+noteMissing(p))}
async function git(token,repo,path,options){return request(api(repo,path),{token,...options})}
async function release(){const p=await prepare();if(p.missing.length)throw Error('Release blocked. Missing approved pages: '+p.missing.map(x=>x.recipeId).join(', '));const source=await fetch('production/visual-sources.json?v='+Date.now(),{cache:'no-store'}).then(r=>r.json());const slugName=source.series?.[p.sel.seriesId]?.visionsSlug;if(!slugName)throw Error('No Visions series mapping. Set up release metadata before publishing.');
const token=sessionStorage.getItem('rexprompt.githubToken');if(!token)throw Error('Enter a GitHub token using Upload Approved Draft first. It must also have Contents read/write access to StarSplitterVisions.');
const metaPath='sites/visions/src/content/series/'+slugName+'.json',meta=await content(VISIONS,metaPath,token);if(!meta)throw Error('Visions series metadata not found: '+slugName);
const n=issueNo(p.sel),dir='issue-'+pad(n),base=slugName+'-'+dir;
const existing=(meta.releases||[]).find(r=>r.issueNumber===n&&r.publicationType==='E')||null;
const cover=existing?.cover||'/images/covers/'+base+'.jpg',coverPath='sites/visions/public'+cover,coverExists=await request(api(VISIONS,'contents/'+coverPath+'?ref=main'),{token,allow404:true});
if(!coverExists)throw Error('Release blocked: issue-specific cover missing: '+coverPath);
const action=existing?'OVERWRITE the already published issue':'Release the issue';
if(!window.confirm(action+' on PUBLIC Visions?\n\n'+p.sel.seriesName+' — '+p.sel.issueLabel+'\n'+p.pages.length+' approved pages.\n\n'+(existing?'This will REPLACE its published page images and collected PDF. Existing catalog identity and original release date will be retained.':'This will publish the pages, collected PDF, and release metadata.')+'\n\nAre you sure?'))return;
const images=await downloadImages(p.approved),{pdf,converted}=await createPdf(images);
report('Preparing canonical GitHub release…');
const ref=await git(token,VISIONS,'git/ref/heads/main'),head=ref.object.sha,commit=await git(token,VISIONS,'git/commits/'+head);
const date=new Date().toISOString().slice(0,10),fileStem=base+'.pdf';
const prev=meta.releases||[],maxSeq=Math.max(0,...prev.map(r=>Number(r.catalogSequence)||0)),maxPub=Math.max(0,...prev.filter(r=>r.publicationType==='E').map(r=>Number(r.publicationNumber)||0));
const pub=maxPub+1,releaseRecord=existing?{...existing}:{catalogId:(meta.seriesCode||slugName.toUpperCase())+'-E'+String(pub).padStart(3,'0')+'-'+new Date().getFullYear()+'-'+String(maxSeq+1).padStart(3,'0'),publicationType:'E',publicationNumber:pub,catalogSequence:maxSeq+1,issueNumber:n,title:'Issue '+pad(n),releaseType:'Collected comic issue',releaseDate:date,cover,description:'Complete collected issue.',externalLink:'/issues/'+slugName+'/'+dir+'/'+fileStem};
const pdfRuntimePath=releaseRecord.externalLink?.startsWith('/issues/')?releaseRecord.externalLink:'/issues/'+slugName+'/'+dir+'/'+fileStem;
const pdfPath='sites/visions/public'+pdfRuntimePath;
if(!existing){meta.releases=[releaseRecord,...prev];meta.currentRelease=releaseRecord.title;meta.status='active';meta.developmentStatus='Publishing';meta.homepage={...(meta.homepage||{}),issue:releaseRecord.title,cover};}
const pagePrefix='/images/pages/'+slugName+'/'+dir+'/';
meta.dailyPages=[...(meta.dailyPages||[]).filter(p=>!String(p.image||'').startsWith(pagePrefix)),...converted.map(x=>({pageNumber:x.page,releaseDate:existing?.releaseDate||date,image:pagePrefix+'page-'+pad3(x.page)+'.jpg'}))];
const entries=[];for(const im of converted){report('Staging canonical page '+im.page+' of '+converted.length+'…');const blob=await git(token,VISIONS,'git/blobs',{method:'POST',body:{content:bytesToB64(im.jpg.bytes),encoding:'base64'}});entries.push({path:'sites/visions/public/images/pages/'+slugName+'/'+dir+'/page-'+pad3(im.page)+'.jpg',mode:'100644',type:'blob',sha:blob.sha})}
for(const [path,bytes,encoding] of [[pdfPath,pdf,'base64'],[metaPath,new TextEncoder().encode(JSON.stringify(meta,null,2)+'\n'),'utf-8']]){const blob=await git(token,VISIONS,'git/blobs',{method:'POST',body:encoding==='base64'?{content:bytesToB64(bytes),encoding}:{content:new TextDecoder().decode(bytes),encoding}});entries.push({path,mode:'100644',type:'blob',sha:blob.sha})}
const tree=await git(token,VISIONS,'git/trees',{method:'POST',body:{base_tree:commit.tree.sha,tree:entries}});
const next=await git(token,VISIONS,'git/commits',{method:'POST',body:{message:(existing?'Replace published ':'Release ')+p.sel.seriesName+' '+releaseRecord.title,tree:tree.sha,parents:[head]}});
await git(token,VISIONS,'git/refs/heads/main',{method:'PATCH',body:{sha:next.sha,force:false}});
report((existing?'Overwrite committed':'Release committed')+' to Visions main: '+next.sha.slice(0,7)+'. Site deployment and public links still require verification.');}
async function run(kind){if(busy)return;busy=true;const buttons=[byId('issuePdfBtn'),byId('issueZipBtn'),byId('issueReleaseBtn')];buttons.forEach(b=>b.disabled=true);try{await (kind==='release'?release():build(kind))}catch(e){report((kind==='release'?'Release':'Export')+' failed: '+(e?.message||e))}finally{busy=false;buttons.forEach(b=>b.disabled=false)}}
function setup(){const issue=byId('issueSel');if(!issue)return;const host=issue.parentElement;const buttons=document.createElement('div');buttons.className='issue-packaging';buttons.style.cssText='display:flex;gap:8px;flex-wrap:wrap;margin:0 0 12px';buttons.innerHTML='<button type="button" id="issuePdfBtn">Download Draft PDF</button><button type="button" id="issueZipBtn">Download Issue ZIP</button><button type="button" id="issueReleaseBtn">Release Issue to Visions</button>';host.appendChild(buttons);const status=document.createElement('div');status.id='issuePackageStatus';status.className='status';status.setAttribute('role','status');host.appendChild(status);byId('issuePdfBtn').onclick=()=>run('pdf');byId('issueZipBtn').onclick=()=>run('zip');byId('issueReleaseBtn').onclick=()=>run('release')}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',setup);else setup();
})();