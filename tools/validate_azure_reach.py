#!/usr/bin/env python3
import base64
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW_ID = "azure-reach-s1"
SHOW = ROOT / "data" / "shows" / SHOW_ID
MANIFEST = ROOT / "data" / "shows.json"
INDEX = ROOT / "index.html"

EXPECTED = [
    (1, "Public Magic", 5), (2, "Ops Reality", 6), (3, "Finfluencer Rehearsal", 10),
    (4, "Four Definitions of Success", 5), (5, "Corporate Polish", 6),
    (6, "Guest Relations Front Line", 6), (7, "Brine Squad Walkthrough", 5),
    (8, "Finfluencer Stage", 6), (9, "Corporate Collision", 6), (10, "The Wrong Success", 7),
    (11, "Staff Huddle", 5), (12, "Guest Reset", 7), (13, "Fleur Reframes the Room", 5),
    (14, "Sponsor Containment", 5), (15, "Live Segment", 7), (16, "Quiet Window", 6),
    (17, "The Real Moment", 5), (18, "Public Success", 5), (19, "Post-Event Debrief", 6),
    (20, "Julian Pitches Up", 7), (21, "The Lesson Goes Wrong", 8), (22, "Backstage Button", 8),
]
STALE = ("The Pelican Drop", "Julian Vale", "Flora Fontaine", "Pip Hart", "Pippa Hart", "@arv1.", "@starsplit.")
LEGACY_PREFIXES = (
    "AZURE REACH VISUAL LANGUAGE:", "PAGE ACTION — SOURCE-LOCKED:", "CHARACTER CONTINUITY —",
    "LOCATION / PROP / STATE CONTINUITY —", "COMIC PAGE / LETTERING —",
)


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def decode(path):
    raw = "".join(path.read_text(encoding="utf-8").split())
    return json.loads(gzip.decompress(base64.b64decode(raw, validate=True)).decode("utf-8"))


shows = load(MANIFEST)
show = next((s for s in shows if s.get("id") == SHOW_ID), None)
assert show, "Azure Reach missing from data/shows.json"
assert show.get("basePath") == "data/shows/azure-reach-s1"
assert show.get("scenesFile") == "pages_base.json"
assert show.get("unitLabel") == "PAGE"
assert "comic page" in show.get("generationLine", "").lower()

pages = []
for overlay in show.get("sceneOverlays", []):
    assert overlay.get("encoding") == "gzip-base64"
    pages.extend(decode(SHOW / overlay["file"]))
assert len(pages) == 22, len(pages)

characters = load(SHOW / "characters.json")
canonical_handles = {v.get("handle") for v in characters.values() if isinstance(v, dict) and v.get("handle")}
factions = load(SHOW / "factions.json")
regions = load(SHOW / "regions.json")
settings = load(SHOW / "settings.json")
directions = load(SHOW / "direction.json")

all_text = json.dumps(pages, ensure_ascii=False)
for stale in STALE:
    assert stale not in all_text, f"Stale/superseded Azure Reach material: {stale}"

seen = set()
dialogue_count = 0
for page, (number, title, panels) in zip(pages, EXPECTED):
    pid = f"AZR_S1E01_P{number:02d}"
    assert page.get("id") == pid
    assert pid not in seen
    seen.add(pid)
    assert page.get("episode") == "S1E01" and page.get("page") == number
    assert page.get("pageTitle") == title
    assert page.get("panelCount") == panels
    assert len(page.get("panelPlan", [])) == panels
    assert page.get("summary")
    assert page.get("setting") in settings
    assert page.get("region") in regions
    assert all(f in factions for f in page.get("factions", []))

    cast = {c.get("handle") for c in page.get("charactersInline", []) if isinstance(c, dict)}
    assert cast and not (cast - canonical_handles), f"{pid}: bad cast"
    lines = page.get("dialogueInline", [])
    assert lines
    dialogue_count += len(lines)
    for line in lines:
        handle = line.get("handle")
        assert line.get("text") and handle in canonical_handles
        if handle != "@azr.Comments":
            assert handle in cast

    refs = page.get("direction", [])
    assert "AZR_PRODUCTION_CORE" in refs and "AZR_LETTERING" in refs
    assert not (set(refs) - set(directions)), f"{pid}: unknown direction ref"
    local = page.get("directionInline", []) or []
    assert len(local) <= 2
    for item in local:
        text = item.get("text", "") if isinstance(item, dict) else str(item)
        assert text.startswith(("PAGE CONTINUITY —", "PAGE DESIGN —"))
        assert not text.startswith(LEGACY_PREFIXES)
    assert page["summary"] not in json.dumps(local, ensure_ascii=False)

maya = json.dumps(characters["AZR_Maya"], ensure_ascii=False).lower()
pip = json.dumps(characters["AZR_Pip"], ensure_ascii=False).lower()
assert "dark navy" in maya and "no hot pink" in maya and "never visually merge with pip" in maya
assert "lighter blue/teal" in pip and "tablet" in pip and "never share maya" in pip

for line in (
    "Care, not contact.", "Sea Turtle Tuesdays. Easier to say. Same turtle.",
    "Shellabration Saturdays.", "Sea Turtle Tuesdays was better.", "Out front, it still looked effortless.",
):
    assert line in all_text, f"Missing source-locked critical line: {line}"

index = INDEX.read_text(encoding="utf-8")
assert 'if(s.direction?.length||s.directionInline?.length){out.push("\\n[DIRECTION]")' in index

print("Azure Reach Issue 1 validation passed")
print("Pages:", len(pages))
print("Panels:", sum(p["panelCount"] for p in pages))
print("Dialogue/lettering entries:", dialogue_count)
