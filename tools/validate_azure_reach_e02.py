#!/usr/bin/env python3
import base64, gzip, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / 'data/shows/azure-reach-s1'
FILES = [f'encoded/pages_e02_p{a:02d}_p{b:02d}.json.gzb64' for a,b in ((1,6),(7,12),(13,18),(19,22))]


def decode(path):
    raw=''.join(path.read_text(encoding='utf-8').split())
    return json.loads(gzip.decompress(base64.b64decode(raw,validate=True)).decode('utf-8'))

pages=[]
for name in FILES:
    pages.extend(decode(SHOW/name))
assert len(pages)==22
assert [p['id'] for p in pages]==[f'AZR_S1E02_P{i:02d}' for i in range(1,23)]
assert all(p['episode']=='S1E02' and p['page']==i for i,p in enumerate(pages,1))
assert all(len(p['panelPlan'])==p['panelCount'] for p in pages)
assert all(p['dialogueInline'] for p in pages)

directions=json.loads((SHOW/'direction.json').read_text(encoding='utf-8'))
assert 'AZR_E02_CONTINUITY' in directions
for p in pages:
    refs=p.get('direction',[])
    assert 'AZR_PRODUCTION_CORE' in refs and 'AZR_LETTERING' in refs and 'AZR_E02_CONTINUITY' in refs
    assert not (set(refs)-set(directions))
    local=p.get('directionInline',[]) or []
    assert len(local)<=2
    assert p['summary'] not in json.dumps(local,ensure_ascii=False)
    for item in local:
        text=item.get('text','') if isinstance(item,dict) else str(item)
        assert text.startswith(('PAGE CONTINUITY —','PAGE DESIGN —'))

text=json.dumps(pages,ensure_ascii=False)
for required in ('Dolphin-shaped chicken nuggets.','Retrieval souvenirs.','Sea Turtle Tuesday.','Not a bad day for the Brine Squad.'):
    assert required in text, required
for forbidden in ('The Pelican Drop','retrieval rings'):
    assert forbidden not in text, forbidden

print('Azure Reach Issue 2 validation passed')
print('Pages:',len(pages))
print('Panels:',sum(p['panelCount'] for p in pages))
print('Dialogue/lettering entries:',sum(len(p['dialogueInline']) for p in pages))
