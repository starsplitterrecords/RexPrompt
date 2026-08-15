#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW_ID = "azure-reach-s1"
SHOW = ROOT / "data" / "shows" / SHOW_ID
MANIFEST = ROOT / "data" / "shows.json"
INDEX = ROOT / "index.html"

EXPECTED = [
    (1, "Public Magic", 5),
    (2, "Ops Reality", 6),
    (3, "Finfluencer Rehearsal", 10),
    (4, "Four Definitions of Success", 5),
    (5, "Corporate Polish", 6),
    (6, "Guest Relations Front Line", 6),
    (7, "Brine Squad Walkthrough", 5),
    (8, "Finfluencer Stage", 6),
    (9, "Corporate Collision", 6),
    (10, "The Wrong Success", 7),
    (11, "Staff Huddle", 5),
    (12, "Guest Reset", 7),
    (13, "Fleur Reframes the Room", 5),
    (14, "Sponsor Containment", 5),
    (15, "Live Segment", 7),
    (16, "Quiet Window", 6),
    (17, "The Real Moment", 5),
    (18, "Public Success", 5),
    (19, "Post-Event Debrief", 6),
    (20, "Julian Pitches Up", 7),
    (21, "The Lesson Goes Wrong", 8),
    (22, "Backstage Button", 8),
]
DIR_PREFIXES = (
    "AZURE REACH VISUAL LANGUAGE:",
    "PAGE ACTION — SOURCE-LOCKED:",
    "CHARACTER CONTINUITY —",
    "LOCATION / PROP / STATE CONTINUITY —",
    "COMIC PAGE / LETTERING —",
)
STALE = (
    "The Pelican Drop",
    "Julian Vale",
    "Flora Fontaine",
    "Pip Hart",
    "Pippa Hart",
    "@arv1.",
    "@starsplit.",
)
REQUIRED_FILES = (
    "blocking.json", "characters.json", "dialogue.json", "direction.json",
    "factions.json", "lighting.json", "mood.json", "negatives.json",
    "regions.json", "settings.json", "pages_base.json",
    "encoded/pages_e01_p01_p06.json.gzb64", "encoded/pages_e01_p07_p12.json.gzb64",
    "encoded/pages_e01_p13_p18.json.gzb64", "encoded/pages_e01_p19_p22.json.gzb64",
)

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

for name in REQUIRED_FILES:
    if not (SHOW / name).exists():
        raise SystemExit(f"Missing Azure Reach data file: {name}")

shows = load(MANIFEST)
show = next((s for s in shows if s.get("id") == SHOW_ID), None)
if not show:
    raise SystemExit("Azure Reach missing from data/shows.json")
if show.get("basePath") != "data/shows/azure-reach-s1":
    raise SystemExit("Azure Reach basePath drift")
if show.get("scenesFile") != "pages_base.json":
    raise SystemExit("Azure Reach base pages file drift")
overlays = show.get("sceneOverlays", [])
expected_overlays = [
    {"file": "encoded/pages_e01_p01_p06.json.gzb64", "encoding": "gzip-base64"},
    {"file": "encoded/pages_e01_p07_p12.json.gzb64", "encoding": "gzip-base64"},
    {"file": "encoded/pages_e01_p13_p18.json.gzb64", "encoding": "gzip-base64"},
    {"file": "encoded/pages_e01_p19_p22.json.gzb64", "encoding": "gzip-base64"},
]
if overlays != expected_overlays:
    raise SystemExit("Azure Reach encoded page overlay drift")
if show.get("unitLabel") != "PAGE":
    raise SystemExit("Azure Reach must assemble as PAGE units")
if "comic page" not in show.get("generationLine", "").lower():
    raise SystemExit("Azure Reach generationLine must explicitly request a comic page")
if "10-second" in show.get("generationLine", "").lower():
    raise SystemExit("Azure Reach must not inherit video generation language")

index = INDEX.read_text(encoding="utf-8")
for required in ("store.__show=show", 'unitLabel=show.unitLabel||"SCENE"', 'if(s.panelPlan?.length){out.push("\\n[PANEL PLAN]")'):
    if required not in index:
        raise SystemExit(f"RexPrompt page-mode support missing: {required}")

import base64, gzip
pages = []
for overlay in overlays:
    encoded = "".join((SHOW / overlay["file"]).read_text(encoding="utf-8").split())
    pages.extend(json.loads(gzip.decompress(base64.b64decode(encoded, validate=True)).decode("utf-8")))
if len(pages) != 22:
    raise SystemExit(f"Expected 22 Issue #1 pages, found {len(pages)}")

characters = load(SHOW / "characters.json")
canonical_handles = {v.get("handle") for v in characters.values() if isinstance(v, dict) and v.get("handle")}
factions = load(SHOW / "factions.json")
regions = load(SHOW / "regions.json")
settings = load(SHOW / "settings.json")

all_text = json.dumps(pages, ensure_ascii=False)
for stale in STALE:
    if stale in all_text:
        raise SystemExit(f"Stale/superseded Azure Reach material found in production pages: {stale}")

seen_ids = set()
dialogue_count = 0
for page, (number, title, panels) in zip(pages, EXPECTED):
    expected_id = f"AZR_S1E01_P{number:02d}"
    if page.get("id") != expected_id:
        raise SystemExit(f"Page {number}: expected id {expected_id}, found {page.get('id')}")
    if page["id"] in seen_ids:
        raise SystemExit(f"Duplicate page id: {page['id']}")
    seen_ids.add(page["id"])
    if page.get("episode") != "S1E01" or page.get("page") != number:
        raise SystemExit(f"{expected_id}: episode/page numbering drift")
    if page.get("pageTitle") != title:
        raise SystemExit(f"{expected_id}: title drift: {page.get('pageTitle')!r}")
    if page.get("panelCount") != panels:
        raise SystemExit(f"{expected_id}: expected {panels} panels, found {page.get('panelCount')}")
    if len(page.get("panelPlan", [])) != panels:
        raise SystemExit(f"{expected_id}: panelPlan must contain exactly {panels} entries")
    if not page.get("summary"):
        raise SystemExit(f"{expected_id}: missing page summary")
    if page.get("setting") not in settings:
        raise SystemExit(f"{expected_id}: unknown setting {page.get('setting')}")
    if page.get("region") not in regions:
        raise SystemExit(f"{expected_id}: unknown region {page.get('region')}")
    for faction in page.get("factions", []):
        if faction not in factions:
            raise SystemExit(f"{expected_id}: unknown faction {faction}")

    cast_handles = {c.get("handle") for c in page.get("charactersInline", []) if isinstance(c, dict)}
    if not cast_handles:
        raise SystemExit(f"{expected_id}: missing charactersInline")
    unknown_cast = cast_handles - canonical_handles
    if unknown_cast:
        raise SystemExit(f"{expected_id}: unknown cast handles {sorted(unknown_cast)}")

    lines = page.get("dialogueInline", [])
    if not lines:
        raise SystemExit(f"{expected_id}: missing exact dialogue/lettering data")
    dialogue_count += len(lines)
    for line in lines:
        if not line.get("text"):
            raise SystemExit(f"{expected_id}: blank dialogue/lettering line")
        handle = line.get("handle")
        if handle not in canonical_handles:
            raise SystemExit(f"{expected_id}: noncanonical dialogue handle {handle}")
        if handle != "@azr.Comments" and handle not in cast_handles:
            raise SystemExit(f"{expected_id}: dialogue speaker {handle} missing from charactersInline")

    direction = [x.get("text", "") for x in page.get("directionInline", []) if isinstance(x, dict)]
    if len(direction) != 5:
        raise SystemExit(f"{expected_id}: exactly five production locks are required")
    for got, prefix in zip(direction, DIR_PREFIXES):
        if not got.startswith(prefix):
            raise SystemExit(f"{expected_id}: direction schema mismatch; expected {prefix}")
    locked_action = direction[1].split(DIR_PREFIXES[1], 1)[1].strip()
    if locked_action != page["summary"]:
        raise SystemExit(f"{expected_id}: PAGE ACTION must equal the source-locked summary")
    if "animal" not in direction[0].lower() or "safe" not in direction[0].lower():
        raise SystemExit(f"{expected_id}: absolute animal-safety visual rule missing")
    if "professional" not in direction[4].lower() or "letter" not in direction[4].lower():
        raise SystemExit(f"{expected_id}: lettering production lock missing")

# Highest-risk visual identity lock: Maya vs Pip.
maya = json.dumps(characters["AZR_Maya"], ensure_ascii=False).lower()
pip = json.dumps(characters["AZR_Pip"], ensure_ascii=False).lower()
if "dark navy" not in maya or "no hot pink" not in maya or "never visually merge with pip" not in maya:
    raise SystemExit("Maya visual lock incomplete")
if "lighter blue/teal" not in pip or "tablet" not in pip or "never share maya" not in pip:
    raise SystemExit("Pip visual lock incomplete")

critical = (
    "Care, not contact.",
    "Sea Turtle Tuesdays. Easier to say. Same turtle.",
    "Shellabration Saturdays.",
    "Sea Turtle Tuesdays was better.",
    "Out front, it still looked effortless.",
)
for line in critical:
    if line not in all_text:
        raise SystemExit(f"Missing source-locked critical line: {line}")

print("Azure Reach validation passed")
print("Pages:", len(pages))
print("Panels:", sum(p["panelCount"] for p in pages))
print("Dialogue/lettering entries:", dialogue_count)
print("Canonical handles:", len(canonical_handles))

