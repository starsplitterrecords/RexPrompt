#!/usr/bin/env python3
"""Flag active Vikings recipe text that is interpretive instead of drawable.
Temporary branch-only audit helper; remove before merge.
"""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
items=json.loads((ROOT/'tmp/vikings_active_recipe_audit.json').read_text(encoding='utf-8'))
ABSTRACT=[
 'reads as','read as','problem rather than','question of authority','grand framing','register','represents','symbol','symbolic','sovereignty','legibility','institutional','dramatic','stakes','the idea','the point','the joke','the comedy','turns the','reframes','functions as','means that','shows that','establishes that','proves that','becomes a','becomes an','as evidence','case language','integration','assimilation','status pressure','power dynamic','authority','spectacle','rather than a','rather than an'
]
flags=[]
for item in items:
    p=item['page']; pid=p.get('id',''); issue=item['issueId']
    summary=str(p.get('summary') or '')
    hits=[k for k in ABSTRACT if k in summary.lower()]
    if hits or len(summary)>210:
        flags.append({'id':pid,'field':'summary','hits':hits,'text':summary})
    for panel in p.get('panelPlan') or []:
        if not isinstance(panel,dict): continue
        action=str(panel.get('action') or ''); loc=str(panel.get('location') or '')
        hits=[k for k in ABSTRACT if k in action.lower()]
        if hits:
            flags.append({'id':pid,'field':f"panel{panel.get('panel')}.action",'hits':hits,'text':action})
        if len(loc)>110 or re.match(r'^(For a beat|Exterior establishes|The |A |Carrie |Bjorn |Gunnar )',loc):
            flags.append({'id':pid,'field':f"panel{panel.get('panel')}.location",'hits':['location-not-place'],'text':loc})
        if issue in {'vikings-2026-s1-e02','vikings-2026-s1-e03'}:
            low=action.lower()
            if any(x in low for x in ('a kin member','one kin member','one of the kin','a member of the kin')):
                flags.append({'id':pid,'field':f"panel{panel.get('panel')}.earlyKin",'hits':['early-kin-individualized'],'text':action})
# de-dupe exact field/text
seen=set(); out=[]
for f in flags:
    key=(f['id'],f['field'],f['text'])
    if key not in seen:
        seen.add(key); out.append(f)
path=ROOT/'tmp/vikings_recipe_flags.json'
path.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Flagged {len(out)} fields')
print(json.dumps(out,ensure_ascii=False,indent=2))
