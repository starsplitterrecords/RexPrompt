#!/usr/bin/env python3
"""Mechanical integrity checks for Azure Reach RexPrompt data.

Creative choices remain authored in RexPrompt/Notion, not in this validator. This
script checks parseability, reference integrity, page identity/ordering, and that
assembler-visible visual anchors exist for established recurring characters.
"""
import base64
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data" / "shows" / "azure-reach-s1"
MANIFEST = ROOT / "data" / "shows.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def decode(path):
    raw = "".join(path.read_text(encoding="utf-8").split())
    return json.loads(gzip.decompress(base64.b64decode(raw, validate=True)).decode("utf-8"))


shows = load(MANIFEST)
azure_entries = [
    entry for entry in shows
    if entry.get("id") == "azure-reach-s1"
    or str(entry.get("id", "")).startswith("azure-reach-s1-e")
]
assert azure_entries, "No Azure Reach manifest entries found"

characters = load(SHOW / "characters.json")
factions = load(SHOW / "factions.json")
regions = load(SHOW / "regions.json")
settings = load(SHOW / "settings.json")
directions = load(SHOW / "direction.json")
canonical_handles = {
    value.get("handle")
    for value in characters.values()
    if isinstance(value, dict) and value.get("handle")
}

# Established recurring production characters need an assembler-visible visual
# anchor because index.html does not emit character notes.
visual_anchor_ids = {
    "AZR_Maya", "AZR_Julian", "AZR_Fleur", "AZR_Pip", "AZR_Sal",
    "AZR_Beatrice", "AZR_Kyler", "AZR_Dora", "AZR_Elliot", "AZR_Nia", "AZR_Raf",
}
for character_id in visual_anchor_ids:
    entry = characters.get(character_id)
    assert isinstance(entry, dict), f"Missing Azure Reach character: {character_id}"
    anchor = entry.get("visualAnchor")
    assert isinstance(anchor, str) and anchor.strip(), f"{character_id}: missing assembler-visible visualAnchor"

assert (SHOW / "pages_base.json").exists(), "Missing pages_base.json"

seen_ids = set()
seen_overlay_files = set()
page_total = 0

for entry in azure_entries:
    show_id = entry.get("id")
    assert entry.get("basePath") == "data/shows/azure-reach-s1", f"{show_id}: basePath drift"
    assert entry.get("scenesFile") == "pages_base.json", f"{show_id}: scenesFile drift"
    assert entry.get("unitLabel") == "PAGE", f"{show_id}: unitLabel must be PAGE"
    assert isinstance(entry.get("generationLine"), str) and entry["generationLine"].strip(), f"{show_id}: missing generationLine"

    overlays = entry.get("sceneOverlays", [])
    assert isinstance(overlays, list) and overlays, f"{show_id}: missing scene overlays"

    pages = []
    for overlay in overlays:
        assert isinstance(overlay, dict) and overlay.get("file"), f"{show_id}: malformed overlay"
        assert overlay.get("encoding") == "gzip-base64", f"{show_id}: unsupported overlay encoding"
        overlay_file = overlay["file"]
        assert overlay_file not in seen_overlay_files, f"Overlay reused by multiple Azure entries: {overlay_file}"
        seen_overlay_files.add(overlay_file)
        path = SHOW / overlay_file
        assert path.exists(), f"Missing overlay: {path}"
        decoded = decode(path)
        assert isinstance(decoded, list), f"{overlay_file}: decoded payload must be a list"
        pages.extend(decoded)

    assert pages, f"{show_id}: no pages assembled"
    episodes = {page.get("episode") for page in pages}
    assert None not in episodes and len(episodes) == 1, f"{show_id}: overlays mix episodes"

    page_numbers = []
    for page in pages:
        assert isinstance(page, dict), f"{show_id}: page payload must be an object"
        page_id = page.get("id")
        assert isinstance(page_id, str) and page_id, f"{show_id}: page missing id"
        assert page_id not in seen_ids, f"Duplicate page id: {page_id}"
        seen_ids.add(page_id)

        page_number = page.get("page")
        assert isinstance(page_number, int) and page_number > 0, f"{page_id}: invalid page number"
        page_numbers.append(page_number)

        assert isinstance(page.get("summary"), str) and page["summary"].strip(), f"{page_id}: missing summary"
        panel_count = page.get("panelCount")
        panel_plan = page.get("panelPlan")
        assert isinstance(panel_count, int) and panel_count > 0, f"{page_id}: invalid panelCount"
        assert isinstance(panel_plan, list) and len(panel_plan) == panel_count, f"{page_id}: panelPlan/panelCount mismatch"

        setting = page.get("setting")
        region = page.get("region")
        assert setting in settings, f"{page_id}: unknown setting {setting}"
        assert region in regions, f"{page_id}: unknown region {region}"

        page_factions = page.get("factions", [])
        assert isinstance(page_factions, list), f"{page_id}: factions must be a list"
        for faction in page_factions:
            assert faction in factions, f"{page_id}: unknown faction {faction}"

        cast = page.get("charactersInline", [])
        assert isinstance(cast, list) and cast, f"{page_id}: missing charactersInline"
        cast_handles = set()
        for character in cast:
            assert isinstance(character, dict), f"{page_id}: malformed character entry"
            handle = character.get("handle")
            assert handle in canonical_handles, f"{page_id}: unknown character handle {handle}"
            assert handle not in cast_handles, f"{page_id}: duplicate character handle {handle}"
            cast_handles.add(handle)

        dialogue = page.get("dialogueInline", [])
        assert isinstance(dialogue, list) and dialogue, f"{page_id}: missing dialogueInline"
        for line in dialogue:
            assert isinstance(line, dict), f"{page_id}: malformed dialogue entry"
            handle = line.get("handle")
            text = line.get("text")
            assert handle in canonical_handles, f"{page_id}: unknown dialogue handle {handle}"
            assert isinstance(text, str) and text.strip(), f"{page_id}: blank dialogue text"
            if handle != "@azr.Comments":
                assert handle in cast_handles, f"{page_id}: dialogue speaker missing from cast {handle}"

        direction_refs = page.get("direction", [])
        assert isinstance(direction_refs, list), f"{page_id}: direction must be a list"
        assert len(direction_refs) == len(set(direction_refs)), f"{page_id}: duplicate direction refs"
        for ref in direction_refs:
            assert ref in directions, f"{page_id}: unknown direction ref {ref}"

        local_direction = page.get("directionInline", [])
        assert isinstance(local_direction, list), f"{page_id}: directionInline must be a list"
        for item in local_direction:
            assert isinstance(item, dict), f"{page_id}: malformed directionInline entry"
            assert isinstance(item.get("text"), str) and item["text"].strip(), f"{page_id}: blank directionInline text"

    ordered = sorted(page_numbers)
    assert len(ordered) == len(set(ordered)), f"{show_id}: duplicate page numbers"
    assert ordered == list(range(1, max(ordered) + 1)), f"{show_id}: non-contiguous page numbering"

    # continuityFrom is optional creative production data. When present, validate
    # only its shape; do not freeze a particular dramatic chain here.
    for page in pages:
        continuity_from = page.get("continuityFrom")
        if continuity_from is not None:
            assert isinstance(continuity_from, str) and continuity_from.strip(), f"{page['id']}: invalid continuityFrom"

    page_total += len(pages)

print("Azure Reach mechanical validation passed")
print("Manifest entries:", len(azure_entries))
print("Pages:", page_total)
print("Unique page ids:", len(seen_ids))
