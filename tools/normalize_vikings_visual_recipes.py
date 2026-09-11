#!/usr/bin/env python3
"""Normalize active Vikings 2026 production recipes for visual execution.

This is a narrow production-data pass. It preserves page IDs, panel count/order,
dialogue, and story content. It adds explicit per-panel location to active
unreleased Vikings Issues 2-5 and applies the approved VIK_S1I02_P01 visual
staging correction. Released Issue 1 is intentionally excluded.
"""

from __future__ import annotations

import base64
import copy
import gzip
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOWS_PATH = ROOT / "data" / "shows.json"
VIKINGS_BASE = ROOT / "data" / "shows" / "vikings-2026-s1"

LOCATION_WORDS = {
    "apartment", "studio", "hallway", "hall", "stairwell", "landing", "street",
    "sidewalk", "stoop", "bodega", "bank", "station", "platform", "train",
    "subway", "library", "park", "laundromat", "courtroom", "court", "dti",
    "office", "kitchen", "bathroom", "roof", "lobby", "counter", "desk",
    "terminal", "room", "building", "threshold", "elevator", "bus", "avenue",
    "corner", "checkout", "entrance", "exit", "interior", "exterior",
}


def load_overlay(path: Path, encoding: str | None):
    if encoding == "gzip-base64":
        encoded = path.read_text(encoding="utf-8")
        payload = gzip.decompress(base64.b64decode("".join(encoded.split())))
        return json.loads(payload.decode("utf-8"))
    if encoding:
        raise ValueError(f"Unsupported encoding: {encoding}")
    return json.loads(path.read_text(encoding="utf-8"))


def save_overlay(path: Path, encoding: str | None, data) -> None:
    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    if encoding == "gzip-base64":
        packed = gzip.compress(text.encode("utf-8"), mtime=0)
        path.write_text(base64.b64encode(packed).decode("ascii") + "\n", encoding="utf-8")
        return
    if encoding:
        raise ValueError(f"Unsupported encoding: {encoding}")
    path.write_text(text, encoding="utf-8")


def scenes_from(raw):
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict) and isinstance(raw.get("pages"), list):
        return raw["pages"]
    if isinstance(raw, dict):
        return [dict({"id": key}, **value) for key, value in raw.items()]
    raise TypeError(type(raw))


def page_setting(scene: dict) -> str:
    text = str(scene.get("settingText") or "").strip()
    if text:
        return text
    setting = str(scene.get("setting") or "").strip()
    return setting


def candidate_from_action(action: str) -> str | None:
    action = " ".join(str(action or "").split())
    if not action:
        return None

    # Many current recipes already begin with a compact location phrase followed
    # by a colon. Promote that phrase into an explicit location field.
    if ":" in action:
        prefix = action.split(":", 1)[0].strip()
        words = set(re.findall(r"[a-z]+", prefix.lower()))
        if len(prefix) <= 120 and words & LOCATION_WORDS:
            return prefix

    # Preserve explicit location-led blocking when it already exists in prose.
    m = re.match(
        r"^(Back at|Inside|Outside|At|In|On|Near|Across from|By|From)\s+([^.;]{2,100})",
        action,
        flags=re.IGNORECASE,
    )
    if m:
        phrase = (m.group(1) + " " + m.group(2)).strip()
        words = set(re.findall(r"[a-z]+", phrase.lower()))
        if words & LOCATION_WORDS:
            return phrase

    return None


def concise_default_location(setting: str) -> str:
    setting = " ".join(setting.split())
    if not setting:
        return "same location as previous panel"
    # The page setting remains an environment family. Keep it intact rather than
    # guessing a narrower place that the stored recipe does not establish.
    return setting


def normalize_panel(panel: dict, default_location: str, previous_location: str | None) -> tuple[dict, str]:
    panel = copy.deepcopy(panel)
    explicit = str(panel.get("location") or "").strip()
    inferred = explicit or candidate_from_action(panel.get("action", ""))
    location = inferred or previous_location or concise_default_location(default_location)

    # Put the visually operative fields first so JSON rendering in the assembler
    # reads like a drawing instruction rather than arbitrary metadata.
    normalized: dict = {}
    for key in ("panel",):
        if key in panel:
            normalized[key] = panel[key]
    normalized["location"] = location
    for key in ("shotType", "action", "dialogueIndices"):
        if key in panel:
            normalized[key] = panel[key]
    for key, value in panel.items():
        if key not in normalized and key != "location":
            normalized[key] = value
    return normalized, location


def patch_landfall_page_one(scene: dict) -> None:
    scene["summary"] = (
        "Carrie reaches apartment 5B with the Viking household; Bjorn fixates on the small door and the key Carrie still controls while Gunnar quietly studies the building's routes."
    )
    scene["settingText"] = (
        "Bushwick fifth-floor walk-up arrival sequence: stairwell landing -> hallway outside apartment 5B -> threshold at 5B. "
        "Worn but ordinary residential interior with scuffed painted walls, old linoleum, radiator pipes, apartment doors, and modest daylight; no exaggerated decay."
    )
    scene["panelPlan"] = [
        {
            "panel": 1,
            "location": "fifth-floor stairwell landing opening into the hallway",
            "shotType": "wide",
            "action": "Carrie reaches the fifth floor first, slightly winded, carrying the thick DTI intake packet. Bjorn, Gunnar, Astrid and the two male Kin climb the last stairs behind her as one readable household group. Apartment 5B is visible farther down the narrow hallway. The building is worn, ordinary and cramped rather than threatening."
        },
        {
            "panel": 2,
            "location": "hallway directly outside apartment 5B",
            "shotType": "medium",
            "action": "Carrie stops at the door marked 5B and produces the small temporary brass key. She is tired but faintly satisfied to have gotten them here. Bjorn and Gunnar have just arrived behind her; Astrid and the two male Kin remain together farther back in the hall.",
            "dialogueIndices": [0]
        },
        {
            "panel": 3,
            "location": "hallway directly outside apartment 5B",
            "shotType": "two-shot",
            "action": "Bjorn studies the modest apartment door, the narrow hallway around it, then Carrie. His face stays controlled and serious: he is trying to reconcile Carrie's claim that she fought for this placement with how small and unimpressive it appears.",
            "dialogueIndices": [1, 2]
        },
        {
            "panel": 4,
            "location": "same fifth-floor hallway, angled to include the stairwell and roof-access end",
            "shotType": "medium",
            "action": "While Carrie and Bjorn remain focused on apartment 5B, Gunnar turns away from them and quietly studies the building geometry: the stairwell they used, the length of the hall, and the roof-access door at the opposite end. His attention is practical and automatic, not theatrical.",
            "dialogueIndices": [3]
        },
        {
            "panel": 5,
            "location": "threshold of apartment 5B",
            "shotType": "close-up",
            "action": "Carrie inserts the brass key into the lock and begins opening the apartment herself. Bjorn's attention drops to the key in her hand rather than the opening door. Carrie still physically controls the key; Bjorn registers that fact without exaggerated reaction.",
            "dialogueIndices": [4, 5]
        }
    ]


def invariants(scenes: list[dict]):
    return {
        s.get("id"): {
            "panel_count": len(s.get("panelPlan") or []),
            "panel_numbers": [p.get("panel") for p in (s.get("panelPlan") or [])],
            "dialogue": copy.deepcopy(s.get("dialogueInline")),
        }
        for s in scenes
        if s.get("id")
    }


def main() -> None:
    shows = json.loads(SHOWS_PATH.read_text(encoding="utf-8"))
    overlay_specs: dict[Path, str | None] = {}

    for show in shows:
        show_id = str(show.get("id") or "")
        if not show_id.startswith("vikings-2026-s1-") or show_id == "vikings-2026-s1-e01":
            continue
        for overlay in show.get("sceneOverlays") or []:
            rel = overlay.get("file")
            if not rel:
                continue
            path = VIKINGS_BASE / rel
            overlay_specs[path] = overlay.get("encoding")

    if not overlay_specs:
        raise SystemExit("No active unreleased Vikings overlays found")

    changed_pages = 0
    changed_panels = 0
    touched_files = 0

    for path, encoding in sorted(overlay_specs.items()):
        raw = load_overlay(path, encoding)
        scenes = scenes_from(raw)
        before = invariants(scenes)
        file_changed = False

        for scene in scenes:
            sid = str(scene.get("id") or "")
            if not sid.startswith("VIK_"):
                continue

            if sid == "VIK_S1I02_P01":
                original_dialogue = copy.deepcopy(scene.get("dialogueInline"))
                patch_landfall_page_one(scene)
                if scene.get("dialogueInline") != original_dialogue:
                    raise AssertionError("Page 1 dialogue changed")
                file_changed = True

            panels = scene.get("panelPlan")
            if not isinstance(panels, list) or not panels:
                continue

            default_location = page_setting(scene)
            prev = None
            normalized_panels = []
            for panel in panels:
                if not isinstance(panel, dict):
                    normalized_panels.append(panel)
                    continue
                normalized, prev = normalize_panel(panel, default_location, prev)
                if normalized != panel:
                    changed_panels += 1
                    file_changed = True
                normalized_panels.append(normalized)
            if normalized_panels != panels:
                scene["panelPlan"] = normalized_panels
                changed_pages += 1

        after = invariants(scenes)
        if set(before) != set(after):
            raise AssertionError(f"Page ID set changed in {path}")
        for sid, state in before.items():
            if after[sid]["panel_count"] != state["panel_count"]:
                raise AssertionError(f"Panel count changed for {sid}")
            if after[sid]["panel_numbers"] != state["panel_numbers"]:
                raise AssertionError(f"Panel order changed for {sid}")
            if after[sid]["dialogue"] != state["dialogue"]:
                raise AssertionError(f"Dialogue changed for {sid}")

        if file_changed:
            save_overlay(path, encoding, raw)
            touched_files += 1

    print(f"Normalized {changed_panels} panel records across {changed_pages} pages in {touched_files} active overlay files.")


if __name__ == "__main__":
    main()
