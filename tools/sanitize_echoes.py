#!/usr/bin/env python3
"""Non-destructive structural sanitizer check for Echoes of a Forgotten War.

Echoes is already normalized into direct per-issue PAGE recipe files. This tool
must not rewrite authored story or editorial copy. It verifies the package shape
that sanitation is expected to preserve and exits without modifying files.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data" / "shows" / "echoes-forgotten-war-s1"
MANIFEST = ROOT / "data" / "shows.json"
SCENE_FILES = [SHOW / f"scenes_e{i:02d}.json" for i in range(1, 9)]
STORY_COUNTS = {1: 17, 2: 16, 3: 15, 4: 16, 5: 16, 6: 15, 7: 16, 8: 18}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def expected_ids(issue: int) -> list[str]:
    story = [f"EFW_S1E{issue:02d}_S{i:02d}" for i in range(1, STORY_COUNTS[issue] + 1)]
    return [f"EFW_S1E{issue:02d}_EDITOR_OPEN", *story, f"EFW_S1E{issue:02d}_EDITOR_CLOSE"]


def main() -> None:
    manifest = load(MANIFEST)
    entries = [entry for entry in manifest if entry.get("id") == "echoes-forgotten-war-s1"]
    if len(entries) != 1:
        raise RuntimeError(f"Expected one Echoes manifest entry, found {len(entries)}")
    entry = entries[0]
    expected_files = [p.name for p in SCENE_FILES]
    if entry.get("scenesFiles") != expected_files:
        raise RuntimeError("Echoes manifest issue files are missing or reordered")
    if entry.get("sceneOverlays"):
        raise RuntimeError("Echoes direct production package must not restore retired enhancement overlays")

    total = 0
    for issue, path in enumerate(SCENE_FILES, start=1):
        pages = load(path)
        ids = [page.get("id") for page in pages]
        expected = expected_ids(issue)
        if ids != expected:
            raise RuntimeError(f"{path.name}: page order/IDs changed")
        total += len(pages)

        for page in (pages[0], pages[-1]):
            if not page.get("summary") or not page.get("settingText"):
                raise RuntimeError(f"Incomplete editorial bookend: {page.get('id')}")
            plan = page.get("panelPlan")
            if not isinstance(plan, list) or not plan:
                raise RuntimeError(f"Missing editorial page architecture: {page.get('id')}")
            lines = page.get("dialogueInline")
            if not isinstance(lines, list) or not lines:
                raise RuntimeError(f"Missing editorial copy: {page.get('id')}")
            if any(line.get("speaker") != "CAPTION" or not line.get("text") for line in lines):
                raise RuntimeError(f"Malformed editorial lettering: {page.get('id')}")
            if page.get("continuityFrom"):
                raise RuntimeError(f"Editorial bookend must not inherit story continuity: {page.get('id')}")

    if total != 145:
        raise RuntimeError(f"Expected 145 Echoes production pages, found {total}")

    print("Echoes sanitizer passed non-destructively: 129 story pages + 16 editorial bookends = 145 PAGE recipes.")


if __name__ == "__main__":
    main()
