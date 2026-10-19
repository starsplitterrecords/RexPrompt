#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const root=path.resolve(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8'),json=p=>JSON.parse(read(p));
const shows=json('data/shows.json'),drafts=json('production/drafts/manifest.json').drafts;
const approved=new Set(Object.values(drafts).filter(d=>d.seriesId==='azure-reach'&&d.status==='approved-production-draft').map(d=>d.recipeId));
const base='data/shows/azure-reach-s1/';
for(let n=1;n<=6;n++){
 const show=shows.find(s=>s.id===(n===1?'azure-reach-s1':'azure-reach-s1-e0'+n));
 if(!show)throw Error('Missing Azure issue '+n);
 let pages=[];
 for(const overlay of show.sceneOverlays||[]){
  if(!/^encoded\/pages_e0/.test(overlay.file))continue;
  const raw=read(base+overlay.file);
  const slice=overlay.encoding==='gzip-base64'?JSON.parse(zlib.gunzipSync(Buffer.from(raw.trim(),'base64')).toString('utf8')):JSON.parse(raw);
  pages.push(...slice);
 }
 console.log('ISSUE '+n+' PAGES '+pages.length);
 for(let i=0;i<pages.length;i++){
  const p=pages[i],locked=n===1||approved.has(p.id),lines=p.dialogueInline||[];
  const panels=p.panelPlan||[];
  const words=t=>(String(t||'').trim().match(/\S+/g)||[]).length;
  const wordTotal=lines.reduce((a,d)=>a+words(d.text),0);
  const linked=lines.filter(d=>/^Panel\s+\d+$/i.test(d.subtext||'')).length;
  const badLength=lines.filter(d=>words(d.text)>19);
  const max=lines.reduce((a,d)=>Math.max(a,words(d.text)),0);
  console.log('PAGE '+p.id+' '+JSON.stringify({title:p.pageTitle,locked,panels:panels.length,lines:lines.length,words:wordTotal,max,linked,over19:badLength.length,continuityFrom:p.continuityFrom||null}));
  for(let j=0;j<lines.length;j++){const d=lines[j]; console.log('D '+p.id+' #'+j+' '+JSON.stringify({...d,words:words(d.text)}));}
  for(let j=0;j<panels.length;j++){
   const panel=panels[j];console.log('P '+p.id+' #'+(j+1)+' '+JSON.stringify({content:String(typeof panel==='string'?panel:panel.action||panel.text||panel.visual||JSON.stringify(panel)).slice(0,300),dialogueIndices:panel.dialogueIndices||null}));
  }
 }
}
