#!/usr/bin/env python3
"""Validate current Echoes of a Forgotten War RexPrompt production structure."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data" / "shows" / "echoes-forgotten-war-s1"
MANIFEST = ROOT / "data" / "shows.json"
SCENE_FILES = [SHOW / f"scenes_e{i:02d}.json" for i in range(1, 9)]
REFERENCE_POLICY = ROOT / "production" / "references" / "echoes-forgotten-war" / "README.md"
REFERENCE_PACK = ROOT / "production" / "references" / "echoes-forgotten-war" / "visual-reference-pack.json"

STORY_COUNTS = {1: 17, 2: 16, 3: 15, 4: 16, 5: 16, 6: 15, 7: 16, 8: 18}
TOTAL_COUNTS = {issue: count + 2 for issue, count in STORY_COUNTS.items()}
CHAMPION_ISSUE = {
    "EFW_Starbreaker": 1,
    "EFW_Redlin": 2,
    "EFW_Atlas": 3,
    "EFW_Arbiter": 4,
    "EFW_Afterlight": 5,
    "EFW_Flux": 6,
    "EFW_Oryon": 7,
    "EFW_Kyn": 8,
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def expected_ids(issue: int) -> list[str]:
    story = [f"EFW_S1E{issue:02d}_S{i:02d}" for i in range(1, STORY_COUNTS[issue] + 1)]
    return [f"EFW_S1E{issue:02d}_EDITOR_OPEN", *story, f"EFW_S1E{issue:02d}_EDITOR_CLOSE"]


def validate_manifest() -> None:
    manifest = load(MANIFEST)
    matches = [entry for entry in manifest if entry.get("id") == "echoes-forgotten-war-s1"]
    assert len(matches) == 1, f"Expected one Echoes manifest entry, found {len(matches)}"
    entry = matches[0]
    assert entry.get("basePath") == "data/shows/echoes-forgotten-war-s1"
    assert entry.get("scenesFiles") == [p.name for p in SCENE_FILES]
    assert not entry.get("sceneOverlays"), "Retired enhancement overlays must not return"
    assert entry.get("unitLabel") == "PAGE"
    assert entry.get("seriesId") == "echoes-forgotten-war"
    assert entry.get("seriesName") == "Echoes of a Forgotten War"
    assert "generationLine" not in entry, (
        "Echoes manifest must not override the package assembler generation contract"
    )


def validate_editorial(page: dict, page_id: str) -> None:
    assert page.get("id") == page_id
    assert isinstance(page.get("summary"), str) and page["summary"].strip(), page_id
    assert isinstance(page.get("settingText"), str) and page["settingText"].strip(), page_id
    assert not page.get("continuityFrom"), f"{page_id}: editorial page inherited story continuity"

    plan = page.get("panelPlan")
    assert isinstance(plan, list) and plan, f"{page_id}: missing editorial panel plan"
    for block in plan:
        assert isinstance(block, dict) and isinstance(block.get("text"), str) and block["text"].strip(), (
            f"{page_id}: bad editorial panel-plan block"
        )

    lines = page.get("dialogueInline")
    assert isinstance(lines, list) and lines, f"{page_id}: missing editorial copy"
    for line in lines:
        assert isinstance(line, dict), f"{page_id}: malformed editorial line"
        assert line.get("speaker") == "CAPTION", f"{page_id}: editorial lettering must use CAPTION speaker"
        assert isinstance(line.get("text"), str) and line["text"].strip(), f"{page_id}: empty editorial line"
        assert not line.get("handle"), f"{page_id}: editorial caption should not masquerade as character dialogue"

    directions = page.get("directionInline", [])
    assert isinstance(directions, list) and directions, f"{page_id}: missing editorial production direction"
    for block in directions:
        assert isinstance(block, dict) and isinstance(block.get("text"), str) and block["text"].strip(), (
            f"{page_id}: bad editorial direction block"
        )


def validate_story_page(
    page: dict,
    issue: int,
    chars: dict,
    settings: dict,
    regions: dict,
    story_ids: set[str],
) -> None:
    page_id = page.get("id")
    assert page_id in story_ids, f"Unexpected story page ID: {page_id}"
    assert isinstance(page.get("summary"), str) and page["summary"].strip(), page_id
    assert page.get("setting") or page.get("settingText"), f"{page_id}: missing setting"
    if page.get("setting"):
        assert page["setting"] in settings, f"{page_id}: unknown setting {page['setting']}"
    if page.get("region"):
        assert page["region"] in regions, f"{page_id}: unknown region {page['region']}"

    for char_id in page.get("characters", []):
        assert char_id in chars, f"{page_id}: unknown character {char_id}"

    plan = page.get("panelPlan")
    assert isinstance(plan, list) and plan, f"{page_id}: missing panel plan"
    for block in plan:
        assert isinstance(block, dict) and isinstance(block.get("text"), str) and block["text"].strip(), (
            f"{page_id}: malformed panel-plan block"
        )

    lines = page.get("dialogueInline")
    assert isinstance(lines, list), f"{page_id}: dialogueInline must be a list"
    for line in lines:
        assert isinstance(line, dict), f"{page_id}: malformed dialogue entry"
        assert isinstance(line.get("text"), str) and line["text"].strip(), f"{page_id}: empty dialogue"
        handle = line.get("handle")
        speaker = line.get("speaker")
        assert handle or speaker, f"{page_id}: dialogue owner missing"
        if isinstance(handle, str) and handle.startswith("@"):
            matching = [cid for cid, entry in chars.items() if entry.get("handle") == handle]
            assert matching, f"{page_id}: unknown dialogue handle {handle}"
            assert matching[0] in page.get("characters", []), (
                f"{page_id}: speaker {handle} absent from page character list"
            )

    directions = page.get("directionInline", [])
    assert isinstance(directions, list), f"{page_id}: directionInline must be a list"
    for block in directions:
        assert isinstance(block, dict) and isinstance(block.get("text"), str) and block["text"].strip(), (
            f"{page_id}: malformed direction block"
        )

    continuity = page.get("continuityFrom")
    if continuity:
        assert continuity in story_ids, f"{page_id}: continuity target is not a story page: {continuity}"


def validate_pages() -> None:
    chars = load(SHOW / "characters.json")
    settings = load(SHOW / "settings.json")
    regions = load(SHOW / "regions.json")

    all_ids: set[str] = set()
    total = 0
    champion_first_issue: dict[str, int] = {}

    for issue, path in enumerate(SCENE_FILES, start=1):
        pages = load(path)
        assert isinstance(pages, list), path.name
        assert len(pages) == TOTAL_COUNTS[issue], (
            f"{path.name}: expected {TOTAL_COUNTS[issue]} pages, found {len(pages)}"
        )

        ids = [page.get("id") for page in pages]
        expected = expected_ids(issue)
        assert ids == expected, f"{path.name}: page order/IDs changed"

        validate_editorial(pages[0], expected[0])
        validate_editorial(pages[-1], expected[-1])

        story_ids = set(expected[1:-1])
        for page in pages[1:-1]:
            validate_story_page(page, issue, chars, settings, regions, story_ids)
            for char_id in page.get("characters", []):
                if char_id in CHAMPION_ISSUE:
                    champion_first_issue.setdefault(char_id, issue)

        for page_id in ids:
            assert page_id not in all_ids, f"Duplicate page ID {page_id}"
            all_ids.add(page_id)

        total += len(pages)

    assert total == 145, f"Expected 145 production pages, found {total}"
    assert len(all_ids) == 145

    for champion, expected_issue in CHAMPION_ISSUE.items():
        assert champion_first_issue.get(champion) == expected_issue, (
            f"{champion} first appears in Issue {champion_first_issue.get(champion)}, expected Issue {expected_issue}"
        )


def validate_architecture() -> None:
    expected_counts = {str(issue): TOTAL_COUNTS[issue] for issue in range(1, 9)}
    expected_counts["season"] = 145

    architecture = load(SHOW / "season_architecture_v2.json")
    assert architecture.get("productionPageCounts") == expected_counts
    assert "145 production pages" in architecture.get("format", "")
    order = [entry.get("newChampion") for entry in architecture.get("revealOrder", [])]
    assert order == ["Starbreaker", "Redlin", "Atlas", "Arbiter", "Afterlight", "Flux", "Oryon", "Kyn"]

    status = load(SHOW / "development_status.json")
    assert status.get("productionPageCounts") == expected_counts
    assert "145 production pages" in status.get("productionMode", "")
    assert "129 unchanged story pages" in status.get("writingRecoveryFrontier", "")
    assert "EFW_S1E01_EDITOR_OPEN" in status.get("visualReferenceState", "")
    for issue in range(1, 9):
        entry = status.get("issues", {}).get(str(issue), {})
        assert entry.get("recipeFile") == f"scenes_e{issue:02d}.json"
        assert entry.get("pageCount") == TOTAL_COUNTS[issue]
        assert entry.get("panelPlan") is True

    spine = load(SHOW / "comic_page_spine_v1.json")
    assert spine.get("productionPageCounts") == expected_counts
    issues = spine.get("issues", [])
    assert len(issues) == 8
    for issue_number, issue in enumerate(issues, start=1):
        assert issue.get("issue") == issue_number
        beats = issue.get("pages", [])
        assert len(beats) == 22, f"Issue {issue_number}: expected 22 retained development beats"
        assert [beat.get("page") for beat in beats] == list(range(1, 23))


def validate_characters_and_references() -> None:
    chars = load(SHOW / "characters.json")
    required = {
        "EFW_Theo", "EFW_Rae", "EFW_Adrian", "EFW_Vark", "EFW_Caelum",
        "EFW_Starbreaker", "EFW_Redlin", "EFW_Atlas", "EFW_Arbiter",
        "EFW_Afterlight", "EFW_Flux", "EFW_Oryon", "EFW_Kyn", "EFW_Mero",
    }
    assert required.issubset(chars), f"Missing required Echoes characters: {sorted(required - set(chars))}"
    for char_id, entry in chars.items():
        assert entry.get("name") and entry.get("handle") and entry.get("visualAnchor"), char_id
        locks = entry.get("continuityLocks")
        assert isinstance(locks, list) and locks, f"{char_id}: missing continuity locks"

    assert REFERENCE_POLICY.exists(), "Missing Echoes visual-reference policy"
    assert REFERENCE_PACK.exists(), "Missing Echoes visual-reference pack"
    pack = load(REFERENCE_PACK)
    assert pack.get("status") == "active", "Echoes visual-reference pack is not active"
    refs = pack.get("references")
    assert isinstance(refs, list) and len(refs) >= 13, "Echoes visual-reference pack is incomplete"
    for ref in refs:
        image = ref.get("image")
        assert image, f"Reference missing image path: {ref.get('id')}"
        assert (ROOT / image).exists(), f"Reference image missing: {image}"


def validate_assembler_contract() -> None:
    assembler = load(SHOW / "assembler.json")
    assert assembler.get("unitLabel") == "PAGE"
    assert assembler.get("requirePanelPlan") is True
    assert assembler.get("requireVisualAnchors") is True
    generation = assembler.get("generationLine", "")
    for required in (
        "One assembled RexPrompt recipe equals one page only",
        "Painterly prestige cosmic science-fiction sequential art",
        "Present-day spaces are tactile and inhabited",
        "Ancient spaces are monumental but physically legible",
        "Follow the PANEL PLAN as page architecture",
        "letter only the exact DIALOGUE supplied by the recipe",
    ):
        assert required in generation, f"Echoes generation contract missing: {required}"


def main() -> None:
    validate_manifest()
    validate_pages()
    validate_architecture()
    validate_characters_and_references()
    validate_assembler_contract()
    print(
        "Echoes validation passed: 8 issues / 145 PAGE recipes "
        "(129 story + 16 editorial bookends), valid reveal order, references, "
        "page counts, continuity targets and package generation contract."
    )


if __name__ == "__main__":
    main()
