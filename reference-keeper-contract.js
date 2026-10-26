/* Reference Keeper's shared intake, selection, and integrity contract.
 * Browser: window.RexPromptKeeperContract; Node: require('./reference-keeper-contract.js')
 * No production approvals or visual canon are inferred by this module.
 */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.RexPromptKeeperContract=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const TYPES=Object.freeze(['character','setting','vehicle','item']);
  const EXT=Object.freeze({'image/png':'png','image/jpeg':'jpg','image/webp':'webp'});
  const MAX_BYTES=50*1024*1024;
  const safe=s=>String(s||'').toLowerCase().replace(/[^a-z0-9._-]+/g,'-').replace(/^-+|-+$/g,'');
  const validSlug=s=>typeof s==='string'&&/^[a-z0-9][a-z0-9._-]*$/.test(s)&&s!=='.'&&s!=='..';
  function canonicalSeries(shows){
    const out=new Map();
    if(!Array.isArray(shows))return [];
    for(const show of shows){
      // Mirror index.html seriesName(show) and seriesId(show), including legacy
      // show records without an explicit seriesId (e.g. Vikings and Backyard Rockets).
      const name=String(show?.seriesName||show?.name||show?.id||'').split(' — ')[0].trim();
      const id=show?.seriesId||name.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
      if(!validSlug(id))continue;
      if(!out.has(id))out.set(id,{id,name});
    }
    return [...out.values()].sort((a,b)=>a.name.localeCompare(b.name));
  }
  function entryKey(seriesId,type,name){
    if(!validSlug(seriesId)||!TYPES.includes(type)||!safe(name))throw Error('Invalid series, reference type, or name');
    return seriesId+'::'+type+'::'+safe(name);
  }
  function storagePath(seriesId,type,name,mime){
    if(!EXT[mime])throw Error('Unsupported image MIME');
    return 'production/references/'+seriesId+'/keeper/'+type+'/'+safe(name)+'.'+EXT[mime];
  }
  function sniff(bytes){
    if(!(bytes instanceof Uint8Array)||bytes.length<24||bytes.length>MAX_BYTES)return null;
    if(bytes[0]===137&&bytes[1]===80&&bytes[2]===78&&bytes[3]===71&&bytes[4]===13&&bytes[5]===10&&bytes[6]===26&&bytes[7]===10)return 'image/png';
    if(bytes[0]===255&&bytes[1]===216&&bytes[bytes.length-2]===255&&bytes[bytes.length-1]===217)return 'image/jpeg';
    if(String.fromCharCode(...bytes.slice(0,4))==='RIFF'&&String.fromCharCode(...bytes.slice(8,12))==='WEBP')return 'image/webp';
    return null;
  }
  function selectEntries(manifest,{seriesId,type='all',query=''}={}){
    const q=String(query||'').trim().toLowerCase();
    return Object.values(manifest?.references||{}).filter(x=>
      x&&x.seriesId===seriesId&&(type==='all'||x.type===type)&&
      (!q||[x.name,x.id,x.sourceFilename,x.type].some(v=>String(v||'').toLowerCase().includes(q)))
    ).sort((a,b)=>(a.type+' '+a.name).localeCompare(b.type+' '+b.name));
  }
  function checkManifest(manifest,shows){
    const errors=[],warnings=[];
    if(manifest?.schemaVersion!==1||!manifest.references||typeof manifest.references!=='object'||Array.isArray(manifest.references)){
      return {errors:['Keeper manifest must contain schemaVersion=1 and references object'],warnings};
    }
    const series=new Map(canonicalSeries(shows).map(x=>[x.id,x.name])),paths=new Map(),names=new Map();
    for(const [key,r] of Object.entries(manifest.references)){
      const tag='Keeper '+key+': ';
      if(!r||typeof r!=='object'||Array.isArray(r)){errors.push(tag+'invalid entry');continue}
      if(r.id!==key||key.split('::').length!==3||key!==[r.seriesId,r.type,key.split('::')[2]].join('::')||!validSlug(key.split('::')[2]))errors.push(tag+'invalid key or entry id');
      if(!series.has(r.seriesId))errors.push(tag+'seriesId not registered in data/shows.json');
      if(!TYPES.includes(r.type))errors.push(tag+'invalid asset category');
      if(typeof r.name!=='string'||!r.name.trim())errors.push(tag+'empty display name');
      if(typeof r.sourceFilename!=='string'||!r.sourceFilename.trim()||/[\/\\\u0000-\u001f]/.test(r.sourceFilename))errors.push(tag+'invalid sourceFilename');
      if(typeof r.updatedAt!=='string'||!Number.isFinite(Date.parse(r.updatedAt)))errors.push(tag+'invalid updatedAt');
      const suffix=EXT[r.mimeType];
      if(!suffix)errors.push(tag+'invalid MIME type');
      const prefix='production/references/'+r.seriesId+'/keeper/'+r.type+'/';
      const p=r.image;
      const match=typeof p==='string'&&p.startsWith(prefix)&&
        !p.includes('\\')&&!p.includes('..')&&!p.includes('//')&&
        /^[-a-z0-9._]+\.(png|jpg|jpeg|webp)$/.test(p.slice(prefix.length));
      if(!match)errors.push(tag+'unsafe or incorrect series/category image path');
      else if(suffix&&!(suffix==='jpg'?/\.(jpg|jpeg)$/:new RegExp('\\.'+suffix+'$')).test(p))errors.push(tag+'file extension does not match MIME');
      if(paths.has(p))errors.push(tag+'image path reused by '+paths.get(p));
      else paths.set(p,key);
      const keyName=r.seriesId+'::'+r.type+'::'+safe(r.name);
      if(names.has(keyName))errors.push(tag+'duplicate normalized identity of '+names.get(keyName));
      else names.set(keyName,key);
      if(series.has(r.seriesId)&&r.seriesName&&
         r.seriesName.toLowerCase()!==series.get(r.seriesId).toLowerCase())
        warnings.push(tag+'series display name differs from registry');
    }
    return {errors,warnings};
  }
  function planIntake({manifest,shows,seriesId,type,name,fileName,mimeType,bytes,replaceId=null,now}){
    if(!canonicalSeries(shows).some(s=>s.id===seriesId))throw Error('Unknown canonical series ID');
    if(!TYPES.includes(type))throw Error('Unknown reference category');
    if(typeof name!=='string'||!name.trim()||name.length>120)throw Error('Reference name must be 1–120 characters');
    if(typeof fileName!=='string'||!fileName.trim()||/[\/\\\u0000-\u001f]/.test(fileName))throw Error('Invalid original filename');
    if(!bytes||!(bytes instanceof Uint8Array))throw Error('Original image bytes required');
    if(!bytes.length||bytes.length>MAX_BYTES)throw Error('Image must be between 1 byte and 50 MB');
    const detected=sniff(bytes);
    if(!detected)throw Error('Invalid or unsupported original image bytes');
    if(detected!==mimeType)throw Error('Image file content does not match declared MIME type');
    const sourceSuffix=fileName.toLowerCase().split('.').pop();
    if(!['jpg','jpeg','png','webp'].includes(sourceSuffix)||
      ((sourceSuffix==='jpg'||sourceSuffix==='jpeg')?'image/jpeg':'image/'+sourceSuffix)!==detected)
      throw Error('Original filename extension does not match image content');
    const id=replaceId||entryKey(seriesId,type,name);
    const old=manifest?.references?.[id];
    if(replaceId){
      if(!old||old.seriesId!==seriesId||old.type!==type||old.name!==name)throw Error('Replacement identity is stale or changed; refresh');
    }else if(old)throw Error('Reference already exists; use Replace');
    const image=storagePath(seriesId,type,name,detected);
    for(const [otherId,other] of Object.entries(manifest?.references||{})){
      if(otherId!==id&&other.image===image)throw Error('Image destination already belongs to another reference');
      if(otherId!==id&&other.seriesId===seriesId&&other.type===type&&safe(other.name)===safe(name))throw Error('Duplicate normalized reference identity');
    }
    const display=canonicalSeries(shows).find(s=>s.id===seriesId).name;
    const entry={id,seriesId,seriesName:display,type,name,image,mimeType:detected,sourceFilename:fileName,updatedAt:now||new Date().toISOString()};
    return {entry,previous:old||null,image,bytes};
  }
  return Object.freeze({TYPES,EXT,MAX_BYTES,safe,canonicalSeries,entryKey,storagePath,sniff,selectEntries,checkManifest,planIntake});
});
