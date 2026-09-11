#!/usr/bin/env python3
"""Emit decoded active Vikings 2026 Issues 2-5 production pages for review.
Temporary branch-only audit helper; remove before merge.
"""
from __future__ import annotations
import base64, gzip, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
shows=json.loads((ROOT/'data/shows.json').read_text(encoding='utf-8'))
base=ROOT/'data/shows/vikings-2026-s1'
out=[]

def load(path, enc):
    if enc=='gzip-base64':
        b64=''.join(path.read_text(encoding='utf-8').split())
        return json.loads(gzip.decompress(base64.b64decode(b64)).decode('utf-8'))
    return json.loads(path.read_text(encoding='utf-8'))

def pages(raw):
    if isinstance(raw,list): return raw
    if isinstance(raw,dict) and isinstance(raw.get('pages'),list): return raw['pages']
    if isinstance(raw,dict): return [dict({'id':k},**v) for k,v in raw.items()]
    return []

for show in shows:
    sid=str(show.get('id') or '')
    if sid not in {'vikings-2026-s1-e02','vikings-2026-s1-e03','vikings-2026-s1-e04','vikings-2026-s1-e05'}:
        continue
    for ov in show.get('sceneOverlays') or []:
        path=base/ov['file']
        raw=load(path, ov.get('encoding'))
        for page in pages(raw):
            pid=str(page.get('id') or '')
            if pid.startswith('VIK_'):
                out.append({'issueId':sid,'overlay':ov['file'],'page':page})

# De-duplicate by page ID using manifest order; active overlays are additive but current
# Vikings issue packages have unique page IDs within an issue.
seen=set(); unique=[]
for item in out:
    pid=item['page'].get('id')
    key=(item['issueId'],pid)
    if key in seen: continue
    seen.add(key); unique.append(item)

p=ROOT/'tmp/vikings_active_recipe_audit.json'
p.parent.mkdir(exist_ok=True)
p.write_text(json.dumps(unique,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Wrote {len(unique)} active Vikings production pages to {p}')
for item in unique:
    if item['page'].get('id')=='VIK_S1I02_P06':
        print('P06_AUDIT='+json.dumps(item,ensure_ascii=False))
