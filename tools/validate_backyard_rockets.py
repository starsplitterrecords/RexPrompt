#!/usr/bin/env python3
import base64, gzip, json, re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data" / "shows" / "backyard-rockets-s1"
MANIFEST = ROOT / "data" / "shows.json"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(raw):
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        out = []
        for key, value in raw.items():
            if isinstance(value, dict):
                item = dict(value)
                item.setdefault("id", key)
                out.append(item)
        return out
    raise TypeError(f"Unsupported scene container: {type(raw).__name__}")


def load_encoded(path):
    text = "".join(path.read_text(encoding="utf-8").split())
    raw = base64.b64decode(text, validate=True)
    return json.loads(gzip.decompress(raw).decode("utf-8"))


def episode(scene):
    ep = scene.get("episode")
    if ep:
        return ep
    match = re.search(r"S1E\d{2}", str(scene.get("id", "")))
    return match.group(0) if match else None


shows = load_json(MANIFEST)
show = next((s for s in shows if s.get("id") == "backyard-rockets-s1"), None)
if not show:
    raise SystemExit("Backyard Rockets show missing from data/shows.json")

base_path = ROOT / show.get("basePath", "data/shows/backyard-rockets-s1")
base_file = base_path / show.get("scenesFile", "scenes_base.json")
scenes = normalize(load_json(base_file))
file_counts = []

for overlay in show.get("sceneOverlays", []):
    path = base_path / overlay["file"]
    if not path.exists():
        raise SystemExit(f"Manifest references missing file: {overlay['file']}")
    try:
        if overlay.get("encoding") == "gzip-base64":
            incoming = normalize(load_encoded(path))
        elif overlay.get("encoding"):
            raise ValueError(f"unsupported encoding {overlay['encoding']}")
        else:
            incoming = normalize(load_json(path))
    except Exception as exc:
        raise SystemExit(f"{overlay['file']}: decode failure: {exc}") from exc
    excluded = set(overlay.get("excludeIds", []))
    incoming = [s for s in incoming if s.get("id") not in excluded]
    if not incoming:
        raise SystemExit(f"{overlay['file']}: contains no production scenes")
    file_counts.append((overlay["file"], len(incoming), incoming[0].get("id"), incoming[-1].get("id")))
    scenes.extend(incoming)

if not scenes:
    raise SystemExit("Backyard Rockets assembled to zero scenes")

ids = [s.get("id") for s in scenes]
if any(not scene_id for scene_id in ids):
    raise SystemExit("One or more Backyard Rockets scenes are missing IDs")
if len(ids) != len(set(ids)):
    dupes = [k for k, v in Counter(ids).items() if v > 1]
    raise SystemExit(f"Duplicate scene IDs: {dupes[:10]}")

expected_eps = [f"S1E{n:02d}" for n in range(1, 9)]
eps = [episode(s) for s in scenes]
if any(ep not in expected_eps for ep in eps):
    bad = [(s.get("id"), episode(s)) for s in scenes if episode(s) not in expected_eps]
    raise SystemExit(f"Invalid/missing episode identifiers: {bad[:10]}")

compressed = []
for ep in eps:
    if not compressed or compressed[-1] != ep:
        compressed.append(ep)
if compressed != expected_eps:
    raise SystemExit(f"Episode ordering invalid: {compressed}")

counts = Counter(eps)
print("Observed scene counts:", dict(counts), flush=True)
print("Observed payload boundaries:", flush=True)
for file, count, first_id, last_id in file_counts:
    print(f"  {file}: {count} [{first_id} .. {last_id}]", flush=True)

expected_authored = {
    "S1E01": 20,
    "S1E02": 30,
    "S1E03": 19,
    "S1E04": 18,
    "S1E05": 21,
    "S1E06": 19,
    "S1E07": 19,
    "S1E08": 22,
}
for ep, expected in expected_authored.items():
    if counts[ep] != expected:
        raise SystemExit(f"{ep}: expected {expected} authored source scenes, found {counts[ep]}")

for scene in scenes:
    if not scene.get("summary"):
        raise SystemExit(f"{scene.get('id')}: missing summary")
    if not (scene.get("settingText") or scene.get("setting")):
        raise SystemExit(f"{scene.get('id')}: missing setting")
    if not (scene.get("directionInline") or scene.get("direction")):
        raise SystemExit(f"{scene.get('id')}: missing direction")

factions = load_json(SHOW / "factions.json")
regions = load_json(SHOW / "regions.json")
for scene in scenes:
    region = scene.get("region")
    if region and region not in regions and not scene.get("regionText"):
        raise SystemExit(f"{scene.get('id')}: unknown region {region}")
    for faction in scene.get("factions", []):
        if faction not in factions:
            raise SystemExit(f"{scene.get('id')}: unknown faction {faction}")

print("Backyard Rockets validation passed")
print("Total scenes:", len(scenes))
for ep in expected_eps:
    label = "authored" if ep in expected_authored else "outline-only"
    print(f"{ep}: {counts[ep]} ({label})")
