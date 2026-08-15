#!/usr/bin/env python3
"""Reconcile Backyard Rockets production cast with the dialogue adaptation.

Dialogue expansion is allowed to bring an additional established character into a scene. When it
does, the generation-facing cast, faction list, and character visual lock must change with it so
RexPrompt never renders a speaker without that character's approved model-sheet identity.
"""
import base64, gzip, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW_ID = "backyard-rockets-s1"
CANON = {"Arvin":"@brk.Arvin","Milo":"@brk.Milo","Lucia":"@brk.Lucia","Cyrus":"@brk.Cyrus","Tamz":"@brk.Tamz"}
SALVAGERS = {"Arvin","Milo","Lucia","Tamz"}
LOCK = {
    "Arvin":"ARVIN: exact approved model sheet; lean narrow angular older engineer; short steel-gray hair; olive utility jacket with blue solar-cell shoulder straps; synthetic graft on RIGHT HAND ONLY; left hand natural.",
    "Milo":"MILO: exact approved model sheet; broad grounded build; dense dark curls; fixed facial cybernetic markings; brown mechanical vest over dark work shirt; realistic tools.",
    "Lucia":"LUCIA: exact approved model sheet; athletic build; black asymmetric razor-cut hair; dark precise field jacket with restrained cyan piping; fitted practical trousers; polished black boots.",
    "Cyrus":"CYRUS: exact approved model sheet; older broad-shouldered build; silvered hair; pale blue eyes; immaculate graphite technical armor with minimal seams and restrained amber-cyan status lines.",
    "Tamz":"TAMZ: exact approved model sheet; braided hair; strong grounded stance; gray field jacket; practical cargo trousers; intentional patch/insignia wear only."
}

def load(p): return json.loads(p.read_text(encoding="utf-8"))
def norm(x):
    if isinstance(x, list): return x
    return [{"id":k, **v} if isinstance(v, dict) else {"id":k,"value":v} for k,v in (x or {}).items()]
def read(p, enc=None):
    if enc == "gzip-base64":
        return json.loads(gzip.decompress(base64.b64decode("".join(p.read_text().split()), validate=True)).decode())
    return load(p)
def write(p, x, enc=None):
    raw = json.dumps(x, ensure_ascii=False, separators=(",",":")).encode()
    if enc == "gzip-base64":
        p.write_text(base64.b64encode(gzip.compress(raw, 9, mtime=0)).decode(), encoding="utf-8")
    else:
        p.write_text(json.dumps(x, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

def patch(scene):
    cast = []
    for c in scene.get("charactersInline", []) or []:
        n = c.get("name") if isinstance(c, dict) else None
        if n in CANON and n not in cast: cast.append(n)
    for d in scene.get("dialogueInline", []) or []:
        n = d.get("speaker") if isinstance(d, dict) else None
        if n in CANON and n not in cast: cast.append(n)
    # Preserve canonical ordering so data is deterministic and visual identities are stable.
    cast = [n for n in CANON if n in cast]
    scene["charactersInline"] = [{"name":n,"handle":CANON[n]} for n in cast]
    factions = []
    if any(n in SALVAGERS for n in cast): factions.append("BR_Salvagers")
    if "Cyrus" in cast: factions.append("BR_Aegis")
    scene["factions"] = factions

    dirs = scene.get("directionInline", []) or []
    if len(dirs) >= 3 and isinstance(dirs[2], dict):
        locks = " ".join(LOCK[n] for n in cast) if cast else "No principal model sheet is required unless explicitly shown by scene action."
        dirs[2]["text"] = "CHARACTER CONTINUITY — " + locks + " Faction wardrobe and body proportions do not change because of location, lighting or action."
        scene["directionInline"] = dirs
    return scene

shows = load(ROOT/"data/shows.json")
show = next(s for s in shows if s.get("id") == SHOW_ID)
base = ROOT/show["basePath"]
files = [(show.get("scenesFile","scenes_base.json"), None)] + [(o["file"], o.get("encoding")) for o in show.get("sceneOverlays", [])]
count = 0
for rel, enc in files:
    p = base/rel
    scenes = norm(read(p, enc))
    scenes = [patch(s) for s in scenes]
    write(p, scenes, enc)
    count += len(scenes)
print(f"Reconciled dialogue cast and visual locks across {count} Backyard Rockets scenes")
