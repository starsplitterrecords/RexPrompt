#!/usr/bin/env python3
import json
from pathlib import Path
base=Path('data/shows/vikings-2026-s1')
files=[base/'pages_i06_p01_p06.json',base/'pages_i06_p07_p12.json',base/'pages_i06_p13_p18.json',base/'pages_i06_p19_p24.json']
converted=0
for path in files:
    pages=json.loads(path.read_text(encoding='utf-8'))
    for page in pages:
        directions=page.get('directionInline')
        if not directions:
            continue
        out=[]
        for item in directions:
            if isinstance(item,str):
                out.append({'text':item})
                converted+=1
            elif isinstance(item,dict):
                out.append(item)
            else:
                raise SystemExit(f'Malformed directionInline entry on {page.get("id")}: {item!r}')
        page['directionInline']=out
    path.write_text(json.dumps(pages,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Converted {converted} Issue 6 direction notes to structured objects')
