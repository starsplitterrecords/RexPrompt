#!/usr/bin/env python3
import base64
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data" / "shows" / "azure-reach-s1"
MANIFEST = ROOT / "data" / "shows.json"

SHOW_IDS = {
    1: "azure-reach-s1",
    2: "azure-reach-s1-e02",
    3: "azure-reach-s1-e03",
    4: "azure-reach-s1-e04",
    5: "azure-reach-s1-e05",
    6: "azure-reach-s1-e06",
}
EXPECTED = {
    1: (22, 136, 303),
    2: (22, 127, 164),
    3: (22, 116, 146),
    4: (22, 117, 149),
    5: (22, 113, 160),
    6: (22, 117, 170),
}
DIR_PREFIXES = (
    "AZURE REACH VISUAL LANGUAGE:",
    "PAGE ACTION — SOURCE-LOCKED:",
    "CHARACTER CONTINUITY —",
    "LOCATION / PROP / STATE CONTINUITY —",
    "COMIC PAGE / LETTERING —",
)
FORBIDDEN = (
    "The Pelican Drop",
    "retrieval rings",
    "Julian Vale",
    "Flora Fontaine",
    "Pip Hart",
    "Pippa Hart",
    "@arv1.",
    "@starsplit.",
)
HANDOFFS = {
    3: ("Make the person exclusive, not the water.", "Feeding Stream Live."),
    4: ("They are not late. We are.", "Scale the interpretation. Do not schedule miracles."),
    5: ("Fifty thousand verified actions in seven days.", "Eighteen thousand four hundred twelve.", "The gala deck is tomorrow."),
    6: ("We can replicate the process.", "The public sees the moment. The work is everything that lets the moment happen.", "Make it invisible."),
}

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def decode_overlay(path):
    raw = "".join(path.read_text(encoding="utf-8").split())
    return json.loads(gzip.decompress(base64.b64decode(raw, validate=True)).decode("utf-8"))

manifest = load(MANIFEST)
by_id = {s.get("id"): s for s in manifest}
characters = load(SHOW / "characters.json")
factions = load(SHOW / "factions.json")
regions = load(SHOW / "regions.json")
settings = load(SHOW / "settings.json")
canonical_handles = {
    v.get("handle")
    for v in characters.values()
    if isinstance(v, dict) and v.get("handle")
}

season_pages = []

for issue in range(1, 7):
    show_id = SHOW_IDS[issue]
    entry = by_id.get(show_id)
    assert entry, f"Missing manifest entry: {show_id}"
    assert entry.get("basePath") == "data/shows/azure-reach-s1"
    assert entry.get("scenesFile") == "pages_base.json"
    assert entry.get("unitLabel") == "PAGE"
    assert "comic page" in entry.get("generationLine", "").lower()

    pages = []
    for overlay in entry.get("sceneOverlays", []):
        assert overlay.get("encoding") == "gzip-base64", (show_id, overlay)
        path = SHOW / overlay["file"]
        assert path.exists(), f"Missing overlay: {path}"
        pages.extend(decode_overlay(path))

    expected_pages, expected_panels, expected_letters = EXPECTED[issue]
    assert len(pages) == expected_pages, (issue, len(pages))
    assert [p.get("id") for p in pages] == [
        f"AZR_S1E{issue:02d}_P{i:02d}" for i in range(1, 23)
    ]
    assert [p.get("page") for p in pages] == list(range(1, 23))
    assert all(p.get("episode") == f"S1E{issue:02d}" for p in pages)

    issue_panels = 0
    issue_letters = 0
    for page in pages:
        page_id = page["id"]
        assert page.get("summary"), f"{page_id}: missing summary"
        assert page.get("setting") in settings, f"{page_id}: unknown setting"
        assert page.get("region") in regions, f"{page_id}: unknown region"
        for faction in page.get("factions", []):
            assert faction in factions, f"{page_id}: unknown faction {faction}"

        panel_count = page.get("panelCount")
        assert len(page.get("panelPlan", [])) == panel_count, f"{page_id}: panelPlan mismatch"
        issue_panels += panel_count

        cast_handles = {
            c.get("handle")
            for c in page.get("charactersInline", [])
            if isinstance(c, dict) and c.get("handle")
        }
        assert cast_handles, f"{page_id}: no cast"
        assert not (cast_handles - canonical_handles), f"{page_id}: noncanonical cast"

        lines = page.get("dialogueInline", [])
        assert lines, f"{page_id}: no lettering"
        issue_letters += len(lines)
        for line in lines:
            handle = line.get("handle")
            assert line.get("text"), f"{page_id}: blank lettering"
            assert handle in canonical_handles, f"{page_id}: noncanonical speaker {handle}"
            if handle != "@azr.Comments":
                assert handle in cast_handles, f"{page_id}: speaker not in cast {handle}"

        direction = [
            x.get("text", "")
            for x in page.get("directionInline", [])
            if isinstance(x, dict)
        ]
        assert len(direction) == 5, f"{page_id}: production lock count"
        for text, prefix in zip(direction, DIR_PREFIXES):
            assert text.startswith(prefix), f"{page_id}: production lock schema {prefix}"
        locked_action = direction[1].split(DIR_PREFIXES[1], 1)[1].strip()
        assert locked_action == page["summary"], f"{page_id}: summary/action drift"
        safety = direction[0].lower()
        assert "animal" in safety and any(word in safety for word in ("safe", "welfare", "voluntary", "calm", "care")), f"{page_id}: animal safety lock"
        assert "professional" in direction[4].lower() and "letter" in direction[4].lower(), f"{page_id}: lettering lock"

    assert issue_panels == expected_panels, (issue, issue_panels, expected_panels)
    assert issue_letters == expected_letters, (issue, issue_letters, expected_letters)

    issue_text = json.dumps(pages, ensure_ascii=False)
    for forbidden in FORBIDDEN:
        assert forbidden not in issue_text, f"Issue {issue}: forbidden residue {forbidden}"
    for required in HANDOFFS.get(issue, ()):
        assert required in issue_text, f"Issue {issue}: missing continuity handoff {required}"

    season_pages.extend(pages)
    print(f"Issue {issue}: 22 pages / {issue_panels} panels / {issue_letters} lettering entries")

assert len(season_pages) == 132
assert sum(p["panelCount"] for p in season_pages) == 726
assert sum(len(p["dialogueInline"]) for p in season_pages) == 1092

plan = load(SHOW / "season_one_plan.json")
assert plan.get("status") == "season one production scripts complete"
assert len(plan.get("issues", [])) == 6
assert all("script" in item.get("status", "") for item in plan["issues"])
assert plan.get("continuity", {}).get("animals") == "never endangered and never the joke"

print("Azure Reach Season One validation passed")
print("Season: 132 pages / 726 panels / 1092 dialogue-lettering entries")
