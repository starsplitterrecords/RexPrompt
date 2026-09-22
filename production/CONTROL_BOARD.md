# Visions Production Control Board

Snapshot: 2026-09-18

This file is an operational snapshot, not a new creative authority.

## Authority

- **Released canon:** `starsplitterrecords/StarSplitterVisions` `main`
- **Current production recipes and writing packages:** `starsplitterrecords/RexPrompt` `main`
- **Approved unpublished production images:** `production/drafts/manifest.json`
- **Curated visual references:** `production/references/` and `production/visual-sources.json`

State terms:

- **Released** means canonical material exists in StarSplitterVisions.
- **Compiled** means RexPrompt can load the material as a current production package.
- **Scripted** means developed writing exists but still requires production review and/or RexPrompt compilation.
- **Approved draft** means an unpublished image is durably registered in `production/drafts/manifest.json`.

## Series board

| Series | Released state | RexPrompt / writing state | Durable approved drafts | Current blocker / next non-image action |
|---|---|---|---|---|
| **Azure Reach** | Issue 1 released: 22 reader pages + collected PDF. | Season 1 Issues 1–6 are production-ready 22-page scripts. | Issue 2 has 9 noncontiguous approved drafts: P01–P08 and P11. | Reconcile the noncontiguous Issue 2 durable draft state before treating production as continuous. Determine whether P09–P10 and P12–P22 have approved source images to recover or are genuinely unproduced. |
| **Backyard Rockets** | Issues 1–2 released as the approved 48-page combined edition. The publishing commit intentionally synchronized that collected edition with 47 reader-page assets, so the reader count is not treated as missing release content. | Issues 3–8 have been read sequentially, developmentally reviewed, sanitized and recompiled in the existing encoded production format. Issues 3–6 were preserved except for one Issue 3 panel-fidelity repair; Issues 7–8 received targeted mission/continuity repairs around Sky-Piercer. | None. | Writing/production package is ready for sequential image production from `BR_S1E03_PS_A01_SC01`. |
| **Low Tide Signal** | Preview only; no released story pages. | Chapters 1–7 are registered as one active P-page contract: 24 / 26 / 28 / 26 / 24 / 24 / 26 pages (178 total). Chapters 4–7 remain encoded enhanced packages. The obsolete eight-page Chapter 1 S-recipe recovery structure has been removed from the active tree. | None. | Recovery reconciliation and the full 178-page developmental read are complete. The sequence is coherent through Chapter 7; the one concrete production inconsistency found in the read (C07 P18 staging named Matt while cast/dialogue required Chris) was corrected. The September recovery attempt never persisted matching approved image binaries, so it does not advance the durable frontier. The dedicated place-naming pass is complete. `the Reach` is retired from visible Low Tide usage. Canonical layers are municipal **Harbor Phase East / Sector 14**, developer **Promise District**, runner slang **Tide Town**, public/media **Low Tide District**, and post-accident **the District**; the final chapter deliberately reduces umbrella naming. The remaining image-preproduction gate is durable visual identity references for the six core characters. |
| **Rex Fleet** | Issue 1 released: 19 reader pages (18 story pages plus editorial material) + collected PDF. | Issues 2–12 are compiled/registered. Issue 2 has 19 pages; Issue 3 has 30; Issues 4–12 are encoded production packages. | None. | No writing-recovery blocker established. Durable unpublished production state is empty, so the repository frontier is Issue 2 Page 1 unless prior approved work is deliberately recovered and registered. |
| **Stardust Station** | Issue 1 released: 22 reader pages + collected PDF. | Issues 2–10 are registered. Issues 2–3 are enhanced, sanitized encoded 22-page packages. Issues 4–10 are finished drama-first 22-page packages; season-level developmental review completed 2026-09-18, and Issues 8–10 production structure was recovered so exact dialogue/lettering is separated from panel staging. | None. | No non-image writing blocker found. Production can proceed from Issue 2 Page 1, subject to the normal visual-reference and approval gates. |
| **Sunforge Outlaw** | Preview only; no released story pages. | Issues 1–12 are compiled. Issue 1 is 22 pages; Issues 2–12 are currently 6 pages each. `series.json` says Issues 13–16 and the final causal answer remain development territory. | None. | Continue dramatic development for Issues 13–16/final causal answer. Also review whether `sourceBoundary.pages = 73` is intentionally historical source metadata or stale relative to the current compiled package; current page files total 88. No durable Sunforge reference pack is configured under `production/references/`. |
| **Vikings 2026** | Issue 1 released: 26 reader pages + collected PDF. | Issues 2–8 are production-ready. Issues 7–8 are locked 24-page production scripts compiled into active page recipes and assembler-audited. Issue 8 is the Season 1 finale; Issue 9 is not planned. | None. | No current writing/compilation blocker. Personal names for the two male Kin and Carrie's full legal/display name remain optional and non-blocking until a future story page requires them. |
| **Division Threshold** | Coming-soon catalog entry exists in StarSplitterVisions; no story assets are yet released there. | Issues 1–8 are compiled at 26 pages each. **Issue 1 image production, including the cover, is complete in the dedicated IMG Division project.** | Repository manifest has not yet been reconciled to the completed IMG Division assets. | Actual production frontier is Issue 1 complete. Next non-image action: import/recover the completed Issue 1 pages and cover, reconcile them to final page/recipe IDs, register durable production state, then prepare release and advance to Issue 2. |
| **Echoes of a Forgotten War** | Unreleased; no Echoes material exists in current StarSplitterVisions `main`. | Issues 1–8 are compiled for sequential page production, 12 pages each. The development-status file explicitly says writing recovery is complete through Issue 8. | None. | No missing-writing blocker. Durable visual reference pack exists. Repository production frontier remains `EFW_S1E01_S01` until a page is approved and stored. New writing would be Issue 9+ or a deliberate enhancement pass, not recovery. |
| **Shattering** | No corresponding released Visions series established by this audit. | Six issues are productionized as **132 page-level comic recipes** (22 pages each); 52 source scenes remain as provenance/source structure and all 124 original dialogue lines are preserved exactly once. Full six-issue writing/continuity review is complete. | None. | Story/recipe work is production-ready. Structured visual inventory now records **29 historical candidates across 13 source-scene groups**, but none are approved references or drafts and exact page mapping still requires original-pixel inspection. Production frontier remains `SHAT_I01_P01`; the only Shattering blocker is the visual-reference gate. |
| **Sun Comes Through — The Musical** | No Visions release established. | 16 scene units across 8 movements. The season plan calls the work a **working dramatic map** and each movement a developed outline. | None. | Continue dramatic development first. This is not yet comparable to a page-compiled comic package and should not be pushed into production merely because scene records exist. |

## Cross-project findings

1. **The approved-draft manifest currently contains only Azure Reach Issue 2 material:** nine approved image entries, P01–P08 and P11. Every other series has zero durable recipe-level approved drafts.
2. **Writing depth is substantially ahead of image-production state.** Multiple series have full seasons or long runs registered in RexPrompt with no unpublished approved image state.
3. **Registration is not the same as editorial readiness.** Stardust Issues 4–10 have completed season-level developmental review and Issues 8–10 production-structure recovery. Shattering is now page-productionized; the Musical remains a scene-level/development structure.
4. **Low Tide Signal recovery hygiene has been normalized.** The active package now has a single P-page recipe contract; obsolete recovery markers and the unused S-page package have been removed. No approved Low Tide production image is durably stored.
5. **Division Threshold's actual production frontier is now Issue 1 complete, including its cover, in the dedicated IMG Division project.** RexPrompt/Visions durability still lags that frontier until those completed image assets are imported/reconciled and registered.

## Immediate non-image work queue

1. **Sunforge Outlaw — develop Issues 13–16/final causal answer and reconcile current package metadata where needed.**
2. **Division Threshold — reconcile/import the completed Issue 1 pages and cover from the IMG Division project, register the durable production state, prepare release, then advance to Issue 2.**
3. **Azure Reach — reconcile/recover the noncontiguous Issue 2 approved-draft state.**

## Production-frontier rule

Do not infer progress from old chats or generated images alone.

For each series, production should advance from:

**released Visions canon + approved RexPrompt drafts + current compiled recipe order**

A generated image that is not released or registered as an approved draft does not advance the durable production checkpoint.
