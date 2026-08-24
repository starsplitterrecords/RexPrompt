#!/usr/bin/env python3
"""Validate sanitized Stardust Station production data for Issues 1-3."""
from __future__ import annotations

import base64
import gzip
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data" / "shows" / "stardust-station"
MANIFEST = ROOT / "data" / "shows.json"

SANITIZATION_RESIDUE = (
    "STARDUST STATION VISUAL LANGUAGE:",
    "PAGE ACTION — SOURCE-LOCKED:",
    "CHARACTER CONTINUITY —",
    "LOCATION / PROP / STATE CONTINUITY —",
    "CAMERA / LIGHT —",
    "COMIC PAGE / LETTERING —",
    "exact source dialogue",
    "exact approved revision dialogue",
    "exact enhanced Issue 2 dialogue",
    "exact enhanced Issue 3 dialogue",
)

ISSUES = {
    1: {
        "show_id": "stardust-station",
        "episode": "S1E01",
        "expected": [
            (1, "Main Bullpen Huddle", 5), (2, "The Inspection Announcement", 6),
            (3, "Astra Frames the Disaster", 6), (4, "Pair Assignments", 7),
            (5, "Procedure and Emotional Readiness", 6), (6, "Rules and Early Arrival", 7),
            (7, "Corridor Lock-In", 6), (8, "Too Many People, Too Little Hallway", 6),
            (9, "Forms, Pressure, and First Honesty", 7), (10, "The Corridor Asks for Honesty", 6),
            (11, "Jax Admits the Small Failure", 6), (12, "Astra Admits Hers", 6),
            (13, "Team Repair", 7), (14, "Release Button", 6), (15, "Procedure Circle", 6),
            (16, "Evidence Review", 6), (17, "Tour Rescue / Vent Form", 4),
            (18, "Useful Waste", 6), (19, "No Optimization Circle", 6),
            (20, "Actual Tour", 6), (21, "Result + Cleanup Montage", 7),
            (22, "Tag: The Vending Machine", 5),
        ],
        "overlays": [
            {"file":"encoded/pages_e01_p01_p06.json.gzb64","encoding":"gzip-base64"},
            {"file":"encoded/pages_e01_p07_p12.json.gzb64","encoding":"gzip-base64"},
            {"file":"encoded/pages_e01_p13_p18.json.gzb64","encoding":"gzip-base64"},
            {"file":"encoded/pages_e01_p19_p22.json.gzb64","encoding":"gzip-base64"},
        ],
        "source": "Stardust Station — Issue 1 Full Script v4: Continuity-Compressed Draft",
        "revision_source": "Stardust Station — Issue 1 Pair-Dynamics Revision, approved 2026-08-21",
        "revision_pages": set(range(15, 21)),
        "panel_total": 133,
        "forbidden": ("Azure Reach", "Launchpad Summer", "@azr.", "@brk.", "@starsplit."),
        "critical": (
            "TEAMWORK: BECAUSE AIR IS SHARED.",
            "PLEASE REPORT ALL CRYSTAL RESIDUE BEFORE IT BECOMES DECOR.",
            "TEMPORARY STORAGE IS NOT A PERSONALITY.",
            "Microwave Feelings Disclosure Form 8C is now mandatory for all grouped personnel.",
            "SUSPICION ZONE", "FEELINGS DISCLOSURE SEAT A", "WITNESS DRONE",
            "UNUSUAL MATERIAL FLAG — CLASSIFY USEFUL WASTE",
            "WOULD YOU LIKE TO SCHEDULE A YIELD OPTIMIZATION CONSULT?",
            "Nobody is optimizing anyone’s emotions. We barely survived optimizing the chairs.",
            "Stardust Station passes adaptive response, cross-functional recovery, and useful byproduct reporting.",
            "Operating status remains active pending follow-up review.",
            "CHARM RESIDUE DETECTED", "FEELINGS NOT ACCEPTED AS PAYMENT",
        ),
    },
    2: {
        "show_id": "stardust-station-e02",
        "episode": "S1E02",
        "expected": [
            (1,"The Room with Too Many Signs",5),(2,"Temporary Means Mandatory",6),
            (3,"Astra Restores Normalcy, in Theory",6),(4,"Report It Before It Becomes a Meeting",6),
            (5,"Correlation Is Not a Confession",6),(6,"Soup Becomes Context",6),
            (7,"The Actual Problem Is Embarrassingly Physical",6),(8,"The Machine Is Easy",6),
            (9,"One Page, One Side",6),(10,"The Bright Chair",6),(11,"The One-Page Procedure",6),
            (12,"One Sample",5),(13,"Normal Lunch Trial",6),(14,"Normal Becomes a Procedure",6),
            (15,"What the Page Is For",6),(16,"No Sequel for the Soup",5),(17,"Three Rules, Apparently",6),
            (18,"The Test",6),(19,"Legacy Integration",6),(20,"Emotionally Unverified",6),
            (21,"Small Things Stay Small",6),(22,"Tag: The Mug",5),
        ],
        "overlays": [
            {"file":"encoded/pages_e02_p01_p06.json.gzb64","encoding":"gzip-base64"},
            {"file":"encoded/pages_e02_p07_p12.json.gzb64","encoding":"gzip-base64"},
            {"file":"encoded/pages_e02_p13_p18.json.gzb64","encoding":"gzip-base64"},
            {"file":"encoded/pages_e02_p19_p22.json.gzb64","encoding":"gzip-base64"},
        ],
        "source": "Stardust Station — Issue 2 Enhanced Production Script, 2026-08-22",
        "panel_total": 128,
        "forbidden": ("Policy and Disorder", "MUG GRIEF UNRESOLVED", "interpersonal sensitivity", "It is not about the mug"),
        "critical": (
            "The break room is not a department.", "Small thing. That side is warmer than yesterday.",
            "The dust does not know about mugs.", "You covered the vent.", "One side is how nuance dies.",
            "I need to know what this page is protecting.",
            "Report physical failures. Ask before taking someone else's things. Otherwise, eat.",
            "We are all going to behave like people who have seen a microwave before.",
            "Form 8C trigger was still mapped to appliance-cycle completion.",
            "PRESSURE CORRELATION — CONTENT UNKNOWN", "Normal enough.",
        ),
    },
    3: {
        "show_id": "stardust-station-e03",
        "episode": "S1E03",
        "expected": [
            (1,"Ten Minutes",5),(2,"Three Items, No Archaeology",6),(3,"Observable Metrics Only",6),
            (4,"Jax Is Available",6),(5,"What Does Owner Mean",6),(6,"The Dust Still Cannot Read",6),
            (7,"Zib Needs the Wall",5),(8,"Someone Should",6),(9,"Item One Returns",6),
            (10,"Correlation, Not Vocabulary",6),(11,"Hide the Dashboard",6),(12,"Support Is Not Ownership",6),
            (13,"Decision Without Owner",6),(14,"The Ownership Rule",6),(15,"Jax Takes One",6),
            (16,"Enough Meeting",5),(17,"The Record Objects",6),(18,"The Meeting Becomes Work",6),
            (19,"Ten Minutes of Repair",6),(20,"After",6),(21,"That Last One Is the Metric",6),
            (22,"Tag: Follow-Up Not Scheduled",5),
        ],
        "overlays": [
            {"file":"encoded/pages_e03_p01_p06.json.gzb64","encoding":"gzip-base64"},
            {"file":"encoded/pages_e03_p07_p12.json.gzb64","encoding":"gzip-base64"},
            {"file":"encoded/pages_e03_p13_p18.json.gzb64","encoding":"gzip-base64"},
            {"file":"encoded/pages_e03_p19_p22.json.gzb64","encoding":"gzip-base64"},
        ],
        "source": "Stardust Station — Issue 3 Enhanced Production Script, 2026-08-22",
        "panel_total": 128,
        "forbidden": ("OWNERSHIP AVOIDANCE:", "DEFLECTION FORMING", "MUG SYMBOLISM", "unresolved mug grief", "SEE ALSO: SOUP"),
        "critical": (
            "The dust still cannot read.", "I am fully available in an advisory capacity.",
            "Unnamed action item detected.", "The dust is not reacting to the word 'owner.'",
            "You keep offering help that ends when the task starts.", "Fine. I own the access label.",
            "No more agenda. We have enough decisions to do work.",
            "Then they remain unassigned until someone has a reason to do them.",
            "An empty line can be honest.", "PRESSURE CORRELATION — CONTENT UNKNOWN",
            "That last one is the metric.", "FOLLOW-UP NOT SCHEDULED.", "WORK IN PROGRESS",
        ),
    },
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def decode(path: Path):
    encoded = "".join(path.read_text(encoding="utf-8").split())
    return json.loads(gzip.decompress(base64.b64decode(encoded, validate=True)).decode("utf-8"))


def validate_registry() -> tuple[dict, dict, dict, dict]:
    characters = load(SHOW / "characters.json")
    allowed_character_fields = {"name", "handle", "visualAnchor", "visualStatus"}
    for key, entry in characters.items():
        if not isinstance(entry, dict):
            raise SystemExit(f"Character {key} must be an object")
        extra = set(entry) - allowed_character_fields
        if extra:
            raise SystemExit(f"Character {key} contains non-production identity fields: {sorted(extra)}")
        if not entry.get("name") or not entry.get("handle"):
            raise SystemExit(f"Character {key} missing name/handle")
    if characters.get("SDS_Kreeb", {}).get("name") != "Kreeb":
        raise SystemExit("Current Kreeb production name drift")
    if characters.get("SDS_Pixa", {}).get("name") != "Pixa":
        raise SystemExit("Current Pixa production name drift")

    regions = load(SHOW / "regions.json")
    settings = load(SHOW / "settings.json")
    factions = load(SHOW / "factions.json")
    region_text = regions["SDS_Stardust_Station"]["text"]
    for required in ("Bright", "maintained", "workplace", "institutional signage"):
        if required.lower() not in region_text.lower():
            raise SystemExit(f"Sanitized Stardust region ground missing: {required}")
    return characters, settings, regions, factions


def expected_source(cfg: dict, page_number: int) -> str:
    if page_number in cfg.get("revision_pages", set()):
        return cfg["revision_source"]
    return cfg["source"]


def validate_issue(cfg: dict, shows: list, characters: dict, settings: dict, regions: dict, factions: dict) -> list:
    show = next((s for s in shows if s.get("id") == cfg["show_id"]), None)
    if not show:
        raise SystemExit(f"Missing show manifest entry: {cfg['show_id']}")
    if show.get("basePath") != "data/shows/stardust-station" or show.get("scenesFile") != "pages_base.json":
        raise SystemExit(f"{cfg['show_id']}: base production path drift")
    if show.get("unitLabel") != "PAGE" or show.get("sceneOverlays") != cfg["overlays"]:
        raise SystemExit(f"{cfg['show_id']}: page/overlay manifest drift")
    if "comic page" not in show.get("generationLine", "").lower():
        raise SystemExit(f"{cfg['show_id']}: generationLine must remain page-production scoped")

    pages = []
    for overlay in cfg["overlays"]:
        path = SHOW / overlay["file"]
        if not path.exists():
            raise SystemExit(f"Missing payload: {overlay['file']}")
        pages.extend(decode(path))

    if len(pages) != 22:
        raise SystemExit(f"{cfg['show_id']}: expected 22 pages, found {len(pages)}")

    all_text = json.dumps(pages, ensure_ascii=False)
    for residue in SANITIZATION_RESIDUE:
        if residue.lower() in all_text.lower():
            raise SystemExit(f"{cfg['show_id']}: repeated production scaffolding returned: {residue}")
    for term in cfg["forbidden"]:
        if term.lower() in all_text.lower():
            raise SystemExit(f"{cfg['show_id']}: stale material returned")
    for term in cfg["critical"]:
        if term not in all_text:
            raise SystemExit(f"{cfg['show_id']}: missing source-locked story text: {term}")

    canonical_handles = {v["handle"] for v in characters.values() if isinstance(v, dict) and v.get("handle")}
    system_handle = "@sds.Station"
    seen = set()
    for page, (number, title, panels) in zip(pages, cfg["expected"]):
        expected_id = f"SDS_{cfg['episode']}_P{number:02d}"
        if page.get("id") != expected_id or page.get("episode") != cfg["episode"] or page.get("page") != number:
            raise SystemExit(f"{cfg['show_id']}: page {number} identity drift")
        if page["id"] in seen:
            raise SystemExit(f"Duplicate page id: {page['id']}")
        seen.add(page["id"])
        if page.get("pageTitle") != title or page.get("panelCount") != panels:
            raise SystemExit(f"{expected_id}: title/panel-count drift")
        if len(page.get("panelPlan", [])) != panels:
            raise SystemExit(f"{expected_id}: panelPlan count drift")
        if page.get("source") != expected_source(cfg, number):
            raise SystemExit(f"{expected_id}: source provenance drift")
        if page.get("setting") not in settings or page.get("region") not in regions:
            raise SystemExit(f"{expected_id}: unknown setting/region")
        for faction in page.get("factions", []):
            if faction not in factions:
                raise SystemExit(f"{expected_id}: unknown faction {faction}")

        cast = {
            c.get("handle") for c in page.get("charactersInline", [])
            if isinstance(c, dict) and c.get("handle")
        }
        if not cast or cast - canonical_handles:
            raise SystemExit(f"{expected_id}: cast reference drift")
        for c in page.get("charactersInline", []):
            if isinstance(c, dict) and set(c) - {"name", "handle"}:
                raise SystemExit(f"{expected_id}: page-level character description returned")

        lines = page.get("dialogueInline", [])
        if not lines:
            raise SystemExit(f"{expected_id}: missing dialogue")
        for line in lines:
            handle = line.get("handle")
            if handle not in canonical_handles:
                raise SystemExit(f"{expected_id}: unknown dialogue handle {handle}")
            if handle != system_handle and handle not in cast:
                raise SystemExit(f"{expected_id}: dialogue speaker missing from declared cast: {handle}")
            if not line.get("text"):
                raise SystemExit(f"{expected_id}: blank dialogue")
            match = re.fullmatch(r"Panel\s+(\d+)", str(line.get("subtext", "")))
            if not match:
                raise SystemExit(f"{expected_id}: dialogue panel mapping must be concise and structured")
            panel_no = int(match.group(1))
            if not 1 <= panel_no <= panels:
                raise SystemExit(f"{expected_id}: dialogue panel out of range")

        if page.get("directionInline"):
            raise SystemExit(f"{expected_id}: standing production prose must not be stored at page scope")

    if sum(page["panelCount"] for page in pages) != cfg["panel_total"]:
        raise SystemExit(f"{cfg['show_id']}: issue panel total drift")
    return pages


def validate_specialized(issue: int, pages: list) -> None:
    if issue == 1:
        expected = {
            15: ("small-group", ["Jax / Glorp / Kreeb"]),
            16: ("small-group", ["Jax / Mira / Zib"]),
            17: ("small-group", ["Astra / Mira / Inspector"]),
            18: ("small-group", ["Astra / Mira / Pixa"]),
            19: ("split-small-groups", ["Astra / Glorp / Kreeb", "Jax / Noola / Brick"]),
            20: ("ensemble-reconvergence", ["Ensemble reconvergence after Pages 15–19 small-group sequence"]),
        }
        for number, (mode, focus) in expected.items():
            if pages[number-1].get("relationshipMode") != mode or pages[number-1].get("relationshipFocus") != focus:
                raise SystemExit(f"Issue 1 page {number}: relationship structure drift")
        page20 = " ".join(x.get("text", "") for x in pages[19].get("dialogueInline", [])).lower()
        if "overbuilt, under-noticed" not in page20 or "underfunded" in page20:
            raise SystemExit("Issue 1 page 20 premise drift")
    elif issue == 2:
        if pages[3].get("relationshipFocus") != ["Astra / Glorp / Kreeb scope control", "Jax / Zib early reporting"]:
            raise SystemExit("Issue 2 page 4 causal ownership drift")
        if "Jax's early report leads Zib" not in pages[6].get("summary", ""):
            raise SystemExit("Issue 2 page 7 causal payoff drift")
        if pages[14].get("relationshipFocus") != ["Astra / Glorp / Kreeb core issue ownership"]:
            raise SystemExit("Issue 2 page 15 ownership drift")
        if "correlation rather than meaning" not in pages[19].get("summary", ""):
            raise SystemExit("Issue 2 page 20 non-semantic framing drift")
    elif issue == 3:
        p4 = " ".join(x.get("text", "") for x in pages[3].get("dialogueInline", []))
        p10 = " ".join(x.get("text", "") for x in pages[9].get("dialogueInline", []))
        p15 = " ".join(x.get("text", "") for x in pages[14].get("dialogueInline", []))
        p17 = " ".join(x.get("text", "") for x in pages[16].get("dialogueInline", []))
        if "advisory capacity" not in p4 or "not reacting to the word" not in p10.lower():
            raise SystemExit("Issue 3 ownership/correlation progression drift")
        if "I own the access label" not in p15 or "empty line can be honest" not in p17:
            raise SystemExit("Issue 3 accountability/incompleteness progression drift")
        if pages[17].get("relationshipMode") != "split-small-groups":
            raise SystemExit("Issue 3 page 18 work-breakout structure drift")


shows = load(MANIFEST)
characters, settings, regions, factions = validate_registry()
for issue, cfg in ISSUES.items():
    pages = validate_issue(cfg, shows, characters, settings, regions, factions)
    validate_specialized(issue, pages)

print("Stardust Station sanitized validation passed")
print("Issues: 3")
print("Pages: 66")
print("Persistent character descriptions at page scope: 0")
print("Standing direction boilerplate at page scope: 0")
