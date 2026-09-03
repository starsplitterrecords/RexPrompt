#!/usr/bin/env python3
import base64, gzip, json, re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data" / "shows" / "backyard-rockets-s1"
MANIFEST = ROOT / "data" / "shows.json"

def load_json(path): return json.loads(path.read_text(encoding="utf-8"))
def normalize(raw):
    if isinstance(raw, list): return raw
    if isinstance(raw, dict):
        return [{"id": key, **value} for key, value in raw.items() if isinstance(value, dict)]
    raise TypeError(f"Unsupported scene container: {type(raw).__name__}")
def load_encoded(path):
    raw = base64.b64decode("".join(path.read_text(encoding="utf-8").split()), validate=True)
    return json.loads(gzip.decompress(raw).decode("utf-8"))
def episode(scene):
    if scene.get("episode"): return scene["episode"]
    match = re.search(r"S1E\d{2}", str(scene.get("id", "")))
    return match.group(0) if match else None

shows = load_json(MANIFEST)
show = next((s for s in shows if s.get("id") == "backyard-rockets-s1"), None)
if not show: raise SystemExit("Backyard Rockets show missing from data/shows.json")
base_path = ROOT / show.get("basePath", "data/shows/backyard-rockets-s1")
base_file = base_path / show.get("scenesFile", "scenes_base.json")
scenes = normalize(load_json(base_file))
file_counts = []
for overlay in show.get("sceneOverlays", []):
    path = base_path / overlay["file"]
    if not path.exists(): raise SystemExit(f"Manifest references missing file: {overlay['file']}")
    try:
        encoding = overlay.get("encoding")
        if encoding == "gzip-base64":
            incoming = normalize(load_encoded(path))
        elif encoding:
            raise ValueError(f"unsupported encoding {encoding}")
        else:
            incoming = normalize(load_json(path))
    except Exception as exc:
        raise SystemExit(f"{overlay['file']}: decode failure: {exc}") from exc
    excluded = set(overlay.get("excludeIds", []))
    incoming = [s for s in incoming if s.get("id") not in excluded]
    if not incoming: raise SystemExit(f"{overlay['file']}: contains no production scenes")
    file_counts.append((overlay["file"], len(incoming), incoming[0].get("id"), incoming[-1].get("id")))
    scenes.extend(incoming)

ids = [s.get("id") for s in scenes]
if any(not x for x in ids): raise SystemExit("One or more Backyard Rockets scenes are missing IDs")
if len(ids) != len(set(ids)): raise SystemExit(f"Duplicate scene IDs: {[k for k,v in Counter(ids).items() if v>1][:10]}")
expected_eps = [f"S1E{n:02d}" for n in range(1, 9)]
eps = [episode(s) for s in scenes]
if any(ep not in expected_eps for ep in eps): raise SystemExit("Invalid/missing episode identifier")
compressed = []
for ep in eps:
    if not compressed or compressed[-1] != ep: compressed.append(ep)
if compressed != expected_eps: raise SystemExit(f"Episode ordering invalid: {compressed}")
counts = Counter(eps)
expected_authored = {"S1E01":20,"S1E02":24,"S1E03":19,"S1E04":18,"S1E05":21,"S1E06":19,"S1E07":19,"S1E08":22}
for ep, expected in expected_authored.items():
    if counts[ep] != expected: raise SystemExit(f"{ep}: expected {expected}, found {counts[ep]}")

factions = load_json(SHOW / "factions.json")
regions = load_json(SHOW / "regions.json")
settings = load_json(SHOW / "settings.json")
characters = load_json(SHOW / "characters.json")
handles = {v.get("handle") for v in characters.values() if isinstance(v, dict) and v.get("handle")}
for scene in scenes:
    sid = scene.get("id")
    if not scene.get("summary"): raise SystemExit(f"{sid}: missing summary")
    setting = scene.get("setting")
    if setting and setting not in settings: raise SystemExit(f"{sid}: unknown setting {setting}")
    if not setting and not scene.get("settingText"): raise SystemExit(f"{sid}: missing setting")
    region = scene.get("region")
    if not region or region not in regions: raise SystemExit(f"{sid}: missing/unknown region {region}")
    for faction in scene.get("factions", []):
        if faction not in factions: raise SystemExit(f"{sid}: unknown faction {faction}")
    for c in scene.get("charactersInline", []) or []:
        if c.get("handle") not in handles: raise SystemExit(f"{sid}: unknown character handle {c.get('handle')}")
    if episode(scene) == "S1E03":
        panels = scene.get("panelPlan") or []
        if len(panels) < 4: raise SystemExit(f"{sid}: Public Sky production page requires at least four planned panels")
        if not any(str(x).strip() for x in scene.get("directionInline", []) or []):
            raise SystemExit(f"{sid}: Public Sky production page missing scene direction")

public_sky = [scene for scene in scenes if episode(scene) == "S1E03"]
previous = "BR_S1E02_R2_P24"
for scene in public_sky:
    sid = scene["id"]
    if scene.get("continuityFrom") != previous:
        raise SystemExit(f"{sid}: Public Sky continuityFrom must be {previous}, found {scene.get('continuityFrom')}")
    previous = sid

print("Observed scene counts:", dict(counts), flush=True)
print("Observed payload boundaries:", flush=True)
for file, count, first_id, last_id in file_counts: print(f"  {file}: {count} [{first_id} .. {last_id}]", flush=True)
print("Public Sky production pages:", len(public_sky), "panel plans:", sum(len(s.get("panelPlan") or []) for s in public_sky), flush=True)
print("Backyard Rockets validation passed")
print("Total scenes:", len(scenes))
