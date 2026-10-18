# Rex Fleet — authored page ingredient scope

RexPrompt assembles each Rex Fleet page from its authored story data and reference shelves. The per-page chef scope is stored in `data/shows/rex-fleet-s1/editorial/page_assembly_scope_iNN.json` for Issues 01–12.

## Contract

Each interior page has one merge-by-ID profile, applied **after** all story, dialogue, and page-layout overlays. The existing RexPrompt `promptSuppress` and `promptCharacterMode` fields control assembled output; these files do not invent a schema or a second recipe.

- `promptCharacterMode: "full"` keeps established visual and performance identity descriptions on selected anchor scenes.
- `promptCharacterMode: "cast"` keeps the explicitly present cast names and separate speaker handles but omits repeated full character biographies.
- `promptSuppress: ["settingContinuity"]` omits repeated shelf descriptions when the authored `settingText`, panel plan, and scene direction already establish the location. It does not suppress `[SETTING]`.
- `promptSuppress: ["region"]` omits repeated region tags on consecutive pages retaining a concrete setting and dramatic geographic context. Changes in region remain represented.
- `promptSuppress: ["factions"]` omits adjacent repeated faction shelf entries; their identities and roles remain in scene-specific story directions.
- An empty `promptSuppress` is an explicit decision to keep the page ingredients.

No production line, summary, unique scene direction, dialogue, authored panel plan, continuity reference, or page-layout instruction is suppressed. Do not flatten unique continuity warnings simply because they use negative language: when they constrain authority, agency, ship geometry, civilian risk, faction identity, or causality, they belong in the current scene.

Covers and editorial pages retain their complete prior assembled recipes. Released Issue 1 and previously approved production assets are not modified.

## Production boundary

This is a **recipe-assembly sanitation pass**, not an image, layout, or dialogue rewrite. The original page data and compressed issue payloads are untouched. If a particular page requires more or less visual context, edit that page's final scope overlay, not browser-local overrides or unrelated source shelves.

## Mechanical review

```sh
node tools/test_rex_fleet_recipe_scopes.cjs
node tools/test_page_layout.cjs
node tools/test_rex_fleet_issue04_density.cjs
node tools/test_rex_fleet_issue05_density.cjs
```

The scope test assembles every Rex Fleet interior, cover and editorial unit using the current browser assembler, comparing original versus scoped recipes. It confirms strict page coverage, approved existing suppression, intact story ingredients, unchanged artistic layout, unaltered special pages, and shorter prompt output. Follow it with visual editorial review of selected newly generated pages: shorter recipes are not themselves proof of better artwork.
