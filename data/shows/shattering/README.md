# Shattering of the Corridors production package

## Current production state

The active RexPrompt package is page-based comic production.

- Series ID: `shattering`
- Shows: `shattering-i01` through `shattering-i06`
- Issues: 6
- Pages per issue: 24 (1 opening editorial + 22 story pages + 1 closing editorial/teaser)
- Total page recipes: 144 (132 story pages + 12 editorial bookends)
- Active files: `pages_i01.json` through `pages_i06.json`
- Production unit: `PAGE`
- Durable approved unpublished images: none at this checkpoint
- Structured visual-reference inventory: `production/references/shattering/reference-inventory.json`
- End-to-end writing/continuity review: complete through Issue 6
- Scene-flow structural pass: complete; `continuityFrom` is limited to true within-scene page continuation, abrupt location cuts are explicitly re-established, and clearly panel-local direction is embedded in the relevant panel plan.
- Scene-first natural-language dialogue rewrite: complete across all 52 scenes in Issues 1–6. Dialogue is authored as continuous dramatic scenes across page boundaries, then distributed into each page’s `dialogueInline` array. The current pass preserves terse operational speech while reducing polished thesis/counter-thesis exchanges in favor of interruptions, incomplete answers, practical objections, and character-specific phrasing. The 132 story pages contain 676 short utterances averaging 5.4 words each and 27.8 dialogue words per story page; editorial bookend copy is tracked separately.
- Comprehensive editorial pass: complete through Issue 6; the active sequence now explicitly carries the emergency-override mechanism, principal-character aftermath, emerging faction-name usage, and the rescue-vessel throughline that forces the final doctrinal compromises into operational choices.
- Character naming normalization: complete. Approved principal identities are Liora Virelia, Lochran Davitt, Iskara Foster, Alan Kessler, Ava Seltos, Damian Cole, Ruben Markham, Heska Strauss, and Owen Hale; retired name-derived IDs/handles are removed from the active production package.
- Page architecture is intentionally non-uniform where the beat requires it; current panel-plan counts are 2-beat: 3, 3-beat: 19, 4-beat: 89, 5-beat: 19, 6-beat: 2.
- Story-level production blockers: none
- Visual-reference gate: open; no approved Shattering image baseline yet
- Production frontier: `SHAT_I01_P01`
- Cover recipe shelf: `data/shows/shattering/covers.json` (Issues 1–6, production-ready)
- Cover production contract: `production/references/shattering/cover-production-normalization.json`
- Cover trade-dress bootstrap: generate/approve `SHAT_I01_COVER` first; after approval persist its exact pixels to `production/references/shattering/assets/covers/issue-01-cover-trade-dress.png`. Later covers must pixel-read that asset for masthead/trade-dress continuity only.

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
| `SCN_SHAT_I01_S01` | `SHAT_I01_P02`–`SHAT_I01_P04` |
| `SCN_SHAT_I01_S02` | `SHAT_I01_P05`–`SHAT_I01_P07` |
| `SCN_SHAT_I01_S03` | `SHAT_I01_P08`–`SHAT_I01_P09` |
| `SCN_SHAT_I01_S04` | `SHAT_I01_P10`–`SHAT_I01_P12` |
| `SCN_SHAT_I01_S05` | `SHAT_I01_P13`–`SHAT_I01_P14` |
| `SCN_SHAT_I01_S06` | `SHAT_I01_P15`–`SHAT_I01_P17` |
| `SCN_SHAT_I01_S07` | `SHAT_I01_P18`–`SHAT_I01_P19` |
| `SCN_SHAT_I01_S08` | `SHAT_I01_P20`–`SHAT_I01_P23` |

### Issue 2

| source scene | Active page range |
|---|---|
| `SCN_SHAT_I02_S01` | `SHAT_I02_P02`–`SHAT_I02_P04` |
| `SCN_SHAT_I02_S02` | `SHAT_I02_P05`–`SHAT_I02_P07` |
| `SCN_SHAT_I02_S03` | `SHAT_I02_P08`–`SHAT_I02_P09` |
| `SCN_SHAT_I02_S04` | `SHAT_I02_P10`–`SHAT_I02_P11` |
| `SCN_SHAT_I02_S05` | `SHAT_I02_P12`–`SHAT_I02_P13` |
| `SCN_SHAT_I02_S06` | `SHAT_I02_P14`–`SHAT_I02_P15` |
| `SCN_SHAT_I02_S07` | `SHAT_I02_P16`–`SHAT_I02_P19` |
| `SCN_SHAT_I02_S08` | `SHAT_I02_P20`–`SHAT_I02_P23` |

### Issue 3

| source scene | Active page range |
|---|---|
| `SCN_SHAT_I03_S01` | `SHAT_I03_P02`–`SHAT_I03_P04` |
| `SCN_SHAT_I03_S02` | `SHAT_I03_P05`–`SHAT_I03_P06` |
| `SCN_SHAT_I03_S03` | `SHAT_I03_P07`–`SHAT_I03_P08` |
| `SCN_SHAT_I03_S04` | `SHAT_I03_P09`–`SHAT_I03_P11` |
| `SCN_SHAT_I03_S05` | `SHAT_I03_P12`–`SHAT_I03_P13` |
| `SCN_SHAT_I03_S06` | `SHAT_I03_P14`–`SHAT_I03_P17` |
| `SCN_SHAT_I03_S07` | `SHAT_I03_P18`–`SHAT_I03_P20` |
| `SCN_SHAT_I03_S08` | `SHAT_I03_P21`–`SHAT_I03_P23` |

### Issue 4

| source scene | Active page range |
|---|---|
| `SCN_SHAT_I04_S01` | `SHAT_I04_P02`–`SHAT_I04_P04` |
| `SCN_SHAT_I04_S02` | `SHAT_I04_P05`–`SHAT_I04_P06` |
| `SCN_SHAT_I04_S03` | `SHAT_I04_P07`–`SHAT_I04_P08` |
| `SCN_SHAT_I04_S04` | `SHAT_I04_P09`–`SHAT_I04_P12` |
| `SCN_SHAT_I04_S05` | `SHAT_I04_P13`–`SHAT_I04_P14` |
| `SCN_SHAT_I04_S06` | `SHAT_I04_P15`–`SHAT_I04_P16` |
| `SCN_SHAT_I04_S07` | `SHAT_I04_P17`–`SHAT_I04_P19` |
| `SCN_SHAT_I04_S08` | `SHAT_I04_P20`–`SHAT_I04_P22` |
| `SCN_SHAT_I04_S09` | `SHAT_I04_P23`–`SHAT_I04_P23` |

### Issue 5

| source scene | Active page range |
|---|---|
| `SCN_SHAT_I05_S01` | `SHAT_I05_P02`–`SHAT_I05_P03` |
| `SCN_SHAT_I05_S02` | `SHAT_I05_P04`–`SHAT_I05_P06` |
| `SCN_SHAT_I05_S03` | `SHAT_I05_P07`–`SHAT_I05_P09` |
| `SCN_SHAT_I05_S04` | `SHAT_I05_P10`–`SHAT_I05_P11` |
| `SCN_SHAT_I05_S05` | `SHAT_I05_P12`–`SHAT_I05_P13` |
| `SCN_SHAT_I05_S06` | `SHAT_I05_P14`–`SHAT_I05_P16` |
| `SCN_SHAT_I05_S07` | `SHAT_I05_P17`–`SHAT_I05_P17` |
| `SCN_SHAT_I05_S08` | `SHAT_I05_P18`–`SHAT_I05_P20` |
| `SCN_SHAT_I05_S09` | `SHAT_I05_P21`–`SHAT_I05_P23` |

### Issue 6

| source scene | Active page range |
|---|---|
| `SCN_SHAT_I06_S01` | `SHAT_I06_P02`–`SHAT_I06_P03` |
| `SCN_SHAT_I06_S02` | `SHAT_I06_P04`–`SHAT_I06_P06` |
| `SCN_SHAT_I06_S03` | `SHAT_I06_P07`–`SHAT_I06_P08` |
| `SCN_SHAT_I06_S04` | `SHAT_I06_P09`–`SHAT_I06_P10` |
| `SCN_SHAT_I06_S05` | `SHAT_I06_P11`–`SHAT_I06_P13` |
| `SCN_SHAT_I06_S06` | `SHAT_I06_P14`–`SHAT_I06_P15` |
| `SCN_SHAT_I06_S07` | `SHAT_I06_P16`–`SHAT_I06_P17` |
| `SCN_SHAT_I06_S08` | `SHAT_I06_P18`–`SHAT_I06_P19` |
| `SCN_SHAT_I06_S09` | `SHAT_I06_P20`–`SHAT_I06_P21` |
| `SCN_SHAT_I06_S10` | `SHAT_I06_P22`–`SHAT_I06_P23` |

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

The current page package preserves the original 22-page story sequence in each issue while adding one art-directed editor splash before it and one teaser/editorial splash after it. The story event order, causal spine, character arcs, major reveals, scene spans, dialogue, and panel plans remain intact; only story page IDs and within-scene continuity pointers shift by one to make room for the opening editorial. There is no released Shattering canon in StarSplitterVisions at this checkpoint.


## Cover production

Shattering has six chef-facing cover recipes in `covers.json`, registered through the `shattering-covers` `COVER` shelf in `data/shows.json`. They use the same assembler-visible fields as story pages, so no assembler change is required.

The Issue 1 cover is the founding trade-dress cover. Its assembled recipe controls the Issue 1 selling image and establishes a repeatable `REX FLEET ACADEMY / SHATTERING OF THE CORRIDORS / ISSUE ##` masthead architecture. After the Issue 1 cover is explicitly approved, persist the exact approved pixels to `production/references/shattering/assets/covers/issue-01-cover-trade-dress.png` and activate the cover contract.

Issues 2–6 must retrieve and visually inspect those actual Issue 1 pixels before cover generation. That pixel reference controls only recurring masthead/trade-dress appearance: title hierarchy, placement, issue-number treatment, margins, logo scale, and cover-brand recognition. The current issue's assembled cover recipe continues to control composition, cast, location, palette, action, symbolism, and spoiler ceiling.

Cover recipes obey Shattering chronology. High Era covers use Cooperative/BHA/Convoy/Outer Band visual language; later covers may show proto-Core/Fleet, proto-Verge, and proto-Shard ancestry through behavior and materials without importing mature post-Shattering uniforms, ships, institutions, or finished faction iconography.
