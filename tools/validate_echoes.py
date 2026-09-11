#!/usr/bin/env python3
"""Validate current Echoes of a Forgotten War RexPrompt production structure.

Developmental/editorial reasoning may remain in writing-only fields and architecture files.
Assembler-visible image recipes must stay concrete: drawable panel staging, visual continuity,
exact lettering and character/world anchors rather than explanations of why the writing works.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data" / "shows" / "echoes-forgotten-war-s1"
MANIFEST = ROOT / "data" / "shows.json"
SCENE_FILES = [SHOW / f"scenes_e{i:02d}.json" for i in range(1, 9)]
ENHANCE_FILES = {issue: SHOW / f"enhance_e{issue:02d}.json" for issue in (6, 7, 8)}
REFERENCE_POLICY = ROOT / "production" / "references" / "echoes-forgotten-war" / "README.md"
REFERENCE_PACK = ROOT / "production" / "references" / "echoes-forgotten-war" / "visual-reference-pack.json"
REVEAL_ORDER = ["Starbreaker", "Redlin", "Atlas", "Arbiter", "Afterlight", "Flux", "Oryon", "Kyn"]
ALLOWED_CHARACTER_FIELDS = {
    "name", "handle", "role", "visualAnchor", "visualStatus", "continuityLocks"
}
ALLOWED_OVERLAY_FIELDS = {"id", "panelPlan", "directionInline", "continuityFrom"}

# Narrow chef-layer guard. This catches editorial/thematic explanation, not ordinary visual
# words. Add a pattern only when it reliably denotes writing analysis rather than something
# an image model can draw.
CHEF_REASONING_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bthe reader\b",
        r"\bthe page's\b",
        r"\bthe issue\b",
        r"\bthe story\b",
        r"\bthe point\b",
        r"\bthe idea\b",
        r"\bthe revelation\b",
        r"\bthe conflict is\b",
        r"\bthe disagreement is\b",
        r"\bthe problem belongs\b",
        r"\bthe uncertainty is\b",
        r"\bthe emotional hinge\b",
        r"\bthematic rhyme\b",
        r"\bproving\b",
        r"\bproof is\b",
        r"\bcreating dramatic irony\b",
        r"\bmore important than\b",
        r"\bmatters because\b",
        r"\bshould make\b",
        r"\bshould feel\b",
        r"\bthe accusation\b",
        r"\bthe shock comes\b",
        r"\bunderstanding that\b",
        r"\brealizing that\b",
        r"\brecognizing what\b",
        r"\bregisters? that\b",
        r"\breads as\b",
        r"\bmeans it literally\b",
        r"\brather than philosophical\b",
        r"\brather than rhetorical\b",
        r"\brather than supernatural\b",
        r"\brather than prophecy\b",
        r"\brather than a technical\b",
        r"\brather than on\b",
        r"\bnot a technical\b",
        r"\bnot a system\b",
        r"\bnot physical combat\b",
        r"\bnot moral theater\b",
        r"\bnot the invention\b",
        r"\bnot mechanism\b",
        r"\bthe crisis has\b",
        r"\bthe answer is\b",
        r"\bthe implication\b",
        r"\bthe line lands\b",
    )
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def expected_issue_ids(issue: int) -> list[str]:
    return [f"EFW_S1E{issue:02d}_S{i:02d}" for i in range(1, 13)]


def validate_manifest() -> None:
    manifest = load(MANIFEST)
    matches = [entry for entry in manifest if entry.get("id") == "echoes-forgotten-war-s1"]
    assert len(matches) == 1, f"Expected one Echoes manifest entry, found {len(matches)}"
    entry = matches[0]
    assert entry.get("scenesFiles") == [p.name for p in SCENE_FILES], (
        "Echoes production manifest must expose Issues 1-8 in source order"
    )
    assert entry.get("sceneOverlays") == [
        {"file": "enhance_e06.json", "mergeById": True},
        {"file": "enhance_e07.json", "mergeById": True},
        {"file": "enhance_e08.json", "mergeById": True},
    ], "Echoes enhancement overlays are missing, reordered, or malformed"
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
    all_ids: list[str] = []
    chars = load(SHOW / "characters.json")
    regions = load(SHOW / "regions.json")
    direction = load(SHOW / "direction.json")

    for issue, path in enumerate(SCENE_FILES, start=1):
        scenes = load(path)
        assert isinstance(scenes, list), path.name
        assert len(scenes) == 12, f"{path.name}: expected 12 source/recipe units, found {len(scenes)}"
        expected = expected_issue_ids(issue)
        ids = [scene.get("id") for scene in scenes]
        assert ids == expected, f"{path.name}: scene IDs/order changed"
        all_ids.extend(ids)

        for index, scene in enumerate(scenes):
            scene_id = scene.get("id")
            assert scene.get("summary"), scene_id
            for char_id in scene.get("characters", []):
                assert char_id in chars, f"Missing character {char_id}: {scene_id}"
            if scene.get("region"):
                assert scene["region"] in regions, f"Missing region {scene['region']}: {scene_id}"

            # Writing/development notes are deliberately preserved but hidden from assembleScene().
            assert "direction" not in scene, f"Chef-visible Issue 1 direction returned: {scene_id}"
            assert "directionInline" not in scene, f"Chef-visible source direction returned: {scene_id}"
            if issue == 1:
                writing_direction = scene.get("writingDirection", [])
                assert isinstance(writing_direction, list), f"Bad writingDirection: {scene_id}"
                for direction_id in writing_direction:
                    assert direction_id in direction, f"Unknown writing direction {direction_id}: {scene_id}"
            else:
                assert scene.get("settingText"), f"Missing settingText: {scene_id}"
                dialogue = scene.get("dialogueInline")
                assert isinstance(dialogue, list), f"Missing inline dialogue: {scene_id}"
                for line in dialogue:
                    assert line.get("handle") and line.get("text"), f"Bad dialogue: {scene_id}"
                writing_notes = scene.get("writingNotes", [])
                assert isinstance(writing_notes, list), f"Bad writingNotes: {scene_id}"
                for note in writing_notes:
                    assert isinstance(note, dict) and isinstance(note.get("text"), str), f"Bad writing note: {scene_id}"

            if issue <= 5:
                plan = scene.get("panelPlan")
                assert isinstance(plan, list) and len(plan) >= 4, f"Missing source page plan: {scene_id}"
                for panel in plan:
                    assert isinstance(panel, dict) and panel.get("text"), f"Bad source panel: {scene_id}"

            if issue in (2, 3, 4, 5) and index > 0:
                assert scene.get("continuityFrom") == scenes[index - 1]["id"], (
                    f"Broken Issue {issue} continuity: {scene_id}"
                )

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


def validate_enhancement_overlays() -> None:
    for issue, overlay_path in ENHANCE_FILES.items():
        source = load(SCENE_FILES[issue - 1])
        source_by_id = {scene["id"]: scene for scene in source}
        overlay = load(overlay_path)
        assert isinstance(overlay, list), overlay_path.name
        assert len(overlay) == 12, f"{overlay_path.name}: expected 12 overlay records"
        ids = [patch.get("id") for patch in overlay]
        assert ids == expected_issue_ids(issue), f"{overlay_path.name}: overlay IDs/order changed"
        assert len(set(ids)) == 12, f"{overlay_path.name}: duplicate IDs"

        for index, patch in enumerate(overlay):
            scene_id = patch["id"]
            extra = set(patch) - ALLOWED_OVERLAY_FIELDS
            assert not extra, f"{overlay_path.name}:{scene_id}: unsafe overlay fields {sorted(extra)}"
            plan = patch.get("panelPlan")
            assert isinstance(plan, list) and len(plan) >= 4, f"Missing overlay page plan: {scene_id}"
            for panel in plan:
                assert isinstance(panel, dict) and panel.get("text"), f"Bad panel plan: {scene_id}"
            if "directionInline" in patch:
                visual_direction = patch["directionInline"]
                assert isinstance(visual_direction, list) and visual_direction, f"Bad overlay direction: {scene_id}"
                for block in visual_direction:
                    assert isinstance(block, dict) and block.get("text"), f"Bad overlay direction: {scene_id}"
            if "continuityFrom" in patch:
                assert index > 0, f"First page cannot continue from prior page: {scene_id}"
                assert patch["continuityFrom"] == ids[index - 1], f"Bad overlay continuity: {scene_id}"

            original = source_by_id[scene_id]
            merged = {**original, **patch}
            assert merged.get("summary") == original.get("summary"), f"Overlay changed summary: {scene_id}"
            assert merged.get("characters") == original.get("characters"), f"Overlay changed cast: {scene_id}"
            assert merged.get("dialogueInline") == original.get("dialogueInline"), f"Overlay changed dialogue: {scene_id}"
            assert merged.get("settingText") == original.get("settingText"), f"Overlay changed setting: {scene_id}"
            assert isinstance(merged.get("panelPlan"), list) and len(merged["panelPlan"]) >= 4


def validate_issue1_references() -> None:
    scenes = load(SCENE_FILES[0])
    dialogue = load(SHOW / "dialogue.json")
    direction = load(SHOW / "direction.json")
    settings = load(SHOW / "settings.json")
    regions = load(SHOW / "regions.json")
    for scene in scenes:
        for dialog_id in scene.get("dialog", []):
            assert dialog_id in dialogue, f"Missing dialogue {dialog_id}"
        for direction_id in scene.get("writingDirection", []):
            assert direction_id in direction, f"Missing writing direction {direction_id}"
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


def validate_visual_references() -> None:
    assert REFERENCE_POLICY.exists(), "Missing Echoes production visual-reference authority policy"
    assert REFERENCE_PACK.exists(), "Missing Echoes visual-reference pack"
    pack = load(REFERENCE_PACK)
    assert pack.get("status") == "active", "Echoes visual-reference pack is not active"
    refs = pack.get("references")
    assert isinstance(refs, list) and len(refs) >= 13, "Echoes visual-reference pack is incomplete"
    for ref in refs:
        image = ref.get("image")
        assert image, f"Reference missing image path: {ref.get('id')}"
        assert (ROOT / image).exists(), f"Reference image missing: {image}"
        assert ref.get("type") in {"approved-current-production-reference", "approved-corrective-reference"}, (
            f"Reference is not explicitly approved: {ref.get('id')}"
        )


def chef_layer_strings() -> list[tuple[str, str]]:
    """Return only strings actually emitted to the image recipe by the assembler."""
    strings: list[tuple[str, str]] = []
    assembler = load(SHOW / "assembler.json")
    strings.append(("assembler:generationLine", assembler.get("generationLine", "")))

    # Summaries carry concise page action and intentionally remain upstream of the visual plan.
    # Developmental writingDirection/writingNotes and direction.json are intentionally excluded:
    # assembleScene() does not emit those fields.
    for issue, path in enumerate(SCENE_FILES, start=1):
        if issue > 5:
            continue
        for scene in load(path):
            scene_id = scene.get("id", path.name)
            for panel_index, panel in enumerate(scene.get("panelPlan", []), start=1):
                if isinstance(panel, dict) and isinstance(panel.get("text"), str):
                    strings.append((f"{scene_id}:panel:{panel_index}", panel["text"]))

    for issue, path in ENHANCE_FILES.items():
        for patch in load(path):
            scene_id = patch.get("id", path.name)
            for panel_index, panel in enumerate(patch.get("panelPlan", []), start=1):
                if isinstance(panel, dict) and isinstance(panel.get("text"), str):
                    strings.append((f"{scene_id}:overlay-panel:{panel_index}", panel["text"]))
            for direction_index, block in enumerate(patch.get("directionInline", []), start=1):
                if isinstance(block, dict) and isinstance(block.get("text"), str):
                    strings.append((f"{scene_id}:overlay-direction:{direction_index}", block["text"]))
    return strings


def validate_chef_layer_separation() -> None:
    candidates: list[tuple[str, str]] = []
    for label, text in chef_layer_strings():
        if any(pattern.search(text) for pattern in CHEF_REASONING_PATTERNS):
            candidates.append((label, text))
    detail = "\n".join(f"{label}: {text}" for label, text in candidates[:30])
    assert not candidates, (
        f"Echoes chef layer contains {len(candidates)} writing/editorial reasoning strings. "
        f"Rewrite them as directly drawable staging:\n{detail}"
    )


def validate_current_production_contract() -> None:
    assembler = load(SHOW / "assembler.json")
    assert assembler.get("unitLabel") == "PAGE"
    assert assembler.get("requirePanelPlan") is True
    assert assembler.get("requireVisualAnchors") is True
    generation_line = assembler.get("generationLine", "")
    for required in (
        "One assembled RexPrompt recipe equals one page only",
        "Render only the selected recipe",
        "Painterly prestige cosmic science-fiction sequential art",
        "Stage emotion through faces, hands, posture, distance, eyelines, touch, carried objects",
        "match camera position, body placement and architectural geometry precisely",
        "show interfaces or diagrams only when the selected page explicitly scripts one",
        "Follow the PANEL PLAN as page architecture",
    ):
        assert required in generation_line, f"Echoes generation contract missing: {required}"

    status = load(SHOW / "development_status.json")
    assert status.get("productionMode") == "one assembled RexPrompt recipe equals one finished portrait comic page"
    assert "dynamically" in status.get("frontierRule", "")
    granularity = status.get("developmentGranularity", "")
    assert "Issues 1-8" in granularity
    assert "merge-by-ID enhancement overlays" in granularity
    visual_state = status.get("visualReferenceState", "")
    assert "visual-reference-pack.json" in visual_state
    assert "approved current-production" in visual_state
    assert "EFW_S1E01_S01" in visual_state

    issues = status.get("issues", {})
    for issue in (1, 2, 3, 4, 5):
        entry = issues.get(str(issue), {})
        assert entry.get("status") == "compiled for sequential page production", issue
        assert entry.get("recipeFile") == f"scenes_e{issue:02d}.json", issue
        assert entry.get("pageCount") == 12, issue
        assert entry.get("panelPlan") is True, issue
    for issue in (6, 7, 8):
        entry = issues.get(str(issue), {})
        assert entry.get("status") == f"compiled for sequential page production via enhance_e{issue:02d}.json overlay", issue
        assert entry.get("recipeFile") == f"scenes_e{issue:02d}.json", issue
        assert entry.get("pageCount") == 12, issue
        assert entry.get("panelPlan") is True, issue


def main() -> None:
    validate_manifest()
    validate_characters()
    validate_scenes()
    validate_enhancement_overlays()
    validate_issue1_references()
    validate_architecture()
    validate_visual_references()
    validate_current_production_contract()
    validate_chef_layer_separation()
    print(
        "Echoes validation passed: 96 PAGE recipes preserve story/cast/dialogue/continuity; "
        "developmental reasoning is kept in writing-only fields; chef-visible direction is concrete visual staging."
    )


if __name__ == "__main__":
    main()
