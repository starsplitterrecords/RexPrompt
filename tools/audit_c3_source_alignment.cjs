#!/usr/bin/env node
'use strict';
// Read-only source snapshots for the cross-series visual continuity audit.
// This script does not change canon or issue approvals.
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const root=path.resolve(__dirname,'..'),selected=[
 ['azure-reach','data/shows/azure-reach-s1/encoded/pages_e01_p07_p12.json.gzb64',['AZR_S1E01_P08']],
 ['azure-reach','data/shows/azure-reach-s1/encoded/pages_e01_p13_p18.json.gzb64',['AZR_S1E01_P14','AZR_S1E01_P15','AZR_S1E01_P18']],
 ['vikings-2026','data/shows/vikings-2026-s1/pages_i01_reordered.json',['VIK_S1I01_P07','VIK_S1I01_P09','VIK_S1I01_P16']],
 ['stardust-station','data/shows/stardust-station/encoded/pages_e01_p07_p12.json.gzb64',['SDS_S1E01_P08']],
 ['stardust-station','data/shows/stardust-station/encoded/pages_e01_p13_p18.json.gzb64',['SDS_S1E01_P17']],
 ['rex-fleet','data/shows/rex-fleet-s1/pages_i01.json',['RF_I01_P09','RF_I01_P15']]
];
function read(p){
 const data=fs.readFileSync(path.join(root,p),'utf8').trim();
 return JSON.parse(p.endsWith('.gzb64')?zlib.gunzipSync(Buffer.from(data,'base64')).toString('utf8'):data);
}
function asPages(data){return Array.isArray(data)?data:Array.isArray(data.pages)?data.pages:Array.isArray(data.scenes)?data.scenes:Object.values(data);}
let found=0,notFound=0,problems=0;
for(const [series,p,ids] of selected){
 try {
  const rows=asPages(read(p));
  for(const id of ids){
   const record=rows.find(x=>x?.id===id);
   if(!record){console.log('UNMAPPED '+series+' '+id+' '+p);notFound++;continue;}
   const pick={};for(const k of ['id','summary','characters','characterIds','cast','setting','region','panelCount','panelPlan','dialogueInline','dialogue','sceneDialogue','direction','pageLayout'])if(record[k]!==undefined)pick[k]=record[k];
   console.log('RECIPE '+series+' '+id+' '+JSON.stringify(pick).slice(0,6200));
   found++;
  }
 }catch(e){console.error('ERROR '+p+': '+e.message);problems++}
}
console.log('SOURCE AUDIT '+JSON.stringify({found,notFound,sourceErrors:problems}));
if(problems)process.exitCode=1;
