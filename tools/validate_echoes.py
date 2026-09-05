#!/usr/bin/env python3
"""Validate current Echoes of a Forgotten War RexPrompt production structure."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data" / "shows" / "echoes-forgotten-war-s1"
MANIFEST = ROOT / "data" / "shows.json"
SCENE_FILES = [SHOW / f"scenes_e{i:02d}.json" for i in range(1, 9)]
READY_SCENE_FILES = SCENE_FILES[:4]
REFERENCE_POLICY = ROOT / "production" / "references" / "echoes-forgotten-war" / "README.md"
REVEAL_ORDER = ["Starbreaker", "Redlin", "Atlas", "Arbiter", "Afterlight", "Flux", "Oryon", "Kyn"]
ALLOWED_CHARACTER_FIELDS = {
    "name", "handle", "role", "visualAnchor", "visualStatus", "continuityLocks"
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate_manifest() -> None:
    manifest = load(MANIFEST)
    matches = [entry for entry in manifest if entry.get("id") == "echoes-forgotten-war-s1"]
    assert len(matches) == 1, f"Expected one Echoes manifest entry, found {len(matches)}"
    entry = matches[0]
    assert entry.get("scenesFiles") == [p.name for p in READY_SCENE_FILES], (
        "Echoes production manifest must expose only image-ready compiled issues"
    )
    assert "unitLabel" not in entry, "Manifest must not override Echoes package PAGE contract"
    assert "generationLine" not in entry, "Manifest must not override Echoes package generation contract"


def validate_characters() -> None:
    chars = load(SHOW / "characters.json")
    assert len(chars) >= 15
    for key, entry in chars.items():
        assert isinstance(entry, dict), key
        extra = set(entry) - ALLOWED_CHARACTER_FIELDS
        assert not extra, f"Out-of-scope character fields on {key}: {sorted(extra)}"
        assert entry.get("name") and entry.get("handle") and entry.get("role"), key
        assert entry.get("visualAnchor"), f"Missing visual anchor: {key}"
        assert entry.get("visualStatus"), f"Missing visual status: {key}"
        locks = entry.get("continuityLocks")
        assert isinstance(locks, list) and locks, f"Missing continuity locks: {key}"
    assert chars["EFW_Mero"]["role"].startswith("Human")
    assert chars["EFW_Redlin"]["name"] == "Redlin"


def validate_scenes() -> None:
    all_ids = []
    chars = load(SHOW / "characters.json")
    regions = load(SHOW / "regions.json")
    for issue, path in enumerate(SCENE_FILES, start=1):
        scenes = load(path)
        assert isinstance(scenes, list), path.name
        assert len(scenes) == 12, f"{path.name}: expected 12 source/recipe units, found {len(scenes)}"
        expected = [f"EFW_S1E{issue:02d}_S{i:02d}" for i in range(1, 13)]
        ids = [scene.get("id") for scene in scenes]
        assert ids == expected, f"{path.name}: scene IDs/order changed"
        all_ids.extend(ids)
        for index, scene in enumerate(scenes):
            assert scene.get("summary"), scene.get("id")
            for char_id in scene.get("characters", []):
                assert char_id in chars, f"Missing character {char_id}: {scene['id']}"
            if scene.get("region"):
                assert scene["region"] in regions, f"Missing region {scene['region']}: {scene['id']}"
            if issue >= 2:
                assert scene.get("settingText"), f"Missing settingText: {scene['id']}"
                assert isinstance(scene.get("dialogueInline"), list), f"Missing inline dialogue: {scene['id']}"
                assert isinstance(scene.get("directionInline"), list), f"Missing inline direction: {scene['id']}"
                for line in scene["dialogueInline"]:
                    assert line.get("handle") and line.get("text"), f"Bad dialogue: {scene['id']}"
            if issue <= 4:
                plan = scene.get("panelPlan")
                assert isinstance(plan, list) and len(plan) >= 4, f"Missing page plan: {scene['id']}"
            if issue in (2, 3, 4) and index > 0:
                assert scene.get("continuityFrom") == scenes[index - 1]["id"], f"Broken Issue {issue} continuity: {scene['id']}"
    assert len(all_ids) == 96 and len(set(all_ids)) == 96

    e04 = load(SCENE_FILES[3])
    for scene in e04[1:10]:
        assert "EFW_Theo" not in scene.get("characters", []), f"Ancient Theo revealed early: {scene['id']}"
        assert "EFW_Rae" not in scene.get("characters", []), f"Ancient Rae revealed early: {scene['id']}"
    assert "EFW_Theo" in e04[11]["characters"]
    assert "EFW_Rae" in e04[11]["characters"]

    e05 = {s["id"]: s for s in load(SCENE_FILES[4])}
    assert "EFW_Theo" in e05["EFW_S1E05_S02"]["characters"]
    assert "EFW_Rae" in e05["EFW_S1E05_S04"]["characters"]


def validate_issue1_references() -> None:
    scenes = load(SCENE_FILES[0])
    dialogue = load(SHOW / "dialogue.json")
    direction = load(SHOW / "direction.json")
    settings = load(SHOW / "settings.json")
    regions = load(SHOW / "regions.json")
    for scene in scenes:
        for dialog_id in scene.get("dialog", []):
            assert dialog_id in dialogue, f"Missing dialogue {dialog_id}"
        for direction_id in scene.get("direction", []):
            assert direction_id in direction, f"Missing direction {direction_id}"
        if scene.get("setting"):
            assert scene["setting"] in settings, f"Missing setting {scene['setting']}"
        if scene.get("region"):
            assert scene["region"] in regions, f"Missing region {scene['region']}"


def validate_architecture() -> None:
    architecture = load(SHOW / "season_architecture_v2.json")
    order = [entry.get("newChampion") for entry in architecture.get("revealOrder", [])]
    assert order == REVEAL_ORDER, order

    reset = load(SHOW / "identity_reset.json")
    assert reset.get("status") == "locked"
    assert "Issue 4" in reset.get("midpointReveal", "")

    spine = load(SHOW / "comic_page_spine_v1.json")
    issues = spine.get("issues", [])
    assert len(issues) == 8
    for issue_number, issue in enumerate(issues, start=1):
        assert issue.get("issue") == issue_number
        pages = issue.get("pages", [])
        assert len(pages) == 22, f"Issue {issue_number}: expected 22 development beats"
        assert [p.get("page") for p in pages] == list(range(1, 23))


def validate_current_production_contract() -> None:
    assembler = load(SHOW / "assembler.json")
    assert assembler.get("unitLabel") == "PAGE"
    assert assembler.get("requirePanelPlan") is True
    assert assembler.get("requireVisualAnchors") is True
    generation_line = assembler.get("generationLine", "")
    assert "One assembled RexPrompt recipe equals one page only" in generation_line
    assert "Render only the selected recipe" in generation_line
    assert "page header" in generation_line

    status = load(SHOW / "development_status.json")
    assert status.get("productionMode") == "one assembled RexPrompt recipe equals one finished portrait comic page"
    assert "dynamically" in status.get("frontierRule", "")
    assert "22-beat-per-issue development map" in status.get("developmentGranularity", "")
    issues = status.get("issues", {})
    for issue in (1, 2, 3, 4):
        entry = issues.get(str(issue), {})
        assert entry.get("status") == "compiled for sequential page production", issue
        assert entry.get("recipeFile") == f"scenes_e{issue:02d}.json", issue
        assert entry.get("pageCount") == 12, issue
        assert entry.get("panelPlan") is True, issue
    for issue in (5, 6, 7, 8):
        entry = issues.get(str(issue), {})
        assert entry.get("status") == "normalized source material; not compiled for image production", issue
        assert entry.get("recipeFile") == f"scenes_e{issue:02d}.json", issue
        assert entry.get("pageCount") == 12, issue
        assert entry.get("panelPlan") is False, issue

    assert REFERENCE_POLICY.exists(), "Missing Echoes production visual-reference authority policy"


def main() -> None:
    validate_manifest()
    validate_characters()
    validate_scenes()
    validate_issue1_references()
    validate_architecture()
    validate_current_production_contract()
    print("Echoes validation passed: 8 normalized source issues; Issues 1-4 exposed as 12 PAGE recipes each; Issues 5-8 blocked from image production until compiled.")


if __name__ == "__main__":
    main()
