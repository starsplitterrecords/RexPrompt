(()=>{
'use strict';
function loadScript(src){return new Promise((resolve,reject)=>{const script=document.createElement('script');script.src=src;script.async=false;script.onload=resolve;script.onerror=()=>reject(new Error('Unable to load '+src));document.head.appendChild(script)})}
loadScript('prompt-suppress.js').then(()=>loadScript('production-coverage-core.js?v=20261107-qc-1')).then(()=>loadScript('visuals-core.js?v=20261107-qc-1')).catch(err=>console.error('RexPrompt extension loader:',err));
})();
