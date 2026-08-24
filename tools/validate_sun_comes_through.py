#!/usr/bin/env python3
"""Validate sanitized Sun Comes Through RexPrompt production data."""
from __future__ import annotations

import base64
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data" / "shows" / "sun-comes-through-musical-s1"

FORBIDDEN_INLINE_KEYS = {
    "charactersInline",
    "directionInline",
    "dialogueInline",
    "settingText",
    "regionText",
    "lyrics",
    "songLyrics",
}

# Model/correction residue that should not return to scene or persistent creative prose.
FORBIDDEN_RESIDUE = (
    "working name.",
    "arc:",
    "the writing must never",
    "ordinary grace is the point",
    "a place where alex can stop filling silence",
    "reconnection must remain ordinary",
    "do not rush toward the theme",
    "alex is not cold",
    "no villain behavior",
    "do not literalize a ghost",
    "this is mira's independent dream",
    "avoid an instant personality rewrite",
    "do not turn the spoken section into a lecture",
    "the resolution is behavioral",
)


def load(name: str):
    return json.loads((SHOW / name).read_text(encoding="utf-8"))


def decode_song_source():
    path = SHOW / "encoded" / "songs_source.json.gzb64"
    raw = "".join(path.read_text(encoding="utf-8").split())
    return json.loads(gzip.decompress(base64.b64decode(raw, validate=True)).decode("utf-8"))


def fail(message: str) -> None:
    raise SystemExit(f"SCT validation failed: {message}")


def check_residue(name: str, value) -> None:
    text = json.dumps(value, ensure_ascii=False).lower()
    for phrase in FORBIDDEN_RESIDUE:
        if phrase in text:
            fail(f"sanitization residue {phrase!r} in {name}")


def main() -> None:
    characters = load("characters.json")
    dialogue = load("dialogue.json")
    direction = load("direction.json")
    settings = load("settings.json")
    regions = load("regions.json")
    scenes = load("scenes_s1.json")
    songs = load("songs.json")
    series_bible = load("series_bible.json")
    structure = load("season_one_plan.json")

    if series_bible.get("format") != "two-act contemporary narrative-pop stage musical":
        fail("series format drifted away from the continuous two-act musical")
    if structure.get("structure") != "one continuous two-act musical":
        fail("structure file no longer identifies one continuous two-act musical")
    if "episodes" in structure:
        fail("episodic creative structure returned; use movements with stable RexPrompt IDs")

    for name, value in (
        ("characters.json", characters),
        ("settings.json", settings),
        ("regions.json", regions),
        ("direction.json", direction),
        ("scenes_s1.json", scenes),
        ("series_bible.json", series_bible),
        ("season_one_plan.json", structure),
    ):
        check_residue(name, value)

    if not isinstance(scenes, list) or not scenes:
        fail("scene list is empty")

    for scene in scenes:
        sid = scene.get("id", "<missing>")
        bad_keys = FORBIDDEN_INLINE_KEYS.intersection(scene)
        if bad_keys:
            fail(f"{sid} contains inline persistent data: {sorted(bad_keys)}")
        if scene.get("setting") not in settings:
            fail(f"{sid} references missing setting {scene.get('setting')!r}")
        if scene.get("region") not in regions:
            fail(f"{sid} references missing region {scene.get('region')!r}")
        for char_id in scene.get("characters", []):
            if char_id not in characters:
                fail(f"{sid} references missing character {char_id!r}")
        for dialog_id in scene.get("dialog", []):
            if dialog_id not in dialogue:
                fail(f"{sid} references missing dialogue {dialog_id!r}")
        for direction_id in scene.get("direction", []):
            if direction_id not in direction:
                fail(f"{sid} references missing direction {direction_id!r}")
        song_id = scene.get("songId")
        if song_id:
            if song_id not in songs:
                fail(f"{sid} references missing song {song_id!r}")
            scene_title = str(scene.get("songTitle", ""))
            catalog_title = str(songs[song_id].get("title", ""))
            if not scene_title.startswith(catalog_title):
                fail(f"{sid} song title does not match catalog title {catalog_title!r}")

    for dialog_id, line in dialogue.items():
        speaker = line.get("speakerId")
        if speaker not in characters:
            fail(f"{dialog_id} references missing speaker {speaker!r}")

    source = decode_song_source()
    source_text = json.dumps(source, ensure_ascii=False)
    for song_id, song in songs.items():
        title = song.get("title")
        if not title or title not in source_text:
            fail(f"{song_id} title {title!r} is missing from encoded source lyrics")

    print(f"SCT sanitized validation passed: {len(scenes)} scenes, {len(songs)} songs")


if __name__ == "__main__":
    main()
