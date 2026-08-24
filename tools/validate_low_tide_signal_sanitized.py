#!/usr/bin/env python3
"""Validate Low Tide Signal RexPrompt sanitization.

This validator keeps the package scoped for production use:
- character-level data belongs in characters / ensemble files
- page and chapter records preserve story action without correction residue
- known stale calibration phrases do not return
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW_DIR = ROOT / "data" / "shows" / "low-tide-signal"

JSON_FILES = [
    "show.json",
    "characters.json",
    "ensemble_dynamics.json",
    "lighting.json",
    "mood.json",
    "negatives.json",
    "pages_base.json",
    "pages_ch01_ch03.json",
    "regions.json",
    "sections_ch01_ch04.json",
    "sections_ch04_ch07.json",
    "settings.json",
    "structure_58_beats.json",
]

FORBIDDEN_RESIDUE = [
    "Velma",
    "Scooby",
    "competent scold",
    "author mouthpiece",
    "author's lens",
    "corrective adult",
    "adult-in-the-room",
    "only competent person",
    "I am surrounded by idiots",
    "revision_directives_nicole_ensemble",
    "suggested_line",
    "suggested_exchange",
    "current_issue",
    "supersede older",
    "formerly",
    "formerly known as",
]

REQUIRED_FILES = set(JSON_FILES)
DISALLOWED_FILES = {"revision_directives_nicole_ensemble.json"}


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    errors: list[str] = []

    existing = {p.name for p in SHOW_DIR.iterdir() if p.is_file()}
    missing = sorted(REQUIRED_FILES - existing)
    if missing:
        errors.append(f"Missing expected files: {missing}")

    disallowed = sorted(DISALLOWED_FILES & existing)
    if disallowed:
        errors.append(f"Disallowed correction-residue files remain: {disallowed}")

    combined = ""
    for name in JSON_FILES:
        path = SHOW_DIR / name
        if not path.exists():
            continue
        try:
            load_json(path)
        except Exception as exc:  # pragma: no cover - validation script
            errors.append(f"Invalid JSON in {name}: {exc}")
        combined += path.read_text(encoding="utf-8") + "\n"

    for phrase in FORBIDDEN_RESIDUE:
        if phrase in combined:
            errors.append(f"Forbidden residue found: {phrase!r}")

    characters = load_json(SHOW_DIR / "characters.json")
    nicole = characters.get("C_lts_nicole_hanley", {})
    if nicole.get("role") != "adult participant / Reach-fascinated member of the friend group":
        errors.append("Nicole role is not the sanitized active role")
    if "scene_use" not in nicole:
        errors.append("Nicole scene_use guidance missing")

    sections = load_json(SHOW_DIR / "sections_ch01_ch04.json")
    if any("witness / structural intelligence" in json.dumps(section) for section in sections):
        errors.append("Old Nicole structural-intelligence framing remains in chapter sections")

    if errors:
        print("Low Tide Signal sanitization validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Low Tide Signal sanitization validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
