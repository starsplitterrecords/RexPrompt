#!/usr/bin/env python3
"""One-shot restoration of sparse Division Threshold literary caption buttons."""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "shows" / "division-threshold-s1"

CAPTIONS = {
    2: ("DT_E002_P26", [
        "We drew the line around them.",
        "Then the line found us.",
    ]),
    3: ("DT_E003_P22", [
        "A rule can be fairer than a person.",
        "It can also reach further.",
    ]),
    4: ("DT_E004_P18", [
        "Nothing was broken.",
        "Everything agreed.",
    ]),
    5: ("DT_E005_P26", [
        "We changed the word.",
        "The permission survived.",
    ]),
    6: ("DT_E006_P13", [
        "No one had to build the whole machine.",
        "They only had to build their part.",
    ]),
    7: ("DT_E007_P18", [
        "Knowing how someone can break is not the same as knowing who they are.",
    ]),
    8: ("DT_E008_P26", [
        "The threshold was never only a number.",
        "It was who got to choose.",
    ]),
}


def object_span(text: str, page_id: str) -> tuple[int, int]:
    start = text.index('{"id":"' + page_id + '"')
    depth = 0
    in_string = False
    escaped = False
    for i in range(start, len(text)):
        c = text[i]
        if in_string:
            if escaped:
                escaped = False
            elif c == "\\":
                escaped = True
            elif c == '"':
                in_string = False
            continue
        if c == '"':
            in_string = True
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return start, i + 1
    raise ValueError(f"Unclosed object for {page_id}")


def add_captions(path: pathlib.Path, page_id: str, field: str, captions: list[str]) -> int:
    text = path.read_text(encoding="utf-8")
    start, end = object_span(text, page_id)
    page = json.loads(text[start:end])
    entries = page[field]
    existing = [e.get("text") for e in entries if isinstance(e, dict) and e.get("speaker") == "CAPTION"]
    if existing:
        if existing == captions:
            return 0
        raise ValueError(f"{path.name} {page_id} already has different CAPTION text: {existing}")
    entries.extend({"speaker": "CAPTION", "text": caption} for caption in captions)
    rendered = json.dumps(page, ensure_ascii=False, separators=(",", ":"))
    candidate = text[:start] + rendered + text[end:]
    json.loads(candidate)
    path.write_text(candidate, encoding="utf-8")
    return len(captions)


def main() -> None:
    total = 0
    touched = []
    for issue, (page_id, captions) in CAPTIONS.items():
        overlay = BASE / f"issue_{issue:02d}_scene_dialogue.json"
        compiled = BASE / f"pages_e{issue:02d}_compiled.json"
        n1 = add_captions(overlay, page_id, "sceneDialogue", captions)
        n2 = add_captions(compiled, page_id, "dialogueInline", captions)
        if n1 != n2:
            raise SystemExit(f"Caption mirror mismatch for issue {issue}: overlay={n1}, compiled={n2}")
        if n1:
            touched.extend([overlay.relative_to(ROOT).as_posix(), compiled.relative_to(ROOT).as_posix()])
            total += n1

    if total != 13:
        raise SystemExit(f"Expected 13 restored caption entries, got {total}")
    print(f"Restored {total} sparse literary captions across Issues 2-8.")
    for path in touched:
        print("  " + path)


if __name__ == "__main__":
    main()
