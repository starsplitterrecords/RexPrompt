# Division Threshold — Issue 1 Production Readiness Audit
Date: 2026-09-18
Status: current production audit; not new creative canon

## Authority reviewed

- Current Division Threshold Notion source-of-truth and clarification pages.
- Current RexPrompt assembler contract in `index.html`.
- `data/shows.json` and `data/shows/division-threshold-s1/assembler.json`.
- Effective Issue 1 recipe sequence after scene and dialogue overlays.
- Current Division Threshold character, setting, region, and faction shelves.
- Current Division Threshold visual-reference pack and approved-draft manifest.
- Current StarSplitterVisions Division Threshold catalog entry.

## Mechanical result

Issue 1 currently resolves to exactly 26 ordered page recipes, `DT_E001_P01` through `DT_E001_P26`.

All effective production references resolve:
- character IDs: pass
- setting IDs: pass
- region IDs: pass
- faction IDs: pass
- dialogue character handles: pass
- continuity targets: pass

The assembler emits page summary, generation line, applicable setting/region/faction/character context, panel plan, exact dialogue, continuity instruction when present, and page-specific direction.

## Repair completed

Three `continuityFrom` values were being used as narrative-thread links even though the assembler interprets the field as direct visual continuation and explicitly tells production to preserve positions, props, damage, eyelines, and emotional state.

The invalid direct-continuity links were cleared:
- `DT_E001_P16` no longer continues directly from P11; the story moves from the Augment clinic to the overpass.
- `DT_E001_P20` no longer continues directly from P16; the thread returns from the overpass to the clinic.
- `DT_E001_P26` no longer continues directly from P25; the issue cuts from Kellen in Oversight to Axiom in the Data Core.

Thread-continuity links that preserve the same cast/location/state were retained.

## Editorial read

The effective P05–P26 sequence is causally coherent:
- Ostra's unauthorized rescue makes agency politically legible.
- Kellen discovers attribution has replaced investigation.
- John and Nathan independently identify engineered failure.
- Nico identifies physical evidence while repairing Ostra.
- Axiom finds that independent judgment predicts outcomes better than assigned-purpose classification.
- The separate investigations converge on a scheduled Concourse 17 observation window without prematurely forming a unified team.
- Issue 1 ends before the next event occurs, preserving the intended Issue 2 handoff.

The production reconciliation already removes provisional supporting-character identity from generation:
- P10 uses an unnamed Oversight director.
- P14 uses an unnamed private-security intermediary.
- Neither supporting role is included as a persistent character record in the effective page cast.

## Remaining creative blocker

Current Notion clarification authority states that **Season One opens with Ostra-9 at Checkpoint 9 and the engineered overpass failure**.

The compiled Issue 1 still opens with four historical prologue pages:
1. biomechanical repair
2. early Organosynthetic hazard work
3. early machine-Intelligence question
4. modern Stack reveal

Those two states cannot both define the literal opening order.

This audit does **not** silently delete, relocate, or rewrite the prologue. Its disposition is an editorial choice, not a mechanical correction.

Until that choice is resolved, sequential image production should not begin at P01 because the canonical first-page order is not actually settled.

## Visual-reference state

The curated reference pack is structurally complete for the six principal characters:
- Ostra-9
- Axiom / AX10M
- Nico-14
- John Mercer
- Nathan Price
- Kellen Cartwright

It also contains one approved page-language/Stack-atmosphere reference mapped to `DT_E001_P05`.

All referenced asset files exist in the repository.

There are no Division Threshold entries in `production/drafts/manifest.json`. The recovered P05 production example is a scoped visual reference; it does not advance the durable sequential production frontier.

Most recurring Issue 1 locations beyond Checkpoint 9/The Stack currently rely on assembler-visible textual setting and region definitions until approved page art establishes a stronger visual baseline.

## Visions state

StarSplitterVisions now contains `sites/visions/src/content/series/division-threshold.json` and lists the series in More Worlds.

That entry is a **coming-soon / in-production catalog entry**, not a story release:
- no cover
- no reader pages
- no release record
- no collected issue PDF

The catalog copy has been aligned to the current political-thriller, legal-personhood, bodily-autonomy, and coalition framing.

Because the Visions slug now exists, the previous RexPrompt source-mapping mismatch is resolved. The catalog entry still does not constitute released visual canon.

## Safe next production transition

Resolve the opening-structure decision first.

After that:
- if the four-page prologue remains first, the sequential frontier is `DT_E001_P01`;
- if the prologue moves or is removed, recompile/renumber the issue before image production so the durable recipe order and production frontier agree.

No other Issue 1 mechanical or assembler blocker was found in this pass.
