#!/usr/bin/env python3
import base64
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data" / "shows" / "rex-fleet-s1" / "encoded" / "pages_i04.json.gzb64"

raw = "".join(PATH.read_text().split())
pages = json.loads(gzip.decompress(base64.b64decode(raw)))
page = next((p for p in pages if p.get("id") == "RF_I04_P28"), None)
if page is None:
    raise SystemExit("RF_I04_P28 not found")

expected = [
    {"name": "Abby Saville", "handle": "@starsplit.abby.saville"},
    {"name": "Oren Pike", "handle": "@starsplit.oren.pike"},
]
current = page.get("charactersInline") or []
by_handle = {c.get("handle"): c for c in current if isinstance(c, dict) and c.get("handle")}
for char in expected:
    by_handle[char["handle"]] = char

# Keep any existing character entries first, then append only missing canonical refs.
seen = set()
merged = []
for char in current + expected:
    if not isinstance(char, dict):
        merged.append(char)
        continue
    handle = char.get("handle")
    if handle and handle in seen:
        continue
    if handle:
        seen.add(handle)
        merged.append(by_handle[handle])
    else:
        merged.append(char)
page["charactersInline"] = merged

payload = (json.dumps(pages, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
PATH.write_text(base64.b64encode(gzip.compress(payload, mtime=0)).decode("ascii") + "\n")

print(json.dumps({"id": page["id"], "charactersInline": page["charactersInline"]}, ensure_ascii=False, indent=2))
