#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..');
const r=JSON.parse(fs.readFileSync(path.join(root,'docs/skills/registry.json'),'utf8'));
const ids=new Set(r.skills.map(x=>x.id));
const required=['img-page-production','img-sequential-production','img-production-recovery','img-binary-readback','img-approval-persistence','img-issue-audit','img-issue-mastering','img-color-normalization','reference-keeper-ingest','reference-keeper-curation','rexprompt-development','rexprompt-data-sanitization','rexprompt-identity-normalization','visions-release','visions-chat-organization','collaboration-continuity'];
for(const id of required)assert(ids.has(id),'Missing '+id);
const index=JSON.parse(fs.readFileSync(path.join(root,'docs/loaders/series-index.json'),'utf8'));
const seen=new Set();
for(const p of index.profiles){assert(!seen.has(p.id));seen.add(p.id);const text=fs.readFileSync(path.join(root,p.path),'utf8');for(const s of ['img-page-production','img-sequential-production','img-production-recovery','img-binary-readback','production/drafts/manifest.json'])assert(text.includes(s),p.id+' missing '+s);}
assert(index.profiles.some(x=>x.id==='division-threshold'));
const dt=fs.readFileSync(path.join(root,'docs/loaders/series/division-threshold.md'),'utf8');
assert(dt.includes('no permanent special case'));
console.log('validated shared loader routing and no Division Threshold exception');
