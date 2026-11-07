'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs');
const {audit,masterStandard}=require('../production-coverage-core.js');
const key=(id)=>'test-series::issue-01::'+id;
const drafts=Object.fromEntries(['P01','P02','P03'].map(id=>[key(id),{status:'approved-production-draft',image:id+'.png'}]));
const facts={[key('P01')]:{width:2400,height:3840},[key('P02')]:{width:1024,height:1536}};
const sample=audit({seriesId:'test-series',issueId:'issue-01',
 units:[{recipeId:'P01'},{recipeId:'P02'},{recipeId:'P03'},{recipeId:'P04',released:true},{recipeId:'P05'}],drafts,facts});
assert.equal(sample.total,5);assert.equal(sample.covered,4);assert.equal(sample.missing,1);
assert.equal(sample.sizeCorrect,1);assert.equal(sample.sizeWrong,1);assert.equal(sample.sizeUnverified,2);
assert.equal(sample.allImages,false);assert.equal(sample.allSizesCorrect,false);
assert.equal(sample.findings.find(x=>x.recipeId==='P02').required.width,2400);
assert.equal(masterStandard('rex-fleet','cover').width,1800);
assert.equal(masterStandard('vikings-2026','cover').width,2400);
const cover=audit({seriesId:'rex-fleet',issueId:'i01',units:[{recipeId:'RF_I01_COVER',assetKind:'cover'}],
 drafts:{'rex-fleet::i01::RF_I01_COVER':{status:'approved-production-draft',image:'cover.png'}},
 facts:{'rex-fleet::i01::RF_I01_COVER':{width:1800,height:2700}}});
assert.equal(cover.allSizesCorrect,true);
const released=audit({seriesId:'rex-fleet',issueId:'i01',units:[{recipeId:'P01',released:true}],publishedAll:true});
assert.equal(released.allImages,true);
assert.equal(released.allSizesCorrect,false,'A published link is not native source-size evidence');
assert.equal(released.sizeUnverified,1);
const actualDrafts=JSON.parse(fs.readFileSync('production/drafts/manifest.json','utf8')).drafts;
const actualFacts=JSON.parse(fs.readFileSync('production/portfolio-source-quality.json','utf8')).images;
const actual=audit({seriesId:'rex-fleet',issueId:'rex-fleet-i01',
 units:[{recipeId:'RF_I01_P18'},{recipeId:'RF_I01_P01'}],
 drafts:actualDrafts,facts:actualFacts});
assert.equal(actual.sizeCorrect,1);
assert.equal(actual.sizeWrong,1);
assert.equal(actual.findings[1].actual.width,1024);
console.log('PASS production image coverage: correct, wrong, absent, released-only unverified, source snapshot and cover policies');
