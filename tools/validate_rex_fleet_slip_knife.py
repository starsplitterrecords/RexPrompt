#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data" / "shows" / "rex-fleet-slip-knife"
MANIFEST = ROOT / "data" / "shows.json"
INDEX = ROOT / "index.html"

REQUIRED_DICTIONARIES = (
    "blocking.json", "characters.json", "dialogue.json", "direction.json",
    "factions.json", "lighting.json", "mood.json", "negatives.json",
    "regions.json", "settings.json",
)

def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

for name in REQUIRED_DICTIONARIES + ("pages_base.json", "pages_i01.json"):
    if not (SHOW / name).exists():
        raise SystemExit(f"Slip Knife package file missing: {name}")

shows = load_json(MANIFEST)
entries = [e for e in shows if e.get("seriesId") == "rex-fleet-slip-knife"]
if len(entries) != 1:
    raise SystemExit(f"Expected one Slip Knife manifest entry, found {len(entries)}")
entry = entries[0]

expected_manifest = {
    "id": "rex-fleet-slip-knife-i01",
    "name": "Rex Fleet: Slip Knife — Issue 1 — First Cut",
    "seriesName": "Rex Fleet: Slip Knife",
    "issueLabel": "Issue 1 — First Cut",
    "basePath": "data/shows/rex-fleet-slip-knife",
    "scenesFile": "pages_base.json",
    "unitLabel": "PAGE",
}
for key, value in expected_manifest.items():
    if entry.get(key) != value:
        raise SystemExit(f"Slip Knife manifest {key} mismatch: {entry.get(key)!r}")

if entry.get("sceneOverlays") != [{"file": "pages_i01.json"}]:
    raise SystemExit("Slip Knife Issue 1 must assemble from pages_base.json + pages_i01.json")
generation = entry.get("generationLine", "")
for required in ("comic page", "Verge Campaign", "Flanking Rule", "Slip Knife"):
    if required not in generation:
        raise SystemExit(f"Slip Knife generation line missing required production anchor: {required}")

if load_json(SHOW / "pages_base.json") != []:
    raise SystemExit("Slip Knife pages_base.json must remain an empty structural base")

characters = load_json(SHOW / "characters.json")
settings = load_json(SHOW / "settings.json")
regions = load_json(SHOW / "regions.json")
factions = load_json(SHOW / "factions.json")
pages = load_json(SHOW / "pages_i01.json")

if len(pages) != 22:
    raise SystemExit(f"Slip Knife Issue 1 must contain 22 production pages, found {len(pages)}")

expected_ids = [f"RFSK_I01_P{n:02d}" for n in range(1, 23)]
ids = [p.get("id") for p in pages]
if ids != expected_ids:
    raise SystemExit(f"Slip Knife page IDs/order invalid: {ids}")
if len(ids) != len(set(ids)):
    raise SystemExit("Duplicate Slip Knife page IDs")

handles = {}
for cid, character in characters.items():
    handle = character.get("handle")
    if not handle:
        raise SystemExit(f"{cid}: missing handle")
    if handle in handles:
        raise SystemExit(f"Duplicate Slip Knife handle: {handle}")
    handles[handle] = cid
    if not character.get("visualAnchor"):
        raise SystemExit(f"{cid}: missing visualAnchor")
    if not character.get("voice"):
        raise SystemExit(f"{cid}: missing voice")

for number, page in enumerate(pages, start=1):
    pid = page.get("id")
    if page.get("unit") != "PAGE":
        raise SystemExit(f"{pid}: unit must be PAGE")
    if page.get("issue") != 1 or page.get("page") != number:
        raise SystemExit(f"{pid}: issue/page metadata mismatch")
    if not page.get("summary"):
        raise SystemExit(f"{pid}: missing summary")
    if not (page.get("setting") or page.get("settingText")):
        raise SystemExit(f"{pid}: missing setting")
    if not (page.get("region") or page.get("regionText")):
        raise SystemExit(f"{pid}: missing region")
    if not page.get("panelPlan"):
        raise SystemExit(f"{pid}: missing panelPlan")
    if number == 1:
        if page.get("continuityFrom"):
            raise SystemExit(f"{pid}: opening page should not have continuityFrom")
    elif page.get("continuityFrom") != expected_ids[number - 2]:
        raise SystemExit(f"{pid}: continuityFrom must point to prior page")
    if page.get("setting") and page["setting"] not in settings:
        raise SystemExit(f"{pid}: unresolved setting {page['setting']}")
    if page.get("region") and page["region"] not in regions:
        raise SystemExit(f"{pid}: unresolved region {page['region']}")
    for faction in page.get("factions", []):
        if faction not in factions:
            raise SystemExit(f"{pid}: unresolved faction {faction}")
    for character in page.get("characters", []):
        if character not in characters:
            raise SystemExit(f"{pid}: unresolved character {character}")
    for dialogue in page.get("dialogueInline", []):
        handle = dialogue.get("handle")
        if handle and handle.startswith("@") and handle not in handles:
            raise SystemExit(f"{pid}: unresolved dialogue handle {handle}")

serialized = json.dumps(pages, ensure_ascii=False)
for forbidden in ("RF_S1E", "generic cyberpunk neon", "Season One political"):
    if forbidden in serialized:
        raise SystemExit(f"Slip Knife production residue remains: {forbidden}")

p20_lines = [d.get("text") for d in pages[19].get("dialogueInline", [])]
if "None." not in p20_lines or "Open the bins." not in p20_lines:
    raise SystemExit("Slip Knife delivery payoff missing from page 20")
p22_lines = [d.get("text") for d in pages[21].get("dialogueInline", [])]
if "What's the next load?" not in p22_lines:
    raise SystemExit("Slip Knife Issue 1 final work-continuity beat missing")
if "chevron" not in json.dumps(pages[21], ensure_ascii=False).lower():
    raise SystemExit("Slip Knife chevron tradition missing from final page")

index_text = INDEX.read_text(encoding="utf-8")
for required in ("s.panelPlan", "s.dialogueInline", "s.continuityFrom", "sceneOverlays"):
    if required not in index_text:
        raise SystemExit(f"Assembler support missing: {required}")

print(f"Slip Knife validation passed: {len(pages)} pages, {len(characters)} recurring characters, {len(settings)} settings.")
