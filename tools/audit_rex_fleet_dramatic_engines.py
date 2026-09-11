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
