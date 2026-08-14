#!/usr/bin/env python3
import base64, gzip, json, re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW_ID = "backyard-rockets-s1"
MANIFEST = ROOT / "data" / "shows.json"
REPORT = ROOT / "backyard-rockets-continuity-report.json"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(raw):
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        return [{"id": k, **v} if isinstance(v, dict) else {"id": k, "value": v} for k, v in raw.items()]
    raise TypeError(type(raw).__name__)


def load_encoded(path):
    text = "".join(path.read_text(encoding="utf-8").split())
    return json.loads(gzip.decompress(base64.b64decode(text, validate=True)).decode("utf-8"))


def scene_episode(scene):
    if scene.get("episode"):
        return scene["episode"]
    m = re.search(r"S1E\d{2}", scene.get("id", ""))
    return m.group(0) if m else "UNKNOWN"


def all_text(value):
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(all_text(v) for v in value)
    if isinstance(value, dict):
        return "\n".join(all_text(v) for v in value.values())
    return ""


shows = load_json(MANIFEST)
show = next(s for s in shows if s.get("id") == SHOW_ID)
base = ROOT / show["basePath"]
scenes = normalize(load_json(base / show.get("scenesFile", "scenes_base.json")))
source_files = [(show.get("scenesFile", "scenes_base.json"), scenes)]
for overlay in show.get("sceneOverlays", []):
    path = base / overlay["file"]
    raw = load_encoded(path) if overlay.get("encoding") == "gzip-base64" else load_json(path)
    incoming = normalize(raw)
    excluded = set(overlay.get("excludeIds", []))
    incoming = [s for s in incoming if s.get("id") not in excluded]
    scenes.extend(incoming)
    source_files.append((overlay["file"], incoming))

characters = load_json(base / "characters.json")
canon_handles = {v["handle"] for v in characters.values() if isinstance(v, dict) and v.get("handle")}
canon_names = {v["name"]: v["handle"] for v in characters.values() if isinstance(v, dict) and v.get("name") and v.get("handle")}
char_keys = set(characters)
known_refs = char_keys | canon_handles | set(canon_names)

VISUAL_CONFLICTS = [
    (re.compile(r"Arvin.{0,180}(?:left[- ]hand|left hand).{0,80}(?:synthetic|graft)|(?:synthetic|graft).{0,80}(?:left[- ]hand|left hand)", re.I | re.S), "Arvin legacy left-hand graft; approved image canon is RIGHT hand only"),
    (re.compile(r"Arvin.{0,180}(?:broad utilitarian build|broad[- ]shouldered|bulky build)", re.I | re.S), "Arvin legacy broad/bulky build; approved image canon is lean, narrow and angular"),
    (re.compile(r"Milo.{0,180}(?:compact|slight build|safety[- ]orange)", re.I | re.S), "Milo legacy compact/orange styling; approved image canon is broad, grounded, brown vest/dark shirt"),
    (re.compile(r"Milo.{0,220}(?:no facial markings|clean[- ]shaven face without markings)", re.I | re.S), "Milo must retain the approved facial cybernetic markings"),
    (re.compile(r"Lucia.{0,180}(?:camel, charcoal and bone|camel jacket|tan tactical jacket)", re.I | re.S), "Lucia legacy camel/tan styling; approved image canon is precise dark jacket with restrained cyan piping"),
    (re.compile(r"Cyrus.{0,220}(?:white armor|chrome-and-white armor|bulky armor|fantasy plating)", re.I | re.S), "Cyrus must use approved graphite technical armor with restrained amber-cyan status lines"),
    (re.compile(r"Tamz.{0,180}(?:loose hair|unbraided hair|black stains|filthy jacket)", re.I | re.S), "Tamz must retain braided hair and intentional gray field-jacket patch/insignia motifs"),
]
TECH_CONFLICTS = [
    (re.compile(r"\b(?:smartphone|iphone|android phone)\b", re.I), "consumer smartphone language conflicts with the tactile late-1980s industrial-future design language"),
    (re.compile(r"\b(?:macbook|ultrabook|gaming laptop)\b", re.I), "modern consumer laptop language conflicts with the established industrial-future hardware language"),
]

issues = []
scene_rows = []
for file_name, group in source_files:
    for scene in group:
        sid = scene.get("id", "<missing>")
        ep = scene_episode(scene)
        text = all_text(scene)
        handles = sorted(set(re.findall(r"@[A-Za-z0-9_.-]+", text)))
        bad_handles = [h for h in handles if h not in canon_handles]
        for handle in bad_handles:
            issues.append({"scene": sid, "episode": ep, "kind": "noncanonical_handle", "detail": handle, "file": file_name})
        refs = scene.get("characters", []) or []
        for ref in [r for r in refs if r not in known_refs]:
            issues.append({"scene": sid, "episode": ep, "kind": "unresolved_character_ref", "detail": str(ref), "file": file_name})
        declared = set(refs)
        for name, handle in canon_names.items():
            if re.search(rf"\b{re.escape(name)}\b", text, re.I) and name not in declared and handle not in declared:
                issues.append({"scene": sid, "episode": ep, "kind": "character_mentioned_not_declared", "detail": f"{name} ({handle})", "file": file_name})
        factions = set(scene.get("factions", []) or [])
        if ("Cyrus" in text or "@brk.Cyrus" in text) and "BR_Salvagers" in factions and "BR_Aegis" not in factions:
            issues.append({"scene": sid, "episode": ep, "kind": "faction_mismatch", "detail": "Cyrus present in Salvagers-only scene", "file": file_name})
        if any(n in text for n in ("Arvin", "Milo", "Lucia", "Tamz")) and "BR_Aegis" in factions and "BR_Salvagers" not in factions:
            issues.append({"scene": sid, "episode": ep, "kind": "faction_mismatch", "detail": "Salvager principal present in Aegis-only scene", "file": file_name})
        for pattern, message in VISUAL_CONFLICTS + TECH_CONFLICTS:
            match = pattern.search(text)
            if match:
                snippet = text[max(0, match.start()-100):min(len(text), match.end()+140)].replace("\n", " ")
                issues.append({"scene": sid, "episode": ep, "kind": "approved_image_or_era_conflict", "detail": message, "snippet": snippet, "file": file_name})
        scene_rows.append({"id": sid, "episode": ep, "file": file_name, "summary": scene.get("summary", ""), "characters": refs, "factions": scene.get("factions", []) or [], "settingText": scene.get("settingText", ""), "dialogueInline": scene.get("dialogueInline", []), "directionInline": scene.get("directionInline", [])})

canon_text = all_text(characters)
required_canon = [
    ("Arvin right-hand graft", r"RIGHT HAND"),
    ("Milo facial markings", r"facial cybernetic markings"),
    ("Lucia cyan-piped dark jacket", r"dark tactical field jacket.*cyan piping"),
    ("Cyrus graphite armor", r"graphite technical armor"),
    ("Tamz braided hair", r"braided hair"),
]
for label, pattern in required_canon:
    if not re.search(pattern, canon_text, re.I | re.S):
        issues.append({"scene": "CHARACTER_CANON", "episode": "CANON", "kind": "missing_approved_image_lock", "detail": label, "file": "characters.json"})

report = {
    "authority": ["latest approved generated model sheets", "approved recurring vehicle/location/prop sheets", "current continuity ledger", "legacy source/export prose"],
    "sceneCount": len(scenes),
    "episodes": dict(sorted(Counter(scene_episode(s) for s in scenes).items())),
    "issueCount": len(issues),
    "issueKinds": dict(sorted(Counter(i["kind"] for i in issues).items())),
    "issues": issues,
    "scenes": scene_rows,
}
REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

print("BACKYARD ROCKETS CONTINUITY AUDIT")
print("Scenes:", report["sceneCount"], "Episodes:", report["episodes"])
print("Findings:", report["issueCount"], report["issueKinds"])
for issue in issues:
    print(f'{issue["scene"]}\t{issue["kind"]}\t{issue["detail"]}\t[{issue["file"]}]')
print("Report:", REPORT)
