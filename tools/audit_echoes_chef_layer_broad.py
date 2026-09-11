#!/usr/bin/env python3
"""Advisory broad review of assembler-visible Echoes image instructions."""
from __future__ import annotations
import json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data" / "shows" / "echoes-forgotten-war-s1"

def load(path): return json.loads(path.read_text(encoding="utf-8"))
PATTERNS = [re.compile(p, re.I) for p in (
    r"\bbecause\b", r"\bmaking (?:clear|the)\b", r"\bmake clear\b",
    r"\bunderstand(?:s|ing)?\b", r"\brealiz(?:e|es|ing)\b", r"\brecogniz(?:e|es|ing)\b",
    r"\bhumaniz(?:e|es|ing)\b", r"\bresponsibility is\b", r"\bthe distinction\b",
    r"\bnot wonder\b", r"\bnot emotional\b", r"\brather than\b", r"\bthe role\b",
    r"\bthe choice\b", r"\bmoral\b", r"\bstakes\b", r"\bthe truth\b",
    r"\bthe history\b", r"\bfamiliarity\b", r"\bimpossibility\b", r"\bmeans that\b",
    r"\bchanges? (?:his|her|their) role\b", r"\bvisibly failing\b",
    r"\bthe reader\b", r"\bthe page's\b", r"\bthe issue\b", r"\bthe story\b",
    r"\bthe point\b", r"\bthe revelation\b", r"\bthe emotional hinge\b",
)]
chef=[]
assembler=load(SHOW/"assembler.json")
chef.append(("assembler",assembler.get("generationLine","")))
for issue in range(1,6):
    for scene in load(SHOW/f"scenes_e{issue:02d}.json"):
        for i,panel in enumerate(scene.get("panelPlan",[]),1): chef.append((f"{scene['id']}:P{i}",panel.get("text","")))
for issue in (6,7,8):
    for scene in load(SHOW/f"enhance_e{issue:02d}.json"):
        for i,panel in enumerate(scene.get("panelPlan",[]),1): chef.append((f"{scene['id']}:P{i}",panel.get("text","")))
        for i,block in enumerate(scene.get("directionInline",[]),1): chef.append((f"{scene['id']}:D{i}",block.get("text","")))
candidates=[(l,t) for l,t in chef if any(p.search(t) for p in PATTERNS)]
print(f"POST-CLEANUP BROAD CHEF REVIEW: {len(candidates)} candidate strings")
for label,text in candidates: print(f"REVIEW {label}: {text}")
