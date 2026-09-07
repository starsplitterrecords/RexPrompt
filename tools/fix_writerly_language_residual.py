#!/usr/bin/env python3
"""One-shot residual cleanup after assembled writerly-language review."""

from __future__ import annotations

import base64
import gzip
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

RULES = {
    "azure-reach-s1": {
        "Respect is not delay.": "It's a cupcake, Pip.",
        "Sal takes one immediately; respect is not delay.": "Sal takes one immediately while Pip is still staring at the cupcake.",
        "—the story. I was going to say the story.": "—the exhibit. I was going to say the exhibit.",
        "She stole the thesis.": "She said it better.",
        "We amplify the meaning, not the animals.": "We make the guest takeaway bigger without adding animal contact.",
        "If the behavior is already meaningful to guests, we can define the meaning safely.": "If guests are already reacting to it, we can explain what they're actually seeing.",
        "Our dolphin partner returns a meaningful object—": "Our dolphin partner returns an approved enrichment object—",
        "Our trained dolphin returns an approved object with meaning—": "Our trained dolphin returns an approved enrichment object—",
        "The meaning is that it is approved.": "The important part is that it is approved.",
        "That is the story, actually.": "That's the explanation we should give them.",
        "PAGE CONTINUITY — Callbacks must preserve prior issue lessons accurately:": "PAGE CONTINUITY — Preserve the established rules from prior issues:",
        "PAGE DESIGN — Page feel: A season's learning compressed into ordinary rehearsal lines. Key image: The staff rehearsing former crises as settled, boring truths.": "PAGE DESIGN — The staff rehearse the same guest questions that caused earlier problems, now answering them routinely and correctly.",
        "Backstage Button": "Backstage Reset",
    },
    "backyard-rockets-s1": {
        "If their rules are principles, urgency will not erase them.": "If they mean what they wrote, they'll hold the limit even now.",
        "If their rules are theater, Glass Basin will tell us before I have to.": "If they don't, Glass Basin will show me.",
        "his test is explicit—he will see whether their principles survive urgency.": "his test is explicit—he will see whether they keep their own limits during a real emergency.",
        "NEW PAGE. Pay off the issue thesis through behavior: route-around happens before the heroes can rescue the network.": "NEW PAGE. The route-around happens before the crew can rescue the network.",
        "Force the issue's thesis into one irreversible choice. With only one burst left,": "With only one burst left,",
        "Nobody becomes collateral to our success.": "We don't use people as collateral just because the launch works.",
    },
    "division-threshold-s1": {
        "That doesn't tell us whether the rules are right.": "Incidents being down doesn't tell me who these rules are hurting.",
        "A rule I can challenge is better than a person I can't.": "At least I can appeal a written denial. I couldn't appeal my supervisor.",
        "Only if the rule gets to exist.": "Only if the registry is allowed to keep that rule.",
        "This is the visual thesis image of the issue: differences remain real, but neither capability is sufficient alone.": "Show both capabilities being necessary in the same rescue; neither can complete the evacuation alone.",
        "This is the midpoint thesis. No one has seized anything.": "No one has seized control; human orders are still issued, but the administrative layer now determines which orders can be executed.",
        "with objective, resistance, discovery, consequence, and a page button.": "with objective, resistance, discovery, consequence, and a concrete end-state.",
        "institutional resistance, accountable choices, and character arc payoffs.": "institutional resistance, accountable choices, and visible consequences for established character decisions.",
    },
    "echoes-forgotten-war-s1": {
        "Taking responsibility now doesn't make what you did right.": "You don't get credit for admitting it now.",
        "The word is not absolution; it is burden.": "Arbiter keeps his eyes on the empty chair and does not ask Atlas for forgiveness.",
        "Hold on the word 'Mine.' Arbiter is not asking to be forgiven. Atlas is not allowed the comfort of proving Arbiter feels nothing.": "Hold on 'Mine.' Arbiter looks at the empty chair rather than Atlas; Atlas's anger does not resolve.",
        "This is as close as the series should get to explaining apparent history. Adrian describes consequence metaphorically, not mechanism.": "Keep the explanation limited to Adrian's line 'It healed around the wound.' Do not add diagrams or a technical mechanism.",
        "Past and present compositions merge. Modern actions rhyme with ancient actions until the reader can follow continuity without labels.": "Match past and present compositions so modern actions repeat specific physical gestures from the ancient scenes.",
    },
    "stardust-station": {
        "Logging possible procurement thesis.": "Logging that as a procurement complaint.",
        "Only if the inheritance is still asking for care.": "Only if the inherited procedure still changes what we have to maintain.",
        "beginning a metaphor about protection and breathing.": "starting to explain why the vent cannot be sealed completely.",
        "Release Button": "Release Protocol",
    },
    "vikings-2026-s1": {
        "You don't enter this city once, Bjorn. You keep getting permission: train, building, account, room.": "Everywhere we go, there's another yes you need: train, building, account, room.",
    },
    "low-tide-signal": {
        "No lead should function only as a theme delivery mechanism.": "Every lead needs a concrete personal reason for entering, staying in, helping within, or resisting the Reach.",
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
                for old, new in rules.items():
                    if old in value:
                        n = value.count(old)
                        value = value.replace(old, new)
                        counts[old] = counts.get(old, 0) + n
                obj[key] = value
            else:
                replace_strings(value, rules, counts)
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            if isinstance(value, str):
                for old, new in rules.items():
                    if old in value:
                        n = value.count(old)
                        value = value.replace(old, new)
                        counts[old] = counts.get(old, 0) + n
                obj[i] = value
            else:
                replace_strings(value, rules, counts)


def rules_for(path: pathlib.Path):
    rel = path.relative_to(DATA).as_posix()
    out = {}
    for marker, rules in RULES.items():
        if marker in rel:
            out.update(rules)
    return out


def main():
    changed = []
    total = {}
    for path in sorted(DATA.rglob("*")):
        if not path.is_file():
            continue
        if {"source", "raw", "archive"} & set(path.relative_to(DATA).parts):
            continue
        rules = rules_for(path)
        if not rules:
            continue
        original = path.read_text(encoding="utf-8")
        counts = {}
        if path.name.endswith(".json.gzb64"):
            try:
                data = decode_gzb64(original)
            except Exception:
                continue
            replace_strings(data, rules, counts)
            if counts:
                path.write_text(encode_gzb64(data), encoding="utf-8")
        elif path.suffix == ".json":
            rendered = original
            for old, new in rules.items():
                if old in rendered:
                    n = rendered.count(old)
                    rendered = rendered.replace(old, new)
                    counts[old] = counts.get(old, 0) + n
            if counts:
                json.loads(rendered)
                path.write_text(rendered, encoding="utf-8")
        else:
            continue
        if counts:
            changed.append(path.relative_to(ROOT).as_posix())
            for old, n in counts.items():
                total[old] = total.get(old, 0) + n

    print(f"Changed {len(changed)} files; applied {sum(total.values())} replacements across {len(total)} patterns.")
    for path in changed:
        print(f"  {path}")
    print("Matched:")
    for old, n in sorted(total.items()):
        print(f"  {n} x {old}")
    print("Unmatched candidates:")
    for marker, rules in RULES.items():
        for old in rules:
            if old not in total:
                print(f"  {marker}: {old}")
    if not changed:
        raise SystemExit("No residual writerly-language candidates matched active data")


if __name__ == "__main__":
    main()
