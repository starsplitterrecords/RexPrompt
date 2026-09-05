#!/usr/bin/env python3
"""Mechanical integrity checks for the Division Threshold production package.

This protects assembly structure and production-reference integrity only. It deliberately
does not freeze creative wording or score narrative quality.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "shows" / "division-threshold-s1"
NORMALIZATION_REFERENCE = ROOT / "production" / "references" / "division-threshold" / "img-production-normalization.json"


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

    assert NORMALIZATION_REFERENCE.exists(), "Missing Division Threshold IMG production normalization reference"
    with NORMALIZATION_REFERENCE.open(encoding="utf-8") as fh:
        normalization = json.load(fh)
    assert normalization.get("schemaVersion") == 1, "Unexpected Division Threshold normalization schema version"
    assert normalization.get("seriesId") == "division-threshold", "Normalization reference has wrong seriesId"
    assert normalization.get("status") == "normalized-img-production-reference", "Normalization reference is not active"
    assert normalization.get("releaseState") == "unreleased-no-released-visual-canon", "Division Threshold release-state contract changed unexpectedly"
    assert normalization.get("frontierPolicy", {}).get("mode") == "derived-not-stored", "Division Threshold production frontier must remain derived"
    assert normalization.get("referenceScopes", {}).get("currentProduction", {}).get("manifest") == "production/drafts/manifest.json", "Approved-draft authority must remain the production draft manifest"
    assert len(normalization.get("sessionStartGate", [])) >= 7, "Division Threshold session-start gate is incomplete"
    assert len(normalization.get("perPageGate", [])) >= 9, "Division Threshold per-page visual gate is incomplete"
    assert normalization.get("storyPageOutputRule"), "Division Threshold story-page output rule is missing"

    expected_visual_overlays = [f"issue_{issue:02d}_visual_reconciliation.json" for issue in range(1, 9)]
    active_scene_overlays = [overlay.get("file") for overlay in assembler.get("sceneOverlays", [])]
    for filename in expected_visual_overlays:
        assert filename in active_scene_overlays, f"Missing normalized visual overlay: {filename}"

    expected_reference_overlays = [f"data/shows/division-threshold-s1/{filename}" for filename in expected_visual_overlays]
    assert normalization.get("textualProductionBaseline", {}).get("visualReconciliation") == expected_reference_overlays, "Normalization reference and assembler visual overlays disagree"

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

    by_id = {page["id"]: page for page in pages}

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
    for pid, (setting, region) in expected_issue1_locations.items():
        page = by_id[pid]
        assert page.get("setting") == setting, f"{pid}: stale/wrong setting {page.get('setting')}"
        assert page.get("region") == region, f"{pid}: stale/wrong region {page.get('region')}"

    # Every issue must carry explicit people-category visual context. Issues 2-8
    # must additionally carry explicit setting/region context on every page.
    # Split/montage pages use inline production text when a single shelf setting
    # would falsely imply one physical location.
    for issue in range(1, 9):
        for page_num in range(1, 27):
            pid = f"DT_E{issue:03d}_P{page_num:02d}"
            assert by_id[pid].get("factions"), f"{pid}: missing visual faction context"

    for issue in range(2, 9):
        for page_num in range(1, 27):
            pid = f"DT_E{issue:03d}_P{page_num:02d}"
            page = by_id[pid]
            assert page.get("setting") or page.get("settingText"), f"{pid}: missing normalized setting context"
            assert page.get("region") or page.get("regionText"), f"{pid}: missing normalized region context"

    # Preserve the strongest recurring-location continuity runs.
    for page_num in [1, 3, 4, 5, 6, 7, 8, 9, 10, 11]:
        pid = f"DT_E002_P{page_num:02d}"
        assert by_id[pid].get("setting") == "DT_Concourse17", f"{pid}: Concourse 17 continuity lost"
        assert by_id[pid].get("region") == "DT_MixedCommercialLevels", f"{pid}: Concourse 17 region continuity lost"

    for pid in ("DT_E002_P14", "DT_E002_P15"):
        assert by_id[pid].get("setting") == "DT_PublicHearingChamber", f"{pid}: hearing-room continuity lost"

    for pid in ("DT_E003_P25", "DT_E003_P26", "DT_E004_P01", "DT_E004_P04", "DT_E004_P05", "DT_E004_P06", "DT_E004_P07", "DT_E004_P08", "DT_E004_P11"):
        assert by_id[pid].get("setting") == "DT_VerticalTransitInterchange", f"{pid}: vertical-interchange continuity lost"

    for page_num in range(9, 20):
        pid = f"DT_E006_P{page_num:02d}"
        assert by_id[pid].get("setting") == "DT_CivicRiskLaboratory", f"{pid}: civic-risk-laboratory continuity lost"

    for pid in ("DT_E007_P20", "DT_E007_P21", "DT_E007_P22"):
        assert by_id[pid].get("setting") == "DT_CivicUtilityWorksite", f"{pid}: utility-worksite continuity lost"

    for pid in ("DT_E008_P25", "DT_E008_P26"):
        assert by_id[pid].get("setting") == "DT_CivicVerificationGate", f"{pid}: finale checkpoint continuity lost"

    # The six locked leads must provide image-generation-visible identity anchors.
    for char_id in ("DT_Ostra9", "DT_JohnMercer", "DT_KellenCartwright", "DT_Axiom", "DT_Nico14", "DT_NathanPrice"):
        char = characters[char_id]
        assert char.get("visualAnchor") or char.get("visual") or char.get("appearance") or char.get("visualDescription"), f"{char_id}: missing assembler-visible visual identity anchor"

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
    print("8 issues / 208 pages / normalized visual context through Issue 8 / durable IMG session contract / locked lead visual anchors / valid production references")


if __name__ == "__main__":
    main()
