#!/usr/bin/env python3
import base64, gzip, json, re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW_ID = "backyard-rockets-s1"
MANIFEST = ROOT / "data" / "shows.json"


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

print("BACKYARD ROCKETS CONTINUITY AUDIT")
print("Scenes:", len(scenes), "Episodes:", dict(sorted(Counter(scene_episode(s) for s in scenes).items())))

issues = []
for file_name, group in source_files:
    for scene in group:
        sid = scene.get("id", "<missing>")
        text = all_text(scene)
        handles = sorted(set(re.findall(r"@[A-Za-z0-9_.-]+", text)))
        bad_handles = [h for h in handles if h not in canon_handles]
        if bad_handles:
            issues.append((sid, "noncanonical handle", ", ".join(bad_handles), file_name))
        refs = scene.get("characters", []) or []
        unresolved = [r for r in refs if r not in known_refs]
        if unresolved:
            issues.append((sid, "unresolved character ref", ", ".join(map(str, unresolved)), file_name))
        # Flag named principal characters present in prose/dialogue but omitted from the scene character list.
        declared = set(refs)
        for name, handle in canon_names.items():
            if re.search(rf"\b{re.escape(name)}\b", text, re.I) and name not in declared and handle not in declared:
                issues.append((sid, "character mentioned but not declared", f"{name} ({handle})", file_name))
        # Faction mismatch guardrail for principal characters.
        factions = set(scene.get("factions", []) or [])
        if ("Cyrus" in text or "@brk.Cyrus" in text) and "BR_Salvagers" in factions and "BR_Aegis" not in factions:
            issues.append((sid, "likely faction mismatch", "Cyrus present in Salvagers-only scene", file_name))
        if any(n in text for n in ("Arvin", "Milo", "Lucia")) and "BR_Aegis" in factions and "BR_Salvagers" not in factions:
            issues.append((sid, "likely faction mismatch", "Salvager principal present in Aegis-only scene", file_name))

print("\nSTRUCTURAL / IDENTITY FINDINGS")
for sid, kind, detail, file_name in issues:
    print(f"{sid}\t{kind}\t{detail}\t[{file_name}]")

print("\nFULL SCENE CONTINUITY DUMP")
for scene in scenes:
    sid = scene.get("id", "<missing>")
    print(f"\n--- {sid} | {scene_episode(scene)} | {scene.get('act','')} ---")
    for key in ("summary", "settingText", "regionText", "region", "factions", "characters", "charactersInline", "dialogueInline", "directionInline"):
        if scene.get(key):
            value = scene[key]
            if isinstance(value, str):
                print(f"{key}: {value}")
            else:
                print(f"{key}: {json.dumps(value, ensure_ascii=False)}")

print("\nTOTAL FINDINGS:", len(issues))
