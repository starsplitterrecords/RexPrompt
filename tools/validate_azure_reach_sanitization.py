#!/usr/bin/env python3
import base64
import gzip
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data" / "shows" / "azure-reach-s1"
INDEX = ROOT / "index.html"

LEGACY_PREFIXES = (
    "AZURE REACH VISUAL LANGUAGE:",
    "PAGE ACTION — SOURCE-LOCKED:",
    "CHARACTER CONTINUITY —",
    "LOCATION / PROP / STATE CONTINUITY —",
    "COMIC PAGE / LETTERING —",
)
REQUIRED_DIRECTION = {
    "AZR_PRODUCTION_CORE",
    "AZR_LETTERING",
    "AZR_VIS_BRINE",
    "AZR_VIS_GUEST_RELATIONS",
    "AZR_VIS_FINFLUENCERS",
    "AZR_VIS_CORPORATE",
    "AZR_VIS_MAYA_PIP_SEPARATION",
    "AZR_E02_CONTINUITY",
}
FACTION_DIRECTION = {
    "AZR_BrineSquad": "AZR_VIS_BRINE",
    "AZR_GuestRelations": "AZR_VIS_GUEST_RELATIONS",
    "AZR_Finfluencers": "AZR_VIS_FINFLUENCERS",
    "AZR_Corporate": "AZR_VIS_CORPORATE",
}
STALE = (
    "The Pelican Drop",
    "retrieval rings",
    "Julian Vale",
    "Flora Fontaine",
    "Pip Hart",
    "Pippa Hart",
    "@arv1.",
    "@starsplit.",
)
EXPECTED = {
    1: (22, 136, 303),
    2: (22, 127, 164),
    3: (22, 116, 146),
    4: (22, 117, 149),
    5: (22, 113, 160),
    6: (22, 117, 170),
}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def decode(path):
    raw = "".join(path.read_text(encoding="utf-8").split())
    return json.loads(gzip.decompress(base64.b64decode(raw, validate=True)).decode("utf-8"))


registry = load(SHOW / "direction.json")
missing = REQUIRED_DIRECTION - set(registry)
assert not missing, f"Missing persistent direction refs: {sorted(missing)}"
issue_keys = {k for k in registry if re.fullmatch(r"AZR_E\d{2}_CONTINUITY", k)}
assert issue_keys == {"AZR_E02_CONTINUITY"}, f"Unapproved issue-level production doctrine: {sorted(issue_keys)}"

pages = []
for path in sorted((SHOW / "encoded").glob("pages_e*.json.gzb64")):
    pages.extend(decode(path))
assert len(pages) == 132, len(pages)

by_issue = {i: [] for i in range(1, 7)}
for page in pages:
    issue = int(page["episode"][-2:])
    by_issue[issue].append(page)

for issue, issue_pages in by_issue.items():
    expected_pages, expected_panels, expected_letters = EXPECTED[issue]
    assert len(issue_pages) == expected_pages, (issue, len(issue_pages))
    assert sum(p["panelCount"] for p in issue_pages) == expected_panels, issue
    assert sum(len(p.get("dialogueInline", [])) for p in issue_pages) == expected_letters, issue

all_text = json.dumps(pages, ensure_ascii=False)
for stale in STALE:
    assert stale not in all_text, f"Stale Azure Reach production residue: {stale}"

local_count = 0
for page in pages:
    pid = page["id"]
    refs = page.get("direction", [])
    assert refs, f"{pid}: missing persistent direction references"
    assert "AZR_PRODUCTION_CORE" in refs, f"{pid}: missing show production core"
    assert "AZR_LETTERING" in refs, f"{pid}: missing lettering rules"
    assert len(refs) == len(set(refs)), f"{pid}: duplicate direction refs"
    unknown = set(refs) - set(registry)
    assert not unknown, f"{pid}: unknown direction refs {sorted(unknown)}"

    for faction in page.get("factions", []):
        expected = FACTION_DIRECTION.get(faction)
        if expected:
            assert expected in refs, f"{pid}: missing faction visual ref {expected}"

    handles = {
        c.get("handle") for c in page.get("charactersInline", [])
        if isinstance(c, dict) and c.get("handle")
    }
    if handles & {"@azr.Maya", "@azr.Pip"}:
        assert "AZR_VIS_MAYA_PIP_SEPARATION" in refs, f"{pid}: missing Maya/Pip separation rule"

    if page["episode"] == "S1E02":
        assert "AZR_E02_CONTINUITY" in refs, f"{pid}: missing approved Issue 2 continuity"
    else:
        assert not any(re.fullmatch(r"AZR_E\d{2}_CONTINUITY", r) for r in refs), f"{pid}: unapproved issue-level doctrine"

    local = page.get("directionInline", []) or []
    assert len(local) <= 2, f"{pid}: too much page-scope production scaffolding ({len(local)})"
    local_count += len(local)
    local_text = json.dumps(local, ensure_ascii=False)
    assert page.get("summary", "") not in local_text, f"{pid}: summary duplicated into direction"
    for item in local:
        text = item.get("text", "") if isinstance(item, dict) else str(item)
        assert text.startswith(("PAGE CONTINUITY —", "PAGE DESIGN —")), f"{pid}: unscoped local direction"
        assert not text.startswith(LEGACY_PREFIXES), f"{pid}: legacy direction prefix remains"

characters = load(SHOW / "characters.json")
assert characters["AZR_Julian"]["name"] == "Julian Heatherington"
assert characters["AZR_Fleur"]["name"] == "Fleur Fontaine"
assert characters["AZR_Pip"]["name"] == "Pip O'Mally"
assert characters["AZR_Maya"]["name"] == "Maya Serrano"

negatives = json.dumps(load(SHOW / "negatives.json"), ensure_ascii=False).lower()
for required in ("animal danger", "incompetence comedy", "grime", "manual-repair", "maya/pip visual merging"):
    assert required in negatives, f"Missing durable negative rule: {required}"

index = INDEX.read_text(encoding="utf-8")
assert 'if(s.direction?.length||s.directionInline?.length){out.push("\\n[DIRECTION]")' in index, "Assembler must combine persistent and local direction"

print("Azure Reach sanitization validation passed")
print("Pages:", len(pages))
print("Panels:", sum(p["panelCount"] for p in pages))
print("Dialogue/lettering entries:", sum(len(p["dialogueInline"]) for p in pages))
print("Page-local direction entries:", local_count)
print("Persistent direction entries:", len(registry))
