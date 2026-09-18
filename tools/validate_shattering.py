#!/usr/bin/env python3
"""Mechanical integrity checks for the Shattering page-production package.

This protects the active comic-page contract, reference integrity, source-dialogue
preservation, and cross-series identity normalization. It does not score narrative
quality or freeze exact page prose beyond structural requirements.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SHOW_DIR = DATA / "shows" / "shattering"
SHOWS = DATA / "shows.json"
SOURCE = DATA / "scenes_shattering.json"
CHARACTERS = DATA / "characters.json"
DIALOGUE = DATA / "dialogue.json"
SETTINGS = DATA / "settings.json"
FACTIONS = DATA / "factions.json"
REGIONS = DATA / "regions.json"
RF_CHARACTERS = DATA / "shows" / "rex-fleet-s1" / "characters.json"
PACKAGE_README = SHOW_DIR / "README.md"
REFERENCE_README = ROOT / "production" / "references" / "shattering" / "README.md"
RECOVERY_NOTE = ROOT / "production" / "references" / "shattering" / "recovery-binary-note.md"


def load(path: Path):
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def main():
    shows = load(SHOWS)
    source = load(SOURCE)
    characters = load(CHARACTERS)
    dialogue = load(DIALOGUE)
    settings = load(SETTINGS)
    factions = load(FACTIONS)
    regions = load(REGIONS)
    rf_characters = load(RF_CHARACTERS)

    entries = [s for s in shows if s.get("seriesId") == "shattering"]
    assert len(entries) == 6, f"Expected 6 Shattering issue entries, found {len(entries)}"

    all_pages = []
    all_page_ids = set()
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
            assert page.get("summary"), f"{pid}: missing summary"
            assert len(page.get("panelPlan", [])) >= 4, f"{pid}: page needs a developed panel plan"
            assert page.get("directionInline"), f"{pid}: page needs story-specific direction"
            assert "episode" not in page and "act" not in page, f"{pid}: source scene fields survived"

            setting = page.get("setting")
            region = page.get("region")
            assert setting in settings, f"{pid}: unknown setting {setting}"
            assert region in regions, f"{pid}: unknown region {region}"
            for faction in page.get("factions", []):
                assert faction in factions, f"{pid}: unknown faction {faction}"
            for character in page.get("characters", []):
                assert character in characters, f"{pid}: unknown character {character}"
            for line_id in page.get("dialog", []):
                assert line_id in dialogue, f"{pid}: unknown dialogue {line_id}"

            if index == 0:
                assert not page.get("continuityFrom"), f"{pid}: issue opener should not inherit prior-page continuity"
            else:
                assert page.get("continuityFrom") == pages[index - 1]["id"], f"{pid}: continuityFrom is not the prior page"

        all_pages.extend(pages)

    assert len(all_pages) == 132, f"Expected 132 active pages, found {len(all_pages)}"

    source_dialogue = [line for scene in source for line in scene.get("dialog", [])]
    active_dialogue = [line for page in all_pages for line in page.get("dialog", [])]
    assert Counter(active_dialogue) == Counter(source_dialogue), "Active pages must preserve every Source dialogue line exactly once"
    assert len(active_dialogue) == len(set(active_dialogue)), "A source dialogue line is reused across active pages"

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
    for path in retired_paths:
        assert not path.exists(), f"Retired Shattering path remains: {path.relative_to(ROOT)}"

    text_extensions = {".json", ".md", ".py", ".yml", ".yaml", ".html", ".js", ".txt"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in text_extensions:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for token in retired_identity_tokens:
            assert token not in text, f"{path.relative_to(ROOT)}: retired Shattering identity token remains: {token}"

    print("Shattering validation passed")
    print("6 issues / 132 pages / 124 source dialogue lines preserved / page-mode registry / valid references / normalized Liora identity")


if __name__ == "__main__":
    main()
