#!/usr/bin/env python3
import base64
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW_ID = "backyard-rockets-s1"
SHOW_DIR = ROOT / "data" / "shows" / SHOW_ID
MANIFEST = ROOT / "data" / "shows.json"
VALIDATOR = ROOT / "tools" / "validate_backyard_rockets.py"
REWRITES = SHOW_DIR / "dialogue-voice-rewrites.json"

NEW = [
    {"file": "encoded/scenes_e01_oxidizer_gap_rebuilt.json.gzb64", "encoding": "gzip-base64"},
    {"file": "encoded/scenes_e02_copper_lattice_rebuilt.json.gzb64", "encoding": "gzip-base64"},
]
OLD_NAMES = {
    *(f"encoded/scenes_e01_p0{i}.json.gzb64" for i in range(1, 5)),
    *(f"encoded/scenes_e02_p0{i}.json.gzb64" for i in range(1, 7)),
}

def load_encoded(path):
    raw = base64.b64decode("".join(path.read_text(encoding="utf-8").split()), validate=True)
    return json.loads(gzip.decompress(raw).decode("utf-8"))

def save_encoded(path, data):
    raw = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    path.write_text(base64.b64encode(gzip.compress(raw, compresslevel=9, mtime=0)).decode("ascii"), encoding="utf-8")

shows = json.loads(MANIFEST.read_text(encoding="utf-8"))
show = next(s for s in shows if s.get("id") == SHOW_ID)
overlays = show.get("sceneOverlays", [])
remaining = [o for o in overlays if o.get("file") not in OLD_NAMES]
insert_at = next(i for i, o in enumerate(remaining) if "scenes_e03_public_sky" in o.get("file", ""))
show["sceneOverlays"] = remaining[:insert_at] + NEW + remaining[insert_at:]
MANIFEST.write_text(json.dumps(shows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

text = VALIDATOR.read_text(encoding="utf-8")
old = '"S1E02": 30,'
if old not in text:
    raise SystemExit("validator S1E02 count marker not found")
VALIDATOR.write_text(text.replace(old, '"S1E02": 24,'), encoding="utf-8")

rewrites = json.loads(REWRITES.read_text(encoding="utf-8"))
rewrites = {k: v for k, v in rewrites.items() if not (k.startswith("BR_S1E01") or k.startswith("BR_S1E02"))}
REWRITES.write_text(json.dumps(rewrites, ensure_ascii=False, indent=2), encoding="utf-8")

for rel in sorted(OLD_NAMES):
    path = SHOW_DIR / rel
    if path.exists():
        path.unlink()

# Normalize documentary-channel metadata and one prosthetic-guard wording before audit.
e1_path = SHOW_DIR / NEW[0]["file"]
e2_path = SHOW_DIR / NEW[1]["file"]
e1 = load_encoded(e1_path)
e2 = load_encoded(e2_path)
for scenes, channel_map in [
    (e1, {"BR_S1E01_R2_P01": "dryline", "BR_S1E01_R2_P04": "tethergrid", "BR_S1E01_R2_P19": "dryline"}),
    (e2, {"BR_S1E02_R2_P04": "tethergrid", "BR_S1E02_R2_P10": "dryline"}),
]:
    for item in scenes:
        channel = channel_map.get(item.get("id"))
        if channel:
            item["documentaryChannel"] = channel

p14 = next(s for s in e1 if s.get("id") == "BR_S1E01_R2_P14")
old_phrase = "Arvin holds the assembly steady with his natural left hand and right-hand graft working a torque tool. "
new_phrase = "Arvin holds the assembly steady while his RIGHT-HAND graft works a torque tool. "
if old_phrase in p14["summary"]:
    p14["summary"] = p14["summary"].replace(old_phrase, new_phrase)
p14["directionInline"][1]["text"] = "SCENE ACTION — SOURCE-LOCKED: " + p14["summary"]

save_encoded(e1_path, e1)
save_encoded(e2_path, e2)

print("Backyard Rockets Issues 1-2 reconstruction installed")
print("Old fragmented payloads removed:", len(OLD_NAMES))
print("Active replacement payloads:", [x["file"] for x in NEW])
