(()=>{'use strict';
// Temporary browser-tab credentials only. Never persist a GitHub PAT.
const SESSION='rexprompt.githubToken';
const REMEMBER='rexprompt.githubToken.remember';
const SAVED='rexprompt.githubToken.saved';
const FORGOTTEN='rexprompt.githubToken.forgetSignal';
const CHANGE='rexprompt:github-auth-change';
const notify=()=>window.dispatchEvent(new Event(CHANGE));
const cleanLegacy=()=>{try{localStorage.removeItem(SAVED);localStorage.removeItem(REMEMBER)}catch{}};
function isRemembered(){return false}
function getToken(){try{return sessionStorage.getItem(SESSION)}catch{return null}}
function setToken(raw){
  const token=String(raw||'').trim();
  if(!token)throw Error('Enter a GitHub token.');
  sessionStorage.setItem(SESSION,token);
  cleanLegacy();
  notify();
}
function setRemember(enabled){
  cleanLegacy();
  notify();
  if(enabled)throw Error('Persistent GitHub token storage has been disabled for security.');
}
function forgetToken(){
  try{sessionStorage.removeItem(SESSION)}catch{}
  cleanLegacy();
  try{localStorage.setItem(FORGOTTEN,String(Date.now())+':'+Math.random())}catch{}
  notify();
}
// Erase any previously remembered credential as soon as this script loads.
cleanLegacy();
window.addEventListener('storage',event=>{
  if(event.key===FORGOTTEN){try{sessionStorage.removeItem(SESSION)}catch{}}
  if([FORGOTTEN,REMEMBER,SAVED].includes(event.key))notify();
});
window.addEventListener('pagehide',()=>{if(!getToken())cleanLegacy()});
window.RexPromptGithubAuth=Object.freeze({isRemembered,getToken,setToken,setRemember,forgetToken});
})();
