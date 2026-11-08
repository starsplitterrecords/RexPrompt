#!/usr/bin/env node
'use strict';
// Enforce single authoritative production field ownership. Additional *new* page/cover
// files are permitted, but revisions of existing IDs may not be layered on top.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const manifest=JSON.parse(fs.readFileSync(path.join(root,'data/shows.json'),'utf8'));
const seen=new Set();
for(const show of manifest){
 assert(!seen.has(show.id),'Duplicate production configuration '+show.id);seen.add(show.id);
 const base=show.basePath||'data';
 const cfgPath=path.join(root,base,show.packageConfigFile||'assembler.json');
 const packageCfg=fs.existsSync(cfgPath)?JSON.parse(fs.readFileSync(cfgPath,'utf8')):{};
 const effective={...packageCfg,...show};
 assert(!(effective.dialogueOverlays||[]).length,'Dialogue replacement layer forbidden: '+show.id);
 for(const o of effective.sceneOverlays||[]){
  assert(!o.mergeById,'Field replacement overlay forbidden: '+show.id+' '+o.file);
  assert(!o.replaceEpisode&&!o.replaceEpisodes,'Episode replacement overlay forbidden: '+show.id+' '+o.file);
  assert(!o.strict,'Strict field overlay unexpectedly registered: '+show.id+' '+o.file);
 }
}
const retired=[
 /^data\/shows\/shattering\/(?:page_layouts_i\d\d|visual_cast_i\d\d)\.json$/,
 /^data\/shows\/sunforge-outlaw-s1\/editorial\/page_(?:layouts|assembly)_e\d\d\.json$/,
 /^data\/shows\/echoes-forgotten-war-s1\/editorial\/page_(?:layouts|recipe_scope)_e\d\d\.json$/,
 /^data\/shows\/backyard-rockets-s1\/editorial_(?:page_layouts|recipe_scope)_e\d\d\.json$/,
 /^data\/shows\/(?:rex-fleet-[\w-]+|rex-fleet-academy-[\w-]+|rfa-reach-resolve)\/editorial\/visual_faction_pages_i\d\d\.json$/
];
let checked=0;function walk(dir){
 for(const e of fs.readdirSync(dir,{withFileTypes:true})){
  const f=path.join(dir,e.name);if(e.isDirectory()){walk(f);continue}
  const rel=path.relative(root,f).split(path.sep).join('/');
  assert(!retired.some(re=>re.test(rel)),'Retired field overlay returned to working tree: '+rel);
  checked++;
 }
}
walk(path.join(root,'data/shows'));
console.log('PASS canonical page-source guard: '+manifest.length+' production configurations, '+checked+' show-package files, no field/dialogue replacement layers and no retired overlay fixtures.');
