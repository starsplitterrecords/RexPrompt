#!/usr/bin/env python3
import json
from pathlib import Path
p=Path('data/shows.json')
shows=json.loads(p.read_text(encoding='utf-8'))
source=next(s for s in shows if s.get('id')=='vikings-2026-s1-e05')
target=next(s for s in shows if s.get('id')=='vikings-2026-s1-e06')
target['generationLine']=source['generationLine']
active=[s for s in shows if str(s.get('id','')).startswith('vikings-2026-s1-')]
lines={s.get('generationLine') for s in active}
if None in lines or len(lines)!=1:
    raise SystemExit(f'Vikings generation contracts still differ: {len(lines)}')
p.write_text(json.dumps(shows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Issue 6 now shares the exact active Vikings generation contract')
