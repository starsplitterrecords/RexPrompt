# Comic issue mastering — operational release gate

## Purpose and authority

Mastering is a **complete-book production operation**, not just a statistical check. The complete-book manifest defines reading order. Approved draft images remain untouched until a distinct replacement passes the established visual, lettering, and approval process. Released StarSplitterVisions canon controls established identities; the exact assembled RexPrompt unit controls dialogue and story intent.

An issue is **not** mastered because a report or PDF was successfully generated.

## Required publication profile

`production/mastering/publication-profiles.json` contains a **working**, not printer-approved, U.S. comic trim target of 6.625 × 10.25 inches, 0.125-inch bleed, 0.25-inch safe inset, 300 DPI original pixel minimum, and a working sRGB IEC61966-2.1 review space. At 300 DPI, the full-bleed native canvas target is **2063 × 3150 pixels**. Do not claim that a 1024 × 1536 image has adequate printing detail simply by enlarging it. A correct aspect ratio does not establish adequate bleed content.

A publisher/printer must confirm actual trim, cover-wrap/spine, press ICC profile and proofing intent before changing profile status to `printer-approved`. The color profile must be preserved or converted with color management, not silently assigned. An image with no embedded ICC needs documented source-space interpretation. A digital-only release must use its own explicitly approved profile; it is not automatically a print master.

No global "normalize to median" grade is allowed. Intentional brightness, color, saturation and lighting differences between cover, editorial, space scenes, interiors, and story beats must be preserved. Statistics flag possible discrepancies only.

## Issue-by-issue production loop

1. Establish the complete-book manifest, verify page count, and resolve source provenance. Include **cover, editorial/open, cast, story, editorial/end matter, closing** as actually specified by the issue.
2. Select a registered series publication profile and confirm the physical output target. Do not use guessed printer requirements for final approval.
3. Run the native-resolution and integrity preflight, then the mastering session in exact reading order:

   `python tools/issue_mastering_session.py --series rex-fleet --issue rex-fleet-i01 --out /tmp/mastering/rex-fleet-i01 --native-tiles`

   `python tools/issue_mastering_session.py --series rex-fleet --issue rex-fleet-i02 --out /tmp/mastering/rex-fleet-i02 --native-tiles`

4. Inspect `contact-sheet.jpg` and `palette-diagnostic.png`; compare adjacent pages, settings and story time rather than indiscriminately equalizing color. Inspect 1:1 crops in `lettering-tiles/` when generated and the complete original page at native pixels.
5. Read `corrective-requirements.md` and classify machine findings as source-art deficiencies, missing input, or technical implementation faults. Identify **genuine re-render or recovery of higher-resolution originals**, not resizing or AI enlargement.
6. Compare the page against its exact assembled production recipe for *every* caption and spoken line: no missing/invented/duplicated text; correct speaker, punctuation, balloon order, tails, legibility at final size, and safe margins.
7. Visually check established faces, clothing, vehicles, locations, props, linework, page rhythm and causal transitions against released canon and adjacent approved pages. Make a deliberate `gradeIntent` finding; mark intentional changes `approved-unchanged`, not erroneous.
8. For a deliberate page-level color correction, use an explicit JSON look proposal and the color-managed proof tool:

   `python tools/render_mastering_grade_proof.py --source <original.png> --grade <proposal.json> --out /tmp/review/<page>.png`

   Embedded ICC profiles are converted to sRGB. Untagged input is blocked without a documented `--untagged-srgb-evidence` statement. The PNG and side-by-side JPG are **proposals only**, never automatic master replacements or print proofs. Assess whether linework, skin color, atmosphere and lettering survive.
9. Fix the smallest failing unit, normally lettering first, then local repair or panel correction, reserving full native-resolution regeneration for genuinely insufficient or unrecoverable source detail. Preserve all approved originals until replacements are separately reviewed. Re-run the *entire issue* after substitutions because one replacement can alter transitions and palette.
10. Complete `mastering-session.json` page checks and issue-wide checks with reviewer identities and actual visual evidence; record the chosen master source SHA for every page. Source machine deficiencies must be resolved, not merely checked off.
11. Establish the real printer, press ICC file/checksum, approved geometry and a final color-managed proof. Update the publication profile to `printer-approved` only on evidence. Sign the issue record explicitly.
12. Run `python tools/verify_mastering_approval.py --record /path/to/mastering-session.json`. **A passing structural/evidence gate does not replace pixel or editorial inspection.** Release tooling remains separate and must use the selected approved art and complete-book manifest.

## Evidence record

`mastering-session.json` carries per-page source hashes, dimensions, DPI, machine deficiencies, corrective requirements, color-intent decisions, ten page review gates, eight full-book review gates, printer ICC provenance and final approval signature. The session starts `not-approved`; no tool grants this automatically.

The accompanying Markdown is a **per-page corrective production brief** suitable for the separate IMG production chats. It explicitly identifies whether native-resolution re-rendering or recovery is required.

## CI and extensions

`Validate Complete Issue Mastering Process` runs Rex Fleet Issue 1 and Issue 2 complete inventories and tests grading against synthetic ICC-tagged and untagged images. It asserts that missing evidence **fails** final approval. Artifacts include each issue's correction brief, mastering record, color diagnostic and contact sheet, with individual source pixels available through GitHub readback.

The series mapping currently covers Rex Fleet, Vikings 2026 and Stardust Station. For other series, use `--profile standard-us-comic-print-v1` **only** if the proposed trim is the correct documented output; otherwise add an explicit series-specific publication profile. Do not publish a complete-book claim before the actual issue manifest exists and is reviewed.

## Never confuse these states

- **Production approved draft:** permission to use that original as current production reference; not proof of print suitability.
- **Inspection report:** machine metrics with unreviewed visual and typography gates.
- **Proposed graded proof:** reversible color study; not canon or an approved master.
- **Mastering approved:** a completed and verified signed production record, all genuine native sources and press specs present, all per-page and issue-wide checks passed.
- **Released canon:** the approved package separately published and verified at StarSplitterVisions.

The end state must be a book whose deficiencies are invisible to a reader, not merely a green automated audit.
