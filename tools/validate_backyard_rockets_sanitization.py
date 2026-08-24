#!/usr/bin/env python3
import base64, gzip, json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW_ID = "backyard-rockets-s1"
SHOW = ROOT / "data" / "shows" / SHOW_ID
MANIFEST = ROOT / "data" / "shows.json"

FORBIDDEN_DIRECTION_PREFIXES = (
    "BACKYARD ROCKETS VISUAL LANGUAGE:", "TETHERGRID DOCUMENTARY LANGUAGE:", "DRYLINE DOCUMENTARY LANGUAGE:",
    "SCENE ACTION — SOURCE-LOCKED:", "CHARACTER CONTINUITY —", "PRESENTER CONTINUITY —",
    "LOCATION / PROP / STATE CONTINUITY —", "LOCATION / GRAPHIC CONTINUITY —",
    "CAMERA / LIGHT —", "CAMERA / EDITORIAL GRAMMAR —",
)
FORBIDDEN_PACKAGE_FILES = {
    "blocking.json", "dialogue.json", "direction.json", "lighting.json", "mood.json", "negatives.json",
    "dialogue-adaptation-notes.md", "dialogue-voice-rewrites.json", "documentary-interstitials.json",
}
FORBIDDEN_ROOT_OUTPUTS = {
    "backyard-rockets-continuity-report.json", "backyard-rockets-scene-payloads.json",
}
FORBIDDEN_TOOLS = {
    "apply_backyard_rockets_voice_rewrites.py", "expand_backyard_rockets_dialogue.py", "fix_backyard_rockets_continuity.py",
    "insert_backyard_rockets_documentary_interstitials.py", "reconcile_backyard_rockets_dialogue_cast.py",
}
CORRECTION_RESIDUE = ("canonical visual override", "story override", "obsolete", "ignore older", "contradictory older")


def load(path): return json.loads(path.read_text(encoding="utf-8"))
def decode(path):
    raw = base64.b64decode("".join(path.read_text(encoding="utf-8").split()), validate=True)
    return json.loads(gzip.decompress(raw).decode("utf-8"))

shows = load(MANIFEST)
show = next(s for s in shows if s.get("id") == SHOW_ID)
scenes = []
for overlay in show.get("sceneOverlays", []):
    p = SHOW / overlay["file"]
    scenes.extend(decode(p) if overlay.get("encoding") == "gzip-base64" else load(p))

errors = []
if len(scenes) != 162:
    errors.append(f"expected 162 active scenes, found {len(scenes)}")

for name in FORBIDDEN_PACKAGE_FILES:
    if (SHOW / name).exists(): errors.append(f"stale package artifact remains: {name}")
for name in FORBIDDEN_ROOT_OUTPUTS:
    if (ROOT / name).exists(): errors.append(f"generated review output is tracked in repository root: {name}")
raw = SHOW / "raw"
if raw.exists() and any(raw.iterdir()): errors.append("stale raw production fragments remain")
for name in FORBIDDEN_TOOLS:
    if (ROOT / "tools" / name).exists(): errors.append(f"retired migration tool remains: {name}")

chars = load(SHOW / "characters.json")
handles = []
char_text = json.dumps(chars, ensure_ascii=False).lower()
for term in CORRECTION_RESIDUE:
    if term in char_text: errors.append(f"character correction residue remains: {term}")
for key, entry in chars.items():
    if not isinstance(entry, dict):
        errors.append(f"invalid character entry: {key}"); continue
    for field in ("text", "voiceProfile"):
        if field in entry: errors.append(f"character field {field} remains: {key}")
    if entry.get("handle"): handles.append(entry["handle"])
for handle, count in Counter(handles).items():
    if count != 1: errors.append(f"duplicate character handle {handle}: {count}")

regions = load(SHOW / "regions.json")
settings = load(SHOW / "settings.json")
factions = load(SHOW / "factions.json")
for stale in ("mojave",):
    if stale in regions: errors.append(f"stale region alias remains: {stale}")
for stale in ("launch_shop", "tethergrid"):
    if stale in factions: errors.append(f"stale faction alias remains: {stale}")

inline_settings = Counter()
for scene in scenes:
    sid = scene.get("id", "<missing>")
    if scene.get("regionText"): errors.append(f"{sid}: regionText should be a region reference")
    region = scene.get("region")
    if not region or region not in regions: errors.append(f"{sid}: missing/unknown region reference {region}")

    setting = scene.get("setting")
    setting_text = scene.get("settingText")
    if setting:
        if setting not in settings: errors.append(f"{sid}: unknown setting reference {setting}")
        if setting_text: errors.append(f"{sid}: has both setting and settingText")
    elif setting_text:
        inline_settings[setting_text] += 1
    else:
        errors.append(f"{sid}: missing setting")

    for item in scene.get("directionInline", []) or []:
        text = str(item.get("text", "")) if isinstance(item, dict) else str(item)
        if text.startswith(FORBIDDEN_DIRECTION_PREFIXES):
            errors.append(f"{sid}: repeated production scaffolding remains")
    for c in scene.get("charactersInline", []) or []:
        if not isinstance(c, dict) or set(c) - {"name", "handle"}:
            errors.append(f"{sid}: scene-scope character identity contamination")
    for d in scene.get("dialogueInline", []) or []:
        if not isinstance(d, dict) or set(d) - {"speaker", "handle", "text"}:
            errors.append(f"{sid}: dialogue carries non-dialogue production metadata")

for text, count in inline_settings.items():
    if count > 1: errors.append(f"repeated setting prose remains inline {count} times: {text[:80]}")

if errors:
    print("BACKYARD ROCKETS SANITIZATION FAILED")
    for e in errors: print("-", e)
    raise SystemExit(1)
print("Backyard Rockets sanitization passed")
print("Scenes:", len(scenes))
print("Character records:", len(chars), "unique handles:", len(handles))
print("Persistent settings:", len(settings), "unique inline settings:", len(inline_settings))
