#!/usr/bin/env node
'use strict';
// Series loaders are public production entry points, not a second registry.
// Reject retired cover-only selectors and incomplete or stale series identities.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const ROOT=path.resolve(__dirname,'..');
const json=p=>JSON.parse(fs.readFileSync(path.join(ROOT,p),'utf8'));
const shows=json('data/shows.json'),registry=json('docs/loaders/series-index.json');
assert.equal(registry.schemaVersion,1);
assert.equal(shows.some(s=>s.unitLabel==='COVER'),false,'Cover-only selector reintroduced');
const activeIds=new Set(shows.map(s=>s.id)),seriesIds=new Set(shows.map(s=>s.seriesId));
const profiles=new Map(),linked=new Set();
for(const p of registry.profiles){
  assert(p.seriesId&&seriesIds.has(p.seriesId),'Loader lacks canonical seriesId: '+p.id);
  assert(!profiles.has(p.seriesId),'Duplicate loader for series: '+p.seriesId);
  profiles.set(p.seriesId,p);
  const live=shows.filter(s=>s.seriesId===p.seriesId).map(s=>s.id);
  assert.deepEqual(p.showIds,live,'Stale or missing show IDs in loader '+p.seriesId);
  for(const id of p.showIds){
    assert(activeIds.has(id),'Loader links to retired selector '+id);
    assert(!linked.has(id),'Configuration appears under multiple series loaders: '+id);
    linked.add(id);
  }
  const full=path.resolve(ROOT,p.path);
  assert(full.startsWith(ROOT+path.sep)&&fs.existsSync(full),'Missing series loader '+p.path);
  const doc=fs.readFileSync(full,'utf8');
  const hit=doc.match(/Verified candidate show IDs:\s*([^\n]+)\./);
  assert(hit,'Loader missing exact registered show list: '+p.path);
  const listed=Array.from(hit[1].matchAll(/`([^`]+)`/g),m=>m[1]);
  assert.deepEqual(listed,p.showIds,'Loader text does not match current active registry: '+p.path);
}
assert.equal(profiles.size,seriesIds.size,'Every distinct series needs one loader');
assert.equal(linked.size,shows.length,'Loader registry must cover every active production configuration');
const separate=profiles.get('rex-fleet-full-performance'),regular=profiles.get('rex-fleet');
assert(separate&&regular&&separate.id!==regular.id,'Full Performance is a distinct series');
assert(separate.showIds.every(id=>!regular.showIds.includes(id)),'Full Performance and Rex Fleet IDs must not overlap');
console.log('PASS: '+profiles.size+' series loaders contain all '+linked.size+' live configurations, with no cover shelf, no stale selectors, and separate Full Performance identity');
