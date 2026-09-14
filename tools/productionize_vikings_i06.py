#!/usr/bin/env python3
from __future__ import annotations

import base64, gzip, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "shows" / "vikings-2026-s1"
PAYLOAD = BASE / "encoded" / "pages_i06.json.gzb64"
CHARS = BASE / "characters.json"
SHOWS = ROOT / "data" / "shows.json"
SCRIPT = BASE / "issue_06_trial_of_toil_script.md"
PLAN = BASE / "season_one_plan.json"

GENERATION_LINE = (
    "Finished full-color portrait interior story comic page in the established Vikings 2026 sequential-art language. "
    "Bright ordinary-2026 New York realism with grounded human acting and clear sequential storytelling. "
    "Use released Issue 1 story art as strict visual canon for established identity and world appearance, and approved current references only for newer continuity. "
    "Preserve scripted panel count and order, panel geography, character placement, props, causal action, and dialogueInline exactly. "
    "Interior story page only; no cover, editorial, dossier, credits, header, or character-label language unless scripted."
)


def load_payload():
    b64 = "".join(PAYLOAD.read_text(encoding="utf-8").split())
    return json.loads(gzip.decompress(base64.b64decode(b64)).decode("utf-8"))


def validate_payload(pages):
    assert len(pages) == 24
    expected = [f"VIK_S1I06_P{i:02d}" for i in range(1,25)]
    assert [p.get("id") for p in pages] == expected
    for p in pages:
        assert p.get("summary") and p.get("settingText")
        panels = p.get("panelPlan") or []
        assert panels
        assert [x.get("panel") for x in panels] == list(range(1, len(panels)+1))
        n = len(p.get("dialogueInline") or [])
        for x in panels:
            assert x.get("location") and x.get("shotType") and x.get("action")
            for idx in x.get("dialogueIndices", []):
                assert 0 <= idx < n, (p["id"], idx, n)
    assert sum(len(p["panelPlan"]) for p in pages) == 120


def update_characters():
    data = json.loads(CHARS.read_text(encoding="utf-8"))
    data["kin-man-1"] = {
        "name": "First Male Kin",
        "handle": "@vik.KinMan1",
        "role": "Production identity label for one of the two unnamed male Kin; this is not an in-world personal name.",
        "visualAnchor": "Use the same specific established male Kin identity carried by the laundry/laundromat thread in current middle-season production and the approved current character reference. Preserve his released Issue 1 face, build, hair, historical clothing identity, and current continuity; do not substitute Bjorn, Gunnar, or the other male Kin.",
        "performance": "Grounded, practical, increasingly neighborhood-rooted. Ordinary competence is more important than broad fish-out-of-water reaction.",
        "promptContinuity": [
            "First Male Kin is a production label only, not a locked personal name",
            "He is one of exactly two male Kin and remains visually distinct from Second Male Kin",
            "Do not clone Bjorn or Gunnar into this identity"
        ]
    }
    data["kin-man-2"] = {
        "name": "Second Male Kin",
        "handle": "@vik.KinMan2",
        "role": "Production identity label for the other unnamed male Kin; this is not an in-world personal name.",
        "visualAnchor": "Use the same specific established male Kin identity carried by the park/independent-movement thread in current middle-season production and the approved current character reference. Preserve his released Issue 1 face, build, hair, historical clothing identity, and current continuity; do not substitute Bjorn, Gunnar, or First Male Kin.",
        "performance": "Grounded, practical, comfortable with modern competence while remaining less willing to promise a permanent future.",
        "promptContinuity": [
            "Second Male Kin is a production label only, not a locked personal name",
            "He is one of exactly two male Kin and remains visually distinct from First Male Kin",
            "Do not clone Bjorn or Gunnar into this identity"
        ]
    }
    data["group-facilitator"] = {
        "name": "Group Facilitator",
        "handle": "@vik.GroupFacilitator",
        "role": "Unnamed peer-support facilitator for DTI temporal arrivals; not a clinician and not Bjorn's authority figure.",
        "visualAnchor": "Grounded middle-aged New Yorker in ordinary contemporary clothes, calm unshowy presence, seated on the same stackable chairs as participants. No therapist-office styling, white coat, podium, or authority costume.",
        "performance": "Plainspoken, patient, willing to interrupt Bjorn without treating him as a problem to manage. Firm boundaries, little ceremony."
    }
    data["participant-1987"] = {
        "name": "1987 Participant",
        "handle": "@vik.Participant1987",
        "role": "Recurring unnamed adult displaced from 1987 who challenges Bjorn's assumption that chronological distance measures loss.",
        "visualAnchor": "Physically mid-30s displaced adult in practical contemporary thrifted layers, with at most one subtle personal object retained from the late 1980s. Never a period-costume joke.",
        "performance": "Direct, guarded, dry, and capable of pushing back on Bjorn. Family grief is lived-in rather than melodramatic."
    }
    CHARS.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_shows():
    shows = json.loads(SHOWS.read_text(encoding="utf-8"))
    shows = [s for s in shows if s.get("id") != "vikings-2026-s1-e06"]
    entry = {
        "id": "vikings-2026-s1-e06",
        "name": "Vikings 2026 — Season 1 / Issue 6 — Trial of Toil",
        "basePath": "data/shows/vikings-2026-s1",
        "scenesFile": "pages_base.json",
        "unitLabel": "PAGE",
        "generationLine": GENERATION_LINE,
        "sceneOverlays": [{"file":"encoded/pages_i06.json.gzb64","encoding":"gzip-base64"}]
    }
    pos = next((i+1 for i,s in enumerate(shows) if s.get("id") == "vikings-2026-s1-e05"), len(shows))
    shows.insert(pos, entry)
    SHOWS.write_text(json.dumps(shows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_script():
    text = SCRIPT.read_text(encoding="utf-8")
    replacements = {
        "Status: DEVELOPMENT SCRIPT — 24-PAGE WRITING + DRAWABLE PAGE STAGING; NOT YET ACTIVE ASSEMBLER INPUT": "Status: PRODUCTION SCRIPT — 24-PAGE WRITING + DRAWABLE PAGE STAGING; ACTIVE ASSEMBLER INPUT",
        "Food comes from men downstairs.": "Food comes from the shop downstairs.",
        "**GROUP FACILITATOR:** Now you're listening.": "**GROUP FACILITATOR:** That's the difference.",
        "**GROUP FACILITATOR:** You may be. Seeing the truth does not make it yours.": "**GROUP FACILITATOR:** You may be. They still did not ask you to say it for them.",
        "**UPSTAIRS NEIGHBOR:** IKEA.": "**UPSTAIRS NEIGHBOR:** Flat-pack furniture.",
        "5. **Exterior long lens from apartment window / street below.** Bjorn is already half a block away moving with purpose through ordinary foot traffic.": "5. **Exterior cut to the Bushwick sidewalk.** Bjorn is already half a block from the apartment, moving with purpose through ordinary foot traffic; do not imply Carrie or Gunnar can see him clearly from inside.",
        "**GROUP FACILITATOR:** A person without useful work suffers. That's not the same sentence.": "**GROUP FACILITATOR:** They suffer. That's different.",
        "**BJORN:** Care without purpose makes a child of an adult.\n   **GROUP FACILITATOR:** Then give adults ways to contribute. Don't make contribution the price of being cared for.": "**BJORN:** If everyone feeds a man and asks nothing of him, they make him a child.\n   **GROUP FACILITATOR:** Then ask something of him. Don't make him earn the right to be fed.",
        "**GROUP FACILITATOR:** A hand can be offered before it's required.\n   **BJORN:** You make everything sound small.\n   **GROUP FACILITATOR:** Most of life is small.": "**GROUP FACILITATOR:** You don't have to be needed before you can be useful.\n   **BJORN:** You make everything sound small.\n   **GROUP FACILITATOR:** Most days are."
    }
    for old,new in replacements.items():
        if old not in text:
            raise AssertionError(f"Expected script text missing: {old[:80]}")
        text = text.replace(old,new)
    SCRIPT.write_text(text, encoding="utf-8")


def update_plan():
    text = PLAN.read_text(encoding="utf-8")
    # Keep formatting intact; change only Issue 6 status language if the pre-production phrase is present.
    text = text.replace(
        '"status": "full 24-page development script complete; ready for production compilation",',
        '"status": "production-ready 24-page script; active RexPrompt page recipes compiled and audited",'
    )
    PLAN.write_text(text, encoding="utf-8")


def main():
    pages = load_payload()
    validate_payload(pages)
    update_characters()
    update_shows()
    update_script()
    update_plan()
    print(f"Validated and registered {len(pages)} Issue 6 pages / {sum(len(p['panelPlan']) for p in pages)} panels.")

if __name__ == "__main__":
    main()
