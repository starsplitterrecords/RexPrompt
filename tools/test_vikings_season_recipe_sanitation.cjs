#!/usr/bin/env node
'use strict';
// Vikings-wide audited recipe sanitation. Run the actual browser assembler;
// preserve exact authored story data, approved pages, visual identity and layouts.
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8'),json=p=>JSON.parse(read(p));
const src=read('index.html'),from=src.indexOf('const SHOW_MANIFEST='),to=src.indexOf('function safeFilePart(',from);
assert(from>=0&&to>from,'Canonical assembler extraction changed');
const context=vm.createContext({});
vm.runInContext(src.slice(from,to)+';globalThis.testExports={assembleScene,prepareCleanPanelPlan,prepareNumberedProsePanels};',context);
const {assembleScene:assemble,prepareCleanPanelPlan,prepareNumberedProsePanels}=context.testExports;
const list=json('data/shows.json').filter(x=>/^vikings-2026-s1-e\d{2}$/.test(x.id)).sort((a,b)=>a.id.localeCompare(b.id));
assert.equal(list.length,12,'Vikings Season 1 issue manifest changed');
const base='data/shows/vikings-2026-s1/';
const store={};
for(const f of ['characters','settings','regions','factions','direction','dialogue'])store[f+'.json']=json(base+f+'.json');
const issue3=json(base+'editorial/chef_recipe_sanitation_i03.json');
const exception6=json(base+'editorial/chef_recipe_exceptions_i06.json');
const byId=(entries)=>new Map(entries.map(p=>[p.id,p]));
assert.equal(issue3.length,20,'Issue 3 should have 20 audited structured pages');
assert.equal(new Set(issue3.map(p=>p.id)).size,20,'Issue 3 duplicate sanitation ID');
assert(issue3.every(x=>Object.keys(x).length===2&&x.promptPanelMode==='clean'),'Issue 3 sanitation must be delivery metadata only');
assert.deepEqual(exception6,[{id:'VIK_S1E06_P23',promptDialogueMode:'original'}],'Unexpected exception expansion');
const groups=[];
const stats={pages:0,original:0,structured:0,prose:0,balloons:0,before:0,after:0};
function section(output,heading){
  const marker='\n['+heading+']\n',start=output.indexOf(marker);
  if(start<0)return null;
  const remaining=output.slice(start+marker.length),next=remaining.search(/\n\[[A-Z][A-Z0-9 /_-]*\]\n/);
  return (next<0?remaining:remaining.slice(0,next)).trim();
}
function verifyTextAndOrder(page,rendered){
  const dialogue=section(rendered,'DIALOGUE');
  for(const [i,d] of (page.dialogueInline||[]).entries()){
    assert(dialogue?.includes('"'+d.text+'"'),'Omitted dialogue '+page.id+' item '+(i+1));
  }
  // Every physical authored panel is a literal subspan of the chef instruction.
  for(const p of page.panelPlan||[]){
    const action=typeof p==='string'?p.trim():p.action?.trim();
    assert(action&&rendered.includes(action),'Lost panel direction '+page.id);
  }
}
for(const show of list){
  const number=Number(show.id.slice(-2));
  store.__show=show;
  const source=show.scenesFiles.filter(f=>f!=='covers.json').flatMap(f=>json(base+f))
    .filter(p=>new RegExp(show.includeIdPattern).test(p.id||''));
  let pages=source;
  if(number===3){
    const overlays=show.sceneOverlays||[];
    assert(overlays.some(o=>o.file==='editorial/chef_recipe_sanitation_i03.json'&&o.strict&&o.mergeById),
      'Issue 3 overlay must be registered as strict merge');
    const map=byId(issue3);
    assert(source.every(p=>p.id.endsWith('P01')||map.has(p.id)),'Unprofiled Issue 3 interior');
    assert(!map.has('VIK_S1E03_P01'),'Issue 3 special editorial P01 must be unchanged');
    pages=source.map(p=>({...p,...(map.get(p.id)||{})}));
  }
  if(number===6){
    const overlays=show.sceneOverlays||[];
    assert(overlays.some(o=>o.file==='editorial/chef_recipe_exceptions_i06.json'&&o.strict&&o.mergeById),
      'Issue 6 out-of-order mapping exception not registered');
    const map=byId(exception6);pages=source.map(p=>({...p,...(map.get(p.id)||{})}));
  }
  if(number>=4){
    assert.equal(show.promptPanelMode,'prose-numbered','Missing audited prose mode '+show.id);
    assert.equal(show.promptDialogueMode,'grouped','Missing grouped lettering '+show.id);
  }
  if(number<=2)assert(!show.promptPanelMode&&!show.promptDialogueMode,
    'Released/approved issues must keep existing recipe delivery');
  let before=0,after=0,changed=0;
  for(let i=0;i<pages.length;i++){
    const page=pages[i];
    const baseline=assemble({...page,promptPanelMode:'original',promptDialogueMode:'original'},
      {...store,__show:{...show,promptPanelMode:'original',promptDialogueMode:'original'}},i);
    const result=assemble(page,store,i);
    const mode=page.promptPanelMode||show.promptPanelMode||'original';
    verifyTextAndOrder(page,result);
    // Only PANEL PLAN and DIALOGUE may change. All other ingredients remain
    // exactly as previously assembled, including continuity and directions.
    for(const heading of ['SETTING','SETTING CONTINUITY','REGION','FACTIONS',
                          'CAST','CHARACTERS','PAGE COMPOSITION','CONTINUITY','DIRECTION']){
      assert.equal(section(result,heading),section(baseline,heading),'Altered '+heading+' on '+page.id);
    }
    if(mode==='original'){
      assert.equal(result,baseline,'Approved/exceptional recipe changed '+page.id);
      stats.original++;
    }else{
      assert(result!==baseline,'Expected delivery improvement '+page.id);
      changed++;
      if(mode==='clean'){
        const product=prepareCleanPanelPlan(page);
        assert.equal(product.panels.length,page.panelPlan.length,'Lost structured panel '+page.id);
        assert(!section(result,'PANEL PLAN').includes('"dialogueIndices"'),'JSON index leakage '+page.id);
        assert.equal(section(result,'DIALOGUE'),section(baseline,'DIALOGUE'),'Changed exact dialogue '+page.id);
        stats.structured++;
      }else{
        assert.equal(mode,'prose-numbered','Unknown Vikings mode '+page.id);
        const product=prepareNumberedProsePanels(page);
        assert.equal(product.panels.length,page.panelPlan.length);
        for(let n=1;n<=product.panels.length;n++)
          assert(section(result,'PANEL PLAN').includes(n+'. '),'Missing ordered prose panel '+n+' '+page.id);
        let lastSeen=0;
        for(const text of page.dialogueInline||[]){
          const n=Number(text.subtext.match(/^Panel\s+(\d+)$/)?.[1]);
          if(page.promptDialogueMode!=='original'&&n<lastSeen)
            throw new Error('Dialogue panel sequence regressed: '+page.id);
          lastSeen=n;
        }
        if(page.promptDialogueMode!=='original'){
          // Every contiguous group states the panel only once; dialog text
          // and line order are untouched, rather than rearranged by panel.
          let panel=0,groups=0;
          for(const n of product.byDialogue)if(n!==panel){panel=n;groups++}
          assert.equal((section(result,'DIALOGUE').match(/^Panel \d+:$/gm)||[]).length,groups,
            'Wrong dialogue group count '+page.id);
        }else assert.equal(section(result,'DIALOGUE'),section(baseline,'DIALOGUE'),
          'Issue 6 exception failed to keep dialogue order '+page.id);
        stats.prose++;
      }
    }
    before+=baseline.length;after+=result.length;
    stats.balloons+=(page.dialogueInline||[]).length;
  }
  groups.push({issue:number,pages:pages.length,changed,saved:before-after});
  stats.pages+=pages.length;stats.before+=before;stats.after+=after;
}
assert.equal(stats.pages,285,'Unexpected Vikings Season 1 interior inventory');
assert.equal(stats.original,40,'Approved issues or deliberate exceptions changed');
assert.equal(stats.structured,20,'Unexpected Issue 3 structured scope');
assert.equal(stats.prose,225,'Unexpected Issues 4–12 prose scope');
assert(stats.before-stats.after>12000,'Sanitation regression: insufficient reduction');
const sample=json(base+'pages_i04_iron_worm.json').find(x=>x.id==='VIK_S1E04_P03');
const valid={...sample,promptPanelMode:'prose-numbered',promptDialogueMode:'grouped'};
const testShow={...list.find(s=>s.id==='vikings-2026-s1-e04')};
store.__show=testShow;
function invalid(page,message){assert.throws(()=>assemble(page,store,0),message)}
invalid({...valid,panelPlan:[...valid.panelPlan,undefined]},/requires nonempty authored string panels/);
invalid({...valid,promptPanelMode:'prose-numbered',dialogueInline:[{text:'bad',subtext:'Panel 999'}]},
  /valid Panel N ownership/);
invalid({...valid,promptDialogueMode:'invented'},/Invalid promptDialogueMode/);
invalid({...valid,promptPanelLetteringMode:'indexed'},/conflicts with indexed lettering/);
console.log('PASS Vikings season 1: '+stats.pages+' story pages, '+stats.original+
  ' protected, '+stats.structured+' clean structured, '+stats.prose+' numbered prose');
console.log('PASS no dialogue, scene actions, canonical cast, setting, continuity or layout lost; '+
  (stats.before-stats.after)+' recipe characters removed; '+stats.balloons+' original lettering items maintained');
console.log('Per issue: '+groups.map(x=>x.issue+':'+x.changed+' sanitized, '+x.saved+' chars saved').join('; '));
