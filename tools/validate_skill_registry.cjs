#!/usr/bin/env node
'use strict';
const fs=require('fs'),path=require('path'),root=path.resolve(__dirname,'..');
const fail=m=>{throw Error(m)};
const registry=JSON.parse(fs.readFileSync(path.join(root,'docs/skills/registry.json'),'utf8'));
if(registry.schemaVersion!==1)fail('unexpected schema version');
const ids=new Set();
for(const s of registry.skills){
 if(!/^(img|reference-keeper|rexprompt|visions|collaboration)-[a-z0-9-]+$/.test(s.id))fail('invalid id '+s.id);
 if(ids.has(s.id))fail('duplicate id '+s.id);
 ids.add(s.id);
 if(!['stable','experimental','deprecated'].includes(s.status))fail('bad status '+s.id);
 for(const k of ['title','path','intents','nonTriggers','dependencies','applicability','requiredCapabilities','standards','outputs'])if(!(k in s))fail('missing '+k+' '+s.id);
 if(s.path!==`docs/skills/${s.id}/SKILL.md`)fail('wrong skill path '+s.id);
 if(!fs.existsSync(path.join(root,s.path)))fail('missing file '+s.path);
 if(!s.intents.length||!s.applicability.length)fail('unroutable '+s.id);
 const fixturePath=path.join(root,'docs/skills',s.id,'tests/contract.json');
 if(!fs.existsSync(fixturePath))fail('missing contract fixture '+s.id);
 const fixture=JSON.parse(fs.readFileSync(fixturePath,'utf8'));
 if(fixture.skillId!==s.id||!fixture.positiveIntentCases.length||!fixture.negativeIntentCases.length||!fixture.requiredPreconditions.length)fail('bad skill test fixture '+s.id);
 for(const std of s.standards||[])if(!fs.existsSync(path.join(root,'docs/standards',std+'.md')))fail('missing standard '+std);
}
for(const s of registry.skills)for(const d of s.dependencies||[])if(!ids.has(d))fail('unresolved dependency '+s.id+' -> '+d);
const nodes=new Map(registry.skills.map(s=>[s.id,s]));
const visited=new Set(),active=new Set();
function dfs(id){if(active.has(id))fail('dependency cycle '+id);if(visited.has(id))return;active.add(id);for(const d of nodes.get(id).dependencies)dfs(d);active.delete(id);visited.add(id)}
for(const id of ids)dfs(id);
const index=JSON.parse(fs.readFileSync(path.join(root,'docs/loaders/series-index.json'),'utf8'));
if(index.profiles.length!==24)fail('must have 24 IMG series loaders');
for(const x of index.profiles){if(!x.showIds.length)fail('empty show selector '+x.id);if(!fs.existsSync(path.join(root,x.path)))fail('missing loader '+x.path);const t=fs.readFileSync(path.join(root,x.path),'utf8');if(!t.includes('SKILLS_COMMIT_SHA')||!t.includes('production/approval-policy.json'))fail('loader contract '+x.id)}
if(!fs.existsSync(path.join(root,'docs/loaders/visions.md')))fail('missing Visions loader');
console.log('validated '+registry.skills.length+' skills, '+index.profiles.length+' IMG loaders, one Visions loader');
