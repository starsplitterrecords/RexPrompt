#!/usr/bin/env python3
import base64
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data" / "shows" / "rex-fleet-s1"


def load_issue(n: int):
    if n in (2, 3):
        return json.loads((SHOW / f"pages_i{n:02d}.json").read_text())
    raw = (SHOW / "encoded" / f"pages_i{n:02d}.json.gzb64").read_text()
    return json.loads(gzip.decompress(base64.b64decode("".join(raw.split()))))


def chars(page):
    return [c.get("name") or c.get("handle") for c in page.get("charactersInline", [])]


def speakers(page):
    return [d.get("speaker") or d.get("handle") for d in page.get("dialogueInline", [])]

for issue in range(2, 13):
    pages = load_issue(issue)
    print(f"\n===== REX FLEET ISSUE {issue:02d} ({len(pages)} pages) =====")
    for p in pages:
        print(f"{p.get('id')} | {p.get('settingText','')} | {p.get('summary','')}")
        print("  CAST:", ", ".join(chars(p)))
        print("  SPEAKERS:", ", ".join(speakers(p)))

selected = {
    4: None,
    6: None,
    10: {"RF_I10_P03", "RF_I10_P11", "RF_I10_P13", "RF_I10_P16", "RF_I10_P23", "RF_I10_P26", "RF_I10_P28", "RF_I10_P29", "RF_I10_P30"},
    12: {"RF_I12_P04", "RF_I12_P05", "RF_I12_P07", "RF_I12_P08", "RF_I12_P15", "RF_I12_P17", "RF_I12_P18", "RF_I12_P20", "RF_I12_P21"},
}

for issue, wanted in selected.items():
    print(f"\n===== FULL CANDIDATE JSON ISSUE {issue:02d} =====")
    for page in load_issue(issue):
        if wanted is None or page.get("id") in wanted:
            print(json.dumps(page, ensure_ascii=False, indent=2))
