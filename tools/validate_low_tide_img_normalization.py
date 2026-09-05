#!/usr/bin/env python3
"""Validate Low Tide Signal image-production normalization state.

This validator is intentionally mechanical. It checks production authority,
reference scope, assembler-visible visual fields, page inventory, and durable
visual-state integrity. It does not freeze dialogue, panel composition, or
other creative choices.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW_DIR = ROOT / "data" / "shows" / "low-tide-signal"
NORMALIZATION = ROOT / "production" / "references" / "low-tide-signal" / "img-production-normalization.json"
VISUAL_SOURCES = ROOT / "production" / "visual-sources.json"
DRAFT_MANIFEST = ROOT / "production" / "drafts" / "manifest.json"
RELEASED_LINKS = ROOT / "production" / "released-links.json"
SHOWS = ROOT / "data" / "shows.json"

CORE_CHARACTER_IDS = {
    "C_lts_matt_donnelly",
    "C_lts_ryan_kelleher",
    "C_lts_chris_barlow",
    "C_lts_justin_rourke",
    "C_lts_nicole_hanley",
    "C_lts_kevin_marsh",
}
REGION_IDS = {"R_lts_inland", "R_lts_threshold", "R_lts_flats", "R_lts_reach"}
PAGE_COUNTS = {1: 24, 2: 26, 3: 28}
PAGE_ID = re.compile(r"^LTS_C0([123])_P(\d{2})$")
PREVIEW_COVER = "/images/covers/low-tide-signal-issue-01-cover.png"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate_normalization_reference() -> None:
    assert NORMALIZATION.is_file(), "missing Low Tide IMG normalization reference"
    ref = load_json(NORMALIZATION)
    assert ref.get("schemaVersion") == 1, "Low Tide IMG normalization schemaVersion drift"
    assert ref.get("seriesId") == "low-tide-signal", "Low Tide IMG normalization seriesId drift"
    assert ref.get("status") == "normalized-img-production-reference", "Low Tide IMG normalization status drift"

    baseline = ref.get("releasedBaseline") or {}
    assert baseline.get("repository") == "starsplitterrecords/StarSplitterVisions", "released baseline repository drift"
    assert baseline.get("branch") == "main", "released baseline must resolve from StarSplitterVisions main"
    assert baseline.get("visionsSlug") == "low-tide-signal", "released baseline slug drift"
    assert baseline.get("currentRelease") == "Preview", "Low Tide current release must remain explicitly scoped as Preview until release state changes"
    assert baseline.get("previewCover") == PREVIEW_COVER, "Low Tide preview cover path drift"
    assert baseline.get("releasedInteriorPageCount") == 0, "normalization must be updated when Low Tide interior pages are released"
    assert baseline.get("releasedInteriorIssueAvailable") is False, "normalization must be updated when a released interior issue exists"

    locks = ref.get("knownScopeLocks") or []
    cover_lock = next((x for x in locks if x.get("path") == PREVIEW_COVER), None)
    assert cover_lock, "preview cover scope lock is missing"
    assert cover_lock.get("characterIdentityAuthority") is False, "preview cover must not become recurring-character authority"
    assert cover_lock.get("storyPageLayoutAuthority") is False, "preview cover must not become story-page layout authority"
    assert cover_lock.get("interiorWorldDesignAuthority") is False, "preview cover must not become interior-world design authority"

    frontier = ref.get("frontierPolicy") or {}
    assert frontier.get("mode") == "derived-not-stored", "Low Tide production frontier must be derived, never stored as a cursor"

    output_rule = ref.get("storyPageOutputRule", "").lower()
    for forbidden in ("page label", "character name", "promotional callout", "cover trade dress"):
        assert forbidden in output_rule, f"story-page output rule lost {forbidden!r} exclusion"


def validate_characters() -> None:
    chars = load_json(SHOW_DIR / "characters.json")
    assert CORE_CHARACTER_IDS.issubset(chars), "Low Tide core cast record missing"
    for cid in CORE_CHARACTER_IDS:
        item = chars[cid]
        assert isinstance(item.get("visual"), str) and item["visual"].strip(), f"{cid}: assembler-visible visual baseline missing"
        status = item.get("visualStatus")
        assert isinstance(status, str) and "no approved character image reference" in status.lower(), f"{cid}: visual approval state is not explicit"
        locks = item.get("continuityLocks")
        assert isinstance(locks, list) and len(locks) >= 3, f"{cid}: continuityLocks missing or too weak"


def validate_regions() -> None:
    regions = load_json(SHOW_DIR / "regions.json")
    assert REGION_IDS.issubset(regions), "Low Tide region record missing"
    for rid in REGION_IDS:
        item = regions[rid]
        text = item.get("text")
        assert isinstance(text, str) and len(text.strip()) >= 60, f"{rid}: assembler-visible production text missing"
        assert isinstance(item.get("visual_palette"), list) and item["visual_palette"], f"{rid}: visual palette missing"


def validate_visual_state() -> None:
    sources = load_json(VISUAL_SOURCES)
    entry = (sources.get("series") or {}).get("low-tide-signal")
    assert entry == {"visionsSlug": "low-tide-signal"}, "Low Tide is not registered correctly in production/visual-sources.json"

    drafts = (load_json(DRAFT_MANIFEST).get("drafts") or {})
    for key, item in drafts.items():
        if not key.startswith("low-tide-signal::"):
            continue
        expected = f"{item.get('seriesId')}::{item.get('issueId')}::{item.get('recipeId')}"
        assert key == expected, f"Low Tide draft key mismatch: {key}"
        assert item.get("seriesId") == "low-tide-signal", f"Low Tide draft seriesId mismatch: {key}"
        assert item.get("status") == "approved-production-draft", f"Low Tide draft is not approved-production-draft: {key}"
        assert PAGE_ID.match(str(item.get("recipeId", ""))), f"Low Tide draft recipeId is not a current page recipe: {key}"

    links = (load_json(RELEASED_LINKS).get("links") or {})
    for key, raw in links.items():
        if not key.startswith("low-tide-signal::"):
            continue
        items = raw if isinstance(raw, list) else raw.get("images", [raw]) if isinstance(raw, dict) else []
        for item in items:
            path = item if isinstance(item, str) else (item.get("path") or item.get("image") or item.get("url") or "")
            assert PREVIEW_COVER not in path, "Low Tide preview cover must never be mapped as released interior recipe canon"


def validate_page_inventory() -> None:
    pages = load_json(SHOW_DIR / "pages_ch01_ch03_compiled.json")
    assert isinstance(pages, list), "Low Tide compiled pages must be an array"
    seen = set()
    counts = {1: 0, 2: 0, 3: 0}
    for page in pages:
        pid = page.get("id", "")
        match = PAGE_ID.match(pid)
        if not match:
            continue
        assert pid not in seen, f"duplicate Low Tide page id: {pid}"
        seen.add(pid)
        chapter = int(match.group(1))
        counts[chapter] += 1
        assert page.get("unit") == "PAGE", f"{pid}: unit must remain PAGE"
    assert counts == PAGE_COUNTS, f"Low Tide compiled page inventory drift: {counts} != {PAGE_COUNTS}"


def validate_show_registration() -> None:
    shows = load_json(SHOWS)
    expected = {"low-tide-signal-c01", "low-tide-signal-c02", "low-tide-signal-c03"}
    records = {x.get("id"): x for x in shows if x.get("id") in expected}
    assert set(records) == expected, "Low Tide Chapter 1-3 show registrations are incomplete"
    for sid, record in records.items():
        assert record.get("unitLabel") == "PAGE", f"{sid}: unitLabel must remain PAGE"
        line = str(record.get("generationLine", "")).lower()
        for required in ("portrait", "comic page", "no supernatural", "no lanterns"):
            assert required in line, f"{sid}: generationLine lost {required!r}"


def validate_show_visual_rules() -> None:
    show = load_json(SHOW_DIR / "show.json")
    rules = "\n".join(show.get("hard_visual_rules") or []).lower()
    for required in ("no lanterns", "no supernatural", "no generic cyberpunk neon"):
        assert required in rules, f"Low Tide show hard visual rule missing: {required}"


def main() -> None:
    validate_normalization_reference()
    validate_characters()
    validate_regions()
    validate_visual_state()
    validate_page_inventory()
    validate_show_registration()
    validate_show_visual_rules()
    print("Low Tide Signal IMG production normalization validation passed")
    print("Core character baselines:", len(CORE_CHARACTER_IDS))
    print("Compiled page inventory:", sum(PAGE_COUNTS.values()))
    print("Durable frontier policy: derived-not-stored")


if __name__ == "__main__":
    main()
