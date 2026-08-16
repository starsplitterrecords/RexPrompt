#!/usr/bin/env python3
import base64,gzip,json,re,sys
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SHOW_ID="backyard-rockets-s1"
MANIFEST=ROOT/"data/shows.json"
REPORT=ROOT/"backyard-rockets-continuity-report.json"
P={"Arvin":"@brk.Arvin","Milo":"@brk.Milo","Lucia":"@brk.Lucia","Cyrus":"@brk.Cyrus","Tamz":"@brk.Tamz"}
SALV={"Arvin","Milo","Lucia","Tamz"}
VOICE_REWRITES=json.loads((ROOT/"data/shows/backyard-rockets-s1/dialogue-voice-rewrites.json").read_text(encoding="utf-8"))

def load(p): return json.loads(p.read_text(encoding="utf-8"))
def norm(x):
    if isinstance(x,list): return x
    return [{"id":k,**v} if isinstance(v,dict) else {"id":k,"value":v} for k,v in (x or {}).items()]
def enc(p): return json.loads(gzip.decompress(base64.b64decode("".join(p.read_text().split()),validate=True)).decode())
def ep(s):
    if s.get("episode"): return s["episode"]
    m=re.search(r"S1E\d{2}",s.get("id","")); return m.group(0) if m else "UNKNOWN"
def text(v):
    if isinstance(v,str): return v
    if isinstance(v,list): return "\n".join(text(x) for x in v)
    if isinstance(v,dict): return "\n".join(text(x) for x in v.values())
    return ""
def quotes(t): return [m.group(1).strip() for m in re.finditer(r'[“\"]([^\"”]{3,350})[”\"]',t)]
def noquotes(t): return re.sub(r'[“\"]([^\"”]*)[”\"]',' ',t)
def narrative_names(summary):
    t=noquotes(summary)
    return [n for n,h in P.items() if re.search(rf'(?<![A-Za-z]){n}(?![A-Za-z])|{re.escape(h)}',t,re.I)]

def ordered_unique(xs):
    out=[]
    for x in xs:
        if x not in out: out.append(x)
    return out

shows=load(MANIFEST)
show=next(s for s in shows if s.get("id")==SHOW_ID)
base=ROOT/show["basePath"]
base_scenes=norm(load(base/show.get("scenesFile","scenes_base.json")))
scenes=list(base_scenes)
groups=[(show.get("scenesFile","scenes_base.json"),base_scenes)]
for o in show.get("sceneOverlays",[]):
    p=base/o["file"]
    inc=norm(enc(p) if o.get("encoding")=="gzip-base64" else load(p))
    exc=set(o.get("excludeIds",[]))
    inc=[s for s in inc if s.get("id") not in exc]
    scenes.extend(inc); groups.append((o["file"],inc))

chars=load(base/"characters.json")
handles={v.get("handle") for v in chars.values() if isinstance(v,dict) and v.get("handle")}
issues=[];rows=[]
legacy=[
(r"left[- ]hand[^.;]{0,30}(?:synthetic|graft)|(?:synthetic|graft)[^.;]{0,30}left[- ]hand","Arvin left-hand graft conflict"),
(r"\b(?:junk-built|scrap-built|rickety) rocket\b","obsolete junk-built rocket language"),
(r"\b(?:gutted fuel tanker|rusted tanker|rusted fuel tanker|oil-slicked belly)\b","obsolete decay-led tanker language"),
(r"\b(?:tattered camouflage net|graveyard of fallen communications towers|primitive control console)\b","obsolete post-apocalyptic production language"),
(r"\b(?:white armored interceptor|chrome-and-white armor|bulky fantasy plating)\b","obsolete Cyrus/Tethergrid design language"),
(r"\b(?:smartphone|iphone|android phone|macbook|ultrabook|gaming laptop)\b","wrong consumer-device era language")]

for file,group in groups:
    for s in group:
        sid=s.get("id","<missing>");e=ep(s);summary=s.get("summary","");alltxt=text(s)
        for h in sorted(set(re.findall(r'@[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)*',alltxt))-handles):
            issues.append({"scene":sid,"episode":e,"kind":"noncanonical_handle","detail":h,"file":file})

        inline=s.get("charactersInline",[]) or []
        dn=[c.get("name") for c in inline if isinstance(c,dict) and c.get("name")]
        dh=[c.get("handle") for c in inline if isinstance(c,dict) and c.get("handle")]
        dia=s.get("dialogueInline",[]) or []
        speakers=[d.get("speaker") for d in dia if isinstance(d,dict) and d.get("speaker")]
        expected=[n for n in P if n in set(narrative_names(summary)+speakers)]
        if dn!=expected:
            issues.append({"scene":sid,"episode":e,"kind":"cast_mismatch","detail":f"declared={dn}; expected narrative+dialogue cast={expected}","file":file})
        for n,h in zip(dn,dh):
            if P.get(n)!=h:
                issues.append({"scene":sid,"episode":e,"kind":"character_handle_mismatch","detail":f"{n}: {h}","file":file})

        ef=[]
        if any(n in SALV for n in dn): ef.append("BR_Salvagers")
        if "Cyrus" in dn: ef.append("BR_Tethergrid")
        if (s.get("factions") or [])!=ef:
            issues.append({"scene":sid,"episode":e,"kind":"faction_mismatch","detail":f"declared={s.get('factions')}; expected={ef}","file":file})

        qs=quotes(summary)
        dt=[d.get("text","").strip() for d in dia if isinstance(d,dict)]
        # Source dialogue must survive exactly unless a scene-indexed, reviewable voice rewrite
        # explicitly replaces it. Added adaptation dialogue follows the source lines.
        missing=[]
        scene_rewrites=VOICE_REWRITES.get(sid,{})
        for source_index,q in enumerate(qs):
            actual=dt[source_index] if source_index<len(dt) else None
            rewrite=scene_rewrites.get(str(source_index))
            if actual!=q and (not rewrite or actual!=rewrite.get("text")):
                missing.append(q)
        if missing:
            issues.append({"scene":sid,"episode":e,"kind":"dialogue_quote_coverage","detail":f"missing source quotes={missing}; dialogueInline={dt}","file":file})
        for d in dia:
            if d.get("speaker") not in dn or d.get("handle")!=P.get(d.get("speaker")):
                issues.append({"scene":sid,"episode":e,"kind":"dialogue_cast_mismatch","detail":str(d),"file":file})

        loc=str(s.get("settingText","")).strip()
        if not loc: issues.append({"scene":sid,"episode":e,"kind":"missing_setting","detail":"settingText empty","file":file})
        dirs=s.get("directionInline",[]) or []
        labels=[str(x.get("text","")) for x in dirs if isinstance(x,dict)]
        req=("BACKYARD ROCKETS VISUAL LANGUAGE:","SCENE ACTION — SOURCE-LOCKED:","CHARACTER CONTINUITY —","LOCATION / PROP / STATE CONTINUITY —","CAMERA / LIGHT —")
        if len(labels)!=5 or any(not labels[i].startswith(req[i]) for i in range(min(len(labels),5))):
            issues.append({"scene":sid,"episode":e,"kind":"direction_schema_mismatch","detail":"five canonical production locks required","file":file})
        if labels:
            a=next((x.split("SCENE ACTION — SOURCE-LOCKED:",1)[1].strip() for x in labels if x.startswith("SCENE ACTION — SOURCE-LOCKED:")),None)
            ea=re.sub(r'\s+',' ',noquotes(summary)).strip()
            if a!=ea:
                issues.append({"scene":sid,"episode":e,"kind":"direction_summary_divergence","detail":"source-locked action differs from summary with source dialogue removed","file":file})
        for pattern,msg in legacy:
            if re.search(pattern,alltxt,re.I|re.S):
                issues.append({"scene":sid,"episode":e,"kind":"legacy_visual_conflict","detail":msg,"file":file})
        rows.append({"id":sid,"episode":e,"file":file,"summary":summary,"charactersInline":inline,"factions":s.get("factions",[]) or [],"settingText":loc,"dialogueInline":dia,"directionInline":dirs})

canon=text(chars)
for label,pattern in [("Arvin right-hand graft",r"RIGHT HAND"),("Milo facial markings",r"facial cybernetic markings"),("Lucia cyan-piped dark jacket",r"dark tactical field jacket.*cyan piping"),("Cyrus graphite armor",r"graphite technical armor"),("Tamz braided hair",r"braided hair")]:
    if not re.search(pattern,canon,re.I|re.S):
        issues.append({"scene":"CHARACTER_CANON","episode":"CANON","kind":"missing_approved_image_lock","detail":label,"file":"characters.json"})
for sid,c in Counter(s.get("id") for s in scenes).items():
    if sid and c>1: issues.append({"scene":sid,"episode":"STRUCTURE","kind":"duplicate_scene_id","detail":f"appears {c} times","file":"manifest/overlays"})

counts=Counter(ep(s) for s in scenes)
report={"authority":["latest approved generated model sheets","approved recurring vehicle/location/prop sheets","current scene narrative summaries","expanded dialogue adaptation","scene-indexed voice rewrites","legacy prose only where non-conflicting"],"sceneCount":len(scenes),"episodes":dict(sorted(counts.items())),"outlineOnlyEpisodes":[e for e,c in sorted(counts.items()) if c==1 and any("OUTLINE" in (s.get("id") or "") for s in scenes if ep(s)==e)],"sourceDialogueQuotes":sum(len(quotes(s.get("summary",""))) for s in scenes),"voiceRewrites":sum(len(v) for v in VOICE_REWRITES.values()),"totalDialogueLines":sum(len(s.get("dialogueInline",[]) or []) for s in scenes),"qualityGatePassed":not issues,"issueCount":len(issues),"issueKinds":dict(sorted(Counter(i["kind"] for i in issues).items())),"issues":issues,"scenes":rows}
REPORT.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
print("BACKYARD ROCKETS CONTINUITY QUALITY GATE")
print("Scenes:",report["sceneCount"],"Episodes:",report["episodes"])
print("Outline-only source episodes:",report["outlineOnlyEpisodes"])
print("Source dialogue quotes accounted for:",report["sourceDialogueQuotes"],"Voice rewrites:",report["voiceRewrites"],"Total dialogue lines:",report["totalDialogueLines"])
print("Passed:",report["qualityGatePassed"],"Findings:",report["issueCount"],report["issueKinds"])
for i in issues: print(f'{i["scene"]}\t{i["kind"]}\t{i["detail"]}\t[{i["file"]}]')
print("Report:",REPORT)
if issues: sys.exit(1)
