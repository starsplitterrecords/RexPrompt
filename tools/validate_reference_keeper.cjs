#!/usr/bin/env node
'use strict';
/* Portfolio-wide read-only Keeper inventory audit. Does not promote or rewrite references. */
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const K=require('../reference-keeper-contract.js');
const ROOT=path.resolve(__dirname,'..');
const read=p=>JSON.parse(fs.readFileSync(path.join(ROOT,p),'utf8'));
const manifest=read('production/references/reference-keeper-manifest.json'),shows=read('data/shows.json');
const {errors,warnings}=K.checkManifest(manifest,shows);
const bySeries={},byCategory={},hashes=new Map();
const banned='production/references/division-threshold/assets/page-language/dt-e001-p05-production-example.jpg';
for(const [key,e] of Object.entries(manifest.references||{})){
  bySeries[e.seriesId]=(bySeries[e.seriesId]||0)+1;
  byCategory[e.type]=(byCategory[e.type]||0)+1;
  if(e.image===banned||e.seriesId==='division-threshold'&&/checkpoint.?9/i.test(e.name||''))
    errors.push('Known malformed Division Threshold Checkpoint 9 source must not be reinstated: '+key);
  const p=path.resolve(ROOT,e.image||'');
  const boundary=path.resolve(ROOT,'production/references')+path.sep;
  if(!p.startsWith(boundary)||!fs.existsSync(p)){errors.push(key+': original image unavailable');continue}
  const stat=fs.lstatSync(p);
  if(!stat.isFile()||stat.isSymbolicLink()){errors.push(key+': file is not a regular source image');continue}
  const buf=fs.readFileSync(p);
  if(buf.length>K.MAX_BYTES){errors.push(key+': source exceeds 50 MB');continue}
  const mime=K.sniff(buf);
  if(!mime||mime!==e.mimeType)errors.push(key+': original image MIME signature mismatch: '+mime+' vs '+e.mimeType);
  const digest=crypto.createHash('sha256').update(buf).digest('hex');
  const identity=e.seriesId+'::'+e.type+'::'+digest;
  if(hashes.has(identity))warnings.push('Duplicate exact bytes in same series/category: '+hashes.get(identity)+' and '+key);
  else hashes.set(identity,key);
}
const entries=Object.values(manifest.references||{});
for(const sid of new Set(entries.map(r=>r.seriesId))){
  for(const type of K.TYPES){
    const expected=entries.filter(x=>x.seriesId===sid&&x.type===type);
    const actual=K.selectEntries(manifest,{seriesId:sid,type});
    if(actual.length!==expected.length)errors.push('UI series/category filtering failed: '+sid+'/'+type);
  }
  const got=K.selectEntries(manifest,{seriesId:sid});
  if(got.length!==bySeries[sid])errors.push('UI all-categories filtering failed: '+sid);
}
const result={keeperEntries:entries.length,seriesWithEntries:Object.keys(bySeries).length,bySeries,byCategory,errors,warnings};
console.log(JSON.stringify(result,null,2));
if(errors.length)process.exitCode=1;
