#!/usr/bin/env python3
import base64, gzip, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SHOW=ROOT/'data/shows/vikings-2026-s1'
files=[SHOW/f'encoded/pages_e02_p{a:02d}_p{b:02d}.json.gzb64' for a,b in ((1,6),(7,12),(13,18),(19,24))]
pages=[]
for path in files:
    pages.extend(json.loads(gzip.decompress(base64.b64decode(''.join(path.read_text().split()),validate=True))))
assert len(pages)==24
assert [p['id'] for p in pages]==[f'VIK_S1E02_P{i:02d}' for i in range(1,25)]
assert all(p['episode']=='S1E02' and p['page']==i for i,p in enumerate(pages,1))
assert all(len(p['panelPlan'])==p['panelCount'] for p in pages)
assert all(len(p['directionInline'])==5 for p in pages)
assert all(p['dialogueInline'] for p in pages)
assert all(all(d['characterHandle']!='UNKNOWN' for d in p['dialogueInline']) for p in pages)
text=json.dumps(pages,ensure_ascii=False)
for required in ('A thrown turnip would breach it.','The grease makes excellent tracing parchment.','It demands a raider\'s share without raiding.','Today he does.','The first toast is owed to our creditor.'):
    assert required in text, required
for forbidden in ('cyberpunk architecture','neo-noir','murder-holes','mount the Coinstar\'s head'):
    assert forbidden not in text, forbidden
manifest=json.loads((SHOW/'source/manifest.json').read_text())
encoded=''.join(''.join((SHOW/'source'/name).read_text().split()) for name in manifest['orderedParts'])
decoded=gzip.decompress(base64.b64decode(encoded,validate=True))
assert len(decoded)==manifest['decodedBytes'] and len(decoded)>5_000_000
assert json.loads(decoded)['showCode']=='VIK'
print('Vikings 2026 Issue 2 validation passed')
print('Pages:',len(pages))
print('Panels:',sum(p['panelCount'] for p in pages))
print('Dialogue/lettering entries:',sum(len(p['dialogueInline']) for p in pages))
