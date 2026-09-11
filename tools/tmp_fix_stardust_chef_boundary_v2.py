#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

import tmp_fix_stardust_chef_boundary as base

ROOT = Path(__file__).resolve().parents[1]
OLD_SCRIPT = ROOT / "tools" / "tmp_fix_stardust_chef_boundary.py"

# Guard phrases must identify writing-room explanation, not ordinary story vocabulary
# such as establishing shot, writing instrument, WHAT CAN WE PROVE, or an issue-number continuity label.
base.META_RE = re.compile(
    r"\b(?:story\s+beat|the\s+story|the\s+series|the\s+arc|dramatic\s+engine|"
    r"writing\s+process|writer[- ]room|writerly|lesson|comic\s+context|page\s+feel|"
    r"key\s+image|rather\s+than\s+preachy|payoff|pays\s+off|causal\s+spine)\b",
    re.IGNORECASE,
)

SETTING_CONTEXT = {
    "SDS_Admin_Hub": "desks, rolling carts, monitors, printers, vents and ordinary work clutter",
    "SDS_West_Corridor": "access panels, route markings, safety lights and the small observation window",
    "SDS_Break_Room": "microwave, vending machine, small tables, mismatched chairs, printer and posted forms",
    "SDS_Maintenance_Bay": "open equipment housings, diagnostic displays, workbench, service tools and temporary-repair tags",
    "SDS_Lab_Work_Area": "sample bench, scanners, test fixtures, custody labels and sealed sample containers",
    "SDS_Multipurpose_Room": "ordinary chairs, portable display, environmental monitor and accessible service chase",
    "SDS_Quiet_Room": "ordinary chairs, drinking water, uncluttered walls and the simple local sign",
    "SDS_Docking_Vestibule": "hatch hardware, visitor-badge slot, route markings and the operations-level entrance",
    "SDS_Galley_Service_Corridor": "water-manifold cabinet, cable junctions, route markings and utility access",
    "SDS_Cargo_Bay": "conveyor service lane, Dock 2 latch hardware, access barriers, route tags and shuttle-status displays",
}


def clean_meta_panel(text: str) -> str:
    text = base.clean_meta_panel(text)
    # Remove archive/issue-number provenance from image instructions while preserving the physical object/state.
    text = text.replace("Morning after Issue 1.", "Morning in the break room.")
    text = re.sub(r"\s+from\s+Issue\s+\d+", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\bIssue\s+\d+\s+", "", text, flags=re.IGNORECASE)
    text = text.replace("from the arc:", "accumulated on the board:")
    text = text.replace("with ordinary chairs, water, and no corporate slogans", "with ordinary chairs, water, uncluttered walls and one simple local sign")
    text = text.replace("a deliberately boring observation sheet", "a plain observation sheet with simple labeled columns")
    text = re.sub(r"^(\s*PANEL\s+\d+\s*[—-]\s*)Later\.\s*", r"\1", text, flags=re.IGNORECASE)
    return text


def page_props(page: dict) -> list[str]:
    text = " ".join(str(item.get("text", "")) for item in page.get("panelPlan", []) if isinstance(item, dict)).lower()
    chosen: list[str] = []
    for phrase in base.PROP_PHRASES:
        p = phrase.lower()
        if p not in text:
            continue
        # Do not select both a specific phrase and its shorter substring.
        if any(p in existing.lower() or existing.lower() in p for existing in chosen):
            continue
        chosen.append(phrase)
        if len(chosen) == 2:
            break
    return chosen


def visual_clause(text: str) -> str:
    body = base.panel_body(text)
    # Remove embedded scripted dialogue from the page-level visual summary; dialogue remains in its own recipe field/panel text.
    parts = re.split(r"(?:^|\s)(?:[A-Z][A-Z0-9 _-]{1,24}):\s", body, maxsplit=1)
    body = parts[0].strip() if parts else body
    body = body.rstrip(".")
    if not body:
        return ""
    # Keep the summary visual and compact; exact signage/detail remains in panelPlan.
    sentences = re.split(r"(?<=[.!?])\s+", body)
    kept = ""
    for sentence in sentences:
        candidate = (kept + " " + sentence).strip()
        if kept and len(candidate) > 240:
            break
        kept = candidate
        if len(kept) >= 150:
            break
    return (kept or body)[:280].rstrip(" .")


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
    return f"Primary composition: {n}-panel page in {base.setting_label(page)}. Open on {first}. Mid-page: {middle}. Finish on {last}."


def enrich_short_panels(page: dict) -> int:
    if base.issue_no(page["id"]) < 4:
        return 0
    panels = page.get("panelPlan") or []
    props = page_props(page)
    place = base.setting_label(page)
    environment = SETTING_CONTEXT.get(page.get("setting"), "maintained StarTrust workplace surfaces, equipment and route markings")
    changed = 0
    for idx, item in enumerate(panels, 1):
        if not isinstance(item, dict) or not isinstance(item.get("text"), str):
            continue
        old = clean_meta_panel(item["text"])
        body = base.panel_body(old)
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
            context += " Keep " + " and ".join(f"the {p}" for p in props) + f" clearly visible against the {environment}."
        else:
            context += f" Keep the {environment} visible around the action."
        number = re.match(r"^\s*(PANEL\s+\d+)\s*[—-]", old, re.IGNORECASE)
        prefix = number.group(1).upper() if number else f"PANEL {idx}"
        item["text"] = f"{prefix} — {context}"
        changed += 1
    return changed


def sanitize_page(page: dict) -> tuple[int, int]:
    old_summary = page.get("summary", "")
    panel_changed = 0
    # Clean page-plan reasoning first so the generated Primary composition cannot repeat it.
    for item in page.get("panelPlan") or []:
        if not isinstance(item, dict) or not isinstance(item.get("text"), str):
            continue
        cleaned = clean_meta_panel(item["text"])
        if cleaned != item["text"]:
            item["text"] = cleaned
            panel_changed += 1
    panel_changed += enrich_short_panels(page)
    page["summary"] = direct_summary(page)
    return int(page["summary"] != old_summary), panel_changed


def update_validator():
    text = base.VALIDATOR.read_text(encoding="utf-8")
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
    insert = '''        panel_plan = page.get("panelPlan")\n        assert isinstance(panel_plan, list) and panel_plan, f"{page_id}: missing panelPlan"\n        if show_id != "stardust-station":\n            assert page["summary"].startswith("Primary composition:"), f"{page_id}: chef-facing summary must be direct primary composition"\n            recipe_visual_text = [page["summary"], str(page.get("settingText", ""))]\n            recipe_visual_text.extend(str(item.get("text", "")) for item in panel_plan if isinstance(item, dict))\n            forbidden = re.compile(r"\\b(?:story\\s+beat|the\\s+story|the\\s+series|the\\s+arc|dramatic\\s+engine|writing\\s+process|writer[- ]room|writerly|lesson|comic\\s+context|page\\s+feel|key\\s+image|rather\\s+than\\s+preachy|payoff|pays\\s+off|causal\\s+spine)\\b", re.IGNORECASE)\n            leaks = [value for value in recipe_visual_text if forbidden.search(value)]\n            assert not leaks, f"{page_id}: writer-room reasoning leaked into image recipe: {leaks[0]}"\n            match = re.search(r"S1E(\\d+)", page_id)\n            if match and int(match.group(1)) >= 4:\n                for item in panel_plan:\n                    panel_text = str(item.get("text", "")) if isinstance(item, dict) else str(item)\n                    body = re.sub(r"^\\s*PANEL\\s+\\d+\\s*[—-]\\s*", "", panel_text, flags=re.IGNORECASE)\n                    assert len(re.findall(r"[A-Za-z0-9’'-]+", body)) >= 8, f"{page_id}: visually underspecified panel: {panel_text}"\n'''
    if marker not in text:
        raise AssertionError("Validator panel marker drifted")
    text = text.replace(marker, insert)
    base.VALIDATOR.write_text(text, encoding="utf-8")


base.clean_meta_panel = clean_meta_panel
base.page_props = page_props
base.visual_clause = visual_clause
base.direct_summary = direct_summary
base.enrich_short_panels = enrich_short_panels
base.sanitize_page = sanitize_page
base.update_validator = update_validator
# Let base.main delete this v2 script and the temporary workflow; remove the superseded v1 afterward.
base.SELF = Path(__file__).resolve()
base.main()
if OLD_SCRIPT.exists():
    OLD_SCRIPT.unlink()
