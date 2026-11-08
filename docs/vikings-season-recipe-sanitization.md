# Vikings 2026 — Season 1 Chef-Recipe Sanitation Audit

This is the Vikings-only follow-through to [the Issue 2 sanitation contract](chef-recipe-sanitation.md). No other series was migrated. The current `data/shows.json` issue records—not the several historical alternative script shelves—are the authoritative production inventory.

## Season-wide disposition

| Registered show | Interior pages | Decision |
| --- | ---: | --- |
| Issue 1 — Arrival in Time | 18 | **Protected, unchanged.** Released/approved pages retain their exact recipes. |
| Issue 2 — Landfall Bushwick | 22 | **Normalized.** All ten dialogue revisions and nineteen sanitation policies now live in the authoritative pages; legacy overlay registrations removed after Item 1 chef-delivery fixes. Approved production preserved. |
| Issue 3 — Territory | 20 | **20 structured pages with clean chef delivery now stored directly** in `pages_i03_territory.json`. No source panels, dialogues, or creative directions modified. |
| Issues 4–12 | 225 | **225 authored prose-panel pages use normalized page-level delivery controls** directly in their Issue 4–12 source files, without active sanitizer overlays. Special covers, openings, and other editorial units retain legacy delivery. |
| Issue 6 Page 23 | Included above | **Dialogue grouping exception** is now recorded directly on Issue 6 P23; panel-4 dialogue appears before panel-3 dialogue in existing authored order. Preserve it verbatim and flag for later writing QA. |

## What is and is not suppressed

- Structured Issue 3 panels are validated and delivered as readable numbered action instructions. The original numbered panel IDs, distinct locations and shot types are preserved; machine `dialogueIndices` and repeated in-page locations are withheld from the chef, not deleted from the source.
- Issues 4–12 already store natural-language panel directions. Their audited pages now get **short numeric panel markers** (`1. …`, `2. …`) that correspond with their caption/balloon assignments. Consecutive dialogue lines are grouped under a single `Panel N:` label instead of repeating that label for every line. No line wording or speaker attribution is rewritten; original line order is never rearranged.
- The current issue authors already made scene-specific setting descriptions and meaningful directions. They are short or story-critical; this pass **does not blanket-suppress settings, factual stage directions, character references, prop provenance, continuity, or layout**. A repeated location name is not enough to justify deleting the only positive place/time anchor.
- Existing `promptVisibleCastOnly` and routine-faction suppression apply across the registered Vikings shows. Keep the current reviewed identities and any issue-level visual presence constraints; do not infer unseen characters just from dialogue.
- **No released/approved Issue 1 or Issue 2 recipe content is rewritten.** Issue 2 retains 19 audited clean pages and its existing approval-protected outputs, now without active supplemental overlays.
- No issues are split or expanded. Authoritative historical and alternative story shelves remain untouched.

## Exceptions requiring subsequent editorial review

- **VIK_S1E06_P23**: the original source lists spoken lines against panel 4, then panel 3, then panel 4 again before panel 5. This is likely a lettering/sequencing editorial question, *not* grounds for a sanitation algorithm to reorder characters' words. The page keeps its original per-line panel labels; panel descriptions are still numbered for clarity.

## Validation

Run `node tools/test_vikings_season_recipe_sanitation.cjs`, alongside the existing Issue 2 and production tests. The test rejects show-wide prose defaults and checks each existing page-level delivery setting directly in the normalized authoritative source. Issue 2 has a separate check for the normalized source. The regression loads the **live inline browser assembler**, all **285 registered season interior pages**, issue overlays, and the original source. It verifies exact action prose, every dialogue line, scene setting, character and faction handling, story order, continuity and page layout; validates the special exception; checks source panel counts; and confirms no changes on the previously approved issues.

The original chef-delivery size reduction at implementation was **13,280 characters across 285 interior pages**, concentrated in Issue 3's structured panels; the prose issues were already comparatively clean. A smaller prompt is not automatically a better page, and actual generated art still requires visual/lettering review.

New shows or schema variants should be audited before using either mode; there is intentionally no global default for all RexPrompt productions.
