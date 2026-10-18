# Chef recipe sanitation and page-scoped suppression

RexPrompt stores complete production data but sends **only scene-relevant information** to the image-generation chef. Sanitizing a recipe must not delete, rewrite, or silently reorder an authored action, dialogue line, setting transition, unique prop, continuity requirement, or artistic page-composition decision.

## Separate the three concerns

1. **Story data** remains complete: `panelPlan`, `dialogueInline`, `directionInline`, stable IDs and speaker ownership, layout data, and status/provenance.
2. **Stored page policies** determine what to omit or compact. `promptSuppress`, `promptCharacterMode`, `promptSettingMode`, and `promptPanelMode` are authored data. Browser-local suppressions are not canonical.
3. **Assembler delivery** formats only the information selected for the chef. It never assumes that every raw JSON field must be literally included in the prompt.

## Panel serialization (new optional capability)

`"promptPanelMode": "clean"` produces a legible `[PANEL PLAN]` rather than serialized JSON:

- `Panel 1 — Location: ...: <exact action>`; subsequent panels state a location only when it is **new within that page**.
- Non-default shot types, including full-page splashes, remain explicit.
- `dialogueIndices`, internal field names, JSON quotes/braces, and identical locations on every panel are *not* sent as literal JSON.
- The dialogue section still contains **every complete authored line**, with its actual panel number and owner. No text or ownership is inferred from visual layout.
- The serializer validates ordered numbered panels, the exact `dialogueIndices` mapping, and any `Panel N` in the original dialogue subtext. Unknown panel fields or invalid mappings cause an assembly error rather than dropping data.
- `promptPanelMode` accepts `original` (default, absolutely unchanged) or `clean`; it can live on an individual page or in a show config after that show has been independently audited.
- `clean` is deliberately incompatible with `promptPanelLetteringMode: indexed`, which solves a separate problem with inline repeated dialogue in panel text. Audit and design a combined representation before enabling both.
- No global migration is inferred from this one-series pilot. Different series have different panel schemas, and unsupported pages retain the original delivery.

The `[PAGE COMPOSITION]` section, when present, remains separate and intact. Panel size, dominance, insets, negative space, and lettering reserves are not reinterpreted by sanitation.

## Vikings 2026 Issue 2 (completed first rollout)

The show loads these data layers in order:

1. `pages_i02.json` — original complete story, approved drafts, page identities, actions, locations, dialogue, direction, and authored layout.
2. `editorial/dialogue_density_i02.json` — approved issue-specific writing/density revisions on ten unapproved pages.
3. `editorial/chef_recipe_sanitation_i02.json` — last, strictly ID-merged production delivery policy.

Pages **P02–P04 remain byte-for-byte unchanged in assembled output**, preserving their approved production recipes. Pages **P05–P23** opt into clean panel delivery; none add or remove a story panel.

Repeated `LANDFALL VISUAL STATE` apartment-wide notes have been further suppressed on P11 and P17–P19, because their actions already depict the first-night cooking, worn room, repairs and pipe hazard. The setting remains visually anchored on the approved introduction and key return/closing pages (including P08 and P22). On P16 the repeated note is excluded but the **unique, ordinary scratched brass-key reference remains**. On P07 the authored page-layout metadata was synchronized with the corrected silver refusal in panel 3 and the card payment in panel 4; the story and page composition structure remain unchanged.

This is **representation-level cleanup**, not another dialogue, page-count, or visual-design rewrite. Complete unsanitized source remains available for editing, provenance, QA and future reference.

## Regression gate

Run `node tools/test_vikings_i02_chef_sanitation.cjs`. It executes the current inline browser assembler and verifies **all 22 pages**; the original scripted panel plan and dialogue are compared directly with the effective recipe. It also checks:

- No loss of unique panel action, location or character-owned dialogue.
- Original dialogue text/order/ownership, continuity and current artistic layout survive intact.
- The three approved recipes remain byte-identical.
- The P16 brass key exception and P07 transaction order are respected.
- Invalid panel numbering, duplicate/missing dialogue mapping, invented panel fields, and contradicting `Panel N` metadata fail closed.
- The net reduction in repeated delivery scaffolding is material, without enforcing an arbitrary target length.

The regular page-assembly workflow runs this alongside the existing Stardust, Rex Fleet, Low Tide, Azure Reach and other series tests. Further rollout to any of those series must be separately audited against their own current source schema and visual canon, not toggled globally.

## What this does *not* solve

A clean recipe cannot make an inherently overfull dramatic beat or impossible balloon count into good sequential art. Run the lettering-density warnings and an actual visual proof to distinguish a chef-information problem from script density or image-generation limitations. Do not auto-expand a 22-page issue into 44 pages.
