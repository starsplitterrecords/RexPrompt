# Low Tide Signal image-production baseline

This directory records the durable visual-authority rules for Low Tide Signal image production.

## Released preview state

StarSplitterVisions currently publishes a **Preview**, not a released interior issue. The current public preview asset is:

- `/images/covers/low-tide-signal-issue-01-cover.png`

That asset is a published preview/cover artifact. It is **not an interior production reference** and must not be used to establish recurring character faces, body models, wardrobe, interior page layout, panel language, or story geography.

Do **not** use its typography, title treatment, trade dress, labels, framing, cover composition, or depicted figures as authority for sequential page generation.

There are currently no released Low Tide interior pages in StarSplitterVisions, so there is no released page-layout baseline and no released page-to-recipe mapping to infer.


## Active recipe contract

Current story production uses page-level `LTS_CNN_PNN` recipes, wrapped by explicit editorial framing recipes.

- Chapter 1: `LTS_C01_EDITOR_OPEN` + 24 story pages + `LTS_C01_EDITOR_NEXT`
- Chapter 2: `LTS_C02_EDITOR_OPEN` + 26 story pages + `LTS_C02_EDITOR_NEXT`
- Chapter 3: `LTS_C03_EDITOR_OPEN` + 28 story pages + `LTS_C03_EDITOR_NEXT`
- Chapter 4: `LTS_C04_EDITOR_OPEN` + 26 story pages + `LTS_C04_EDITOR_NEXT`
- Chapter 5: `LTS_C05_EDITOR_OPEN` + 24 story pages + `LTS_C05_EDITOR_NEXT`
- Chapter 6: `LTS_C06_EDITOR_OPEN` + 24 story pages + `LTS_C06_EDITOR_NEXT`
- Chapter 7: `LTS_C07_EDITOR_OPEN` + 26 story pages + `LTS_C07_EDITOR_CLOSE`

The 178 story-page recipes remain unchanged. Editorial framing lives in separate opener/closer overlays so story payloads and story IDs are not renumbered. The retired scene-level Chapter 1 recovery structure is not an active production contract and must not be mixed with current page IDs. No approved Low Tide production image is currently persisted in the draft manifest.

## Character visual state

The six core characters have assembler-visible textual design baselines in `data/shows/low-tide-signal/characters.json`, but no approved character image reference is currently stored in RexPrompt.

The new editorial framing pages deliberately use environments and objects rather than identifiable core-character faces. They may be produced before recurring-character identity references are approved, but they do not satisfy or bypass the identity gate for the first character-bearing story page.

Before sequential production advances into character-bearing pages, establish and approve visual identity references for:

- Matt Donnelly
- Ryan Kelleher
- Chris Barlow
- Justin Rourke
- Nicole Hanley
- Kevin Marsh

Once approved, use those images as identity authority for faces, apparent ages, body models, hair, proportions, and stable wardrobe language. Text descriptions remain supplementary.

## Environment baseline

Use the current Low Tide production data and approved creative source for the established contrast:

- **Inland Harbor Phase:** safe, optimized, gray-blue, glassy, softly lit, automated, comfortable, emotionally flat.
- **Threshold / Floodwall:** wet asphalt, cold mist, vehicle headlights, contractor work lights, dark concrete.
- **The Flats:** black tidal mud, old pavement, channels, broken pilings, shell debris, fog, returning water.
- **The Reach:** fixed physical abandoned offshore districts; wet concrete, rust orange, black water, deep cyan, faded institutional green; beautiful because real, never supernatural.

Practical light only: headlamps, cheap LEDs, phone lights, contractor work lights, battery flood bars, emergency strobes, scanner screens, distant infrastructure glow, vehicle headlights.

No lanterns. No supernatural effects. No generic cyberpunk neon. No apocalypse-brown filler. No superhero posing.

## Interior page-language rule

Normal story pages are prestige indie sequential comic pages, not infographics, dossiers, promotional cards, title pages, or labeled character sheets unless the exact RexPrompt recipe explicitly calls for one. The `EDITOR_OPEN`, `EDITOR_NEXT`, and `EDITOR_CLOSE` recipes are the explicit editorial-framing exception: they are art-directed environment-led pages whose scripted display text and editor copy are intentional issue content.

Do not add:

- page headers
- scene labels
- character-name labels
- issue/chapter labels
- production metadata
- decorative cover trade dress

Letter only the captions, dialogue, signs, interface text, and SFX required by the assembled recipe.

## Reference hygiene

Do not use rejected generations, repeated failed attempts, superseded designs, promotional labels, development diagrams, preview-cover figures, or unapproved concept art as continuity authority.

For every generation, use the mandatory production gate:

1. exact assembled RexPrompt recipe
2. relevant approved character/environment references
3. approved current-production continuity when it exists
4. immediate prior successful page only for state that genuinely carries forward

The previous generated page is never the sole visual authority.

## Durable production state

Approved sequential pages belong in `production/drafts/manifest.json` under their exact `<seriesId>::<issueId>::<recipeId>` key. Failed or merely generated attempts do not advance production.

Do not store a cursor. The production frontier is always derived from released canon + approved current-production drafts + ordered RexPrompt recipes.

## Cover production

Low Tide Signal now has dedicated chef-facing cover recipes in `data/shows/low-tide-signal/covers.json`:

- `LTS_C01_COVER` — The Flats
- `LTS_C02_COVER` — The Dead Mall
- `LTS_C03_COVER` — No Signal
- `LTS_C04_COVER` — Between Runs
- `LTS_C05_COVER` — Return Tide
- `LTS_C06_COVER` — After the Water
- `LTS_C07_COVER` — The Last Low Tide

Each is registered as a separate cover production unit in `data/shows.json`. The existing assembler is unchanged; the cover recipes use assembler-visible summary, setting/region, character, panel-plan, dialogue and direction fields.

### Cover trade-dress pixel authority

For every Low Tide Signal cover, retrieve and inspect the actual pixels of the published Issue 1 preview cover:

- repository: `starsplitterrecords/StarSplitterVisions`
- branch: `main`
- path: `sites/visions/public/images/covers/low-tide-signal-issue-01-cover.png`

This asset is now authoritative **only** for cover masthead/logotype, title hierarchy, issue/chapter label behavior, recurring brand marks and cover-line trade dress.

It remains explicitly **non-authoritative** for recurring-character identity, interior page layout, interior lettering, story geography, or issue-specific cover composition. The active `LTS_CNN_COVER` recipe controls the selling image for that chapter. Preview-cover figures must never be substituted for approved character identity references.

The full cover authority and generation gate is recorded in `production/references/low-tide-signal/cover-production-normalization.json`.

