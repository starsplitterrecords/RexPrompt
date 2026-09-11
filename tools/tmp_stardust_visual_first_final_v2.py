#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

import tmp_stardust_visual_first_final as base

V1 = Path(__file__).with_name("tmp_stardust_visual_first_final.py")


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
    body = re.sub(r",\s*(?:proving|paying off|establishing)\b[^.]*", "", body, flags=re.IGNORECASE)
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


base.panel_body = panel_body
base.clean_panel_body = clean_panel_body
base.sanitize_encoded = sanitize_encoded
base.SELF = Path(__file__).resolve()
base.main()
if V1.exists():
    V1.unlink()
