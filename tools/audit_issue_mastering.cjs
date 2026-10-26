#!/usr/bin/env node
'use strict';
/*
 * Non-destructive preflight for RexPrompt approved artwork.
 * This validates file integrity, pixel geometry and color-profile hints.
 * It does NOT change source pixels or substitute for a visual/lettering audit.
 */
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const opts={};
for(let i=2;i<process.argv.length;i++){
  const arg=process.argv[i];
  if(!arg.startsWith('--'))throw Error('Unknown argument: '+arg);
  const key=arg.slice(2);
  if(key==='json'){opts.json=true;continue}
  if(!['series','issue','min-width','min-height','aspect','aspect-tolerance'].includes(key))throw Error('Unknown option: '+arg);
  opts[key]=process.argv[++i];
  if(opts[key]===undefined)throw Error('Missing value for '+arg);
}
const numeric=(name,defaultValue)=>{
  if(opts[name]===undefined)return defaultValue;
  const n=Number(opts[name]);
  if(!Number.isFinite(n)||n<=0)throw Error('Invalid '+name);
  return n;
};
const minWidth=numeric('min-width',0),minHeight=numeric('min-height',0);
const aspect=numeric('aspect',0.625),tolerance=numeric('aspect-tolerance',0.025);
const manifest=JSON.parse(fs.readFileSync('production/drafts/manifest.json','utf8'));
let books={};
if(fs.existsSync('production/book-manifests.json')){
  const bm=JSON.parse(fs.readFileSync('production/book-manifests.json','utf8'));
  books=bm.issues||{};
}
const facts=[],errors=[],warnings=[];
function parsePNG(buf){
  if(buf.length<24||buf.toString('hex',0,8)!=='89504e470d0a1a0a')throw Error('Invalid PNG signature');
  if(buf.toString('ascii',12,16)!=='IHDR')throw Error('Invalid PNG IHDR');
  let icc=false,srgb=false,p=8;
  while(p+12<=buf.length){
    const size=buf.readUInt32BE(p),end=p+12+size;
    if(end>buf.length)break;
    const type=buf.toString('ascii',p+4,p+8);
    if(type==='iCCP')icc=true;if(type==='sRGB')srgb=true;
    p=end;if(type==='IEND')break;
  }
  return {type:'image/png',width:buf.readUInt32BE(16),height:buf.readUInt32BE(20),colorProfile:icc?'ICC embedded':srgb?'sRGB chunk':'unspecified'};
}
function parseJPEG(buf){
  if(buf.length<4||buf[0]!==255||buf[1]!==216)throw Error('Invalid JPEG signature');
  let p=2,width=0,height=0,icc=false;
  while(p+4<buf.length){
    if(buf[p]!==255){p++;continue}
    let marker=buf[++p];while(marker===255)marker=buf[++p];
    p++;
    if(marker===0xD9||marker===0xDA)break;
    if(marker===0x01||(marker>=0xD0&&marker<=0xD7))continue;
    if(p+2>buf.length)break;
    const size=buf.readUInt16BE(p);
    if(size<2||p+size>buf.length)throw Error('Invalid JPEG segment length');
    if(marker===0xE2&&buf.toString('ascii',p+2,p+14)==='ICC_PROFILE\u0000')icc=true;
    if([0xC0,0xC1,0xC2,0xC3,0xC5,0xC6,0xC7,0xC9,0xCA,0xCB,0xCD,0xCE,0xCF].includes(marker)){
      height=buf.readUInt16BE(p+3);width=buf.readUInt16BE(p+5);
    }
    p+=size;
  }
  if(!width||!height)throw Error('JPEG dimensions not found');
  return {type:'image/jpeg',width,height,colorProfile:icc?'ICC embedded':'unspecified'};
}
function parseWEBP(buf){
  if(buf.length<30||buf.toString('ascii',0,4)!=='RIFF'||buf.toString('ascii',8,12)!=='WEBP')throw Error('Invalid WebP signature');
  const kind=buf.toString('ascii',12,16);
  let width,height;
  if(kind==='VP8X'){
    width=1+buf[24]+(buf[25]<<8)+(buf[26]<<16);
    height=1+buf[27]+(buf[28]<<8)+(buf[29]<<16);
  }else if(kind==='VP8 '){
    width=buf.readUInt16LE(26)&0x3fff;height=buf.readUInt16LE(28)&0x3fff;
  }else if(kind==='VP8L'){
    width=1+(((buf[22]&0x3f)<<8)|buf[21]);
    height=1+(((buf[24]&0x0f)<<10)|(buf[23]<<2)|((buf[22]&0xc0)>>6));
  }else throw Error('Unsupported WebP encoding '+kind);
  return {type:'image/webp',width,height,colorProfile:'not inspected'};
}
function decode(buf){
  if(buf.length>=8&&buf[0]===0x89&&buf[1]===0x50)return parsePNG(buf);
  if(buf.length>=4&&buf[0]===255&&buf[1]===216)return parseJPEG(buf);
  if(buf.length>=30&&buf.toString('ascii',0,4)==='RIFF')return parseWEBP(buf);
  throw Error('Unsupported or corrupt raster signature');
}
const entries=Object.entries(manifest.drafts||{}).filter(([,v])=>
  (!opts.series||v.seriesId===opts.series)&&(!opts.issue||v.issueId===opts.issue));
for(const [id,item] of entries){
  if(item.status!=='approved-production-draft')errors.push(id+': not approved');
  if(!item.image||item.image.startsWith('/')||item.image.includes('..')){errors.push(id+': unsafe image path');continue}
  const expected=[item.seriesId,item.issueId,item.recipeId].join('::');
  if(id!==expected)errors.push(id+': manifest key identity mismatch');
  const file=path.resolve(item.image);
  if(!file.startsWith(path.resolve('production/drafts')+path.sep)){errors.push(id+': escapes production drafts');continue}
  if(!fs.existsSync(file)){errors.push(id+': image missing: '+item.image);continue}
  try{
    const buf=fs.readFileSync(file),im=decode(buf);
    if(im.type!==item.mimeType)errors.push(id+': MIME mismatch '+im.type+' vs '+item.mimeType);
    if(!im.width||!im.height)errors.push(id+': zero image dimension');
    if(minWidth&&im.width<minWidth)errors.push(id+': width '+im.width+' below '+minWidth);
    if(minHeight&&im.height<minHeight)errors.push(id+': height '+im.height+' below '+minHeight);
    if(Math.abs(im.width/im.height-aspect)>tolerance)warnings.push(id+': aspect '+(im.width/im.height).toFixed(4)+' outside expected '+aspect);
    if(im.colorProfile==='unspecified')warnings.push(id+': no embedded color profile detected');
    facts.push({id,image:item.image,bytes:buf.length,sha256:crypto.createHash('sha256').update(buf).digest('hex'),...im});
  }catch(e){errors.push(id+': '+e.message)}
}
for(const [key,book] of Object.entries(books)){
  if(opts.series&&opts.series!==book.seriesId)continue;
  if(opts.issue&&opts.issue!==book.issueId)continue;
  for(const unit of book.units||[]){
    const id=[book.seriesId,book.issueId,unit].join('::');
    if(!manifest.drafts?.[id])errors.push(key+': missing required book unit '+unit);
  }
}
const result={series:opts.series||'all',issue:opts.issue||'all',checked:entries.length,decoded:facts.length,errors,warnings,images:facts};
if(opts.json)console.log(JSON.stringify(result,null,2));
else{
  console.log('Issue mastering preflight: '+facts.length+'/'+entries.length+' decodable approved images');
  for(const x of facts)console.log(x.id+' '+x.width+'x'+x.height+' '+x.type+' '+x.colorProfile);
  for(const e of errors)console.error('ERROR '+e);
  for(const w of warnings)console.warn('WARN '+w);
  console.log('Errors: '+errors.length+'; warnings: '+warnings.length);
}
if(errors.length)process.exitCode=1;