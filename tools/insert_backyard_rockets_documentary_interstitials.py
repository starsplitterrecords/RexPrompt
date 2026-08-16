#!/usr/bin/env python3
"""Insert the canonical Tethergrid/Dryline documentary interstitials into production order."""

import base64
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW_ID = "backyard-rockets-s1"
SHOW = ROOT / "data" / "shows" / SHOW_ID
SPECS = json.loads((SHOW / "documentary-interstitials.json").read_text(encoding="utf-8"))

CHANNELS = {
    "tethergrid": {
        "speaker": "Tetherwell Narrator",
        "handle": "@brk.TetherwellNarrator",
        "factions": ["BR_Tethergrid"],
        "language": "TETHERGRID DOCUMENTARY LANGUAGE: immaculate narrated promotional film or civic commercial; controlled camera movement, pristine corporate typography, water-blue data graphics, comforting human imagery and precise graphite/cyan Tethergrid design. Persuasive through selective framing and technically defensible omission rather than cartoonish lies.",
    },
    "dryline": {
        "speaker": "Dryline Reporter",
        "handle": "@brk.DrylineReporter",
        "factions": ["BR_Dryline"],
        "language": "DRYLINE DOCUMENTARY LANGUAGE: rigorous independent investigative journalism made under field constraints; handheld but legible footage, natural desert color, direct equipment evidence, sourced records, restrained annotation and honest uncertainty. Visually imperfect never means incompetent or sensationalized.",
    },
}


def load(path, encoding=None):
    if encoding == "gzip-base64":
        packed = base64.b64decode("".join(path.read_text(encoding="utf-8").split()), validate=True)
        return json.loads(gzip.decompress(packed).decode("utf-8"))
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value, encoding=None):
    raw = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode()
    if encoding == "gzip-base64":
        path.write_text(base64.b64encode(gzip.compress(raw, 9, mtime=0)).decode(), encoding="utf-8")
    else:
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def scene_from(spec):
    channel = CHANNELS[spec["channel"]]
    speaker = channel["speaker"]
    handle = channel["handle"]
    return {
        "id": spec["id"],
        "episode": spec["episode"],
        "act": "DOCUMENTARY INTERSTITIAL",
        "summary": spec["summary"],
        "settingText": spec["setting"],
        "region": "BR_Mojave",
        "factions": channel["factions"],
        "charactersInline": [{"name": speaker, "handle": handle, "visibility": "voice-over only; never shown"}],
        "dialogueInline": [{"speaker": speaker, "handle": handle, "text": spec["narration"], "delivery": "voice-over"}],
        "directionInline": [
            {"text": channel["language"]},
            {"text": "SCENE ACTION — SOURCE-LOCKED: " + spec["summary"]},
            {"text": "PRESENTER CONTINUITY — Voice-over only. Do not show, silhouette, or invent an on-camera narrator or reporter unless a later scene explicitly introduces one."},
            {"text": "LOCATION / GRAPHIC CONTINUITY — " + spec["setting"] + " Preserve all named screens, labels, footage sources, water states and equipment conditions exactly; the two channels may reuse identical footage with different crops or evidence overlays."},
            {"text": "CAMERA / EDITORIAL GRAMMAR — 10-second vertical documentary insert. Make every statistic, authorization state and physical water consequence immediately legible. Tethergrid controls the frame; Dryline reveals what was cropped out."},
        ],
        "documentaryChannel": spec["channel"],
    }


manifest = json.loads((ROOT / "data" / "shows.json").read_text(encoding="utf-8"))
show = next(item for item in manifest if item.get("id") == SHOW_ID)
base = ROOT / show["basePath"]
files = [(show.get("scenesFile", "scenes_base.json"), None)]
files += [(item["file"], item.get("encoding")) for item in show.get("sceneOverlays", [])]

pending = {spec["id"]: spec for spec in SPECS}
inserted = []
for relative, encoding in files:
    path = base / relative
    payload = load(path, encoding)
    if not isinstance(payload, list):
        raise TypeError(f"{relative}: documentary insertion requires list scene payloads")
    existing_documentaries = {scene.get("id") for scene in payload if scene.get("documentaryChannel")}
    payload = [scene for scene in payload if scene.get("id") not in pending]
    out = []
    for scene in payload:
        out.append(scene)
        anchor = scene.get("id")
        chain = [spec for spec in SPECS if spec["after"] == anchor]
        while chain:
            for spec in chain:
                built = scene_from(spec)
                out.append(built)
                inserted.append(spec["id"])
                pending.pop(spec["id"], None)
            anchors = {spec["id"] for spec in chain}
            chain = [spec for spec in SPECS if spec["after"] in anchors]
    if len(out) != len(payload) or existing_documentaries:
        write(path, out, encoding)

if pending:
    raise SystemExit(f"Documentary interstitial anchors did not resolve: {sorted(pending)}")
if len(inserted) != len(SPECS):
    raise SystemExit(f"Expected {len(SPECS)} interstitials, inserted {len(inserted)}")

print(f"Inserted {len(inserted)} Backyard Rockets documentary interstitials")
