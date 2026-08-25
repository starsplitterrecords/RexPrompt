#!/usr/bin/env python3
import base64, gzip, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data" / "shows" / "rex-fleet-s1"
MANIFEST = ROOT / "data" / "shows.json"
INDEX = ROOT / "index.html"

GENERIC = {
    "Play the dialogue as an exchange with listening, interruption and reaction; avoid posed recitation. Keep faces readable and let the environment stay active.",
    "Continuous from the prior beat in this location; preserve positions, props, damage, eyelines and emotional momentum.",
    "Let this visual beat breathe long enough to establish consequence before the next exchange.",
}
CONTINUOUS = "Continuous from the prior beat in this location; preserve positions, props, damage, eyelines and emotional momentum."
META_PREFIXES = ("Canon anchors", "Characters:", "Tone:", "Season 2 hooks:", "Visual tone guidance:")
FORBIDDEN_IDS = {
    "C_mother_soft", "C_venn_soft_to_herself", "C_jex_low", "C_billie_low",
    "C_tess_vo", "C_kerr_cerulean", "C_triarch_voice", "C_rhyne_aegis", "C_keating_ember",
}
ID_MAP = {
    "C_mother_soft": "C_luminara_mother",
    "C_venn_soft_to_herself": "C_commodore_ella_venn",
    "C_jex_low": "C_jex_marrin",
    "C_billie_low": "C_billie_rusk",
    "C_tess_vo": "C_tessa_banks",
    "C_kerr_cerulean": "C_soren_kerr",
    "C_rhyne_aegis": "C_admiral_colin_rhyne",
    "C_keating_ember": "C_admiral_janet_keating",
    "C_triarch_voice": "C_silent_triarch",
}
REFERENCE_NAMES = {
    "C_commodore_ella_venn": "Venn", "C_admiral_cael_dominion": "Dominion",
    "C_abby_saville": "Abby", "C_tessa_banks": "Tess", "C_billie_rusk": "Billie",
    "C_governor_halev": "Halev", "C_captain_naomi_sol": "Naomi", "C_jex_marrin": "Jex",
    "C_elder_wallace": "Elder Wallace", "C_oren_pike": "Pike", "C_silent_triarch": "Triarch",
    "C_luminara_mother": "Mother", "C_luminara_boy": "Luminara Boy",
    "C_archivist_selene_stormwell": "Selene", "C_liora_virelia": "Liora",
    "C_lieutenant_deka": "Deka", "C_jia_morgan": "Jia", "C_soren_kerr": "Kerr",
    "C_tom_barrett": "Tom", "C_admiral_colin_rhyne": "Rhyne", "C_admiral_janet_keating": "Keating",
}
FUNCTIONAL = {
    "C_second": ("Second", "@starsplit.second", "Verge escort second officer"),
    "C_officer": ("Officer", "@starsplit.officer", "Fleet officer"),
    "C_raider": ("Raider", "@starsplit.raider", "Shard raider"),
    "C_fleet_sergeant": ("Fleet Sergeant", "@starsplit.fleet.sergeant", "Fleet sergeant"),
    "C_tactical": ("Tactical", "@starsplit.tactical", "Fleet tactical officer"),
    "C_medic": ("Medic", "@starsplit.medic", "Fleet medic"),
    "C_crew_various": ("Crew (various)", "@starsplit.crew.various", "Fleet crew ensemble"),
    "C_rival_captain": ("Rival Captain", "@starsplit.rival.captain", "Shard rival captain"),
    "C_scribe": ("Scribe", "@starsplit.scribe", "Court or market scribe"),
    "C_emissary": ("Emissary", "@starsplit.emissary", "Triarch emissary"),
    "C_child": ("Child", "@starsplit.child", "Civilian child"),
}

def load(path): return json.loads(path.read_text(encoding="utf-8"))
def save(path, obj): path.write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
def save_list(path, seq):
    path.write_text("[\n" + ",\n".join(json.dumps(x, ensure_ascii=False, separators=(",", ":")) for x in seq) + "\n]\n", encoding="utf-8")
def load_encoded(path):
    raw = base64.b64decode("".join(path.read_text(encoding="utf-8").split()), validate=True)
    return json.loads(gzip.decompress(raw).decode("utf-8"))
def save_encoded(path, obj):
    raw = json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    path.write_text(base64.b64encode(gzip.compress(raw, mtime=0)).decode("ascii") + "\n", encoding="utf-8")

def split_notes(entry):
    notes = entry.pop("notes", None)
    if not notes:
        return
    cleaned = re.sub(r"\s*Production reference:.*$", "", notes).strip()
    cleaned = re.sub(r"\s*Source speaker label:.*$", "", cleaned).strip()
    m = re.match(r"Voice:\s*(.*?)(?:\s+Arc:\s*(.*))?$", cleaned)
    if m:
        voice = (m.group(1) or "").strip()
        arc = (m.group(2) or "").strip()
        if voice: entry["voice"] = voice
        if arc: entry["arc"] = arc
    elif cleaned:
        entry["notes"] = cleaned

# Show scope.
shows = load(MANIFEST)
rf = next(s for s in shows if s.get("id") == "rex-fleet-s1")
rf["unitLabel"] = "SCENE"
rf["generationLine"] = "Prestige full-color comic-book sequential-art scene. Preserve scripted action, character identity, continuity, and exact lettering. Fictional production."
save(MANIFEST, shows)

# Character scope: transform current records instead of replacing the current cast.
chars = load(SHOW / "characters.json")
for dead in FORBIDDEN_IDS:
    chars.pop(dead, None)
for cid, entry in list(chars.items()):
    split_notes(entry)
    if cid in REFERENCE_NAMES:
        entry["referenceName"] = REFERENCE_NAMES[cid]
for cid, (name, handle, role) in FUNCTIONAL.items():
    if cid in chars:
        chars[cid] = {"name": name, "handle": handle, "role": role}

# Locked current identities whose duplicate source records were removed.
chars.setdefault("C_admiral_colin_rhyne", {})
chars["C_admiral_colin_rhyne"].update({
    "name": "Admiral Colin Rhyne", "handle": "@starsplit.colin.rhyne",
    "role": "Fleet Admiralty — Aegis / Defense", "referenceName": "Rhyne",
    "aliases": ["@starsplit.admiral.colin.rhyne"],
    "voice": "Practical, protective, integration-minded; favors Verge pilots in Fleet pickets and civilian access."
})
chars.setdefault("C_admiral_janet_keating", {})
chars["C_admiral_janet_keating"].update({
    "name": "Admiral Janet Keating", "handle": "@starsplit.janet.keating",
    "role": "Fleet Admiralty — hard-line military voice", "referenceName": "Keating",
    "aliases": ["@starsplit.admiral.janet.keating"],
    "voice": "Force- and blockade-oriented; treats delay and civilian constraints as operational risk."
})
if "C_soren_kerr" in chars:
    chars["C_soren_kerr"].update({"name": "Admiral Soren Kerr", "role": "Fleet Admiralty — Cerulean / restraint", "referenceName": "Kerr"})
tri = chars.get("C_silent_triarch", {})
if tri:
    tri["name"] = "The Silent Triarch"
    tri["aliases"] = sorted(set(tri.get("aliases", []) + ["@starsplit.triarch", "@starsplit.triarch.voice"]))
    tri["referenceName"] = "Triarch"
for cid, name, handle, role, ref, alias, voice in [
    ("C_silent_triarch_raid", "Silent Triarch — Raid", "@starsplit.silent.triarch.raid", "Triarch mask — Raid", "Raid Mask", "@starsplit.raid.mask", "Sparse and imperative; frames seizure as survival."),
    ("C_silent_triarch_fear", "Silent Triarch — Fear", "@starsplit.silent.triarch.fear", "Triarch mask — Fear", "Fear Mask", "@starsplit.fear.mask", "Sparse and clinical; treats fear as a governing instrument."),
    ("C_silent_triarch_trade", "Silent Triarch — Trade", "@starsplit.silent.triarch.trade", "Triarch mask — Trade", "Trade Mask", "@starsplit.trade.mask", "Sparse and transactional; frames control as managed flow."),
]:
    chars[cid] = {"name": name, "handle": handle, "role": role, "referenceName": ref, "aliases": [alias], "voice": voice}
save(SHOW / "characters.json", chars)

# Episode 1 references and lookup tables.
e1 = load(SHOW / "scenes_e01.json")
for scene in e1:
    if scene.get("characters"):
        out = []
        for cid in scene["characters"]:
            cid = ID_MAP.get(cid, cid)
            if scene.get("id") == "RF_S1E01_S06" and cid == "C_billie_rusk":
                continue
            if cid not in out:
                out.append(cid)
        scene["characters"] = out
save_list(SHOW / "scenes_e01.json", e1)
save_list(SHOW / "scenes_prequel.json", e1)

dialogue = load(SHOW / "dialogue.json")
for key, speaker, subtext in [
    ("D_RF_E01_S07_03", "C_luminara_mother", "soft"),
    ("D_RF_E01_S08_02", "C_commodore_ella_venn", "soft, to herself"),
    ("D_RF_E01_S09_03", "C_jex_marrin", "low"),
]:
    if key in dialogue:
        dialogue[key]["speakerId"] = speaker
        dialogue[key]["subtext"] = subtext
refs_dialogue = [k for s in e1 for k in s.get("dialog", [])]
refs_direction = [k for s in e1 for k in s.get("direction", [])]
refs_settings = list(dict.fromkeys(s["setting"] for s in e1 if s.get("setting")))
dialogue = {k: dialogue[k] for k in refs_dialogue if k in dialogue}
direction = load(SHOW / "direction.json")
direction = {k: direction[k] for k in refs_direction if k in direction}
settings = load(SHOW / "settings.json")
settings = {k: settings[k] for k in refs_settings if k in settings}
save(SHOW / "dialogue.json", dialogue)
save(SHOW / "direction.json", direction)
save(SHOW / "settings.json", settings)

# Inline episodes: remove repeated scaffolding while retaining all unique story/staging material.
all_inline = []
e2 = load(SHOW / "scenes_e02.json")
all_inline.extend(e2)
for n in range(3, 13):
    path = SHOW / "encoded" / f"scenes_e{n:02d}.json.gzb64"
    scenes = load_encoded(path)
    previous = None
    for scene in scenes:
        old = list(scene.get("directionInline", []))
        had_continuity = CONTINUOUS in old
        cleaned = []
        for item in old:
            if item.startswith("Performance:") or item in GENERIC or item.startswith(META_PREFIXES):
                continue
            cleaned.append(item)
        if cleaned:
            scene["directionInline"] = cleaned
        else:
            scene.pop("directionInline", None)
        if had_continuity and previous and not scene.get("continuityFrom"):
            scene["continuityFrom"] = previous.get("id")
        previous = scene
    save_encoded(path, scenes)
    all_inline.extend(scenes)

# Assembler: persistent character identity/voice + structured continuity.
html = INDEX.read_text(encoding="utf-8")
if "function findCharacterByHandle" not in html:
    needle = "function normalizeScenes(raw)"
    helper = 'function findCharacterByHandle(h,c){return Object.values(c||{}).find(e=>e&&(e.handle===h||(Array.isArray(e.aliases)&&e.aliases.includes(h))))}function formatCharacter(e,fallback){if(!e)return fallback;const p=[e.name||fallback];if(e.role)p.push(e.role);if(e.voice)p.push("Voice: "+e.voice);return p.join(" — ")}function normalizeScenes(raw)'
    if needle not in html: raise SystemExit("normalizeScenes assembler anchor missing")
    html = html.replace(needle, helper, 1)
old_chars = 'if(s.charactersInline?.length){out.push("\\n[CHARACTERS]");s.charactersInline.forEach(c=>out.push(c.name||c.handle))}else if(s.characters?.length){out.push("\\n[CHARACTERS]");s.characters.forEach(k=>{const e=store["characters.json"]?.[k];if(e)out.push(formatEntry(e))})}'
new_chars = 'if(s.charactersInline?.length){out.push("\\n[CHARACTERS]");s.charactersInline.forEach(c=>{const e=findCharacterByHandle(c.handle,store["characters.json"]||{});out.push(formatCharacter(e,c.name||c.handle))})}else if(s.characters?.length){out.push("\\n[CHARACTERS]");s.characters.forEach(k=>{const e=store["characters.json"]?.[k];if(e)out.push(formatCharacter(e,k))})}'
if old_chars in html: html = html.replace(old_chars, new_chars, 1)
elif new_chars not in html: raise SystemExit("character rendering assembler anchor missing")
old_dir = 'if(s.direction?.length||s.directionInline?.length){out.push("\\n[DIRECTION]");if(s.direction?.length)s.direction.forEach(k=>{const e=store["direction.json"]?.[k];if(e)out.push(formatEntry(e))});if(s.directionInline?.length)s.directionInline.forEach(x=>out.push(formatEntry(x)))}'
new_dir = 'if(s.continuityFrom)out.push("\\n[CONTINUITY]\\nContinue directly from "+s.continuityFrom+"; preserve established positions, props, damage, eyelines, and emotional state.");if(s.direction?.length||s.directionInline?.length){out.push("\\n[DIRECTION]");if(s.direction?.length)s.direction.forEach(k=>{const e=store["direction.json"]?.[k];if(e)out.push(formatEntry(e))});if(s.directionInline?.length)s.directionInline.forEach(x=>out.push(formatEntry(x)))}'
if old_dir in html: html = html.replace(old_dir, new_dir, 1)
elif new_dir not in html: raise SystemExit("direction rendering assembler anchor missing")
INDEX.write_text(html, encoding="utf-8")

# Sanitation audit.
chars = load(SHOW / "characters.json")
residue = FORBIDDEN_IDS & set(chars)
if residue: raise SystemExit(f"pseudo character residue: {sorted(residue)}")
handles = [v.get("handle") for v in chars.values() if v.get("handle")]
if len(handles) != len(set(handles)): raise SystemExit("duplicate primary handles")
blob = json.dumps(chars, ensure_ascii=False)
if "Production reference:" in blob or "Source speaker label:" in blob: raise SystemExit("character correction/source residue")
if set(load(SHOW / "dialogue.json")) != set(refs_dialogue): raise SystemExit("dialogue lookup scope mismatch")
if set(load(SHOW / "direction.json")) != set(refs_direction): raise SystemExit("direction lookup scope mismatch")
if set(load(SHOW / "settings.json")) != set(refs_settings): raise SystemExit("settings lookup scope mismatch")
ids = {s.get("id") for s in all_inline}
for scene in all_inline:
    for item in scene.get("directionInline", []):
        if item.startswith("Performance:") or item in GENERIC or item.startswith(META_PREFIXES):
            raise SystemExit(f"scene scaffold survived: {scene.get('id')}")
    target = scene.get("continuityFrom")
    if target and target not in ids: raise SystemExit(f"broken continuityFrom: {scene.get('id')} -> {target}")
for handle, cid in [("@starsplit.admiral.colin.rhyne", "C_admiral_colin_rhyne"), ("@starsplit.admiral.janet.keating", "C_admiral_janet_keating")]:
    matches = [k for k,v in chars.items() if v.get("handle") == handle or handle in v.get("aliases", [])]
    if matches != [cid]: raise SystemExit(f"alias does not resolve uniquely: {handle} -> {matches}")
print("Current Rex Fleet sanitation passed")
