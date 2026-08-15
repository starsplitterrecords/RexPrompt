#!/usr/bin/env python3
"""Rebuild Backyard Rockets scene payloads from approved image canon.

The scene summary is narrative authority. Everything generation-facing is rebuilt from it so
legacy directions, cast lists, settings and faction metadata cannot contaminate a scene.
"""
import base64, gzip, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW_ID = "backyard-rockets-s1"
CANON = {"Arvin":"@brk.Arvin","Milo":"@brk.Milo","Lucia":"@brk.Lucia","Cyrus":"@brk.Cyrus","Tamz":"@brk.Tamz"}
ALIASES = {
    "@starsplit.Arvin":"@brk.Arvin","@starsplit.arvin":"@brk.Arvin",
    "@starsplit.Milo":"@brk.Milo","@starsplit.milo":"@brk.Milo",
    "@starsplit.Lucia":"@brk.Lucia","@starsplit.lucia":"@brk.Lucia",
    "@starsplit.Cyrus":"@brk.Cyrus","@starsplit.cyrus":"@brk.Cyrus","@starsplit.cyru":"@brk.Cyrus",
    "@starsplit.Tamz":"@brk.Tamz","@starsplit.tamz":"@brk.Tamz",
}
PHRASE_FIXES = {
    "gutted, rusted fuel tanker":"converted, weathered fuel tanker",
    "gutted fuel tanker":"converted fuel tanker",
    "rusted fuel tanker":"weathered, maintained fuel tanker",
    "rusted tanker":"weathered, maintained tanker",
    "rust-streaked belly":"sun-weathered belly",
    "oil-slicked belly":"work-worn belly",
    "junk-built rocket":"hand-built rocket assembled from maintained legacy aerospace hardware",
    "scrap-built rocket":"hand-built rocket assembled from maintained legacy aerospace hardware",
    "rickety rocket":"hand-built rocket",
    "makeshift rocket":"hand-built rocket",
    "scrap heap":"organized salvage stock",
    "scrap-fields":"salvage fields",
    "pile of scrap metal":"organized stack of salvage metal",
    "tattered camouflage net":"sun-faded camouflage net",
    "graveyard of fallen communications towers":"decommissioned communications field",
    "sprawling sea of industrial waste and jagged rebar":"organized salvage yard of decommissioned industrial frames and stacked structural steel",
    "towering mess of rusted barrels and salvaged aerospace tubing":"towering hand-built assembly of maintained legacy pressure vessels and reclaimed aerospace tubing",
    "oil drums and aerospace scrap":"legacy pressure vessels and reclaimed aerospace hardware",
    "industrial scrap":"reclaimed industrial hardware",
    "discarded circuitry":"sorted reclaimed circuitry",
    "frayed nylon ropes and wooden beams":"weathered heavy-duty rigging and timber cribbing",
    "discarded ceramic tiles":"salvaged refractory ceramic tiles",
    "primitive control console":"analog field control console",
    "sleek, white armored interceptor vehicle":"sleek graphite Aegis interceptor vehicle",
    "white armored interceptor":"graphite Aegis interceptor",
    "polished black armor":"matte graphite technical armor",
    "amateur welds":"field welds",
    "The synthetic skin of Arvin's hand":"The synthetic skin on the back of Arvin's RIGHT hand",
}
VISUAL_LANGUAGE = (
    "BACKYARD ROCKETS VISUAL LANGUAGE: bright, colorful prestige science fiction rooted in the natural beauty of the American Southwest. "
    "The Launch-Shop culture is clean, capable solar-wave retrofuturism: maintained late-20th-century aerospace forms, painted metal, tactile analog-digital instruments, practical repairs, organized tools and purposeful field engineering. "
    "Aegis is a distinct newer layer of graphite composite, brushed alloy, technical ceramic, robotics and restrained cyan/amber status light. "
    "No junkyard/post-apocalyptic styling, pervasive grime, rust-as-aesthetic, garbage piles, lanterns, glowing crystals or excessive holography. Clothing stays tied to character/faction regardless of environment."
)
CHAR_LOCK = {
    "Arvin":"ARVIN: exact approved model sheet; lean narrow angular older engineer; short steel-gray hair; olive utility jacket with blue solar-cell shoulder straps; synthetic graft on RIGHT HAND ONLY; left hand natural.",
    "Milo":"MILO: exact approved model sheet; broad grounded build; dense dark curls; fixed facial cybernetic markings; brown mechanical vest over dark work shirt; realistic tools.",
    "Lucia":"LUCIA: exact approved model sheet; athletic build; black asymmetric razor-cut hair; dark precise field jacket with restrained cyan piping; fitted practical trousers; polished black boots.",
    "Cyrus":"CYRUS: exact approved model sheet; older broad-shouldered build; silvered hair; pale blue eyes; immaculate graphite technical armor with minimal seams and restrained amber-cyan status lines.",
    "Tamz":"TAMZ: exact approved model sheet; braided hair; strong grounded stance; gray field jacket; practical cargo trousers; intentional patch/insignia wear only.",
}

def load(path): return json.loads(path.read_text(encoding="utf-8"))
def norm(raw):
    if isinstance(raw,list): return raw
    return [{"id":k,**v} if isinstance(v,dict) else {"id":k,"value":v} for k,v in (raw or {}).items()]
def read(path,enc=None):
    if enc == "gzip-base64":
        b = "".join(path.read_text(encoding="utf-8").split())
        return json.loads(gzip.decompress(base64.b64decode(b,validate=True)).decode("utf-8"))
    return load(path)
def write(path,data,enc=None):
    raw = json.dumps(data,ensure_ascii=False,separators=(",",":")).encode("utf-8")
    if enc == "gzip-base64": path.write_text(base64.b64encode(gzip.compress(raw,9,mtime=0)).decode("ascii"),encoding="utf-8")
    else: path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def fixstr(text):
    for a,b in sorted(ALIASES.items(),key=lambda x:-len(x[0])): text=text.replace(a,b)
    text=re.sub(r"@starsplit\b","",text,flags=re.I)
    for a,b in PHRASE_FIXES.items(): text=text.replace(a,b)
    text=text.replace("holographic projector","optical projection unit")
    # Remove repeated legacy decay cues without erasing legitimate local damage.
    text=re.sub(r"\brusted\b","weathered",text,flags=re.I)
    text=re.sub(r"\btattered\b","worn",text,flags=re.I)
    text=re.sub(r"\bmakeshift\b","field-built",text,flags=re.I)
    text=re.sub(r"\bscavenger fleet\b","salvager fleet",text,flags=re.I)
    text=re.sub(r"\bnomadic fleet of scavengers\b","nomadic salvager fleet",text,flags=re.I)
    text=re.sub(r"\bprimitive\b","tactile analog",text,flags=re.I)
    text=re.sub(r" +([,.])",r"\1",text)
    text=re.sub(r" {2,}"," ",text)
    return text.strip()
def strings(x):
    if isinstance(x,str): return fixstr(x)
    if isinstance(x,list): return [strings(v) for v in x]
    if isinstance(x,dict): return {k:strings(v) for k,v in x.items()}
    return x

def without_quotes(text):
    return re.sub(r"[“\"]([^\"”]*)[”\"]"," ",text)
def mentions(text,name):
    return bool(re.search(rf"(?<![A-Za-z]){re.escape(name)}(?![A-Za-z])|{re.escape(CANON[name])}",text,re.I))
def cast(scene):
    # Dialogue content may mention absent people. Cast is derived from narration plus explicit speaker tags.
    summary=scene.get("summary","")
    narration=without_quotes(summary)
    names=[n for n in CANON if mentions(narration,n)]
    for m in re.finditer(r"(Arvin|Milo|Lucia|Cyrus|Tamz)\s+(?:says|whispers|notes|declares|replies|asks)\b",summary,re.I):
        n=m.group(1).title()
        if n not in names:names.append(n)
    return [n for n in CANON if n in names]

def dialogue(scene,present):
    summary=scene.get("summary","")
    matches=list(re.finditer(r"[“\"]([^\"”]{3,350})[”\"]",summary))
    out=[]
    for m in matches:
        quote=m.group(1).strip(); before=summary[max(0,m.start()-180):m.start()]; after=summary[m.end():m.end()+180]
        speaker=None
        for chunk in (after,before):
            q=re.search(r"(Arvin|Milo|Lucia|Cyrus|Tamz)\s+(?:says|whispers|notes|declares|replies|asks)\b",chunk,re.I)
            if q: speaker=q.group(1).title(); break
        if speaker not in present:speaker=None
        if not speaker and len(present)==1:speaker=present[0]
        if not speaker:
            addressed=[n for n in present if re.search(rf"\b{n}\b",quote,re.I)]
            if len(present)==2 and len(addressed)==1:speaker=next(n for n in present if n!=addressed[0])
        if not speaker and present:
            # Use the nearest named participant before the quote.
            candidates=[]
            for n in present:
                hits=list(re.finditer(rf"\b{n}\b",before,re.I))
                if hits:candidates.append((hits[-1].start(),n))
            if candidates:speaker=max(candidates)[1]
        if speaker:
            item={"handle":CANON[speaker],"speaker":speaker,"text":quote}
            if item not in out:out.append(item)
    return out

def derive_setting(summary,present,scene_id):
    if "OUTLINE" in scene_id:
        return "EPISODE OUTLINE — production beats not yet developed into individual scene recipes in source."
    low=summary.lower()
    if any(k in low for k in ("aegis interception suite","aegis command rover","interceptor cockpit","cockpit of a sleek","inside the interceptor")):
        return "Aegis mobile interception platform — immaculate graphite corporate hardware, brushed alloy, precise tactile/glass controls, restrained cyan/amber status light, Mojave terrain beyond."
    if any(k in low for k in ("inside the pressurized welding bay","inside the storage tanker","inside the shadows of a storage tanker","inside the tanker","inside the dim","inside the cramped","inside the cavernous","inside the belly","inside the hull","storage hold","engine bay of the tanker","mobile tanker base","mobile tanker workshop","lead tanker","converted fuel tanker")):
        return "Mobile Launch-Shop tanker interior — maintained retro-industrial aerospace workshop, painted metal, tactile analog-digital instruments, organized tools, practical task lighting and controlled localized wear."
    if any(k in low for k in ("cab of the lead tanker","cabin of the lead truck","control trailer","launch trailer")):
        return "Launch-Shop mobile control cabin — compact maintained retro-aerospace controls, analog gauges, physical switches, restrained digital readouts and bright Mojave light through the windows."
    if any(k in low for k in ("flatbed truck","tanker roof","atop a","roof of")):
        return "Launch-Shop exterior work deck — maintained tanker/flatbed structure, organized field hardware, hard Mojave sun and broad desert horizon."
    if "solar array" in low or "photovoltaic" in low:
        return "Damaged solar-array recovery site — bright open desert, geometric photovoltaic structures, organized salvage operation and maintained technical field gear."
    if "wind turbine" in low:
        return "Decommissioned wind-turbine recovery site — open Mojave basin, large engineered structure, hard desert light and organized field equipment."
    if "radio dish" in low or "communications" in low:
        return "Decommissioned communications site — monumental late-20th-century infrastructure, open Mojave terrain and purposeful salvage activity."
    if "cave" in low or "cavern" in low:
        return "Mojave limestone cave — cool pale mineral interior, practical portable worklights, rough stone and equipment carried in from the bright desert."
    if "canyon" in low:
        return "Mojave box canyon — sun-cut rock walls, narrow vehicle access, dry wash floor and hard reflected desert light."
    if any(k in low for k in ("limestone ridge","limestone outcrop","limestone overlook","ridge","overlook")):
        return "Mojave limestone ridge — pale fractured stone, bright high-desert sun, long sightlines, sparse scrub and the launch corridor below."
    if any(k in low for k in ("salt flat","salt flats","salt pan","dry lake bed","white salt")):
        return "Mojave salt flat — immense bright mineral basin, hard blue sky, heat shimmer, distant mountains and clean geometric horizons."
    if any(k in low for k in ("launch pad","launch site","launch rail","base of the rocket","under the skeletal frame","rocket's fuselage","rocket’s fuselage")):
        return "Mojave field launch site — maintained hand-built aerospace hardware, compact support equipment, practical rigging, hard desert light and broad unobstructed sky."
    if present==["Cyrus"]:
        return "Aegis Mojave observation position — immaculate graphite interceptor equipment, disciplined field geometry and long-range desert visibility."
    return "Mojave Launch-Shop field site — bright open-desert workspace with maintained legacy aerospace equipment, organized tools, practical rigging and dramatic geological distance."

def action_text(summary):
    text=without_quotes(summary)
    text=re.sub(r"\s+"," ",text).strip()
    return text

def direction(summary,present,setting):
    locks=" ".join(CHAR_LOCK[n] for n in present) if present else "No principal character model sheet is required unless explicitly shown by the scene action."
    return [
        {"text":VISUAL_LANGUAGE},
        {"text":"SCENE ACTION — SOURCE-LOCKED: "+action_text(summary)},
        {"text":"CHARACTER CONTINUITY — "+locks+" Faction wardrobe and body proportions do not change because of location, lighting or action."},
        {"text":"LOCATION / PROP / STATE CONTINUITY — "+setting+" Preserve the exact condition, placement and ownership of every named vehicle, tool, component, injury, garment, weapon and piece of damage established here into adjacent scenes until the story explicitly changes it. Do not invent extra dirt, damage, accessories, vehicles or wardrobe changes."},
        {"text":"CAMERA / LIGHT — Readable prestige-TV coverage with bright Southwest color separation and motivated practical light. Favor physical scale, hands performing real work, clear geography and legible silhouettes over murky atmosphere or generic action coverage."},
    ]

def patch(scene):
    s=strings(scene)
    present=cast(s)
    summary=s.get("summary","")
    sid=s.get("id","")
    setting=derive_setting(summary,present,sid)
    s["settingText"]=setting
    s.pop("setting",None)
    s["charactersInline"]=[{"name":n,"handle":CANON[n]} for n in present]
    s.pop("characters",None)
    s["dialogueInline"]=dialogue(s,present)
    s.pop("dialog",None)
    factions=[]
    if any(n in present for n in ("Arvin","Milo","Lucia","Tamz")): factions.append("BR_Salvagers")
    if "Cyrus" in present: factions.append("BR_Aegis")
    s["factions"]=factions
    s["directionInline"]=direction(summary,present,setting)
    s.pop("direction",None)
    return s

shows=load(ROOT/"data/shows.json")
show=next(s for s in shows if s.get("id")==SHOW_ID)
base=ROOT/show["basePath"]
files=[(show.get("scenesFile","scenes_base.json"),None)]+[(o["file"],o.get("encoding")) for o in show.get("sceneOverlays",[])]
count=0
for rel,enc in files:
    path=base/rel
    data=norm(read(path,enc))
    fixed=[patch(s) for s in data]
    write(path,fixed,enc)
    count+=len(fixed)
print("Rebuilt",count,"Backyard Rockets scene recipes across",len(files),"files from summary + approved image canon")
