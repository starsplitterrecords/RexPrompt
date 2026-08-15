#!/usr/bin/env python3
import base64, gzip, json, re, sys
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SHOW_ID="backyard-rockets-s1"
MANIFEST=ROOT/"data/shows.json"
REPORT=ROOT/"backyard-rockets-continuity-report.json"
PRINCIPALS={"Arvin":"@brk.Arvin","Milo":"@brk.Milo","Lucia":"@brk.Lucia","Cyrus":"@brk.Cyrus","Tamz":"@brk.Tamz"}
SALVAGERS={"Arvin","Milo","Lucia","Tamz"}

def load(path): return json.loads(path.read_text(encoding="utf-8"))
def norm(raw):
    if isinstance(raw,list): return raw
    return [{"id":k,**v} if isinstance(v,dict) else {"id":k,"value":v} for k,v in (raw or {}).items()]
def encoded(path):
    text="".join(path.read_text(encoding="utf-8").split())
    return json.loads(gzip.decompress(base64.b64decode(text,validate=True)).decode("utf-8"))
def episode(scene):
    if scene.get("episode"): return scene["episode"]
    m=re.search(r"S1E\d{2}",scene.get("id","")); return m.group(0) if m else "UNKNOWN"
def all_text(v):
    if isinstance(v,str): return v
    if isinstance(v,list): return "\n".join(all_text(x) for x in v)
    if isinstance(v,dict): return "\n".join(all_text(x) for x in v.values())
    return ""
def without_quotes(text): return re.sub(r"[“\"]([^\"”]*)[”\"]"," ",text)
def narrative_names(summary):
    text=without_quotes(summary)
    return [n for n,h in PRINCIPALS.items() if re.search(rf"(?<![A-Za-z]){n}(?![A-Za-z])|{re.escape(h)}",text,re.I)]
def add(issues,scene,kind,detail,file): issues.append({"scene":scene,"episode":episode({"id":scene}) if scene.startswith("BR_") else "STRUCTURE","kind":kind,"detail":detail,"file":file})

shows=load(MANIFEST); show=next(s for s in shows if s.get("id")==SHOW_ID); base=ROOT/show["basePath"]
base_scenes=norm(load(base/show.get("scenesFile","scenes_base.json")))
scenes=list(base_scenes); groups=[(show.get("scenesFile","scenes_base.json"),base_scenes)]
for o in show.get("sceneOverlays",[]):
    p=base/o["file"]; incoming=norm(encoded(p) if o.get("encoding")=="gzip-base64" else load(p)); excluded=set(o.get("excludeIds",[])); incoming=[s for s in incoming if s.get("id") not in excluded]
    scenes.extend(incoming); groups.append((o["file"],incoming))

characters=load(base/"characters.json")
canon_handles={v.get("handle") for v in characters.values() if isinstance(v,dict) and v.get("handle")}
issues=[]; rows=[]
legacy_patterns=[
    (r"left[- ]hand.{0,60}(?:synthetic|graft)|(?:synthetic|graft).{0,60}left[- ]hand","Arvin left-hand graft conflict"),
    (r"\b(?:junk-built|scrap-built|rickety) rocket\b","obsolete junk-built rocket language"),
    (r"\b(?:gutted fuel tanker|rusted tanker|rusted fuel tanker|oil-slicked belly)\b","obsolete decay-led tanker language"),
    (r"\b(?:tattered camouflage net|graveyard of fallen communications towers|primitive control console)\b","obsolete post-apocalyptic production language"),
    (r"\b(?:white armored interceptor|chrome-and-white armor|bulky fantasy plating)\b","obsolete Cyrus/Aegis design language"),
    (r"\b(?:smartphone|iphone|android phone|macbook|ultrabook|gaming laptop)\b","wrong consumer-device era language"),
]
for file_name,group in groups:
    for scene in group:
        sid=scene.get("id","<missing>"); ep=episode(scene); summary=scene.get("summary",""); text=all_text(scene)
        handles=set(re.findall(r"@[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)*",text))
        for h in sorted(handles-canon_handles): issues.append({"scene":sid,"episode":ep,"kind":"noncanonical_handle","detail":h,"file":file_name})
        inline=scene.get("charactersInline",[]) or []
        declared_names=[c.get("name") for c in inline if isinstance(c,dict) and c.get("name")]
        declared_handles=[c.get("handle") for c in inline if isinstance(c,dict) and c.get("handle")]
        expected=narrative_names(summary)
        if declared_names!=expected: issues.append({"scene":sid,"episode":ep,"kind":"cast_mismatch","detail":f"declared={declared_names}; expected from narrative={expected}","file":file_name})
        for n in declared_names:
            if n not in PRINCIPALS: issues.append({"scene":sid,"episode":ep,"kind":"unknown_character","detail":n,"file":file_name})
        for n,h in zip(declared_names,declared_handles):
            if PRINCIPALS.get(n)!=h: issues.append({"scene":sid,"episode":ep,"kind":"character_handle_mismatch","detail":f"{n}: {h}","file":file_name})
        expected_f=[]
        if any(n in SALVAGERS for n in declared_names): expected_f.append("BR_Salvagers")
        if "Cyrus" in declared_names: expected_f.append("BR_Aegis")
        if (scene.get("factions") or [])!=expected_f: issues.append({"scene":sid,"episode":ep,"kind":"faction_mismatch","detail":f"declared={scene.get('factions')}; expected={expected_f}","file":file_name})
        for d in scene.get("dialogueInline",[]) or []:
            if d.get("speaker") not in declared_names or d.get("handle")!=PRINCIPALS.get(d.get("speaker")):
                issues.append({"scene":sid,"episode":ep,"kind":"dialogue_cast_mismatch","detail":str(d),"file":file_name})
        setting=str(scene.get("settingText","")).strip()
        if not setting: issues.append({"scene":sid,"episode":ep,"kind":"missing_setting","detail":"settingText is empty","file":file_name})
        dirs=scene.get("directionInline",[]) or []
        labels=[str(x.get("text","")) for x in dirs if isinstance(x,dict)]
        required=("BACKYARD ROCKETS VISUAL LANGUAGE:","SCENE ACTION — SOURCE-LOCKED:","CHARACTER CONTINUITY —","LOCATION / PROP / STATE CONTINUITY —","CAMERA / LIGHT —")
        if len(labels)!=5 or any(not labels[i].startswith(required[i]) for i in range(min(len(labels),5))) or len(labels)!=len(required):
            issues.append({"scene":sid,"episode":ep,"kind":"direction_schema_mismatch","detail":"directionInline must contain exactly the five rebuilt production locks in canonical order","file":file_name})
        if labels:
            action=next((x.split("SCENE ACTION — SOURCE-LOCKED:",1)[1].strip() for x in labels if x.startswith("SCENE ACTION — SOURCE-LOCKED:")),None)
            expected_action=re.sub(r"\s+"," ",without_quotes(summary)).strip()
            if action!=expected_action: issues.append({"scene":sid,"episode":ep,"kind":"direction_summary_divergence","detail":"source-locked action does not exactly match narrative summary with dialogue removed","file":file_name})
        for pattern,message in legacy_patterns:
            if re.search(pattern,text,re.I|re.S): issues.append({"scene":sid,"episode":ep,"kind":"legacy_visual_conflict","detail":message,"file":file_name})
        rows.append({"id":sid,"episode":ep,"file":file_name,"summary":summary,"charactersInline":inline,"factions":scene.get("factions",[]) or [],"settingText":setting,"dialogueInline":scene.get("dialogueInline",[]),"directionInline":dirs})

canon=all_text(characters)
for label,pattern in [
    ("Arvin right-hand graft",r"RIGHT HAND"),("Milo facial markings",r"facial cybernetic markings"),("Lucia cyan-piped dark jacket",r"dark tactical field jacket.*cyan piping"),("Cyrus graphite armor",r"graphite technical armor"),("Tamz braided hair",r"braided hair")]:
    if not re.search(pattern,canon,re.I|re.S): issues.append({"scene":"CHARACTER_CANON","episode":"CANON","kind":"missing_approved_image_lock","detail":label,"file":"characters.json"})
ids=[s.get("id") for s in scenes]
for sid,count in Counter(ids).items():
    if sid and count>1: issues.append({"scene":sid,"episode":"STRUCTURE","kind":"duplicate_scene_id","detail":f"appears {count} times","file":"manifest/overlays"})

report={
    "authority":["latest approved generated model sheets","approved recurring vehicle/location/prop sheets","current scene narrative summaries","legacy source/export prose only where non-conflicting"],
    "sceneCount":len(scenes),"episodes":dict(sorted(Counter(episode(s) for s in scenes).items())),
    "outlineOnlyEpisodes":[ep for ep,c in sorted(Counter(episode(s) for s in scenes).items()) if c==1 and any("OUTLINE" in (s.get("id") or "") for s in scenes if episode(s)==ep)],
    "qualityGatePassed":not issues,"issueCount":len(issues),"issueKinds":dict(sorted(Counter(i["kind"] for i in issues).items())),"issues":issues,"scenes":rows,
}
REPORT.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
print("BACKYARD ROCKETS CONTINUITY QUALITY GATE")
print("Scenes:",report["sceneCount"],"Episodes:",report["episodes"])
print("Outline-only source episodes:",report["outlineOnlyEpisodes"])
print("Passed:",report["qualityGatePassed"],"Findings:",report["issueCount"],report["issueKinds"])
for i in issues: print(f'{i["scene"]}\t{i["kind"]}\t{i["detail"]}\t[{i["file"]}]')
print("Report:",REPORT)
if issues: sys.exit(1)
