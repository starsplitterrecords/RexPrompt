#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

import tmp_stardust_visual_first_final as base

V1 = Path(__file__).with_name("tmp_stardust_visual_first_final.py")
V2 = Path(__file__).with_name("tmp_stardust_visual_first_final_v2.py")
V3 = Path(__file__).with_name("tmp_stardust_visual_first_final_v3.py")

base.GENERATION_LINE = (
    "Finished full-color portrait interior story comic page for Stardust Station. "
    "Bright polished workplace science fiction with clean maintained StarTrust interiors, natural coworker acting, "
    "clear physical props and equipment, varied cinematic sequential composition, and clean professional integrated lettering. "
    "Match released Issue 1 interior-story visual canon for established character identity, station design, palette, page language and lettering. "
    "Use approved current-production references only for later continuity state. Preserve scripted panel count and order, physical geography, "
    "character identity, prop and equipment state, and exact lettering. Interior story page only—no cover, title banner, page header, character labels, "
    "dossier, promotional or infographic framing unless explicitly scripted. Fictional production."
)
base.WRITER_META = re.compile(
    r"\b(?:story\s+beat|dramatic\s+engine|writer[- ]room|writerly|page\s+feel|key\s+image|"
    r"causal\s+spine|reader\s+function|payoff|pays\s+off|rather\s+than\s+preachy|"
    r"institutionally\s+rather\s+than|scientifically\s+rather\s+than)\b",
    re.IGNORECASE,
)
base.EXACT_REWRITES.update({
    "Astra relaxes slightly.": "Close on Astra beside the report screen; her shoulders loosen slightly as she reads the result.",
    "Astra looks around the station.": "Astra turns from the report to scan the active maintenance bay: open unit, workbench and crew still working.",
    "The Liaison waits.": "The Liaison holds still on the call, hands off the tablet, giving the crew space to answer.",
})


def panel_body(text: str) -> str:
    return re.sub(r"^\s*PANEL\s+\d+\s*[—-]\s*", "", text, flags=re.IGNORECASE).strip()


def clean_panel_body(body: str) -> str:
    if body in base.EXACT_REWRITES:
        body = base.EXACT_REWRITES[body]
    body = re.sub(r"^Later\.\s*", "", body, flags=re.IGNORECASE)
    body = re.sub(r"\b(?:after|before|from|during)\s+Issue\s+\d+\b", "", body, flags=re.IGNORECASE)
    body = re.sub(r"\bIssue\s+\d+\s+", "", body, flags=re.IGNORECASE)
    body = body.replace("from the arc:", "accumulated on the board:")
    body = body.replace(", making the contrast physical", "")
    body = re.sub(r",\s*(?:paying off|establishing)\b[^.]*", "", body, flags=re.IGNORECASE)
    body = re.sub(r"\s+([.,;:!?])", r"\1", body)
    body = re.sub(r"\s{2,}", " ", body)
    return body.strip()


def sanitize_encoded(entries: dict):
    summaries = panels = 0
    for show_id in ("stardust-station-e02", "stardust-station-e03"):
        for overlay in entries[show_id]["sceneOverlays"]:
            path = base.SHOW / overlay["file"]
            payload = base.decode(path)
            pages = payload.get("pages") if isinstance(payload, dict) else payload
            for page in pages:
                plans = page.get("panelPlan") or []
                old_summary = page.get("summary")
                cleaned_bodies = []
                for idx, item in enumerate(plans, 1):
                    if not isinstance(item, dict) or "text" not in item:
                        continue
                    old = item["text"]
                    body = panel_body(old)
                    cleaned = clean_panel_body(body)
                    cleaned_bodies.append(cleaned)
                    if cleaned != body:
                        item["text"] = f"{base.prefix(old, idx)} — {cleaned}"
                        panels += 1
                page["summary"] = base.direct_summary(page, cleaned_bodies)
                summaries += int(page["summary"] != old_summary)
            base.encode(path, payload)
    print("Encoded provenance-only panel cleanups:", panels)
    return summaries


def append_validator_guards():
    text = base.VALIDATOR.read_text(encoding="utf-8")
    marker = "# STARDUST_VISUAL_FIRST_FINAL_GUARD"
    if marker in text:
        return
    guard = r'''

# STARDUST_VISUAL_FIRST_FINAL_GUARD
# Chef-facing Stardust fields must describe observable image work, not writing-room rationale.
_writer_meta = re.compile(r"\b(?:story\s+beat|dramatic\s+engine|writer[- ]room|writerly|page\s+feel|key\s+image|causal\s+spine|reader\s+function|payoff|pays\s+off|rather\s+than\s+preachy|institutionally\s+rather\s+than|scientifically\s+rather\s+than)\b", re.IGNORECASE)
_issue_provenance = re.compile(r"\b(?:from\s+|after\s+|before\s+|during\s+)?Issue\s+\d+\b", re.IGNORECASE)
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
    base.VALIDATOR.write_text(text + guard, encoding="utf-8")


base.panel_body = panel_body
base.clean_panel_body = clean_panel_body
base.sanitize_encoded = sanitize_encoded
base.append_validator_guards = append_validator_guards
base.SELF = Path(__file__).resolve()
base.main()
for path in (V1, V2, V3):
    if path.exists():
        path.unlink()
