#!/usr/bin/env python3
"""Mechanical integrity checks for Rex Fleet Academy: Between the Beacons."""

import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"
SHOW_DIR=DATA/"shows"/"rex-fleet-academy-between-beacons"
SHELVES=("blocking.json","characters.json","dialogue.json","direction.json","factions.json","lighting.json","mood.json","negatives.json","regions.json","settings.json")

def load(path):
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)

def main():
    shows=load(DATA/"shows.json")
    shelves={n:load(SHOW_DIR/n) for n in SHELVES}
    pages=load(SHOW_DIR/"pages_i01.json")
    assert load(SHOW_DIR/"pages_base.json")==[]
    entry=[s for s in shows if s.get("seriesId")=="rex-fleet-academy-between-beacons"]
    assert len(entry)==1
    entry=entry[0]
    assert entry["id"]=="rex-fleet-academy-between-beacons-i01"
    assert entry["basePath"]=="data/shows/rex-fleet-academy-between-beacons"
    assert entry["scenesFile"]=="pages_base.json"
    assert entry["sceneOverlays"]==[{"file":"pages_i01.json"}]
    assert entry["includeIdPattern"]=="^RFA_BB_I01_"
    assert entry["unitLabel"]=="PAGE"
    assert "between the beacons" in entry["generationLine"].lower()
    assert "26-page" in entry["formatNote"]

    assert len(pages)==26
    assert [p["id"] for p in pages]==[f"RFA_BB_I01_P{n:02d}" for n in range(1,27)]
    assert [p.get("page") for p in pages]==list(range(1,27))
    assert all(p.get("unit")=="PAGE" and p.get("issue")==1 for p in pages)

    opener, story, closer=pages[0], pages[1:-1], pages[-1]
    assert opener.get("title")=="From the Editor"
    assert closer.get("title")=="Next Course"
    assert not opener.get("sceneId") and not closer.get("sceneId")
    assert all(line.get("speaker")=="CAPTION" and line.get("text") for line in opener.get("dialogueInline",[]))
    assert all(line.get("speaker")=="CAPTION" and line.get("text") for line in closer.get("dialogueInline",[]))
    assert any(line["text"]=="FROM THE EDITOR" for line in opener["dialogueInline"])
    assert any("NAVIGATING THE MIRRORFOLD" in line["text"] for line in closer["dialogueInline"])

    assert len(story)==24
    chars=shelves["characters.json"]; factions=shelves["factions.json"]; regions=shelves["regions.json"]; settings=shelves["settings.json"]; directions=shelves["direction.json"]
    handles={c.get("handle"):cid for cid,c in chars.items() if c.get("handle")}
    spans=[("RFA_BB_I01_S01",4),("RFA_BB_I01_S02",3),("RFA_BB_I01_S03",3),("RFA_BB_I01_S04",3),("RFA_BB_I01_S05",3),("RFA_BB_I01_S06",4),("RFA_BB_I01_S07",3),("RFA_BB_I01_S08",1)]
    pos=0
    for sid,count in spans:
        for offset in range(count):
            p=story[pos]
            assert p.get("id")==f"RFA_BB_I01_P{pos+2:02d}"
            assert p.get("page")==pos+2
            assert p.get("title") and p.get("summary") and p.get("panelPlan")
            assert p.get("setting") in settings and p.get("region") in regions
            assert p.get("sceneId")==sid
            if offset==0:
                assert not p.get("continuityFrom")
            else:
                assert p.get("continuityFrom")==story[pos-1]["id"]
            cast=set(p.get("characters",[])); assert cast
            for cid in cast: assert cid in chars
            for f in p.get("factions",[]): assert f in factions
            for d in p.get("direction",[]): assert d in directions
            for line in p.get("dialogueInline",[]):
                assert line.get("text")
                if line.get("handle"):
                    assert line["handle"] in handles
                    assert handles[line["handle"]] in cast
            pos+=1
    assert pos==24

    rf=load(DATA/"shows"/"rex-fleet-s1"/"characters.json")
    for field in ("name","handle","visualAnchor"):
        assert chars["C_jia_morgan"][field]==rf["C_jia_morgan"][field]

    assert (SHOW_DIR/"README.md").exists()
    bible=load(SHOW_DIR/"series_bible.json")
    assert bible["seriesId"]=="rex-fleet-academy-between-beacons"
    assert (ROOT/"production"/"references"/"rex-fleet-academy-between-beacons"/"README.md").exists()
    print("Rex Fleet Academy: Between the Beacons validation passed")
    print("1 issue / 26 production pages / 24 preserved story pages / 2 editorial splashes / 8 story scenes")

if __name__=="__main__":
    main()
