#!/usr/bin/env python3
import base64
import gzip
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data" / "shows" / "rex-fleet-s1"
MANIFEST = ROOT / "data" / "shows.json"
INDEX = ROOT / "index.html"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_payload(entry):
    overlay = entry.get("sceneOverlays", [None])[0]
    if not overlay:
        raise SystemExit(f"{entry.get('id')}: normalized issue payload missing")
    path = SHOW / overlay["file"]
    if overlay.get("encoding") == "gzip-base64":
        text = "".join(path.read_text(encoding="utf-8").split())
        raw = base64.b64decode(text, validate=True)
        return json.loads(gzip.decompress(raw).decode("utf-8"))
    return load_json(path)


def assert_clean_recipe(page, all_ids):
    page_id = page.get("id")
    if not page_id:
        raise SystemExit("Rex Fleet page missing id")
    for field in ("episode", "act"):
        if field in page:
            raise SystemExit(f"{page_id}: legacy {field} field survived comic normalization")
    if not page.get("summary"):
        raise SystemExit(f"{page_id}: missing summary")
    if not (page.get("settingText") or page.get("setting")):
        raise SystemExit(f"{page_id}: missing setting")
    if not (page.get("regionText") or page.get("region")):
        raise SystemExit(f"{page_id}: missing region")
    if len(page.get("panelPlan", [])) < 1:
        raise SystemExit(f"{page_id}: comic page needs a complete panel plan")
    target = page.get("continuityFrom")
    if target and target not in all_ids:
        raise SystemExit(f"{page_id}: continuity target does not resolve: {target}")
    for item in page.get("directionInline", []):
        if isinstance(item, str) and item.startswith(("Canon anchors", "Characters:", "Tone:", "Season 2 hooks:", "Visual tone guidance:")):
            raise SystemExit(f"{page_id}: editorial/correction residue survived")


shows = load_json(MANIFEST)
rex = [entry for entry in shows if entry.get("seriesId") == "rex-fleet" or entry.get("id") == "rex-fleet-s1"]
if len(rex) != 11:
    raise SystemExit(f"Expected 11 explicit Rex Fleet issue entries (2-12), found {len(rex)}")
if any(entry.get("id") == "rex-fleet-s1" for entry in rex):
    raise SystemExit("Legacy Rex Fleet season manifest entry remains")

issues = {}
for expected_issue, entry in zip(range(2, 13), rex):
    if entry.get("id") != f"rex-fleet-i{expected_issue:02d}":
        raise SystemExit(f"Rex Fleet issue order/id mismatch at Issue {expected_issue}: {entry.get('id')}")
    if entry.get("name") != f"Rex Fleet — Issue {expected_issue}":
        raise SystemExit(f"Issue {expected_issue}: comic-first display name mismatch")
    if entry.get("issueLabel") != f"Issue {expected_issue}":
        raise SystemExit(f"Issue {expected_issue}: issue label mismatch")
    if entry.get("unitLabel") != "PAGE":
        raise SystemExit(f"Issue {expected_issue}: production unit must be PAGE")
    if entry.get("scenesFile") != "pages_base.json":
        raise SystemExit(f"Issue {expected_issue}: normalized page base missing")
    manifest_text = json.dumps(entry, ensure_ascii=False)
    if "replaceEpisode" in manifest_text or "replaceEpisodes" in manifest_text:
        raise SystemExit(f"Issue {expected_issue}: episode replacement machinery survived")
    if re.search(r"\bSeason\b|\bepisode\b", entry.get("name", "") + " " + entry.get("generationLine", ""), re.I):
        raise SystemExit(f"Issue {expected_issue}: show/episode language survived user-facing production config")
    if "comic page" not in entry.get("generationLine", ""):
        raise SystemExit(f"Issue {expected_issue}: comic-page production mode missing")
    issues[expected_issue] = load_payload(entry)

if load_json(SHOW / "pages_base.json") != []:
    raise SystemExit("Rex Fleet pages_base.json must remain an empty structural base")

all_ids = {page.get("id") for pages in issues.values() for page in pages}
if None in all_ids:
    raise SystemExit("One or more normalized pages are missing IDs")
if len(all_ids) != sum(len(pages) for pages in issues.values()):
    raise SystemExit("Duplicate normalized Rex Fleet page IDs")

for issue, pages in issues.items():
    expected_ids = [f"RF_I{issue:02d}_P{n:02d}" for n in range(1, len(pages) + 1)]
    ids = [page.get("id") for page in pages]
    if ids != expected_ids:
        raise SystemExit(f"Issue {issue}: page IDs/order invalid: {ids}")
    for page in pages:
        assert_clean_recipe(page, all_ids)

if len(issues[2]) != 19:
    raise SystemExit(f"Issue 2 must contain 19 production pages, found {len(issues[2])}")
if len(issues[3]) != 30:
    raise SystemExit(f"Issue 3 must contain 30 production pages, found {len(issues[3])}")

serialized = json.dumps(issues, ensure_ascii=False)
if "RF_S1E" in serialized:
    raise SystemExit("Legacy episode-style recipe ID remains in active page payloads")
for retired in (
    "Ilyra Venn", "Varra Cindral", "Elyra Vorn", "Sira Red Fang", "Nira Sol",
    "Elder Branth", "Mara Vey", "Ilan Vey", "Ilyan Vey",
    "@starsplit.mara.vey", "@starsplit.ilan.vey", "C_mara_vey", "C_ilan_vey",
):
    if retired.lower() in serialized.lower():
        raise SystemExit(f"Retired Rex Fleet identity remains: {retired}")
if re.search(r"\bVey\b", serialized, re.I):
    raise SystemExit("Unresolved Vey identity residue remains")

characters = load_json(SHOW / "characters.json")
for forbidden_id in (
    "C_mara_vey", "C_ilan_vey", "C_mother_soft", "C_venn_soft_to_herself",
    "C_jex_low", "C_billie_low", "C_tess_vo", "C_kerr_cerulean",
    "C_triarch_voice", "C_rhyne_aegis", "C_keating_ember",
):
    if forbidden_id in characters:
        raise SystemExit(f"Retired/correction identity record remains: {forbidden_id}")
handles = [entry.get("handle") for entry in characters.values() if entry.get("handle")]
if len(handles) != len(set(handles)):
    raise SystemExit("Duplicate primary Rex Fleet handles remain")
for required_id in (
    "C_commodore_ella_venn", "C_abby_saville", "C_tessa_banks", "C_billie_rusk",
    "C_governor_halev", "C_captain_naomi_sol", "C_jex_marrin",
    "C_richard_secundo", "C_paul_secundo",
):
    if required_id not in characters:
        raise SystemExit(f"Required current identity missing: {required_id}")
    if not characters[required_id].get("visualAnchor"):
        raise SystemExit(f"Canonical/current visual anchor missing: {required_id}")


primary={e.get("handle"):e for e in characters.values() if isinstance(e,dict) and e.get("handle")}
aliases={}
for e in characters.values():
    if isinstance(e,dict):
        for a in e.get("aliases",[]) or []: aliases[a]=e
for page in [p for issue_pages in issues.values() for p in issue_pages]:
    for c in page.get("charactersInline",[]) or []:
        if not isinstance(c,dict) or not c.get("handle"): continue
        e=primary.get(c["handle"]) or aliases.get(c["handle"])
        if not e: raise SystemExit(f"{page.get('id')}: unresolved character handle {c['handle']}")
        if not (e.get("visualAnchor") or e.get("visual") or e.get("appearance") or e.get("visualDescription")): raise SystemExit(f"{page.get('id')}: image-visible character lacks visual anchor {c['handle']}")
    for d in page.get("dialogueInline",[]) or []:
        if not isinstance(d,dict): continue
        h=d.get("handle")
        if h and h.startswith("@") and not (primary.get(h) or aliases.get(h)): raise SystemExit(f"{page.get('id')}: unresolved dialogue character handle {h}")
pack=ROOT/"production/references/rex-fleet/visual-reference-pack.json"
if not pack.exists(): raise SystemExit("Rex Fleet visual reference pack missing")
vp=load_json(pack)
if vp.get("seriesId")!="rex-fleet" or len(vp.get("references",[]))!=18: raise SystemExit("Rex Fleet released visual reference pack incomplete")
if any(r.get("image","").endswith("page-001.jpg") for r in vp.get("references",[])): raise SystemExit("Editorial page leaked into story visual references")

character_serialized = json.dumps(characters, ensure_ascii=False)
for residue in (
    "Production reference:", "Source speaker label:", "visualStatus", "continuityLocks",
    "formerly developed under", "Do not transfer", "not the redhead", "duplicate bodies",
    "exaggerated villain poses",
):
    if residue in character_serialized:
        raise SystemExit(f"Character correction/source residue remains: {residue}")

for old_path in list(SHOW.glob("scenes_e*.json")) + list((SHOW / "encoded").glob("scenes_e*.json.gzb64")):
    raise SystemExit(f"Legacy scene/episode payload remains active: {old_path.relative_to(ROOT)}")
if (SHOW / "scenes_prequel.json").exists():
    raise SystemExit("Legacy Rex Fleet prequel/episode payload remains active")

index_text = INDEX.read_text(encoding="utf-8")
if "Series (show)" in index_text or "Scene / page (recipes)" in index_text:
    raise SystemExit("Legacy show/scene language remains in RexPrompt production selector")
for required in ("function findCharacterByHandle", "function formatCharacter", "e.wardrobe", "e.performance", "e.relationship", "s.continuityFrom"):
    if required not in index_text:
        raise SystemExit(f"Assembler continuity support missing: {required}")

print("Rex Fleet comic normalization validation passed")
print("Production model: series -> issue -> page -> panel")
for issue in range(2, 13):
    print(f"Issue {issue}: {len(issues[issue])} pages")
