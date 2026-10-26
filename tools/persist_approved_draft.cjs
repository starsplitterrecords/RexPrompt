#!/usr/bin/env node
'use strict';
// Implements the existing RexPrompt Git Data image+manifest atomic persistence contract.
// Requires an already reviewed/approved image in the active runtime. No transport service.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const env=process.env;
const required=['GITHUB_TOKEN','GITHUB_REPOSITORY','TARGET_BRANCH','SOURCE_IMAGE','SERIES_ID','ISSUE_ID','RECIPE_ID','APPROVAL_METHOD','EVALUATION_SUMMARY','REVIEWED_APPROVAL'];
for(const key of required)if(!env[key])throw Error('Required setting missing: '+key);
if(env.REVIEWED_APPROVAL!=='true')throw Error('Artwork has not passed the substantial-pass approval gate');
if(env.TARGET_BRANCH==='main'&&env.ALLOW_MAIN_WRITE!=='true')throw Error('Explicit ALLOW_MAIN_WRITE required for main');
const validId=/^[a-z0-9][a-z0-9-]*$/,recipePattern=/^[A-Za-z0-9][A-Za-z0-9_-]*$/;
for(const name of ['SERIES_ID','ISSUE_ID'])if(!validId.test(env[name]))throw Error('Invalid '+name);
if(!recipePattern.test(env.RECIPE_ID)||env.RECIPE_ID.length>128)throw Error('Invalid RECIPE_ID');
if(!/^[A-Za-z0-9_./-]+$/.test(env.TARGET_BRANCH)||env.TARGET_BRANCH.includes('..'))throw Error('Invalid TARGET_BRANCH');
if(env.GITHUB_REPOSITORY!=='starsplitterrecords/RexPrompt'&&!env.ALLOW_TEST_REPOSITORY)throw Error('Unexpected GitHub repository');
const original=fs.readFileSync(env.SOURCE_IMAGE),extension=path.extname(env.SOURCE_IMAGE).toLowerCase();
const types={'.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.webp':'image/webp'};
const mimeType=types[extension];
if(!mimeType||original.length<24||original.length>50*1024*1024)throw Error('Invalid image format or length');
const isPng=original.subarray(0,8).equals(Buffer.from('89504e470d0a1a0a','hex'));
const isJpeg=original[0]===255&&original[1]===216&&original.subarray(-2).equals(Buffer.from('ffd9','hex'));
const isWebp=original.toString('ascii',0,4)==='RIFF'&&original.toString('ascii',8,12)==='WEBP'&&original.readUInt32LE(4)===original.length-8;
if(!(isPng&&mimeType==='image/png'||isJpeg&&mimeType==='image/jpeg'||isWebp&&mimeType==='image/webp'))throw Error('Image MIME does not match actual bytes');
const imageHash=crypto.createHash('sha256').update(original).digest('hex');
const gitHash=buffer=>crypto.createHash('sha1').update('blob '+buffer.length+'\0').update(buffer).digest('hex');
const apiBase=env.GITHUB_API_URL||'https://api.github.com';
if(apiBase!=='https://api.github.com'&&!(env.ALLOW_LOCAL_TEST_API==='true'&&/^http:\/\/(127\.0\.0\.1|localhost):\d+$/.test(apiBase)))throw Error('Untrusted API endpoint');
const repo='/repos/'+env.GITHUB_REPOSITORY;
async function api(method,url,body){
 const response=await fetch(apiBase+repo+url,{
  method,headers:{'Accept':'application/vnd.github+json','Authorization':'Bearer '+env.GITHUB_TOKEN,
   'X-GitHub-Api-Version':'2022-11-28',...(body?{'Content-Type':'application/json'}:{})},
  ...(body?{body:JSON.stringify(body)}:{})});
 if(!response.ok)throw Error('GitHub '+method+' '+url+' failed: '+response.status+' '+(await response.text()).slice(0,300));
 return response.json();
}
const refPath='/git/refs/heads/'+env.TARGET_BRANCH;
const imageKey=[env.SERIES_ID,env.ISSUE_ID,env.RECIPE_ID].join('::');
function encodedGitContent(b){return {content:b.toString('base64'),encoding:'base64'}}
async function main(){
 const ref=await api('GET','/git/ref/heads/'+env.TARGET_BRANCH);
 const head=ref.object?.sha;
 if(!/^[a-f0-9]{40}$/.test(head||''))throw Error('Invalid source branch revision');
 if(env.EXPECTED_HEAD_SHA&&head!==env.EXPECTED_HEAD_SHA)throw Error('Branch head differs from expected preflight revision');
 const commit=await api('GET','/git/commits/'+head);
 const treeSha=commit.tree?.sha;
 if(!treeSha)throw Error('Cannot resolve branch tree');
 const manifestResult=await api('GET','/contents/production/drafts/manifest.json?ref='+encodeURIComponent(env.TARGET_BRANCH));
 if(manifestResult.encoding!=='base64')throw Error('Manifest response is not base64');
 const manifest=JSON.parse(Buffer.from(manifestResult.content.replace(/\s/g,''),'base64').toString('utf8'));
 if(manifest.schemaVersion!==1||!manifest.drafts||typeof manifest.drafts!=='object')throw Error('Unexpected approved draft manifest contract');
 const existing=manifest.drafts[imageKey],replacing=env.REPLACE_APPROVED==='true';
 if(existing&&existing.status!=='approved-production-draft')throw Error('Existing entry has an unexpected status');
 if(existing&&!replacing){
  if(existing.sha256===imageHash&&existing.mimeType===mimeType)console.log('Already approved content, no mutation requested');
  throw Error('Approved draft exists; explicit REPLACE_APPROVED=true required to alter active state');
 }
 const safeExt=extension==='.jpeg'?'.jpg':extension;
 const newPath='production/drafts/'+env.SERIES_ID+'/'+env.ISSUE_ID+'/'+env.RECIPE_ID.toLowerCase()+safeExt;
 if(existing&&existing.image!==newPath&& !existing.image.startsWith('production/drafts/'+env.SERIES_ID+'/'+env.ISSUE_ID+'/'))throw Error('Existing image path is unsafe to replace');
 const entry={seriesId:env.SERIES_ID,issueId:env.ISSUE_ID,recipeId:env.RECIPE_ID,status:'approved-production-draft',image:newPath,
  mimeType,sha256:imageHash,updatedAt:new Date().toISOString(),approvalMethod:env.APPROVAL_METHOD,evaluationSummary:env.EVALUATION_SUMMARY};
 const blob=await api('POST','/git/blobs',encodedGitContent(original));
 if(blob.sha!==gitHash(original))throw Error('GitHub image blob mismatch; no branch change performed');
 manifest.drafts[imageKey]=entry;
 const manifestBytes=Buffer.from(JSON.stringify(manifest,null,2)+'\n','utf8');
 const manifestBlob=await api('POST','/git/blobs',{content:manifestBytes.toString('utf8'),encoding:'utf-8'});
 if(manifestBlob.sha!==gitHash(manifestBytes))throw Error('GitHub manifest blob mismatch; no branch change performed');
 const entries=[{path:newPath,mode:'100644',type:'blob',sha:blob.sha},
  {path:'production/drafts/manifest.json',mode:'100644',type:'blob',sha:manifestBlob.sha}];
 if(existing&&existing.image!==newPath)entries.push({path:existing.image,mode:'100644',type:'blob',sha:null});
 const tree=await api('POST','/git/trees',{base_tree:treeSha,tree:entries});
 const next=await api('POST','/git/commits',{message:'Persist reviewed approved production draft '+imageKey,tree:tree.sha,parents:[head]});
 // One ref update is the atomic visibility boundary; force:false prevents racing branch updates.
 await api('PATCH',refPath,{sha:next.sha,force:false});
 const newRef=await api('GET','/git/ref/heads/'+env.TARGET_BRANCH);
 if(newRef.object?.sha!==next.sha)throw Error('Committed ref advanced unexpectedly; inspect branch history');
 const committedManifest=await api('GET','/contents/production/drafts/manifest.json?ref='+encodeURIComponent(next.sha));
 const check=JSON.parse(Buffer.from(committedManifest.content.replace(/\s/g,''),'base64').toString('utf8'));
 if(check.drafts?.[imageKey]?.sha256!==imageHash||check.drafts?.[imageKey]?.image!==newPath)throw Error('Committed approved manifest did not verify');
 const committedImage=await api('GET','/git/blobs/'+blob.sha);
 if(committedImage.encoding!=='base64'||!Buffer.from(committedImage.content.replace(/\s/g,''),'base64').equals(original))throw Error('Read-after-write binary verification failed');
 console.log(JSON.stringify({status:'persisted-and-readback-verified',key:imageKey,revision:next.sha,path:newPath,
  mimeType,sha256:imageHash,gitBlobSha:blob.sha,originalBytes:original.length,sourceBytesUnchanged:true},null,2));
}
main().catch(e=>{console.error('Persistence failed: '+e.message);process.exitCode=1});
