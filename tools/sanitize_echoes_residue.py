#!/usr/bin/env python3
"""Temporary second-stage cleanup while hardening sanitize_echoes.py."""
from __future__ import annotations

import re
import sanitize_echoes as s

s.FRAGMENT_REWRITES = s.FRAGMENT_REWRITES + (
    (" No mechanism, no scanner.", ""),
    (" No mechanism, no scanner", ""),
)


def split_sentences_with_quotes(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    text = re.sub(r"([.!?][\"'”])\s+(?=[A-Z0-9@\"'“])", r"\1\n", text)
    parts: list[str] = []
    for chunk in text.splitlines():
        parts.extend(re.split(r"(?<=[.!?])\s+(?=[A-Z0-9@\"'“])", chunk))
    return [part for part in parts if part]


s.split_sentences = split_sentences_with_quotes

scene_count, scene_changes = s.sanitize_scenes()
direction_changes = s.sanitize_direction_dictionary()
character_removed = s.sanitize_characters()
s.sanitize_settings_and_regions()
s.sanitize_revision_charter()
s.sanitize_identity_reset()
s.sanitize_warrior_gods()
s.sanitize_relationships()
s.sanitize_timeline()
s.sanitize_season_architecture()
s.sanitize_page_spine()
s.sanitize_development_status()
s.sanitize_manifest()
s.verify_clean()
print(f"Sanitized {scene_count} Echoes scenes")
print(f"Normalized {scene_changes + direction_changes} production-text blocks")
print(f"Removed {character_removed} out-of-scope character fields")
