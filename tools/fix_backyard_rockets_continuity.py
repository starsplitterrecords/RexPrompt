#!/usr/bin/env python3
"""Deterministically repair Backyard Rockets scene continuity from approved image canon.

Scene summary is the narrative authority inside each RexPrompt recipe. Legacy cinematic-beat,
dialogue, cast and continuity data that belongs to another scene is removed or rebuilt.
"""
import base64,gzip,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SHOW_ID='backyard-rockets-s1'
CANON={'Arvin':'@brk.Arvin','Milo':'@brk.Milo','Lucia':'@brk.Lucia','Cyrus':'@brk.Cyrus','Tamz':'@brk.Tamz'}
ALIASES={
'@starsplit.Arvin':'@brk.Arvin','@starsplit.arvin':'@brk.Arvin',
'@starsplit.Milo':'@brk.Milo','@starsplit.milo':'@brk.Milo',
'@starsplit.Lucia':'@brk.Lucia','@starsplit.lucia':'@brk.Lucia',
'@starsplit.Cyrus':'@brk.Cyrus','@starsplit.cyrus':'@brk.Cyrus','@starsplit.cyru':'@brk.Cyrus',
'@starsplit.Tamz':'@brk.Tamz','@starsplit.tamz':'@brk.Tamz'}
TEXT_FIXES={
'gutted, rusted fuel tanker':'converted, weathered fuel tanker',
'rusted fuel tanker':'weathered, maintained fuel tanker','rusted tanker':'weathered, maintained tanker',
'rust-streaked belly':'sun-weathered belly','junk-built rocket':'hand-built rocket assembled from maintained legacy aerospace hardware',
'rickety rocket':'hand-built rocket','scrap heap':'organized salvage stock','pile of scrap metal':'organized stack of salvage metal',
'tattered camouflage net':'sun-faded camouflage net','sprawling sea of industrial waste and jagged rebar':'organized salvage yard of decommissioned industrial frames and stacked structural steel',
'towering mess of rusted barrels and salvaged aerospace tubing':'towering hand-built assembly of maintained legacy pressure vessels and reclaimed aerospace tubing',
'oil drums and aerospace scrap':'legacy pressure vessels and reclaimed aerospace hardware','frayed nylon ropes and wooden beams':'weathered heavy-duty rigging and timber cribbing',
'discarded ceramic tiles':'salvaged refractory ceramic tiles','sleek, white armored interceptor vehicle':'sleek graphite Aegis interceptor vehicle',
'polished black armor':'matte graphite technical armor','white armored interceptor':'graphite Aegis interceptor',
"The synthetic skin of Arvin's hand":"The synthetic skin on the back of Arvin's RIGHT hand"}

def load(path): return json.loads(path.read_text(encoding='utf-8'))
def norm(raw):
    if isinstance(raw,list): return raw
    return [{'id':k,**v} if isinstance(v,dict) else {'id':k,'value':v} for k,v in (raw or {}).items()]
def read(path,enc=None):
    if enc=='gzip-base64':
        b=''.join(path.read_text().split()); return json.loads(gzip.decompress(base64.b64decode(b,validate=True)).decode())
    return load(path)
def write(path,data,enc=None):
    raw=json.dumps(data,ensure_ascii=False,separators=(',',':')).encode()
    if enc=='gzip-base64': path.write_text(base64.b64encode(gzip.compress(raw,9,mtime=0)).decode(),encoding='utf-8')
    else: path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def fixstr(t):
    for a,b in sorted(ALIASES.items(),key=lambda x:-len(x[0])): t=t.replace(a,b)
    t=re.sub(r'@starsplit\b','',t,flags=re.I)
    for a,b in TEXT_FIXES.items(): t=t.replace(a,b)
    t=t.replace('holographic projector','optical projection unit')
    t=re.sub(r' +([,.])',r'\1',t); t=re.sub(r' {2,}',' ',t)
    return t.strip()
def strings(x):
    if isinstance(x,str): return fixstr(x)
    if isinstance(x,list): return [strings(v) for v in x]
    if isinstance(x,dict): return {k:strings(v) for k,v in x.items()}
    return x
def mentions(text,name): return bool(re.search(rf'(?<![A-Za-z]){name}(?![A-Za-z])|{re.escape(CANON[name])}',text,re.I))
def sentences(text): return re.split(r'(?<=[.!?])\s+',text.strip())
def cast(scene):
    s=scene.get('summary',''); names=[n for n in CANON if mentions(s,n)]
    if not names:return []
    first=min(((m.start(),n) for n in CANON for m in [re.search(rf'(?<![A-Za-z]){n}(?![A-Za-z])|{re.escape(CANON[n])}',s,re.I)] if m),default=(9999,None))[1]
    if 'Cyrus' in names and len(names)>1:
        co=[r'Arvin and Cyrus',r'Cyrus and Arvin',r'Lucia and Cyrus',r'Cyrus and Lucia',r'Milo and Cyrus',r'Cyrus and Milo',r'Lucia meets Cyrus',r'Cyrus approaches',r'Cyrus walks .*?Arvin',r'Cyrus stops .*?Arvin',r'Cyrus emerges .*?Arvin',r'Cyrus stands .*?Arvin',r'Arvin stands .*?Cyrus',r'face[- ]to[- ]face',r'opposite sides of a narrow canyon',r'approaches with a drawn']
        if not any(re.search(p,s,re.I|re.S) for p in co): names=['Cyrus'] if first=='Cyrus' else [n for n in names if n!='Cyrus']
    return [n for n in CANON if n in names]
def subject_before(summary,pos):
    subject=None
    for sent in sentences(summary[:pos]):
        st=sent.strip(); m=re.match(r'^(?:Dialogue:\s*)?(Arvin|Milo|Lucia|Cyrus|Tamz)\b',st,re.I)
        if m: subject=m.group(1).title(); continue
        if re.match(r'^(He|She)\b',st,re.I): continue
        m=re.search(r'^(?:[^,]{0,140},\s*)?(Arvin|Milo|Lucia|Cyrus|Tamz)\b',st,re.I)
        if m: subject=m.group(1).title()
    return subject
def dialogue(scene,present):
    s=scene.get('summary',''); m=re.search(r'[“"]([^"”]{3,350})[”"]',s)
    if not m:return []
    quote=m.group(1).strip(); before=s[:m.start()]; after=s[m.end():m.end()+110]; speaker=None
    a=re.search(r'(Arvin|Milo|Lucia|Cyrus|Tamz)\s+(?:says|whispers|notes|declares|replies|asks)',after,re.I)
    if a:speaker=a.group(1).title()
    if not speaker:
        a=re.search(r'(Arvin|Milo|Lucia|Cyrus|Tamz)\s+(?:says|whispers|notes|declares|replies|asks)\s*:?\s*$',before,re.I)
        if a:speaker=a.group(1).title()
    if not speaker:speaker=subject_before(s,m.start())
    if speaker not in present:speaker=None
    if not speaker and len(present)==1:speaker=present[0]
    if not speaker:
        addressed=[n for n in present if re.search(rf'\b{n}\b',quote,re.I)]
        if len(present)==2 and len(addressed)==1:speaker=next(n for n in present if n!=addressed[0])
    if not speaker and present:speaker=present[0]
    return [{'handle':CANON[speaker],'speaker':speaker,'text':quote}] if speaker else []
def continuity(text,present):
    if not text.startswith('CONTINUITY'):return text
    if ':' in text: head,body=text.split(':',1)
    else:
        m=re.match(r'^(CONTINUITY\s*[—-])\s*(.*)$',text)
        if not m:return text
        head,body=m.group(1),m.group(2)
    keep=[]
    for c in [x.strip() for x in body.split('|') if x.strip()]:
        named=[n for n in CANON if mentions(c,n)]
        if any(n not in present for n in named):continue
        keep.append(c)
    return head.rstrip(' —-')+': '+' | '.join(keep) if keep else ''
def patch(scene):
    s=strings(scene); present=cast(s)
    if 'charactersInline' in s:s['charactersInline']=[{'name':n,'handle':CANON[n]} for n in present]
    if 'characters' in s:s['characters']=[CANON[n] for n in present]
    if 'dialogueInline' in s:s['dialogueInline']=dialogue(s,present)
    fac=[]
    if any(n in present for n in ('Arvin','Milo','Lucia','Tamz')):fac.append('BR_Salvagers')
    if 'Cyrus' in present:fac.append('BR_Aegis')
    if 'factions' in s:s['factions']=fac
    dirs=[]
    for x in s.get('directionInline',[]) or []:
        if not isinstance(x,dict) or 'text' not in x:dirs.append(x);continue
        t=x['text']; named=[n for n in CANON if mentions(t,n)]; extra=[n for n in named if n not in present]
        if t.startswith('CONTINUITY'):
            t=continuity(t,present)
            if t:dirs.append({**x,'text':t})
        elif extra and not t.startswith('BACKYARD ROCKETS VISUAL LANGUAGE'):continue
        else:dirs.append(x)
    s['directionInline']=dirs
    return s

shows=load(ROOT/'data/shows.json'); show=next(s for s in shows if s.get('id')==SHOW_ID); base=ROOT/show['basePath']
files=[(show.get('scenesFile','scenes_base.json'),None)]+[(o['file'],o.get('encoding')) for o in show.get('sceneOverlays',[])]
count=0
for rel,enc in files:
    path=base/rel; data=norm(read(path,enc)); fixed=[patch(s) for s in data]; write(path,fixed,enc); count+=len(fixed)
print('Repaired',count,'Backyard Rockets scene recipes across',len(files),'files')
