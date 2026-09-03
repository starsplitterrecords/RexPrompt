#!/usr/bin/env python3
"""Mechanical integrity checks for the Division Threshold production package.

This protects assembly structure and reference integrity only. It deliberately does
not freeze creative wording or score narrative quality.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "shows" / "division-threshold-s1"


def load(name: str):
    with (BASE / name).open(encoding="utf-8") as fh:
        return json.load(fh)


def normalize_overlay(raw):
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict) and isinstance(raw.get("pages"), list):
        return raw["pages"]
    if isinstance(raw, dict):
        return [{"id": key, **value} for key, value in raw.items()]
    raise AssertionError(f"Unsupported overlay shape: {type(raw).__name__}")


def merge_by_id(pages, incoming):
    updates = {page["id"]: page for page in incoming if page.get("id")}
    merged = []
    seen = set()
    for page in pages:
        patch = updates.get(page["id"])
        if patch:
            merged.append({**page, **patch})
            seen.add(page["id"])
        else:
            merged.append(page)
    for page in incoming:
        if page.get("id") and page["id"] not in seen and not any(existing["id"] == page["id"] for existing in pages):
            merged.append(page)
    return merged


def apply_dialogue(pages, incoming):
    updates = {page["id"]: page for page in incoming if page.get("id")}
    result = []
    for page in pages:
        patch = updates.get(page["id"])
        if not patch:
            result.append(page)
            continue
        dialogue = patch.get("dialogueInline") or patch.get("sceneDialogue")
        result.append({**page, "dialogueInline": dialogue} if isinstance(dialogue, list) else page)
    return result


def main():
    assembler = load("assembler.json")
    characters = load("characters.json")
    settings = load("settings.json")
    regions = load("regions.json")
    factions = load("factions.json")

    pages = []
    for filename in assembler["scenesFiles"]:
        pages.extend(load(filename))

    for overlay in assembler.get("sceneOverlays", []):
        incoming = normalize_overlay(load(overlay["file"]))
        pages = merge_by_id(pages, incoming) if overlay.get("mergeById") else pages + incoming

    for overlay in assembler.get("dialogueOverlays", []):
        pages = apply_dialogue(pages, normalize_overlay(load(overlay["file"])))

    ids = [page["id"] for page in pages]
    assert len(ids) == 208, f"Expected 208 assembled pages, found {len(ids)}"
    assert len(ids) == len(set(ids)), "Duplicate assembled page IDs"

    for issue in range(1, 9):
        prefix = f"DT_E{issue:03d}_P"
        issue_pages = [page for page in pages if page["id"].startswith(prefix)]
        assert len(issue_pages) == 26, f"Issue {issue}: expected 26 pages, found {len(issue_pages)}"
        expected = [f"DT_E{issue:03d}_P{page:02d}" for page in range(1, 27)]
        assert [page["id"] for page in issue_pages] == expected, f"Issue {issue}: page order/IDs are not canonical"

    for page in pages:
        pid = page["id"]
        assert page.get("summary"), f"{pid}: missing summary"
        assert len(page.get("panelPlan", [])) >= 1, f"{pid}: missing panel plan"
        assert isinstance(page.get("dialogueInline", []), list), f"{pid}: dialogue must be a list"

        if page.get("setting"):
            assert page["setting"] in settings, f"{pid}: unknown setting {page['setting']}"
        if page.get("region"):
            assert page["region"] in regions, f"{pid}: unknown region {page['region']}"
        for faction_id in page.get("factions", []):
            assert faction_id in factions, f"{pid}: unknown faction {faction_id}"
        for char_id in page.get("characters", []):
            assert char_id in characters, f"{pid}: unknown character {char_id}"

        prior = page.get("continuityFrom")
        if prior:
            assert prior in ids, f"{pid}: continuityFrom references missing page {prior}"

    # Issue 1 was rebuilt after its original draft. These checks prevent fields
    # from the retired page actions from leaking through merge-by-id assembly.
    expected_issue1_locations = {
        "DT_E001_P17": ("DT_OversightOffice", "DT_GovernanceUpperLevels"),
        "DT_E001_P18": ("DT_OrganicSafehouse", "DT_OrganicDistricts"),
        "DT_E001_P19": ("DT_OrganicSafehouse", "DT_OrganicDistricts"),
        "DT_E001_P20": ("DT_AugmentClinic", "DT_Stack"),
        "DT_E001_P21": ("DT_OversightOffice", "DT_GovernanceUpperLevels"),
        "DT_E001_P22": ("DT_DataCore", "DT_GovernanceUpperLevels"),
        "DT_E001_P23": ("DT_OrganicSafehouse", "DT_OrganicDistricts"),
        "DT_E001_P24": ("DT_AugmentClinic", "DT_Stack"),
        "DT_E001_P25": ("DT_OversightOffice", "DT_GovernanceUpperLevels"),
        "DT_E001_P26": ("DT_DataCore", "DT_GovernanceUpperLevels"),
    }
    by_id = {page["id"]: page for page in pages}
    for pid, (setting, region) in expected_issue1_locations.items():
        page = by_id[pid]
        assert page.get("setting") == setting, f"{pid}: stale/wrong setting {page.get('setting')}"
        assert page.get("region") == region, f"{pid}: stale/wrong region {page.get('region')}"

    # Every current Issue 1 page now carries explicit people-category visual
    # context so RexPrompt does not rely on the image model to invent a shared
    # visual language for Baselines, Organics, Augments or Intelligences.
    for page_num in range(1, 27):
        pid = f"DT_E001_P{page_num:02d}"
        assert by_id[pid].get("factions"), f"{pid}: missing Issue 1 visual faction context"

    for faction_id in ("DT_BaselineHumans", "DT_Organosynthetics", "DT_AugmentedHumans", "DT_Intelligences"):
        text = factions[faction_id].get("text", "")
        assert len(text) >= 200, f"{faction_id}: faction visual language is too thin for production"

    retired_issue1_phrases = (
        "white facility",
        "drone frames ambush",
        "suppressant discharges",
        "capability review required",
    )
    for pid in [f"DT_E001_P{n:02d}" for n in range(18, 27)]:
        text = " ".join([
            by_id[pid].get("summary", ""),
            " ".join(map(str, by_id[pid].get("panelPlan", []))),
        ]).lower()
        for phrase in retired_issue1_phrases:
            assert phrase not in text, f"{pid}: retired Issue 1 story residue: {phrase}"

    handles = set()
    for char in characters.values():
        if char.get("handle"):
            handles.add(char["handle"])
        handles.update(char.get("aliases", []))
    for page in pages:
        for line in page.get("dialogueInline", []):
            handle = line.get("handle")
            if handle:
                assert handle in handles, f"{page['id']}: unknown dialogue handle {handle}"

    print("Division Threshold validation passed")
    print("8 issues / 208 pages / canonical Issue 1 locations / visual faction context / valid production references")


if __name__ == "__main__":
    main()
