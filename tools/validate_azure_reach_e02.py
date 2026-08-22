#!/usr/bin/env python3
import base64, gzip, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SHOW=ROOT/'data/shows/azure-reach-s1'
files=[f'encoded/pages_e02_p{a:02d}_p{b:02d}.json.gzb64' for a,b in ((1,6),(7,12),(13,18),(19,22))]
pages=[]
for name in files:
    raw=''.join((SHOW/name).read_text().split())
    pages.extend(json.loads(gzip.decompress(base64.b64decode(raw,validate=True))))
assert len(pages)==22
assert [p['id'] for p in pages]==[f'AZR_S1E02_P{i:02d}' for i in range(1,23)]
assert all(p['episode']=='S1E02' and p['page']==i for i,p in enumerate(pages,1))
assert all(len(p['panelPlan'])==p['panelCount'] for p in pages)
assert all(len(p['directionInline'])==5 for p in pages)
assert all(p['dialogueInline'] for p in pages)
assert all(p['summary'] in p['directionInline'][1]['text'] for p in pages)
text=json.dumps(pages,ensure_ascii=False)
for required in ('Dolphin-shaped chicken nuggets.','Retrieval souvenirs.','Sea Turtle Tuesday.','Not a bad day for the Brine Squad.'):
    assert required in text, required
for forbidden in ('The Pelican Drop','retrieval rings'):
    assert forbidden not in text, forbidden
print('Azure Reach Issue 2 validation passed')
print('Pages:',len(pages))
print('Panels:',sum(p['panelCount'] for p in pages))
print('Dialogue/lettering entries:',sum(len(p['dialogueInline']) for p in pages))
