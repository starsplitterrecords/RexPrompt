#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "data" / "shows" / "vikings-2026-s1"
replacements = {
    "issue_06_trial_of_toil_script.md": [
        ("**GROUP FACILITATOR:** Small things are where people live.", "**GROUP FACILITATOR:** Most of life is small.")
    ],
    "issue_07_war_council_script.md": [
        ("**CARRIE:** Right. A perfect case could still be the wrong life.", "**CARRIE:** Right. The file can be perfect and still get the person wrong.")
    ],
    "issue_08_trial_by_combat_script.md": [
        ("**BJORN:** I do not choose another person's road because I am strong enough to block it.", "**BJORN:** Strength does not make another person's road mine.")
    ],
}

for filename, pairs in replacements.items():
    path = ROOT / filename
    text = path.read_text(encoding="utf-8")
    for old, new in pairs:
        if old not in text:
            raise SystemExit(f"Expected text missing in {filename}: {old}")
        text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")
    print(f"polished {filename}")
