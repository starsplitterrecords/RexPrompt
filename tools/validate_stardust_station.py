#!/usr/bin/env python3
"""Mechanical integrity checks for Stardust Station RexPrompt production data.

This validator deliberately does not freeze story choices, dialogue, page titles,
page counts, or dramatic beats. It checks that the live Stardust package decodes,
references canonical shelves correctly, preserves usable visual-identity locks, and
keeps curated visual-reference metadata internally coherent.
"""
from __future__ import annotations

import base64
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data" / "shows" / "stardust-station"
MANIFEST = ROOT / "data" / "shows.json"
REFERENCE_PACK = ROOT / "production" / "references" / "stardust-station" / "visual-reference-pack.json"
DRAFT_MANIFEST = ROOT / "production" / "drafts" / "manifest.json"

TEXT_SPEAKERS = {
    "CAPTION", "SYSTEM", "SCREEN", "DISPLAY", "MESSAGE", "GROUP CHAT",
    "MONITOR", "SIGN", "SFX", "MAP", "TIDE BOARD", "SECURITY", "TECHNICIAN"
}
CORE_HANDLES = {
    "@sds.Astra", "@sds.Mira", "@sds.Jax", "@sds.Noola", "@sds.Zib",
    "@sds.Glorp", "@sds.Kreeb", "@sds.Pixa", "@sds.Brick"
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def decode_gzip_base64(path: Path):
    raw = "".join(path.read_text(encoding="utf-8").split())
    return json.loads(gzip.decompress(base64.b64decode(raw, validate=True)).decode("utf-8"))


def load_overlay(path: Path, encoding: str | None):
    if encoding is None:
        return load(path)
    assert encoding == "gzip-base64", f"Unsupported Stardust overlay encoding: {encoding}"
    return decode_gzip_base64(path)


shows = load(MANIFEST)
stardust_entries = [
    entry for entry in shows
    if entry.get("id") == "stardust-station"
    or str(entry.get("id", "")).startswith("stardust-station-e")
]
assert stardust_entries, "No Stardust Station manifest entries found"

characters = load(SHOW / "characters.json")
factions = load(SHOW / "factions.json")
regions = load(SHOW / "regions.json")
settings = load(SHOW / "settings.json")
canonical_handles = {
    value.get("handle")
    for value in characters.values()
    if isinstance(value, dict) and value.get("handle")
}
assert CORE_HANDLES <= canonical_handles, "Core Stardust handles are missing from characters.json"

for key, character in characters.items():
    if not isinstance(character, dict):
        continue
    handle = character.get("handle")
    assert isinstance(handle, str) and handle, f"{key}: missing handle"
    if handle in CORE_HANDLES:
        assert isinstance(character.get("visualAnchor"), str) and character["visualAnchor"].strip(), f"{key}: core character missing visualAnchor"
        locks = character.get("continuityLocks")
        assert isinstance(locks, list) and locks and all(isinstance(item, str) and item.strip() for item in locks), f"{key}: core character missing continuityLocks"
        status = character.get("visualStatus")
        assert isinstance(status, str) and status.strip(), f"{key}: core character missing visualStatus"

assert isinstance(characters.get("SDS_Station", {}).get("visualStatus"), str), "Station System must define non-humanoid visual status"
assert isinstance(characters.get("SDS_Liaison", {}).get("visualAnchor"), str), "Operations Liaison must define a provisional visual anchor"

assert (SHOW / "pages_base.json").exists(), "Missing pages_base.json"

seen_ids: set[str] = set()
seen_overlay_files: set[str] = set()
all_recipe_ids: set[str] = set()
page_total = 0

for entry in stardust_entries:
    show_id = entry.get("id")
    assert entry.get("basePath") == "data/shows/stardust-station", f"{show_id}: basePath drift"
    assert entry.get("scenesFile") == "pages_base.json", f"{show_id}: scenesFile drift"
    assert entry.get("unitLabel") == "PAGE", f"{show_id}: unitLabel must be PAGE"
    generation_line = entry.get("generationLine")
    assert isinstance(generation_line, str) and generation_line.strip(), f"{show_id}: missing generationLine"
    if show_id != "stardust-station":
        assert "released Issue 1 interior-story visual canon" in generation_line, f"{show_id}: released interior-story canon lock missing"
        assert "no cover, title banner, page header, character labels" in generation_line, f"{show_id}: page-style contamination exclusion missing"
        assert "approved" in generation_line and "continuity" in generation_line, f"{show_id}: approved-production continuity rule missing"

    overlays = entry.get("sceneOverlays", [])
    assert isinstance(overlays, list) and overlays, f"{show_id}: missing scene overlays"

    pages = []
    for overlay in overlays:
        assert isinstance(overlay, dict) and overlay.get("file"), f"{show_id}: malformed overlay"
        overlay_file = overlay["file"]
        assert overlay_file not in seen_overlay_files, f"Overlay reused by multiple Stardust entries: {overlay_file}"
        seen_overlay_files.add(overlay_file)
        path = SHOW / overlay_file
        assert path.exists(), f"Missing overlay: {path}"
        decoded = load_overlay(path, overlay.get("encoding"))
        if isinstance(decoded, dict) and isinstance(decoded.get("pages"), list):
            decoded = decoded["pages"]
        assert isinstance(decoded, list), f"{overlay_file}: payload must be a list"
        pages.extend(decoded)

    assert pages, f"{show_id}: no pages assembled"
    page_numbers: list[int] = []

    for page in pages:
        assert isinstance(page, dict), f"{show_id}: page payload must be an object"
        page_id = page.get("id")
        assert isinstance(page_id, str) and page_id, f"{show_id}: page missing id"
        assert page_id not in seen_ids, f"Duplicate Stardust page id: {page_id}"
        seen_ids.add(page_id)
        all_recipe_ids.add(page_id)

        page_number = page.get("page")
        assert isinstance(page_number, int) and page_number > 0, f"{page_id}: invalid page number"
        page_numbers.append(page_number)

        assert isinstance(page.get("summary"), str) and page["summary"].strip(), f"{page_id}: missing summary"
        panel_plan = page.get("panelPlan")
        assert isinstance(panel_plan, list) and panel_plan, f"{page_id}: missing panelPlan"
        panel_count = page.get("panelCount")
        if panel_count is not None:
            assert isinstance(panel_count, int) and panel_count > 0, f"{page_id}: invalid panelCount"
            assert len(panel_plan) == panel_count, f"{page_id}: panelPlan/panelCount mismatch"

        setting = page.get("setting")
        region = page.get("region")
        if setting is not None:
            assert setting in settings, f"{page_id}: unknown setting {setting}"
        if region is not None:
            assert region in regions, f"{page_id}: unknown region {region}"

        page_factions = page.get("factions", [])
        assert isinstance(page_factions, list), f"{page_id}: factions must be a list"
        for faction in page_factions:
            assert faction in factions, f"{page_id}: unknown faction {faction}"

        cast = page.get("charactersInline", [])
        if cast:
            assert isinstance(cast, list), f"{page_id}: charactersInline must be a list"
            cast_handles: set[str] = set()
            for character in cast:
                assert isinstance(character, dict), f"{page_id}: malformed character entry"
                handle = character.get("handle")
                assert handle in canonical_handles, f"{page_id}: unknown character handle {handle}"
                assert handle not in cast_handles, f"{page_id}: duplicate character handle {handle}"
                cast_handles.add(handle)
        else:
            cast_handles = {
                characters[key].get("handle") for key in page.get("characters", [])
                if key in characters and isinstance(characters[key], dict)
            }
            for key in page.get("characters", []):
                assert key in characters, f"{page_id}: unknown character id {key}"

        dialogue = page.get("dialogueInline", [])
        if dialogue:
            assert isinstance(dialogue, list), f"{page_id}: dialogueInline must be a list"
            for line in dialogue:
                assert isinstance(line, dict), f"{page_id}: malformed dialogue entry"
                speaker = line.get("handle") or line.get("speaker")
                text = line.get("text")
                assert isinstance(text, str) and text.strip(), f"{page_id}: blank dialogue text"
                if isinstance(speaker, str) and speaker.startswith("@"):
                    assert speaker in canonical_handles, f"{page_id}: unknown dialogue handle {speaker}"
                    assert speaker in cast_handles, f"{page_id}: dialogue speaker missing from cast {speaker}"
                else:
                    assert speaker in TEXT_SPEAKERS, f"{page_id}: unsupported text speaker {speaker!r}"

    ordered = sorted(page_numbers)
    assert len(ordered) == len(set(ordered)), f"{show_id}: duplicate page numbers"
    assert ordered == list(range(1, max(ordered) + 1)), f"{show_id}: non-contiguous page numbering"
    page_total += len(pages)

pack = load(REFERENCE_PACK)
assert pack.get("schemaVersion") == 1, "Stardust reference pack schemaVersion must be 1"
assert pack.get("seriesId") == "stardust-station", "Stardust reference pack seriesId drift"
refs = pack.get("references")
assert isinstance(refs, list) and refs, "Stardust reference pack must contain references"
ref_ids = {ref.get("id") for ref in refs if isinstance(ref, dict)}
assert None not in ref_ids and len(ref_ids) == len(refs), "Stardust reference pack ids must be unique and non-empty"
character_order = pack.get("characterReferenceOrder")
assert isinstance(character_order, dict), "Stardust characterReferenceOrder missing"
for handle in CORE_HANDLES:
    order = character_order.get(handle)
    assert isinstance(order, list) and order, f"Reference pack missing core character {handle}"
    assert all(ref_id in ref_ids for ref_id in order), f"Reference pack has unknown reference id for {handle}"
assert "@sds.Inspector" in character_order, "Reference pack missing released Inspector anchor"

manifest = load(DRAFT_MANIFEST)
drafts = manifest.get("drafts", {})
assert isinstance(drafts, dict), "Draft manifest drafts must be an object"
for key, draft in drafts.items():
    if not key.startswith("stardust-station::"):
        continue
    assert isinstance(draft, dict), f"{key}: malformed Stardust draft"
    recipe_id = draft.get("recipeId")
    assert recipe_id in all_recipe_ids, f"{key}: approved draft points to unknown Stardust recipe {recipe_id}"

print("Stardust Station mechanical validation passed")
print("Manifest entries:", len(stardust_entries))
print("Pages:", page_total)
print("Unique page ids:", len(seen_ids))
print("Curated references:", len(refs))
print("Approved Stardust drafts:", sum(1 for key in drafts if key.startswith("stardust-station::")))
