#!/usr/bin/env python3
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data" / "shows" / "azure-reach"
MANIFEST = ROOT / "data" / "shows.json"
REQUIRED_DATA_FILES = [
    "blocking.json",
    "characters.json",
    "dialogue.json",
    "direction.json",
    "factions.json",
    "lighting.json",
    "mood.json",
    "negatives.json",
    "regions.json",
    "settings.json",
]
EXPECTED_PANEL_COUNTS = [5, 6, 10, 5, 6, 6, 5, 6, 6, 7, 5, 7, 5, 5, 7, 6, 5, 5, 6, 7, 8, 8]


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


for filename in REQUIRED_DATA_FILES:
    path = SHOW / filename
    if not path.exists():
        raise SystemExit(f"Azure Reach missing required RexPrompt data file: {filename}")
    try:
        load_json(path)
    except Exception as exc:
        raise SystemExit(f"{filename}: invalid JSON: {exc}") from exc

shows = load_json(MANIFEST)
show = next((entry for entry in shows if entry.get("id") == "azure-reach"), None)
if not show:
    raise SystemExit("Azure Reach show missing from data/shows.json")
if show.get("basePath") != "data/shows/azure-reach":
    raise SystemExit(f"Unexpected Azure Reach basePath: {show.get('basePath')}")

scene_files = show.get("scenesFiles") or ([show["scenesFile"]] if show.get("scenesFile") else [])
if scene_files != ["pages_i01_01-11.json", "pages_i01_12-22.json"]:
    raise SystemExit(f"Unexpected Azure Reach page files: {scene_files}")

pages = []
for filename in scene_files:
    path = SHOW / filename
    if not path.exists():
        raise SystemExit(f"Manifest references missing Azure Reach page file: {filename}")
    chunk = load_json(path)
    if not isinstance(chunk, list) or not chunk:
        raise SystemExit(f"{filename}: expected nonempty page list")
    pages.extend(chunk)

if len(pages) != 22:
    raise SystemExit(f"Issue 1 must contain exactly 22 page recipes; found {len(pages)}")

ids = [page.get("id") for page in pages]
if len(ids) != len(set(ids)):
    dupes = [key for key, count in Counter(ids).items() if count > 1]
    raise SystemExit(f"Duplicate Azure Reach page IDs: {dupes}")

characters = load_json(SHOW / "characters.json")
known_handles = {entry.get("handle") for entry in characters.values() if isinstance(entry, dict) and entry.get("handle")}
factions = load_json(SHOW / "factions.json")
regions = load_json(SHOW / "regions.json")
region_text = str(regions.get("AZR_Marine_Park", {}).get("text", "")).lower()
if "safe" not in region_text or "animals" not in region_text:
    raise SystemExit("Azure Reach region context must lock animal safety globally")

for index, page in enumerate(pages, start=1):
    expected_id = f"AZR_I01_P{index:02d}"
    if page.get("id") != expected_id:
        raise SystemExit(f"Page {index}: expected ID {expected_id}, found {page.get('id')}")
    if page.get("issue") != "I01" or page.get("page") != index:
        raise SystemExit(f"{expected_id}: issue/page metadata mismatch")
    expected_panels = EXPECTED_PANEL_COUNTS[index - 1]
    if page.get("panelCount") != expected_panels:
        raise SystemExit(
            f"{expected_id}: expected {expected_panels} panels, found {page.get('panelCount')}"
        )
    if not page.get("title") or not page.get("summary"):
        raise SystemExit(f"{expected_id}: missing title or summary")
    if not page.get("source") or "Compressed Draft 3" not in page["source"]:
        raise SystemExit(f"{expected_id}: missing Draft 3 source lock")
    if not page.get("settingText"):
        raise SystemExit(f"{expected_id}: missing source-locked setting text")
    if page.get("region") not in regions:
        raise SystemExit(f"{expected_id}: unknown region {page.get('region')}")
    for faction in page.get("factions", []):
        if faction not in factions:
            raise SystemExit(f"{expected_id}: unknown faction {faction}")

    format_line = page.get("formatLine", "")
    if "comic-book page" not in format_line or "video" not in format_line.lower():
        raise SystemExit(f"{expected_id}: formatLine must explicitly request comic page and reject video")
    if "10-second vertical clip" in format_line:
        raise SystemExit(f"{expected_id}: inherited video format leaked into page recipe")

    direction = page.get("directionInline")
    if not isinstance(direction, list) or len(direction) < 4:
        raise SystemExit(f"{expected_id}: insufficient production direction")
    direction_text = "\n".join(str(entry.get("text", "")) for entry in direction)
    required_locks = ["SOURCE-LOCKED", "LETTERING", "CHARACTER CONTINUITY", "CAMERA / LIGHT"]
    missing = [lock for lock in required_locks if lock not in direction_text]
    if missing:
        raise SystemExit(f"{expected_id}: missing production locks {missing}")
    if f"exactly {expected_panels} panels" not in direction_text:
        raise SystemExit(f"{expected_id}: panel-count lock not repeated in production direction")

    for character in page.get("charactersInline", []):
        handle = character.get("handle")
        if not handle or handle not in known_handles:
            raise SystemExit(f"{expected_id}: unknown or missing character handle {handle!r}")
        if not handle.startswith("@azr."):
            raise SystemExit(f"{expected_id}: non-Azure handle leaked into character list: {handle}")

    for line in page.get("dialogueInline", []):
        text = line.get("text")
        subtext = line.get("subtext", "")
        if not text:
            raise SystemExit(f"{expected_id}: blank dialogue entry")
        handle = line.get("handle")
        if handle:
            if handle not in known_handles:
                raise SystemExit(f"{expected_id}: unknown dialogue handle {handle}")
            if not handle.startswith("@azr."):
                raise SystemExit(f"{expected_id}: non-Azure handle leaked into dialogue: {handle}")
        match = re.search(r"Panel\s+(\d+)", subtext, re.IGNORECASE)
        if not match:
            raise SystemExit(f"{expected_id}: dialogue lacks panel allocation: {text!r}")
        panel_number = int(match.group(1))
        if not (1 <= panel_number <= expected_panels):
            raise SystemExit(
                f"{expected_id}: dialogue allocated to invalid panel {panel_number}: {text!r}"
            )
        if "exact" not in subtext.lower():
            raise SystemExit(f"{expected_id}: dialogue missing exact-lettering lock: {text!r}")

print("Azure Reach validation passed")
print("Issue 1 pages:", len(pages))
print("Panel counts:", EXPECTED_PANEL_COUNTS)
print("Total panels:", sum(EXPECTED_PANEL_COUNTS))
print("Page range:", ids[0], "..", ids[-1])
