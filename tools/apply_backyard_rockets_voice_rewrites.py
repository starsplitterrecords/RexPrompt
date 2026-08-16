#!/usr/bin/env python3
"""Apply the approved Backyard Rockets character-voice pass to every production payload."""

import base64
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW_ID = "backyard-rockets-s1"
SHOW = ROOT / "data" / "shows" / SHOW_ID
RULES = json.loads((SHOW / "dialogue-voice-rewrites.json").read_text(encoding="utf-8"))
CANON = {
    "Arvin": "@brk.Arvin",
    "Milo": "@brk.Milo",
    "Lucia": "@brk.Lucia",
    "Cyrus": "@brk.Cyrus",
    "Tamz": "@brk.Tamz",
}


def load(path, encoding=None):
    if encoding == "gzip-base64":
        packed = base64.b64decode("".join(path.read_text(encoding="utf-8").split()), validate=True)
        return json.loads(gzip.decompress(packed).decode("utf-8"))
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value, encoding=None):
    if encoding == "gzip-base64":
        raw = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode()
        path.write_text(
            base64.b64encode(gzip.compress(raw, 9, mtime=0)).decode(), encoding="utf-8"
        )
        return
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalized(value):
    if isinstance(value, list):
        return value
    return [dict({"id": key}, **item) for key, item in value.items()]


def apply_to_scenes(scenes):
    changed = 0
    visited = set()
    for scene in normalized(scenes):
        scene_id = scene.get("id")
        rules = RULES.get(scene_id, {})
        dialogue = scene.get("dialogueInline") or []
        for index_text, replacement in rules.items():
            index = int(index_text)
            if index >= len(dialogue):
                raise IndexError(f"{scene_id}: rewrite index {index} exceeds {len(dialogue)} lines")
            line = dialogue[index]
            speaker = replacement["speaker"]
            line["speaker"] = speaker
            line["handle"] = CANON[speaker]
            line["text"] = replacement["text"]
            changed += 1
            visited.add((scene_id, index_text))
    return changed, visited


manifest = json.loads((ROOT / "data" / "shows.json").read_text(encoding="utf-8"))
show = next(item for item in manifest if item.get("id") == SHOW_ID)
base = ROOT / show["basePath"]
files = [(show.get("scenesFile", "scenes_base.json"), None)]
files += [(item["file"], item.get("encoding")) for item in show.get("sceneOverlays", [])]

total_changed = 0
visited = set()
for relative, encoding in files:
    path = base / relative
    payload = load(path, encoding)
    changed, seen = apply_to_scenes(payload)
    total_changed += changed
    visited |= seen
    write(path, payload, encoding)

expected = {(scene_id, index) for scene_id, items in RULES.items() for index in items}
missing = sorted(expected - visited)
if missing:
    raise SystemExit(f"Voice rewrite rules did not resolve: {missing[:10]}")

print(f"Applied {total_changed} Backyard Rockets dialogue voice rewrites")
