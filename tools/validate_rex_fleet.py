#!/usr/bin/env python3
import base64, gzip, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data" / "shows" / "rex-fleet-s1"
MANIFEST = ROOT / "data" / "shows.json"
INDEX = ROOT / "index.html"


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


def dialogue_texts(scene):
    return [item.get("text", "") for item in scene.get("dialogueInline", [])]


def validate_clean_scene(scene):
    generic = {
        "Play the dialogue as an exchange with listening, interruption and reaction; avoid posed recitation. Keep faces readable and let the environment stay active.",
        "Continuous from the prior beat in this location; preserve positions, props, damage, eyelines and emotional momentum.",
        "Let this visual beat breathe long enough to establish consequence before the next exchange.",
    }
    meta_prefixes = (
        "Canon anchors",
        "Characters:",
        "Tone:",
        "Season 2 hooks:",
        "Visual tone guidance:",
    )
    for item in scene.get("directionInline", []):
        if item.startswith("Performance:"):
            raise SystemExit(f"{scene.get('id')}: character voice duplicated at scene scope")
        if item in generic:
            raise SystemExit(f"{scene.get('id')}: generic production scaffold survived")
        if item.startswith(meta_prefixes):
            raise SystemExit(f"{scene.get('id')}: editorial/correction residue survived")


def validate_issue_2(scenes):
    expected_ids = [f"RF_S1E02_A{n:02d}" for n in range(1, 28)]
    ids = [scene.get("id") for scene in scenes]
    if ids != expected_ids:
        raise SystemExit(f"S1E02: expected ordered A01-A27, found {ids}")

    serialized = json.dumps(scenes, ensure_ascii=False).lower()
    forbidden_fragments = {
        "lantern": "retired Issue 2 lantern metaphor",
        "commerce finds a way": "retired commerce refrain",
        "flow finds a way.": "retired Issue 2 closing line",
        "ilyra venn": "retired character identity",
        "varra cindral": "retired character identity",
        "elyra vorn": "retired character identity",
        "sira red fang": "retired character identity",
        "nira sol": "retired character identity",
        "elder branth": "retired character identity",
    }
    for fragment, reason in forbidden_fragments.items():
        if fragment in serialized:
            raise SystemExit(f"S1E02: {reason} survived: {fragment!r}")

    by_id = {scene["id"]: scene for scene in scenes}
    required_dialogue = {
        "RF_S1E02_A22": ["Log the crossing. Keep the lane open."],
        "RF_S1E02_A25": [
            "Verge convoy to Thunderbreak. Thanks for the shadow.",
            "You brought them through, Captain.",
        ],
        "RF_S1E02_A26": ["Next time, I choose the mark."],
        "RF_S1E02_A27": ["Now they need the road. Tomorrow they need me."],
    }
    for scene_id, expected in required_dialogue.items():
        actual = dialogue_texts(by_id[scene_id])
        if actual != expected:
            raise SystemExit(f"{scene_id}: canonical dialogue mismatch: {actual}")

    required_names = {
        "RF_S1E02_A09": {"Billie Rusk"},
        "RF_S1E02_A11": {"Tessa Banks"},
        "RF_S1E02_A14": {"Captain Naomi Sol"},
        "RF_S1E02_A19": {"Billie Rusk", "Abby Saville"},
        "RF_S1E02_A22": {"Commodore Ella Venn"},
        "RF_S1E02_A24": {"Tessa Banks", "Abby Saville"},
        "RF_S1E02_A25": {"Captain Naomi Sol", "Commodore Ella Venn"},
        "RF_S1E02_A26": {"Billie Rusk", "Abby Saville"},
        "RF_S1E02_A27": {"Jex Marrin"},
    }
    for scene_id, expected in required_names.items():
        actual = {c.get("name") for c in by_id[scene_id].get("charactersInline", [])}
        if not expected.issubset(actual):
            raise SystemExit(f"{scene_id}: missing canonical character identity: {sorted(expected - actual)}")

    if "failed heater module" not in " ".join(by_id["RF_S1E02_A05"].get("directionInline", [])).lower():
        raise SystemExit("RF_S1E02_A05: civilian heater consequence is missing")

    for scene in scenes:
        if scene.get("dialog") or scene.get("direction"):
            raise SystemExit(f"{scene['id']}: S1E02 must use canonical inline dialogue and direction only")
        validate_clean_scene(scene)


shows = load_json(MANIFEST)
show = next((s for s in shows if s.get("id") == "rex-fleet-s1"), None)
if not show:
    raise SystemExit("Rex Fleet show missing from data/shows.json")
overlays = {o.get("replaceEpisode"): o for o in show.get("sceneOverlays", [])}

generation_line = show.get("generationLine", "")
if "comic-book" not in generation_line:
    raise SystemExit("Rex Fleet must declare comic-book production mode")
if "10-second vertical clip" in generation_line or "TV style" in generation_line:
    raise SystemExit("Rex Fleet inherited legacy video-generation language")

characters = load_json(SHOW / "characters.json")
forbidden_character_ids = {
    "C_mother_soft",
    "C_venn_soft_to_herself",
    "C_jex_low",
    "C_billie_low",
    "C_tess_vo",
    "C_kerr_cerulean",
    "C_triarch_voice",
    "C_rhyne_aegis",
    "C_keating_ember",
}
residue = sorted(forbidden_character_ids & set(characters))
if residue:
    raise SystemExit(f"Delivery/correction identity records remain: {residue}")
primary_handles = [entry.get("handle") for entry in characters.values() if entry.get("handle")]
if len(primary_handles) != len(set(primary_handles)):
    raise SystemExit("Duplicate primary character handles remain")
character_serialized = json.dumps(characters, ensure_ascii=False)
for fragment in ("Production reference:", "Source speaker label:"):
    if fragment in character_serialized:
        raise SystemExit(f"Character correction/source residue remains: {fragment}")
for required_id in (
    "C_commodore_ella_venn",
    "C_admiral_cael_dominion",
    "C_soren_kerr",
    "C_admiral_colin_rhyne",
    "C_admiral_janet_keating",
    "C_captain_naomi_sol",
    "C_tessa_banks",
    "C_billie_rusk",
):
    if required_id not in characters:
        raise SystemExit(f"Required current Rex Fleet identity missing: {required_id}")

for required_id in (
    "C_commodore_ella_venn",
    "C_abby_saville",
    "C_tessa_banks",
    "C_billie_rusk",
    "C_governor_halev",
    "C_captain_naomi_sol",
    "C_jex_marrin",
):
    entry = characters[required_id]
    if not entry.get("visualAnchor") or not entry.get("continuityLocks"):
        raise SystemExit(f"Released-canon visual continuity missing: {required_id}")

legacy = normalize(load_json(SHOW / "scenes_prequel.json"))
legacy_other = [s.get("id") for s in legacy if episode(s) != "S1E01"]
if legacy_other:
    raise SystemExit(f"Superseded scenes remain in scenes_prequel.json: {legacy_other[:5]}")
legacy_e1 = [s for s in legacy if episode(s) == "S1E01"]
base = normalize(load_json(SHOW / "scenes_e01.json"))
if base != legacy_e1:
    raise SystemExit("Explicit Episode 1 base differs from the original Rex Fleet Episode 1")

for scene in base:
    for character_id in scene.get("characters", []):
        if character_id not in characters:
            raise SystemExit(f"{scene.get('id')}: unresolved Episode 1 character ID {character_id}")

legacy_dialogue = load_json(SHOW / "dialogue.json")
legacy_direction = load_json(SHOW / "direction.json")
legacy_settings = load_json(SHOW / "settings.json")
expected_dialogue_keys = {key for scene in base for key in scene.get("dialog", [])}
expected_direction_keys = {key for scene in base for key in scene.get("direction", [])}
expected_setting_keys = {scene.get("setting") for scene in base if scene.get("setting")}
if set(legacy_dialogue) != expected_dialogue_keys:
    extra = sorted(set(legacy_dialogue) - expected_dialogue_keys)
    missing = sorted(expected_dialogue_keys - set(legacy_dialogue))
    raise SystemExit(f"Episode 1 dialogue lookup scope mismatch; extra={extra}, missing={missing}")
if set(legacy_direction) != expected_direction_keys:
    extra = sorted(set(legacy_direction) - expected_direction_keys)
    missing = sorted(expected_direction_keys - set(legacy_direction))
    raise SystemExit(f"Episode 1 direction lookup scope mismatch; extra={extra}, missing={missing}")
if set(legacy_settings) != expected_setting_keys:
    extra = sorted(set(legacy_settings) - expected_setting_keys)
    missing = sorted(expected_setting_keys - set(legacy_settings))
    raise SystemExit(f"Episode 1 setting lookup scope mismatch; extra={extra}, missing={missing}")

for key, entry in legacy_dialogue.items():
    if entry.get("speakerId") not in characters:
        raise SystemExit(f"{key}: dialogue speaker ID does not resolve: {entry.get('speakerId')}")

index_text = INDEX.read_text(encoding="utf-8")
for required in ("function findCharacterByHandle", "function formatCharacter", "s.continuityFrom"):
    if required not in index_text:
        raise SystemExit(f"Assembler sanitation support missing: {required}")

e2 = normalize(load_json(SHOW / "scenes_e02.json"))
validate_issue_2(e2)

published_tail = [f"RF_S1E02_A{n:02d}" for n in range(1, 9)]
issue_1_overlay = next(
    (item for item in show.get("sceneOverlays", []) if item.get("replaceEpisode") == "S1E01"),
    None,
)
issue_2_overlay = next(
    (item for item in show.get("sceneOverlays", []) if item.get("replaceEpisode") == "S1E02"),
    None,
)
if not issue_1_overlay or issue_1_overlay.get("includeIds") != published_tail:
    raise SystemExit("Issue 1 must include the released A01-A08 tail in published order")
if not issue_2_overlay or issue_2_overlay.get("excludeIds") != published_tail:
    raise SystemExit("Issue 2 must exclude the already-published A01-A08 tail")
if show.get("excludeSceneIds") != ["RF_S1E01_S07"]:
    raise SystemExit("Issue 1 must omit the unpublished duplicate RF_S1E01_S07")

production_issue_2 = e2[8:]
if [scene.get("id") for scene in production_issue_2] != [f"RF_S1E02_A{n:02d}" for n in range(9, 28)]:
    raise SystemExit("Production Issue 2 must run in order from A09 through A27")
for scene in production_issue_2:
    if len(scene.get("panelPlan", [])) < 4:
        raise SystemExit(f"{scene['id']}: production Issue 2 needs a complete panel plan")
    if not scene.get("continuityFrom"):
        raise SystemExit(f"{scene['id']}: production Issue 2 needs causal continuity")

production_issue_1 = [dict(scene, episode="S1E01") for scene in e2[:8]]
production_issue_2 = [dict(scene, episode="S1E02") for scene in e2[8:]]
base = production_issue_1 + production_issue_2
expected_counts = {"S1E01": len(production_issue_1), "S1E02": len(production_issue_2)}

for n in range(3, 13):
    ep = f"S1E{n:02d}"
    readable_path = SHOW / f"scenes_e{n:02d}.json"
    encoded_path = SHOW / "encoded" / f"scenes_e{n:02d}.json.gzb64"
    path = readable_path if readable_path.exists() else encoded_path
    try:
        incoming = normalize(load_json(path) if path == readable_path else load_encoded(path))
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
    for scene in incoming:
        validate_clean_scene(scene)
    if ep == "S1E03":
        silent_visual_pages = {
            "RF_S1E03_A10", "RF_S1E03_A13", "RF_S1E03_A15", "RF_S1E03_A18",
            "RF_S1E03_A21", "RF_S1E03_A23", "RF_S1E03_A27",
        }
        expected_issue_3_ids = [f"RF_S1E03_A{index:02d}" for index in range(1, 31)]
        if ids != expected_issue_3_ids:
            raise SystemExit("S1E03: recipes must remain in canonical A01-A30 order")
        for index, scene in enumerate(incoming):
            if len(scene.get("panelPlan", [])) < 4:
                raise SystemExit(f"{scene['id']}: Issue 3 needs a complete panel plan")
            expected_prior = incoming[index - 1]["id"] if index else None
            if scene.get("continuityFrom") != expected_prior:
                raise SystemExit(f"{scene['id']}: Issue 3 causal continuity is not sequential")
            dialogue_count = len(scene.get("dialogueInline", []))
            if scene["id"] in silent_visual_pages and dialogue_count:
                raise SystemExit(f"{scene['id']}: designated visual page should remain silent")
            if scene["id"] not in silent_visual_pages | {"RF_S1E03_A30"} and dialogue_count < 2:
                raise SystemExit(f"{scene['id']}: speaking scene lacks sufficient exchange")
    excluded = set(overlays.get(ep, {}).get("excludeIds", []))
    incoming = [s for s in incoming if s.get("id") not in excluded]
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
all_id_set = set(all_ids)
for scene in base:
    target = scene.get("continuityFrom")
    if target and target not in all_id_set:
        raise SystemExit(f"{scene.get('id')}: continuityFrom target does not resolve: {target}")

for forbidden in ("RF_S1E10_A31", "RF_S1E10_A32"):
    if forbidden in all_ids:
        raise SystemExit(f"Non-story metadata beat survived exclusion: {forbidden}")

season_serialized = json.dumps(base, ensure_ascii=False).lower()
for retired_name in ("ilyra venn", "varra cindral", "elyra vorn", "sira red fang", "nira sol", "elder branth"):
    if retired_name in season_serialized:
        raise SystemExit(f"Retired Rex Fleet identity remains in assembled season: {retired_name}")

for scene in base:
    if not scene.get("summary"):
        raise SystemExit(f"{scene.get('id')}: missing summary")
    if episode(scene) != "S1E01":
        if not (scene.get("settingText") or scene.get("setting")):
            raise SystemExit(f"{scene.get('id')}: missing setting")
        if not (scene.get("regionText") or scene.get("region")):
            raise SystemExit(f"{scene.get('id')}: missing region")

print("Rex Fleet validation passed")
print("Sanitized structure required")
print("Total scenes:", len(base))
for ep in expected_order:
    print(f"{ep}: {counts[ep]}")
