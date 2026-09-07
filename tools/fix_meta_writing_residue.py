#!/usr/bin/env python3
"""One-shot cleanup of residual meta-writing language in active RexPrompt story data."""

from __future__ import annotations

import base64
import gzip
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

# Exact semantic residue found in the assembled production-review output after the
# first dialogue pass. Rules are path-scoped so legitimate language elsewhere is
# untouched. Each replacement redirects attention from prose mechanics to the
# in-world action, consequence, object, or institutional behavior.
RULES = {
    "azure-reach-s1": {
        "cannot put that sentence on a sponsor placard": "cannot put that answer on a sponsor placard",
        "Pip asks for one sentence": "Pip asks what they can tell guests",
        "Pip calls Beatrice’s sentence lab-grown": "Pip mocks Beatrice’s corporate polish",
        "Pip calls Beatrice's sentence lab-grown": "Pip mocks Beatrice's corporate polish",
        "before the sentence runs out of clauses": "before the disclaimer runs out of clauses",
        "guest-facing sentence": "guest-facing explanation",
        "one readable sentence on the card": "one readable instruction on the card",
        "food-service plot": "food-service problem",
        "stops mid-sentence before the promise is made": "catches himself before making the promise",
        "turns the sentence into a question to Maya": "stops and asks Maya instead",
        "before she finishes the sentence": "before she finishes speaking",
        "accurate sentence he can use live": "accurate answer he can use live",
    },
    "backyard-rockets-s1": {
        "Milo strips the problem to one sentence": "Milo strips the problem to one operational fact",
    },
    "division-threshold-s1": {
        "News extracts John's final sentence from the hearing": "News extracts John's final answer from the hearing",
        "part of a grand plot": "part of a larger conspiracy",
        "becomes a plot emergency": "becomes a medical emergency",
        "The migration of words is part of the plot": "The migration of words is part of the escalation",
        "I can't defend that sentence.": "I can't defend what we did.",
    },
    "echoes-forgotten-war-s1": {
        "Theo: 'You had to ruin that sentence.'": "Theo: 'You couldn't let me have that, could you?'",
        "Theo: ‘You had to ruin that sentence.’": "Theo: ‘You couldn’t let me have that, could you?’",
        "beginning a private sentence to Arbiter after Pax-Aeterna but not finishing it": "turning to Arbiter with something private to say after Pax-Aeterna before the memory cuts",
        "beginning a sentence to Arbiter after the extinction ruling": "starting to answer Arbiter after the extinction ruling",
        "beginning of a sentence she once said to Arbiter but not how she finished it": "beginning of an answer she once gave Arbiter but not how she finished it",
        "That's the sentence that keeps ruining us.": "That false choice keeps ruining us.",
        "That’s the sentence that keeps ruining us.": "That false choice keeps ruining us.",
        "that sentence should terrify him": "his uncertainty should terrify him",
        "That sentence should terrify you.": "Not knowing should terrify you.",
    },
    "rex-fleet-s1": {
        "before the hazard plot": "before the dangerous approach",
    },
    "stardust-station": {
        "hears all the escape hatches in the sentence": "hears every way Astra left herself room to retreat",
        "writes a dense opening sentence containing": "fills the opening paragraph with",
        "Kreeb waits until he reaches the third semicolon.": "Kreeb waits until Glorp has filled half the page.",
        "No Sequel for the Soup": "No Second Incident",
        "looks offended by his own sentence": "hears himself and immediately regrets volunteering",
        "reads the sentence again": "rereads the screen",
        "points at the sentence": "points at the offending requirement",
        "with the expression of someone reading a sentence she did not write": "with the expression of someone delivering a corporate briefing she does not believe in",
        "The first visible sentence describes": "The display first describes",
        "The next sentence states": "The display then states",
        "That is almost a sentence I recognize.": "That almost sounds like us.",
        "Today we need a department-shaped sentence.": "Today we need it to.",
        "One sentence.": "Give me the plain answer.",
    },
    "sun-comes-through": {
        "relationship plot": "relationship arc",
    },
    "vikings-2026-s1": {
        "not a sentence or compliance hearing": "not a disciplinary or compliance hearing",
    },
    "low-tide-signal": {
        "than a plot emergency": "than a crisis",
    },
}


def decode_gzb64(text: str):
    raw = re.sub(r"\s+", "", text).rstrip("=")
    raw += "=" * ((4 - len(raw) % 4) % 4)
    return json.loads(gzip.decompress(base64.b64decode(raw)).decode("utf-8"))


def encode_gzb64(data) -> str:
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return base64.b64encode(gzip.compress(payload, mtime=0)).decode("ascii")


def replace_strings(obj, rules, counts):
    if isinstance(obj, dict):
        for key, value in list(obj.items()):
            if isinstance(value, str):
                new = value
                for old, replacement in rules.items():
                    if old in new:
                        occurrences = new.count(old)
                        new = new.replace(old, replacement)
                        counts[old] = counts.get(old, 0) + occurrences
                obj[key] = new
            else:
                replace_strings(value, rules, counts)
    elif isinstance(obj, list):
        for value in obj:
            replace_strings(value, rules, counts)


def matching_rules(path: pathlib.Path):
    rel = path.relative_to(DATA).as_posix()
    merged = {}
    for marker, rules in RULES.items():
        if marker in rel:
            merged.update(rules)
    return merged


def main():
    changed_files = []
    total_counts = {}

    for path in sorted(DATA.rglob("*")):
        if not path.is_file():
            continue
        rules = matching_rules(path)
        if not rules:
            continue
        rel_parts = set(path.relative_to(DATA).parts)
        if {"source", "raw", "archive"} & rel_parts:
            continue

        original = path.read_text(encoding="utf-8")
        encoded = path.name.endswith(".json.gzb64")
        counts = {}

        if encoded:
            try:
                data = decode_gzb64(original)
            except Exception:
                continue
            replace_strings(data, rules, counts)
            if counts:
                path.write_text(encode_gzb64(data), encoding="utf-8")
        elif path.suffix == ".json":
            # Preserve byte-level formatting in readable JSON: all rules are literal
            # prose substitutions and do not alter JSON syntax.
            rendered = original
            for old, replacement in rules.items():
                if old in rendered:
                    occurrences = rendered.count(old)
                    rendered = rendered.replace(old, replacement)
                    counts[old] = counts.get(old, 0) + occurrences
            if counts:
                json.loads(rendered)
                path.write_text(rendered, encoding="utf-8")
        else:
            continue

        if not counts:
            continue
        changed_files.append(path.relative_to(ROOT).as_posix())
        for old, count in counts.items():
            total_counts[old] = total_counts.get(old, 0) + count

    print(f"Changed {len(changed_files)} files.")
    for rel in changed_files:
        print(f"  {rel}")
    print(f"Applied {sum(total_counts.values())} residual replacements across {len(total_counts)} matched patterns.")

    missing = []
    optional_variants = {
        "Pip calls Beatrice's sentence lab-grown",
        "Theo: ‘You had to ruin that sentence.’",
        "That’s the sentence that keeps ruining us.",
    }
    for marker, rules in RULES.items():
        for old in rules:
            if old in optional_variants:
                continue
            if total_counts.get(old, 0) == 0:
                missing.append(f"{marker}: {old}")
    if missing:
        print("Unmatched expected residue patterns:")
        for item in missing:
            print(f"  {item}")
        raise SystemExit(2)


if __name__ == "__main__":
    main()
