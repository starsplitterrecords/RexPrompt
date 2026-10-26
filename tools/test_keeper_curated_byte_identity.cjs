#!/usr/bin/env node
'use strict';
// Read-only recovery test: explicitly approved identity refs imported from
// curated visual packs must retain the exact original source image bytes.
// Never infer approval for unregistered candidates from this test.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const root=path.resolve(__dirname,'..');
const load=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const manifest=Object.values(load('production/references/reference-keeper-manifest.json').references);
const packs=[
 'production/references/echoes-forgotten-war/visual-reference-pack.json',
 'production/references/division-threshold/visual-reference-pack.json',
 'production/references/stardust-station/visual-reference-pack.json'
];
const digest=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
let examined=0; const failures=[];
for(const p of packs){
 const pack=load(p);
 const approved=(pack.references||[]).filter(x=>
   x.type==='approved-current-production-reference'&&
   x.scope?.includes('character-identity')&&
   x.image?.startsWith('production/references/')&&
   !x.image.includes('/keeper/')
 );
 const keeper=manifest.filter(x=>x.seriesId===pack.seriesId&&x.type==='character');
 for(const ref of approved){
   examined++;
   try{
     const source=digest(ref.image);
     const matches=keeper.filter(k=>digest(k.image)===source);
     if(matches.length!==1)failures.push(p+': '+ref.id+' matches '+matches.length+' Keeper entries (expected one exact-byte match)');
   }catch(e){failures.push(p+': '+ref.id+' '+e.message)}
 }
}
assert(examined>=20,'Curated identity source coverage unexpectedly reduced below 20');
if(failures.length){
 for(const f of failures)console.error('RECOVERY_MISMATCH '+f);
 process.exitCode=1;
}else console.log('Keeper curated identity references verified byte-for-byte: '+examined);
