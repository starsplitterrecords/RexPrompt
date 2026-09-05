# Low Tide Signal image-production baseline

This directory records the durable visual-authority rules for Low Tide Signal image production.

## Released baseline

StarSplitterVisions currently publishes a **Preview**, not a released interior issue. The current public preview asset is:

- `/images/covers/low-tide-signal-issue-01-cover.png`

Treat that released cover as **series atmosphere / world-tone reference only** unless a later approved decision explicitly gives it narrower character authority.

Do **not** use cover typography, title treatment, trade dress, labels, framing, or cover composition as interior-page design authority.

There are currently no released Low Tide interior pages in StarSplitterVisions, so there is no released page-layout baseline and no released page-to-recipe mapping to infer.

## Character visual state

The six core characters have assembler-visible textual design baselines in `data/shows/low-tide-signal/characters.json`, but no approved character image reference is currently stored in RexPrompt.

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

Interior pages are prestige indie sequential comic pages, not infographics, dossiers, promotional cards, title pages, or labeled character sheets unless the exact RexPrompt recipe explicitly calls for one.

Do not add:

- page headers
- scene labels
- character-name labels
- issue/chapter labels
- production metadata
- decorative cover trade dress

Letter only the captions, dialogue, signs, interface text, and SFX required by the assembled recipe.

## Reference hygiene

Do not use rejected generations, repeated failed attempts, superseded designs, promotional labels, development diagrams, or unapproved concept art as continuity authority.

For every generation, use the mandatory production gate:

1. exact assembled RexPrompt recipe
2. relevant approved character/environment references
3. approved current-production continuity when it exists
4. immediate prior successful page only for state that genuinely carries forward

The previous generated page is never the sole visual authority.

## Durable production state

Approved sequential pages belong in `production/drafts/manifest.json` under their exact `<seriesId>::<issueId>::<recipeId>` key. Failed or merely generated attempts do not advance production.

Do not store a cursor. The production frontier is always derived from released canon + approved current-production drafts + ordered RexPrompt recipes.
