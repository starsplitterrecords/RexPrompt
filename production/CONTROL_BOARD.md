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
| **Backyard Rockets** | Issues 1–2 released as combined edition. Visions exposes 47 reader-page assets for the combined release; release copy describes a 48-page edition. | RexPrompt registry exposes Season 1 through Issue 8. Issues 1–2 are rebuilt packages; Issues 3–8 are encoded production packages. | None. | Verify the 47-reader-page vs 48-page collected-edition count before changing release metadata; it may simply reflect a cover/editorial page outside the reader. Separately perform a developmental readiness pass on Issues 3–8 before assuming registration alone means final writing. |
| **Low Tide Signal** | Preview only; no released story pages. | Chapters 1–7 are registered. Chapters 1–3 contain 78 compiled pages total; Chapters 4–7 are enhanced encoded packages. | None. | Clean and resolve the reference/recovery state first. `recovery-status.json` says `binary-persistence-pending` for 8 scene pages, while the reference directory still contains explicit temporary/pause residue including a file that says it should not exist in final state. |
| **Rex Fleet** | Issue 1 released: 19 reader pages (18 story pages plus editorial material) + collected PDF. | Issues 2–12 are compiled/registered. Issue 2 has 19 pages; Issue 3 has 30; Issues 4–12 are encoded production packages. | None. | No writing-recovery blocker established. Durable unpublished production state is empty, so the repository frontier is Issue 2 Page 1 unless prior approved work is deliberately recovered and registered. |
| **Stardust Station** | Issue 1 released: 22 reader pages + collected PDF. | Issues 2–10 are registered. Issues 2–3 are enhanced, sanitized encoded 22-page packages. Issues 4–10 are finished drama-first 22-page packages; season-level developmental review completed 2026-09-18, and Issues 8–10 production structure was recovered so exact dialogue/lettering is separated from panel staging. | None. | No non-image writing blocker found. Production can proceed from Issue 2 Page 1, subject to the normal visual-reference and approval gates. |
| **Sunforge Outlaw** | Preview only; no released story pages. | Issues 1–12 are compiled. Issue 1 is 22 pages; Issues 2–12 are currently 6 pages each. `series.json` says Issues 13–16 and the final causal answer remain development territory. | None. | Continue dramatic development for Issues 13–16/final causal answer. Also review whether `sourceBoundary.pages = 73` is intentionally historical source metadata or stale relative to the current compiled package; current page files total 88. No durable Sunforge reference pack is configured under `production/references/`. |
| **Vikings 2026** | Issue 1 released: 26 reader pages + collected PDF. | Issues 2–8 are production-ready. Issues 7–8 are locked 24-page production scripts compiled into active page recipes and assembler-audited. Issue 8 is the Season 1 finale; Issue 9 is not planned. | None. | No current writing/compilation blocker. Personal names for the two male Kin and Carrie's full legal/display name remain optional and non-blocking until a future story page requires them. |
| **Division Threshold** | No StarSplitterVisions series metadata currently exists. | Issues 1–8 are compiled at 26 pages each and are registered through the supported `scenesFiles` path. | None. | Decide release/preview intent. `production/visual-sources.json` currently declares a `division-threshold` Visions slug even though that series JSON does not exist; the durable reference pack is therefore the usable visual authority until a release exists. |
| **Echoes of a Forgotten War** | Unreleased; no Echoes material exists in current StarSplitterVisions `main`. | Issues 1–8 are compiled for sequential page production, 12 pages each. The development-status file explicitly says writing recovery is complete through Issue 8. | None. | No missing-writing blocker. Durable visual reference pack exists. Repository production frontier remains `EFW_S1E01_S01` until a page is approved and stored. New writing would be Issue 9+ or a deliberate enhancement pass, not recovery. |
| **Star Splitter Prequel** | No corresponding released Visions series established by this audit. | Six issue packages exist as 52 **scene-level** recipes: 8/8/8/9/9/10 scenes. They do not contain page panel plans. | None. | Convert/compile the scene-level material into page-level comic production recipes before treating it like the newer one-recipe-per-page series. Existing durable reference material is recovery-oriented rather than a normal production reference pack. |
| **Sun Comes Through — The Musical** | No Visions release established. | 16 scene units across 8 movements. The season plan calls the work a **working dramatic map** and each movement a developed outline. | None. | Continue dramatic development first. This is not yet comparable to a page-compiled comic package and should not be pushed into production merely because scene records exist. |

## Cross-project findings

1. **The approved-draft manifest currently contains only Azure Reach Issue 2 material:** nine approved image entries, P01–P08 and P11. Every other series has zero durable recipe-level approved drafts.
2. **Writing depth is substantially ahead of image-production state.** Multiple series have full seasons or long runs registered in RexPrompt with no unpublished approved image state.
3. **Registration is not the same as editorial readiness.** Stardust Issue 4 is explicitly temporary; the Prequel and Musical remain scene-level/development structures.
4. **Low Tide Signal has the clearest repository-hygiene blocker.** Temporary recovery artifacts and a pending binary-persistence state remain in the active reference tree.
5. **Division Threshold has a source-mapping inconsistency.** RexPrompt expects a Visions slug that does not currently exist.
5. **Backyard Rockets needs a count verification, not an automatic fix.** The 47 reader assets may be correct if the advertised 48-page edition includes a cover/editorial page outside the reader.

## Immediate non-image work queue

1. **Low Tide Signal — finish recovery-state cleanup and sanitize the active reference tree.**
2. **Stardust Station — editorial review of Issue 4 “Temporary Material” and downstream Issues 5–10.**
3. **Star Splitter Prequel — convert scene-level material into page-level production recipes.**
4. **Sunforge Outlaw — develop Issues 13–16/final causal answer and reconcile current package metadata where needed.**
6. **Backyard Rockets — developmental readiness review of Issues 3–8 and verify the 47/48-page release-count interpretation.**
6. **Division Threshold — decide whether to establish Visions metadata/preview or keep the series intentionally unreleased and adjust source mapping accordingly.**
7. **Azure Reach — reconcile/recover the noncontiguous Issue 2 approved-draft state.**

## Production-frontier rule

Do not infer progress from old chats or generated images alone.

For each series, production should advance from:

**released Visions canon + approved RexPrompt drafts + current compiled recipe order**

A generated image that is not released or registered as an approved draft does not advance the durable production checkpoint.
