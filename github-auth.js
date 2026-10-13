(()=>{'use strict';
const SESSION='rexprompt.githubToken',REMEMBER='rexprompt.githubToken.remember',SAVED='rexprompt.githubToken.saved',FORGOTTEN='rexprompt.githubToken.forgetSignal',CHANGE='rexprompt:github-auth-change';
const read=(storage,key)=>{try{return storage.getItem(key)}catch{return null}};
const notify=()=>window.dispatchEvent(new Event(CHANGE));
function isRemembered(){return read(localStorage,REMEMBER)==='1'}
function getToken(){if(isRemembered()){const saved=read(localStorage,SAVED);if(saved){if(read(sessionStorage,SESSION)!==saved)sessionStorage.setItem(SESSION,saved);return saved}}return read(sessionStorage,SESSION)}
function setToken(raw){const token=String(raw||'').trim();if(!token)throw Error('Enter a GitHub token.');sessionStorage.setItem(SESSION,token);if(isRemembered()){try{localStorage.setItem(SAVED,token)}catch{try{localStorage.removeItem(REMEMBER);localStorage.removeItem(SAVED)}catch{}notify();throw Error('Safari could not remember the token. It remains available for this tab only; disable Remember on this device or check Safari storage settings.')}}notify()}
function setRemember(enabled){if(enabled){const current=getToken();try{if(current)localStorage.setItem(SAVED,current);localStorage.setItem(REMEMBER,'1')}catch{try{localStorage.removeItem(SAVED);localStorage.removeItem(REMEMBER)}catch{}notify();throw Error('Persistent storage is unavailable. Token will remain session-only.')}}else{localStorage.removeItem(REMEMBER);localStorage.removeItem(SAVED)}notify()}
function forgetToken(){sessionStorage.removeItem(SESSION);localStorage.removeItem(SAVED);localStorage.removeItem(REMEMBER);localStorage.setItem(FORGOTTEN,String(Date.now())+':'+Math.random());notify()}
if(isRemembered())getToken();else{try{localStorage.removeItem(SAVED)}catch{}}
window.addEventListener('storage',event=>{if(event.key===FORGOTTEN)sessionStorage.removeItem(SESSION);if([FORGOTTEN,REMEMBER,SAVED].includes(event.key))notify()});
window.RexPromptGithubAuth=Object.freeze({isRemembered,getToken,setToken,setRemember,forgetToken});
})();