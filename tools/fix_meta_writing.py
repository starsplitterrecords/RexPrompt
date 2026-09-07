#!/usr/bin/env python3
"""One-shot repair for meta-writing dialogue contamination in active RexPrompt data."""

from __future__ import annotations

import base64
import gzip
import json
import pathlib
import re
import subprocess
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

TARGETS = {'AZR_S1E01_P03': {'I know the words.': 'I know the name.',
                   'The words are suing you.': "Your mouth doesn't.",
                   'Never lead with that sentence.': 'Do not make failure the brand.',
                   'Clean. Memorable. Moves.': 'Guests will remember Tuesdays.'},
 'AZR_S1E01_P04': {'That sentence is wearing a scarf indoors.': 'Whatever that means, keep people off the care path.'},
 'AZR_S1E01_P05': {'That is not a sentence I can put on a sponsor placard.': "I cannot put 'less public, less moment' in front of the sponsor."},
 'AZR_S1E01_P11': {'I need one sentence that means no touching, no release, no adoption, and this is still worth their parking fee.': 'Give me something I can tell the guests: no touching, no release, no adoption, and this is still worth their parking fee.'},
 'AZR_S1E01_P14': {'That sentence was grown in a lab.': 'You made crowd control sound like luxury skincare.',
                   'And cleared for public use.': 'Sponsors understand it.'},
 'AZR_S1E02_P01': {'That sentence is going to cost us.': "If guests believe that, we're paying for it."},
 'AZR_S1E02_P09': {'There should not be a sentence containing all of those nouns.': 'We should not be discussing dolphins and nuggets in the same breath.'},
 'AZR_S1E02_P13': {'That was almost an operations sentence.': 'You sound like you work here now.'},
 'AZR_S1E03_P09': {'That sentence survives legal.': 'Legal can live with that.'},
 'AZR_S1E04_P03': {'I need a sentence that does not sound like we lost our own rays.': 'I need an answer that does not sound like we lost our own rays.'},
 'AZR_S1E04_P05': {'I need one sentence saying the stream is not a veterinary consultation.': 'I need a clear disclaimer: the stream is not a veterinary consultation.',
                   'Please make it sound like a human wrote it.': "Please don't make the guests feel scolded."},
 'AZR_S1E04_P16': {'Careful with that sentence.': "They're guests, Julian. Not a test group."},
 'AZR_S1E05_P05': {'Please do not use that sentence near Beatrice.': 'Beatrice will turn that into a KPI.'},
 'AZR_S1E06_P06': {'That sentence can stay.': 'Good. Take the wall down.'},
 'AZR_S1E05_P13': {'Water tests. Food prep. Habitat checks. Turns out Tuesday has a plot.': 'Water tests. Food prep. Habitat checks. Tuesday is plenty.'},
 'SDS_S1E01_P01': {'Good morning, team. I am seeing upright bodies, open eyes, and a room that is one good sentence away from readiness.': 'Good morning, team. I am seeing upright bodies, open eyes, and a room that could pass for ready if everyone sits up at once.',
                   'Two are technically horizontal, but I respect the sentence.': 'Two are technically horizontal, but your optimism is doing real work.'},
 'SDS_S1E01_P04': {'Finally, a sentence with bolts in it.': 'Good. A problem with bolts.'},
 'SDS_S1E01_P06': {'Also avoid that sentence.': 'Also keep the sandwich out of the briefing.'},
 'SDS_S1E01_P10': {'We do not need vulnerability. We need a repair-relevant clarification that lets me keep one clean sentence for the report.': 'We do not need vulnerability. We need a repair-relevant clarification I can actually put in the report.',
                   'That sentence has so many escape hatches I want to diagram it.': 'You just built yourself six exits from responsibility.'},
 'SDS_S1E01_P20': {'The byproduct is real. Not magic. Not a plan. More like the station sweating value when people stop pretending the pressure isn’t there. Gross sentence. Accurate enough.': 'The byproduct is real. Not magic. Not a plan. Pressure builds; people respond; the station produces something useful.',
                   'Make it less gross and I’ll sign.': 'That I can sign.',
                   'No promises.': 'Good.'},
 'SDS_S1E01_P21': {'That was a very narrow hallway of a sentence.': 'So we stay open.'},
 'SDS_S1E02_P03': {'Brick, punctuation is not evidence.': 'We are not opening a case on the break room, Brick.',
                   'Depends who adds it.': 'Normal is still unproven.'},
 'SDS_S1E02_P06': {'That is not soup. That is recurring character assassination.': "You're building a case file around my lunch."},
 'SDS_S1E02_P08': {'That sentence helps me more than you know.': 'Good. I can fix appliance-shaped.'},
 'SDS_S1E02_P11': {'And one sentence that makes people less alone with leftovers.': "And something that tells people what to do when 'normal' stops being obvious."},
 'SDS_S1E02_P16': {"I'm not giving this room a sequel.": "I'm not turning lunch into another incident.",
                   'The sequel may already be seated.': 'The bowl is still here.'},
 'SDS_S1E03_P10': {'We keep starting the same sentence.': 'We keep restarting the same argument.'},
 'SDS_S1E03_P21': {'No sequel filed.': 'No follow-up meeting.'},
 'SDS_S1E05_P01': {'That sentence caused physical pain.': 'I hate that already.'},
 'SDS_S1E05_P03': {'That phrase is trying very hard not to say what it means.': 'They want us to manufacture more incidents.',
                   'PANEL 6 — Kreeb studies the sentence.': 'PANEL 6 — Kreeb studies the instruction packet.'},
 'SDS_S1E06_P18': {'That is the same sentence.': "Then 'optional' means nothing."},
 'SDS_S1E06_P19': {'We gave them a null result and they gave us a sequel.': 'We gave them nothing and they built another program.'},
 'SDS_S1E07_P04': {'That is an observable sentence.': 'Finally, something we can measure without guessing.'},
 'VIK_S1I02_P02': {'Okay. This is temporary housing. Temporary is doing a lot of work in that sentence.': 'Okay. This is temporary housing. How temporary is still apparently a mystery.'},
 'VIK_S1E03_P12': {'Do not finish that sentence as content.': "Don't turn him into content."},
 'VIK_S1E03_P23': {'That sentence cost me forty minutes.': 'That distinction cost me forty minutes.'},
 'RF_I02_P06': {'That is what the sentence means.': 'Yes. Get them aboard.'},
 'RF_I03_P06': {"Finish that sentence and I'll price you into an airlock.": "Try pricing refugees out of shelter and I'll put you in an airlock."},
 'BR_S1E02_R2_P21': {'Never thought I’d hear that sentence.': "Never thought I'd see you leave launch hardware behind."},
 'BR_S1E03_PS_A02_SC05': {'Yesterday you would have hated that sentence.': 'Yesterday you would have called those two windows non-negotiable.',
                          'I hate it today.': 'I still hate losing them.'},
 'DT_E002_P16': {'You gave them the sentence they needed.': 'You gave them the answer they came for.'},
 'EFW_S1E03_S11': {'You had to ruin that sentence.': "You couldn't let me have that, could you?"},
 'LTS_C03_P08': {'That sentence kills people.': 'That assumption gets people killed.'}}

ID_FIELDS = {
    "id", "pageId", "page_id", "sceneId", "scene_id", "fid", "sourceFid",
    "source_fid", "unitId", "unit_id",
}


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value)
    return (
        value.replace("’", "'")
        .replace("‘", "'")
        .replace("“", '"')
        .replace("”", '"')
        .replace("–", "-")
        .replace("—", "-")
        .strip()
    )


NORMALIZED_TARGETS = {
    unit_id: {normalize(old): (old, new) for old, new in changes.items()}
    for unit_id, changes in TARGETS.items()
}


def unit_id_for(obj, inherited=None):
    if not isinstance(obj, dict):
        return inherited
    for key, value in obj.items():
        if key in ID_FIELDS and isinstance(value, str) and value in TARGETS:
            return value
    return inherited


def rewrite(obj, inherited_id=None, counts=None):
    if counts is None:
        counts = {}
    if isinstance(obj, dict):
        local_id = unit_id_for(obj, inherited_id)
        for key, value in list(obj.items()):
            child_id = key if isinstance(key, str) and key in TARGETS else local_id
            if isinstance(value, str) and child_id in NORMALIZED_TARGETS:
                match = NORMALIZED_TARGETS[child_id].get(normalize(value))
                if match:
                    old, new = match
                    obj[key] = new
                    counts[(child_id, old)] = counts.get((child_id, old), 0) + 1
                    continue
            rewrite(value, child_id, counts)
    elif isinstance(obj, list):
        for value in obj:
            rewrite(value, inherited_id, counts)
    return counts


def b64_normalize(text: str) -> str:
    data = re.sub(r"\s+", "", text).rstrip("=")
    if len(data) % 4 == 1:
        raise ValueError(f"impossible Base64 data length {len(data)}")
    return data + ("=" * ((4 - len(data) % 4) % 4))


def decode_encoded(text: str):
    raw = b64_normalize(text)
    payload = gzip.decompress(base64.b64decode(raw)).decode("utf-8")
    return json.loads(payload)


def recover_unique_history(path: pathlib.Path):
    rel = path.relative_to(ROOT).as_posix()
    commits = subprocess.check_output(
        ["git", "log", "--all", "--format=%H", "--", rel],
        cwd=ROOT,
        text=True,
    ).splitlines()
    variants = {}
    for commit in commits:
        try:
            historical = subprocess.check_output(
                ["git", "show", f"{commit}:{rel}"],
                cwd=ROOT,
                text=True,
                stderr=subprocess.DEVNULL,
            )
            data = decode_encoded(historical)
        except Exception:
            continue
        canonical = json.dumps(data, sort_keys=True, ensure_ascii=False)
        variants.setdefault(canonical, data)
    if len(variants) != 1:
        raise ValueError(
            f"{rel}: cannot recover uniquely from history ({len(variants)} valid variants)"
        )
    return next(iter(variants.values()))


def encode_encoded(data) -> str:
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return base64.b64encode(gzip.compress(payload, mtime=0)).decode("ascii")


def write_json(path: pathlib.Path, data, original: str):
    if "\n" in original.strip():
        rendered = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    else:
        rendered = json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n"
    path.write_text(rendered, encoding="utf-8")


def should_scan(path: pathlib.Path) -> bool:
    parts = set(path.relative_to(DATA).parts)
    if "source" in parts or "raw" in parts or "archive" in parts:
        return False
    return True


def main():
    total_counts = {}
    changed_files = []
    recovered_files = []

    for path in sorted(DATA.rglob("*")):
        if not path.is_file() or not should_scan(path):
            continue

        if path.suffix == ".json":
            original = path.read_text(encoding="utf-8")
            try:
                data = json.loads(original)
            except Exception:
                continue
            counts = {}
            rewrite(data, counts=counts)
            if counts:
                write_json(path, data, original)
                changed_files.append(path.relative_to(ROOT).as_posix())
                for key, value in counts.items():
                    total_counts[key] = total_counts.get(key, 0) + value

        elif path.name.endswith(".json.gzb64"):
            original = path.read_text(encoding="utf-8")
            try:
                data = decode_encoded(original)
            except Exception:
                try:
                    data = recover_unique_history(path)
                    recovered_files.append(path.relative_to(ROOT).as_posix())
                except Exception:
                    continue
            counts = {}
            rewrite(data, counts=counts)
            if counts:
                path.write_text(encode_encoded(data), encoding="utf-8")
                changed_files.append(path.relative_to(ROOT).as_posix())
                for key, value in counts.items():
                    total_counts[key] = total_counts.get(key, 0) + value

    missing = []
    for unit_id, changes in TARGETS.items():
        for old in changes:
            if total_counts.get((unit_id, old), 0) == 0:
                missing.append(f"{unit_id}: {old}")

    print(f"Changed {len(changed_files)} files.")
    for path in changed_files:
        print(f"  {path}")
    if recovered_files:
        print("Recovered uniquely from history before repair:")
        for path in recovered_files:
            print(f"  {path}")

    print(f"Applied {sum(total_counts.values())} replacements across {len(total_counts)} targeted strings.")

    if missing:
        print("Missing targeted source strings:")
        for item in missing:
            print(f"  {item}")
        raise SystemExit(2)


if __name__ == "__main__":
    main()
