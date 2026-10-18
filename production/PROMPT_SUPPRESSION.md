# RexPrompt prompt suppression and recipe sanitation

RexPrompt preserves complete scripted story data in its source shelves. The assembled chef recipe carries only page-relevant supporting references and production direction. The live assembler in `index.html` controls which fields are actually emitted.

## Stored per-page policy

The read-only `prompt-suppress.js` view displays decisions stored in recipe data. There are no live checkboxes, browser-local overrides, or next-page suppression carryovers.

- `promptSuppress`: any of `summary`, `production`, `setting`, `settingContinuity`, `region`, `factions`, `characters`, `direction`.
- `promptCharacterMode`: `full`, `cast`, or `none`. The `characters` suppression value also forces `none`.
- `promptSettingMode`: `full` or `label`, for shelf-backed recurring settings.
- `pageLayout`: protected artistic hierarchy; not suppressible.

**Never suppress panel plans, dialogue, continuityFrom, or page composition.** Old instructions that described continuity checkboxes are obsolete and must not be followed.

Setting suppression is rejected unless every panel has an explicit nonblank location; use the `label` mode for an established setting. Never strip essential geography, character introductions, action, or unique state changes merely to reduce prompt length.

## Editorial rules

Read each issue in sequence. Give the chef full character/location references when they are being introduced, and shorter references when continuity is already established. Suppress formulaic summaries only when their content is entirely carried by the panel plan; preserve dramatic summaries that add unique motivation or necessary subtext. Do not suppress an entire direction section when it mixes unique state with repeated generic production boilerplate. Sanitize just the boilerplate in source data.

## Implemented production rollout

| Package | Data-level decision |
| --- | --- |
| Vikings 2026 Issue 2 | Existing targeted apartment direction suppression and compact cast handling, preserving scene geography and lettering |
| Stardust Issue 2 | Earlier 22-page strict scope overlay |
| Stardust Issues 4–10 | Seven strict page-scoping overlays: suppress 153 formulaic summaries, compact established cast, label immediately repeated shelf locations while retaining new character introductions |
| Echoes Issues 1–8 | Eight separate strict recipe-scope overlays: compact established cast after issue introductions; retain all original page layouts and story data |
| Echoes direct sanitation | Remove 131 repeated generic production direction blocks while preserving unique directives, the season's 149 page recipes, and all 690 lettering items |

Echoes `pageLayout` overlays and `page_recipe_scope` overlays are deliberately separate. Additional franchises are not automatically granted blanket suppression: their active recipe structures and visual-reference requirements require an independent audit.

## Validation

Run `node tools/test_prompt_assembly.cjs`, `node tools/test_editorial_page_scopes.cjs`, `node tools/test_recipe_sanitation_rollout.cjs`, `node tools/test_echoes_page_layout.cjs`, and `python tools/validate_echoes.py`. These tests assert identical scripted panel plans, dialogue, and downstream continuity in actual assembled recipes before/after scoping. Mechanical recipe validation does not mean regenerated artwork has passed visual-quality review.
