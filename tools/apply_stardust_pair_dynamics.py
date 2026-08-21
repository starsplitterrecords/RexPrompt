#!/usr/bin/env python3
import base64
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data" / "shows" / "stardust-station"
REVISION_FILE = SHOW / "raw" / "pages_e01_p15_p20_pair_dynamics.json"
BUNDLES = [
    SHOW / "encoded" / "pages_e01_p13_p18.json.gzb64",
    SHOW / "encoded" / "pages_e01_p19_p22.json.gzb64",
]
VALIDATOR = ROOT / "tools" / "validate_stardust_station.py"
BASE_SOURCE = "Stardust Station — Issue 1 Full Script v4: Continuity-Compressed Draft"
REVISION_SOURCE = "Stardust Station — Issue 1 Pair-Dynamics Revision, approved 2026-08-21"


def decode_bundle(path):
    encoded = "".join(path.read_text(encoding="utf-8").split())
    encoded = encoded.rstrip("=")
    encoded += "=" * ((4 - len(encoded) % 4) % 4)
    return json.loads(gzip.decompress(base64.b64decode(encoded, validate=True)).decode("utf-8"))


def encode_bundle(path, data):
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    encoded = base64.b64encode(gzip.compress(payload, mtime=0)).decode("ascii")
    path.write_text(encoded + "\n", encoding="utf-8")


revisions = json.loads(REVISION_FILE.read_text(encoding="utf-8"))
revision_by_id = {page["id"]: page for page in revisions}
expected_ids = {f"SDS_S1E01_P{n:02d}" for n in range(15, 21)}
if set(revision_by_id) != expected_ids:
    raise SystemExit(f"Revision file must contain exactly Pages 15-20; got {sorted(revision_by_id)}")

replaced = set()
for bundle in BUNDLES:
    pages = decode_bundle(bundle)
    for i, page in enumerate(pages):
        replacement = revision_by_id.get(page.get("id"))
        if replacement is not None:
            pages[i] = replacement
            replaced.add(replacement["id"])
    encode_bundle(bundle, pages)

if replaced != expected_ids:
    raise SystemExit(f"Did not replace every revised page; replaced {sorted(replaced)}")

validator = VALIDATOR.read_text(encoding="utf-8")

if "REVISION_SOURCE =" not in validator:
    anchor = 'SHOW_ID = "stardust-station"\n'
    insert = anchor + f'BASE_SOURCE = {BASE_SOURCE!r}\nREVISION_SOURCE = {REVISION_SOURCE!r}\nREVISED_PAGE_NUMBERS = set(range(15, 21))\n\n'
    if anchor not in validator:
        raise SystemExit("Validator SHOW_ID anchor not found")
    validator = validator.replace(anchor, insert, 1)

old_source = '''    if page.get("source") != "Stardust Station — Issue 1 Full Script v4: Continuity-Compressed Draft":\n        raise SystemExit(f"{expected_id}: source authority drift")\n'''
new_source = '''    expected_source = REVISION_SOURCE if number in REVISED_PAGE_NUMBERS else BASE_SOURCE\n    if page.get("source") != expected_source:\n        raise SystemExit(f"{expected_id}: source authority drift")\n'''
if old_source in validator:
    validator = validator.replace(old_source, new_source, 1)
elif new_source not in validator:
    raise SystemExit("Validator source-lock block not found")

old_dialogue = '''        subtext = line.get("subtext", "")\n        if f"Panel " not in subtext or "exact source dialogue" not in subtext:\n            raise SystemExit(f"{expected_id}: dialogue lacks exact panel/source lock: {line.get('text')}")\n'''
new_dialogue = '''        subtext = line.get("subtext", "")\n        dialogue_lock = "exact approved revision dialogue" if number in REVISED_PAGE_NUMBERS else "exact source dialogue"\n        if f"Panel " not in subtext or dialogue_lock not in subtext:\n            raise SystemExit(f"{expected_id}: dialogue lacks exact panel/source lock: {line.get('text')}")\n'''
if old_dialogue in validator:
    validator = validator.replace(old_dialogue, new_dialogue, 1)
elif new_dialogue not in validator:
    raise SystemExit("Validator dialogue-lock block not found")

relationship_checks = '''\n# Pair-dynamics production pass: Pages 15-19 must break the ensemble into owned small groups,\n# and Page 20 must deliberately reconverge the ensemble.\nrelationship_expected = {\n    15: ("small-group", ["Jax / Glorp / Kreeb"]),\n    16: ("small-group", ["Jax / Mira / Zib"]),\n    17: ("small-group", ["Astra / Mira / Inspector"]),\n    18: ("small-group", ["Astra / Mira / Pixa"]),\n    19: ("split-small-groups", ["Astra / Glorp / Kreeb", "Jax / Noola / Brick"]),\n    20: ("ensemble-reconvergence", ["Ensemble reconvergence after Pages 15–19 small-group sequence"]),\n}\nfor number, (mode, focus) in relationship_expected.items():\n    page = pages[number - 1]\n    if page.get("relationshipMode") != mode:\n        raise SystemExit(f"Page {number}: relationship mode drift")\n    if page.get("relationshipFocus") != focus:\n        raise SystemExit(f"Page {number}: relationship focus drift")\nfor number in (15, 16, 17, 18):\n    cast = {c.get("handle") for c in pages[number - 1].get("charactersInline", []) if isinstance(c, dict)}\n    if len(cast) != 3:\n        raise SystemExit(f"Page {number}: small-group page must have exactly three declared characters")\npage20_dialogue = " ".join(line.get("text", "") for line in pages[19].get("dialogueInline", [])).lower()\nif "underfunded" in page20_dialogue:\n    raise SystemExit("Page 20: stale underfunded framing returned")\nif "overbuilt, under-noticed" not in page20_dialogue:\n    raise SystemExit("Page 20: overbuilt/under-noticed series premise missing")\n\n'''
anchor = 'if sum(p["panelCount"] for p in pages) != 133:\n'
if "relationship_expected =" not in validator:
    if anchor not in validator:
        raise SystemExit("Validator panel-total anchor not found")
    validator = validator.replace(anchor, relationship_checks + anchor, 1)

VALIDATOR.write_text(validator, encoding="utf-8")
print("Applied Stardust Station pair-dynamics revision to Pages 15-20")
