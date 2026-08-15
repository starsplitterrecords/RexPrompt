#!/usr/bin/env python3
"""Rebuild Backyard Rockets generation payloads from approved image canon + scene summaries."""
import base64,gzip,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SHOW_ID="backyard-rockets-s1"
CANON={"Arvin":"@brk.Arvin","Milo":"@brk.Milo","Lucia":"@brk.Lucia","Cyrus":"@brk.Cyrus","Tamz":"@brk.Tamz"}
SALVAGERS={"Arvin","Milo","Lucia","Tamz"}
ALIASES={
"@starsplit.Arvin":"@brk.Arvin","@starsplit.arvin":"@brk.Arvin","@starsplit.Milo":"@brk.Milo","@starsplit.milo":"@brk.Milo",
"@starsplit.Lucia":"@brk.Lucia","@starsplit.lucia":"@brk.Lucia","@starsplit.Cyrus":"@brk.Cyrus","@starsplit.cyrus":"@brk.Cyrus","@starsplit.cyru":"@brk.Cyrus",
"@starsplit.Tamz":"@brk.Tamz","@starsplit.tamz":"@brk.Tamz"}
PHRASE_FIXES={
"gutted, rusted fuel tanker":"converted, weathered fuel tanker","gutted fuel tanker":"converted fuel tanker","rusted fuel tanker":"weathered, maintained fuel tanker",
"rusted tanker":"weathered, maintained tanker","rust-streaked belly":"sun-weathered belly","oil-slicked belly":"work-worn belly",
"junk-built rocket":"hand-built rocket assembled from maintained legacy aerospace hardware","scrap-built rocket":"hand-built rocket assembled from maintained legacy aerospace hardware",
"rickety rocket":"hand-built rocket","makeshift rocket":"hand-built rocket","scrap heap":"organized salvage stock","scrap-fields":"salvage fields",
"pile of scrap metal":"organized stack of salvage metal","tattered camouflage net":"sun-faded camouflage net","graveyard of fallen communications towers":"decommissioned communications field",
"sprawling sea of industrial waste and jagged rebar":"organized salvage yard of decommissioned industrial frames and stacked structural steel",
"towering mess of rusted barrels and salvaged aerospace tubing":"towering hand-built assembly of maintained legacy pressure vessels and reclaimed aerospace tubing",
"oil drums and aerospace scrap":"legacy pressure vessels and reclaimed aerospace hardware","industrial scrap":"reclaimed industrial hardware","discarded circuitry":"sorted reclaimed circuitry",
"frayed nylon ropes and wooden beams":"weathered heavy-duty rigging and timber cribbing","discarded ceramic tiles":"salvaged refractory ceramic tiles",
"primitive control console":"analog field control console","sleek, white armored interceptor vehicle":"sleek graphite Aegis interceptor vehicle",
"white armored interceptor":"graphite Aegis interceptor","polished black armor":"matte graphite technical armor","amateur welds":"field welds",
"The synthetic skin of Arvin's hand":"The synthetic skin on the back of Arvin's RIGHT hand"}
# Editorially resolved only where grammar/context is genuinely ambiguous. These supersede contaminated legacy speaker metadata.
DIALOGUE_OVERRIDES={
"BR_S1E01_A01_SC05":["Arvin"],"BR_S1E01_A02_SC03":["Cyrus"],"BR_S1E01_A03_SC03":["Cyrus"],
"BR_S1E02_A01_SC02":["Lucia"],"BR_S1E02_A03_SC06":["Arvin"],"BR_S1E02_A04_SC02":["Lucia"],"BR_S1E02_A04_SC03":["Cyrus"],
"BR_S1E02_A04_SC04":["Milo"],"BR_S1E02_A05_SC02":["Lucia"],"BR_S1E03_A01_SC04":["Arvin"],"BR_S1E04_A02_SC05":["Lucia"],
"BR_S1E05_A01_SC03":["Arvin"],"BR_S1E05_A01_SC05":["Arvin"],"BR_S1E05_A02_SC05":["Milo"]}
VISUAL=("BACKYARD ROCKETS VISUAL LANGUAGE: bright, colorful prestige science fiction rooted in the natural beauty of the American Southwest. "
"Launch-Shop culture is clean, capable solar-wave retrofuturism: maintained late-20th-century aerospace forms, painted metal, tactile analog-digital instruments, practical repairs, organized tools and purposeful field engineering. "
"Aegis is a distinct newer layer of graphite composite, brushed alloy, technical ceramic, robotics and restrained cyan/amber status light. "
"No junkyard/post-apocalyptic styling, pervasive grime, rust-as-aesthetic, garbage piles, lanterns, glowing crystals or excessive holography. Clothing stays tied to character/faction regardless of environment.")
LOCK={
"Arvin":"ARVIN: exact approved model sheet; lean narrow angular older engineer; short steel-gray hair; olive utility jacket with blue solar-cell shoulder straps; synthetic graft on RIGHT HAND ONLY; left hand natural.",
"Milo":"MILO: exact approved model sheet; broad grounded build; dense dark curls; fixed facial cybernetic markings; brown mechanical vest over dark work shirt; realistic tools.",
"Lucia":"LUCIA: exact approved model sheet; athletic build; black asymmetric razor-cut hair; dark precise field jacket with restrained cyan piping; fitted practical trousers; polished black boots.",
"Cyrus":"CYRUS: exact approved model sheet; older broad-shouldered build; silvered hair; pale blue eyes; immaculate graphite technical armor with minimal seams and restrained amber-cyan status lines.",
"Tamz":"TAMZ: exact approved model sheet; braided hair; strong grounded stance; gray field jacket; practical cargo trousers; intentional patch/insignia wear only."}

def load(p):return json.loads(p.read_text(encoding="utf-8"))
def norm(x):
 if isinstance(x,list):return x
 return [{"id":k,**v} if isinstance(v,dict) else {"id":k,"value":v} for k,v in (x or {}).items()]
def read(p,e=None):
 if e=="gzip-base64":return json.loads(gzip.decompress(base64.b64decode("".join(p.read_text().split()),validate=True)).decode())
 return load(p)
def write(p,x,e=None):
 raw=json.dumps(x,ensure_ascii=False,separators=(",",":")).encode()
 if e=="gzip-base64":p.write_text(base64.b64encode(gzip.compress(raw,9,mtime=0)).decode(),encoding="utf-8")
 else:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def fixstr(t):
 for a,b in sorted(ALIASES.items(),key=lambda z:-len(z[0])):t=t.replace(a,b)
 t=re.sub(r"@starsplit\b","",t,flags=re.I)
 for a,b in PHRASE_FIXES.items():t=t.replace(a,b)
 t=t.replace("holographic projector","optical projection unit")
 t=re.sub(r"\brusted\b","weathered",t,flags=re.I);t=re.sub(r"\btattered\b","worn",t,flags=re.I);t=re.sub(r"\bmakeshift\b","field-built",t,flags=re.I)
 t=re.sub(r"\bscavenger fleet\b","salvager fleet",t,flags=re.I);t=re.sub(r"\bnomadic fleet of scavengers\b","nomadic salvager fleet",t,flags=re.I);t=re.sub(r"\bprimitive\b","tactile analog",t,flags=re.I)
 return re.sub(r" {2,}"," ",re.sub(r" +([,.])",r"\1",t)).strip()
def strings(x):
 if isinstance(x,str):return fixstr(x)
 if isinstance(x,list):return [strings(v) for v in x]
 if isinstance(x,dict):return {k:strings(v) for k,v in x.items()}
 return x
def quotes(t):return [m.group(1).strip() for m in re.finditer(r'[“\"]([^\"”]{3,350})[”\"]',t)]
def noquotes(t):return re.sub(r'[“\"]([^\"”]*)[”\"]',' ',t)
def mentions(t,n):return bool(re.search(rf'(?<![A-Za-z]){n}(?![A-Za-z])|{re.escape(CANON[n])}',t,re.I))
def cast(s):
 text=noquotes(s.get("summary","")); names=[n for n in CANON if mentions(text,n)]
 return [n for n in CANON if n in names]
def last_subject(before,present):
 # Walk narrative clauses, carrying singular subject through pronoun-led follow-ons.
 subject=None
 for clause in re.split(r'(?<=[.!?])\s+|;\s+|\.\s*',before):
  c=clause.strip()
  explicit=[]
  for n in present:
   hits=list(re.finditer(rf'\b{n}\b',c,re.I))
   if hits:explicit.append((hits[-1].start(),n))
  if explicit:subject=max(explicit)[1]
  elif re.match(r'^(He|She)\b',c,re.I):pass
 return subject
def dialogue(scene,present):
 summary=scene.get("summary",""); ms=list(re.finditer(r'[“\"]([^\"”]{3,350})[”\"]',summary)); out=[]; override=DIALOGUE_OVERRIDES.get(scene.get("id",""),[])
 for i,m in enumerate(ms):
  q=m.group(1).strip(); before=summary[:m.start()]; after=summary[m.end():m.end()+180]; speaker=override[i] if i<len(override) else None
  if not speaker:
   x=re.search(r'(Arvin|Milo|Lucia|Cyrus|Tamz)\s+(?:says|whispers|notes|declares|replies|asks)\b',after,re.I)
   if x:speaker=x.group(1).title()
  if not speaker:
   # Explicit 'X says:' immediately before quote wins.
   x=re.search(r'(Arvin|Milo|Lucia|Cyrus|Tamz)\s+(?:says|whispers|notes|declares|replies|asks)\s*:?\s*$',before,re.I)
   if x:speaker=x.group(1).title()
  if not speaker:speaker=last_subject(before,present)
  if speaker not in present:speaker=None
  if not speaker and len(present)==1:speaker=present[0]
  if not speaker:
   addressed=[n for n in present if re.search(rf'\b{n}\b',q,re.I)]
   if len(present)==2 and len(addressed)==1:speaker=next(n for n in present if n!=addressed[0])
  if not speaker and len(present)==2 and re.search(r'\b(?:we|our|us)\b',q,re.I) and "Cyrus" in present:
   others=[n for n in present if n!="Cyrus"]
   if len(others)==1:speaker=others[0]
  if not speaker:raise ValueError(f"{scene.get('id')}: cannot resolve speaker for quote {q!r}; present={present}")
  out.append({"handle":CANON[speaker],"speaker":speaker,"text":q})
 return out
def setting(summary,present,sid):
 if "OUTLINE" in sid:return "EPISODE OUTLINE — production beats not yet developed into individual scene recipes in source."
 l=summary.lower()
 if any(k in l for k in ("aegis interception suite","aegis command rover","interceptor cockpit","cockpit of a sleek","inside the interceptor")):return "Aegis mobile interception platform — immaculate graphite corporate hardware, brushed alloy, tactile/glass controls, restrained cyan/amber status light, Mojave terrain beyond."
 if any(k in l for k in ("inside the pressurized welding bay","inside the storage tanker","inside the shadows of a storage tanker","inside the tanker","inside the dim","inside the cramped","inside the cavernous","inside the belly","inside the hull","storage hold","engine bay of the tanker","mobile tanker base","mobile tanker workshop","air of the tanker","mobile workshop","within the tanker","lead tanker","converted fuel tanker")):return "Mobile Launch-Shop tanker interior — maintained retro-industrial aerospace workshop, painted metal, tactile analog-digital instruments, organized tools, practical task lighting and controlled localized wear."
 if any(k in l for k in ("cab of the lead tanker","cabin of the lead truck","control trailer","launch trailer")):return "Launch-Shop mobile control cabin — compact maintained retro-aerospace controls, analog gauges, physical switches, restrained digital readouts and bright Mojave light through the windows."
 if any(k in l for k in ("flatbed truck","tanker roof","atop a","roof of","command deck")):return "Launch-Shop exterior work deck — maintained tanker/flatbed structure, organized field hardware, hard Mojave sun and broad desert horizon."
 if "solar array" in l or "photovoltaic" in l:return "Damaged solar-array recovery site — bright open desert, geometric photovoltaic structures, organized salvage operation and maintained technical field gear."
 if "wind turbine" in l:return "Decommissioned wind-turbine recovery site — open Mojave basin, large engineered structure, hard desert light and organized field equipment."
 if "radio dish" in l or "communications" in l:return "Decommissioned communications site — monumental late-20th-century infrastructure, open Mojave terrain and purposeful salvage activity."
 if "cave" in l or "cavern" in l:return "Mojave limestone cave — cool pale mineral interior, practical portable worklights, rough stone and equipment carried in from the bright desert."
 if "canyon" in l:return "Mojave box canyon — sun-cut rock walls, narrow vehicle access, dry wash floor and hard reflected desert light."
 if any(k in l for k in ("limestone ridge","limestone outcrop","limestone overlook","ridge","overlook")):return "Mojave limestone ridge — pale fractured stone, bright high-desert sun, long sightlines, sparse scrub and the launch corridor below."
 if any(k in l for k in ("salt flat","salt flats","salt pan","dry lake bed","white salt")):return "Mojave salt flat — immense bright mineral basin, hard blue sky, heat shimmer, distant mountains and clean geometric horizons."
 if any(k in l for k in ("launch pad","launch site","launch rail","base of the rocket","under the skeletal frame","rocket's fuselage","rocket’s fuselage")):return "Mojave field launch site — maintained hand-built aerospace hardware, compact support equipment, practical rigging, hard desert light and broad unobstructed sky."
 if present==["Cyrus"]:return "Aegis Mojave observation position — immaculate graphite interceptor equipment, disciplined field geometry and long-range desert visibility."
 return "Mojave Launch-Shop field site — bright open-desert workspace with maintained legacy aerospace equipment, organized tools, practical rigging and dramatic geological distance."
def action(summary):return re.sub(r'\s+',' ',noquotes(summary)).strip()
def directions(summary,present,loc):
 locks=" ".join(LOCK[n] for n in present) if present else "No principal model sheet is required unless explicitly shown by scene action."
 return [{"text":VISUAL},{"text":"SCENE ACTION — SOURCE-LOCKED: "+action(summary)},
 {"text":"CHARACTER CONTINUITY — "+locks+" Faction wardrobe and body proportions do not change because of location, lighting or action."},
 {"text":"LOCATION / PROP / STATE CONTINUITY — "+loc+" Preserve exact condition, placement and ownership of every named vehicle, tool, component, injury, garment, weapon and piece of damage into adjacent scenes until explicitly changed. Do not invent extra dirt, damage, accessories, vehicles or wardrobe changes."},
 {"text":"CAMERA / LIGHT — Readable prestige-TV coverage with bright Southwest color separation and motivated practical light. Favor physical scale, hands performing real work, clear geography and legible silhouettes over murky atmosphere or generic action coverage."}]
def patch(scene):
 s=strings(scene);present=cast(s);summary=s.get("summary","");sid=s.get("id","");loc=setting(summary,present,sid)
 s["settingText"]=loc;s.pop("setting",None);s["charactersInline"]=[{"name":n,"handle":CANON[n]} for n in present];s.pop("characters",None)
 s["dialogueInline"]=dialogue(s,present);s.pop("dialog",None);f=[]
 if any(n in SALVAGERS for n in present):f.append("BR_Salvagers")
 if "Cyrus" in present:f.append("BR_Aegis")
 s["factions"]=f;s["directionInline"]=directions(summary,present,loc);s.pop("direction",None);return s
shows=load(ROOT/"data/shows.json");show=next(s for s in shows if s.get("id")==SHOW_ID);base=ROOT/show["basePath"]
files=[(show.get("scenesFile","scenes_base.json"),None)]+[(o["file"],o.get("encoding")) for o in show.get("sceneOverlays",[])]
count=0
for rel,enc in files:
 p=base/rel;data=norm(read(p,enc));fixed=[patch(s) for s in data];write(p,fixed,enc);count+=len(fixed)
print("Rebuilt",count,"Backyard Rockets scene recipes across",len(files),"files; all quoted dialogue resolved")
