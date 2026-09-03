#!/usr/bin/env python3
import base64, gzip, json, pathlib

root = pathlib.Path('data/shows/azure-reach-s1/encoded')
for path in [root / 'pages_e02_p01_p06.json.gzb64', root / 'pages_e02_p07_p12.json.gzb64']:
    raw = ''.join(path.read_text().split())
    pages = json.loads(gzip.decompress(base64.b64decode(raw)).decode())
    changed = False
    for page in pages:
        before = page.get('directionInline', [])
        after = [
            item for item in before
            if not str(item.get('text', '')).startswith('CAUSAL FUNCTION —')
        ]
        if after != before:
            page['directionInline'] = after
            changed = True
    if changed:
        payload = json.dumps(pages, ensure_ascii=False, separators=(',', ':')).encode()
        path.write_text(base64.b64encode(gzip.compress(payload, mtime=0)).decode())
        print('sanitized', path)
