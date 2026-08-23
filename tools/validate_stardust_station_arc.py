#!/usr/bin/env python3
import base64, gzip, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SHOW=ROOT/"data"/"shows"/"stardust-station"
MANIFEST=ROOT/"data"/"shows.json"

DIR_PREFIXES=(
    "STARDUST STATION VISUAL LANGUAGE:",
    "PAGE ACTION — SOURCE-LOCKED:",
    "CHARACTER CONTINUITY —",
    "LOCATION / PROP / STATE CONTINUITY —",
    "CAMERA / LIGHT —",
    "COMIC PAGE / LETTERING —",
)
RANGES=((1,6),(7,12),(13,18),(19,22))

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def decode(path):
    encoded="".join(path.read_text(encoding="utf-8").split())
    return json.loads(gzip.decompress(base64.b64decode(encoded,validate=True)).decode("utf-8"))

characters=load(SHOW/"characters.json")
handles={v.get("handle") for v in characters.values() if isinstance(v,dict) and v.get("handle")}
if "@sds.Liaison" not in handles:
    raise SystemExit("Corporate liaison canonical handle missing")

shows=load(MANIFEST)
show_ids={x.get("id") for x in shows}
for issue in range(4,11):
    sid=f"stardust-station-e{issue:02d}"
    if sid not in show_ids:
        raise SystemExit(f"Manifest selection missing: {sid}")

issues={}
for issue in range(4,11):
    pages=[]
    for a,b in RANGES:
        path=SHOW/"encoded"/f"pages_e{issue:02d}_p{a:02d}_p{b:02d}.json.gzb64"
        if not path.exists():
            raise SystemExit(f"Missing payload: {path.name}")
        pages.extend(decode(path))
    if len(pages)!=22:
        raise SystemExit(f"Issue {issue}: expected 22 pages, found {len(pages)}")
    if [p.get("page") for p in pages] != list(range(1,23)):
        raise SystemExit(f"Issue {issue}: page sequence drift")
    if sum(p.get("panelCount",0) for p in pages)!=128:
        raise SystemExit(f"Issue {issue}: panel total drift")
    expected_source=f"Stardust Station — Issue {issue} Enhanced Production Script, 2026-08-22"
    for p in pages:
        n=p["page"]
        if p.get("id") != f"SDS_S1E{issue:02d}_P{n:02d}":
            raise SystemExit(f"Issue {issue} page {n}: id drift")
        if p.get("episode") != f"S1E{issue:02d}" or p.get("issue") != issue:
            raise SystemExit(f"Issue {issue} page {n}: episode/issue drift")
        if p.get("source") != expected_source:
            raise SystemExit(f"Issue {issue} page {n}: source drift")
        panels=p.get("panelCount")
        if len(p.get("panelPlan",[])) != panels:
            raise SystemExit(f"Issue {issue} page {n}: panel plan mismatch")
        lines=p.get("dialogueInline",[])
        if not lines:
            raise SystemExit(f"Issue {issue} page {n}: dialogue missing")
        cast={c.get("handle") for c in p.get("charactersInline",[]) if isinstance(c,dict)}
        for d in lines:
            if d.get("handle") not in handles or d.get("handle") not in cast:
                raise SystemExit(f"Issue {issue} page {n}: dialogue/cast handle drift")
            sub=d.get("subtext","")
            if f"exact enhanced Issue {issue} dialogue" not in sub or "Panel " not in sub:
                raise SystemExit(f"Issue {issue} page {n}: dialogue lock missing")
        directions=[x.get("text","") for x in p.get("directionInline",[]) if isinstance(x,dict)]
        if len(directions)!=6:
            raise SystemExit(f"Issue {issue} page {n}: requires six direction locks")
        for got,prefix in zip(directions,DIR_PREFIXES):
            if not got.startswith(prefix):
                raise SystemExit(f"Issue {issue} page {n}: direction prefix drift")
        if directions[1].split(DIR_PREFIXES[1],1)[1].strip() != p.get("summary"):
            raise SystemExit(f"Issue {issue} page {n}: PAGE ACTION != summary")
        if f"exactly {panels} panels" not in directions[5]:
            raise SystemExit(f"Issue {issue} page {n}: exact panel lock missing")
        if "do not add, remove, merge, reorder, paraphrase or invent" not in directions[5].lower():
            raise SystemExit(f"Issue {issue} page {n}: zero-drift guardrail missing")
        if issue>=5 and "SDS_StarTrust" not in p.get("factions",[]):
            raise SystemExit(f"Issue {issue} page {n}: StarTrust continuity missing")
    issues[issue]=pages

story_text={}
for issue,pages in issues.items():
    story_text[issue]=" ".join(
        [p.get("summary","")] + [d.get("text","") for p in pages for d in p.get("dialogueInline",[])]
    )

# Residue remains physical/correlational. No semantic or mind-reading mechanism may enter canon.
for issue,text in story_text.items():
    lower=text.lower()
    forbidden=(
        "the dust knows",
        "the residue knows",
        "the dust wants",
        "the residue wants",
        "reads feelings",
        "reads emotion",
        "crystals chose",
        "the station chose",
        "positive emotions make",
        "conflict makes better",
        "argument makes better",
    )
    for term in forbidden:
        if term in lower:
            raise SystemExit(f"Issue {issue}: semantic/telemetric residue drift: {term}")

# Cross-issue causal ladder.
required={
    5:(
        "Behavioral intervention is not approved.",
        "WELLNESS BASELINE WEEK BEGINS MONDAY.",
    ),
    6:(
        "Intervention altered operating conditions.",
        "No-entry accepted.",
        "No one owes a feeling.",
    ),
    7:(
        "ON-SITE OPERATIONS LIAISON RECOMMENDED.",
        "Fine. I own the visitor route.",
        "VISITOR CONFIRMED: STARTRUST OPERATIONS LIAISON.",
    ),
    8:(
        "No behavioral recipe.",
        "Passive collection only.",
        "TARGET MASS UPDATED.",
    ),
    9:(
        "Target missed.",
        "Quality varied independently of mass.",
        "PILOT STATUS REVIEW SCHEDULED.",
    ),
    10:(
        "We have a fourth.",
        "No inferred emotional fields.",
        "Adaptive Operations / Incidental Materials Observation.",
        "No target.",
        "STATION STATUS: ACTIVE.",
        "Normal enough.",
    ),
}
for issue,terms in required.items():
    for term in terms:
        if term not in story_text[issue]:
            raise SystemExit(f"Issue {issue}: missing continuity payoff: {term}")

# Character progression must accumulate rather than reset.
if "My strongest skill is becoming unavailable." in story_text[8] or "scheduled with myself" in story_text[8]:
    raise SystemExit("Jax reset detected after Issue 3")
for term in ("This one is mine.","Fine. I own the visitor route."):
    if term not in story_text[7]+story_text[8]:
        raise SystemExit(f"Jax ownership progression missing: {term}")
if "I am not selling certainty we do not have." not in story_text[8]:
    raise SystemExit("Astra bounded-honesty progression missing")
if "None that we can defend." not in story_text[8]:
    raise SystemExit("Mira mechanism-uncertainty lock missing")
if "The purpose would still be the number." not in story_text[9]:
    raise SystemExit("Kreeb output-boundary progression missing")
if "Intentional blank space." not in story_text[10]:
    raise SystemExit("Glorp/Kreeb shared-procedure payoff missing")

print("Stardust Station Issues 4-10 arc validation passed")
print("Issues:",7)
print("Pages:",sum(len(v) for v in issues.values()))
print("Panels:",sum(sum(p["panelCount"] for p in v) for v in issues.values()))
