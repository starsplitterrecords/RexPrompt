#!/usr/bin/env python3
import base64
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data" / "shows" / "rex-fleet-s1"
SHOWS = json.loads((ROOT / "data" / "shows.json").read_text())
GENERATION = {int(s["issueLabel"].split()[-1]): s["generationLine"] for s in SHOWS if s.get("seriesId") == "rex-fleet"}


def load_issue(n):
    if n in (2, 3):
        return json.loads((SHOW / f"pages_i{n:02d}.json").read_text())
    raw = "".join((SHOW / "encoded" / f"pages_i{n:02d}.json.gzb64").read_text().split())
    return json.loads(gzip.decompress(base64.b64decode(raw)))


def assemble(page, issue):
    out = []
    for d in page.get("dialogueInline", []):
        h = d.get("handle") or d.get("speaker")
        if isinstance(h, str) and h.startswith("@") and h not in out:
            out.append(h)
    out.extend([f"\n=== PAGE: {page['id']} ===", page.get("summary", ""), GENERATION[issue]])
    if page.get("settingText"):
        out.extend(["\n[SETTING]", page["settingText"]])
    if page.get("regionText"):
        out.extend(["\n[REGION]", page["regionText"]])
    if page.get("charactersInline"):
        out.append("\n[CHARACTERS]")
        out.extend(c.get("handle") or c.get("name", "") for c in page["charactersInline"])
    if page.get("panelPlan"):
        out.append("\n[PANEL PLAN]")
        out.extend(page["panelPlan"])
    if page.get("dialogueInline"):
        out.append("\n[DIALOGUE]")
        for d in page["dialogueInline"]:
            sp = d.get("handle") or d.get("speaker") or "TEXT"
            out.append(f'{sp} says "{d.get("text", "")}"')
            if d.get("subtext"):
                out.append(f'  ({d["subtext"]})')
    if page.get("continuityFrom"):
        out.extend(["\n[CONTINUITY]", f"Continue directly from {page['continuityFrom']}; preserve established positions, props, damage, eyelines, and emotional state."])
    if page.get("directionInline"):
        out.append("\n[DIRECTION]")
        out.extend(page["directionInline"])
    return "\n".join(out).strip()

# Full-season reread at the summary level: enough to expose repeated engine drift.
for issue in range(2, 13):
    pages = load_issue(issue)
    print(f"\n===== ISSUE {issue:02d} — {len(pages)} PAGES =====")
    for page in pages:
        print(f"{page['id']}: {page.get('summary','')}")

# Exact chef-facing material for every substantively changed dramatic hinge.
review = {
    4: ["RF_I04_P06", "RF_I04_P15", "RF_I04_P22", "RF_I04_P28", "RF_I04_P31"],
    6: ["RF_I06_P05", "RF_I06_P06", "RF_I06_P07", "RF_I06_P12", "RF_I06_P13", "RF_I06_P14"],
    10: ["RF_I10_P23", "RF_I10_P26"],
    12: ["RF_I12_P20", "RF_I12_P21"],
}
for issue, ids in review.items():
    by_id = {p["id"]: p for p in load_issue(issue)}
    print(f"\n===== ASSEMBLED REVIEW ISSUE {issue:02d} =====")
    for page_id in ids:
        if page_id not in by_id:
            raise RuntimeError(f"missing review page {page_id}")
        print("\n" + assemble(by_id[page_id], issue))

print("\nRex Fleet dramatic-divergence reread complete")
