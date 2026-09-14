#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "shows" / "vikings-2026-s1"
CHUNKS = [BASE / f"pages_i06_p{a:02d}_p{b:02d}.json" for a,b in ((1,6),(7,12),(13,18),(19,24))]
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


def load_pages():
    pages = []
    for path in CHUNKS:
        pages.extend(json.loads(path.read_text(encoding="utf-8")))
    return pages


def validate_pages(pages):
    assert len(pages) == 24
    expected = [f"VIK_S1I06_P{i:02d}" for i in range(1,25)]
    assert [p.get("id") for p in pages] == expected
    total_panels = 0
    for page in pages:
        assert page.get("summary") and page.get("settingText")
        panels = page.get("panelPlan") or []
        assert panels
        total_panels += len(panels)
        assert [p.get("panel") for p in panels] == list(range(1, len(panels)+1))
        dialogue_count = len(page.get("dialogueInline") or [])
        for panel in panels:
            assert panel.get("location") and panel.get("shotType") and panel.get("action")
            for idx in panel.get("dialogueIndices", []):
                assert 0 <= idx < dialogue_count, (page["id"], idx, dialogue_count)
    assert total_panels == 120, total_panels


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
        "sceneOverlays": [{"file": path.name} for path in CHUNKS]
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
    old_status = '"status": "full 24-page development script drafted with dialogue and drawable panel staging; production review and RexPrompt compilation pending",\n      "developmentFile": "issue_06_trial_of_toil_development.json",'
    new_status = '"status": "production-ready 24-page script; active RexPrompt page recipes compiled and aggressively audited",\n      "developmentFile": "issue_06_trial_of_toil_development.json",'
    if old_status not in text:
        raise AssertionError("Issue 6 season-plan status text not found")
    text = text.replace(old_status, new_status, 1)
    issue5_payload = '''    {
      "payloadIds": "VIK_S1E05_P01-P24",
      "storyPlacement": "Issue 5 — The Skaldic Interface",
      "status": "production-ready"
    }
  ],'''
    issue6_payload = '''    {
      "payloadIds": "VIK_S1E05_P01-P24",
      "storyPlacement": "Issue 5 — The Skaldic Interface",
      "status": "production-ready"
    },
    {
      "payloadIds": "VIK_S1I06_P01-P24",
      "storyPlacement": "Issue 6 — Trial of Toil",
      "status": "production-ready",
      "source": "Compiled from the approved full Issue 6 script into four active plain-JSON page overlays after page-level visual and assembler audit."
    }
  ],'''
    if issue5_payload not in text:
        raise AssertionError("Issue 5 payload tail not found")
    text = text.replace(issue5_payload, issue6_payload, 1)
    text = text.replace(
        '    "Production edit/review of Issues 6–8 full page scripts before compilation",\n    "Compilation of approved Issues 6–8 scripts into the current active RexPrompt page-recipe structures",',
        '    "Production edit/review of Issues 7–8 full page scripts before compilation",\n    "Compilation of approved Issues 7–8 scripts into the current active RexPrompt page-recipe structures",'
    )
    PLAN.write_text(text, encoding="utf-8")


def main():
    pages = load_pages()
    validate_pages(pages)
    update_characters()
    update_shows()
    update_script()
    update_plan()
    print(f"Validated and registered {len(pages)} Issue 6 pages / {sum(len(p['panelPlan']) for p in pages)} panels.")

if __name__ == "__main__":
    main()
