#!/usr/bin/env python3
"""Mechanical integrity checks for the Shattering page-production package.

This protects the active comic-page contract, reference integrity, scene continuity,
and cross-series identity normalization. It deliberately does not score narrative
quality or freeze creative choices such as exact dialogue, page density, or panel count.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SHOW_DIR = DATA / "shows" / "shattering"
SHOWS = DATA / "shows.json"
SOURCE = DATA / "scenes_shattering.json"
CHARACTERS = DATA / "characters.json"
SETTINGS = DATA / "settings.json"
FACTIONS = DATA / "factions.json"
REGIONS = DATA / "regions.json"
RF_CHARACTERS = DATA / "shows" / "rex-fleet-s1" / "characters.json"
PACKAGE_README = SHOW_DIR / "README.md"
REFERENCE_README = ROOT / "production" / "references" / "shattering" / "README.md"
RECOVERY_NOTE = ROOT / "production" / "references" / "shattering" / "recovery-binary-note.md"
REFERENCE_INVENTORY = ROOT / "production" / "references" / "shattering" / "reference-inventory.json"


def load(path: Path):
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def main():
    shows = load(SHOWS)
    source = load(SOURCE)
    characters = load(CHARACTERS)
    settings = load(SETTINGS)
    factions = load(FACTIONS)
    regions = load(REGIONS)
    rf_characters = load(RF_CHARACTERS)

    source_ids = {scene.get("id") for scene in source}
    assert None not in source_ids, "A Shattering source scene is missing an id"
    assert len(source_ids) == len(source), "Duplicate Shattering source scene ids"

    handles_to_ids = {
        character.get("handle"): cid
        for cid, character in characters.items()
        if character.get("handle")
    }

    entries = [s for s in shows if s.get("seriesId") == "shattering"]
    assert len(entries) == 6, f"Expected 6 Shattering issue entries, found {len(entries)}"

    all_pages = []
    all_page_ids = set()
    active_scene_ids = set()

    for issue, entry in enumerate(entries, start=1):
        expected_id = f"shattering-i{issue:02d}"
        assert entry.get("id") == expected_id, f"Issue {issue}: show id mismatch"
        assert entry.get("name") == f"Shattering — Issue {issue}", f"Issue {issue}: display name mismatch"
        assert entry.get("issueLabel") == f"Issue {issue}", f"Issue {issue}: issue label mismatch"
        assert entry.get("unitLabel") == "PAGE", f"Issue {issue}: production unit must be PAGE"
        assert "comic page" in entry.get("generationLine", "").lower(), f"Issue {issue}: comic-page generation line missing"
        assert "10-second vertical clip" not in entry.get("generationLine", "").lower(), f"Issue {issue}: legacy video mode remains"

        expected_file = f"shows/shattering/pages_i{issue:02d}.json"
        assert entry.get("basePath") == "data", f"Issue {issue}: unexpected basePath"
        assert entry.get("scenesFile") == expected_file, f"Issue {issue}: active page file mismatch"
        assert entry.get("includeIdPattern") == f"^SHAT_I{issue:02d}_", f"Issue {issue}: include pattern mismatch"
        assert entry.get("scenesFile") != "scenes_shattering.json", f"Issue {issue}: source scene file still active"

        pages = load(DATA / expected_file)
        assert len(pages) == 22, f"Issue {issue}: expected 22 pages, found {len(pages)}"
        expected_ids = [f"SHAT_I{issue:02d}_P{page:02d}" for page in range(1, 23)]
        ids = [p.get("id") for p in pages]
        assert ids == expected_ids, f"Issue {issue}: page order/IDs invalid"

        for index, page in enumerate(pages):
            pid = page["id"]
            assert pid not in all_page_ids, f"Duplicate page ID {pid}"
            all_page_ids.add(pid)

            assert isinstance(page.get("summary"), str) and page["summary"].strip(), f"{pid}: missing summary"
            panel_plan = page.get("panelPlan")
            assert isinstance(panel_plan, list) and panel_plan, f"{pid}: missing panel plan"
            assert all(isinstance(item, str) and item.strip() for item in panel_plan), f"{pid}: invalid panel-plan entry"
            assert "episode" not in page and "act" not in page, f"{pid}: source scene fields survived"

            scene_id = page.get("sceneId")
            assert scene_id in source_ids, f"{pid}: unknown source scene {scene_id}"
            active_scene_ids.add(scene_id)

            setting = page.get("setting")
            region = page.get("region")
            assert setting in settings, f"{pid}: unknown setting {setting}"
            assert region in regions, f"{pid}: unknown region {region}"

            for faction in page.get("factions", []):
                assert faction in factions, f"{pid}: unknown faction {faction}"

            page_characters = set(page.get("characters", []))
            for character in page_characters:
                assert character in characters, f"{pid}: unknown character {character}"

            dialogue_inline = page.get("dialogueInline", [])
            assert isinstance(dialogue_inline, list), f"{pid}: dialogueInline must be a list"
            for line in dialogue_inline:
                assert isinstance(line, dict), f"{pid}: malformed dialogue entry"
                handle = line.get("handle")
                text = line.get("text")
                assert isinstance(handle, str) and handle, f"{pid}: dialogue handle missing"
                assert isinstance(text, str) and text.strip(), f"{pid}: dialogue text missing"
                if handle.startswith("@"):
                    assert handle in handles_to_ids, f"{pid}: unknown dialogue handle {handle}"
                    speaker_id = handles_to_ids[handle]
                    assert speaker_id in page_characters, f"{pid}: speaker {handle} absent from page character list"

            if index == 0:
                assert not page.get("continuityFrom"), f"{pid}: issue opener should not inherit prior-page continuity"
            else:
                previous = pages[index - 1]
                same_scene = page.get("sceneId") == previous.get("sceneId")
                if same_scene:
                    assert page.get("continuityFrom") == previous["id"], f"{pid}: within-scene continuity must point to prior page"
                else:
                    assert not page.get("continuityFrom"), f"{pid}: new scene must not inherit prior-scene continuity"

        all_pages.extend(pages)

    assert len(all_pages) == 132, f"Expected 132 active pages, found {len(all_pages)}"
    assert active_scene_ids == source_ids, "Active page package and source-scene package do not describe the same scene set"

    assert all(scene.get("region") != "PostBreakNetwork" for scene in source), "Retired invalid PostBreakNetwork region remains in source"
    active_text = json.dumps(all_pages, ensure_ascii=False)
    assert "PostBreakNetwork" not in active_text, "Retired invalid PostBreakNetwork region remains in active pages"

    liora = characters.get("C_liora")
    rf_liora = rf_characters.get("C_liora_virelia")
    assert liora and rf_liora, "Liora identity missing from Shattering or Rex Fleet"
    assert liora.get("name") == rf_liora.get("name") == "Liora Virelia", "Liora name diverges across packages"
    assert liora.get("handle") == rf_liora.get("handle"), "Liora handle diverges across packages"
    assert liora.get("visualAnchor") == rf_liora.get("visualAnchor"), "Liora visual anchor diverges across packages"

    handles = [c.get("handle") for c in characters.values() if c.get("handle")]
    assert len(handles) == len(set(handles)), "Duplicate character handles in Shattering shelf"
    names = [c.get("name") for c in characters.values() if c.get("name")]
    assert len(names) == len(set(names)), "Duplicate character names in Shattering shelf"

    assert REFERENCE_INVENTORY.exists(), "Shattering structured reference inventory missing"
    inventory = load(REFERENCE_INVENTORY)
    assert inventory.get("schemaVersion") == 1, "Shattering reference inventory schemaVersion must be 1"
    assert inventory.get("seriesId") == "shattering", "Shattering reference inventory seriesId mismatch"
    groups = inventory.get("recoveryGroups")
    assert isinstance(groups, list), "Shattering reference inventory recoveryGroups must be a list"
    page_ids = {page["id"] for page in all_pages}
    seen_file_ids = set()
    seen_group_keys = set()
    for group in groups:
        assert isinstance(group, dict), "Every Shattering recovery group must be an object"
        scene_id = group.get("sourceSceneId")
        assert scene_id in source_ids, f"Unknown recovery source scene {scene_id!r}"
        key = (group.get("issueId"), scene_id)
        assert key not in seen_group_keys, f"Duplicate recovery group {key!r}"
        seen_group_keys.add(key)
        page_range = group.get("candidatePageRange")
        assert isinstance(page_range, list) and len(page_range) == 2, f"{scene_id}: candidatePageRange must contain start/end page ids"
        assert page_range[0] in page_ids and page_range[1] in page_ids, f"{scene_id}: candidate page range points outside active Shattering pages"
        candidates = group.get("candidates")
        assert isinstance(candidates, list) and candidates, f"{scene_id}: recovery group must contain at least one candidate"
        for candidate in candidates:
            file_id = candidate.get("fileLibraryId")
            assert isinstance(file_id, str) and file_id.startswith("file_"), f"{scene_id}: invalid File Library id"
            assert file_id not in seen_file_ids, f"Duplicate File Library id {file_id}"
            seen_file_ids.add(file_id)

    assert PACKAGE_README.exists(), "Shattering package README missing"
    assert REFERENCE_README.exists(), "Shattering visual-reference README missing"
    assert RECOVERY_NOTE.exists(), "Historical recovery provenance missing"
    recovery_text = RECOVERY_NOTE.read_text(encoding="utf-8")
    assert "source" in recovery_text.lower(), "Recovery note still presents old scene IDs as current recipes"
    assert "exact active page recipe" in recovery_text, "Recovery note lacks page-level remapping requirement"

    retired_identity_tokens = (
        "Star Splitter " + "Prequel",
        "star-splitter-" + "prequel",
        "P" + "REQ_",
        "prequel" + "-e",
        "validate_star_splitter_" + "prequel",
        "validate-star-splitter-" + "prequel",
    )
    retired_paths = (
        DATA / ("scenes_" + "prequel.json"),
        DATA / "shows" / ("star-splitter-" + "prequel"),
        ROOT / "production" / "references" / ("star-splitter-" + "prequel"),
        ROOT / "tools" / ("validate_star_splitter_" + "prequel.py"),
        ROOT / ".github" / "workflows" / ("validate-star-splitter-" + "prequel.yml"),
    )
    for old_path in retired_paths:
        assert not old_path.exists(), f"Retired Shattering path remains: {old_path.relative_to(ROOT)}"

    text_extensions = {".json", ".md", ".py", ".yml", ".yaml", ".html", ".js", ".txt"}
    for text_path in ROOT.rglob("*"):
        if not text_path.is_file() or text_path.suffix.lower() not in text_extensions:
            continue
        try:
            text = text_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for token in retired_identity_tokens:
            assert token not in text, f"{text_path.relative_to(ROOT)}: retired Shattering identity token remains: {token}"

    print("Shattering validation passed")
    print("6 issues / 132 pages / scene-aware continuity / inline dialogue / valid references / normalized Liora identity")


if __name__ == "__main__":
    main()
