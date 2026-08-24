#!/usr/bin/env python3
"""Sanitize Backyard Rockets production data without changing authored story content."""
from __future__ import annotations

import base64
import copy
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW_ID = "backyard-rockets-s1"
SHOW = ROOT / "data" / "shows" / SHOW_ID
MANIFEST = ROOT / "data" / "shows.json"

DROP_DIRECTION_PREFIXES = (
    "BACKYARD ROCKETS VISUAL LANGUAGE:",
    "TETHERGRID DOCUMENTARY LANGUAGE:",
    "DRYLINE DOCUMENTARY LANGUAGE:",
    "SCENE ACTION — SOURCE-LOCKED:",
    "CHARACTER CONTINUITY —",
    "PRESENTER CONTINUITY —",
    "LOCATION / PROP / STATE CONTINUITY —",
    "LOCATION / GRAPHIC CONTINUITY —",
    "CAMERA / LIGHT —",
    "CAMERA / EDITORIAL GRAMMAR —",
)

SETTING_MAP = {
    "Community water-coordination room — practical municipal tables, printed basin maps, physical ledgers, rugged radios, pump telemetry and ordinary maintained public infrastructure.": "BR_Community_Water_Coordination_Room",
    "Tethergrid mobile command platform — immaculate graphite corporate hardware, brushed alloy, tactile/glass controls, restrained cyan/amber status light and Mojave terrain beyond.": "BR_Tethergrid_Mobile_Command_Platform",
    "Launch-Shop mobile control cabin — compact maintained retro-aerospace controls, analog gauges, physical switches, restrained digital readouts and bright Mojave light through the windows.": "BR_Launch_Shop_Control_Cabin",
    "Mobile Launch-Shop tanker workshop — maintained retro-industrial aerospace interior, painted metal, tactile analog-digital instruments, organized tools, practical task lighting and controlled localized wear.": "BR_Launch_Shop_Tanker_Workshop",
    "Mojave field launch site — maintained hand-built aerospace hardware, compact support equipment, practical rigging, hard desert light and broad unobstructed sky.": "BR_Mojave_Field_Launch_Site",
    "Community wellhead and pump yard — maintained water hardware, sun-bleached concrete, shade structure, visible mechanical gauges, clear piping state and hard Mojave daylight.": "BR_Community_Wellhead_Pump_Yard",
    "Launch-Shop exterior work deck — maintained tanker/flatbed structure, organized field hardware, hard Mojave sun and broad desert horizon.": "BR_Launch_Shop_Exterior_Work_Deck",
    "Mojave limestone ridge — pale fractured stone, bright high-desert sun, long sightlines, sparse scrub and the launch corridor below.": "BR_Mojave_Limestone_Ridge",
    "Public Sky ground-relay site — maintained mast, compact solar power, tactile control box, physical status lamps and open Mojave terrain with line-of-sight to neighboring ridges.": "BR_Public_Sky_Ground_Relay_Site",
    "Remote propulsion test stand — reinforced concrete, clear exclusion zone, instrumented test article, shielded observation position and bright open desert.": "BR_Remote_Propulsion_Test_Stand",
    "Tethergrid mobile interception platform — immaculate graphite corporate hardware, brushed alloy, tactile/glass controls, restrained cyan/amber status light, Mojave terrain beyond.": "BR_Tethergrid_Mobile_Interception_Platform",
    "Decommissioned hydroelectric service gallery — massive concrete structure, damp cool air, old mechanical governors, steel railings, moss at exposed spillway edges and safe portable work lighting.": "BR_Decommissioned_Hydroelectric_Service_Gallery",
    "Mobile Launch-Shop tanker interior — maintained retro-industrial aerospace workshop, painted metal, tactile analog-digital instruments, organized tools, practical task lighting and controlled localized wear.": "BR_Launch_Shop_Tanker_Interior",
    "Mobile Sky-Piercer launch route inside a Mojave sandstorm — low visibility, disciplined vehicle lighting, secured hardware, blowing grit and intermittent amber desert light.": "BR_Sky_Piercer_Sandstorm_Route",
}

CHARACTERS = {
    "hv9jfbgm9": {
        "name": "Arvin", "handle": "@brk.Arvin", "modelSheet": "Arvin: Southwest solar-wave engineer.png",
        "visualAnchor": "Lean, narrow, angular older aerospace architect with deeply tanned olive skin, short steel-gray hair, heavy-lidded dark amber eyes, olive utility jacket with blue solar-cell shoulder straps, practical canvas work trousers and field boots. His pale synthetic graft is on the RIGHT HAND; the left hand is natural.",
        "continuityLocks": ["synthetic graft is right hand only", "lean narrow angular build", "short steel-gray hair", "olive utility jacket with blue solar-cell shoulder straps"],
    },
    "5snrx2won": {
        "name": "Milo", "handle": "@brk.Milo", "modelSheet": "Milo's Southwest retro-tech character sheet.png",
        "visualAnchor": "Broad, grounded engineer with desert-clay skin, a round youthful face, dense dark curls and fixed facial cybernetic markings. Brown mechanical vest over a dark work shirt, practical field trousers, real-scale tool belt and rugged boots.",
        "continuityLocks": ["broad grounded build", "dense dark curls", "fixed facial cybernetic markings", "brown mechanical vest over dark work shirt"],
    },
    "8tg8ibh7z": {
        "name": "Lucia", "handle": "@brk.Lucia", "modelSheet": "Lucia: Retro-Solar Desert Tactician.png",
        "visualAnchor": "Athletic fair-skinned woman with high cheekbones, skeptical brow, black asymmetric razor-cut hair, dark tactical field jacket with restrained cyan piping, fitted practical field trousers and polished black combat boots.",
        "continuityLocks": ["black asymmetric razor-cut hair", "athletic high-cheekboned face", "dark tactical field jacket with restrained cyan piping", "polished black combat boots"],
    },
    "dljv31xue": {
        "name": "Cyrus", "handle": "@brk.Cyrus", "modelSheet": "Cyrus: Graphite interceptor character sheet.png", "role": "Tethergrid executive enforcer",
        "visualAnchor": "Broad-shouldered older man with silvered hair, weathered skin and pale blue eyes. Immaculately fitted graphite technical armor with minimal seams, restrained amber-cyan status lines and heavy matte-black tactical boots.",
        "continuityLocks": ["older broad-shouldered build", "silvered hair and pale blue eyes", "graphite technical armor with restrained amber-cyan status lines", "immaculate fit and minimal seams"],
    },
    "tamz": {
        "name": "Tamz", "handle": "@brk.Tamz", "modelSheet": "Tamz, solar-wave desert scout.png", "role": "desert scout",
        "visualAnchor": "Desert scout with braided hair, a strong grounded stance, gray field jacket, practical cargo trousers and expedition gear with intentional patch or insignia wear.",
        "continuityLocks": ["braided hair", "strong grounded stance", "gray field jacket", "practical cargo trousers"],
    },
    "tamsin": {
        "name": "Tamsin", "handle": "@brk.Tamsin", "role": "community water-systems operator",
        "visualAnchor": "Medium build, warm brown skin, dark brown hair in a low ponytail, faded indigo work shirt, light canvas utility vest with water-system tags, tan field trousers, practical boots and clear safety glasses at the collar.",
        "continuityLocks": ["low dark-brown ponytail", "faded indigo work shirt", "light canvas water-systems utility vest", "tan field trousers and practical boots", "clear safety glasses clipped at collar"],
    },
    "@brk.TetherwellNarrator": {"name": "Tetherwell Narrator", "handle": "@brk.TetherwellNarrator", "presentation": "voice-over only"},
    "@brk.DrylineReporter": {"name": "Dryline Reporter", "handle": "@brk.DrylineReporter", "presentation": "voice-over only"},
}

REGIONS = {
    "BR_Mojave": {"text": "Immense sunlit American Southwest high desert with sandstone cliffs, mesas, dry lake beds, slot canyons, escarpments and long clear horizons. Working sites are purposeful field environments integrated into the terrain."}
}

FACTIONS = {
    "BR_Salvagers": {"text": "Launch-Shop engineers use maintained older-generation aerospace hardware, rugged field equipment, painted and brushed metal, canvas, tactile analog-digital instruments and warm solar-wave retrofuturist forms."},
    "BR_Tethergrid": {"text": "Tethergrid Corp operates the Tetherwell water-authorization network. Its current-generation corporate design uses graphite, brushed aluminum, carbon composite, technical ceramic, precise seams, restrained cyan instrumentation, robotics and automation."},
    "BR_Dryline": {"text": "The Dryline Report is independent investigative journalism focused on water access, allocation records and physical infrastructure, using field footage, documents, restrained annotations and evidence-first reporting."},
}

ORPHAN_PACKAGE_FILES = [
    "blocking.json", "dialogue.json", "direction.json", "lighting.json", "mood.json", "negatives.json",
    "dialogue-adaptation-notes.md", "dialogue-voice-rewrites.json", "documentary-interstitials.json",
]
LEGACY_TOOLS = [
    "apply_backyard_rockets_voice_rewrites.py", "expand_backyard_rockets_dialogue.py", "fix_backyard_rockets_continuity.py",
    "insert_backyard_rockets_documentary_interstitials.py", "reconcile_backyard_rockets_dialogue_cast.py",
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def decode(path: Path):
    raw = base64.b64decode("".join(path.read_text(encoding="utf-8").split()), validate=True)
    return json.loads(gzip.decompress(raw).decode("utf-8"))


def encode(path: Path, value) -> None:
    raw = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    path.write_text(base64.b64encode(gzip.compress(raw, compresslevel=9, mtime=0)).decode("ascii"), encoding="utf-8")


def semantic_fingerprint(scene: dict) -> dict:
    out = copy.deepcopy(scene)
    out.pop("directionInline", None)
    out.pop("direction", None)
    out.pop("regionText", None)
    out.pop("region", None)
    out.pop("settingText", None)
    out.pop("setting", None)
    out["charactersInline"] = [(c.get("name"), c.get("handle")) for c in scene.get("charactersInline", []) if isinstance(c, dict)]
    out["dialogueInline"] = [(d.get("speaker"), d.get("handle"), d.get("text")) for d in scene.get("dialogueInline", []) if isinstance(d, dict)]
    return out


def sanitize_scene(scene: dict) -> tuple[dict, int]:
    before = semantic_fingerprint(scene)
    out = copy.deepcopy(scene)
    removed = 0

    kept = []
    for item in out.get("directionInline", []) or []:
        if isinstance(item, dict) and str(item.get("text", "")).startswith(DROP_DIRECTION_PREFIXES):
            removed += 1
        else:
            kept.append(item)
    if kept:
        out["directionInline"] = kept
    else:
        out.pop("directionInline", None)
    out.pop("direction", None)

    out["charactersInline"] = [
        {k: c[k] for k in ("name", "handle") if isinstance(c, dict) and c.get(k)}
        for c in out.get("charactersInline", []) if isinstance(c, dict)
    ]
    out["dialogueInline"] = [
        {k: d[k] for k in ("speaker", "handle", "text") if isinstance(d, dict) and d.get(k) is not None}
        for d in out.get("dialogueInline", []) if isinstance(d, dict)
    ]

    out["region"] = out.get("region") or "BR_Mojave"
    out.pop("regionText", None)

    setting_text = out.get("settingText")
    if setting_text in SETTING_MAP:
        out["setting"] = SETTING_MAP[setting_text]
        out.pop("settingText", None)

    after = semantic_fingerprint(out)
    if before != after:
        raise RuntimeError(f"Sanitization changed authored story content on {scene.get('id')}")
    return out, removed


def active_payloads():
    shows = load(MANIFEST)
    show = next(s for s in shows if s.get("id") == SHOW_ID)
    for overlay in show.get("sceneOverlays", []):
        yield SHOW / overlay["file"], overlay.get("encoding")


def sanitize_payloads() -> tuple[int, int]:
    count = removed = 0
    for path, encoding in active_payloads():
        data = decode(path) if encoding == "gzip-base64" else load(path)
        if not isinstance(data, list):
            raise RuntimeError(f"Expected list payload in {path}")
        cleaned = []
        for scene in data:
            fixed, n = sanitize_scene(scene)
            cleaned.append(fixed)
            count += 1
            removed += n
        if encoding == "gzip-base64":
            encode(path, cleaned)
        else:
            dump(path, cleaned)
    return count, removed


def sanitize_registries() -> None:
    dump(SHOW / "characters.json", CHARACTERS)
    dump(SHOW / "regions.json", REGIONS)
    dump(SHOW / "factions.json", FACTIONS)
    settings = {sid: {"text": text} for text, sid in SETTING_MAP.items()}
    dump(SHOW / "settings.json", settings)


def remove_residue() -> tuple[int, int]:
    package_removed = 0
    for rel in ORPHAN_PACKAGE_FILES:
        p = SHOW / rel
        if p.exists():
            p.unlink(); package_removed += 1
    raw = SHOW / "raw"
    if raw.exists():
        for p in raw.glob("*"):
            if p.is_file():
                p.unlink(); package_removed += 1
        try:
            raw.rmdir()
        except OSError:
            pass
    tools_removed = 0
    for name in LEGACY_TOOLS:
        p = ROOT / "tools" / name
        if p.exists():
            p.unlink(); tools_removed += 1
    return package_removed, tools_removed


if __name__ == "__main__":
    scenes, blocks = sanitize_payloads()
    sanitize_registries()
    package_removed, tools_removed = remove_residue()
    print(f"Sanitized {scenes} Backyard Rockets scenes")
    print(f"Removed {blocks} repeated scene-scope production blocks")
    print(f"Removed {package_removed} orphan/stale package artifacts")
    print(f"Removed {tools_removed} retired one-off migration tools")
