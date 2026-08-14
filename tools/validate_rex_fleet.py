#!/usr/bin/env python3
import base64, gzip, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data" / "shows" / "rex-fleet-s1"


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


def episode(scene):
    if scene.get("episode"):
        return scene["episode"]
    m = re.match(r"^RF_(S1E\d{2})_", str(scene.get("id", "")))
    return m.group(1) if m else None


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_encoded(path):
    text = "".join(path.read_text(encoding="utf-8").split())
    raw = base64.b64decode(text, validate=True)
    decoded = gzip.decompress(raw).decode("utf-8")
    return json.loads(decoded)


legacy = normalize(load_json(SHOW / "scenes_prequel.json"))
legacy_e1 = [s for s in legacy if episode(s) == "S1E01"]
base = normalize(load_json(SHOW / "scenes_e01.json"))
if base != legacy_e1:
    raise SystemExit("Explicit Episode 1 base differs from the original Rex Fleet Episode 1")

e2 = normalize(load_json(SHOW / "scenes_e02.json"))
base.extend(e2)
expected_counts = {"S1E01": len(legacy_e1), "S1E02": len(e2)}

for n in range(3, 13):
    ep = f"S1E{n:02d}"
    path = SHOW / "encoded" / f"scenes_e{n:02d}.json.gzb64"
    try:
        incoming = normalize(load_encoded(path))
    except Exception as exc:
        raise SystemExit(f"{path.name}: decode failure: {exc}") from exc
    bad = [s.get("id") for s in incoming if episode(s) != ep]
    if bad:
        raise SystemExit(f"{ep}: payload contains scenes from another episode: {bad[:5]}")
    ids = [s.get("id") for s in incoming]
    if not ids or any(not scene_id for scene_id in ids):
        raise SystemExit(f"{ep}: one or more scenes are missing IDs")
    if len(ids) != len(set(ids)):
        raise SystemExit(f"{ep}: duplicate scene IDs inside payload")
    expected_counts[ep] = len(incoming)
    base.extend(incoming)

expected_order = [f"S1E{n:02d}" for n in range(1, 13)]
sequence = [episode(s) for s in base]
compressed = []
for e in sequence:
    if not compressed or compressed[-1] != e:
        compressed.append(e)
if compressed != expected_order:
    raise SystemExit(f"Episode order invalid: {compressed}")

counts = {ep: sum(1 for s in base if episode(s) == ep) for ep in expected_order}
for ep, expected in expected_counts.items():
    if counts[ep] != expected:
        raise SystemExit(f"{ep}: expected {expected} scenes, found {counts[ep]}")

all_ids = [s.get("id") for s in base]
if len(all_ids) != len(set(all_ids)):
    raise SystemExit("Duplicate scene IDs exist in final assembled season")

for forbidden in ("RF_S1E10_A31", "RF_S1E10_A32"):
    if forbidden in all_ids:
        raise SystemExit(f"Non-story metadata beat survived cleanup: {forbidden}")

for scene in base:
    if not scene.get("summary"):
        raise SystemExit(f"{scene.get('id')}: missing summary")
    if episode(scene) != "S1E01":
        if not (scene.get("settingText") or scene.get("setting")):
            raise SystemExit(f"{scene.get('id')}: missing setting")
        if not (scene.get("regionText") or scene.get("region")):
            raise SystemExit(f"{scene.get('id')}: missing region")

print("Rex Fleet validation passed")
print("Total scenes:", len(base))
for ep in expected_order:
    print(f"{ep}: {counts[ep]}")
