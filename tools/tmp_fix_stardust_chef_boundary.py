#!/usr/bin/env python3
from __future__ import annotations

import base64
import gzip
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data" / "shows" / "stardust-station"
MANIFEST = ROOT / "data" / "shows.json"
VALIDATOR = ROOT / "tools" / "validate_stardust_station.py"
SELF = ROOT / "tools" / "tmp_fix_stardust_chef_boundary.py"
WORKFLOW = ROOT / ".github" / "workflows" / "stardust-chef-boundary-repair.yml"

ISSUE_IDS = [f"stardust-station-e{i:02d}" for i in range(2, 11)]
PLAIN_ISSUES = range(4, 11)

GENERATION_LINE = (
    "Finished full-color portrait interior story comic page for Stardust Station. "
    "Bright polished workplace science fiction with clean maintained StarTrust interiors, "
    "natural coworker acting, clear physical props and equipment, varied cinematic sequential composition, "
    "and clean professional integrated lettering. Use released Stardust Station Issue 1 as strict visual canon "
    "for established character identity and world appearance; use approved current-production references for "
    "later continuity state. Preserve scripted panel count, panel order, physical geography, character identity, "
    "prop and equipment state, and exact lettering. Interior story page only; no cover, promotional, dossier, "
    "page-header, character-label, or infographic framing unless explicitly scripted. Fictional production."
)

CHARACTERS = {
    "SDS_Astra": {
        "name": "Astra Vega", "handle": "@sds.Astra",
        "visualAnchor": "Human station manager with purple hair and a composed professional silhouette.",
        "wardrobe": "Polished blue blazer or neat station-management workwear; ID badge; tablet, clipboard or ordinary work orders when scripted.",
        "performance": "Controlled, capable and dry. Show pressure through posture, eyeline and small facial reactions rather than broad mugging.",
        "promptContinuity": ["Keep face, apparent age, body proportions, purple hair and management silhouette consistent with supplied Stardust references."]
    },
    "SDS_Mira": {
        "name": "Mira Klare", "handle": "@sds.Mira",
        "visualAnchor": "Human scientist with a practical, precise workplace appearance.",
        "wardrobe": "White lab coat or science workwear over the established black-hole or eclipse shirt; scanner, sample case or tablet when scripted.",
        "performance": "Observant, understated and exact. Reactions are small and evidence-focused; she handles samples and instruments with practiced care.",
        "promptContinuity": ["Keep face, apparent age, body proportions, hair and established science-work silhouette consistent with supplied Stardust references."]
    },
    "SDS_Jax": {
        "name": "Jax Orien", "handle": "@sds.Jax",
        "visualAnchor": "Human technician with a visible augmented or prosthetic forearm.",
        "wardrobe": "Blue practical workwear; tool belt, access tags, handheld reader or route slate when scripted.",
        "performance": "Physically competent, economical and wry. Casual posture should never erase his attention to access, tools and the job in front of him.",
        "promptContinuity": ["Keep face, apparent age, body proportions, prosthetic forearm and blue technician silhouette consistent with supplied Stardust references."]
    },
    "SDS_Noola": {
        "name": "Noola Vaneel", "handle": "@sds.Noola",
        "visualAnchor": "Aquatic coworker carried in the established transparent water-dome or tank-suit body rig.",
        "wardrobe": "Use the established water-dome or tank-suit hardware and any ordinary work accessories shown by supplied references.",
        "performance": "Calm, readable and economical; communicate attention through eye direction, rig orientation and small deliberate movements.",
        "promptContinuity": ["Keep aquatic body model, apparent scale, water-dome or tank-suit geometry and costume hardware consistent with supplied Stardust references."]
    },
    "SDS_Zib": {
        "name": "Zib “Sgotcha” Diaz", "handle": "@sds.Zib",
        "visualAnchor": "Orange monkey-like fixer with a compact practical maintenance silhouette.",
        "wardrobe": "Yellow utility vest; practical tool belt; tape, wires and maintenance tools when scripted.",
        "performance": "Quick, precise and task-focused. Hands and tools should remain actively engaged with equipment whenever he is working.",
        "promptContinuity": ["Keep species, body model, apparent scale, face and yellow-utility-workwear silhouette consistent with supplied Stardust references."]
    },
    "SDS_Glorp": {
        "name": "Glorp", "handle": "@sds.Glorp",
        "visualAnchor": "Translucent gelatinous office-worker body with the established color treatment and human-scale office silhouette.",
        "wardrobe": "Shirt and tie; binder, forms, labels or stamps when scripted.",
        "performance": "Earnest procedural concentration. Use body shape, eyeline and careful handling of paperwork for reactions rather than exaggerated comedy poses.",
        "promptContinuity": ["Keep gelatinous body model, translucency, color treatment, scale and office-wear silhouette consistent with supplied Stardust references."]
    },
    "SDS_Kreeb": {
        "name": "Kreeb", "handle": "@sds.Kreeb",
        "visualAnchor": "Tall teal-and-yellow insectoid coworker with large yellow-green eyes and long antennae.",
        "wardrobe": "Tailored yellow shirt with teal vest and trousers; formal office-worker silhouette.",
        "performance": "Gentle, deliberate and attentive. Antennae, posture and large eyes carry restrained reactions without caricature.",
        "promptContinuity": ["Keep insectoid body model, relative height, eyes, antennae and yellow-teal formal costume consistent with supplied Stardust references."]
    },
    "SDS_Pixa": {
        "name": "Pixa", "handle": "@sds.Pixa",
        "visualAnchor": "Friendly white-and-blue android or drone-AI body with the established clean interface language.",
        "wardrobe": "No added clothing unless scripted; use integrated screens, projections or compact UI elements when required by the page.",
        "performance": "Helpful, literal and measured. Small body tilts, screen changes and clean gestures carry the acting.",
        "promptContinuity": ["Keep chassis, proportions, white-and-blue treatment and interface design consistent with supplied Stardust references."]
    },
    "SDS_Brick": {
        "name": "Brick Talos", "handle": "@sds.Brick",
        "visualAnchor": "Large stone figure with a broad security silhouette.",
        "wardrobe": "Dark coat and fedora; notebook or security-related prop only when scripted.",
        "performance": "Still, deadpan and physically heavy. Favor minimal movement and small head or eye changes over broad gestures.",
        "promptContinuity": ["Keep stone body model, relative scale, face, dark coat and fedora silhouette consistent with supplied Stardust references."]
    },
    "SDS_Inspector": {
        "name": "Inspector", "handle": "@sds.Inspector",
        "visualAnchor": "Ordinary professional workplace inspector with a neutral, practical silhouette.",
        "wardrobe": "Practical neutral clothing; tablet or checklist when scripted.",
        "performance": "Procedural, dry and observant; composed workplace posture without villainous styling.",
        "promptContinuity": ["Match the supplied released Inspector reference whenever the character recurs."]
    },
    "SDS_Station": {
        "name": "Station System", "handle": "@sds.Station",
        "visualAnchor": "Environmental station presence expressed through built-in displays, indicator lights, speakers and ordinary StarTrust UI.",
        "performance": "Literal system response through environmental interfaces; no facial acting or humanoid body unless the page explicitly scripts one.",
        "promptContinuity": ["Keep the Station System environmental and non-humanoid unless a recipe explicitly introduces a physical embodiment."]
    },
    "SDS_Liaison": {
        "name": "Operations Liaison", "handle": "@sds.Liaison",
        "visualAnchor": "Polished StarTrust operations professional with a distinct ordinary human workplace appearance.",
        "wardrobe": "Clean corporate workwear, temporary visitor badge, compact case or tablet.",
        "performance": "Composed, friendly, curious and professionally credible; never sinister, grandiose or cartoonishly corporate.",
        "promptContinuity": ["Establish a distinct first-appearance design from this anchor; after an approved Liaison reference exists, match that supplied reference exactly."]
    },
}

SETTINGS = {
    "SDS_Admin_Hub": {"name": "Main Bullpen / Admin Hub", "text": "Cramped multi-use workplace hub with desks, rolling carts, open service panels, printers, vents, monitors, corporate signage and the nearby taped-off break-room microwave. Bright, maintained and busy, with readable paths through ordinary workplace clutter."},
    "SDS_West_Corridor": {"name": "West Corridor", "text": "Narrow maintained station corridor with access panels, doors at both ends, safety lighting and a small observation window opening onto spectacular space. Ordinary route markings and service hardware keep the scale workplace-sized."},
    "SDS_Break_Room": {"name": "Break Room", "text": "Ordinary shared employee break room with microwave, vending machine, mismatched chairs, printer and forms, small tables and accumulated workplace residue. Familiar institutional scale with bright maintained surfaces."},
    "SDS_Maintenance_Bay": {"name": "Maintenance Bay", "text": "Bright maintained StarTrust maintenance bay with polished white, blue and metal surfaces, accessible equipment housings, diagnostic displays, workbench, approved clamps and mesh, temporary-repair tags and clear service space. Orderly, fully functional working area."},
    "SDS_Lab_Work_Area": {"name": "Lab Work Area", "text": "Compact immaculate station lab adjoining operations, with sealed physical samples, scanners, test blocks, compression and vibration fixtures, chain-of-custody labels and clean blue-white StarTrust lighting. Instruments and specimens are laid out clearly on practical work surfaces."},
    "SDS_Multipurpose_Room": {"name": "Multipurpose Room", "text": "Clean configurable employee room used for meetings, training and wellness programming; ordinary chairs, portable display screen, environmental monitor and a ventilation-damper service chase with clear physical access."},
    "SDS_Quiet_Room": {"name": "Quiet Room", "text": "Small adjacent employee room with ordinary chairs, drinking water, a simple local sign, uncluttered surfaces and soft neutral station lighting."},
    "SDS_Docking_Vestibule": {"name": "Docking Vestibule", "text": "Bright clean StarTrust docking-entry vestibule with practical hatch hardware, visitor-badge return slot, route markings and a clear transition into the working operations level."},
    "SDS_Galley_Service_Corridor": {"name": "Galley Service Corridor", "text": "Maintained blue-white service corridor behind the station galley with water-manifold cabinet, cable junctions, route markings, utility access and enough working clearance for a small maintenance response."},
    "SDS_Cargo_Bay": {"name": "Cargo Bay / Dock 2", "text": "Clean active station cargo bay with conveyor service lane, Dock 2 latch hardware, access barriers, route tags and shuttle-approach status displays. Maintained logistics equipment and clear physical geography."},
}

REGIONS = {
    "SDS_Stardust_Station": {
        "name": "Stardust Station",
        "text": "Bright, maintained, livable workplace space station with clean readable sci-fi surfaces, ordinary offices, break rooms, labs, service corridors and cargo areas, colorful institutional signage, practical workplace clutter and polished corporate finishes showing everyday wear."
    }
}

FACTIONS = {
    "SDS_Station_Crew": {
        "name": "Stardust Station Crew",
        "text": "Mixed-species StarTrust coworkers in role-specific practical workwear and gear, sharing the same maintained station workspaces at ordinary human workplace scale."
    },
    "SDS_StarTrust": {
        "name": "StarTrust Extractives",
        "text": "Polished blue-white corporate visual language: clean signage, standardized forms and UI, labeled equipment, standardized containers, visitor badges and understated workplace branding."
    },
    "SDS_Inspection": {
        "name": "Morale-and-Safety Inspection",
        "text": "External procedural workplace inspection presence: neutral professional clothing, tablet or checklist, visitor markings and calm observational posture."
    },
}

PROP_PHRASES = [
    "coolant-balancing unit", "stabilizer bracket", "replacement-part tag", "replacement part", "collection rack",
    "collection bins", "collection bin", "sample trays", "sample tray", "sample case", "corporate packet",
    "route slate", "route history", "work board", "work-order sheet", "work orders", "participation table",
    "personal-disclosure envelope", "quiet-room chairs", "vending machine", "context dashboard", "dashboard",
    "service panel", "east hatch", "whistling vent", "cargo conveyor", "conveyor", "Dock 2", "review slate",
    "temporary bracket", "temporary repair", "custody slips", "custody labels", "handheld flow reader", "flow reader",
    "temporary-material-usage form", "wellness banner", "forms", "printer", "microwave", "sample"
]

META_RE = re.compile(
    r"\b(?:proves?|proving|establish(?:es|ed|ing)?|payoff|pays\s+off|setup|sets\s+up|"
    r"story\s+beat|the\s+story|the\s+issue|the\s+series|the\s+arc|dramatic\s+engine|"
    r"writing|writer|lesson|comic\s+context|page\s+feel|key\s+image|rather\s+than\s+preachy)\b",
    re.IGNORECASE,
)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def decode(path: Path):
    raw = "".join(path.read_text(encoding="utf-8").split())
    return json.loads(gzip.decompress(base64.b64decode(raw, validate=True)).decode("utf-8"))


def encode(path: Path, payload):
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    compressed = gzip.compress(data, mtime=0)
    b64 = base64.b64encode(compressed).decode("ascii")
    path.write_text("\n".join(b64[i:i+76] for i in range(0, len(b64), 76)) + "\n", encoding="utf-8")


def issue_no(page_id: str) -> int:
    m = re.search(r"S1E(\d+)", page_id)
    if not m:
        raise AssertionError(f"Cannot parse issue from {page_id}")
    return int(m.group(1))


def panel_body(text: str) -> str:
    return re.sub(r"^\s*PANEL\s+\d+\s*[—-]\s*", "", text, flags=re.IGNORECASE).strip()


def visual_clause(text: str) -> str:
    body = panel_body(text)
    # Dialogue embedded in some late page plans should not be duplicated into the page-level composition line.
    body = re.split(r"\s\b[A-Z][A-Z0-9 _-]{1,24}:\s", body, maxsplit=1)[0].strip()
    return body.rstrip(".")


def setting_label(page: dict) -> str:
    key = page.get("setting")
    if key in SETTINGS:
        return SETTINGS[key]["name"]
    text = str(page.get("settingText") or "Stardust Station workplace location").strip()
    return text.split(";")[0].split(".")[0].strip()


def direct_summary(page: dict) -> str:
    panels = page.get("panelPlan") or []
    n = len(panels)
    clauses = [visual_clause(item.get("text", "")) for item in panels if isinstance(item, dict) and item.get("text")]
    clauses = [c for c in clauses if c]
    if not clauses:
        raise AssertionError(f"{page.get('id')}: no visual clauses")
    first = clauses[0]
    middle = clauses[len(clauses)//2]
    last = clauses[-1]
    return f"Primary composition: {n}-panel page in {setting_label(page)}. Open on {first}. Mid-page: {middle}. Finish on {last}."


def page_props(page: dict) -> list[str]:
    text = " ".join(str(item.get("text", "")) for item in page.get("panelPlan", []) if isinstance(item, dict)).lower()
    out = []
    for phrase in PROP_PHRASES:
        if phrase.lower() in text and phrase not in out:
            out.append(phrase)
        if len(out) == 2:
            break
    return out


def clean_meta_panel(text: str) -> str:
    original = text
    # Known writer-judgment phrasing from the late-season enhancement pass.
    text = text.replace(
        "Astra makes the wrong call. ASTRA: Do it.",
        "Astra looks at the six-day-early conveyor-service schedule, then gives Zib the go-ahead. ASTRA: Do it.",
    )
    # Remove trailing explanation clauses that tell the image model why a physical beat was written.
    text = re.sub(r",\s*(?:proving|establishing|reinforcing|paying off|setting up|making the contrast|turning the evidence|turning his evidence)\b[^.]*", "", text, flags=re.IGNORECASE)
    # Remove standalone writer-room sentences while retaining physical action around them.
    sentences = re.split(r"(?<=[.!?])\s+", text)
    kept = []
    for sentence in sentences:
        if re.search(r"\b(?:the story|the issue|the series|the arc|this page|story beat|comic context|writing lesson)\b", sentence, re.IGNORECASE):
            continue
        kept.append(sentence)
    text = " ".join(kept).strip()
    if not text:
        return original
    return text


def enrich_short_panels(page: dict) -> int:
    if issue_no(page["id"]) < 4:
        return 0
    panels = page.get("panelPlan") or []
    props = page_props(page)
    place = setting_label(page)
    changed = 0
    for idx, item in enumerate(panels, 1):
        if not isinstance(item, dict) or not isinstance(item.get("text"), str):
            continue
        old = clean_meta_panel(item["text"])
        body = panel_body(old)
        # Keep already useful physical descriptions intact.
        words = re.findall(r"[A-Za-z0-9’'-]+", body)
        if len(words) >= 9:
            if old != item["text"]:
                item["text"] = old
                changed += 1
            continue
        lower = body.lower()
        if idx == 1:
            shot = "Wide establishing shot"
        elif idx == len(panels):
            shot = "Tighter closing shot"
        elif re.search(r"\b(looks?|stares?|nods?|exhales?|freezes?|hesitates?|waits?|considers?|reads?|watches?|glances?)\b", lower):
            shot = "Medium-close reaction shot"
        else:
            shot = "Medium workplace shot"
        context = f"{shot} in the {place}. {body}"
        if props:
            context += " Keep " + " and ".join(f"the {p}" for p in props) + " visible in the frame."
        else:
            context += " Keep the active workplace surface, nearby equipment and current prop state visible."
        number = re.match(r"^\s*(PANEL\s+\d+)\s*[—-]", old, re.IGNORECASE)
        prefix = number.group(1).upper() if number else f"PANEL {idx}"
        item["text"] = f"{prefix} — {context}"
        changed += 1
    return changed


def sanitize_page(page: dict) -> tuple[int, int]:
    old_summary = page.get("summary", "")
    page["summary"] = direct_summary(page)
    summary_changed = int(page["summary"] != old_summary)
    panel_changed = enrich_short_panels(page)
    # Clean writer-room residue in all panel plans, including the already-detailed I2-I3 pages.
    for item in page.get("panelPlan") or []:
        if not isinstance(item, dict) or not isinstance(item.get("text"), str):
            continue
        cleaned = clean_meta_panel(item["text"])
        if cleaned != item["text"]:
            item["text"] = cleaned
            panel_changed += 1
    return summary_changed, panel_changed


def replace_json_value(raw: str, key: str, old: str, new: str) -> str:
    if old == new:
        return raw
    old_json = json.dumps(old, ensure_ascii=False)
    new_json = json.dumps(new, ensure_ascii=False)
    pattern = re.compile(rf'("{re.escape(key)}"\s*:\s*){re.escape(old_json)}')
    raw2, count = pattern.subn(lambda m: m.group(1) + new_json, raw, count=1)
    if count != 1:
        raise AssertionError(f"Could not replace {key}: {old[:80]}")
    return raw2


def sanitize_plain_file(path: Path) -> tuple[int, int]:
    raw = path.read_text(encoding="utf-8")
    pages = json.loads(raw)
    summary_changes = 0
    panel_changes = 0
    for page in pages:
        old_summary = page["summary"]
        old_panels = [item.get("text") for item in page.get("panelPlan", [])]
        old_setting_text = page.get("settingText")
        s, p = sanitize_page(page)
        summary_changes += s
        panel_changes += p
        raw = replace_json_value(raw, "summary", old_summary, page["summary"])
        for old, item in zip(old_panels, page.get("panelPlan", [])):
            if old is not None and old != item.get("text"):
                raw = replace_json_value(raw, "text", old, item["text"])
        if old_setting_text and META_RE.search(old_setting_text):
            cleaned = re.sub(r"\s*Keep every beat grounded[^.]*\.?", "", old_setting_text, flags=re.IGNORECASE).strip()
            if cleaned != old_setting_text:
                page["settingText"] = cleaned
                raw = replace_json_value(raw, "settingText", old_setting_text, cleaned)
    path.write_text(raw, encoding="utf-8")
    return summary_changes, panel_changes


def manifest_entries():
    return {entry["id"]: entry for entry in load(MANIFEST) if entry.get("id") in ISSUE_IDS}


def sanitize_encoded_issues(entries: dict) -> tuple[int, int]:
    summary_changes = 0
    panel_changes = 0
    for show_id in ("stardust-station-e02", "stardust-station-e03"):
        for overlay in entries[show_id]["sceneOverlays"]:
            path = SHOW / overlay["file"]
            payload = decode(path)
            pages = payload.get("pages") if isinstance(payload, dict) else payload
            assert isinstance(pages, list)
            for page in pages:
                s, p = sanitize_page(page)
                summary_changes += s
                panel_changes += p
            encode(path, payload)
    return summary_changes, panel_changes


def clean_manifest_generation_lines():
    raw = MANIFEST.read_text(encoding="utf-8")
    replacement = json.dumps(GENERATION_LINE, ensure_ascii=False)
    count = 0
    for show_id in ISSUE_IDS:
        pattern = re.compile(
            rf'("id"\s*:\s*"{re.escape(show_id)}".*?"generationLine"\s*:\s*)"(?:\\.|[^"\\])*"',
            re.DOTALL,
        )
        raw, n = pattern.subn(lambda m: m.group(1) + replacement, raw, count=1)
        if n != 1:
            raise AssertionError(f"Could not replace generationLine for {show_id}")
        count += n
    MANIFEST.write_text(raw, encoding="utf-8")
    return count


def update_validator():
    text = VALIDATOR.read_text(encoding="utf-8")
    old = '''    if handle in CORE_HANDLES:\n        assert isinstance(character.get("visualAnchor"), str) and character["visualAnchor"].strip(), f"{key}: core character missing visualAnchor"\n        locks = character.get("continuityLocks")\n        assert isinstance(locks, list) and locks and all(isinstance(item, str) and item.strip() for item in locks), f"{key}: core character missing continuityLocks"\n        status = character.get("visualStatus")\n        assert isinstance(status, str) and status.strip(), f"{key}: core character missing visualStatus"\n\nassert isinstance(characters.get("SDS_Station", {}).get("visualStatus"), str), "Station System must define non-humanoid visual status"\nassert isinstance(characters.get("SDS_Liaison", {}).get("visualAnchor"), str), "Operations Liaison must define a provisional visual anchor"\n'''
    new = '''    if handle in CORE_HANDLES:\n        assert isinstance(character.get("visualAnchor"), str) and character["visualAnchor"].strip(), f"{key}: core character missing visualAnchor"\n        assert isinstance(character.get("performance"), str) and character["performance"].strip(), f"{key}: core character missing image-facing performance"\n        locks = character.get("promptContinuity")\n        assert isinstance(locks, list) and locks and all(isinstance(item, str) and item.strip() for item in locks), f"{key}: core character missing promptContinuity"\n\nassert isinstance(characters.get("SDS_Station", {}).get("visualAnchor"), str), "Station System must define environmental visual anchor"\nassert isinstance(characters.get("SDS_Liaison", {}).get("visualAnchor"), str), "Operations Liaison must define a provisional visual anchor"\n'''
    if old not in text:
        raise AssertionError("Validator character block drifted")
    text = text.replace(old, new)

    old2 = '''    if show_id != "stardust-station":\n        assert "released Issue 1 interior-story visual canon" in generation_line, f"{show_id}: released interior-story canon lock missing"\n        assert "no cover, title banner, page header, character labels" in generation_line, f"{show_id}: page-style contamination exclusion missing"\n        assert "approved" in generation_line and "continuity" in generation_line, f"{show_id}: approved-production continuity rule missing"\n'''
    new2 = '''    if show_id != "stardust-station":\n        assert "released Stardust Station Issue 1" in generation_line, f"{show_id}: released visual canon lock missing"\n        assert "approved current-production" in generation_line, f"{show_id}: approved-production continuity rule missing"\n        assert "physical geography" in generation_line and "prop and equipment state" in generation_line, f"{show_id}: physical continuity contract missing"\n        assert "Interior story page only" in generation_line, f"{show_id}: interior-page scope missing"\n'''
    if old2 not in text:
        raise AssertionError("Validator generationLine block drifted")
    text = text.replace(old2, new2)

    marker = '''        panel_plan = page.get("panelPlan")\n        assert isinstance(panel_plan, list) and panel_plan, f"{page_id}: missing panelPlan"\n'''
    insert = '''        panel_plan = page.get("panelPlan")\n        assert isinstance(panel_plan, list) and panel_plan, f"{page_id}: missing panelPlan"\n        if show_id != "stardust-station":\n            assert page["summary"].startswith("Primary composition:"), f"{page_id}: chef-facing summary must be direct primary composition"\n            recipe_visual_text = [page["summary"], str(page.get("settingText", ""))]\n            recipe_visual_text.extend(str(item.get("text", "")) for item in panel_plan if isinstance(item, dict))\n            forbidden = re.compile(r"\\b(?:proves?|proving|establish(?:es|ed|ing)?|payoff|pays\\s+off|story\\s+beat|the\\s+story|the\\s+issue|the\\s+series|the\\s+arc|dramatic\\s+engine|writing|writer|lesson|comic\\s+context|page\\s+feel|key\\s+image|rather\\s+than\\s+preachy)\\b", re.IGNORECASE)\n            leaks = [value for value in recipe_visual_text if forbidden.search(value)]\n            assert not leaks, f"{page_id}: writer-room reasoning leaked into image recipe: {leaks[0]}"\n            match = re.search(r"S1E(\\d+)", page_id)\n            if match and int(match.group(1)) >= 4:\n                for item in panel_plan:\n                    panel_text = str(item.get("text", "")) if isinstance(item, dict) else str(item)\n                    body = re.sub(r"^\\s*PANEL\\s+\\d+\\s*[—-]\\s*", "", panel_text, flags=re.IGNORECASE)\n                    assert len(re.findall(r"[A-Za-z0-9’'-]+", body)) >= 8, f"{page_id}: visually underspecified panel: {panel_text}"\n'''
    if marker not in text:
        raise AssertionError("Validator panel marker drifted")
    text = text.replace(marker, insert)
    VALIDATOR.write_text(text, encoding="utf-8")


def audit_all(entries: dict):
    failures = []
    summaries = 0
    panels = 0
    for show_id, entry in entries.items():
        for overlay in entry["sceneOverlays"]:
            path = SHOW / overlay["file"]
            payload = decode(path) if overlay.get("encoding") else load(path)
            pages = payload.get("pages") if isinstance(payload, dict) else payload
            for page in pages:
                summaries += 1
                if not str(page.get("summary", "")).startswith("Primary composition:"):
                    failures.append((page.get("id"), "summary", page.get("summary")))
                fields = [("summary", page.get("summary", "")), ("settingText", page.get("settingText", ""))]
                fields.extend(("panel", item.get("text", "")) for item in page.get("panelPlan", []) if isinstance(item, dict))
                for kind, value in fields:
                    if META_RE.search(str(value)):
                        failures.append((page.get("id"), kind, value))
                if issue_no(page["id"]) >= 4:
                    for item in page.get("panelPlan", []):
                        body = panel_body(str(item.get("text", "")))
                        if len(re.findall(r"[A-Za-z0-9’'-]+", body)) < 8:
                            failures.append((page.get("id"), "short-panel", item.get("text")))
                        panels += 1
    if failures:
        print("CHEF BOUNDARY FAILURES:")
        for failure in failures[:80]:
            print(" -", failure)
        raise AssertionError(f"Chef-boundary audit found {len(failures)} failures")
    print("Chef-boundary audit passed")
    print("Unreleased Stardust summaries checked:", summaries)
    print("Issue 4-10 panels checked for visual specificity:", panels)


def main():
    entries = manifest_entries()
    assert set(entries) == set(ISSUE_IDS), f"Missing Stardust entries: {set(ISSUE_IDS) - set(entries)}"

    # Snapshot story-bearing dialogue before any transformation.
    before_dialogue = {}
    for show_id, entry in entries.items():
        for overlay in entry["sceneOverlays"]:
            path = SHOW / overlay["file"]
            payload = decode(path) if overlay.get("encoding") else load(path)
            pages = payload.get("pages") if isinstance(payload, dict) else payload
            for page in pages:
                before_dialogue[page["id"]] = page.get("dialogueInline")

    (SHOW / "characters.json").write_text(json.dumps(CHARACTERS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (SHOW / "settings.json").write_text(json.dumps(SETTINGS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (SHOW / "regions.json").write_text(json.dumps(REGIONS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (SHOW / "factions.json").write_text(json.dumps(FACTIONS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    generation_count = clean_manifest_generation_lines()
    s_encoded, p_encoded = sanitize_encoded_issues(entries)
    s_plain = p_plain = 0
    for issue in PLAIN_ISSUES:
        s, p = sanitize_plain_file(SHOW / f"pages_e{issue:02d}.json")
        s_plain += s
        p_plain += p

    update_validator()

    # Reload manifest after generation-line changes; overlays are unchanged.
    entries_after = manifest_entries()
    audit_all(entries_after)

    after_dialogue = {}
    for show_id, entry in entries_after.items():
        for overlay in entry["sceneOverlays"]:
            path = SHOW / overlay["file"]
            payload = decode(path) if overlay.get("encoding") else load(path)
            pages = payload.get("pages") if isinstance(payload, dict) else payload
            for page in pages:
                after_dialogue[page["id"]] = page.get("dialogueInline")
    assert before_dialogue == after_dialogue, "Dialogue regression detected during chef-boundary rewrite"

    print("Generation lines rewritten:", generation_count)
    print("Summaries rewritten:", s_encoded + s_plain)
    print("Panel instructions expanded/cleaned:", p_encoded + p_plain)
    print("Character, setting, region and faction shelves rewritten as image-facing data")
    print("Dialogue regression check passed")

    # Temporary machinery must not remain in the production diff.
    if WORKFLOW.exists():
        WORKFLOW.unlink()
    if SELF.exists():
        SELF.unlink()


if __name__ == "__main__":
    main()
