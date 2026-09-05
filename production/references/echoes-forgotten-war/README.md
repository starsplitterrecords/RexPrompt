# Echoes of a Forgotten War — Production Visual Baseline

Echoes is currently unreleased. Current StarSplitterVisions `main` contains no released Echoes pages, covers, or issue assets, so there is no released visual canon yet.

## Current authority

Until released canon exists, use this order for image production:

1. Exact assembled RexPrompt recipe for the selected production page.
2. Explicitly approved durable Echoes image references stored in this repository.
3. Approved production drafts stored against the exact recipe ID.
4. Assembler-visible visual anchors and continuity locks in `data/shows/echoes-forgotten-war-s1/characters.json`.
5. Relevant setting and region production language in the Echoes package.
6. Immediate continuity from the previous approved page when applicable.

A previous generated page is never the sole character or world reference.

## Not visual authority

Do not use any of the following as continuity references unless the user explicitly approves and stores them as such:

- failed, rejected, repeated, superseded, or abandoned generations
- unlabeled prior-chat images whose approval status cannot be established
- promotional lineups or labeled character graphics
- contact sheets, montages, covers, title pages, credits, editorial pages, or production annotations
- the 22-beat development map in `comic_page_spine_v1.json` as an image-production cursor
- remembered visual descriptions when durable production data is available

## Durable approval rule

When an Echoes page passes reader test, recipe fidelity, character/world continuity, composition, and lettering review, store the approved image as a recipe-level approved production draft under `production/drafts/` and register it in `production/drafts/manifest.json`.

A standalone approved corrective or character/world reference should be stored under this reference directory with its scope stated clearly.

Until an actual approved Echoes image is stored durably, the series is in a clean visual-start state: text anchors define identity constraints, but no prior generated artwork is presumed canonical.
