#!/usr/bin/env python3
import base64
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data" / "shows" / "stardust-station"
MANIFEST = ROOT / "data" / "shows.json"
SHOW_ID = "stardust-station-e03"
SOURCE = "Stardust Station — Issue 3 Enhanced Production Script, 2026-08-22"

EXPECTED = [
    (1, "Ten Minutes", 5),
    (2, "Three Items, No Archaeology", 6),
    (3, "Observable Metrics Only", 6),
    (4, "Jax Is Available", 6),
    (5, "What Does Owner Mean", 6),
    (6, "The Dust Still Cannot Read", 6),
    (7, "Zib Needs the Wall", 5),
    (8, "Someone Should", 6),
    (9, "Item One Returns", 6),
    (10, "Correlation, Not Vocabulary", 6),
    (11, "Hide the Dashboard", 6),
    (12, "Support Is Not Ownership", 6),
    (13, "Decision Without Owner", 6),
    (14, "The Ownership Rule", 6),
    (15, "Jax Takes One", 6),
    (16, "Enough Meeting", 5),
    (17, "The Record Objects", 6),
    (18, "The Meeting Becomes Work", 6),
    (19, "Ten Minutes of Repair", 6),
    (20, "After", 6),
    (21, "That Last One Is the Metric", 6),
    (22, "Tag: Follow-Up Not Scheduled", 5),
]
EXPECTED_OVERLAYS = [
    {"file":"encoded/pages_e03_p01_p06.json.gzb64","encoding":"gzip-base64"},
    {"file":"encoded/pages_e03_p07_p12.json.gzb64","encoding":"gzip-base64"},
    {"file":"encoded/pages_e03_p13_p18.json.gzb64","encoding":"gzip-base64"},
    {"file":"encoded/pages_e03_p19_p22.json.gzb64","encoding":"gzip-base64"},
]
DIR_PREFIXES = (
    "STARDUST STATION VISUAL LANGUAGE:",
    "PAGE ACTION — SOURCE-LOCKED:",
    "CHARACTER CONTINUITY —",
    "LOCATION / PROP / STATE CONTINUITY —",
    "CAMERA / LIGHT —",
    "COMIC PAGE / LETTERING —",
)
FORBIDDEN = (
    "The dust moved.",
    "it prefers the agenda item nobody wants",
    "OWNERSHIP AVOIDANCE:",
    "DEFLECTION FORMING",
    "MUG SYMBOLISM",
    "You schedule elsewhere because here makes you real",
    "That is your fear wearing a joke",
    "unresolved mug grief",
    "SEE ALSO: SOUP",
    "the dust is reacting to the word",
    "dust arrow",
    "MUG GRIEF UNRESOLVED",
    "Kreeg Hssssk",
    "Pixa9",
)
CRITICAL = (
    "The dust still cannot read.",
    "I am fully available in an advisory capacity.",
    "Unnamed action item detected.",
    "The dust is not reacting to the word 'owner.'",
    "You keep offering help that ends when the task starts.",
    "Fine. I own the access label.",
    "No more agenda. We have enough decisions to do work.",
    "Then they remain unassigned until someone has a reason to do them.",
    "An empty line can be honest.",
    "PRESSURE CORRELATION — CONTENT UNKNOWN",
    "That last one is the metric.",
    "FOLLOW-UP NOT SCHEDULED.",
    "WORK IN PROGRESS",
)

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

shows = load(MANIFEST)
show = next((s for s in shows if s.get("id") == SHOW_ID), None)
if not show:
    raise SystemExit("Stardust Station Issue 3 missing from data/shows.json")
if show.get("basePath") != "data/shows/stardust-station":
    raise SystemExit("Issue 3 basePath drift")
if show.get("scenesFile") != "pages_base.json":
    raise SystemExit("Issue 3 base pages drift")
if show.get("unitLabel") != "PAGE":
    raise SystemExit("Issue 3 must assemble as PAGE units")
if show.get("sceneOverlays") != EXPECTED_OVERLAYS:
    raise SystemExit("Issue 3 overlay manifest drift")
generation = show.get("generationLine","").lower()
for required in ("issue #3","comic page","issue 1","issue 2"):
    if required not in generation:
        raise SystemExit(f"Issue 3 generationLine missing continuity lock: {required}")

pages=[]
for overlay in EXPECTED_OVERLAYS:
    path=SHOW/overlay["file"]
    if not path.exists():
        raise SystemExit(f"Missing Issue 3 payload: {overlay['file']}")
    encoded="".join(path.read_text(encoding="utf-8").split())
    decoded=gzip.decompress(base64.b64decode(encoded,validate=True)).decode("utf-8")
    pages.extend(json.loads(decoded))

if len(pages) != 22:
    raise SystemExit(f"Expected 22 Issue 3 pages, found {len(pages)}")

characters=load(SHOW/"characters.json")
handles={v.get("handle") for v in characters.values() if isinstance(v,dict) and v.get("handle")}
settings=load(SHOW/"settings.json")
regions=load(SHOW/"regions.json")
factions=load(SHOW/"factions.json")
all_text=json.dumps(pages,ensure_ascii=False)

for term in FORBIDDEN:
    if term.lower() in all_text.lower():
        raise SystemExit(f"Forbidden stale/semantic material in Issue 3: {term}")
for term in CRITICAL:
    if term not in all_text:
        raise SystemExit(f"Missing Issue 3 critical line: {term}")

seen=set()
for p,(number,title,panels) in zip(pages,EXPECTED):
    eid=f"SDS_S1E03_P{number:02d}"
    if p.get("id") != eid:
        raise SystemExit(f"Page {number} id drift: {p.get('id')}")
    if p["id"] in seen:
        raise SystemExit(f"Duplicate page id {p['id']}")
    seen.add(p["id"])
    if p.get("episode") != "S1E03" or p.get("issue") != 3 or p.get("page") != number:
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
    if not cast or cast-handles:
        raise SystemExit(f"{eid} cast drift")
    lines=p.get("dialogueInline",[])
    if not lines:
        raise SystemExit(f"{eid} missing exact dialogue")
    for line in lines:
        h=line.get("handle")
        if h not in handles or h not in cast:
            raise SystemExit(f"{eid} dialogue speaker not in declared canonical cast: {h}")
        sub=line.get("subtext","")
        if "exact enhanced Issue 3 dialogue" not in sub or "Panel " not in sub:
            raise SystemExit(f"{eid} dialogue lock missing")
        pn=int(sub.split("Panel ",1)[1].split(" ",1)[0])
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

p4=" ".join(x["text"] for x in pages[3]["dialogueInline"])
if "advisory capacity" not in p4 or "elsewhere" in p4.lower():
    raise SystemExit("Page 4 must advance Jax from escape to ownership-evasion while staying present")
p6=" ".join(x["text"] for x in pages[5]["dialogueInline"])
if "dust still cannot read" not in p6.lower():
    raise SystemExit("Page 6 must explicitly preserve non-semantic residue")
p10=" ".join(x["text"] for x in pages[9]["dialogueInline"])
if "not reacting to the word 'owner'" not in p10.lower():
    raise SystemExit("Page 10 must reject vocabulary-based residue interpretation")
p15=" ".join(x["text"] for x in pages[14]["dialogueInline"])
if "I own the access label" not in p15:
    raise SystemExit("Page 15 must advance Jax through voluntary small-task ownership")
p17=" ".join(x["text"] for x in pages[16]["dialogueInline"])
if "remain unassigned" not in p17 or "empty line can be honest" not in p17:
    raise SystemExit("Page 17 must establish Astra/Kreeb honest incompleteness")
if pages[17].get("relationshipMode") != "split-small-groups":
    raise SystemExit("Page 18 must break the meeting into owned small-group work")
p22=" ".join(x["text"] for x in pages[21]["dialogueInline"])
if "No." not in p22 or "Exactly." not in p22:
    raise SystemExit("Page 22 must pay off Astra refusing unnecessary follow-up")

if sum(p["panelCount"] for p in pages) != 128:
    raise SystemExit("Issue 3 panel total drift")

print("Stardust Station Issue 3 validation passed")
print("Pages:",len(pages))
print("Panels:",sum(p["panelCount"] for p in pages))
print("Dialogue entries:",sum(len(p["dialogueInline"]) for p in pages))
