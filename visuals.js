(()=>{
'use strict';
function loadScript(src){return new Promise((resolve,reject)=>{const script=document.createElement('script');script.src=src;script.async=false;script.onload=resolve;script.onerror=()=>reject(new Error('Unable to load '+src));document.head.appendChild(script)})}
loadScript('prompt-suppress.js').then(()=>loadScript('visuals-core.js')).catch(err=>console.error('RexPrompt extension loader:',err));
})();
