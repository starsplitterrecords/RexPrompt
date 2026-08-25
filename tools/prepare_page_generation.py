#!/usr/bin/env python3
from __future__ import annotations
import base64,gzip,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; MANIFEST=ROOT/'data/shows.json'; INDEX=ROOT/'index.html'
def load(p): return json.loads(p.read_text(encoding='utf-8'))
def dump(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def dec(p):
    s=''.join(p.read_text().split()).rstrip('='); s+='='*((4-len(s)%4)%4)
    return json.loads(gzip.decompress(base64.b64decode(s)).decode())
def enc(p,v):
    raw=json.dumps(v,ensure_ascii=False,separators=(',',':')).encode(); p.write_text(base64.b64encode(gzip.compress(raw,9,mtime=0)).decode())

# Division Threshold: compile the existing 26-page Draft 01 without inventing story.
DT={'OSTRA':('Ostra-9','@dt.Ostra9'),'JOHN':('John Mercer','@dt.JohnMercer'),'KELLEN':('Kellen Cartwright','@dt.KellenCartwright'),'AX10M':('AX10M','@dt.AX10M'),'NICO':('Nico-14','@dt.Nico14'),'NATHAN':('Nathan Price','@dt.NathanPrice'),'RINN':('Director Rinn','@dt.Rinn'),'SAEL':('Mr. Sael','@dt.Sael')}
def dt_place(n):
    m={5:'DT_Checkpoint9',6:'DT_Checkpoint9',7:'DT_Overpass',8:'DT_Overpass',9:'DT_Overpass',10:'DT_OversightOffice',11:'DT_AugmentClinic',12:'DT_OrganicSafehouse',13:'DT_OrganicSafehouse',14:'DT_OversightOffice',15:'DT_DataCore',16:'DT_Overpass',17:'DT_Overpass',18:'DT_TransitSpine',19:'DT_TransitSpine',20:'DT_TransitSpine',21:'DT_WhiteFacility',22:'DT_WhiteFacility',23:'DT_WhiteFacility',24:'DT_WhiteFacility',25:'DT_SharedDistrictRooftop'}
    if n in m: return {'setting':m[n],'region':'DT_GovernanceUpperLevels' if n in (10,14,15) else ('DT_OrganicDistricts' if n in (12,13) else 'DT_Stack')}
    if n==4:return {'settingText':'The Stack in full civic scale: layered old and new infrastructure, transit, service volumes, neighborhoods and towers.','region':'DT_Stack'}
    if n==1:return {'settingText':'Historical human trauma bay after an industrial accident; recognizable advanced medical environment, not superheroic.','regionText':'Historical pre-Stack human infrastructure.'}
    if n==2:return {'settingText':'Historical hazardous industrial zone and adjacent advanced Organosynthetic growth facility.','regionText':'Historical pre-Stack industrial infrastructure.'}
    if n==3:return {'settingText':'Historical city-grid control room with a vast machine intelligence coordinating infrastructure.','regionText':'Historical pre-Stack civic infrastructure.'}
    return {'settingText':'Unseen control and monitoring layer connected to the incident-generation system.','regionText':'Unknown location within or beyond the Stack.'}
def dt_panels(n,b):
    q=[m.group(1).strip() for m in re.finditer(r'(?m)^\d+\.\s+(.+)$',b)]
    if q:return q
    if n==4:
        m=re.search(r'(?m)^Full-page reveal of (.+)$',b); return ['Full-page reveal of '+m.group(1).strip()] if m else []
    if n==26:
        return [f'{x} tier: '+re.search(rf'(?m)^{x}:\s*(.+)$',b).group(1).strip() for x in ('Top','Middle','Bottom')]
    return []
def dt_dialogue(b):
    out=[]; seen=set(); panel=None
    labels='CAPTION(?:\\s+\\d+)?|OSTRA|KELLEN|RINN|JOHN|NATHAN|NICO|SAEL|AX10M|TECHNICIAN|SECURITY|SYSTEM'
    pat=re.compile(rf'(?i)\b({labels})(?:\s*,\s*[^:]{{0,60}})?\s*:\s*(.*?)(?=\s+(?:{labels})(?:\s*,\s*[^:]{{0,60}})?\s*:|$)')
    prose=re.compile(r'(?i)\b(Ostra|Kellen|John|Nathan|Nico|Sael|Rinn|AX10M)\b[^:\n]{0,80}:\s*([^:\n]+)$')
    for raw in b.splitlines():
        s=raw.strip(); num=re.match(r'^(\d+)\.\s+(.+)$',s)
        if num: panel=int(num.group(1)); s=num.group(2)
        hits=list(pat.finditer(s));
        if not hits:
            m=prose.search(s); hits=[m] if m else []
        for m in hits:
            sp=re.sub(r'\s+\d+$','',m.group(1).upper()); text=m.group(2).strip().strip('“”"')
            if not text: continue
            d={'text':text}; d['handle' if sp in DT else 'speaker']=DT[sp][1] if sp in DT else sp
            if panel:d['subtext']=f'Panel {panel}'
            k=(d.get('handle') or d.get('speaker'),text,d.get('subtext'))
            if k not in seen:seen.add(k);out.append(d)
    return out
def division():
    d=ROOT/'data/shows/division-threshold-s1'; t=(d/'issue_01_draft_01.md').read_text(); heads=list(re.finditer(r'(?m)^### PAGE (\d+) — (.+)$',t)); assert len(heads)==26
    pages=[]
    for i,h in enumerate(heads):
        n=int(h.group(1)); end=heads[i+1].start() if i+1<len(heads) else t.find('\n## Character movement',h.end()); b=t[h.end():end if end>0 else len(t)]; panels=dt_panels(n,b); assert panels
        pur=re.search(r'(?m)^Purpose:\s*(.+)$',b); page={'id':f'DT_E001_P{n:02d}','episode':'S1E01','issue':'Issue #1 — Purpose Updated','page':n,'pageTitle':h.group(2).strip().title(),'panelCount':len(panels),'summary':pur.group(1).strip() if pur else h.group(2).strip(),'source':'Division Threshold — Issue #1: Purpose Updated — Draft 01, 2026-08-24','panelPlan':[{'text':f'Panel {j+1} — {x}'} for j,x in enumerate(panels)],'dialogueInline':dt_dialogue(b),**dt_place(n)}
        cast=[]
        for key,(name,handle) in DT.items():
            if re.search(rf'\b(?:{re.escape(name)}|{key})\b',b,re.I):cast.append({'name':name,'handle':handle})
        if cast:page['charactersInline']=cast
        pages.append(page)
    dump(d/'pages_e01_compiled.json',pages)

# Low Tide Signal: expose only actual Chapters 1-3 pages and make exact lettering assembler-readable.
LTS={'matt':'Matt Donnelly','ryan':'Ryan Kelleher','chris':'Chris Barlow','justin':'Justin Rourke','nicole':'Nicole Hanley','kevin':'Kevin Marsh','caption':'CAPTION','system':'SYSTEM','screen':'SCREEN','display':'DISPLAY','message':'MESSAGE','groupchat':'GROUP CHAT','monitor':'MONITOR','sign':'SIGN','sfx':'SFX','map':'MAP','tideboard':'TIDE BOARD'}
def low_tide():
    d=ROOT/'data/shows/low-tide-signal'; src=load(d/'pages_ch01_ch03.json'); out=[]
    for p in src:
        assert p.get('unit')=='PAGE'; q=dict(p); lines=[]
        for item in q.pop('dialogue',[]) or []:
            assert isinstance(item,dict) and len(item)==1; k,v=next(iter(item.items())); lines.append({'speaker':LTS.get(str(k).lower(),str(k).replace('_',' ').upper()),'text':str(v)})
        q['dialogueInline']=lines; notes=q.pop('productionNotes',[]) or []
        if notes:q['directionInline']=[{'text':str(x)} for x in notes]
        q['source']='Low Tide Signal — Chapters 1–3 graphic page treatment'; out.append(q)
    dump(d/'pages_ch01_ch03_compiled.json',out)

# Vikings: repair source payloads, remove repeated reader-function boilerplate, and bind dialogue to panels.
def historical(p):
    vals={}
    for c in subprocess.check_output(['git','log','--all','--format=%H','--',str(p.relative_to(ROOT))],text=True).splitlines():
        try:
            s=subprocess.check_output(['git','show',f'{c}:{p.relative_to(ROOT)}'],text=True,stderr=subprocess.DEVNULL); raw=''.join(s.split()).rstrip('='); raw+='='*((4-len(raw)%4)%4); v=json.loads(gzip.decompress(base64.b64decode(raw)).decode()); vals.setdefault(json.dumps(v,sort_keys=True,ensure_ascii=False),v)
        except Exception:pass
    if len(vals)!=1:raise RuntimeError(f'{p.name}: ambiguous historical recovery ({len(vals)} variants)')
    return next(iter(vals.values()))
def strip_reader(v):
    if isinstance(v,list):return [strip_reader(x) for x in v]
    if isinstance(v,dict):
        return {k:strip_reader(x) for k,x in v.items() if re.sub('[^a-z]','',str(k).lower())!='readerfunction' and not(isinstance(x,str) and x.strip()=='Advance the beat clearly; preserve speaker identity and natural balloon order.')}
    return v
def vikings():
    for p in sorted((ROOT/'data/shows/vikings-2026-s1/encoded').glob('pages_*.json.gzb64')):
        try:pages=dec(p)
        except Exception:pages=historical(p)
        fixed=[]
        for page in pages:
            q=strip_reader(page); lines=q.get('dialogueInline',[]) or []; inds=[]
            for pan in q.get('panelPlan',[]) or []:
                if isinstance(pan,dict):inds += [x for x in (pan.get('dialogueIndices') or pan.get('dialogue_indices') or []) if isinstance(x,int)]
            one=bool(inds) and 0 not in inds and min(inds)>=1 and max(inds)<=len(lines); mp={}
            for pn,pan in enumerate(q.get('panelPlan',[]) or [],1):
                if not isinstance(pan,dict):continue
                for x in pan.get('dialogueIndices') or pan.get('dialogue_indices') or []:
                    i=x-1 if one else x
                    if isinstance(i,int) and 0<=i<len(lines):mp[i]=pn
            for i,line in enumerate(lines):
                if isinstance(line,dict):
                    if not line.get('handle') and line.get('characterHandle'):line['handle']=line['characterHandle']
                    if i in mp:line['subtext']=f'Panel {mp[i]}'
            fixed.append(q)
        enc(p,fixed)

def manifest():
    s=load(MANIFEST); b={x.get('id'):x for x in s}
    x=b['backyard-rockets-s1'];x['unitLabel']='PAGE';x['generationLine']='Finished full-color portrait comic page for Backyard Rockets. Bright prestige science fiction rooted in the American Southwest; clean maintained retrofuturist aerospace hardware, clear physical engineering, exact character identity and exact lettering. Fictional production.'
    x=b['division-threshold-s1'];x['name']='Division Threshold — Issue 1 — Purpose Updated';x['scenesFile']='pages_e01_compiled.json';x['unitLabel']='PAGE'
    x=b['low-tide-signal'];x['name']='Low Tide Signal — Chapters 1–3 Production';x['scenesFile']='pages_base.json';x['sceneOverlays']=[{'file':'pages_ch01_ch03_compiled.json'}];x['unitLabel']='PAGE'
    x=b['rex-fleet-s1'];x['unitLabel']='SCENE';x['generationLine']='Prestige full-color comic-book sequential-art scene. Preserve scripted action, character identity, continuity, and exact lettering. Fictional production.'
    dump(MANIFEST,s)
def assembler():
    t=INDEX.read_text(); old='function joinPath(base,file){return String(base||"data").replace(/\\/$/,"")+"/"+file}function getHandle(id,c){const e=c[id];return e?e.handle||e.name||id:id}function formatEntry(e){if(typeof e==="string")return e;if(e.text)return e.text;if(e.name)return e.name;if(e.summary)return e.summary;return JSON.stringify(e)}function normalizeScenes(raw){if(Array.isArray(raw))return raw;return Object.entries(raw||{}).map(([id,scene])=>({id,...scene}))}'; new='function joinPath(base,file){return String(base||"data").replace(/\\/$/,"")+"/"+file}function getHandle(id,c){const e=c[id];return e?e.handle||e.name||id:id}function formatEntry(e){if(typeof e==="string")return e;if(e.text)return e.text;if(e.name)return e.name;if(e.summary)return e.summary;return JSON.stringify(e)}function findCharacterByHandle(h,c){if(!h)return null;return Object.values(c||{}).find(e=>e&&(e.handle===h||(Array.isArray(e.aliases)&&e.aliases.includes(h))))}function formatCharacter(e,fallback){if(!e)return fallback;const p=[e.name||fallback];if(e.handle)p.push(e.handle);const v=e.visualAnchor||e.visual||e.appearance||e.visualDescription;if(v)p.push("Visual: "+v);if(e.visualStatus)p.push("Visual status: "+e.visualStatus);if(Array.isArray(e.continuityLocks)&&e.continuityLocks.length)p.push("Continuity: "+e.continuityLocks.join("; "));return p.join(" — ")}function normalizeScenes(raw){if(Array.isArray(raw))return raw;return Object.entries(raw||{}).map(([id,scene])=>({id,...scene}))}'
    if old in t:t=t.replace(old,new)
    elif 'function formatCharacter' not in t:raise RuntimeError('assembler helper mismatch')
    a='if(s.dialogueInline?.length)s.dialogueInline.forEach(d=>cameos.add(d.handle||d.speaker));else s.dialog?.forEach(k=>{const d=store["dialogue.json"]?.[k];if(d)cameos.add(getHandle(d.speakerId,store["characters.json"]||{}))});'; z='if(s.dialogueInline?.length)s.dialogueInline.forEach(d=>{const h=d.handle||d.speaker;if(typeof h==="string"&&h.startsWith("@"))cameos.add(h)});else s.dialog?.forEach(k=>{const d=store["dialogue.json"]?.[k];if(d)cameos.add(getHandle(d.speakerId,store["characters.json"]||{}))});'; t=t.replace(a,z) if a in t else t
    a='if(s.charactersInline?.length){out.push("\\n[CHARACTERS]");s.charactersInline.forEach(c=>out.push(c.name||c.handle))}else if(s.characters?.length){out.push("\\n[CHARACTERS]");s.characters.forEach(k=>{const e=store["characters.json"]?.[k];if(e)out.push(formatEntry(e))})}'; z='if(s.charactersInline?.length){out.push("\\n[CHARACTERS]");s.charactersInline.forEach(c=>{const e=findCharacterByHandle(c.handle,store["characters.json"]||{});out.push(formatCharacter(e,c.name||c.handle))})}else if(s.characters?.length){out.push("\\n[CHARACTERS]");s.characters.forEach(k=>{const e=store["characters.json"]?.[k];if(e)out.push(formatCharacter(e,k))})}';
    if a in t:t=t.replace(a,z)
    elif z not in t:raise RuntimeError('assembler character mismatch')
    a='s.dialogueInline.forEach(d=>{out.push((d.handle||d.speaker)+\' says "\'+(d.text||\'\')+\'"\');if(d.subtext)out.push("  ("+d.subtext+")")})'; z='s.dialogueInline.forEach(d=>{const sp=d.handle||d.speaker||\'TEXT\',label=/^(CAPTION|SYSTEM|SCREEN|DISPLAY|MESSAGE|GROUP CHAT|MONITOR|SIGN|SFX|MAP|TIDE BOARD|SECURITY|TECHNICIAN)$/.test(sp);out.push(label?sp+\': "\'+(d.text||\'\')+\'"\':sp+\' says "\'+(d.text||\'\')+\'"\');if(d.subtext)out.push("  ("+d.subtext+")")})'
    if a in t:t=t.replace(a,z)
    elif z not in t:raise RuntimeError('assembler dialogue mismatch')
    marker='if(s.direction?.length||s.directionInline?.length){out.push("\\n[DIRECTION]")'; c='if(s.continuityFrom)out.push("\\n[CONTINUITY]\\nContinue directly from "+s.continuityFrom+"; preserve established positions, props, damage, eyelines, and emotional state.");'
    if c not in t:
        if marker not in t:raise RuntimeError('assembler direction mismatch')
        t=t.replace(marker,c+marker)
    INDEX.write_text(t)
def verify():
    b={x.get('id'):x for x in load(MANIFEST)}; assert b['backyard-rockets-s1']['unitLabel']=='PAGE'; assert b['division-threshold-s1']['scenesFile']=='pages_e01_compiled.json'; assert b['low-tide-signal']['sceneOverlays']==[{'file':'pages_ch01_ch03_compiled.json'}]
    d=load(ROOT/'data/shows/division-threshold-s1/pages_e01_compiled.json'); assert len(d)==26 and [x['page'] for x in d]==list(range(1,27)) and all(len(x['panelPlan'])==x['panelCount'] for x in d)
    l=load(ROOT/'data/shows/low-tide-signal/pages_ch01_ch03_compiled.json'); assert l and all(x.get('unit')=='PAGE' and 'dialogueInline' in x for x in l)
    vv=[]
    for p in sorted((ROOT/'data/shows/vikings-2026-s1/encoded').glob('pages_*.json.gzb64')):vv+=dec(p)
    txt=json.dumps(vv); assert 'Reader Function' not in txt and 'readerFunction' not in txt
    for p in vv:
        for x in p.get('dialogueInline',[]) or []:
            if isinstance(x,dict) and x.get('characterHandle'):assert x.get('handle')==x.get('characterHandle')
    t=INDEX.read_text(); assert 'function formatCharacter' in t and 'visualAnchor' in t and 'if(s.continuityFrom)' in t
if __name__=='__main__':division();low_tide();vikings();manifest();assembler();verify();print('Page-generation preparation passed')
