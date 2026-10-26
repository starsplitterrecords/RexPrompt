'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),zlib=require('node:zlib');
const core=require('../production-dashboard-core.js'),read=(p,encoding)=>{const b=fs.readFileSync(p);return JSON.parse(encoding==='gzip-base64'?zlib.gunzipSync(Buffer.from(b.toString('utf8').replace(/\s+/g,''),'base64')).toString('utf8'):b.toString('utf8'))};
(async()=>{
 const shows=read('data/shows.json'),inventories=await core.inventory(shows,async(p,e)=>read(p,e));
 const m=core.build({shows,inventories,approvalManifest:read('production/drafts/manifest.json'),keeperManifest:read('production/references/reference-keeper-manifest.json'),bookManifest:read('production/book-manifests.json'),releasedLinks:read('production/released-links.json'),findings:read('production/dashboard-source-quality.json').findings,recovery:read('production/dashboard-recovery-candidates.json').candidates});
 assert.equal(m.summary.registryConfigurations,shows.length);
 assert(m.summary.assembledRecipeAssignments>shows.length);
 assert.equal(m.summary.approvedDraftManifestEntries,Object.keys(read('production/drafts/manifest.json').drafts).length);
 assert(m.rows.find(x=>x.issueId==='rex-fleet-i03'&&x.seriesId==='rex-fleet').unresolvedRecovery===5);
 assert(m.series.find(x=>x.id==='stardust-station'));
 console.log('PASS portfolio dashboard source truth and issue recovery validation');
})().catch(e=>{console.error(e.stack);process.exitCode=1});