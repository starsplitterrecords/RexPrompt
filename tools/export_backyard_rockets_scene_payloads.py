#!/usr/bin/env python3
import base64, gzip, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
shows=json.loads((ROOT/'data/shows.json').read_text())
show=next(s for s in shows if s.get('id')=='backyard-rockets-s1')
base=ROOT/show['basePath']

def norm(raw):
    if isinstance(raw,list): return raw
    return [{'id':k,**v} if isinstance(v,dict) else {'id':k,'value':v} for k,v in (raw or {}).items()]

def read_overlay(path,encoding=None):
    if encoding=='gzip-base64':
        b64=''.join(path.read_text().split())
        return json.loads(gzip.decompress(base64.b64decode(b64,validate=True)).decode())
    return json.loads(path.read_text())

groups=[]
base_file=show.get('scenesFile','scenes_base.json')
groups.append({'file':base_file,'encoding':None,'scenes':norm(json.loads((base/base_file).read_text()))})
for o in show.get('sceneOverlays',[]):
    raw=read_overlay(base/o['file'],o.get('encoding'))
    excluded=set(o.get('excludeIds',[]))
    scenes=[s for s in norm(raw) if s.get('id') not in excluded]
    groups.append({'file':o['file'],'encoding':o.get('encoding'),'scenes':scenes})
(ROOT/'backyard-rockets-scene-payloads.json').write_text(json.dumps({'groups':groups},indent=2,ensure_ascii=False))
print(sum(len(g['scenes']) for g in groups),'scenes exported from',len(groups),'source groups')
