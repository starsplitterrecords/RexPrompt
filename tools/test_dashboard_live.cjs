#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict');
const base=(process.env.REXPROMPT_PUBLIC_URL||'https://starsplitterrecords.github.io/RexPrompt/').replace(/\/?$/,'/');
const sleep=(ms)=>new Promise(resolve=>setTimeout(resolve,ms));
async function inspect(){
 const paths=['production-dashboard.html','production-dashboard.js','production-dashboard-core.js','data/shows.json','production/dashboard-source-quality.json','production/dashboard-recovery-candidates.json'];
 const results={};
 for(const p of paths){
  const url=base+p,r=await fetch(url,{signal:AbortSignal.timeout(18000),cache:'no-store'});
  if(!r.ok)throw Error('LIVE HTTP '+r.status+' '+url);
  results[p]=await r.text();
  if(!results[p].length)throw Error('Empty deployed asset '+url);
 }
 assert.match(results['production-dashboard.html'],/Portfolio production operations/,'Expected deployed dashboard, not old config-only view');
 assert.match(results['production-dashboard.js'],/Assembling original scripts and overlays/,'Deployed client not updated');
 assert.match(results['production-dashboard-core.js'],/sourceIndex/,'Server is not serving current effective-recipe core');
 const shows=JSON.parse(results['data/shows.json']);assert(Array.isArray(shows)&&shows.length>=126);
 assert(Array.isArray(JSON.parse(results['production/dashboard-source-quality.json']).findings));
 assert(Array.isArray(JSON.parse(results['production/dashboard-recovery-candidates.json']).candidates));
 console.log('LIVE DASHBOARD STATIC VERIFIED '+JSON.stringify({url:base,configurations:shows.length,assets:paths,status:'reachable-current-evidence-files'}));
}
(async()=>{
 const retries=Number(process.env.REXPROMPT_LIVE_RETRIES||'6');
 for(let attempt=1;attempt<=retries;attempt++){
  try{await inspect();return}catch(e){console.error('Live audit attempt '+attempt+'/'+retries+': '+e.message);if(attempt===retries)throw e;await sleep(15000)}
 }
})().catch(e=>{console.error(e.stack);process.exitCode=1});