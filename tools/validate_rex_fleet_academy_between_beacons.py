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

    assert len(pages)==24
    assert [p["id"] for p in pages]==[f"RFA_BB_I01_P{n:02d}" for n in range(1,25)]

    chars=shelves["characters.json"]; factions=shelves["factions.json"]; regions=shelves["regions.json"]; settings=shelves["settings.json"]; directions=shelves["direction.json"]
    handles={c.get("handle"):cid for cid,c in chars.items() if c.get("handle")}
    spans=[("RFA_BB_I01_S01",4),("RFA_BB_I01_S02",3),("RFA_BB_I01_S03",3),("RFA_BB_I01_S04",3),("RFA_BB_I01_S05",3),("RFA_BB_I01_S06",4),("RFA_BB_I01_S07",3),("RFA_BB_I01_S08",1)]
    pos=0
    for sid,count in spans:
        for offset in range(count):
            p=pages[pos]; pid=p["id"]
            assert p.get("unit")=="PAGE" and p.get("issue")==1 and p.get("page")==pos+1
            assert p.get("title") and p.get("summary") and p.get("panelPlan")
            assert p.get("setting") in settings and p.get("region") in regions
            assert p.get("sceneId")==sid
            if offset==0:
                assert not p.get("continuityFrom")
            else:
                assert p.get("continuityFrom")==pages[pos-1]["id"]
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

    rf=load(DATA/"shows"/"rex-fleet-s1"/"characters.json")
    for field in ("name","handle","visualAnchor"):
        assert chars["C_jia_morgan"][field]==rf["C_jia_morgan"][field]

    assert (SHOW_DIR/"README.md").exists()
    bible=load(SHOW_DIR/"series_bible.json")
    assert bible["seriesId"]=="rex-fleet-academy-between-beacons"
    assert (ROOT/"production"/"references"/"rex-fleet-academy-between-beacons"/"README.md").exists()
    print("Rex Fleet Academy: Between the Beacons validation passed")
    print("1 issue / 24 story pages / 8 scenes / overlay-based Academy topic-series package")

if __name__=="__main__":
    main()
