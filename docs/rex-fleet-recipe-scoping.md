# Rex Fleet — authored page ingredient scope

RexPrompt assembles each Rex Fleet page from its authored story data and reference shelves. The per-page chef scope is stored directly on canonical page records in `data/shows/rex-fleet-s1` for Issues 01–12.

## Contract

Each interior page carries its own `promptSuppress` and `promptCharacterMode` fields in the authoritative page source. There is no post-assembly profile or second version of a page.

- `promptCharacterMode: "full"` keeps established visual and performance identity descriptions on selected anchor scenes.
- `promptCharacterMode: "cast"` keeps the explicitly present cast names and separate speaker handles but omits repeated full character biographies.
- `promptSuppress: ["settingContinuity"]` omits repeated shelf descriptions when the authored `settingText`, panel plan, and scene direction already establish the location. It does not suppress `[SETTING]`.
- `promptSuppress: ["region"]` omits repeated region tags on consecutive pages retaining a concrete setting and dramatic geographic context. Changes in region remain represented.
- `promptSuppress: ["factions"]` omits adjacent repeated faction shelf entries; their identities and roles remain in scene-specific story directions.
- An empty `promptSuppress` is an explicit decision to keep the page ingredients.

No production line, summary, unique scene direction, dialogue, authored panel plan, continuity reference, or page-layout instruction is suppressed. Do not flatten unique continuity warnings simply because they use negative language: when they constrain authority, agency, ship geometry, civilian risk, faction identity, or causality, they belong in the current scene.

Covers and editorial pages retain their complete prior assembled recipes. Released Issue 1 and previously approved production assets are not modified.

## Production boundary

This is a **recipe-assembly sanitation pass**, not an image, layout, or dialogue rewrite. The current page data and compressed issue payloads are authoritative. If a particular page requires more or less visual context, edit its canonical production record, not an overlay or browser-local override.

## Mechanical review

```sh
node tools/test_rex_fleet_recipe_scopes.cjs
node tools/test_page_layout.cjs
node tools/test_rex_fleet_issue04_density.cjs
node tools/test_rex_fleet_issue05_density.cjs
```

The scope test assembles every Rex Fleet interior, cover and editorial unit using the current browser assembler. It checks page coverage, the stored suppression rules, intact story ingredients, unchanged artistic layouts, and unaltered special pages. Follow it with visual editorial review of selected newly generated pages: shorter recipes are not themselves proof of better artwork.
