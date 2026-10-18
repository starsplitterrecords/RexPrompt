#!/usr/bin/env node
'use strict';
// Inspection-only: compact, repeatable report of page context entering the chef.
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const root=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8');
const json=p=>JSON.parse(read(p)),shows=json('data/shows.json');
const asset="data/shows/azure-reach-s1/";
for(let n=2;n<=6;n++){
  const id='azure-reach-s1-e0'+n,show=shows.find(x=>x.id===id);if(!show)throw Error('Missing '+id);
  let scenes=[];
  for(const o of show.sceneOverlays||[]){
    let value;
    if(o.encoding==="gzip-base64")value=JSON.parse(zlib.gunzipSync(Buffer.from(read(asset+o.file).trim(),'base64')).toString('utf8'));
    else value=json(asset+o.file);
    if(!Array.isArray(value))value=value.pages||[];
    if(o.mergeById){const patches=new Map(value.map(x=>[x.id,x]));scenes=scenes.map(s=>({...s,...(patches.get(s.id)||{})}));}
    else scenes.push(...value);
  }
  console.log("ISSUE "+n+" ALL "+scenes.length);
  const counts={full:0,cast:0,summary:0,settingText:0,settingRef:0,directionInline:0,region:0,factions:0};
  for(const p of scenes){
    const ds=p.directionInline||[];
    const flags=[p.settingText?'setText':p.setting?'setRef':'noSet',p.regionText?'regText':p.region?'regRef':'noReg',p.charactersInline?.length?'castInline'+p.charactersInline.length:p.characters?.length?'charRef'+p.characters.length:'noCast',ds.length?'dirInline'+ds.length:p.direction?.length?'dirRef'+p.direction.length:'noDir',p.factions?.length?'faction'+p.factions.length:''];
    counts.full++;counts.cast+=p.charactersInline?.length||p.characters?.length||0;counts.summary+=(p.summary||'').length;counts.settingText+=(p.settingText||'').length;if(p.setting)counts.settingRef++;counts.directionInline+=ds.length;counts.region+=Number(!!p.region||!!p.regionText);counts.factions+=p.factions?.length||0;
    const dirs=ds.map(d=>String(d.text||d).slice(0,120)).join(' | ');
    console.log([p.id,p.pageTitle||'',p.panelPlan?.length||0,p.dialogueInline?.length||0,flags.join(','),'summary='+String(p.summary||'').slice(0,95),'directionKeys='+JSON.stringify(p.direction||[]),'location='+String(p.setting||''),'directions='+dirs.slice(0,80),'panel='+String(p.panelPlan?.[0]?.text||p.panelPlan?.[0]?.action||p.panelPlan?.[0]||'').slice(0,85)].join(' ~ '));
  }
  console.log("TOTALS "+id+" "+JSON.stringify(counts));
}
