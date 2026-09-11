#!/usr/bin/env python3
"""Safely normalize and verify the current Echoes RexPrompt production contract.

The earlier Echoes sanitizer was a one-time development migration. The current
package contains approved production identity anchors and assembler-visible page
architecture, so this tool must never strip character anchors, downgrade PAGE
recipes to SCENE units, remove enhancement overlays, or rewrite authored story.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data" / "shows" / "echoes-forgotten-war-s1"
MANIFEST = ROOT / "data" / "shows.json"
SCENE_FILES = [SHOW / f"scenes_e{i:02d}.json" for i in range(1, 9)]
ENHANCE_FILES = {issue: SHOW / f"enhance_e{issue:02d}.json" for issue in (6, 7, 8)}
REFERENCE_PACK = ROOT / "production" / "references" / "echoes-forgotten-war" / "visual-reference-pack.json"

SHOW_ENTRY = {
    "id": "echoes-forgotten-war-s1",
    "name": "Echoes of a Forgotten War — Season 1",
    "basePath": "data/shows/echoes-forgotten-war-s1",
    "scenesFiles": [f"scenes_e{i:02d}.json" for i in range(1, 9)],
    "sceneOverlays": [
        {"file": "enhance_e06.json", "mergeById": True},
        {"file": "enhance_e07.json", "mergeById": True},
        {"file": "enhance_e08.json", "mergeById": True},
    ],
}

ALLOWED_CHARACTER_FIELDS = {
    "name", "handle", "role", "visualAnchor", "visualStatus", "continuityLocks"
}
ALLOWED_OVERLAY_FIELDS = {"id", "panelPlan", "directionInline", "continuityFrom"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def expected_ids(issue: int) -> list[str]:
    return [f"EFW_S1E{issue:02d}_S{i:02d}" for i in range(1, 13)]


def sanitize_manifest() -> bool:
    """Restore the exact assembler registration without touching other shows."""
    data = load(MANIFEST)
    if not isinstance(data, list):
        raise RuntimeError("data/shows.json must be a list")
    matches = [i for i, entry in enumerate(data) if entry.get("id") == SHOW_ENTRY["id"]]
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one Echoes manifest entry, found {len(matches)}")
    index = matches[0]
    if data[index] == SHOW_ENTRY:
        return False
    data[index] = copy.deepcopy(SHOW_ENTRY)
    dump(MANIFEST, data)
    return True


def sanitize_development_status() -> bool:
    """Remove only known stale claims; preserve production maturity and authored policy."""
    path = SHOW / "development_status.json"
    data = load(path)
    current = data.get("visualReferenceState", "")
    stale = "No durable approved Echoes image reference is currently stored in RexPrompt."
    if stale not in current:
        return False
    data["visualReferenceState"] = (
        "Active durable approved Echoes identity references are stored in "
        "production/references/echoes-forgotten-war/visual-reference-pack.json and its characters/ assets. "
        "They are approved current-production identity and pantheon-differentiation references, not released canon "
        "and not page-style authority. No recipe-level approved Echoes comic-page draft is currently stored; "
        "the image-production frontier remains EFW_S1E01_S01 until a page passes approval and is registered under "
        "production/drafts/."
    )
    dump(path, data)
    return True


def verify_characters() -> None:
    chars = load(SHOW / "characters.json")
    if len(chars) < 15:
        raise RuntimeError("Echoes character package is unexpectedly incomplete")
    for key, entry in chars.items():
        if not isinstance(entry, dict):
            raise RuntimeError(f"Bad character record: {key}")
        extra = set(entry) - ALLOWED_CHARACTER_FIELDS
        if extra:
            raise RuntimeError(f"Out-of-scope character fields on {key}: {sorted(extra)}")
        for field in ("name", "handle", "role", "visualAnchor", "visualStatus"):
            if not entry.get(field):
                raise RuntimeError(f"Missing {field}: {key}")
        locks = entry.get("continuityLocks")
        if not isinstance(locks, list) or not locks:
            raise RuntimeError(f"Missing continuity locks: {key}")


def verify_sources_and_overlays() -> None:
    all_ids: list[str] = []
    for issue, path in enumerate(SCENE_FILES, start=1):
        scenes = load(path)
        if not isinstance(scenes, list) or len(scenes) != 12:
            raise RuntimeError(f"{path.name}: expected 12 source recipes")
        ids = [scene.get("id") for scene in scenes]
        if ids != expected_ids(issue):
            raise RuntimeError(f"{path.name}: source recipe IDs/order changed")
        all_ids.extend(ids)
        for scene in scenes:
            if not scene.get("summary") or not scene.get("characters"):
                raise RuntimeError(f"Incomplete source recipe: {scene.get('id')}")
            if issue >= 2 and not isinstance(scene.get("dialogueInline"), list):
                raise RuntimeError(f"Missing inline dialogue: {scene.get('id')}")
            if issue <= 5:
                plan = scene.get("panelPlan")
                if not isinstance(plan, list) or len(plan) < 4:
                    raise RuntimeError(f"Missing source page architecture: {scene.get('id')}")
    if len(all_ids) != 96 or len(set(all_ids)) != 96:
        raise RuntimeError("Echoes source recipe count or IDs are malformed")

    for issue, path in ENHANCE_FILES.items():
        source = {scene["id"]: scene for scene in load(SCENE_FILES[issue - 1])}
        overlay = load(path)
        if not isinstance(overlay, list) or len(overlay) != 12:
            raise RuntimeError(f"{path.name}: expected 12 overlay recipes")
        ids = [patch.get("id") for patch in overlay]
        if ids != expected_ids(issue):
            raise RuntimeError(f"{path.name}: overlay IDs/order changed")
        for patch in overlay:
            scene_id = patch["id"]
            extra = set(patch) - ALLOWED_OVERLAY_FIELDS
            if extra:
                raise RuntimeError(f"{path.name}:{scene_id}: overlay may not replace story fields {sorted(extra)}")
            plan = patch.get("panelPlan")
            if not isinstance(plan, list) or len(plan) < 4:
                raise RuntimeError(f"Missing overlay page architecture: {scene_id}")
            merged = {**source[scene_id], **patch}
            if merged.get("summary") != source[scene_id].get("summary"):
                raise RuntimeError(f"Overlay changed summary: {scene_id}")
            if merged.get("characters") != source[scene_id].get("characters"):
                raise RuntimeError(f"Overlay changed cast: {scene_id}")
            if merged.get("dialogueInline") != source[scene_id].get("dialogueInline"):
                raise RuntimeError(f"Overlay changed dialogue: {scene_id}")


def verify_manifest() -> None:
    data = load(MANIFEST)
    matches = [entry for entry in data if entry.get("id") == SHOW_ENTRY["id"]]
    if matches != [SHOW_ENTRY]:
        raise RuntimeError("Echoes manifest registration does not match current PAGE/overlay contract")


def verify_reference_authority() -> None:
    pack = load(REFERENCE_PACK)
    if pack.get("status") != "active":
        raise RuntimeError("Echoes visual-reference pack is not active")
    refs = pack.get("references")
    if not isinstance(refs, list) or len(refs) < 13:
        raise RuntimeError("Echoes visual-reference pack is incomplete")
    for ref in refs:
        image = ref.get("image")
        if not image or not (ROOT / image).exists():
            raise RuntimeError(f"Missing approved Echoes reference asset: {image or ref.get('id')}")


def verify_status() -> None:
    status = load(SHOW / "development_status.json")
    if "visual-reference-pack.json" not in status.get("visualReferenceState", ""):
        raise RuntimeError("Echoes development status does not acknowledge active durable references")
    issues = status.get("issues", {})
    for issue in range(1, 9):
        entry = issues.get(str(issue), {})
        if entry.get("panelPlan") is not True:
            raise RuntimeError(f"Issue {issue} is not marked page-compiled")
    if "merge-by-ID enhancement overlays" not in status.get("developmentGranularity", ""):
        raise RuntimeError("Echoes development status does not describe enhancement overlay architecture")


def verify_clean() -> None:
    verify_characters()
    verify_sources_and_overlays()
    verify_manifest()
    verify_reference_authority()
    verify_status()


def main() -> None:
    manifest_changed = sanitize_manifest()
    status_changed = sanitize_development_status()
    verify_clean()
    print("Echoes sanitizer passed without rewriting authored story or production identity.")
    print(f"Manifest normalized: {manifest_changed}")
    print(f"Reference-status claim normalized: {status_changed}")


if __name__ == "__main__":
    main()
