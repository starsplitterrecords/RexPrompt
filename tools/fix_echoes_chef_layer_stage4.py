#!/usr/bin/env python3
"""Final Echoes chef-layer polish and durable validator guard correction."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data" / "shows" / "echoes-forgotten-war-s1"
VALIDATOR = ROOT / "tools" / "validate_echoes.py"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def set_panel(path: Path, scene_id: str, panel_number: int, text: str) -> None:
    records = load(path)
    scene = next(item for item in records if item.get("id") == scene_id)
    scene["panelPlan"][panel_number - 1]["text"] = text
    dump(path, records)


set_panel(
    SHOW / "scenes_e02.json", "EFW_S1E02_S09", 3,
    "Panel 3 — Tight on Starbreaker, exhausted and afraid: 'I know.' Around his forward hand, first-light forms as several fractured planes and branching ribbons of white-gold stellar radiance with dark gaps between them; there is no single continuous beam shape."
)
set_panel(
    SHOW / "scenes_e04.json", "EFW_S1E04_S07", 2,
    "Panel 2 — Mero steps close to Arbiter and lowers his voice: 'Can you live with it?' His command posture is gone; one hand rests heavily on the table, fingers spread, while he waits at eye level for her face to answer."
)
set_panel(
    SHOW / "scenes_e04.json", "EFW_S1E04_S11", 2,
    "Panel 2 — Rae keeps her eyes fixed on the empty chair: 'Arbiter crossed out the first line.' Theo watches Rae's face and asks, 'What line?' Keep the panel entirely in the present-day vault with no flashback image."
)
set_panel(
    SHOW / "scenes_e05.json", "EFW_S1E05_S11", 3,
    "Panel 3 — Mero: 'That's why I kept you.' Theo looks up: 'Because I'm scared?' Theo gives a small crooked smile; one corner of Mero's mouth briefly lifts before he looks back toward the war-room door."
)
set_panel(
    SHOW / "enhance_e07.json", "EFW_S1E07_S08", 1,
    "Panel 1 — Ancient Mero staff room during Neo-Vectra. Senior voices argue behind a closed door. Mero closes the inner office door, pulls a plain chair beside junior Theo and sits at the same level, leaving the formal command table empty in the background."
)
set_panel(
    SHOW / "enhance_e06.json", "EFW_S1E06_S01", 3,
    "Panel 3 — Rae asks, 'You're sure?' Theo answers, 'The clasp sticks on the left.' His hand is already held in the old opening grip beside the display case, thumb angled toward the left-side clasp; he notices his own hand and goes still."
)

text = VALIDATOR.read_text(encoding="utf-8")
old = 'r"\\bthe page(?:\'s)?\\b",'
new = 'r"\\bthe page\'s\\b",'
if old not in text:
    raise RuntimeError("Expected broad page-analysis regex not found in Echoes validator")
VALIDATOR.write_text(text.replace(old, new, 1), encoding="utf-8")

print("Echoes final chef-layer polish applied")
print("Narrowed validator page-analysis guard so physical pages/paper remain drawable nouns")
