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
    raw = base64.b64decode("".join(path.read_text(encoding="utf-8").split()), validate=True)
    return json.loads(gzip.decompress(raw).decode("utf-8"))


base = normalize(load_json(SHOW / "scenes_prequel.json"))
original_e1 = [s.get("id") for s in base if episode(s) == "S1E01"]

# Apply Episode 2 JSON overlay.
e2 = normalize(load_json(SHOW / "scenes_e02.json"))
first = next(i for i, s in enumerate(base) if episode(s) == "S1E02")
base = [s for s in base if episode(s) != "S1E02"]
base[first:first] = e2

expected_overlay_counts = {"S1E02": len(e2)}
for n in range(3, 13):
    ep = f"S1E{n:02d}"
    path = SHOW / "encoded" / f"scenes_e{n:02d}.json.gzb64"
    incoming = normalize(load_encoded(path))
    bad = [s.get("id") for s in incoming if episode(s) != ep]
    if bad:
        raise SystemExit(f"{ep}: payload contains scenes from another episode: {bad[:5]}")
    ids = [s.get("id") for s in incoming]
    if len(ids) != len(set(ids)):
        raise SystemExit(f"{ep}: duplicate scene IDs inside payload")
    expected_overlay_counts[ep] = len(incoming)
    positions = [i for i, s in enumerate(base) if episode(s) == ep]
    insert_at = positions[0] if positions else len(base)
    base = [s for s in base if episode(s) != ep]
    base[insert_at:insert_at] = incoming

# E1 must be bit-for-bit identical by identity and order.
final_e1 = [s.get("id") for s in base if episode(s) == "S1E01"]
if final_e1 != original_e1:
    raise SystemExit("Episode 1 changed or moved internally")

# Every season episode appears in one contiguous block and in numerical order.
sequence = [episode(s) for s in base]
season_sequence = [e for e in sequence if e and e.startswith("S1E")]
compressed = []
for e in season_sequence:
    if not compressed or compressed[-1] != e:
        compressed.append(e)
expected_order = [f"S1E{n:02d}" for n in range(1, 13)]
if compressed != expected_order:
    raise SystemExit(f"Episode order invalid: {compressed}")

# Overlay counts must survive replacement exactly once.
counts = {ep: sum(1 for s in base if episode(s) == ep) for ep in expected_order}
for ep, expected in expected_overlay_counts.items():
    if counts[ep] != expected:
        raise SystemExit(f"{ep}: expected {expected} scenes after overlay, found {counts[ep]}")

all_ids = [s.get("id") for s in base if s.get("id")]
if len(all_ids) != len(set(all_ids)):
    raise SystemExit("Duplicate scene IDs exist in final assembled season")

print("Rex Fleet validation passed")
print("Total scenes:", len(base))
for ep in expected_order:
    print(f"{ep}: {counts[ep]}")
