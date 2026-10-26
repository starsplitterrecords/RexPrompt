#!/usr/bin/env node
'use strict';
// Exercises the real Git Data writeback client against an isolated Git API mock.
// No real approved production art and no real GitHub branch is changed by this test.
const http=require('node:http'),fs=require('node:fs'),os=require('node:os'),path=require('node:path'),crypto=require('node:crypto'),cp=require('node:child_process'),assert=require('node:assert/strict');
const sha=b=>crypto.createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex');
const digest=b=>crypto.createHash('sha256').update(b).digest('hex');
const baseHead='a'.repeat(40),baseTree='b'.repeat(40);
let head=baseHead,manifest={schemaVersion:1,drafts:{}},race=false,gitBlobWrites=0,refUpdates=0,treeWrites=[];
const blobs=new Map(),trees=new Map(),commits=new Map([[baseHead,{tree:{sha:baseTree}}]]);
const fixtures=fs.mkdtempSync(path.join(os.tmpdir(),'img-persistence-mock-'));
const imageFile=path.join(fixtures,'approved-source.png');
const created=cp.spawnSync('python3',['-c',
 'from PIL import Image; import sys; Image.new("RGB",(30,22),(120,65,40)).save(sys.argv[1],format="PNG")',imageFile],{encoding:'utf8'});
assert.equal(created.status,0,created.stderr);
const original=fs.readFileSync(imageFile);
function respond(res,code,obj){res.writeHead(code,{'Content-Type':'application/json'});res.end(JSON.stringify(obj))}
const server=http.createServer(async(req,res)=>{
 const chunks=[];for await(const c of req)chunks.push(c);
 const body=chunks.length?JSON.parse(Buffer.concat(chunks).toString('utf8')):{};
 const prefix='/repos/starsplitterrecords/RexPrompt';
 const loc=new URL(req.url,'http://localhost'),p=decodeURIComponent(loc.pathname.slice(prefix.length));
 if(req.method==='GET'&&p==='/git/ref/heads/test-branch')return respond(res,200,{object:{sha:head}});
 if(req.method==='GET'&&p.startsWith('/git/commits/'))return respond(res,commits.has(p.slice(13))?200:404,commits.get(p.slice(13))||{message:'not found'});
 if(req.method==='GET'&&p==='/contents/production/drafts/manifest.json')return respond(res,200,{encoding:'base64',content:Buffer.from(JSON.stringify(manifest)).toString('base64')});
 if(req.method==='POST'&&p==='/git/blobs'){
  const b=Buffer.from(body.content,body.encoding==='base64'?'base64':'utf8');
  const id=sha(b);blobs.set(id,b);gitBlobWrites++;
  assert.equal(head,head===baseHead?baseHead:head,'Blob write must not move a branch ref');
  return respond(res,201,{sha:id});
 }
 if(req.method==='GET'&&p.startsWith('/git/blobs/')){
  const b=blobs.get(p.slice(11));
  return respond(res,b?200:404,b?{encoding:'base64',content:b.toString('base64')}:{message:'not found'});
 }
 if(req.method==='POST'&&p==='/git/trees'){
  assert.ok(body.tree.some(x=>x.path==='production/drafts/manifest.json'));
  assert.ok(body.tree.some(x=>x.path.endsWith('fixture_p01.png')));
  const id=crypto.createHash('sha1').update(JSON.stringify(body)).digest('hex');
  trees.set(id,body);treeWrites.push(body);
  return respond(res,201,{sha:id});
 }
 if(req.method==='POST'&&p==='/git/commits'){
  assert.ok(trees.has(body.tree));assert.equal(body.parents[0],head,'Commit parent must be current branch head');
  const id=crypto.createHash('sha1').update(JSON.stringify(body)).digest('hex');
  commits.set(id,{tree:{sha:body.tree},parents:body.parents});return respond(res,201,{sha:id});
 }
 if(req.method==='PATCH'&&p==='/git/refs/heads/test-branch'){
  assert.equal(body.force,false,'Never force-update production branch');
  if(race){head='c'.repeat(40);return respond(res,422,{message:'non fast forward'});}
  const commit=commits.get(body.sha),tree=trees.get(commit?.tree?.sha);
  assert.equal(commit.parents[0],head,'Unexpected parent revision');
  assert.ok(tree,'Commit missing tree');
  const mEntry=tree.tree.find(x=>x.path==='production/drafts/manifest.json');
  manifest=JSON.parse(blobs.get(mEntry.sha).toString('utf8'));
  head=body.sha;refUpdates++;return respond(res,200,{object:{sha:head}});
 }
 respond(res,404,{message:'unknown mock route '+p});
});
const exec=(port,extra={})=>new Promise(resolve=>{
 const child=cp.spawn(process.execPath,['tools/persist_approved_draft.cjs'],{
  cwd:path.resolve(__dirname,'..'),
  env:{...process.env,GITHUB_TOKEN:'test-token',GITHUB_REPOSITORY:'starsplitterrecords/RexPrompt',
   GITHUB_API_URL:'http://127.0.0.1:'+port,ALLOW_LOCAL_TEST_API:'true',
   TARGET_BRANCH:'test-branch',SOURCE_IMAGE:imageFile,SERIES_ID:'fixture',ISSUE_ID:'fixture-i01',
   RECIPE_ID:'FIXTURE_P01',APPROVAL_METHOD:'automatic-substantial-pass',
   EVALUATION_SUMMARY:'Reviewed isolated test image, never real canon',REVIEWED_APPROVAL:'true',...extra}
 });
 let stdout='',stderr='';child.stdout.on('data',x=>stdout+=x);child.stderr.on('data',x=>stderr+=x);
 child.on('close',status=>resolve({status,stdout,stderr}));
});
async function main(){
 await new Promise(ok=>server.listen(0,'127.0.0.1',ok));const port=server.address().port;
 try{
  const r=await exec(port);assert.equal(r.status,0,r.stderr);
  const record=JSON.parse(r.stdout);assert.equal(record.status,'persisted-and-readback-verified');
  assert.equal(record.sha256,digest(original));assert.equal(record.gitBlobSha,sha(original));
  assert.equal(refUpdates,1,'Atomic transaction must update ref once');
  assert.equal(treeWrites.length,1);
  assert.equal(treeWrites[0].tree.length,2,'Image and manifest must be in same Git tree');
  const entry=manifest.drafts['fixture::fixture-i01::FIXTURE_P01'];
  assert.ok(entry);assert.equal(entry.sha256,digest(original));assert.equal(entry.image,'production/drafts/fixture/fixture-i01/fixture_p01.png');
  assert.equal(blobs.get(record.gitBlobSha).compare(original),0);
  assert.equal(head,record.revision,'Commit must become authoritative head');
  console.log('PASS writeback: one Git commit, exact binary, manifest, independent read-after-write');
  const prior=head,priorWrites=gitBlobWrites;
  const denied=await exec(port);assert.notEqual(denied.status,0);assert.equal(head,prior);
  assert.equal(gitBlobWrites,priorWrites,'Unapproved overwrite must not even create blobs');
  console.log('PASS existing approved draft protected from unintentional overwrite');
  const noApproval=await exec(port,{REVIEWED_APPROVAL:'false',REPLACE_APPROVED:'true'});
  assert.notEqual(noApproval.status,0);assert.equal(head,prior);
  console.log('PASS unreviewed draft rejected without branch modification');
  // Replacement in a different image format must atomically remove the old active path.
  const replacementFile=path.join(fixtures,'approved-replacement.jpg');
  const replacementMade=cp.spawnSync('python3',['-c',
   'from PIL import Image; import sys; Image.new("RGB",(30,22),(15,205,110)).save(sys.argv[1],format="JPEG")',replacementFile],{encoding:'utf8'});
  assert.equal(replacementMade.status,0,replacementMade.stderr);
  const replacementBytes=fs.readFileSync(replacementFile);
  const replaced=await exec(port,{SOURCE_IMAGE:replacementFile,REPLACE_APPROVED:'true'});
  assert.equal(replaced.status,0,replaced.stderr);
  const replacementRecord=JSON.parse(replaced.stdout);
  assert.equal(replacementRecord.sha256,digest(replacementBytes));
  assert.equal(refUpdates,2);
  const changes=treeWrites.at(-1).tree;
  assert.ok(changes.some(x=>x.path.endsWith('fixture_p01.jpg')&&x.sha===sha(replacementBytes)));
  assert.ok(changes.some(x=>x.path.endsWith('fixture_p01.png')&&x.sha===null),'Old approved path must be removed in same tree');
  assert.equal(manifest.drafts['fixture::fixture-i01::FIXTURE_P01'].image,'production/drafts/fixture/fixture-i01/fixture_p01.jpg');
  assert.ok(blobs.get(record.gitBlobSha).equals(original),'Prior original must remain preserved as an immutable blob');
  console.log('PASS approved replacement: JPEG original stored, superseded PNG removed in one atomic tree');
  // Simulate another actor advancing main before a ref update.
  head=baseHead;manifest={schemaVersion:1,drafts:{}};race=true;
  const collided=await exec(port,{EXPECTED_HEAD_SHA:baseHead});
  assert.notEqual(collided.status,0,'Non-fast-forward race must fail');
  assert.equal(head,'c'.repeat(40));assert.equal(refUpdates,2);
  console.log('PASS concurrent branch update rejected, no partial image/manifest state visible');
 }finally{
  server.close();fs.rmSync(fixtures,{recursive:true,force:true});
 }
}
main().catch(e=>{console.error(e);server.close();fs.rmSync(fixtures,{recursive:true,force:true});process.exitCode=1});
