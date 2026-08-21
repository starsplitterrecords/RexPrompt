#!/usr/bin/env python3
import base64
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW_ID = "stardust-station"
BASE_SOURCE = 'Stardust Station — Issue 1 Full Script v4: Continuity-Compressed Draft'
REVISION_SOURCE = 'Stardust Station — Issue 1 Pair-Dynamics Revision, approved 2026-08-21'
REVISED_PAGE_NUMBERS = set(range(15, 21))

SHOW = ROOT / "data" / "shows" / SHOW_ID
MANIFEST = ROOT / "data" / "shows.json"
INDEX = ROOT / "index.html"

EXPECTED = [
    (1, "Main Bullpen Huddle", 5),
    (2, "The Inspection Announcement", 6),
    (3, "Astra Frames the Disaster", 6),
    (4, "Pair Assignments", 7),
    (5, "Procedure and Emotional Readiness", 6),
    (6, "Rules and Early Arrival", 7),
    (7, "Corridor Lock-In", 6),
    (8, "Too Many People, Too Little Hallway", 6),
    (9, "Forms, Pressure, and First Honesty", 7),
    (10, "The Corridor Asks for Honesty", 6),
    (11, "Jax Admits the Small Failure", 6),
    (12, "Astra Admits Hers", 6),
    (13, "Team Repair", 7),
    (14, "Release Button", 6),
    (15, "Procedure Circle", 6),
    (16, "Evidence Review", 6),
    (17, "Tour Rescue / Vent Form", 4),
    (18, "Useful Waste", 6),
    (19, "No Optimization Circle", 6),
    (20, "Actual Tour", 6),
    (21, "Result + Cleanup Montage", 7),
    (22, "Tag: The Vending Machine", 5),
]

DIR_PREFIXES = (
    "STARDUST STATION VISUAL LANGUAGE:",
    "PAGE ACTION — SOURCE-LOCKED:",
    "CHARACTER CONTINUITY —",
    "LOCATION / PROP / STATE CONTINUITY —",
    "CAMERA / LIGHT —",
    "COMIC PAGE / LETTERING —",
)

REQUIRED_FILES = (
    "blocking.json", "characters.json", "dialogue.json", "direction.json",
    "factions.json", "lighting.json", "mood.json", "negatives.json",
    "regions.json", "settings.json", "pages_base.json",
    "encoded/pages_e01_p01_p06.json.gzb64",
    "encoded/pages_e01_p07_p12.json.gzb64",
    "encoded/pages_e01_p13_p18.json.gzb64",
    "encoded/pages_e01_p19_p22.json.gzb64",
)

EXPECTED_OVERLAYS = [
    {"file": "encoded/pages_e01_p01_p06.json.gzb64", "encoding": "gzip-base64"},
    {"file": "encoded/pages_e01_p07_p12.json.gzb64", "encoding": "gzip-base64"},
    {"file": "encoded/pages_e01_p13_p18.json.gzb64", "encoding": "gzip-base64"},
    {"file": "encoded/pages_e01_p19_p22.json.gzb64", "encoding": "gzip-base64"},
]

FORBIDDEN_PAGE_TEXT = (
    "Azure Reach",
    "Launchpad Summer",
    "@azr.",
    "@brk.",
    "@starsplit.",
    "sacred crystal",
    "glowing crystal",
    "crystal temple",
    "Kreeg Hssssk",
    "Pixa9",
)

CRITICAL_TEXT = (
    "TEAMWORK: BECAUSE AIR IS SHARED.",
    "PLEASE REPORT ALL CRYSTAL RESIDUE BEFORE IT BECOMES DECOR.",
    "TEMPORARY STORAGE IS NOT A PERSONALITY.",
    "Microwave Feelings Disclosure Form 8C is now mandatory for all grouped personnel.",
    "SUSPICION ZONE",
    "FEELINGS DISCLOSURE SEAT A",
    "WITNESS DRONE",
    "UNUSUAL MATERIAL FLAG — CLASSIFY USEFUL WASTE",
    "WOULD YOU LIKE TO SCHEDULE A YIELD OPTIMIZATION CONSULT?",
    "Nobody is optimizing anyone’s emotions. We barely survived optimizing the chairs.",
    "Stardust Station passes adaptive response, cross-functional recovery, and useful byproduct reporting.",
    "Operating status remains active pending follow-up review.",
    "CHARM RESIDUE DETECTED",
    "FEELINGS NOT ACCEPTED AS PAYMENT",
)

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

for name in REQUIRED_FILES:
    if not (SHOW / name).exists():
        raise SystemExit(f"Missing Stardust Station data file: {name}")

shows = load(MANIFEST)
show = next((s for s in shows if s.get("id") == SHOW_ID), None)
if not show:
    raise SystemExit("Stardust Station missing from data/shows.json")
if show.get("basePath") != "data/shows/stardust-station":
    raise SystemExit("Stardust Station basePath drift")
if show.get("scenesFile") != "pages_base.json":
    raise SystemExit("Stardust Station base pages file drift")
if show.get("sceneOverlays") != EXPECTED_OVERLAYS:
    raise SystemExit("Stardust Station encoded page overlay drift")
if show.get("unitLabel") != "PAGE":
    raise SystemExit("Stardust Station must assemble as PAGE units")
generation = show.get("generationLine", "").lower()
if "comic page" not in generation or "10-second" in generation or "video" in generation:
    raise SystemExit("Stardust Station generationLine must be comic-page-only")

index = INDEX.read_text(encoding="utf-8")
for required in (
    "store.__show=show",
    'unitLabel=show.unitLabel||"SCENE"',
    'show.generationLine||"10-second vertical clip.',
    'if(s.panelPlan?.length){out.push("\\n[PANEL PLAN]")',
):
    if required not in index:
        raise SystemExit(f"RexPrompt page-mode support missing: {required}")

pages = []
for overlay in EXPECTED_OVERLAYS:
    encoded = "".join((SHOW / overlay["file"]).read_text(encoding="utf-8").split())
    pages.extend(json.loads(gzip.decompress(base64.b64decode(encoded, validate=True)).decode("utf-8")))

if len(pages) != 22:
    raise SystemExit(f"Expected 22 Issue #1 pages, found {len(pages)}")

characters = load(SHOW / "characters.json")
canonical_handles = {
    v.get("handle") for v in characters.values()
    if isinstance(v, dict) and v.get("handle")
}
system_handles = {"@sds.Station"}
factions = load(SHOW / "factions.json")
regions = load(SHOW / "regions.json")
settings = load(SHOW / "settings.json")

region_text = json.dumps(regions["SDS_Stardust_Station"], ensure_ascii=False).lower()
for required in ("bright", "maintained", "workplace", "no grimdark", "sacred-crystal"):
    if required not in region_text:
        raise SystemExit(f"Stardust visual ground missing required guardrail: {required}")

all_page_text = json.dumps(pages, ensure_ascii=False)
for forbidden in FORBIDDEN_PAGE_TEXT:
    if forbidden.lower() in all_page_text.lower():
        raise SystemExit(f"Foreign/stale material found in Stardust production pages: {forbidden}")

seen = set()
dialogue_count = 0
for page, (number, title, panels) in zip(pages, EXPECTED):
    expected_id = f"SDS_S1E01_P{number:02d}"
    if page.get("id") != expected_id:
        raise SystemExit(f"Page {number}: expected id {expected_id}, found {page.get('id')}")
    if page["id"] in seen:
        raise SystemExit(f"Duplicate page id: {page['id']}")
    seen.add(page["id"])
    if page.get("episode") != "S1E01" or page.get("page") != number:
        raise SystemExit(f"{expected_id}: numbering drift")
    if page.get("pageTitle") != title:
        raise SystemExit(f"{expected_id}: title drift")
    if page.get("panelCount") != panels:
        raise SystemExit(f"{expected_id}: expected {panels} panels, found {page.get('panelCount')}")
    if len(page.get("panelPlan", [])) != panels:
        raise SystemExit(f"{expected_id}: panelPlan must contain exactly {panels} entries")
    expected_source = REVISION_SOURCE if number in REVISED_PAGE_NUMBERS else BASE_SOURCE
    if page.get("source") != expected_source:
        raise SystemExit(f"{expected_id}: source authority drift")
    if page.get("setting") not in settings:
        raise SystemExit(f"{expected_id}: unknown setting {page.get('setting')}")
    if page.get("region") not in regions:
        raise SystemExit(f"{expected_id}: unknown region {page.get('region')}")
    for faction in page.get("factions", []):
        if faction not in factions:
            raise SystemExit(f"{expected_id}: unknown faction {faction}")

    cast_handles = {
        c.get("handle") for c in page.get("charactersInline", [])
        if isinstance(c, dict) and c.get("handle")
    }
    if not cast_handles:
        raise SystemExit(f"{expected_id}: missing charactersInline")
    unknown_cast = cast_handles - canonical_handles
    if unknown_cast:
        raise SystemExit(f"{expected_id}: unknown cast handles {sorted(unknown_cast)}")
    if any(not h.startswith("@sds.") for h in cast_handles):
        raise SystemExit(f"{expected_id}: non-Stardust handle in cast")

    lines = page.get("dialogueInline", [])
    if not lines:
        raise SystemExit(f"{expected_id}: missing exact dialogue")
    dialogue_count += len(lines)
    for line in lines:
        handle = line.get("handle")
        if handle not in canonical_handles:
            raise SystemExit(f"{expected_id}: noncanonical dialogue handle {handle}")
        if handle not in system_handles and handle not in cast_handles:
            raise SystemExit(f"{expected_id}: dialogue speaker {handle} missing from visible/declared cast")
        if not line.get("text"):
            raise SystemExit(f"{expected_id}: blank dialogue line")
        subtext = line.get("subtext", "")
        dialogue_lock = "exact approved revision dialogue" if number in REVISED_PAGE_NUMBERS else "exact source dialogue"
        if f"Panel " not in subtext or dialogue_lock not in subtext:
            raise SystemExit(f"{expected_id}: dialogue lacks exact panel/source lock: {line.get('text')}")
        try:
            panel_no = int(subtext.split("Panel ",1)[1].split(" ",1)[0])
        except Exception as exc:
            raise SystemExit(f"{expected_id}: cannot parse dialogue panel: {subtext}") from exc
        if not 1 <= panel_no <= panels:
            raise SystemExit(f"{expected_id}: dialogue panel out of range: {panel_no}")

    direction = [
        x.get("text", "") for x in page.get("directionInline", [])
        if isinstance(x, dict)
    ]
    if len(direction) != 6:
        raise SystemExit(f"{expected_id}: exactly six production locks are required")
    for got, prefix in zip(direction, DIR_PREFIXES):
        if not got.startswith(prefix):
            raise SystemExit(f"{expected_id}: direction schema mismatch; expected {prefix}")
    locked_action = direction[1].split(DIR_PREFIXES[1], 1)[1].strip()
    if locked_action != page.get("summary"):
        raise SystemExit(f"{expected_id}: PAGE ACTION must equal source-locked summary")
    if f"exactly {panels} panels" not in direction[5]:
        raise SystemExit(f"{expected_id}: exact panel-count lock missing")
    if "do not add, remove, merge, reorder, paraphrase or invent" not in direction[5].lower():
        raise SystemExit(f"{expected_id}: zero-drift lettering/layout guardrail missing")


# Pair-dynamics production pass: Pages 15-19 must break the ensemble into owned small groups,
# and Page 20 must deliberately reconverge the ensemble.
relationship_expected = {
    15: ("small-group", ["Jax / Glorp / Kreeb"]),
    16: ("small-group", ["Jax / Mira / Zib"]),
    17: ("small-group", ["Astra / Mira / Inspector"]),
    18: ("small-group", ["Astra / Mira / Pixa"]),
    19: ("split-small-groups", ["Astra / Glorp / Kreeb", "Jax / Noola / Brick"]),
    20: ("ensemble-reconvergence", ["Ensemble reconvergence after Pages 15–19 small-group sequence"]),
}
for number, (mode, focus) in relationship_expected.items():
    page = pages[number - 1]
    if page.get("relationshipMode") != mode:
        raise SystemExit(f"Page {number}: relationship mode drift")
    if page.get("relationshipFocus") != focus:
        raise SystemExit(f"Page {number}: relationship focus drift")
for number in (15, 16, 17, 18):
    cast = {c.get("handle") for c in pages[number - 1].get("charactersInline", []) if isinstance(c, dict)}
    if len(cast) != 3:
        raise SystemExit(f"Page {number}: small-group page must have exactly three declared characters")
page20_dialogue = " ".join(line.get("text", "") for line in pages[19].get("dialogueInline", [])).lower()
if "underfunded" in page20_dialogue:
    raise SystemExit("Page 20: stale underfunded framing returned")
if "overbuilt, under-noticed" not in page20_dialogue:
    raise SystemExit("Page 20: overbuilt/under-noticed series premise missing")

if sum(p["panelCount"] for p in pages) != 133:
    raise SystemExit("Issue 1 panel total drift")

for text in CRITICAL_TEXT:
    if text not in all_page_text:
        raise SystemExit(f"Missing source-locked critical text: {text}")

if "SDS_Kreeb" not in characters or characters["SDS_Kreeb"].get("name") != "Kreeb":
    raise SystemExit("Current Issue 1 Kreeb writing name drift")
if "unresolved" not in json.dumps(characters["SDS_Kreeb"], ensure_ascii=False).lower():
    raise SystemExit("Kreeb unresolved visual-identity warning missing")
if characters["SDS_Pixa"].get("name") != "Pixa":
    raise SystemExit("Current Issue 1 Pixa writing name drift")
if "white/blue" not in json.dumps(characters["SDS_Pixa"], ensure_ascii=False).lower():
    raise SystemExit("Pixa current visual reference missing")

print("Stardust Station validation passed")
print("Pages:", len(pages))
print("Panels:", sum(p["panelCount"] for p in pages))
print("Dialogue entries:", dialogue_count)
print("Canonical handles:", len(canonical_handles))
