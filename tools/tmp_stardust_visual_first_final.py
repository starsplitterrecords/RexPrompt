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
SELF = ROOT / "tools" / "tmp_stardust_visual_first_final.py"
WORKFLOW = ROOT / ".github" / "workflows" / "stardust-visual-first-final.yml"

ISSUE_IDS = [f"stardust-station-e{i:02d}" for i in range(2, 11)]
GENERATION_LINE = (
    "Finished full-color portrait interior story comic page for Stardust Station. "
    "Bright polished workplace science fiction with clean maintained StarTrust interiors, natural coworker acting, "
    "clear physical props and equipment, varied cinematic sequential composition, and clean professional integrated lettering. "
    "Use released Stardust Station Issue 1 as strict visual canon for established character identity and world appearance; "
    "use approved current-production references for later continuity state. Preserve scripted panel count and order, physical geography, "
    "character identity, prop and equipment state, and exact lettering. Interior story page only; no cover, promotional, dossier, "
    "page-header, character-label, or infographic framing unless explicitly scripted. Fictional production."
)

SETTING_TEXT = {
    "SDS_Admin_Hub": "Cramped multi-use workplace hub with desks, rolling carts, open service panels, printers, vents, monitors, corporate signage and the nearby taped-off break-room microwave. Bright, maintained and busy, with readable paths through ordinary workplace clutter.",
    "SDS_West_Corridor": "Narrow maintained station corridor with access panels, doors at both ends, safety lighting and a small observation window opening onto spectacular space. Ordinary route markings and service hardware keep the scale workplace-sized.",
    "SDS_Break_Room": "Ordinary shared employee break room with microwave, vending machine, mismatched chairs, printer and forms, small tables and accumulated workplace residue. Familiar institutional scale with bright maintained surfaces.",
    "SDS_Maintenance_Bay": "Bright maintained StarTrust maintenance bay with polished white, blue and metal surfaces, accessible equipment housings, diagnostic displays, workbench, approved clamps and mesh, temporary-repair tags and clear service space. Orderly, fully functional working area.",
    "SDS_Lab_Work_Area": "Compact immaculate station lab adjoining operations, with sealed physical samples, scanners, test blocks, compression and vibration fixtures, chain-of-custody labels and clean blue-white StarTrust lighting. Instruments and specimens are laid out clearly on practical work surfaces.",
    "SDS_Multipurpose_Room": "Clean configurable employee room used for meetings, training and wellness programming; ordinary chairs, portable display screen, environmental monitor and a ventilation-damper service chase with clear physical access.",
    "SDS_Quiet_Room": "Small adjacent employee room with ordinary chairs, drinking water, a simple local sign, uncluttered surfaces and soft neutral station lighting.",
    "SDS_Docking_Vestibule": "Bright clean StarTrust docking-entry vestibule with practical hatch hardware, visitor-badge return slot, route markings and a clear transition into the working operations level.",
    "SDS_Galley_Service_Corridor": "Maintained blue-white service corridor behind the station galley with water-manifold cabinet, cable junctions, route markings, utility access and enough working clearance for a small maintenance response.",
    "SDS_Cargo_Bay": "Clean active station cargo bay with conveyor service lane, Dock 2 latch hardware, access barriers, route tags and shuttle-approach status displays. Maintained logistics equipment and clear physical geography.",
}

REGION_TEXT = "Bright, maintained, livable workplace space station with clean readable sci-fi surfaces, ordinary offices, break rooms, labs, service corridors and cargo areas, colorful institutional signage, practical workplace clutter and polished corporate finishes showing everyday wear."
FACTION_TEXT = {
    "SDS_Station_Crew": "Mixed-species StarTrust coworkers in role-specific practical workwear and gear, sharing the same maintained station workspaces at ordinary human workplace scale.",
    "SDS_StarTrust": "Polished blue-white corporate visual language: clean signage, standardized forms and UI, labeled equipment, standardized containers, visitor badges and understated workplace branding.",
    "SDS_Inspection": "External procedural workplace inspection presence: neutral professional clothing, tablet or checklist, visitor markings and calm observational posture.",
}

WRITER_META = re.compile(
    r"\b(?:story\s+beat|the\s+story|the\s+series|the\s+arc|dramatic\s+engine|writer[- ]room|writerly|"
    r"page\s+feel|key\s+image|causal\s+spine|reader\s+function|payoff|pays\s+off|proves?|proving|"
    r"rather\s+than\s+preachy|institutionally\s+rather\s+than|scientifically\s+rather\s+than)\b",
    re.IGNORECASE,
)
ISSUE_PROVENANCE = re.compile(r"\b(?:from\s+)?Issue\s+\d+\b", re.IGNORECASE)

NAMES = ["Astra", "Mira", "Jax", "Zib", "Glorp", "Kreeb", "Pixa", "Brick", "Liaison", "Noola", "Inspector"]
WEAK_VERBS = (
    "nods", "nods once", "agrees", "looks up", "does not look up", "stops", "turns", "shrugs",
    "keeps working", "continues", "waits", "relaxes slightly", "looks around the station",
)

EXACT_REWRITES = {
    "Astra makes the wrong call. ASTRA: Do it.": "Astra studies the six-day-early conveyor-service schedule, jaw tight, then gives Zib the go-ahead. ASTRA: Do it.",
    "Mira immediately qualifies it.": "Mira raises one hand before anyone reacts, cautious expression fixed on the test result.",
    "Zib refuses to over-credit it.": "Zib studies the patch skeptically, one hand still on the approved clamp.",
    "Glorp reluctantly reduces the procedure to three required fields.": "Glorp deletes lines from the form until only three labeled fields remain.",
    "Mira sets the sequence.": "Mira lays out three test cards beside the rig: HEAT / COMPRESSION / VIBRATION.",
    "Pixa displays only the physical result.": "Pixa's display shows measured flow and patch status only, without an explanatory headline.",
    "She shows the reporting requirement.": "Mira turns the screen toward Astra and highlights the REPORT REQUIRED field.",
    "Kreeb answers calmly.": "Kreeb meets Glorp's eyes over the tablet, antennae still and posture relaxed.",
    "The report waits on the station manager signature.": "The terminal shows a blank STATION MANAGER SIGNATURE field above the SEND control.",
    "Astra checks the causal language.": "Astra traces one sentence on the report with a fingertip, pausing over the highlighted causal wording.",
    "Mira answers the part Astra cannot dismiss.": "Mira meets Astra's eyes across the workbench, calm and firm.",
    "Astra hears the phrase from across the bay.": "Across the bay, Astra turns toward them at the phrase.",
    "Astra's expression changes.": "Astra's face tightens as she reads the second line on the screen.",
    "No one knows how long it will take.": "Astra, Zib and Jax look from the UNDER EVALUATION status back to the still-open bracket panel.",
    "A second line appears.": "Insert on the active screen as a second line appears beneath the first notification.",
    "Zib passes through.": "Zib walks through the quiet maintenance bay behind Jax, glancing toward the reader.",
    "Astra and Mira stand across the workbench. Neither is angry. Both understand the stakes.": "Astra and Mira face each other across the workbench with controlled, serious expressions; the report and patched unit sit between them.",
    "Glorp, Kreeb, Mira, and Astra work around one terminal rather than holding another meeting.": "Glorp, Kreeb, Mira and Astra cluster around one terminal while the active maintenance bay remains visible behind them.",
}

ANCHORS = [
    ("coolant-balancing", "the open coolant-balancing unit"),
    ("bracket", "the temporary bracket and open equipment housing"),
    ("brace", "the temporary brace"),
    ("patch", "the temporary patch"),
    ("sample", "the sealed sample and test bench"),
    ("reader", "the handheld reader"),
    ("route slate", "the route slate"),
    ("review slate", "the review slate"),
    ("work board", "the work board"),
    ("report", "the report screen"),
    ("form", "the open form"),
    ("screen", "the active screen"),
    ("display", "the active display"),
    ("notification", "the notification screen"),
    ("conveyor", "the cargo conveyor and service lane"),
    ("dock 2", "the Dock 2 service area"),
    ("damper", "the ventilation service access"),
    ("vent", "the ventilation access"),
    ("chairs", "the room's ordinary chairs"),
    ("vending", "the vending machine"),
    ("microwave", "the break-room microwave"),
    ("work order", "the work orders on the bench"),
    ("terminal", "the terminal"),
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def decode(path: Path):
    raw = "".join(path.read_text(encoding="utf-8").split())
    return json.loads(gzip.decompress(base64.b64decode(raw, validate=True)).decode("utf-8"))


def encode(path: Path, payload):
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    packed = gzip.compress(data, mtime=0)
    b64 = base64.b64encode(packed).decode("ascii")
    path.write_text("\n".join(b64[i:i+76] for i in range(0, len(b64), 76)) + "\n", encoding="utf-8")


def issue_no(page_id: str) -> int:
    return int(re.search(r"S1E(\d+)", page_id).group(1))


def panel_body(text: str) -> str:
    return re.sub(r"^\s*PANEL\s+\d+\s*[—-]\s*", "", text).strip()


def prefix(text: str, idx: int) -> str:
    m = re.match(r"^\s*(PANEL\s+\d+)\s*[—-]", text, re.IGNORECASE)
    return m.group(1).upper() if m else f"PANEL {idx}"


def setting_label(page: dict) -> str:
    key = page.get("setting")
    settings = load(SHOW / "settings.json")
    if key in settings:
        return settings[key].get("name", key)
    text = str(page.get("settingText") or "Stardust Station workplace").strip()
    return text.split(";")[0].split(".")[0]


def strip_dialogue_for_summary(body: str) -> str:
    # Keep physical action before embedded script dialogue.
    body = re.split(r"\s+(?:ASTRA|MIRA|JAX|ZIB|GLORP|KREEB|PIXA|BRICK|LIAISON|SCREEN|DISPLAY|SIGN|STATION):\s", body, maxsplit=1)[0].strip()
    return body.rstrip(" .")


def clean_panel_body(body: str) -> str:
    if body in EXACT_REWRITES:
        return EXACT_REWRITES[body]
    body = re.sub(r"^Later\.\s*", "", body, flags=re.IGNORECASE)
    body = re.sub(r"\s+from\s+Issue\s+\d+", "", body, flags=re.IGNORECASE)
    body = re.sub(r"\bIssue\s+\d+\s+", "", body, flags=re.IGNORECASE)
    body = body.replace("from the arc:", "accumulated on the board:")
    body = body.replace(", making the contrast physical", "")
    body = re.sub(r",\s*(?:proving|paying off|establishing)\b[^.]*", "", body, flags=re.IGNORECASE)
    return body.strip()


def nearby_anchor(bodies: list[str], idx: int) -> str:
    neighborhood = " ".join(bodies[max(0, idx-2): min(len(bodies), idx+3)]).lower()
    for needle, phrase in ANCHORS:
        if needle in neighborhood:
            return phrase
    return "the active work surface"


def nearby_other(bodies: list[str], idx: int, subject: str) -> str | None:
    neighborhood = " ".join(bodies[max(0, idx-2): min(len(bodies), idx+3)])
    for name in NAMES:
        if name != subject and re.search(rf"\b{re.escape(name)}\b", neighborhood):
            return name
    return None


def resolve_pronoun_subject(bodies: list[str], idx: int) -> str | None:
    for j in range(idx - 1, -1, -1):
        for name in NAMES:
            if re.search(rf"\b{re.escape(name)}\b", bodies[j]):
                return name
    return None


def enrich_weak(body: str, bodies: list[str], idx: int) -> str:
    lower = body.lower().strip(" .")
    anchor = nearby_anchor(bodies, idx)
    # Dialogue-only panel: stage the speaker instead of sending only words to the chef.
    m = re.match(r"^(ASTRA|MIRA|JAX|ZIB|GLORP|KREEB|PIXA|BRICK|LIAISON):\s*(.+)$", body)
    if m:
        subject = m.group(1).title()
        if subject == "Pixa":
            return f"Medium close on Pixa beside {anchor}; her display or body angle turns toward the others as she speaks. {body}"
        return f"Medium close on {subject} beside {anchor}, expression readable and eyeline directed toward the others. {body}"

    subject = None
    for name in NAMES:
        if re.match(rf"^{re.escape(name)}\b", body, re.IGNORECASE):
            subject = name
            break
    if subject is None and re.match(r"^(She|He|They)\b", body):
        subject = resolve_pronoun_subject(bodies, idx)
    if not subject:
        if lower in {"nobody speaks", "no one speaks"}:
            return f"Hold on the group around {anchor}; everyone stays silent, eyes on the result."
        return body

    other = nearby_other(bodies, idx, subject)
    target = other or "the nearby coworker"
    if re.search(r"\bnods?(?: once)?\.?$", lower):
        return f"Close reaction on {subject} beside {anchor}; a small confirming nod toward {target}."
    if re.search(r"\bagrees\.?$", lower):
        return f"Close reaction on {subject} beside {anchor}; a small confirming nod toward {target}."
    if "does not look up" in lower:
        return f"Close on {subject} still working at {anchor}; they answer or react without lifting their eyes from the task."
    if "looks up" in lower:
        return f"Close on {subject} lifting their gaze from {anchor} toward {target}."
    if re.search(r"\bstops\.?$", lower):
        return f"Tight reaction on {subject}; their hands stop over {anchor} as they notice the change."
    if re.search(r"\bturns\.?$", lower):
        return f"Medium close on {subject} turning from {anchor} toward {target}."
    if re.search(r"\bshrugs\.?$", lower):
        return f"Medium close on {subject} beside {anchor}; one small shrug, posture otherwise relaxed."
    if "keeps working" in lower:
        return f"Medium on {subject} continuing the hands-on task at {anchor}, attention still on the job while the conversation continues nearby."
    if re.search(r"\bcontinues\.?$", lower):
        return f"Medium on {subject} continuing the conversation beside {anchor}, one hand still indicating the same document or equipment."
    if re.search(r"\bwaits\.?$", lower):
        return f"Hold on {subject} beside {anchor}, still and attentive while the others finish the task."
    return body


def needs_enrichment(body: str) -> bool:
    low = body.lower().strip(" .")
    if re.match(r"^(ASTRA|MIRA|JAX|ZIB|GLORP|KREEB|PIXA|BRICK|LIAISON):\s", body):
        return True
    if any(low.endswith(v) for v in WEAK_VERBS):
        return True
    if low in {"nobody speaks", "no one speaks"}:
        return True
    return False


def direct_summary(page: dict, cleaned_bodies: list[str]) -> str:
    visual = [strip_dialogue_for_summary(b) for b in cleaned_bodies]
    visual = [v for v in visual if v]
    n = len(cleaned_bodies)
    first = visual[0]
    middle = visual[len(visual)//2]
    last = visual[-1]
    return (
        f"Primary composition: {n}-panel page in {setting_label(page)}. "
        f"Opening image: {first}. Middle image: {middle}. Closing image: {last}."
    )


def sanitize_page(page: dict, alter_panels: bool) -> tuple[bool, int]:
    plans = page.get("panelPlan") or []
    original_bodies = [panel_body(str(item.get("text", ""))) for item in plans if isinstance(item, dict)]
    cleaned_bodies = [clean_panel_body(b) for b in original_bodies]
    old_summary = page.get("summary")
    page["summary"] = direct_summary(page, cleaned_bodies)
    changed = 0
    if alter_panels:
        final_bodies = cleaned_bodies[:]
        # Enrichment sees cleaned neighbor context but only touches weak/non-drawable beats.
        for i, body in enumerate(cleaned_bodies):
            if needs_enrichment(body):
                final_bodies[i] = enrich_weak(body, cleaned_bodies, i)
        panel_idx = 0
        for i, item in enumerate(plans, 1):
            if not isinstance(item, dict) or "text" not in item:
                continue
            old = item["text"]
            new = f"{prefix(old, i)} — {final_bodies[panel_idx]}"
            panel_idx += 1
            if new != old:
                item["text"] = new
                changed += 1
    return page["summary"] != old_summary, changed


def replace_json_value(raw: str, key: str, old: str, new: str) -> str:
    if old == new:
        return raw
    old_json = json.dumps(old, ensure_ascii=False)
    new_json = json.dumps(new, ensure_ascii=False)
    pattern = re.compile(rf'("{re.escape(key)}"\s*:\s*){re.escape(old_json)}')
    raw2, count = pattern.subn(lambda m: m.group(1) + new_json, raw, count=1)
    if count != 1:
        raise AssertionError(f"Could not replace {key}: {old[:100]}")
    return raw2


def manifest_entries():
    return {e["id"]: e for e in load(MANIFEST) if e.get("id") in ISSUE_IDS}


def rewrite_manifest():
    raw = MANIFEST.read_text(encoding="utf-8")
    replacement = json.dumps(GENERATION_LINE, ensure_ascii=False)
    count = 0
    for show_id in ISSUE_IDS:
        pattern = re.compile(rf'("id"\s*:\s*"{show_id}".*?"generationLine"\s*:\s*)"(?:\\.|[^"\\])*"', re.DOTALL)
        raw, n = pattern.subn(lambda m: m.group(1) + replacement, raw, count=1)
        assert n == 1, show_id
        count += n
    MANIFEST.write_text(raw, encoding="utf-8")
    return count


def rewrite_shelves():
    settings = load(SHOW / "settings.json")
    for key, text in SETTING_TEXT.items():
        if key in settings:
            settings[key]["text"] = text
    (SHOW / "settings.json").write_text(json.dumps(settings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    regions = load(SHOW / "regions.json")
    if "SDS_Stardust_Station" in regions:
        regions["SDS_Stardust_Station"]["text"] = REGION_TEXT
    (SHOW / "regions.json").write_text(json.dumps(regions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    factions = load(SHOW / "factions.json")
    for key, text in FACTION_TEXT.items():
        if key in factions:
            factions[key]["text"] = text
    (SHOW / "factions.json").write_text(json.dumps(factions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sanitize_encoded(entries: dict):
    summaries = 0
    for show_id in ("stardust-station-e02", "stardust-station-e03"):
        for overlay in entries[show_id]["sceneOverlays"]:
            path = SHOW / overlay["file"]
            payload = decode(path)
            pages = payload.get("pages") if isinstance(payload, dict) else payload
            for page in pages:
                changed, _ = sanitize_page(page, alter_panels=False)
                summaries += int(changed)
            encode(path, payload)
    return summaries


def sanitize_plain(path: Path):
    raw = path.read_text(encoding="utf-8")
    pages = json.loads(raw)
    summaries = panels = 0
    for page in pages:
        old_summary = page["summary"]
        old_panels = [item.get("text") for item in page.get("panelPlan", []) if isinstance(item, dict)]
        old_setting_text = page.get("settingText")
        changed_summary, changed_panels = sanitize_page(page, alter_panels=True)
        summaries += int(changed_summary)
        panels += changed_panels
        raw = replace_json_value(raw, "summary", old_summary, page["summary"])
        new_panels = [item.get("text") for item in page.get("panelPlan", []) if isinstance(item, dict)]
        for old, new in zip(old_panels, new_panels):
            if old != new:
                raw = replace_json_value(raw, "text", old, new)
        if old_setting_text and WRITER_META.search(old_setting_text):
            cleaned = re.sub(r"\s*Keep every beat grounded[^.]*\.?", "", old_setting_text, flags=re.IGNORECASE).strip()
            if cleaned != old_setting_text:
                raw = replace_json_value(raw, "settingText", old_setting_text, cleaned)
    path.write_text(raw, encoding="utf-8")
    return summaries, panels


def append_validator_guards():
    text = VALIDATOR.read_text(encoding="utf-8")
    marker = "# STARDUST_VISUAL_FIRST_FINAL_GUARD"
    if marker in text:
        return
    guard = r'''

# STARDUST_VISUAL_FIRST_FINAL_GUARD
# Chef-facing Stardust fields must describe observable image work, not writing-room rationale.
_writer_meta = re.compile(r"\b(?:story\s+beat|the\s+story|the\s+series|the\s+arc|dramatic\s+engine|writer[- ]room|writerly|page\s+feel|key\s+image|causal\s+spine|reader\s+function|payoff|pays\s+off|proves?|proving|rather\s+than\s+preachy|institutionally\s+rather\s+than|scientifically\s+rather\s+than)\b", re.IGNORECASE)
_issue_provenance = re.compile(r"\b(?:from\s+)?Issue\s+\d+\b", re.IGNORECASE)
for _show_id, _entry in stardust_entries.items():
    if _show_id == "stardust-station":
        continue
    for _overlay in _entry["sceneOverlays"]:
        _overlay_path = ROOT / _entry["basePath"] / _overlay["file"]
        _payload = load_overlay(_overlay_path, _overlay)
        _pages = _payload.get("pages") if isinstance(_payload, dict) else _payload
        for _page in _pages:
            assert str(_page.get("summary", "")).startswith("Primary composition:"), f"{_page.get('id')}: summary is not direct image composition"
            _chef_fields = [str(_page.get("summary", "")), str(_page.get("settingText", ""))]
            _chef_fields.extend(str(_p.get("text", "")) for _p in (_page.get("panelPlan") or []) if isinstance(_p, dict))
            for _value in _chef_fields:
                assert not _writer_meta.search(_value), f"{_page.get('id')}: writer-room rationale leaked into image recipe: {_value}"
                assert not _issue_provenance.search(_value), f"{_page.get('id')}: archive/issue provenance leaked into image recipe: {_value}"
                assert "visible around the action" not in _value and "Keep the " not in _value, f"{_page.get('id')}: repetitive boilerplate staging leaked into image recipe: {_value}"
'''
    VALIDATOR.write_text(text + guard, encoding="utf-8")


def audit(entries: dict, before_dialogue: dict, before_ids: list[str], before_panel_counts: dict):
    after_dialogue = {}
    after_ids = []
    after_counts = {}
    total = 0
    weak_remaining = []
    for show_id, entry in entries.items():
        for overlay in entry["sceneOverlays"]:
            path = SHOW / overlay["file"]
            payload = decode(path) if overlay.get("encoding") else load(path)
            pages = payload.get("pages") if isinstance(payload, dict) else payload
            for page in pages:
                pid = page["id"]
                total += 1
                after_ids.append(pid)
                after_dialogue[pid] = page.get("dialogueInline")
                after_counts[pid] = len(page.get("panelPlan") or [])
                assert page["summary"].startswith("Primary composition:"), pid
                fields = [page.get("summary", ""), page.get("settingText", "")]
                fields += [p.get("text", "") for p in page.get("panelPlan", []) if isinstance(p, dict)]
                for value in fields:
                    assert not WRITER_META.search(str(value)), (pid, value)
                    assert not ISSUE_PROVENANCE.search(str(value)), (pid, value)
                    assert "visible around the action" not in str(value) and "Keep the " not in str(value), (pid, value)
                if issue_no(pid) >= 4:
                    for p in page.get("panelPlan", []):
                        body = panel_body(str(p.get("text", "")))
                        if needs_enrichment(body):
                            weak_remaining.append((pid, body))
    assert before_dialogue == after_dialogue, "dialogue changed"
    assert before_ids == after_ids, "page id/order changed"
    assert before_panel_counts == after_counts, "panel counts changed"
    assert not weak_remaining, weak_remaining[:20]
    print("Visual-first audit passed")
    print("Unreleased pages checked:", total)
    print("Dialogue, page order and panel counts unchanged")


def main():
    entries = manifest_entries()
    assert set(entries) == set(ISSUE_IDS)

    before_dialogue = {}
    before_ids = []
    before_panel_counts = {}
    for show_id, entry in entries.items():
        for overlay in entry["sceneOverlays"]:
            path = SHOW / overlay["file"]
            payload = decode(path) if overlay.get("encoding") else load(path)
            pages = payload.get("pages") if isinstance(payload, dict) else payload
            for page in pages:
                before_ids.append(page["id"])
                before_dialogue[page["id"]] = page.get("dialogueInline")
                before_panel_counts[page["id"]] = len(page.get("panelPlan") or [])

    generation_count = rewrite_manifest()
    rewrite_shelves()
    encoded_summaries = sanitize_encoded(entries)
    plain_summaries = panel_changes = 0
    for issue in range(4, 11):
        s, p = sanitize_plain(SHOW / f"pages_e{issue:02d}.json")
        plain_summaries += s
        panel_changes += p
    append_validator_guards()
    entries_after = manifest_entries()
    audit(entries_after, before_dialogue, before_ids, before_panel_counts)

    print("Generation contracts rewritten:", generation_count)
    print("Summaries rewritten:", encoded_summaries + plain_summaries)
    print("Selective panel rewrites:", panel_changes)
    print("Persistent settings/region/faction shelves rewritten as visual data")

    if WORKFLOW.exists():
        WORKFLOW.unlink()
    if SELF.exists():
        SELF.unlink()


if __name__ == "__main__":
    main()
