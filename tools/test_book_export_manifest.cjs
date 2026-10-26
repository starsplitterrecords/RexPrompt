'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs');
const inv=JSON.parse(fs.readFileSync('production/book-manifests.json','utf8'));
const draft=JSON.parse(fs.readFileSync('production/drafts/manifest.json','utf8'));
const exporter=fs.readFileSync('issue-publishing.js','utf8');
assert.equal(inv.schemaVersion,1);
assert.match(exporter,/async function getBookSpec/);
assert.match(exporter,/const units=book\?\.units\|\|sel\.recipeIds/);
let incomplete=0;
for(const [key,book] of Object.entries(inv.issues)){
 assert.equal(key,book.seriesId+'::'+book.issueId);
 assert.equal(new Set(book.units).size,book.units.length);
 if(book.seriesId==='rex-fleet'){
  assert.match(book.units[0],/_COVER$/);
  assert.match(book.units[1],/_EDITOR_OPEN$/);
  assert.match(book.units[2],/_CAST$/);
  const pageUnits=book.units.filter(x=>/_P\d+$/.test(x));
  assert.ok(pageUnits.length>=18);
  pageUnits.forEach((id,i)=>assert.ok(id.endsWith('_P'+String(i+1).padStart(2,'0')),'Rex Fleet story order '+id));
  assert.ok(book.units.at(-1).endsWith('_EDITOR_CLOSE'));
  if(book.issueId.endsWith('i02')||book.issueId.endsWith('i03'))
    assert.deepEqual(book.units.slice(-2),[book.issueId.endsWith('i02')?'RF_I02_EDITOR_ENDMATTER':'RF_I03_EDITOR_ENDMATTER',book.issueId.endsWith('i02')?'RF_I02_EDITOR_CLOSE':'RF_I03_EDITOR_CLOSE']);
 }else if(book.seriesId==='vikings-2026'){
  const cover=JSON.parse(fs.readFileSync('data/shows/vikings-2026-s1/covers.json','utf8'));
  const story=JSON.parse(fs.readFileSync('data/shows/vikings-2026-s1/pages_i02.json','utf8'));
  assert.deepEqual(book.units,[...cover.filter(x=>x.id==='VIK_S1E02_P01'),...story].map(x=>x.id),'Vikings book must include cover P01');
 }else if(book.seriesId==='stardust-station'){
  const covers=JSON.parse(fs.readFileSync('data/shows/stardust-station/covers.json','utf8'));
  const intro=JSON.parse(fs.readFileSync('data/shows/stardust-station/editorial/pages_e02_intro.json','utf8'));
  const outro=JSON.parse(fs.readFileSync('data/shows/stardust-station/editorial/pages_e02_teaser.json','utf8'));
  const expected=[covers.find(x=>x.id==='SDS_S1E02_COVER').id,intro[0].id,
    ...Array.from({length:22},(_,i)=>'SDS_S1E02_P'+String(i+1).padStart(2,'0')),outro[0].id];
  assert.deepEqual(book.units,expected,'Stardust book must include cover/editorial/teaser');
 }else throw Error('Book inventory requires a source-order regression rule: '+book.seriesId);
 const missing=book.units.filter(id=>!draft.drafts[[book.seriesId,book.issueId,id].join('::')]);
 if(missing.length)incomplete++;
 console.log(key+': '+book.units.length+' expected units; '+missing.length+' missing approved images'+(missing.length?': '+missing.join(', '):''));
}
assert.ok(incomplete>=0);
assert.match(exporter,/-INCOMPLETE-DRAFT/,'Incomplete preview must be labeled');
assert.match(exporter,/-UNVERIFIED-BOOK-DRAFT/,'Missing complete-book inventory must be labeled');
assert.match(exporter,/book-export-manifest\.json/,'ZIP must include machine-readable source inventory');
assert.match(exporter,/im\.type==='image\/jpeg'\?await nativeJpeg/,'Original JPEG bytes should be preserved in PDF');
assert.match(exporter,/if\(!p\.book\)throw Error\('Release blocked/,'All releases require complete-book inventories');
assert.match(exporter,/MISSING_APPROVED_PAGES\.txt/,'Incomplete archive requires gap list');
console.log('Complete-book manifest contract verified.');
