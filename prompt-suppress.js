(()=>{
'use strict';
// Stored per-page assembly policy is authoritative. Display it without browser-local overrides.
const labels={
  summary:"Summary",production:"Production brief",setting:"Setting",
  settingContinuity:"Setting continuity",region:"Region",factions:"Factions",
  characters:"Cast",direction:"Direction"
};
function render(){
  const mount=document.getElementById("promptSuppressMount");
  const active=window.__rexPromptActiveAssembly;
  if(!mount||!active?.scene)return;
  const scene=active.scene,show=active.show||{};
  const suppress=Array.isArray(scene.promptSuppress)?scene.promptSuppress.filter(x=>labels[x]):[];
  const characterMode=suppress.includes("characters")?"none":scene.promptCharacterMode||(show.compactCharacters?"cast":"full");
  const settingMode=scene.promptSettingMode||"full";
  const selection=suppress.length?suppress.map(x=>labels[x]).join(", "):"None";
  mount.replaceChildren();
  const panel=document.createElement("div");
  panel.className="prompt-suppress";
  panel.style.cssText="margin:8px 0 14px;padding:10px 12px;border:1px solid var(--border);border-radius:6px;background:var(--surface-soft);font-size:.84rem";
  const title=document.createElement("strong");title.textContent="Stored page assembly";
  const detail=document.createElement("div");
  detail.style.cssText="margin-top:6px;line-height:1.5";
  detail.textContent="Character detail: "+characterMode+" · Setting detail: "+settingMode+" · Suppressed sections: "+selection;
  const foot=document.createElement("div");
  foot.style.cssText="margin-top:5px;color:var(--muted);font-size:.77rem";
  foot.textContent="Read-only: these settings come from the page's RexPrompt data and apply to copying and exports. No browser or next-page override.";
  panel.append(title,detail,foot);mount.append(panel);
}
document.addEventListener("rexprompt:assembly-changed",render);
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",render,{once:true});
else render();
})();