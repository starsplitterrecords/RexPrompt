(function(root,factory){
 const api=factory();
 if(typeof module==='object'&&module.exports)module.exports=api;
 else root.RexProductionCoverage=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
// The same pixel geometry is used by individual image checks and issue-wide accounting.
function masterStandard(seriesId,assetKind){
 if(assetKind==='cover'){
  if(seriesId==='vikings-2026')return {kind:'cover',width:2400,height:3840,ratio:'5:8',note:'Vikings 2026 series cover specification'};
  return {kind:'cover',width:1800,height:2700,ratio:'2:3',note:'Visions issue cover specification'};
 }
 return {kind:'interior',width:2400,height:3840,ratio:'5:8',note:'Interior comic master specification'};
}
function isCover(id,assetKind){
 return assetKind==='cover'||(!assetKind&&/(?:^|[_-])COVER(?:$|[_-])/i.test(id));
}
// This checks source pixel dimensions, not artistic fidelity, color, DPI or full mastering.
function audit({seriesId,issueId,units=[],drafts={},facts={},publishedAll=false}){
 const findings=units.map(unit=>{
  const recipeId=unit.recipeId,assetKind=unit.assetKind|| (isCover(recipeId)?'cover':'interior');
  const required=masterStandard(seriesId,assetKind);
  const key=[seriesId,issueId,recipeId].join('::');
  const draft=drafts[key],hasDraft=Boolean(draft?.status==='approved-production-draft'&&draft.image);
  const released=Boolean(unit.released||publishedAll);
  const imageState=hasDraft?'approved-draft':released?'released':'not-indexed';
  const observation=hasDraft?facts[key]||null:null;
  const sizeState=!hasDraft&&!released?'missing':!observation?'unverified':
   Number.isInteger(observation.width)&&Number.isInteger(observation.height)&&
   observation.width===required.width&&observation.height===required.height?'correct':'wrong';
  return {recipeId,assetKind,imageState,sizeState,required,
    actual:observation?{width:observation.width,height:observation.height}:null,
    source:observation?.source||null};
 });
 const count=state=>findings.filter(x=>x.sizeState===state).length;
 const covered=findings.filter(x=>x.imageState!=='not-indexed').length;
 return {total:findings.length,covered,missing:count('missing'),sizeCorrect:count('correct'),
  sizeWrong:count('wrong'),sizeUnverified:count('unverified'),
  allImages:findings.length>0&&covered===findings.length,
  allSizesCorrect:findings.length>0&&count('correct')===findings.length,
  findings};
}
return {masterStandard,audit};
});
