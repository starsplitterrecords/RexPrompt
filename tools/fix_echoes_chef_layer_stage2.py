#!/usr/bin/env python3
"""Second-stage Echoes chef-layer cleanup plus broader editorial-leak review."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data" / "shows" / "echoes-forgotten-war-s1"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def set_panel(path: Path, scene_id: str, panel_number: int, text: str) -> None:
    records = load(path)
    scene = next(item for item in records if item.get("id") == scene_id)
    scene["panelPlan"][panel_number - 1]["text"] = text
    dump(path, records)


assembler_path = SHOW / "assembler.json"
assembler = load(assembler_path)
assembler["generationLine"] = assembler["generationLine"].replace(
    "Use varied panel sizes when the page plan supports it,",
    "Use varied panel sizes when supported by the selected panel architecture,",
)
dump(assembler_path, assembler)

set_panel(
    SHOW / "scenes_e02.json", "EFW_S1E02_S01", 4,
    "Panel 4 — Theo turns fully toward Adrian: 'Then tell us which one happened.' Adrian answers, 'They both did.' Rae stops sorting the notes and looks directly at Adrian; he meets her eyes without softening the answer."
)

# Correct the one accidental cast substitution introduced during the first migration.
set_panel(
    SHOW / "scenes_e04.json", "EFW_S1E04_S02", 5,
    "Panel 5 — Mero: 'So am I. That's why I'm grateful for the easy part.' End in a wide panel with Mero, Atlas and Redlin together at the overlook while an evacuation ship lifts away below them, its light crossing all three faces."
)
set_panel(
    SHOW / "scenes_e04.json", "EFW_S1E04_S08", 3,
    "Panel 3 — Redlin clears fallen material from the route and says, 'For once, nobody argue with Atlas.' Atlas immediately takes the opened side of the transport while Starbreaker braces the opposite frame; all three work on the same damaged vehicle."
)
set_panel(
    SHOW / "scenes_e04.json", "EFW_S1E04_S12", 3,
    "Panel 3 — Adrian faces Rae across the black table: 'You sat beside Arbiter.' Rae says, 'No.' Adrian answers, 'You recorded the rulings.' Hold on present-day Rae as her grip tightens on the chair back and she stops breathing for a beat."
)

set_panel(
    SHOW / "scenes_e05.json", "EFW_S1E05_S01", 4,
    "Panel 4 — Theo: 'Prove it.' Adrian: 'I can't.' Rae: 'Convenient.' Adrian stays seated, both hands open on his knees, and holds eye contact with Theo while Rae watches from the opposite side."
)
set_panel(
    SHOW / "scenes_e05.json", "EFW_S1E05_S04", 1,
    "Panel 1 — Repeat the established post-decision composition: Arbiter alone at the black Pax-Aeterna table after the others leave, same camera height, same chair placement, same light direction and same cropped empty space at frame right."
)

set_panel(
    SHOW / "enhance_e07.json", "EFW_S1E07_S09", 4,
    "Panel 4 — Theo stands in the plaza and watches two opposite reactions at once: one pair of strangers embraces after recognition while another person steps backward from someone reaching toward them. Keep both pairs visible behind Theo in the same wide frame."
)
set_panel(
    SHOW / "enhance_e08.json", "EFW_S1E08_S08", 4,
    "Panel 4 — Mero: 'You watched us use every door you opened to find another battlefield.' He gestures toward the open council-room door, then places the same hand against his own chest. Adrian remains still across from him."
)

# Broader review list: advisory only. These are intentionally wider than the durable validator
# so a human can inspect borderline acting language before deciding whether it belongs upstream.
REVIEW = [
    re.compile(p, re.I) for p in (
        r"\bbecause\b", r"\bmaking (?:clear|the)\b", r"\bmake clear\b",
        r"\bunderstand(?:s|ing)?\b", r"\brealiz(?:e|es|ing)\b", r"\brecogniz(?:e|es|ing)\b",
        r"\bhumaniz(?:e|es|ing)\b", r"\bresponsibility is\b", r"\bthe distinction\b",
        r"\bnot wonder\b", r"\bnot emotional\b", r"\brather than\b", r"\bthe role\b",
        r"\bthe choice\b", r"\bmoral\b", r"\bstakes\b", r"\bthe truth\b",
        r"\bthe history\b", r"\bfamiliarity\b", r"\bimpossibility\b", r"\bmeans that\b",
        r"\bchanges? (?:his|her|their) role\b", r"\bvisibly failing\b",
    )
]

chef = [("assembler", assembler["generationLine"])]
for issue in range(1, 6):
    for scene in load(SHOW / f"scenes_e{issue:02d}.json"):
        for i, panel in enumerate(scene.get("panelPlan", []), 1):
            chef.append((f"{scene['id']}:P{i}", panel.get("text", "")))
for issue in (6, 7, 8):
    for scene in load(SHOW / f"enhance_e{issue:02d}.json"):
        for i, panel in enumerate(scene.get("panelPlan", []), 1):
            chef.append((f"{scene['id']}:P{i}", panel.get("text", "")))
        for i, block in enumerate(scene.get("directionInline", []), 1):
            chef.append((f"{scene['id']}:D{i}", block.get("text", "")))

candidates = [(label, text) for label, text in chef if any(p.search(text) for p in REVIEW)]
print(f"BROADER CHEF REVIEW: {len(candidates)} candidate strings")
for label, text in candidates:
    print(f"REVIEW {label}: {text}")
