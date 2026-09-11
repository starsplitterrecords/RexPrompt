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
SELF = ROOT / "tools" / "tmp_stardust_visual_first_selective.py"
WORKFLOW = ROOT / ".github" / "workflows" / "stardust-visual-first-selective.yml"

ISSUE_IDS = [f"stardust-station-e{i:02d}" for i in range(2, 11)]
GENERATION_LINE = (
    "Finished full-color portrait interior story comic page for Stardust Station. "
    "Bright polished workplace science fiction with clean maintained StarTrust interiors, natural coworker acting, "
    "clear physical props and equipment, varied cinematic sequential composition, and clean professional integrated lettering. "
    "Match released Issue 1 interior-story visual canon for established character identity, station design, palette, page language and lettering. "
    "Use approved current-production references only for later continuity state. Preserve scripted panel count and order, physical geography, "
    "character identity, prop and equipment state, and exact lettering. Interior story page only—no cover, title banner, page header, character labels, "
    "dossier, promotional or infographic framing unless explicitly scripted. Fictional production."
)

WRITER_META = re.compile(
    r"\b(?:story\s+beat|dramatic\s+engine|writer[- ]room|writerly|page\s+feel|key\s+image|"
    r"causal\s+spine|reader\s+function|payoff|pays\s+off|rather\s+than\s+preachy|"
    r"institutionally\s+rather\s+than|scientifically\s+rather\s+than)\b",
    re.IGNORECASE,
)
ISSUE_PROVENANCE = re.compile(r"\b(?:from\s+|after\s+|before\s+|during\s+)?Issue\s+\d+\b", re.IGNORECASE)
DIALOGUE_ONLY = re.compile(r"^(ASTRA|MIRA|JAX|ZIB|GLORP|KREEB|PIXA|BRICK|LIAISON|INSPECTOR|SCREEN|DISPLAY|SIGN|STATION):\s+", re.IGNORECASE)

SETTING_NAMES = {
    "SDS_Admin_Hub": "Main Bullpen / Admin Hub",
    "SDS_West_Corridor": "West Corridor",
    "SDS_Break_Room": "Break Room",
    "SDS_Maintenance_Bay": "Maintenance Bay",
    "SDS_Lab_Work_Area": "Lab Work Area",
    "SDS_Multipurpose_Room": "Multipurpose Room",
    "SDS_Quiet_Room": "Quiet Room",
    "SDS_Docking_Vestibule": "Docking Vestibule",
    "SDS_Galley_Service_Corridor": "Galley Service Corridor",
    "SDS_Cargo_Bay": "Cargo Bay / Dock 2",
}

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
    "Astra relaxes slightly.": "Close on Astra beside the report screen; her shoulders loosen slightly as she reads the result.",
    "Astra looks around the station.": "Astra turns from the report to scan the active maintenance bay: open unit, workbench and crew still working.",
    "The Liaison waits.": "The Liaison holds still on the call, hands off the tablet, giving the crew space to answer.",
    "Astra and Mira stand across the workbench. Neither is angry. Both understand the stakes.": "Astra and Mira face each other across the workbench with controlled, serious expressions; the report and patched unit sit between them.",
    "Glorp, Kreeb, Mira, and Astra work around one terminal rather than holding another meeting.": "Glorp, Kreeb, Mira and Astra cluster around one terminal while the active maintenance bay remains visible behind them.",
}


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


def panel_body(text: str) -> str:
    return re.sub(r"^\s*PANEL\s+\d+\s*[—-]\s*", "", text, flags=re.IGNORECASE).strip()


def panel_prefix(text: str, idx: int) -> str:
    m = re.match(r"^\s*(PANEL\s+\d+)\s*[—-]", text, flags=re.IGNORECASE)
    return m.group(1).upper() if m else f"PANEL {idx}"


def setting_label(page: dict) -> str:
    if page.get("setting") in SETTING_NAMES:
        return SETTING_NAMES[page["setting"]]
    text = str(page.get("settingText") or "Stardust Station workplace").strip()
    return text.split(";")[0].split(".")[0].strip()


def clean_body(body: str) -> str:
    if body in EXACT_REWRITES:
        body = EXACT_REWRITES[body]
    body = re.sub(r"^Later\.\s*", "", body, flags=re.IGNORECASE)
    body = re.sub(r"\b(?:after|before|from|during)\s+Issue\s+\d+\b", "", body, flags=re.IGNORECASE)
    body = re.sub(r"\bIssue\s+\d+\s+", "", body, flags=re.IGNORECASE)
    body = body.replace("from the arc:", "accumulated on the board:")
    body = body.replace(", making the contrast physical", "")
    body = re.sub(r",\s*(?:paying off|establishing)\b[^.]*", "", body, flags=re.IGNORECASE)
    body = re.sub(r"\s+([.,;:!?])", r"\1", body)
    return re.sub(r"\s{2,}", " ", body).strip()


def stage_dialogue_only(body: str, page: dict) -> str:
    m = DIALOGUE_ONLY.match(body)
    if not m:
        return body
    speaker = m.group(1).upper()
    place = setting_label(page)
    if speaker in {"SCREEN", "DISPLAY"}:
        return f"Insert on the active station display in {place}. {body}"
    if speaker == "SIGN":
        return f"Insert on the posted sign in {place}. {body}"
    if speaker == "STATION":
        return f"Environmental view of {place} with the built-in station interface active. {body}"
    display_name = speaker.title()
    if speaker == "PIXA":
        return f"Medium close on Pixa in {place}; her chassis or display turns toward the crew as she speaks. {body}"
    if speaker == "LIAISON":
        return f"Medium close on the Operations Liaison on the live call, composed and attentive. {body}"
    return f"Medium close on {display_name} in {place}; expression readable and eyeline directed toward the others. {body}"


def visual_clause(body: str) -> str:
    body = re.split(r"\s+(?:ASTRA|MIRA|JAX|ZIB|GLORP|KREEB|PIXA|BRICK|LIAISON|INSPECTOR|SCREEN|DISPLAY|SIGN|STATION):\s", body, maxsplit=1, flags=re.IGNORECASE)[0].strip()
    return body.rstrip(" .")


def make_summary(page: dict, bodies: list[str]) -> str:
    visuals = [visual_clause(b) for b in bodies]
    visuals = [v for v in visuals if v]
    assert visuals, page.get("id")
    return (
        f"Primary composition: {len(bodies)}-panel page in {setting_label(page)}. "
        f"Opening image: {visuals[0]}. Middle image: {visuals[len(visuals)//2]}. Closing image: {visuals[-1]}."
    )


def transform_page(page: dict, allow_panel_edits: bool) -> tuple[int, int]:
    plans = page.get("panelPlan") or []
    bodies = []
    panel_changes = 0
    for idx, item in enumerate(plans, 1):
        if not isinstance(item, dict) or not isinstance(item.get("text"), str):
            continue
        old = item["text"]
        body = clean_body(panel_body(old))
        if allow_panel_edits:
            body = stage_dialogue_only(body, page)
        else:
            # For encoded I2-I3, only remove archive provenance; choreography remains otherwise untouched.
            pass
        bodies.append(body)
        new = f"{panel_prefix(old, idx)} — {body}"
        if new != old:
            item["text"] = new
            panel_changes += 1
    old_summary = page.get("summary")
    page["summary"] = make_summary(page, bodies)
    return int(page["summary"] != old_summary), panel_changes


def entries():
    return {e["id"]: e for e in load(MANIFEST) if e.get("id") in ISSUE_IDS}


def rewrite_manifest():
    raw = MANIFEST.read_text(encoding="utf-8")
    replacement = json.dumps(GENERATION_LINE, ensure_ascii=False)
    for show_id in ISSUE_IDS:
        pat = re.compile(rf'("id"\s*:\s*"{show_id}".*?"generationLine"\s*:\s*)"(?:\\.|[^"\\])*"', re.DOTALL)
        raw, n = pat.subn(lambda m: m.group(1) + replacement, raw, count=1)
        assert n == 1, show_id
    MANIFEST.write_text(raw, encoding="utf-8")


def rewrite_shelves():
    settings = load(SHOW / "settings.json")
    for key, text in SETTING_TEXT.items():
        if key in settings:
            settings[key]["text"] = text
    (SHOW / "settings.json").write_text(json.dumps(settings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    regions = load(SHOW / "regions.json")
    regions["SDS_Stardust_Station"]["text"] = REGION_TEXT
    (SHOW / "regions.json").write_text(json.dumps(regions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    factions = load(SHOW / "factions.json")
    for key, text in FACTION_TEXT.items():
        if key in factions:
            factions[key]["text"] = text
    (SHOW / "factions.json").write_text(json.dumps(factions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def transform_plain(path: Path):
    raw = path.read_text(encoding="utf-8")
    pages = json.loads(raw)
    summaries = panels = 0
    for page in pages:
        old_summary = page["summary"]
        old_panel_texts = [x.get("text") for x in page.get("panelPlan", []) if isinstance(x, dict)]
        old_setting_text = page.get("settingText")
        s, p = transform_page(page, True)
        summaries += s; panels += p
        old_json = json.dumps(old_summary, ensure_ascii=False)
        new_json = json.dumps(page["summary"], ensure_ascii=False)
        raw, n = re.subn(r'("summary"\s*:\s*)' + re.escape(old_json), lambda m: m.group(1) + new_json, raw, count=1)
        assert n == 1, page["id"]
        new_panel_texts = [x.get("text") for x in page.get("panelPlan", []) if isinstance(x, dict)]
        for old, new in zip(old_panel_texts, new_panel_texts):
            if old == new:
                continue
            oj = json.dumps(old, ensure_ascii=False); nj = json.dumps(new, ensure_ascii=False)
            raw, n = re.subn(r'("text"\s*:\s*)' + re.escape(oj), lambda m: m.group(1) + nj, raw, count=1)
            assert n == 1, (page["id"], old)
        if old_setting_text and WRITER_META.search(old_setting_text):
            cleaned = re.sub(r"\s*Keep every beat grounded[^.]*\.?", "", old_setting_text, flags=re.IGNORECASE).strip()
            if cleaned != old_setting_text:
                oj = json.dumps(old_setting_text, ensure_ascii=False); nj = json.dumps(cleaned, ensure_ascii=False)
                raw, n = re.subn(r'("settingText"\s*:\s*)' + re.escape(oj), lambda m: m.group(1) + nj, raw, count=1)
                assert n == 1
    path.write_text(raw, encoding="utf-8")
    return summaries, panels


def add_guard():
    text = VALIDATOR.read_text(encoding="utf-8")
    marker = "# STARDUST_VISUAL_FIRST_SELECTIVE_GUARD"
    if marker in text:
        return
    guard = r'''

# STARDUST_VISUAL_FIRST_SELECTIVE_GUARD
_writer_meta = re.compile(r"\b(?:story\s+beat|dramatic\s+engine|writer[- ]room|writerly|page\s+feel|key\s+image|causal\s+spine|reader\s+function|payoff|pays\s+off|rather\s+than\s+preachy|institutionally\s+rather\s+than|scientifically\s+rather\s+than)\b", re.IGNORECASE)
_issue_provenance = re.compile(r"\b(?:from\s+|after\s+|before\s+|during\s+)?Issue\s+\d+\b", re.IGNORECASE)
for _entry in stardust_entries:
    if _entry.get("id") == "stardust-station":
        continue
    for _overlay in _entry["sceneOverlays"]:
        _payload = load_overlay(ROOT / _entry["basePath"] / _overlay["file"], _overlay.get("encoding"))
        _pages = _payload.get("pages") if isinstance(_payload, dict) else _payload
        for _page in _pages:
            assert str(_page.get("summary", "")).startswith("Primary composition:"), f"{_page.get('id')}: summary is not image-facing composition"
            _fields = [str(_page.get("summary", "")), str(_page.get("settingText", ""))]
            _fields.extend(str(_p.get("text", "")) for _p in (_page.get("panelPlan") or []) if isinstance(_p, dict))
            for _value in _fields:
                assert not _writer_meta.search(_value), f"{_page.get('id')}: writer-room rationale leaked into recipe: {_value}"
                assert not _issue_provenance.search(_value), f"{_page.get('id')}: issue/archive provenance leaked into recipe: {_value}"
                assert "visible around the action" not in _value and "Keep the " not in _value, f"{_page.get('id')}: repetitive staging boilerplate leaked into recipe: {_value}"
'''
    VALIDATOR.write_text(text + guard, encoding="utf-8")


def main():
    es = entries(); assert set(es) == set(ISSUE_IDS)
    before_dialogue = {}; before_ids = []; before_counts = {}
    for sid, e in es.items():
        for ov in e["sceneOverlays"]:
            path = SHOW / ov["file"]
            payload = decode(path) if ov.get("encoding") else load(path)
            pages = payload.get("pages") if isinstance(payload, dict) else payload
            for page in pages:
                pid = page["id"]; before_ids.append(pid); before_dialogue[pid] = page.get("dialogueInline"); before_counts[pid] = len(page.get("panelPlan") or [])

    rewrite_manifest(); rewrite_shelves()
    summary_changes = panel_changes = 0
    for sid in ("stardust-station-e02", "stardust-station-e03"):
        for ov in es[sid]["sceneOverlays"]:
            path = SHOW / ov["file"]; payload = decode(path); pages = payload.get("pages") if isinstance(payload, dict) else payload
            for page in pages:
                s, p = transform_page(page, False); summary_changes += s; panel_changes += p
            encode(path, payload)
    for issue in range(4, 11):
        s, p = transform_plain(SHOW / f"pages_e{issue:02d}.json"); summary_changes += s; panel_changes += p
    add_guard()

    es2 = entries(); after_dialogue = {}; after_ids = []; after_counts = {}; total = 0
    for sid, e in es2.items():
        for ov in e["sceneOverlays"]:
            path = SHOW / ov["file"]; payload = decode(path) if ov.get("encoding") else load(path); pages = payload.get("pages") if isinstance(payload, dict) else payload
            for page in pages:
                pid = page["id"]; total += 1; after_ids.append(pid); after_dialogue[pid] = page.get("dialogueInline"); after_counts[pid] = len(page.get("panelPlan") or [])
                fields = [page.get("summary", ""), page.get("settingText", "")] + [p.get("text", "") for p in page.get("panelPlan", []) if isinstance(p, dict)]
                assert page["summary"].startswith("Primary composition:")
                for value in fields:
                    assert not WRITER_META.search(str(value)), (pid, value)
                    assert not ISSUE_PROVENANCE.search(str(value)), (pid, value)
                    assert "visible around the action" not in str(value) and "Keep the " not in str(value), (pid, value)
    assert before_dialogue == after_dialogue, "dialogue changed"
    assert before_ids == after_ids, "page order/id changed"
    assert before_counts == after_counts, "panel counts changed"
    print("Selective visual-first audit passed")
    print("Unreleased pages checked:", total)
    print("Summaries rewritten:", summary_changes)
    print("Panel instructions changed:", panel_changes)
    print("Dialogue, page order and panel counts unchanged")

    if WORKFLOW.exists(): WORKFLOW.unlink()
    if SELF.exists(): SELF.unlink()

if __name__ == "__main__":
    main()
