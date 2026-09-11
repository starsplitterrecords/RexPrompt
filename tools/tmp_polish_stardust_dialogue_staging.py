#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data" / "shows" / "stardust-station"

REPLACEMENTS = {
    "pages_e08.json": {
        "Primary composition: 6-panel page in Observation-glass alcove off Stardust Station's working operations level. Opening image: The Liaison asks Astra to step aside near the observation glass. Middle image: Medium close on the Operations Liaison on the live call, composed and attentive. Closing image: The Liaison does not threaten her.":
        "Primary composition: 6-panel page in Observation-glass alcove off Stardust Station's working operations level. Opening image: The Liaison asks Astra to step aside near the observation glass. Middle image: The Liaison turns from the bracket status to the active lab visible beyond the glass, calm and matter-of-fact. Closing image: The Liaison does not threaten her.",
        "PANEL 2 — Medium close on the Operations Liaison on the live call, composed and attentive. LIAISON: Your station needs procurement priority.":
        "PANEL 2 — Beside the observation glass, the Liaison rests one hand on the compact case and gestures toward the temporary-bracket status visible across the working level. LIAISON: Your station needs procurement priority.",
        "PANEL 4 — Medium close on the Operations Liaison on the live call, composed and attentive. LIAISON: A material pilot is easier to fund than \\\"interesting operations.\\\"":
        "PANEL 4 — The Liaison turns from the bracket status to the active lab visible beyond the glass, calm and matter-of-fact. LIAISON: A material pilot is easier to fund than \\\"interesting operations.\\\"",
        "PANEL 2 — Medium close on the Operations Liaison on the live call, composed and attentive. LIAISON: I can recommend a limited pilot. Central review will ask what it produces.":
        "PANEL 2 — The Liaison sets the closed compact case on the lab bench beside the sample tray. LIAISON: I can recommend a limited pilot. Central review will ask what it produces.",
        "PANEL 4 — Medium close on Astra in Lab Work Area; expression readable and eyeline directed toward the others. ASTRA: I am not selling certainty we do not have.":
        "PANEL 4 — Astra keeps the sample tray and the operations record side by side on the bench, one hand braced between them. ASTRA: I am not selling certainty we do not have.",
    },
    "pages_e09.json": {
        "PANEL 2 — Medium close on Astra in Main Bullpen / Admin Hub; expression readable and eyeline directed toward the others. ASTRA: We could clear it early too.":
        "PANEL 2 — Astra keeps one finger on the six-day conveyor-service entry in the maintenance calendar and looks to Zib. ASTRA: We could clear it early too.",
        "PANEL 2 — Medium close on Astra in Cargo Bay / Dock 2; expression readable and eyeline directed toward the others. ASTRA: Conveyor service. Can we do it this afternoon?":
        "PANEL 2 — Astra stands beside the cargo service lane with the schedule open on her tablet, pointing to the empty afternoon window. ASTRA: Conveyor service. Can we do it this afternoon?",
        "PANEL 2 — Medium close on Astra in Cargo Bay / Dock 2; expression readable and eyeline directed toward the others. ASTRA: Six minutes. Close clean, then Dock 2.":
        "PANEL 2 — Astra looks from the half-finished conveyor to the shuttle-hold timer and raises one hand to halt further service. ASTRA: Six minutes. Close clean, then Dock 2.",
        "PANEL 4 — Medium close on Astra in Main Bullpen / Admin Hub; expression readable and eyeline directed toward the others. ASTRA: Stop. Put the station back.":
        "PANEL 4 — Astra closes the accelerated-work list and restores the ordinary maintenance calendar on the screen. ASTRA: Stop. Put the station back.",
    },
    "pages_e10.json": {
        "Primary composition: 5-panel page in Cargo Bay / Dock 2. Opening image: Jax walks Astra to the cargo lane and opens the route history on his route slate beside the actual conveyor they serviced early. Middle image: Medium close on Jax in Cargo Bay / Dock 2; expression readable and eyeline directed toward the others. Closing image: Jax sends the Dock 2 access-log entry from the route slate to Astra's review packet.":
        "Primary composition: 5-panel page in Cargo Bay / Dock 2. Opening image: Jax walks Astra to the cargo lane and opens the route history on his route slate beside the actual conveyor they serviced early. Middle image: Jax traces the route slate from the accelerated conveyor closure to the Dock 2 delay, with the actual lane behind him. Closing image: Jax sends the Dock 2 access-log entry from the route slate to Astra's review packet.",
        "PANEL 3 — Medium close on Jax in Cargo Bay / Dock 2; expression readable and eyeline directed toward the others. JAX: When collection became the reason for the job, the actual route got worse.":
        "PANEL 3 — Jax traces the route slate from the accelerated conveyor closure to the Dock 2 delay, with the actual lane behind him. JAX: When collection became the reason for the job, the actual route got worse.",
        "Primary composition: 6-panel page in Main Bullpen / Admin Hub. Opening image: The Operations Liaison joins the review by live call from another StarTrust site. Middle image: Medium close on the Operations Liaison on the live call, composed and attentive. Closing image: The Liaison keeps reading.":
        "Primary composition: 6-panel page in Main Bullpen / Admin Hub. Opening image: The Operations Liaison joins the review by live call from another StarTrust site. Middle image: On the live call, the Liaison lowers the tablet after reading the fourth recommendation, professional and skeptical. Closing image: The Liaison keeps reading.",
        "PANEL 4 — Medium close on the Operations Liaison on the live call, composed and attentive. LIAISON: This is not a standard pilot category.":
        "PANEL 4 — On the live call, the Liaison lowers the tablet after reading the fourth recommendation, professional and skeptical. LIAISON: This is not a standard pilot category.",
        "PANEL 2 — Medium close on the Operations Liaison on the live call, composed and attentive. LIAISON: Dedicated material pilot is the safer funding recommendation.":
        "PANEL 2 — On the live call, the Liaison points to the budget comparison on the shared review screen. LIAISON: Dedicated material pilot is the safer funding recommendation.",
        "Primary composition: 6-panel page in Main Bullpen / Admin Hub. Opening image: The Liaison asks directly. Middle image: Medium close on Astra in Main Bullpen / Admin Hub; expression readable and eyeline directed toward the others. Closing image: Astra does not revise it.":
        "Primary composition: 6-panel page in Main Bullpen / Admin Hub. Opening image: The Liaison asks directly. Middle image: Astra slides the three standard options aside and keeps the handwritten fourth recommendation centered in front of her. Closing image: Astra does not revise it.",
        "PANEL 4 — Medium close on Astra in Main Bullpen / Admin Hub; expression readable and eyeline directed toward the others. ASTRA: Recommend the station we actually run.":
        "PANEL 4 — Astra slides the three standard options aside and keeps the handwritten fourth recommendation centered in front of her. ASTRA: Recommend the station we actually run.",
        "Primary composition: 6-panel page in Main Bullpen / Admin Hub. Opening image: The review asks for one concise value statement. Middle image: Medium close on Mira in Main Bullpen / Admin Hub; expression readable and eyeline directed toward the others. Closing image: Medium close on Kreeb in Main Bullpen / Admin Hub; expression readable and eyeline directed toward the others.":
        "Primary composition: 6-panel page in Main Bullpen / Admin Hub. Opening image: The review asks for one concise value statement. Middle image: Mira lifts the sealed sample card from the secondary-observation stack as she gives her part of the answer. Closing image: Kreeb taps the intentional blank on the reporting form while Astra types the final line.",
        "PANEL 3 — Medium close on Zib in Main Bullpen / Admin Hub; expression readable and eyeline directed toward the others. ZIB: We keep the place working.":
        "PANEL 3 — Zib plants one hand on the stained work board beside the open-work-order column. ZIB: We keep the place working.",
        "PANEL 4 — Medium close on Mira in Main Bullpen / Admin Hub; expression readable and eyeline directed toward the others. MIRA: And we measure the strange part without pretending we understand it.":
        "PANEL 4 — Mira lifts the sealed sample card from the secondary-observation stack as she gives her part of the answer. MIRA: And we measure the strange part without pretending we understand it.",
        "PANEL 5 — Medium close on Glorp in Main Bullpen / Admin Hub; expression readable and eyeline directed toward the others. GLORP: With records.":
        "PANEL 5 — Glorp raises the clean reporting form beside the stained work board. GLORP: With records.",
        "PANEL 6 — Medium close on Kreeb in Main Bullpen / Admin Hub; expression readable and eyeline directed toward the others. KREEB: That do not require people to become records. Astra types.":
        "PANEL 6 — Kreeb taps the intentional blank on the reporting form while Astra types the final line. KREEB: That do not require people to become records.",
    },
}

for filename, replacements in REPLACEMENTS.items():
    path = SHOW / filename
    text = path.read_text(encoding="utf-8")
    for old, new in replacements.items():
        count = text.count(old)
        if count != 1:
            raise SystemExit(f"{filename}: expected one exact match, found {count}: {old}")
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")

# Final quality gate: the known generic dialogue staging must be gone from plain Stardust issues.
for path in sorted(SHOW.glob("pages_e*.json")):
    text = path.read_text(encoding="utf-8")
    assert "expression readable and eyeline directed toward the others" not in text, path
    assert "Medium close on the Operations Liaison on the live call, composed and attentive" not in text, path

# Remove temporary audit/rewrite machinery from the final production diff.
for path in [
    ROOT / ".github" / "workflows" / "stardust-generic-staging-audit.yml",
    ROOT / ".github" / "workflows" / "stardust-final-staging-polish.yml",
    Path(__file__).resolve(),
]:
    if path.exists():
        path.unlink()

print("Stardust dialogue-staging polish passed")
