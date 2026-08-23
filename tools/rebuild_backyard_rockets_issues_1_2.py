#!/usr/bin/env python3
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

print("Backyard Rockets Issues 1-2 reconstruction installed")
print("Old fragmented payloads removed:", len(OLD_NAMES))
print("Active replacement payloads:", [x["file"] for x in NEW])
