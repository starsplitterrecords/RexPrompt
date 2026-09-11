#!/usr/bin/env python3
"""Validate Low Tide Signal image-production normalization state.

Mechanical production checks only. The validator protects reference authority,
page inventory, chef-visible visual specificity, and the writing/image boundary.
It deliberately does not freeze dialogue or exact creative composition.
"""

from __future__ import annotations

import base64
import gzip
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
PAGE_COUNTS = {1: 24, 2: 26, 3: 28, 4: 26, 5: 24, 6: 24, 7: 26}
PAGE_ID = re.compile(r"^LTS_C0([1-7])_P(\d{2})$")
PREVIEW_COVER = "/images/covers/low-tide-signal-issue-01-cover.png"
ENCODED_PAGE_FILES = (
    "pages_c04_between_runs_enhanced.json.gzb64",
    "pages_c05_return_tide_enhanced.json.gzb64",
    "pages_c06_after_the_water_enhanced.json.gzb64",
    "pages_c07_last_low_tide_enhanced.json.gzb64",
)

# These belong in writing/development source, not the assembled image recipe.
CHEF_META = re.compile(
    r"\b(?:thesis|narrative|story function|dramatic beat|authority arc|social defect|"
    r"corrective woman|audience surrogate|validator|moralistic|self-exoneration|"
    r"editorial rationale|writing rationale|reader should|writer should|indict)\b|"
    r"\bnot proof\b|\bnot a research problem\b|\bhidden-history revelation\b|"
    r"\bshould feel\b|\bshould carry\b|\blet the choice\b|\bcloses inquiry\b|"
    r"\bopens? a mystery\b",
    re.IGNORECASE,
)

# Page-level rather than line-level: an individual panel instruction may validly
# be terse ("Nicole buys coffee"), while the complete page still needs concrete
# bodies, props, environment, geography, light, framing, or physical action.
DRAWABLE = re.compile(
    r"\b(?:wide|close|close-up|medium|two-shot|three-shot|profile|overhead|foreground|"
    r"background|panel|frame|face|eyes?|mouth|hands?|arms?|shoulders?|body|head|gaze|"
    r"look|looks|looking|watch|watches|stare|stares|glance|glances|grin|grins|smile|"
    r"smiles|laugh|laughs|nod|nods|frown|frowns|shrug|shrugs|gesture|gestures|stand|"
    r"stands|standing|sit|sits|sitting|walk|walks|walking|run|runs|running|climb|climbs|"
    r"climbing|hold|holds|holding|carry|carries|carrying|point|points|pointing|turn|turns|"
    r"turning|lean|leans|leaning|step|steps|stepping|crouch|crouches|kneel|kneels|pack|"
    r"packs|packing|check|checks|checking|phone|screen|monitor|sensor|rope|bag|boot|boots|"
    r"jacket|water|mud|concrete|fog|rain|light|headlamp|wall|rail|roof|stairs?|door|table|"
    r"chair|bar|glass|window|vehicle|market|mall|apartment|workshop|gym|map|sign|runner|"
    r"crowd|route|floor|plaza|school|clinic|building|shore|tide|channel|arch|tower|bridge|"
    r"walkway|silhouette|figures?|street|transit|store|storefront|device|display|workstation|"
    r"asphalt|road|pavement|structure|corridor|support|gate|floodwall|car|trunk|coffee|"
    r"recorder|graph|chart|desk|bench|mat|stairwell|platform|railing|monitor|work light|"
    r"headlights?|boots?|coat|hood|pack|strap|puddle|pool|signage|wayfinding)\b",
    re.IGNORECASE,
)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def decode_pages(path: Path):
    raw = "".join(path.read_text(encoding="utf-8").split())
    obj = json.loads(gzip.decompress(base64.b64decode(raw)))
    pages = obj.get("pages", obj) if isinstance(obj, dict) else obj
    assert isinstance(pages, list), f"{path.name}: decoded page payload must be a list"
    return pages


def load_all_pages():
    pages = load_json(SHOW_DIR / "pages_ch01_ch03_compiled.json")
    assert isinstance(pages, list), "Low Tide Chapters 1-3 compiled pages must be an array"
    for filename in ENCODED_PAGE_FILES:
        pages.extend(decode_pages(SHOW_DIR / "encoded" / filename))
    return pages


def assert_no_meta(label: str, text: str) -> None:
    assert not CHEF_META.search(text or ""), f"{label}: chef-visible writing rationale detected: {text!r}"


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
    assert baseline.get("currentRelease") == "Preview", "Low Tide current release must remain scoped as Preview until release state changes"
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

        performance = item.get("performance")
        assert isinstance(performance, str) and len(performance.strip()) >= 80, f"{cid}: visual acting direction is too weak"
        assert_no_meta(f"{cid}.performance", performance)

        prompt = item.get("promptContinuity")
        assert isinstance(prompt, list) and len(prompt) >= 4, f"{cid}: promptContinuity missing or too weak"
        assert_no_meta(f"{cid}.promptContinuity", " ".join(map(str, prompt)))

        assert "relationship" not in item, f"{cid}: development relationship prose is again assembler-visible"
        assert isinstance(item.get("developmentRelationship"), str), f"{cid}: development relationship source was not preserved"
        assert isinstance(item.get("developmentPerformance"), str), f"{cid}: development performance source was not preserved"


def validate_regions_and_settings() -> None:
    regions = load_json(SHOW_DIR / "regions.json")
    assert REGION_IDS.issubset(regions), "Low Tide region record missing"
    for rid in REGION_IDS:
        item = regions[rid]
        text = item.get("text")
        assert isinstance(text, str) and len(text.strip()) >= 100, f"{rid}: assembler-visible production text missing"
        assert_no_meta(f"{rid}.text", text)
        assert isinstance(item.get("visual_palette"), list) and item["visual_palette"], f"{rid}: visual palette missing"

    settings = load_json(SHOW_DIR / "settings.json")
    assert settings, "Low Tide settings shelf missing"
    for sid, item in settings.items():
        text = item.get("text")
        assert isinstance(text, str) and text.strip(), f"{sid}: assembler-visible setting text missing"
        assert_no_meta(f"{sid}.text", text)


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


def validate_page_inventory_and_chef_boundary() -> None:
    pages = load_all_pages()
    chars = load_json(SHOW_DIR / "characters.json")
    settings = load_json(SHOW_DIR / "settings.json")
    regions = load_json(SHOW_DIR / "regions.json")

    seen = set()
    counts = {chapter: 0 for chapter in PAGE_COUNTS}
    for page in pages:
        pid = str(page.get("id", ""))
        match = PAGE_ID.match(pid)
        assert match, f"unexpected Low Tide page id: {pid!r}"
        assert pid not in seen, f"duplicate Low Tide page id: {pid}"
        seen.add(pid)

        chapter = int(match.group(1))
        counts[chapter] += 1
        assert page.get("unit") == "PAGE", f"{pid}: unit must remain PAGE"
        assert int(page.get("chapter")) == chapter, f"{pid}: chapter field disagrees with id"

        plan = page.get("panelPlan")
        assert isinstance(plan, list) and plan, f"{pid}: panelPlan is required for image generation"
        assert len(plan) <= 8, f"{pid}: panelPlan unexpectedly large; inspect for prose dumping"
        for i, panel in enumerate(plan, start=1):
            assert isinstance(panel, str) and len(panel.strip()) >= 12, f"{pid} panel {i}: instruction too weak"
            assert_no_meta(f"{pid}.panelPlan[{i}]", panel)

        combined_plan = " ".join(plan)
        drawable_hits = len(DRAWABLE.findall(combined_plan))
        minimum_hits = 1 if len(plan) == 1 else 2
        assert drawable_hits >= minimum_hits, f"{pid}: page plan lacks concrete visual construction ({drawable_hits} drawable cues)"
        assert len(combined_plan) >= 60, f"{pid}: page plan is too thin for image construction"

        summary = page.get("summary")
        assert isinstance(summary, str) and summary.strip(), f"{pid}: visual page summary missing"
        assert_no_meta(f"{pid}.summary", summary)
        assert "Opening image:" in summary or summary.startswith("Full-page composition:"), f"{pid}: summary is not visual-first"

        assert "directionInline" not in page, f"{pid}: directionInline reintroduced; put visible staging in panelPlan"

        setting = page.get("setting")
        if setting:
            assert setting in settings, f"{pid}: unknown setting {setting}"
        region = page.get("region")
        if region:
            assert region in regions, f"{pid}: unknown region {region}"
        for cid in page.get("characters") or []:
            assert cid in chars, f"{pid}: unknown character {cid}"

    assert counts == PAGE_COUNTS, f"Low Tide page inventory drift: {counts} != {PAGE_COUNTS}"
    assert len(seen) == sum(PAGE_COUNTS.values()) == 178, f"Low Tide total page inventory drift: {len(seen)}"


def validate_show_registration() -> None:
    shows = load_json(SHOWS)
    expected = {f"low-tide-signal-c{n:02d}" for n in range(1, 8)}
    records = {x.get("id"): x for x in shows if x.get("id") in expected}
    assert set(records) == expected, "Low Tide Chapter 1-7 show registrations are incomplete"

    for sid, record in records.items():
        assert record.get("seriesId") == "low-tide-signal", f"{sid}: seriesId drift"
        assert record.get("unitLabel") == "PAGE", f"{sid}: unitLabel must remain PAGE"
        line = str(record.get("generationLine", ""))
        lower = line.lower()
        for required in ("portrait", "comic page", "headlamps", "no lanterns", "supernatural effects"):
            assert required in lower, f"{sid}: generationLine lost {required!r}"
        assert_no_meta(f"{sid}.generationLine", line)

        overlays = record.get("sceneOverlays") or []
        assert len(overlays) == 1, f"{sid}: expected exactly one chapter overlay"
        chapter = int(sid[-2:])
        if chapter <= 3:
            assert overlays[0].get("file") == "pages_ch01_ch03_compiled.json", f"{sid}: C1-C3 source drift"
        else:
            assert overlays[0].get("encoding") == "gzip-base64", f"{sid}: encoded chapter lost encoding declaration"


def validate_show_visual_rules() -> None:
    show = load_json(SHOW_DIR / "show.json")
    rules = "\n".join(show.get("hard_visual_rules") or []).lower()
    for required in ("no lanterns", "no supernatural", "no generic cyberpunk neon"):
        assert required in rules, f"Low Tide show hard visual rule missing: {required}"


def main() -> None:
    validate_normalization_reference()
    validate_characters()
    validate_regions_and_settings()
    validate_visual_state()
    validate_page_inventory_and_chef_boundary()
    validate_show_registration()
    validate_show_visual_rules()
    print("Low Tide Signal IMG production normalization validation passed")
    print("Core character baselines:", len(CORE_CHARACTER_IDS))
    print("Page inventory:", sum(PAGE_COUNTS.values()))
    print("Chef page plans:", sum(PAGE_COUNTS.values()), "/", sum(PAGE_COUNTS.values()))
    print("Chef directionInline blocks: 0")
    print("Registered chapters: 7")
    print("Durable frontier policy: derived-not-stored")


if __name__ == "__main__":
    main()
