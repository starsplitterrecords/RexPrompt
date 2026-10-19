# Azure Reach — Phase C dialogue, balloon order, and density review

**Production scope:** Season One, Issues 2–6 (101 unapproved interior pages). Issue 1 and the nine approved Issue 2 draft pages are excluded. All issue lengths, character identities, art layouts, physical continuity and panel actions remain unchanged.

## Audit findings

The principal problem was not excessively long dialogue. Across the 101 eligible pages there were 588 brief dialogue/caption items (less than six per page on average). Dialogue was held separately from the panel plans with no explicit panel ownership, so the image generator had to infer balloon placement, speaker positions and reader path. The pressure points were conversations involving several people and double-width reveal panels whose visual quiet could be disrupted by poorly placed balloons.

## Editorial implementation

- `editorial/dialogue_c_e02.json` through `e06.json` are **dialogue-only overlays**. They load through the existing `dialogueOverlays` pipeline after all script, recipe-suppression and layout overlays. The original compressed source files are immutable.
- Every unapproved page has an authored `subtext: "Panel N"` for each existing dialogue/caption line, in the **original reading order**. This uses the current production assembler's existing field instead of introducing a new storage schema.
- Twelve selective voice and specificity revisions were made where dialogue sounded like a theme declaration, over-described the stakes, or asserted more about animal behavior than staff could justify. Dialogue elsewhere was retained, including joke timing, character friction and institutional/animal-care boundaries.
- One unnecessary final balloon, the sponsor's spoken "Congratulations" on `AZR_S1E06_P20`, was removed so the reef-school reveal remains silent and the final staff invitation has fewer competing speakers. Sponsor acknowledgment is visual and remains compatible with the existing scripted scene.
- No page was automatically split, extended, or re-panelled. No additional action, animal cue, staff access, props, or readable signage was invented.

## Specific editorial corrections

- `AZR_S1E03_P01`: Pip asks the concrete guest-expectation question instead of repeating the word "forty."
- `AZR_S1E03_P02`: Fleur's assessment of the tidepool light becomes concise, visual and character-specific.
- `AZR_S1E03_P13`: The sponsor's invitation request lands as a real visitor's desire.
- `AZR_S1E03_P17`: Elliot states the habitat-wide support arrangement plainly.
- `AZR_S1E04_P11`: Kyler's four-stream proposal is shorter without losing its overreach.
- `AZR_S1E05_P04`: Pip identifies the incorrect lines directly and takes immediate guest-service action.
- `AZR_S1E05_P11`: Nia responds with observable family behavior, not a general claim about metrics.
- `AZR_S1E05_P14`: Nia describes specific guests pulled away from animals toward stamp tables.
- `AZR_S1E05_P18`: Nia gives the sponsor a grounded observation about visitors in the jellyfish gallery.
- `AZR_S1E06_P03`: Nia identifies the real stroller clearance problem.
- `AZR_S1E06_P08`: Raf makes the distinction between available seating and forced sitting in his own voice.
- `AZR_S1E06_P17`: Julian directs the guest to Dora's observed expertise without claiming to know why a ray took a particular route.

## Production verification

`node tools/test_azure_dialogue_c.cjs` loads the canonical gzip/base64 scripts and production drafts, executes the **live** RexPrompt assembler, verifies exactly 101 eligible pages, checks all preserved speaker handles and character attribution, checks monotonically increasing panel placement, enforces 12 listed text edits and one explicit line removal, and confirms the assembled setting, layout, panels, continuity and direction sections remain identical.

Original published and approved pages receive **no** overlays. The separate original Azure mechanical validator's historical `AZR_S1E01_P03` `panelPlan`/`panelCount` mismatch is not modified by this pass.

## Visual follow-up

The mappings eliminate ambiguity in the written recipe, but they are not proof that every rendered balloon will fit. Check actual page renders at print and mobile sizes, especially multi-speaker panels (notably `AZR_S1E05_P17` and the last staff panel of `AZR_S1E06_P20`). If a layout remains unreadable, prioritize a local stage/composition revision and better visual quiet before expanding issue length or removing essential character dialogue.
