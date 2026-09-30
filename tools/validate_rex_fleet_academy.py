#!/usr/bin/env python3
"""Mechanical integrity checks for the Rex Fleet Academy page-production package."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SHOW_DIR = DATA / "shows" / "rex-fleet-academy"
SHOWS = DATA / "shows.json"
RF_CHARACTERS = DATA / "shows" / "rex-fleet-s1" / "characters.json"
PACKAGE_README = SHOW_DIR / "README.md"
REFERENCE_README = ROOT / "production" / "references" / "rex-fleet-academy" / "README.md"

SHELVES = (
    "blocking.json", "characters.json", "dialogue.json", "direction.json",
    "factions.json", "lighting.json", "mood.json", "negatives.json",
    "regions.json", "settings.json",
)


def load(path: Path):
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def main():
    shows = load(SHOWS)
    shelves = {name: load(SHOW_DIR / name) for name in SHELVES}
    pages = load(SHOW_DIR / "pages_i01.json")
    rf_characters = load(RF_CHARACTERS)

    for name, value in shelves.items():
        assert isinstance(value, dict), f"{name} must be a JSON object"

    entries = [s for s in shows if s.get("seriesId") == "rex-fleet-academy"]
    assert len(entries) == 1, f"Expected one Academy issue entry, found {len(entries)}"
    entry = entries[0]
    assert entry.get("id") == "rex-fleet-academy-i01"
    assert entry.get("name") == "Rex Fleet Academy — Issue 1 — Between the Beacons"
    assert entry.get("seriesName") == "Rex Fleet Academy"
    assert entry.get("issueLabel") == "Issue 1 — Between the Beacons"
    assert entry.get("basePath") == "data/shows/rex-fleet-academy"
    assert entry.get("scenesFile") == "pages_i01.json"
    assert entry.get("includeIdPattern") == "^RFA_I01_"
    assert entry.get("unitLabel") == "PAGE"
    generation = entry.get("generationLine", "")
    assert "comic page" in generation.lower()
    assert "rex fleet academy" in generation.lower()
    assert "10-second vertical clip" not in generation.lower()

    assert isinstance(pages, list), "pages_i01.json must be a list"
    assert len(pages) == 24, f"Expected 24 pages, found {len(pages)}"
    expected_ids = [f"RFA_I01_P{n:02d}" for n in range(1, 25)]
    ids = [p.get("id") for p in pages]
    assert ids == expected_ids, "Academy page IDs/order invalid"
    assert len(ids) == len(set(ids)), "Duplicate Academy page IDs"

    characters = shelves["characters.json"]
    factions = shelves["factions.json"]
    regions = shelves["regions.json"]
    settings = shelves["settings.json"]
    direction = shelves["direction.json"]

    handles_to_ids = {
        c.get("handle"): cid for cid, c in characters.items() if c.get("handle")
    }
    assert len(handles_to_ids) == len([c for c in characters.values() if c.get("handle")]), "Duplicate character handles"
    names = [c.get("name") for c in characters.values() if c.get("name")]
    assert len(names) == len(set(names)), "Duplicate character names"

    editorial_indices = {0, 23}
    story_pages = []
    for index, page in enumerate(pages):
        pid = page["id"]
        assert isinstance(page.get("summary"), str) and page["summary"].strip(), f"{pid}: missing summary"
        panel_plan = page.get("panelPlan")
        assert isinstance(panel_plan, list) and panel_plan, f"{pid}: missing panel plan"

        dialogue = page.get("dialogueInline", [])
        assert isinstance(dialogue, list), f"{pid}: dialogueInline must be a list"

        if index in editorial_indices:
            assert not page.get("sceneId"), f"{pid}: editorial page must not claim a story scene"
            assert isinstance(page.get("settingText"), str) and page["settingText"].strip(), f"{pid}: missing editorial art direction"
            assert not page.get("continuityFrom"), f"{pid}: editorial page must not inherit continuity"
            assert dialogue, f"{pid}: editorial copy missing"
            for line in dialogue:
                assert line.get("speaker") == "CAPTION", f"{pid}: editorial text must use CAPTION"
                assert isinstance(line.get("text"), str) and line["text"].strip(), f"{pid}: blank editorial text"
            continue

        story_pages.append(page)
        setting = page.get("setting")
        region = page.get("region")
        assert setting in settings, f"{pid}: unknown setting {setting!r}"
        assert region in regions, f"{pid}: unknown region {region!r}"

        for faction in page.get("factions", []):
            assert faction in factions, f"{pid}: unknown faction {faction}"

        cast = set(page.get("characters", []))
        assert cast, f"{pid}: story page needs a cast"
        for cid in cast:
            assert cid in characters, f"{pid}: unknown character {cid}"

        for key in page.get("direction", []):
            assert key in direction, f"{pid}: unknown direction {key}"

        for line in dialogue:
            text = line.get("text")
            assert isinstance(text, str) and text.strip(), f"{pid}: blank dialogue"
            handle = line.get("handle")
            if handle:
                assert handle in handles_to_ids, f"{pid}: unknown dialogue handle {handle}"
                assert handles_to_ids[handle] in cast, f"{pid}: speaker {handle} absent from cast"

    assert len(story_pages) == 22, f"Expected 22 story pages, found {len(story_pages)}"

    expected_spans = [
        ("RFA_I01_S01", 3),
        ("RFA_I01_S02", 3),
        ("RFA_I01_S03", 3),
        ("RFA_I01_S04", 3),
        ("RFA_I01_S05", 3),
        ("RFA_I01_S06", 4),
        ("RFA_I01_S07", 3),
    ]
    cursor = 0
    for scene_id, count in expected_spans:
        for offset in range(count):
            page = story_pages[cursor]
            assert page.get("sceneId") == scene_id, f"{page['id']}: expected {scene_id}"
            if offset == 0:
                assert not page.get("continuityFrom"), f"{page['id']}: new scene must not inherit prior scene"
            else:
                previous = story_pages[cursor - 1]["id"]
                assert page.get("continuityFrom") == previous, f"{page['id']}: must continue from {previous}"
            cursor += 1
    assert cursor == len(story_pages)

    local_jia = characters.get("C_jia_morgan")
    rf_jia = rf_characters.get("C_jia_morgan")
    assert local_jia and rf_jia, "Jia Morgan missing from Academy or Rex Fleet"
    for field in ("name", "handle", "visualAnchor"):
        assert local_jia.get(field) == rf_jia.get(field), f"Jia {field} diverges from Rex Fleet continuity"

    assert PACKAGE_README.exists(), "Academy package README missing"
    assert REFERENCE_README.exists(), "Academy visual-reference README missing"

    print("Rex Fleet Academy validation passed")
    print("1 issue / 24 pages / 22 story pages / 7 scenes / valid shelves and cross-series Jia continuity")


if __name__ == "__main__":
    main()
