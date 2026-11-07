#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const ROOT=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(ROOT,p),'utf8'),json=p=>JSON.parse(read(p));
const exists=p=>fs.existsSync(path.join(ROOT,p));
const html=read('index.html'),start=html.indexOf('const SHOW_MANIFEST='),end=html.indexOf('function safeFilePart(',start);
if(start<0||end<=start)throw Error('Cannot extract actual RexPrompt assembler');
const ctx=vm.createContext({fetch:async raw=>{
 const p=String(raw);if(p.startsWith('/')||p.includes('..'))throw Error('Unsafe local source '+p);
 if(!exists(p))return {ok:false,status:404,json:async()=>null,text:async()=>''};
 return {ok:true,status:200,json:async()=>json(p),text:async()=>read(p)}},
 Blob,Response,DecompressionStream,atob});
vm.runInContext(html.slice(start,end)+';globalThis.api={loadShow,expandIssues,assembleScene,validatePageLayout,pageLayoutWarnings};',ctx);
const api=ctx.api,shows=json('data/shows.json'),drafts=json('production/drafts/manifest.json').drafts;
const output=path.resolve(process.argv[2]||'docs/audits/storytelling-2026-11-07');
const rows=[],issues=[],errors=[],q=String.fromCharCode(96);
const clean=s=>String(s||'').replace(/\s+/g,' ').trim();
const wc=s=>clean(s).split(/\s+/).filter(Boolean).length;
const matches=(s,r)=>[...clean(s).matchAll(r)].length;
const safe=s=>clean(s).replace(/\|/g,'/').replace(/[\r\n]+/g,' ');
const csv=x=>'"'+String(x==null?'':x).replace(/"/g,'""')+'"';
const pattern={
 shots:/\b(wide|medium|tight|close[- ]?up|establish(?:ing)?|insert|over[- ]the[- ]shoulder|two[- ]shot|reaction strip|foreground|background|overhead|profile|silhouette|full[- ]page|splash|panorama|full[- ]bleed|low[- ]angle|high[- ]angle)\b/gi,
 geo:/\b(left|right|foreground|background|beside|behind|ahead|between|across|toward|towards|above|below|near|beyond|inside|outside|threshold|window|door|corridor|deck|roof|stairs|platform|console|table|street|alley|bridge|room|doorway|horizon|distance|station|field|ship|ramp|hall)\b/gi,
 env:/\b(light|shadow|sunlight|glow|glass|metal|concrete|brick|stone|wood|fabric|rain|dust|smoke|weather|fog|sky|skyline|worn|scuffed|rust|damaged|debris|grime|texture|reflection|palette|blue|green|red|gold|white|black|gray|grey|morning|night|evening|dawn|dusk|afternoon)\b/gi,
 move:/\b(move|moves|walk|walks|run|runs|turn|turns|step|steps|reach|reaches|lean|leans|sit|sits|stand|stands|enter|enters|exit|exits|open|opens|close|closes|lift|lifts|lower|lowers|touch|touches|hold|holds|grip|grips|point|points|pull|pulls|push|pushes|cross|crosses|back|backs|approach|approaches|follow|follows|withdraw|withdraws|place|places|take|takes|carry|carries|release|releases|stop|stops|collapse|collapses|strike|strikes|hit|hits|shift|shifts|pass|passes|hand|hands|drop|drops|catch|catches|watch|watches|look|looks|glance|glances|nod|nods|shake|shakes|gesture|gestures|pivot|pivots)\b/gi,
 act:/\b(flinch|flinches|hesitate|hesitates|hesitation|reluctant|tension|tense|nervous|uncertain|fear|frightened|anger|angry|fury|furious|smile|smiles|grin|grins|frown|frowns|grimace|grimaces|wince|winces|laugh|laughs|cry|cries|tear|tears|breath|breathes|speechless|silence|quietly|pause|pauses|stare|stares|eyes|eyeline|expression|face|jaw|hands|shoulders|posture|body language|reaction|recoil|startle|soften|hardens|strain|confidence|carefully|gentle|tender|defiant|dissatisfied|disbelief|shock|surprise|smug|skeptical|suspicious|wary|worry|worried|impatient|intimate|comprehension|shame|pride|frustration|composure|regret|resentment|embarrassment|dread|trust|affection|unease|guarded|reassure|notices|react|reacts|subtext|emotion|emotional)\b/gi};
const result=(grade,note)=>({grade,note});
function section(s,key){
 const tag='\n['+key+']\n',i=s.indexOf(tag);if(i<0)return '';
 const t=s.slice(i+tag.length),m=t.match(/\n\[[A-Z][A-Z ]+\]\n|\n=== /);return m?t.slice(0,m.index):t;
}
function assess(s,store,previous){
 const show=store.__show||{},panels=s.panelPlan||[],panelText=panels.map(x=>typeof x==='string'?x:JSON.stringify(x)).join(' ');
 const shot=matches(panelText,pattern.shots),geo=matches(panelText,pattern.geo),env=matches(panelText,pattern.env);
 const move=matches(panelText,pattern.move),acting=matches(panelText+' '+(s.directionInline||[]).join(' '),pattern.act);
 const n=panels.length,dialogue=s.dialogueInline||[],d=dialogue.length,cast=(s.characters||s.charactersInline||[]).length;
 let assembled='',assemblyError='',layoutError='',warnings=[];
 try{assembled=String(api.assembleScene(s,store,0));}catch(e){assemblyError=String(e.message||e)}
 try{api.validatePageLayout(s)}catch(e){layoutError=String(e.message||e)}
 try{warnings=[...api.pageLayoutWarnings(s)]}catch(e){warnings.push(String(e))}
 const renderedSetting=section(assembled,'SETTING'),renderedPanel=section(assembled,'PANEL PLAN'),renderedLayout=section(assembled,'PAGE COMPOSITION');
 const continuity=!!previous&&(
   (s.continuityFrom&&s.continuityFrom===previous.id)||
   (s.setting&&s.setting===previous.setting)||
   (s.settingText&&s.settingText===previous.settingText));
 const noncharacter=!cast&&!d&&/\b(splash|panorama|full.page|environment|infrastructure|landscape)\b/i.test(panelText+' '+(s.summary||''));
 const detail=shot+geo+env,wd=wc(panelText);
 let layout;
 if(layoutError||assemblyError)layout=result('invalid',layoutError||('Assembler: '+assemblyError));
 else if(show.unitLabel==='SCENE')layout=result('na','Non-page scene: evaluate shot/beat direction instead');
 else if(s.pageLayout&&renderedLayout)layout=result('pass','Validated '+s.pageLayout.composition+' composition; '+n+' assigned beats and reading flow');
 else if(n===1&&/\b(splash|full.page|single|full.bleed|cover)\b/i.test(panelText))layout=result('pass','Explicit single-image composition');
 else if(n&&!shot)layout=result('gap',n+' beats with no defined framing or visual hierarchy');
 else if(n)layout=result('review',n+' beats, '+shot+' shot/scale cues; no validated page composition');
 else layout=result('gap','No panel or beat layout supplied');
 let visual;
 if(!n&&!renderedPanel)visual=result('gap','No authored panel visual description reaches the assembler');
 else if(wd>=80&&detail>=5)visual=result('pass',wd+' panel words and '+detail+' concrete framing/spatial/environment cues');
 else if(wd>=25&&detail>=2)visual=result('review',wd+' panel words and '+detail+' concrete cues; judge specificity and repeat scaffolding');
 else visual=result('gap','Only '+wd+' panel words and '+detail+' concrete visual cues');
 const visibleEnv=wc(renderedSetting),cue=geo+env;
 let setting;
 if(visibleEnv>=18)setting=result('pass','Delivered setting supplies '+visibleEnv+' contextual words');
 else if(continuity)setting=result('carry','Carried setting from '+previous.id+'; check visual state and prop continuity');
 else if(visibleEnv&&cue>=3)setting=result('pass','Named setting plus '+cue+' panel geography/environment details');
 else if(cue>=5)setting=result('review','Setting inferred from '+cue+' panel cues, without full establishing context');
 else if(visibleEnv||cue>=2)setting=result('review','Location label or sparse setting: '+cue+' concrete cues');
 else setting=result('gap','No delivered setting and no adequate scene/environment description');
 const mapped=panels.some(p=>p&&typeof p==='object'&&Array.isArray(p.dialogueIndices))||
   (d>0&&dialogue.every(x=>/^Panel\s+\d+$/i.test(String(x.subtext||''))));
 const density=warnings.length||n>=8||(d>=13&&d/Math.max(n,1)>=2.4);
 let blocking;
 if(noncharacter)blocking=result('na','Environment-only composition, no actor blocking required');
 else if(density)blocking=result('review','Dense staging/lettering: '+n+' beats / '+d+' dialogue items / '+warnings.length+' assembler warnings');
 else if(move>=Math.max(3,Math.ceil(n*.7))&&geo>=2&&!(d>=7&&!mapped))blocking=result('pass',move+' physical verbs, '+geo+' spatial cues, action/read order can be staged');
 else if(move>=2)blocking=result('review',move+' action cues, '+geo+' spatial cues'+(d>=7&&!mapped?'; dialogue not fully panel-assigned':''));
 else blocking=result('gap',move+' physical action cues across '+n+' beats; insufficient blocking/causality');
 let emotion;
 if(noncharacter)emotion=result('na','Environment-only page/beat');
 else if(acting>=Math.max(3,Math.ceil(n*.75)))emotion=result('pass',acting+' acting/subtext/posture/reaction cues in delivered directions');
 else if(acting>=1)emotion=result('review',acting+' acting cues; assess reaction ownership, changes and specific expression');
 else if(d||cast)emotion=result('gap','No specific emotional acting or reaction instructions despite characters/dialogue');
 else emotion=result('review','No acting directions; verify whether characters or reactions are required');
 // A musical SCENE is not a comic page. Do not score missing comic-page scaffolding as an editorial defect.
 if(show.unitLabel==='SCENE'){
  visual=result('na','Not a comic production page; scene visual-adaptation scope has not been defined');
  blocking=result('na','Not a panel-based comic production unit');
  emotion=result('na','Song/scene dramatic acting is not specified by a comic-page storyboard');
 }
 return {layout,visual,setting,blocking,emotion,layoutError,assemblyError,panels:n,dialogue:d,cast,shot,geo,env,move,acting,sample:clean(panelText).slice(0,190),warnings};
}
function sum(rs){
 const x={total:rs.length};for(const k of ['layout','visual','setting','blocking','emotion']){
 x[k]={pass:0,carry:0,review:0,gap:0,invalid:0,na:0};
 for(const r of rs)x[k][r[k]]++;}
 return x;
}
const unclosed=k=>k.review+k.gap+k.invalid;
const score={pass:'OK',carry:'CR',review:'RV',gap:'GAP',invalid:'INV',na:'—'};
async function main(){
 for(const show of shows){
  let expansions;
  try{expansions=api.expandIssues(show)}catch(e){errors.push({show:show.id,error:String(e)});continue}
  for(const issue of expansions){
   let store;try{store=await api.loadShow(issue)}catch(e){errors.push({show:issue.id,error:String(e)});continue}
   let previous=null;const local=[];
   for(const s of store.__scenes){
    const v=assess(s,store,previous);
    const id=issue.issueId||issue.id,approvedKey=(issue.seriesId||show.seriesId)+'::'+id+'::'+s.id;
    const row={seriesId:issue.seriesId||show.seriesId,seriesName:issue.seriesName||show.seriesName||show.name,issueId:id,
      issueLabel:issue.issueLabel||issue.name,sourceShow:show.id,recipeId:s.id,unitLabel:store.__show.unitLabel||'PAGE',
      approved:!!drafts[approvedKey],summary:s.summary||'',panels:v.panels,dialogue:v.dialogue,cast:v.cast,
      layout:v.layout.grade,layoutWhy:v.layout.note,visual:v.visual.grade,visualWhy:v.visual.note,
      setting:v.setting.grade,settingWhy:v.setting.note,blocking:v.blocking.grade,blockingWhy:v.blocking.note,
      emotion:v.emotion.grade,emotionWhy:v.emotion.note,continuityFrom:s.continuityFrom||'',
      pageSetting:s.setting||s.settingText||'',firstPanel:v.sample,assemblerError:v.assemblyError,
      sourceFiles:(issue.scenesFiles||[issue.scenesFile||'']).join('; ')};
    rows.push(row);local.push(row);previous=s;
   }
   issues.push({id:issue.issueId||issue.id,label:issue.issueLabel||issue.name,seriesId:issue.seriesId||show.seriesId,seriesName:issue.seriesName||show.seriesName||show.name,rows:local});
  }
 }
 const dirname=output;fs.mkdirSync(path.join(dirname,'series'),{recursive:true});
 const columns=['seriesId','seriesName','issueId','issueLabel','sourceShow','recipeId','unitLabel','approved','summary','panels','dialogue','cast','layout','layoutWhy','visual','visualWhy','setting','settingWhy','blocking','blockingWhy','emotion','emotionWhy','continuityFrom','pageSetting','firstPanel','assemblerError','sourceFiles'];
 fs.writeFileSync(path.join(dirname,'all-pages.csv'),[columns.map(csv).join(','),...rows.map(r=>columns.map(k=>csv(r[k])).join(','))].join('\n')+'\n');
 const seriesIds=[...new Set(issues.map(i=>i.seriesId))];
 const index=['# RexPrompt storytelling recipe survey — November 7, 2026','',
 '**Scope:** 25 production series, expanded issues, and individual recipe units loaded from the LIVE assembler. Assesses the instructions that reach generation, not rendered comic pixels.','',
 '**Codes:** OK = enough explicit evidence under a structural screen; CR = setting carried from previous page; RV = editorial review; GAP = insufficient description; INV = assembler invalid; — = not applicable.','',
 '**Interpretation:** These are triage classifications, not conclusive artistic judgments. A long generic prompt may pass a textual screen but still fail to tell the story. A visually effective sparse panel may need less direction.','',
 '## Coverage',''];
 const all=sum(rows);index.push('**'+seriesIds.length+' distinct series / '+issues.length+' issue configurations / '+rows.length+' production units.**','');
 for(const k of ['layout','visual','setting','blocking','emotion'])index.push('- '+k+': '+all[k].pass+' OK, '+all[k].carry+' carried, '+all[k].review+' review, '+(all[k].gap+all[k].invalid)+' missing/invalid');
 index.push('','## Issue and page-level reports','','| Series | Issue configs | Units | Layout flagged | Visual flagged | Setting flagged | Blocking flagged | Acting flagged |','|---|---:|---:|---:|---:|---:|---:|---:|');
 for(const sid of seriesIds){
  const ii=issues.filter(i=>i.seriesId===sid),rr=ii.flatMap(i=>i.rows),t=sum(rr);
  index.push('| ['+safe(ii[0].seriesName)+'](series/'+sid+'.md) | '+ii.length+' | '+rr.length+' | '+unclosed(t.layout)+' | '+unclosed(t.visual)+' | '+unclosed(t.setting)+' | '+unclosed(t.blocking)+' | '+unclosed(t.emotion)+' |');
  const doc=['# '+ii[0].seriesName,'','**Production series:** '+q+sid+q+' · **Issue configurations:** '+ii.length+' · **Units:** '+rr.length,'',
    '**This is a recipe-source screen.** Approved imagery, lettering, printed layout and subjective emotional effectiveness were not visually inspected.',''];
  for(const i of ii){
   const t=sum(i.rows);
   doc.push('## '+i.label+' ('+i.id+')','',
     '**'+i.rows.length+' units.** Layout: '+unclosed(t.layout)+' flagged; visual: '+unclosed(t.visual)+'; environment: '+unclosed(t.setting)+'; blocking: '+unclosed(t.blocking)+'; acting: '+unclosed(t.emotion)+'.','',
     '| Unit | Panels | Composition | Image detail | Setting | Blocking | Acting | Review note |',
     '|---|---:|---|---|---|---|---|---|');
   for(const r of i.rows){
    const ks=['layout','visual','setting','blocking','emotion'];
    const grades=ks.map(k=>score[r[k]]||'?');
    let reasons=ks.filter(k=>['gap','invalid'].includes(r[k])).map(k=>k+': '+r[k+'Why']);
    if(!reasons.length)reasons=ks.filter(k=>r[k]==='review').map(k=>k+': '+r[k+'Why']);
    const note=reasons.length?safe(reasons.slice(0,2).join('; ')).slice(0,260):'No structural gap detected; sequence still requires editorial review';
    doc.push('| '+q+r.recipeId+q+' | '+r.panels+' | '+grades[0]+' | '+grades[1]+' | '+grades[2]+' | '+grades[3]+' | '+grades[4]+' | '+note+' |');
   }
   doc.push('');
  }
  fs.writeFileSync(path.join(dirname,'series',sid+'.md'),doc.join('\n')+'\n');
 }
 index.push('','[Full page-level CSV with explanation of every score](all-pages.csv) · [Methodology and limitations](METHOD.md).','','## Critical source gaps (first 60)','');
 let bad=rows.filter(r=>['layout','visual','setting','blocking','emotion'].some(k=>['gap','invalid'].includes(r[k])));
 for(const r of bad.slice(0,60)){const k=['layout','visual','setting','blocking','emotion'].filter(k=>['gap','invalid'].includes(r[k]));index.push('- '+q+r.seriesId+' / '+r.issueLabel+' / '+r.recipeId+q+': '+safe(k.map(z=>z+' — '+r[z+'Why']).join('; ')).slice(0,250))}
 index.push('','**The series pages and CSV include every flagged unit, not just this sample.**','');
 fs.writeFileSync(path.join(dirname,'index.md'),index.join('\n')+'\n');
 fs.writeFileSync(path.join(dirname,'METHOD.md'),[
 '# Method and limits','',
 '## Source','',
 'This audit runs RexPrompt main index.html loadShow, expandIssues, assembleScene, validatePageLayout and pageLayoutWarnings in Node. The exported CSV contains one row per registered unit within its assembled issue. It reads the actual visible panel and setting sections rather than trusting unused metadata alone. The first previous page is reset at issue boundaries.','',
 '## Rules','',
 '- Composition: validated layout passes; explicit one-panel splash passes; shot cues without layout hierarchy require review; invalid layouts are blockers; musical scenes are not page layouts.',
 '- Image detail: authored panel visual words PLUS concrete shot, geography and physical/lighting cues. Generic generationLine boilerplate is excluded from specificity.',
 '- Setting: detailed emitted setting passes, otherwise same setting or explicit continuityFrom on immediate prior page is acceptable carryover; sparse new environment needs review or fails.',
 '- Blocking: character physical movement, location and props; dense lettering without explicit assignment is review; no acting required on environment-only pages.',
 '- Emotional performance: expression, gaze, posture, meaningful reactions and subtext; lack of any with dialogue or visible cast is a gap. Does NOT measure true dramatic impact.',
 '- Each row includes the evidence explaining the score and the first panel excerpt for human follow-up.',
 '',
 '## Limits','',
 '- Editorial heuristics are NOT a substitute for reading the entire sequence and its actual references. They can overestimate adequacy of long generic descriptions and underestimate economy or artful silence.',
 '- No image pixel inspection, actual face consistency, palette, lettering or print quality assessed. Neither a passing score nor approved draft record is final art approval.',
 '- A reported unapproved page may exist elsewhere outside the approved RexPrompt manifest.',
 '- This audit modifies NO source scripts, dialogue, images, approvals, published material or continuity canon.',
 '',
 '## Inventory','',
 'Registered configurations: '+shows.length,
 'Expanded issues: '+issues.length,
 'Unit rows: '+rows.length,
 'Load errors: '+errors.length,
 '',
 'Errors: '+JSON.stringify(errors)
 ].join('\n')+'\n');
 fs.writeFileSync(path.join(dirname,'summary.json'),JSON.stringify({generatedAt:new Date().toISOString(),configurationCount:shows.length,issues:issues.length,series:seriesIds.length,units:rows.length,totals:all,byIssue:issues.map(i=>({id:i.id,series:i.seriesId,units:i.rows.length,status:sum(i.rows)})),errors},null,2)+'\n');
 console.log(JSON.stringify({configurations:shows.length,series:seriesIds.length,issues:issues.length,units:rows.length,errors,totals:all},null,2));
 if(errors.length)process.exitCode=1;
}
main().catch(e=>{console.error(e.stack||e);process.exitCode=1});
