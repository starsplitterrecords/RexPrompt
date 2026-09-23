# Shattering of the Corridors production package

## Current production state

The active RexPrompt package is page-based comic production.

- Series ID: `shattering`
- Shows: `shattering-i01` through `shattering-i06`
- Issues: 6
- Pages per issue: 22
- Total page recipes: 132
- Active files: `pages_i01.json` through `pages_i06.json`
- Production unit: `PAGE`
- Durable approved unpublished images: none at this checkpoint
- Structured visual-reference inventory: `production/references/shattering/reference-inventory.json`
- End-to-end writing/continuity review: complete through Issue 6
- Scene-flow structural pass: complete; `continuityFrom` is limited to true within-scene page continuation, abrupt location cuts are explicitly re-established, and clearly panel-local direction is embedded in the relevant panel plan.
- Scene-first natural-language dialogue rewrite: complete across all 52 scenes in Issues 1–6. Dialogue is authored as continuous dramatic scenes across page boundaries, then distributed into each page’s `dialogueInline` array. The current pass preserves terse operational speech while reducing polished thesis/counter-thesis exchanges in favor of interruptions, incomplete answers, practical objections, and character-specific phrasing. The active pages contain 676 short utterances averaging 5.4 words each and 27.8 dialogue words per page.
- Comprehensive editorial pass: complete through Issue 6; the active sequence now explicitly carries the emergency-override mechanism, principal-character aftermath, emerging faction-name usage, and the rescue-vessel throughline that forces the final doctrinal compromises into operational choices.
- Character naming normalization: complete. Approved principal identities are Liora Virelia, Lochran Davitt, Iskara Foster, Alan Kessler, Ava Seltos, Damian Cole, Ruben Markham, Heska Strauss, and Owen Hale; retired name-derived IDs/handles are removed from the active production package.
- Page architecture is intentionally non-uniform where the beat requires it; current panel-plan counts are 2-beat: 3, 3-beat: 19, 4-beat: 89, 5-beat: 19, 6-beat: 2.
- Story-level production blockers: none
- Visual-reference gate: open; no approved Shattering image baseline yet
- Production frontier: `SHAT_I01_P01`

`data/scenes_shattering.json` is the source-scene and provenance package. Its legacy dialogue-ID arrays have been retired. Each active page now carries a `sceneId`, and the active generation path is the six page files under `data/shows/shattering/`, with production dialogue stored directly in `dialogueInline`.

## Story architecture

The six-issue arc remains:

1. warning and institutional minimization
2. accumulating systemwide evidence and unauthorized intervention
3. failed damping attempt and transition from prevention to triage
4. network collapse
5. practical post-collapse survival methods diverge into factional traditions
6. contested inheritance, shared sigil, and the launch of the first multiworld rescue vessel

## Source scene to active page crosswalk


### Issue 1

| source scene | Active page range |
|---|---|
| `SCN_SHAT_I01_S01` | `SHAT_I01_P01`–`SHAT_I01_P03` |
| `SCN_SHAT_I01_S02` | `SHAT_I01_P04`–`SHAT_I01_P06` |
| `SCN_SHAT_I01_S03` | `SHAT_I01_P07`–`SHAT_I01_P08` |
| `SCN_SHAT_I01_S04` | `SHAT_I01_P09`–`SHAT_I01_P11` |
| `SCN_SHAT_I01_S05` | `SHAT_I01_P12`–`SHAT_I01_P13` |
| `SCN_SHAT_I01_S06` | `SHAT_I01_P14`–`SHAT_I01_P16` |
| `SCN_SHAT_I01_S07` | `SHAT_I01_P17`–`SHAT_I01_P18` |
| `SCN_SHAT_I01_S08` | `SHAT_I01_P19`–`SHAT_I01_P22` |

### Issue 2

| source scene | Active page range |
|---|---|
| `SCN_SHAT_I02_S01` | `SHAT_I02_P01`–`SHAT_I02_P03` |
| `SCN_SHAT_I02_S02` | `SHAT_I02_P04`–`SHAT_I02_P06` |
| `SCN_SHAT_I02_S03` | `SHAT_I02_P07`–`SHAT_I02_P08` |
| `SCN_SHAT_I02_S04` | `SHAT_I02_P09`–`SHAT_I02_P10` |
| `SCN_SHAT_I02_S05` | `SHAT_I02_P11`–`SHAT_I02_P12` |
| `SCN_SHAT_I02_S06` | `SHAT_I02_P13`–`SHAT_I02_P14` |
| `SCN_SHAT_I02_S07` | `SHAT_I02_P15`–`SHAT_I02_P18` |
| `SCN_SHAT_I02_S08` | `SHAT_I02_P19`–`SHAT_I02_P22` |

### Issue 3

| source scene | Active page range |
|---|---|
| `SCN_SHAT_I03_S01` | `SHAT_I03_P01`–`SHAT_I03_P03` |
| `SCN_SHAT_I03_S02` | `SHAT_I03_P04`–`SHAT_I03_P05` |
| `SCN_SHAT_I03_S03` | `SHAT_I03_P06`–`SHAT_I03_P07` |
| `SCN_SHAT_I03_S04` | `SHAT_I03_P08`–`SHAT_I03_P10` |
| `SCN_SHAT_I03_S05` | `SHAT_I03_P11`–`SHAT_I03_P12` |
| `SCN_SHAT_I03_S06` | `SHAT_I03_P13`–`SHAT_I03_P16` |
| `SCN_SHAT_I03_S07` | `SHAT_I03_P17`–`SHAT_I03_P19` |
| `SCN_SHAT_I03_S08` | `SHAT_I03_P20`–`SHAT_I03_P22` |

### Issue 4

| source scene | Active page range |
|---|---|
| `SCN_SHAT_I04_S01` | `SHAT_I04_P01`–`SHAT_I04_P03` |
| `SCN_SHAT_I04_S02` | `SHAT_I04_P04`–`SHAT_I04_P05` |
| `SCN_SHAT_I04_S03` | `SHAT_I04_P06`–`SHAT_I04_P07` |
| `SCN_SHAT_I04_S04` | `SHAT_I04_P08`–`SHAT_I04_P11` |
| `SCN_SHAT_I04_S05` | `SHAT_I04_P12`–`SHAT_I04_P13` |
| `SCN_SHAT_I04_S06` | `SHAT_I04_P14`–`SHAT_I04_P15` |
| `SCN_SHAT_I04_S07` | `SHAT_I04_P16`–`SHAT_I04_P18` |
| `SCN_SHAT_I04_S08` | `SHAT_I04_P19`–`SHAT_I04_P21` |
| `SCN_SHAT_I04_S09` | `SHAT_I04_P22`–`SHAT_I04_P22` |

### Issue 5

| source scene | Active page range |
|---|---|
| `SCN_SHAT_I05_S01` | `SHAT_I05_P01`–`SHAT_I05_P02` |
| `SCN_SHAT_I05_S02` | `SHAT_I05_P03`–`SHAT_I05_P05` |
| `SCN_SHAT_I05_S03` | `SHAT_I05_P06`–`SHAT_I05_P08` |
| `SCN_SHAT_I05_S04` | `SHAT_I05_P09`–`SHAT_I05_P10` |
| `SCN_SHAT_I05_S05` | `SHAT_I05_P11`–`SHAT_I05_P12` |
| `SCN_SHAT_I05_S06` | `SHAT_I05_P13`–`SHAT_I05_P15` |
| `SCN_SHAT_I05_S07` | `SHAT_I05_P16`–`SHAT_I05_P16` |
| `SCN_SHAT_I05_S08` | `SHAT_I05_P17`–`SHAT_I05_P19` |
| `SCN_SHAT_I05_S09` | `SHAT_I05_P20`–`SHAT_I05_P22` |

### Issue 6

| source scene | Active page range |
|---|---|
| `SCN_SHAT_I06_S01` | `SHAT_I06_P01`–`SHAT_I06_P02` |
| `SCN_SHAT_I06_S02` | `SHAT_I06_P03`–`SHAT_I06_P05` |
| `SCN_SHAT_I06_S03` | `SHAT_I06_P06`–`SHAT_I06_P07` |
| `SCN_SHAT_I06_S04` | `SHAT_I06_P08`–`SHAT_I06_P09` |
| `SCN_SHAT_I06_S05` | `SHAT_I06_P10`–`SHAT_I06_P12` |
| `SCN_SHAT_I06_S06` | `SHAT_I06_P13`–`SHAT_I06_P14` |
| `SCN_SHAT_I06_S07` | `SHAT_I06_P15`–`SHAT_I06_P16` |
| `SCN_SHAT_I06_S08` | `SHAT_I06_P17`–`SHAT_I06_P18` |
| `SCN_SHAT_I06_S09` | `SHAT_I06_P19`–`SHAT_I06_P20` |
| `SCN_SHAT_I06_S10` | `SHAT_I06_P21`–`SHAT_I06_P22` |

## Production readiness

The six-issue writing, causal continuity, character aftermath, page architecture, identity normalization, Rex Fleet lineage check, assembled-page structure, and end-to-end sequence review are complete. The remaining gate is visual rather than narrative: image generation should not begin until a usable approved Shattering reference baseline is established.

The current reference inventory records 29 historical recovery candidates across 13 source-scene groups. None are approved references or approved drafts.

## Recovery boundary

Historical image candidates mapped to source scene IDs are not automatically valid page references. A source scene now spans one to four page recipes.

Before any recovered image can become an approved current-production reference:

1. recover and inspect the original pixels;
2. identify the exact active page recipe the image actually depicts;
3. verify recipe fidelity and continuity;
4. approve the image;
5. register it in `production/drafts/manifest.json`.

Do not infer the page mapping from the old filename or source scene ID alone.

## Editorial boundary

The current page package preserves the original event order, causal spine, character arcs, and major reveals while substantially rewriting dialogue for scene-level dramatic flow. Existing 22-page issue lengths were retained because the established scene spans provide sufficient visual and dialogue room after the rewrite; no page was added or removed merely to increase dialogue density. There is no released Shattering canon in StarSplitterVisions at this checkpoint.
