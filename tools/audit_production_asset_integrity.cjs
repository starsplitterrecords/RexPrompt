#!/usr/bin/env node
'use strict';
// Read-only integrity scan of canonical approved-production drafts and Keeper assets.
// Does not approve images or substitute for visual continuity / lettering review.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),strict=process.argv.includes('--strict');
const draftFile='production/drafts/manifest.json';
const keeperFile='production/references/reference-keeper-manifest.json';
const load=file=>JSON.parse(fs.readFileSync(path.join(root,file),'utf8'));
const errors=[],warnings=[],rows=[],seenPaths=new Map();
const good={drafts:0,references:0},totals={drafts:0,references:0};
const add=(kind,key,image,mime,expectedPrefix)=>{
  const label=kind+': '+key;
  if(typeof image!=='string'||!image.startsWith(expectedPrefix+'/')||image.includes('\\')||image.includes('\0')){
    errors.push(label+' unsafe or unexpected image path: '+String(image));return;
  }
  const resolved=path.resolve(root,image);
  if(!resolved.startsWith(root+path.sep)||image.split('/').includes('..')){
    errors.push(label+' path escapes repository');return;
  }
  const previous=seenPaths.get(image);
  if(previous&&previous!==label)errors.push(label+' reuses image path belonging to '+previous);
  seenPaths.set(image,label);
  if(!fs.existsSync(resolved)){errors.push(label+' missing image '+image);return;}
  if(!fs.statSync(resolved).isFile()){errors.push(label+' image is not a file '+image);return;}
  const stat=fs.statSync(resolved);
  if(stat.size<24){errors.push(label+' image too short '+image);return;}
  const fd=fs.openSync(resolved,'r'),head=Buffer.alloc(32);
  try{fs.readSync(fd,head,0,32,0)}finally{fs.closeSync(fd)}
  let dimensions=null,valid=false;
  const ext=path.extname(image).toLowerCase();
  if(mime==='image/png'&&ext==='.png'){
    valid=head.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10]))&&head.toString('ascii',12,16)==='IHDR';
    if(valid){const w=head.readUInt32BE(16),h=head.readUInt32BE(20);valid=w>0&&h>0;dimensions=[w,h];}
  }else if(mime==='image/jpeg'&&['.jpg','.jpeg'].includes(ext)){
    valid=head[0]===255&&head[1]===216&&head[2]===255;
  }else if(mime==='image/webp'&&ext==='.webp'){
    valid=head.toString('ascii',0,4)==='RIFF'&&head.toString('ascii',8,12)==='WEBP';
  }else{errors.push(label+' MIME / file extension mismatch '+mime+' '+ext);return;}
  if(!valid){errors.push(label+' invalid file signature/header '+image);return;}
  good[kind]++;
  rows.push({kind,key,image,bytes:stat.size,dimensions});
};
const draft=load(draftFile),keeper=load(keeperFile);
assert.equal(draft.schemaVersion,1,'Draft manifest schema changed');
assert.equal(keeper.schemaVersion,1,'Keeper manifest schema changed');
assert(draft.drafts&&typeof draft.drafts==='object');
assert(keeper.references&&typeof keeper.references==='object');
for(const [key,item] of Object.entries(draft.drafts)){
  totals.drafts++;
  if(key!==[item.seriesId,item.issueId,item.recipeId].join('::'))errors.push('draft key/identity mismatch: '+key);
  if(item.status!=='approved-production-draft')errors.push('draft unexpected status: '+key);
  add('drafts',key,item.image,item.mimeType,['production','drafts',item.seriesId,item.issueId].join('/'));
}
for(const [key,item] of Object.entries(keeper.references)){
  totals.references++;
  if(item.id!==key)errors.push('keeper id/key mismatch: '+key);
  if(!['character','setting','vehicle','item'].includes(item.type))errors.push('keeper unsupported type: '+key);
  add('references',key,item.image,item.mimeType,['production','references',item.seriesId,'keeper',item.type].join('/'));
}
const counts={};
for(const [key,item] of Object.entries(draft.drafts)){
  const s=item.seriesId,issue=item.issueId;
  if(!counts[s])counts[s]={drafts:0,issues:{}};
  counts[s].drafts++;
  counts[s].issues[issue]=(counts[s].issues[issue]||0)+1;
}
const referenceCounts={};
for(const item of Object.values(keeper.references)){
 const s=item.seriesId;
 if(!referenceCounts[s])referenceCounts[s]={total:0,types:{}};
 referenceCounts[s].total++;
 referenceCounts[s].types[item.type]=(referenceCounts[s].types[item.type]||0)+1;
}
console.log('PRODUCTION ASSET INVENTORY — read-only');
console.log('Drafts indexed: '+totals.drafts+'; signatures verified: '+good.drafts);
console.log('Keeper references indexed: '+totals.references+'; signatures verified: '+good.references);
console.log('Approved drafts by series and issue: '+JSON.stringify(counts));
console.log('Keeper references by series and type: '+JSON.stringify(referenceCounts));
for(const item of warnings)console.log('WARN '+item);
for(const item of errors)console.error('ERROR '+item);
console.log('Integrity problems: '+errors.length);
console.log('NOT TESTED: artistic continuity, exact lettering, narrative correctness, full-resolution quality, mastering, or user approval.');
if(errors.length&&(strict||process.env.CI))process.exitCode=1;
