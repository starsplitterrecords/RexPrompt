#!/usr/bin/env python3
import json,re
from pathlib import Path
base=Path('data/shows/vikings-2026-s1')
files=[base/'pages_i06_p01_p06.json',base/'pages_i06_p07_p12.json',base/'pages_i06_p13_p18.json',base/'pages_i06_p19_p24.json']
seen=[]
for path in files:
    pages=json.loads(path.read_text(encoding='utf-8'))
    for page in pages:
        m=re.fullmatch(r'VIK_S1I06_P(\d{2})',page.get('id',''))
        if not m:
            raise SystemExit(f'Unexpected Issue 6 page id: {page.get("id")}')
        n=int(m.group(1))
        page['page']=n
        seen.append(n)
    path.write_text(json.dumps(pages,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if sorted(seen)!=list(range(1,25)):
    raise SystemExit(f'Expected pages 1-24 exactly, got {sorted(seen)}')
print('Added explicit page numbers to all 24 Issue 6 production pages')
