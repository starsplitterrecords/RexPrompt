#!/usr/bin/env python3
"""Restore main-branch formatting for repaired plain JSON while retaining only targeted text changes."""

from __future__ import annotations

import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]

FILES = {'data/shows/division-threshold-s1/issue_02_scene_dialogue.json': {'You gave them the sentence they needed.': 'You gave them the answer they came for.'},
 'data/shows/division-threshold-s1/pages_e02_compiled.json': {'You gave them the sentence they needed.': 'You gave them the answer they came for.'},
 'data/shows/echoes-forgotten-war-s1/scenes_e03.json': {'You had to ruin that sentence.': "You couldn't let me have that, could you?"},
 'data/shows/low-tide-signal/pages_ch01_ch03.json': {'That sentence kills people.': 'That assumption gets people killed.'},
 'data/shows/low-tide-signal/pages_ch01_ch03_compiled.json': {'That sentence kills people.': 'That assumption gets people killed.'},
 'data/shows/rex-fleet-s1/pages_i02.json': {'That is what the sentence means.': 'Yes. Get them aboard.'},
 'data/shows/rex-fleet-s1/pages_i03.json': {"Finish that sentence and I'll price you into an airlock.": "Try pricing refugees out of shelter and I'll put you in an airlock."},
 'data/shows/stardust-station/pages_e05.json': {'That sentence caused physical pain.': 'I hate that already.',
                                              'That phrase is trying very hard not to say what it means.': 'They want us to manufacture more incidents.',
                                              'PANEL 6 — Kreeb studies the sentence.': 'PANEL 6 — Kreeb studies the instruction packet.'},
 'data/shows/stardust-station/pages_e06.json': {'That is the same sentence.': "Then 'optional' means nothing.",
                                              'We gave them a null result and they gave us a sequel.': 'We gave them nothing and they built another program.'},
 'data/shows/stardust-station/pages_e07.json': {'That is an observable sentence.': 'Finally, something we can measure without guessing.'}}


def replace_json_literal(text: str, old: str, new: str, path: str) -> tuple[str, int]:
    total = 0
    for ensure_ascii in (False, True):
        old_literal = json.dumps(old, ensure_ascii=ensure_ascii)
        new_literal = json.dumps(new, ensure_ascii=ensure_ascii)
        count = text.count(old_literal)
        if count:
            text = text.replace(old_literal, new_literal)
            total += count
            break
    if total == 0:
        raise SystemExit(f"{path}: source literal not found on origin/main: {old}")
    return text, total


def main():
    changed = []
    total = 0
    for rel, changes in FILES.items():
        original = subprocess.check_output(
            ["git", "show", f"origin/main:{rel}"],
            cwd=ROOT,
            text=True,
        )
        repaired = original
        file_count = 0
        for old, new in changes.items():
            repaired, count = replace_json_literal(repaired, old, new, rel)
            file_count += count
        json.loads(repaired)
        path = ROOT / rel
        path.write_text(repaired, encoding="utf-8")
        changed.append((rel, file_count))
        total += file_count

    print(f"Restored exact main formatting in {len(changed)} plain JSON files.")
    print(f"Retained {total} targeted text replacements.")
    for rel, count in changed:
        print(f"  {rel}: {count}")


if __name__ == "__main__":
    main()
