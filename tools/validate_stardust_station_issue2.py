#!/usr/bin/env python3
import base64
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data" / "shows" / "stardust-station"
MANIFEST = ROOT / "data" / "shows.json"
SHOW_ID = "stardust-station-e02"
SOURCE = 'Stardust Station — Issue 2 Enhanced Production Script, 2026-08-22'

EXPECTED = [
    [1, "The Room with Too Many Signs", 5],
    [2, "Temporary Means Mandatory", 6],
    [3, "Astra Restores Normalcy, in Theory", 6],
    [4, "Report It Before It Becomes a Meeting", 6],
    [5, "Correlation Is Not a Confession", 6],
    [6, "Soup Becomes Context", 6],
    [7, "The Actual Problem Is Embarrassingly Physical", 6],
    [8, "The Machine Is Easy", 6],
    [9, "One Page, One Side", 6],
    [10, "The Bright Chair", 6],
    [11, "The One-Page Procedure", 6],
    [12, "One Sample", 5],
    [13, "Normal Lunch Trial", 6],
    [14, "Normal Becomes a Procedure", 6],
    [15, "What the Page Is For", 6],
    [16, "No Sequel for the Soup", 5],
    [17, "Three Rules, Apparently", 6],
    [18, "The Test", 6],
    [19, "Legacy Integration", 6],
    [20, "Emotionally Unverified", 6],
    [21, "Small Things Stay Small", 6],
    [22, "Tag: The Mug", 5],
]
EXPECTED_OVERLAYS = [
    {"file":"encoded/pages_e02_p01_p06.json.gzb64","encoding":"gzip-base64"},
    {"file":"encoded/pages_e02_p07_p12.json.gzb64","encoding":"gzip-base64"},
    {"file":"encoded/pages_e02_p13_p18.json.gzb64","encoding":"gzip-base64"},
    {"file":"encoded/pages_e02_p19_p22.json.gzb64","encoding":"gzip-base64"},
]
REQUIRED_FILES = [*[x["file"] for x in EXPECTED_OVERLAYS]]
DIR_PREFIXES = (
    "STARDUST STATION VISUAL LANGUAGE:",
    "PAGE ACTION — SOURCE-LOCKED:",
    "CHARACTER CONTINUITY —",
    "LOCATION / PROP / STATE CONTINUITY —",
    "CAMERA / LIGHT —",
    "COMIC PAGE / LETTERING —",
)
FORBIDDEN = (
    "Policy and Disorder",
    "Kreeg Hssssk",
    "Pixa9",
    "dust arrow",
    "MUG GRIEF UNRESOLVED",
    "interpersonal sensitivity",
    "It is not about the mug",
)
CRITICAL = (
    "The break room is not a department.",
    "Small thing. That side is warmer than yesterday.",
    "The dust does not know about mugs.",
    "You covered the vent.",
    "One side is how nuance dies.",
    "I need to know what this page is protecting.",
    "Report physical failures. Ask before taking someone else's things. Otherwise, eat.",
    "We are all going to behave like people who have seen a microwave before.",
    "Form 8C trigger was still mapped to appliance-cycle completion.",
    "PRESSURE CORRELATION — CONTENT UNKNOWN",
    "Normal enough.",
)

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

for rel in REQUIRED_FILES:
    if not (SHOW / rel).exists():
        raise SystemExit(f"Missing Issue 2 file: {rel}")

shows = load(MANIFEST)
show = next((s for s in shows if s.get("id") == SHOW_ID), None)
if not show:
    raise SystemExit("Stardust Station Issue 2 missing from data/shows.json")
if show.get("basePath") != "data/shows/stardust-station":
    raise SystemExit("Issue 2 basePath drift")
if show.get("scenesFile") != "pages_base.json":
    raise SystemExit("Issue 2 base pages drift")
if show.get("unitLabel") != "PAGE":
    raise SystemExit("Issue 2 must assemble as PAGE units")
if show.get("sceneOverlays") != EXPECTED_OVERLAYS:
    raise SystemExit("Issue 2 overlay manifest drift")
generation = show.get("generationLine","").lower()
if "issue #2" not in generation or "comic page" not in generation:
    raise SystemExit("Issue 2 generationLine must identify Issue #2 comic-page production")
if "issue 1" not in generation:
    raise SystemExit("Issue 2 generationLine must lock released Issue 1 as visual canon")

pages=[]
for overlay in EXPECTED_OVERLAYS:
    encoded="".join((SHOW / overlay["file"]).read_text(encoding="utf-8").split())
    decoded=gzip.decompress(base64.b64decode(encoded,validate=True)).decode("utf-8")
    pages.extend(json.loads(decoded))

if len(pages) != 22:
    raise SystemExit(f"Expected 22 Issue 2 pages, found {len(pages)}")

characters=load(SHOW / "characters.json")
handles={v.get("handle") for v in characters.values() if isinstance(v,dict) and v.get("handle")}
settings=load(SHOW / "settings.json")
regions=load(SHOW / "regions.json")
factions=load(SHOW / "factions.json")
all_text=json.dumps(pages,ensure_ascii=False)

for term in FORBIDDEN:
    if term.lower() in all_text.lower():
        raise SystemExit(f"Forbidden stale/semantic material in Issue 2: {term}")
for term in CRITICAL:
    if term not in all_text:
        raise SystemExit(f"Missing Issue 2 critical line: {term}")

seen=set()
for p,(number,title,panels) in zip(pages,EXPECTED):
    eid=f"SDS_S1E02_P{number:02d}"
    if p.get("id") != eid:
        raise SystemExit(f"Page {number} id drift: {p.get('id')}")
    if p["id"] in seen:
        raise SystemExit(f"Duplicate page id {p['id']}")
    seen.add(p["id"])
    if p.get("episode") != "S1E02" or p.get("issue") != 2 or p.get("page") != number:
        raise SystemExit(f"{eid} numbering drift")
    if p.get("pageTitle") != title or p.get("panelCount") != panels:
        raise SystemExit(f"{eid} title/panel drift")
    if p.get("source") != SOURCE:
        raise SystemExit(f"{eid} source drift")
    if len(p.get("panelPlan",[])) != panels:
        raise SystemExit(f"{eid} panelPlan count mismatch")
    if p.get("setting") not in settings or p.get("region") not in regions:
        raise SystemExit(f"{eid} unknown setting/region")
    for faction in p.get("factions",[]):
        if faction not in factions:
            raise SystemExit(f"{eid} unknown faction {faction}")
    cast={c.get("handle") for c in p.get("charactersInline",[]) if isinstance(c,dict) and c.get("handle")}
    if not cast:
        raise SystemExit(f"{eid} missing cast")
    if cast - handles:
        raise SystemExit(f"{eid} unknown cast handles {sorted(cast-handles)}")
    lines=p.get("dialogueInline",[])
    if not lines:
        raise SystemExit(f"{eid} missing exact dialogue")
    for line in lines:
        h=line.get("handle")
        if h not in handles:
            raise SystemExit(f"{eid} unknown dialogue handle {h}")
        if h != "@sds.Station" and h not in cast:
            raise SystemExit(f"{eid} dialogue speaker not in declared cast: {h}")
        sub=line.get("subtext","")
        if "exact enhanced Issue 2 dialogue" not in sub or "Panel " not in sub:
            raise SystemExit(f"{eid} dialogue lock missing")
        try:
            pn=int(sub.split("Panel ",1)[1].split(" ",1)[0])
        except Exception as exc:
            raise SystemExit(f"{eid} bad dialogue panel lock: {sub}") from exc
        if not 1 <= pn <= panels:
            raise SystemExit(f"{eid} dialogue panel out of range: {pn}")
    direction=[x.get("text","") for x in p.get("directionInline",[]) if isinstance(x,dict)]
    if len(direction) != 6:
        raise SystemExit(f"{eid} requires six direction locks")
    for got,prefix in zip(direction,DIR_PREFIXES):
        if not got.startswith(prefix):
            raise SystemExit(f"{eid} direction prefix drift: {prefix}")
    action=direction[1].split(DIR_PREFIXES[1],1)[1].strip()
    if action != p.get("summary"):
        raise SystemExit(f"{eid} PAGE ACTION must equal summary")
    if f"exactly {panels} panels" not in direction[5]:
        raise SystemExit(f"{eid} exact panel lock missing")
    if "do not add, remove, merge, reorder, paraphrase or invent" not in direction[5].lower():
        raise SystemExit(f"{eid} zero-drift lettering guardrail missing")

if pages[3]["relationshipFocus"] != ["Astra / Glorp / Kreeb scope control", "Jax / Zib early reporting"]:
    raise SystemExit("Page 4 must establish Jax's early-reporting continuity advance")
if "Jax's early report leads Zib" not in pages[6]["summary"]:
    raise SystemExit("Page 7 must causally pay off Jax's Page 4 report")
if pages[14]["relationshipFocus"] != ["Astra / Glorp / Kreeb core issue ownership"]:
    raise SystemExit("Page 15 must give Astra/Glorp/Kreeb core issue ownership")
if pages[17]["pageTitle"] != "The Test":
    raise SystemExit("Page 18 must remain the microwave-test climax")
if "correlation rather than meaning" not in pages[19]["summary"]:
    raise SystemExit("Page 20 must preserve non-semantic residue framing")
if sum(p["panelCount"] for p in pages) != 128:
    raise SystemExit("Issue 2 panel total drift")

print("Stardust Station Issue 2 validation passed")
print("Pages:",len(pages))
print("Panels:",sum(p["panelCount"] for p in pages))
print("Dialogue entries:",sum(len(p["dialogueInline"]) for p in pages))
