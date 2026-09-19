# RexPrompt prompt-section suppression

RexPrompt supports optional suppression of non-core assembled-recipe content without deleting or rewriting source data.

## UI

The assembler shows **Suppress from assembled recipe** checkboxes for:

- Summary
- Production brief
- Setting
- Region
- Factions
- Characters
- Continuity
- Direction

Panel Plan and Dialogue are intentionally not suppressible because they are the core page-production instructions.

With all suppression options enabled, an assembled page contains only its page header, **Panel Plan**, and **Dialogue**.

Selections may be stored per series / issue / recipe in the current browser. Commit carries the active selection forward for the current browser tab. **Reset page** removes the browser override and returns the page to its stored default.

## Optional stored default

A page may optionally define:

```json
"promptSuppress": ["summary", "production", "factions", "region"]
```

Recognized values are `summary`, `production`, `setting`, `region`, `factions`, `characters`, `continuity`, and `direction`.

Pages without `promptSuppress` retain the historical assembled output unless a browser selection is active.

## Scope

Suppression changes assembled prompt output only. It does not delete summaries, production briefs, shelves, character data, settings, regions, continuity metadata, directions, panel plans, or dialogue.
