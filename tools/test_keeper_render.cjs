#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),src=fs.readFileSync(path.join(root,'reference-keeper.js'),'utf8'),K=require('../reference-keeper-contract.js');
const start=src.indexOf('function render(){'),stop=src.indexOf('\n// Keep all changes',start);
assert(start>=0&&stop>start);
const manifest=JSON.parse(fs.readFileSync(path.join(root,'production/references/reference-keeper-manifest.json'))),C={owner:'starsplitterrecords',repo:'RexPrompt',branch:'main',types:K.TYPES};
class E{constructor(){this.children=[];this.parts=new Map();this.dataset={};this.value='';this.textContent='';this.isConnected=true}
append(v){this.children.push(v)}
setAttribute(k,v){this[k]=v}
querySelector(k){if(k==='.cancel-delete')return null;if(!this.parts.has(k))this.parts.set(k,new E);return this.parts.get(k)}}
const UI={series:new E,view:new E,search:new E,count:new E,groups:new E},S={manifest,ui:UI};
const render=vm.runInNewContext(src.slice(start,stop)+'\nrender',{
 S,C,K,document:{createElement:()=>new E},
 title:v=>v[0].toUpperCase()+v.slice(1),imgUrl:e=>'https://raw.githubusercontent.com/starsplitterrecords/RexPrompt/main/'+e.image+'?v='+encodeURIComponent(e.updatedAt),
 token:()=>false,askToken(){},openLightbox(){},replace(){},remove(){}
});
const cards=()=>UI.groups.children.flatMap(x=>x.querySelector('.keeper-grid').children);
const ids=[...new Set(Object.values(manifest.references).map(x=>x.seriesId))];let checked=0;
for(const id of ids){
 for(const type of ['all',...K.TYPES]){
  UI.series.value=id;UI.view.value=type;UI.search.value='';UI.groups.children=[];render();
  const expected=Object.values(manifest.references).filter(x=>x.seriesId===id&&(type==='all'||x.type===type));
  assert.equal(cards().length,expected.length,id+'/'+type);
  for(const card of cards()){
    assert(card.querySelector('img').src.includes('/production/references/'+id+'/keeper/'));
    assert(card.querySelector('.keeper-name').textContent);
  }
  checked++;
 }
 const name=Object.values(manifest.references).find(x=>x.seriesId===id).name;
 UI.series.value=id;UI.view.value='all';UI.search.value=name.slice(0,3);UI.groups.children=[];render();
 assert(cards().some(c=>c.querySelector('.keeper-name').textContent===name));
}
const first=Object.values(manifest.references)[0],extra={...first,id:first.seriesId+'::'+first.type+'::portfolio-reload-test',name:'Portfolio Reload Test'};
const next=JSON.parse(JSON.stringify(manifest));next.references[extra.id]=extra;S.manifest=JSON.parse(JSON.stringify(next));
UI.series.value=first.seriesId;UI.view.value=first.type;UI.search.value='portfolio reload';UI.groups.children=[];render();
assert.equal(cards().length,1);const card=cards()[0];assert.equal(card.querySelector('.keeper-name').textContent,extra.name);
card.querySelector('img').onerror();assert(card.querySelector('.keeper-card-status').textContent.includes('unavailable'));
console.log(JSON.stringify({series:ids.length,categoryViews:checked,textSearch:ids.length,reload:true,brokenImageStatus:true}));
