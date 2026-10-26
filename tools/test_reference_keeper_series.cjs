#!/usr/bin/env node
'use strict';
// Execute the production series resolver in a sandbox to guard the Keeper
// filter against mismatches between display names and canonical series IDs.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const src = fs.readFileSync(path.join(__dirname, '..', 'reference-keeper.js'), 'utf8');
const start = src.indexOf('function seriesFrom(shows){');
const end = src.indexOf('\nfunction setMode', start);
assert(start >= 0 && end > start, 'Keeper series resolver must be present');
const snippet = src.slice(start, end);
const K=require('../reference-keeper-contract.js');
const safe=K.safe;
const S = {manifest: {references: {
  e1: {seriesId:'echoes-forgotten-war',seriesName:'Echoes of a Forgotten War'},
  r1: {seriesId:'rex-fleet',seriesName:'Rex Fleet'},
  extra: {seriesId:'custom-registered',seriesName:'Custom Registered Name'}
}}};
const resolve = vm.runInNewContext(snippet + '\nseriesFrom', {S,safe,K});
const shows = [
  {seriesId:'echoes-forgotten-war',seriesName:'Echoes of a Forgotten War'},
  {seriesId:'rex-fleet',seriesName:'Rex Fleet'},
  {seriesId:'rex-fleet-academy-anomalies',seriesName:'Rex Fleet Academy: Anomalies of Broken Space'},
  {seriesId:'division-threshold',seriesName:'Division Threshold'},
  {seriesId:'stardust-station',seriesName:'Stardust Station'},
  {id:'vikings-2026-s1-e01',seriesName:'Vikings 2026',name:'Vikings 2026 — Issue 1'},
  {id:'backyard-rockets-s1',name:'Backyard Rockets — Season 1'}
];
const rows = resolve(shows);
const lookup = new Map(rows.map(x => [x.id,x.name]));
for (const [id,name] of [
  ['echoes-forgotten-war','Echoes of a Forgotten War'],
  ['rex-fleet','Rex Fleet'],
  ['rex-fleet-academy-anomalies','Rex Fleet Academy: Anomalies of Broken Space'],
  ['division-threshold','Division Threshold'],
  ['stardust-station','Stardust Station'],
  ['vikings-2026','Vikings 2026'],
  ['backyard-rockets','Backyard Rockets']
]) assert.equal(lookup.get(id),name,'Keeper series selection must preserve canonical id '+id);
assert.equal(lookup.has('custom-registered'),false,'Unknown manifest-only series must not appear as upload target');
assert.equal(lookup.has('echoes-of-a-forgotten-war'),false,'Display-name slug must not create a phantom Echoes series');
assert.equal(rows.filter(x=>x.id==='echoes-forgotten-war').length,1,'Only one Echoes option');
console.log('Reference Keeper canonical series ID tests passed ('+rows.length+' options).');
