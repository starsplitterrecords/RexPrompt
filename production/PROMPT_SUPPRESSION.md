# RexPrompt prompt-section suppression

RexPrompt supports optional page-level suppression of non-core assembled-recipe sections without requiring any series data migration.

## UI

The assembler shows **Suppress from assembled recipe** checkboxes for:

- Setting
- Region
- Factions
- Characters
- Continuity
- Direction

Unchecked sections assemble exactly as before. Checkbox choices are saved per series / issue / recipe in the current browser.

**Reset page** removes the browser override and returns the page to its stored default.

Panel Plan and Dialogue are intentionally not suppressible because they are core production instructions.

## Optional stored default

A page may optionally define:

```json
"promptSuppress": ["factions", "region"]
```

Recognized values are `setting`, `region`, `factions`, `characters`, `continuity`, and `direction`.

No existing page needs this field. Pages without it retain the historical assembler output.

A browser checkbox choice overrides the stored default for that page; Reset page restores the stored default.

## Scope

Suppression changes only assembled prompt output. It does not delete or rewrite source data, faction shelves, character shelves, settings, regions, continuity metadata, or dialogue.
