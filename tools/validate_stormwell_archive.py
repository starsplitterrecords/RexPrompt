#!/usr/bin/env python3
"""Validate Rex Fleet: Stormwell Archive production data."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data" / "shows" / "rex-fleet-stormwell-archive-s1"
MANIFEST = ROOT / "data" / "shows.json"
REQUIRED_SHELVES = (
    "blocking.json","characters.json","dialogue.json","direction.json","factions.json",
    "lighting.json","mood.json","negatives.json","regions.json","settings.json",
)
KNOWN_TEXT_SPEAKERS = {"CAPTION","SYSTEM","SCREEN","DISPLAY","MESSAGE","MONITOR","TECHNICIAN","SFX"}

def load(name: str):
    return json.loads((SHOW / name).read_text(encoding="utf-8"))

def fail(message: str) -> None:
    raise SystemExit(f"Stormwell Archive validation failed: {message}")

def main() -> None:
    for name in REQUIRED_SHELVES + ("pages_base.json","pages_i01.json","series.json"):
        if not (SHOW / name).exists():
            fail(f"missing {name}")
    characters=load("characters.json")
    settings=load("settings.json")
    regions=load("regions.json")
    factions=load("factions.json")
    direction=load("direction.json")
    pages=load("pages_i01.json")
    series=load("series.json")
    if series.get("seriesId") != "rex-fleet-stormwell-archive":
        fail("seriesId mismatch")
    if series.get("name") != "Rex Fleet: Stormwell Archive":
        fail("series name mismatch")
    if len(pages) != 22:
        fail(f"expected 22 Issue 1 pages, got {len(pages)}")
    handles={v.get("handle") for v in characters.values() if v.get("handle")}
    seen=set()
    for index,page in enumerate(pages,1):
        expected=f"STORM_I01_P{index:02d}"
        if page.get("id") != expected or page.get("page") != index or page.get("issue") != 1:
            fail(f"page ordering mismatch at {index}: {page.get('id')}")
        if page["id"] in seen:
            fail(f"duplicate page id {page['id']}")
        seen.add(page["id"])
        if page.get("setting") not in settings:
            fail(f"{page['id']} missing setting {page.get('setting')}")
        if page.get("region") not in regions:
            fail(f"{page['id']} missing region {page.get('region')}")
        for cid in page.get("characters",[]):
            if cid not in characters:
                fail(f"{page['id']} missing character {cid}")
        for fid in page.get("factions",[]):
            if fid not in factions:
                fail(f"{page['id']} missing faction {fid}")
        for did in page.get("direction",[]):
            if did not in direction:
                fail(f"{page['id']} missing direction {did}")
        if not page.get("summary") or not page.get("panelPlan"):
            fail(f"{page['id']} lacks story summary or panel plan")
        for line in page.get("dialogueInline",[]):
            handle=line.get("handle")
            speaker=line.get("speaker")
            if handle and handle not in handles:
                fail(f"{page['id']} uses unknown dialogue handle {handle}")
            if speaker and speaker not in KNOWN_TEXT_SPEAKERS:
                fail(f"{page['id']} uses unsupported text speaker {speaker}")
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    registrations=[x for x in manifest if x.get("id")=="rex-fleet-stormwell-archive-i01"]
    if len(registrations)!=1:
        fail(f"expected one manifest registration, got {len(registrations)}")
    reg=registrations[0]
    if reg.get("basePath")!="data/shows/rex-fleet-stormwell-archive-s1":
        fail("manifest basePath mismatch")
    if reg.get("scenesFile")!="pages_base.json":
        fail("manifest base scene file mismatch")
    overlays=reg.get("sceneOverlays") or []
    if overlays!=[{"file":"pages_i01.json"}]:
        fail(f"manifest overlay mismatch: {overlays!r}")
    selene=characters.get("C_archivist_selene_stormwell",{})
    if selene.get("handle")!="@starsplit.selene.stormwell":
        fail("Selene handle drifted from Rex Fleet canon")
    continuity=" ".join(selene.get("promptContinuity",[])).lower()
    if "research infrastructure" not in continuity or "not a priest" not in continuity:
        fail("Selene archival-science continuity lock missing")
    print(f"Stormwell Archive validation passed: {len(pages)} Issue 1 pages, {len(characters)} characters")

if __name__=="__main__":
    main()
