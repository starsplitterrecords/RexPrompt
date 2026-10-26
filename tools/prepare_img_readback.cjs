#!/usr/bin/env node
'use strict';
// Exact approved-image export for GitHub Actions artifacts. Never alters pixels.
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const args={};
for(let i=2;i<process.argv.length;i++){
  const key=process.argv[i]; if(!/^--(series|issue|recipe|out|manifest)$/.test(key))throw Error('Unknown argument: '+key);
  args[key.slice(2)]=process.argv[++i]; if(!args[key.slice(2)])throw Error('Missing value for '+key);
}
for(const name of ['series','issue','recipe'])if(!args[name])throw Error('Missing --'+name);
const root=path.resolve('production/drafts');
const manifestFile=path.resolve(args.manifest||'production/drafts/manifest.json');
const manifest=JSON.parse(fs.readFileSync(manifestFile,'utf8'));
const key=[args.series,args.issue,args.recipe].join('::');
const entry=manifest.drafts?.[key];
if(!entry)throw Error('Approved draft not found in manifest: '+key);
if(entry.status!=='approved-production-draft')throw Error('Draft not approved: '+key);
if(entry.seriesId!==args.series||entry.issueId!==args.issue||entry.recipeId!==args.recipe)throw Error('Manifest identity mismatch: '+key);
if(typeof entry.image!=='string'||!entry.image.startsWith('production/drafts/'))throw Error('Unsafe draft path');
const source=path.resolve(entry.image);
if(!source.startsWith(root+path.sep)||path.relative(root,source).startsWith('..'))throw Error('Source escapes production/drafts');
if(!fs.statSync(source).isFile())throw Error('Source is not a regular file');
if(!fs.realpathSync(source).startsWith(fs.realpathSync(root)+path.sep))throw Error('Source symlink escapes production/drafts');
const bytes=fs.readFileSync(source);
const head=bytes.subarray(0,16);
const mime=head.subarray(0,8).equals(Buffer.from('89504e470d0a1a0a','hex'))?'image/png':
  head.subarray(0,3).equals(Buffer.from('ffd8ff','hex'))?'image/jpeg':
  head.toString('ascii',0,4)==='RIFF'&&head.toString('ascii',8,12)==='WEBP'?'image/webp':null;
if(!mime||mime!==entry.mimeType)throw Error('Image signature/MIME mismatch: '+key);
const sha256=crypto.createHash('sha256').update(bytes).digest('hex');
if(entry.sha256&&sha256.toLowerCase()!==entry.sha256.toLowerCase())throw Error('Draft checksum mismatch: '+key);
const out=path.resolve(args.out||'img-readback');
fs.mkdirSync(out,{recursive:true});
const filename=path.basename(source),target=path.join(out,filename);
fs.writeFileSync(target,bytes,{flag:'w'});
if(!fs.readFileSync(target).equals(bytes))throw Error('Readback copy differs from original');
const result={schemaVersion:1,identity:key,seriesId:args.series,issueId:args.issue,recipeId:args.recipe,source:entry.image,filename,byteLength:bytes.length,mimeType:mime,sha256,
  gitBlobSha:crypto.createHash('sha1').update(Buffer.concat([Buffer.from('blob '+bytes.length+'\0'),bytes])).digest('hex'),
  note:'Exact image binary; inspect actual pixels before continuity use'};
fs.writeFileSync(path.join(out,'readback.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result,null,2));
