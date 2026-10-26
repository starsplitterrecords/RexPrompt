# IMG historical generated-page recovery — portfolio evidence checkpoint

**Evidence date:** 2026-10-25 (America/New_York); **baseline RexPrompt commit:** `bf72a9939aabfb9ebc90b724eb3836be510fd5c7`; approved-draft manifest Git blob: `5145db2d68e3ca08e30a4becf806feab1339dd72`.

This is an evidence-preserving audit, not a mastering report, approval, release, or claim that every chat-history generation is recoverable. Approved image bytes must be original, and image promotion requires exact active `seriesId::issueId::recipeId` identity plus approval evidence.

## Current registered original draft assets

- **113** manifest-approved draft records across Rex Fleet **76**, Vikings 2026 **22**, Azure Reach **11**, and Stardust Station **4**.
- Existing `tools/audit_asset_recovery.cjs` checks all 113 registered paths, image signatures, Keeper assets and book completeness; current Git tree likewise contains 113 draft image blobs at the registered paths. Do not re-add or overwrite them merely because a similarly titled Library image exists.
- Sampled historical Git revisions `0eff5ee6` (11), `ff9ab70a` (57), `1affa917` (113), and current main (113) showed no older approved draft path missing from the current main set. **This is a checkpoint comparison, not a claim of exhaustive commit-by-commit Git history reconstruction.**
- Book slots are provided by `production/book-manifests.json`. A series lacking a book manifest cannot be called a complete issue merely because it has no draft entries.

## Complete book manifests and exact currently unregistered units

| Authoritative book inventory | Registered/required | Specific missing recipe IDs |
| --- | ---: | --- |
| `rex-fleet::rex-fleet-i01` | 22/22 | None |
| `rex-fleet::rex-fleet-i02` | 24/24 | None |
| `rex-fleet::rex-fleet-i03` | 30/35 | `RF_I03_P28`, `RF_I03_P29`, `RF_I03_P30`, `RF_I03_EDITOR_ENDMATTER`, `RF_I03_EDITOR_CLOSE` |
| `vikings-2026::vikings-2026-s1-e02` | 4/23 | `VIK_S1E02_P05`, `VIK_S1E02_P06`, `VIK_S1E02_P07`, `VIK_S1E02_P08`, `VIK_S1E02_P09`, `VIK_S1E02_P10`, `VIK_S1E02_P11`, `VIK_S1E02_P12`, `VIK_S1E02_P13`, `VIK_S1E02_P14`, `VIK_S1E02_P15`, `VIK_S1E02_P16`, `VIK_S1E02_P17`, `VIK_S1E02_P18`, `VIK_S1E02_P19`, `VIK_S1E02_P20`, `VIK_S1E02_P21`, `VIK_S1E02_P22`, `VIK_S1E02_P23` |
| `stardust-station::stardust-station-e02` | 4/25 | `SDS_S1E02_COVER`, `SDS_S1E02_EDITOR`, `SDS_S1E02_P01`, `SDS_S1E02_P05`, `SDS_S1E02_P07`, `SDS_S1E02_P08`, `SDS_S1E02_P09`, `SDS_S1E02_P10`, `SDS_S1E02_P11`, `SDS_S1E02_P12`, `SDS_S1E02_P13`, `SDS_S1E02_P14`, `SDS_S1E02_P15`, `SDS_S1E02_P16`, `SDS_S1E02_P17`, `SDS_S1E02_P18`, `SDS_S1E02_P19`, `SDS_S1E02_P20`, `SDS_S1E02_P21`, `SDS_S1E02_P22`, `SDS_S1E02_TEASER` |

## Priority source dispositions

### Rex Fleet Issue 3 — five missing

- `RF_I03_P28`: historical output and subsequent revisions reported, but documented pseudo-lettering/identity defects; no passing approved original confirmed. **No promotion.**
- `RF_I03_P29`: corrected five-panel output reported in historical conversation, but no durable original binary for that approved-looking revision has been identified in current RexPrompt or searched IMG source directories. **Do not infer approval from generation.**
- `RF_I03_P30`: past temporary/upscaled candidate rejected as native-resolution master; no passing original confirmed. **No promotion.**
- `RF_I03_EDITOR_ENDMATTER`: exact original 5,579,878-byte PNG, **2400 × 3840**, ICC present; Library `file_0000000033cc81f5afb10f03273a14f4`, SHA-256 `318b43cc91ddb9951a7e8717698c4b87b66392d0c1cf08a57c6329cf5f1d4c20`. Editable original SVG also present (`file_000000009b9081f58533d13bbf47320e`). Visually inspected, but the source is not a durable record of final user approval. **Preserved candidate, not approved draft.**
- `RF_I03_EDITOR_CLOSE`: exact original 7,699,765-byte PNG, **2400 × 3840**, Library `file_0000000018f881f5a1d501defa057c51`, SHA-256 `9a7f442d4fe511849b8134eae62e03127df3923dc65c9499bb86be07c71305e3`. SVG `file_00000000a3f081f58bf442265ec3f701` includes **991 × 1587** embedded raster art; page-canvas dimensions do not prove native source detail. Prior user rejection/supersession prevents assuming it is final. **Preserved candidate, not approved draft.**

### Vikings 2026

- Issue 2 authoritative inventory: 23 slots, 4 manifest records, **19 missing**, enumerated above.
- The Library `vik_s1e02_p01_simple_cover.png` (file `file_0000000017fc820d88eeb7d92261c291`, 10,384,358 bytes) is **exactly** the current registered Git blob `ce2b626176ad322610716690def7af582b4659b1`; recovered bytes matched via Git's blob SHA-1 framing. Already safely stored. The earlier `vik_s1e02_p01_cover.png` is a distinct superseded candidate.
- Library `VIK_S1E02_P03.png` (file `file_00000000db1c81f591c73cb298eb9011`) has original Git blob hash `e954c8ecc51446edbdf6dbd1882cb49290719680` and does **not** match the stored approved draft P03 (`c2eb565cd8bbe3de89298d5904ec92ecef09c7c3`). The older candidate was reported to contain corrupted lettering, panel-count and lighting issues; do not overwrite approved P03.
- Nine `VIK_S1E08_P01`–`P09` Library images exist; original P09 was retrieved at 2400 × 3840, ICC present, SHA-256 `761b57af0a29ffc1ffe27cf4edc378815979376e0e113a8c0f07a4b56d734b33` (Library `file_000000009e2881f59aec3e5b78cb6f7f`). Image generation was requested, but durable final approvals and modern recipe fidelity have not been established. **Historical candidates only.**
- The separate `/IMG Vikings/` archive `pages.zip` (Library `file_00000000e8c881f5afe2a8e676f56184`) could not be materialized by the current Project authorization path; this does not establish that it is corrupted or permanently inaccessible.

### Stardust Station Issue 2

- The issue has 4 registered of 25 expected book slots; **21 missing**, enumerated above.
- `SDS_S1E02_P08_master.png`, Library `file_000000000a0881f5bcd958ff0d8c0acc`, 11,044,495 bytes, and `SDS_S1E02_P09_master.png`, Library `file_00000000939c81f5b509d3a547570aa9`, 10,517,258 bytes, are discoverable and visible as actual pixels via Library image readback. They show original sequence artwork, but no final user approval is substantiated.
- Raw-byte materialization of both Stardust Library files returned **"This Project file does not have an authorized raw-byte materialization path."** Therefore there is no verified exact SHA-256 or original binary to commit in this session. **Accessible as visual candidates, not yet byte-recovered or approved.**

### Shattering — deliberately preserve scene/page boundary

- All **29** prior historical File Library candidates from **13 legacy source-scene groups** in `production/references/shattering/reference-inventory.json` were materialized as exact unchanged PNG bytes and visually inspected as a contact sheet. **27 are 864 × 1821**, one **887 × 1774**, and one **862 × 1825**; none has embedded ICC.
- The current series is **page-based**. The legacy source scene and candidate page ranges cannot resolve a unique active recipe by filename alone; multiple images have identical legacy scenes and divergent titles. All 29 remain **unapproved** and the current first-page frontier remains `SHAT_I01_P01`.
- See `production/references/shattering/recovery-binary-note.md` for updated evidence and `reference-inventory.json` for every original Library ID and candidate page span.

## Released Visions — different authority, not draft masters

StarSplitterVisions main includes **157 published JPEG comic-page files** in six issue folders, and six issue PDFs:

| Released issue | Published page-image files |
| --- | ---: |
| Azure Reach Issue 1 | 22 |
| Backyard Rockets Issue 1 | 21 |
| Backyard Rockets Issue 2 | 47 |
| Rex Fleet Issue 1 | 19 |
| Stardust Station Issue 1 | 22 |
| Vikings 2026 Issue 1 | 26 |

These released images are visual/release canon and can be inspected, but JPEG derivatives are **not substituted** for absent original generated PNG draft binaries. The total `157` reflects the on-disk published JPEG files, not an assurance that every desired editorial/cover/book unit is in the PDF.

## Portfolio-wide registered show configurations

RexPrompt contains **126 show configurations** across page, scene and cover modes; these are **not 126 comic pages**. The table below identifies every registered configuration. Issue labels without book-manifest records are **not** asserted complete, and a blank approval count means **no approved-draft mapping**, not that no IMG image was ever generated. Run `node tools/audit_all_series_production.cjs --out <report.json>` for the assembled recipe-unit count and missing IDs for every registered configuration.

| Series / registration scope | Configuration IDs (approved-draft records noted) |
| --- | --- |
| shattering | `shattering-i01`, `shattering-i02`, `shattering-i03`, `shattering-i04`, `shattering-i05`, `shattering-i06`, `shattering-covers` |
| rex-fleet-academy-anomalies | `rex-fleet-academy-anomalies-i01` |
| rfa-reach-resolve | `rfa-reach-resolve-i01` |
| rex-fleet | `rex-fleet-i01` (22 recorded), `rex-fleet-i02` (24 recorded), `rex-fleet-i03` (30 recorded), `rex-fleet-i04`, `rex-fleet-i05`, `rex-fleet-i06`, `rex-fleet-i07`, `rex-fleet-i08`, `rex-fleet-i09`, `rex-fleet-i10`, `rex-fleet-i11`, `rex-fleet-i12` |
| rex-fleet-stormwell-archive | `rex-fleet-stormwell-archive-i01` |
| rex-fleet-glass-horizon | `rex-fleet-glass-horizon-i01` |
| backyard-rockets | `backyard-rockets-s1` |
| azure-reach | `azure-reach-s1`, `azure-reach-s1-e02` (11 recorded), `azure-reach-s1-e03`, `azure-reach-s1-e04`, `azure-reach-s1-e05`, `azure-reach-s1-e06`, `azure-reach-s1-covers` |
| stardust-station | `stardust-station`, `stardust-station-e02` (4 recorded), `stardust-station-e03`, `stardust-station-e04`, `stardust-station-e05`, `stardust-station-e06`, `stardust-station-e07`, `stardust-station-e08`, `stardust-station-e09`, `stardust-station-e10`, `stardust-station-cover-e01`, `stardust-station-cover-e02`, `stardust-station-cover-e03`, `stardust-station-cover-e04`, `stardust-station-cover-e05`, `stardust-station-cover-e06`, `stardust-station-cover-e07`, `stardust-station-cover-e08`, `stardust-station-cover-e09`, `stardust-station-cover-e10` |
| vikings-2026 | `vikings-2026-s1-e01` (18 recorded), `vikings-2026-s1-e02` (4 recorded), `vikings-2026-s1-e03`, `vikings-2026-s1-e04`, `vikings-2026-s1-e05`, `vikings-2026-s1-e06`, `vikings-2026-s1-e07`, `vikings-2026-s1-e08`, `vikings-2026-s1-e09`, `vikings-2026-s1-e10`, `vikings-2026-s1-e11`, `vikings-2026-s1-e12` |
| low-tide-signal | `low-tide-signal-c01`, `low-tide-signal-c02`, `low-tide-signal-c03`, `low-tide-signal-c04`, `low-tide-signal-c05`, `low-tide-signal-c06`, `low-tide-signal-c07`, `low-tide-signal-cover-c01`, `low-tide-signal-cover-c02`, `low-tide-signal-cover-c03`, `low-tide-signal-cover-c04`, `low-tide-signal-cover-c05`, `low-tide-signal-cover-c06`, `low-tide-signal-cover-c07` |
| division-threshold | `division-threshold-s1-e01`, `division-threshold-s1-e02`, `division-threshold-s1-e03`, `division-threshold-s1-e04`, `division-threshold-s1-e05`, `division-threshold-s1-e06`, `division-threshold-s1-e07`, `division-threshold-s1-e08`, `division-threshold-s1-cover-e01`, `division-threshold-s1-cover-e02`, `division-threshold-s1-cover-e03`, `division-threshold-s1-cover-e04`, `division-threshold-s1-cover-e05`, `division-threshold-s1-cover-e06`, `division-threshold-s1-cover-e07`, `division-threshold-s1-cover-e08`, `division-threshold-s1-editorial-e01`, `division-threshold-s1-editorial-e02`, `division-threshold-s1-editorial-e03`, `division-threshold-s1-editorial-e04`, `division-threshold-s1-editorial-e05`, `division-threshold-s1-editorial-e06`, `division-threshold-s1-editorial-e07`, `division-threshold-s1-editorial-e08` |
| sun-comes-through | `sun-comes-through-musical-s1` |
| echoes-forgotten-war | `echoes-forgotten-war-s1`, `echoes-forgotten-war-s1-covers` |
| sunforge-outlaw | `sunforge-outlaw-s1-e01`, `sunforge-outlaw-s1-e02`, `sunforge-outlaw-s1-e03`, `sunforge-outlaw-s1-e04`, `sunforge-outlaw-s1-e05`, `sunforge-outlaw-s1-e06`, `sunforge-outlaw-s1-e07`, `sunforge-outlaw-s1-e08`, `sunforge-outlaw-s1-e09`, `sunforge-outlaw-s1-e10`, `sunforge-outlaw-s1-e11`, `sunforge-outlaw-s1-e12` |
| rex-fleet-academy-navigating-mirrorfold | `rex-fleet-academy-navigating-mirrorfold-i01` |
| rex-fleet-academy-doctrine-many-crowns | `rex-fleet-academy-doctrine-many-crowns-i01` |
| rex-fleet-academy-between-beacons | `rex-fleet-academy-between-beacons-i01`, `rex-fleet-academy-between-beacons-cover-i01` |
| rex-fleet-academy-core-worlds | `rex-fleet-academy-core-worlds-i01` |
| rex-fleet-academy-physics-lattice | `rex-fleet-academy-physics-lattice-i01` |
| rex-fleet-aegis-vigil | `rex-fleet-aegis-vigil-i01` |
| rex-fleet-ghostwind-arrow | `rex-fleet-ghostwind-arrow-i01` |
| rex-fleet-slip-knife | `rex-fleet-slip-knife-i01` |
| rex-fleet-crimson-warden | `rex-fleet-crimson-warden-i01` |

## Full accessible Library image search (completed)

An image-filtered, recursive Library listing exhausted all **3,534** currently returned image records across 18 API pages (descending creation order, back to 2025-03-29). Relevant top-level Library folders included `/Visions/` **958**, `/IMG Rex Fleet/` **387**, `/IMG Vikings/` **319**, `/IMG Stardust Station/` **74**, `/IMG Echoes of a Forgotten War/` **50**, `/IMG Division Threshold/` **37**, `/IMG Low Tide Signal/` **24**, `/IMG Sunforge Outlaw/` **7**, `/IMG Backyard Rockets/` **6**, and `/IMG Azure Reach/` **2** image entries. Many others are outside IMG or stored with non-identifying filenames. These folder tallies are discovery counts, **not** approved-page or original-master counts.

Targeted raw-byte availability is heterogeneous: some historically generated images materialized intact; five additional named Vikings Issue 2 P05 revisions were found but denied raw-byte materialization in this Project (`VIK_S1E02_P05_four_line_exchange_master.png`, `VIK_S1E02_P05_dialogue_edit_master.png`, `VIK_S1E02_P05_apartment_revised_candidate.png`, `VIK_S1E02_P05_remake_candidate.png`, `VIK_S1E02_P05_repaired_candidate.png`). Prior production notes identify P05 remake/apartment variants as unapproved and record outstanding panel-continuity repairs. **No P05 image is added to RexPrompt.**

This exhaustive returned-image listing does **not** provide a machine-verifiable reverse mapping for descriptively named artifacts to all active page recipes or durable approval decisions from every original conversation. It also excludes non-image ZIP/PDF archives, some of which may have different access controls. For that reason no unsupported assertion of permanent inaccessibility is made.

## Boundaries and next recovery blockers

1. **No new approvals have been fabricated**; a found image, successful generation, native-size page canvas, or user request to generate does not itself prove final approval.
2. Raw originals may remain accessible in Library even when a given Project materialization call is denied. The 29 Shattering originals demonstrate why historical `401 Unauthorized` claims should not be treated as permanent file loss.
3. Additional IMG images in `/Visions/` and named Library folders have descriptive filenames that do not encode exact active recipe IDs. They are discovery candidates pending conversation-level approval and direct image inspection.
4. Source images already in published Visions are intentionally not reverse-imported as native drafts.
5. No issue is certified finished, mastered, print-native, continuity-safe, or published as a result of this audit.
