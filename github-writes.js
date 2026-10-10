(()=>{
'use strict';
// One write lane for both RexPrompt uploaders, with cross-tab coordination
// where the browser supports Web Locks. Conflicts still retry for other writers.
let lane=Promise.resolve(),freshCounter=0;
const LOCK_NAME='rexprompt:github:starsplitterrecords/RexPrompt:main';
function run(task){
  const next=lane.catch(()=>{}).then(()=>{
    const locks=typeof navigator==='undefined'?null:navigator.locks;
    if(locks&&typeof locks.request==='function'){
      return locks.request(LOCK_NAME,{mode:'exclusive'},task);
    }
    return task();
  });
  lane=next.catch(()=>{});
  return next;
}
function freshPath(path){
  const separator=path.includes('?')?'&':'?';
  return path+separator+'rexprompt_fresh='+Date.now().toString(36)+'-'+(++freshCounter);
}
function isConflict(error){
  const message=String(error?.message||error||'');
  return /not a fast.forward|reference update failed|failed to update ref|conflict|HTTP 409\b/i.test(message);
}
async function retryConflicts(work,onRetry,maxAttempts=4){
  for(let attempt=1;attempt<=maxAttempts;attempt++){
    try{return await work(attempt)}
    catch(error){
      if(attempt===maxAttempts||!isConflict(error))throw error;
      if(onRetry)onRetry(attempt,error);
      await new Promise(resolve=>setTimeout(resolve,150*attempt));
    }
  }
}
window.RexPromptGithubWrites=Object.freeze({run,freshPath,isConflict,retryConflicts});
})();
