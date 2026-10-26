#!/usr/bin/env node
'use strict';
// Reconcile durable approved drafts/keeper images with the original on-disk files.
// This audits existing state only: never recovers missing images or changes approvals.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const drafts=JSON.parse(fs.readFileSync('production/drafts/manifest.json','utf8')).drafts;
const refs=JSON.parse(fs.readFileSync('production/references/reference-keeper-manifest.json','utf8')).references;
const books=JSON.parse(fs.readFileSync('production/book-manifests.json','utf8')).issues;
const errors=[],warnings=[],seen=new Map(),byIssue={},bySeries={};
function safeImage(repoPath,root){
 if(typeof repoPath!=='string'||!repoPath.startsWith(root+'/')||repoPath.includes('..')||repoPath.includes('\\'))return false;
 const real=path.resolve(repoPath),base=path.resolve(root);
 return real.startsWith(base+path.sep);
}
function kind(buf){
 if(buf.length<24)return null;
 if(buf.toString('hex',0,8)==='89504e470d0a1a0a')return 'image/png';
 if(buf[0]===255&&buf[1]===216&&buf[buf.length-2]===255&&buf[buf.length-1]===217)return 'image/jpeg';
 if(buf.toString('ascii',0,4)==='RIFF'&&buf.toString('ascii',8,12)==='WEBP')return 'image/webp';
 return null;
}
function verify(id,v,mode){
 const root=mode==='draft'?'production/drafts':'production/references';
 if(!safeImage(v.image,root)){errors.push(id+': unsafe '+mode+' path');return}
 if(!fs.existsSync(v.image)||fs.lstatSync(v.image).isSymbolicLink()){errors.push(id+': binary absent or symlink');return}
 const bytes=fs.readFileSync(v.image),actual=kind(bytes);
 if(actual!==v.mimeType)errors.push(id+': MIME/signature mismatch ('+actual+' vs '+v.mimeType+')');
 if(bytes.length<24)errors.push(id+': image smaller than header');
 const x=seen.get(v.image);
 if(x&&x!==id)errors.push('Multiple manifest keys point to same active image '+v.image);
 seen.set(v.image,id);
 return bytes.length;
}
for(const [id,v] of Object.entries(drafts)){
 if(id!==[v.seriesId,v.issueId,v.recipeId].join('::')||v.status!=='approved-production-draft')errors.push(id+': invalid approval identity');
 if(!v.image?.startsWith('production/drafts/'+v.seriesId+'/'+v.issueId+'/'))errors.push(id+': wrong draft series/issue path');
 verify(id,v,'draft');
 const key=v.seriesId+'::'+v.issueId;
 byIssue[key]=(byIssue[key]||0)+1;
}
for(const [id,v] of Object.entries(refs)){
 if(id!==v.id||id!==[v.seriesId,v.type,id.split('::').at(-1)].join('::'))errors.push(id+': invalid Keeper identity');
 if(!v.image?.startsWith('production/references/'+v.seriesId+'/keeper/'+v.type+'/'))errors.push(id+': wrong Keeper series/type path');
 verify(id,v,'reference');
 bySeries[v.seriesId]=(bySeries[v.seriesId]||0)+1;
}
function walk(root){
 if(!fs.existsSync(root))return [];
 const files=[];
 for(const dirent of fs.readdirSync(root,{withFileTypes:true})){
  const p=path.join(root,dirent.name);
  if(dirent.isDirectory())files.push(...walk(p));
  else if(dirent.isFile())files.push(p.replace(/\\/g,'/'));
 }
 return files;
}
const binaryPaths=walk('production/drafts').filter(x=>/\.(png|jpe?g|webp)$/i.test(x));
const orphans=binaryPaths.filter(x=>!seen.has(x));
for(const x of orphans)errors.push('Unindexed approved-draft binary '+x);
const bookGaps={};
for(const [id,book] of Object.entries(books)){
 const expected=book.units||[];
 if(id!==[book.seriesId,book.issueId].join('::')||new Set(expected).size!==expected.length)errors.push(id+': invalid book unit inventory');
 const missing=expected.filter(x=>!drafts[[book.seriesId,book.issueId,x].join('::')]);
 bookGaps[id]={expected:expected.length,approved:expected.length-missing.length,missing};
 if(missing.length)warnings.push(id+': '+missing.length+' book units missing approved images');
}
const report={approvedDraftEntries:Object.keys(drafts).length,storedDraftFiles:binaryPaths.length,keeperEntries:Object.keys(refs).length,byIssue,keeperBySeries:bySeries,bookGaps,unindexedBinaryPaths:orphans,errors,warnings};
console.log(JSON.stringify(report,null,2));
if(errors.length)process.exitCode=1;