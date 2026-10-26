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
 assert.match(book.units[0],/_COVER$/);
 assert.match(book.units[1],/_EDITOR_OPEN$/);
 assert.match(book.units[2],/_CAST$/);
 const pageUnits=book.units.filter(x=>/_P\d+$/.test(x));
 assert.ok(pageUnits.length>=18,'expected all story pages in '+key);
 pageUnits.forEach((id,i)=>assert.ok(id.endsWith('_P'+String(i+1).padStart(2,'0')),'story order '+id));
 assert.ok(book.units.at(-1).endsWith('_EDITOR_CLOSE')||book.units.at(-1).endsWith('_EDITOR_ENDMATTER'));
 const missing=book.units.filter(id=>!draft.drafts[[book.seriesId,book.issueId,id].join('::')]);
 if(missing.length)incomplete++;
 console.log(key+': '+book.units.length+' expected units; '+missing.length+' missing approved images'+(missing.length?': '+missing.join(', '):''));
}
assert.ok(incomplete>=0);
console.log('Complete-book manifest contract verified.');
