#!/usr/bin/env python3
"""Normalize Stardust Station RexPrompt production data.

This migration preserves authored story/page content while removing repeated
production scaffolding that belongs at persistent/show scope rather than page scope.
It is intentionally idempotent.
"""
from __future__ import annotations

import base64
import copy
import gzip
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data" / "shows" / "stardust-station"
ENCODED = SHOW / "encoded"

DROP_DIRECTION_PREFIXES = (
    "STARDUST STATION VISUAL LANGUAGE:",
    "PAGE ACTION — SOURCE-LOCKED:",
    "CHARACTER CONTINUITY —",
    "LOCATION / PROP / STATE CONTINUITY —",
    "CAMERA / LIGHT —",
    "COMIC PAGE / LETTERING —",
)

DIALOGUE_LOCK_MARKERS = (
    "exact source dialogue",
    "exact approved revision dialogue",
    "exact enhanced Issue 2 dialogue",
    "exact enhanced Issue 3 dialogue",
)

POSITIVE_REGION_TEXT = (
    "Bright, maintained, livable workplace space station with clean readable sci-fi surfaces, "
    "ordinary offices, break rooms and corridors, colorful institutional signage, practical "
    "workplace clutter, and corporate optimism showing everyday wear. Workplace comedy remains "
    "visually primary."
)

POSITIVE_SETTINGS = {
    "SDS_Admin_Hub": (
        "Cramped multi-use workplace hub with desks, carts, open panels, printers, vents, monitors, "
        "corporate signage and the nearby taped-off break-room microwave. Busy, readable and maintained."
    ),
    "SDS_West_Corridor": (
        "Narrow maintained station corridor with access panels, doors at both ends, safety lighting "
        "and a small observation window to spectacular space that the coworkers mostly ignore."
    ),
    "SDS_Break_Room": (
        "Ordinary shared employee break room with microwave, vending machine, chairs, printer/forms "
        "and accumulated workplace residue. Institutional, familiar and recognizably workplace-scale."
    ),
}

POSITIVE_FACTIONS = {
    "SDS_Station_Crew": (
        "The recurring coworkers who keep Stardust Station functioning. Their mismatches, dependencies "
        "and forced proximity generate the workplace action."
    ),
    "SDS_StarTrust": (
        "Corporate employer/owner context. Stardust is near low-value shutdown at the start; corporate "
        "interest in the material byproduct emerges opportunistically."
    ),
    "SDS_Inspection": (
        "Routine outside morale-and-safety inspection pressure conducted by a procedural, dry evaluator."
    ),
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def decode(path: Path):
    raw = "".join(path.read_text(encoding="utf-8").split())
    return json.loads(gzip.decompress(base64.b64decode(raw, validate=True)).decode("utf-8"))


def encode(path: Path, value) -> None:
    raw = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    packed = gzip.compress(raw, compresslevel=9, mtime=0)
    path.write_text(base64.b64encode(packed).decode("ascii"), encoding="utf-8")


def story_fingerprint(page: dict) -> dict:
    """Fields whose creative/story content must not change in this migration."""
    return {
        "id": page.get("id"),
        "episode": page.get("episode"),
        "issue": page.get("issue"),
        "page": page.get("page"),
        "pageTitle": page.get("pageTitle"),
        "panelCount": page.get("panelCount"),
        "summary": page.get("summary"),
        "panelPlan": copy.deepcopy(page.get("panelPlan")),
        "dialogueText": [
            (line.get("handle"), line.get("speaker"), line.get("text"))
            for line in page.get("dialogueInline", [])
            if isinstance(line, dict)
        ],
        "setting": page.get("setting"),
        "region": page.get("region"),
        "factions": copy.deepcopy(page.get("factions")),
        "relationshipMode": page.get("relationshipMode"),
        "relationshipFocus": copy.deepcopy(page.get("relationshipFocus")),
        "source": page.get("source"),
    }


def sanitize_dialogue(line: dict) -> dict:
    out = copy.deepcopy(line)
    sub = out.get("subtext")
    if not isinstance(sub, str):
        return out
    lower = sub.lower()
    if any(marker.lower() in lower for marker in DIALOGUE_LOCK_MARKERS):
        match = re.search(r"\bPanel\s+(\d+)\b", sub, flags=re.I)
        if not match:
            raise RuntimeError(f"Cannot preserve panel mapping while sanitizing dialogue subtext: {sub!r}")
        out["subtext"] = f"Panel {int(match.group(1))}"
    return out


def sanitize_page(page: dict) -> tuple[dict, int]:
    before = story_fingerprint(page)
    out = copy.deepcopy(page)

    removed = 0
    kept_direction = []
    for item in out.get("directionInline", []) or []:
        if not isinstance(item, dict):
            kept_direction.append(item)
            continue
        text = str(item.get("text", ""))
        if text.startswith(DROP_DIRECTION_PREFIXES):
            removed += 1
            continue
        kept_direction.append(item)
    if kept_direction:
        out["directionInline"] = kept_direction
    else:
        out.pop("directionInline", None)

    if out.get("charactersInline"):
        cleaned_cast = []
        for char in out["charactersInline"]:
            if not isinstance(char, dict):
                cleaned_cast.append(char)
                continue
            cleaned_cast.append({k: char[k] for k in ("name", "handle") if char.get(k)})
        out["charactersInline"] = cleaned_cast

    if out.get("dialogueInline"):
        out["dialogueInline"] = [
            sanitize_dialogue(line) if isinstance(line, dict) else line
            for line in out["dialogueInline"]
        ]

    after = story_fingerprint(out)
    if before != after:
        raise RuntimeError(f"Sanitization changed story content on {page.get('id')}")
    return out, removed


def sanitize_pages() -> tuple[int, int]:
    pages = 0
    removed_blocks = 0
    paths = sorted(ENCODED.glob("pages_e*.json.gzb64"))
    if not paths:
        raise RuntimeError("No Stardust encoded page payloads found")
    for path in paths:
        data = decode(path)
        if not isinstance(data, list):
            raise RuntimeError(f"Expected list payload in {path}")
        cleaned = []
        for page in data:
            fixed, removed = sanitize_page(page)
            cleaned.append(fixed)
            pages += 1
            removed_blocks += removed
        encode(path, cleaned)
    return pages, removed_blocks


def sanitize_characters() -> int:
    path = SHOW / "characters.json"
    data = load(path)
    removed = 0
    for entry in data.values():
        if not isinstance(entry, dict):
            continue
        for key in ("text", "voiceProfile"):
            if key in entry:
                entry.pop(key)
                removed += 1
    dump(path, data)
    return removed


def sanitize_positive_reference_text() -> None:
    regions = load(SHOW / "regions.json")
    regions["SDS_Stardust_Station"]["text"] = POSITIVE_REGION_TEXT
    dump(SHOW / "regions.json", regions)

    settings = load(SHOW / "settings.json")
    for key, text in POSITIVE_SETTINGS.items():
        settings[key]["text"] = text
    dump(SHOW / "settings.json", settings)

    factions = load(SHOW / "factions.json")
    for key, text in POSITIVE_FACTIONS.items():
        factions[key]["text"] = text
    dump(SHOW / "factions.json", factions)


def verify_clean() -> None:
    forbidden = DROP_DIRECTION_PREFIXES + DIALOGUE_LOCK_MARKERS
    for path in sorted(ENCODED.glob("pages_e*.json.gzb64")):
        data = decode(path)
        text = json.dumps(data, ensure_ascii=False).lower()
        for term in forbidden:
            if term.lower() in text:
                raise RuntimeError(f"Sanitization residue {term!r} remains in {path.name}")

    chars = load(SHOW / "characters.json")
    for key, entry in chars.items():
        if isinstance(entry, dict) and ({"text", "voiceProfile"} & set(entry)):
            raise RuntimeError(f"Behavior/voice production prose remains in character registry: {key}")


if __name__ == "__main__":
    page_count, removed_blocks = sanitize_pages()
    removed_character_fields = sanitize_characters()
    sanitize_positive_reference_text()
    verify_clean()
    print(f"Sanitized {page_count} Stardust pages")
    print(f"Removed {removed_blocks} repeated page-scope production blocks")
    print(f"Removed {removed_character_fields} character behavior/voice fields from RexPrompt")
