#!/usr/bin/env python3
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'data/shows/vikings-2026-s1'
OUT=BASE/'issue_06_assembled_audit.md'
CHUNKS=[BASE/f'pages_i06_p{a:02d}_p{b:02d}.json' for a,b in ((1,6),(7,12),(13,18),(19,24))]

def find_char(handle, chars):
    for e in chars.values():
        if isinstance(e,dict) and (e.get('handle')==handle or handle in (e.get('aliases') or [])):
            return e

def fmt_char(e,fallback):
    if not e:return fallback
    p=[e.get('name') or fallback]
    structured=bool(e.get('wardrobe') or e.get('performance') or e.get('relationship') or e.get('promptContinuity'))
    if e.get('handle'):p.append(e['handle'])
    v=e.get('visualAnchor') or e.get('visual') or e.get('appearance') or e.get('visualDescription')
    if v:p.append(('Identity: ' if structured else 'Visual: ')+v)
    if structured:
        if e.get('wardrobe'):p.append('Wardrobe: '+e['wardrobe'])
        if e.get('performance'):p.append('Performance: '+e['performance'])
        if e.get('relationship'):p.append('Relationship: '+e['relationship'])
        if e.get('promptContinuity'):p.append('Continuity: '+'; '.join(e['promptContinuity']))
    return ' — '.join(p)

def main():
    shows=json.loads((ROOT/'data/shows.json').read_text())
    show=next(x for x in shows if x.get('id')=='vikings-2026-s1-e06')
    chars=json.loads((BASE/'characters.json').read_text())
    pages=[]
    for f in CHUNKS:pages.extend(json.loads(f.read_text()))
    warnings=[]; blocks=[]
    abstract=re.compile(r'\b(realiz\w*|recogniz\w*|understand\w*|means?|meaning|because|rather than|instead of|represents?|proves?|shows that|symboli[sz]\w*|theme|reads as|feels like|demonstrates?|as if|genuinely|clearly|obviously|impulse|satisfied|interested|intends?|trying to|tries to|wants? to)\b',re.I)
    correction=re.compile(r'\b(do not imply|do not make|do not turn|not a|rather than|instead of|correction|avoid|should not)\b',re.I)
    for page in pages:
        out=[f"## {page['id']}",page.get('summary',''),show['generationLine']]
        out+=['','[SETTING]',page.get('settingText',''),'','[CHARACTERS]']
        for c in page.get('charactersInline',[]):
            e=find_char(c.get('handle'),chars);out.append(fmt_char(e,c.get('name') or c.get('handle')))
            if not e:warnings.append(f"{page['id']}: undefined character handle in charactersInline: {c.get('handle')}")
        out+=['','[PANEL PLAN]']
        for p in page.get('panelPlan',[]):
            out.append(json.dumps(p,ensure_ascii=False,separators=(',',':')))
            if abstract.search(str(p.get('action',''))):warnings.append(f"{page['id']} P{p.get('panel')}: ABSTRACT? {p.get('action')}")
        out+=['','[DIALOGUE]']
        for d in page.get('dialogueInline',[]):
            sp=d.get('handle') or d.get('speaker') or 'TEXT'
            out.append(f'{sp} says "{d.get("text","")}"')
            if isinstance(sp,str) and sp.startswith('@') and not find_char(sp,chars):
                warnings.append(f"{page['id']}: undefined dialogue handle: {sp}")
        if page.get('directionInline'):
            out+=['','[DIRECTION]']
            for x in page['directionInline']:
                out.append(str(x))
                if correction.search(str(x)):warnings.append(f"{page['id']}: CORRECTION-RESIDUE? {x}")
        blocks.append('\n'.join(out))
    header=['# Vikings Issue 6 exact assembled-output audit','',f'Pages: {len(pages)}',f'Panels: {sum(len(p.get("panelPlan",[])) for p in pages)}',f'Warnings: {len(warnings)}','','## WARNINGS']
    header += [f'- {w}' for w in warnings] or ['- none']
    OUT.write_text('\n'.join(header)+'\n\n# ASSEMBLED PAGES\n\n'+'\n\n'.join(blocks)+'\n',encoding='utf-8')
    print(f'wrote {OUT}; warnings={len(warnings)}')
if __name__=='__main__':main()
