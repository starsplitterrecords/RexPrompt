#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "data" / "shows" / "vikings-2026-s1"

# Issue 6 JSON: preserve the spine, update only status + pointer to the full script.
p6 = ROOT / "issue_06_trial_of_toil_development.json"
data = json.loads(p6.read_text(encoding="utf-8"))
data["status"] = "full-script-drafted-production-review-pending"
data["scriptFile"] = "issue_06_trial_of_toil_script.md"
p6.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# Issues 7-8 treatments remain useful as development history but no longer describe current script status.
for filename, script in [
    ("issue_07_war_council_treatment.md", "issue_07_war_council_script.md"),
    ("issue_08_trial_by_combat_treatment.md", "issue_08_trial_by_combat_script.md"),
]:
    path = ROOT / filename
    text = path.read_text(encoding="utf-8")
    old = "Status: ENHANCED TREATMENT — 24-PAGE DRAMATIC SPINE LOCKED; PANEL/DIALOGUE PASS PENDING  "
    if old not in text:
        raise SystemExit(f"Expected status line missing: {filename}")
    new = f"Status: ENHANCED TREATMENT — SUPERSEDED FOR CURRENT WRITING BY FULL 24-PAGE DEVELOPMENT SCRIPT `{script}`  "
    text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")

print("Synchronized Issues 6-8 development status pointers")
