# Cross-series production-quality and continuity audit

**Date:** 2026-10-25 (GitHub inspection continued into 2026-10-26 UTC). **Authority:** RexPrompt assembled scripts/drafts/references; published StarSplitterVisions assets are immutable released canon absent explicitly approved correction.

## What was and was not verified

- All **126** registered RexPrompt configurations assemble as reported by the existing all-series audit, covering **24** series and **2,546** recipe units (including a musical whose comic visual QC is not applicable).
- Current inventory at this check: **113** RexPrompt approved-draft records; **41** Keeper references; **74** exact book inventories. GitHub Actions verified source/overlay loading and structural integrity, not the appearance of every stored picture.
- **Six** published editions contain **157** public daily-page JPEG paths, with **six** linked PDF paths. Every referenced path exists in the release tree. Actual pixels were inspected in a **sample of 32 pages** spanning Azure Reach, Backyard Rockets (both editions), Rex Fleet, Stardust Station, and Vikings. The full 157-page visual sequence is NOT marked passed.
- Exact selected samples, passing-scope limitations, and evidence are in `production/audits/visual_review_2026-10-25.json`.
- Approved draft PNG binary readback into this model's visual context was unsuccessful; therefore no approved RexPrompt draft is claimed visually verified. Keeper references were structurally indexed but not inspected as pixels here. Other IMG renders in conversation histories remain recovery-dependent.

## Confirmed / evidence-backed findings

| ID | Series / issue / exact unit | Severity | Finding / required handling |
| --- | --- | --- | --- |
| VIS-C3-001 | Rex Fleet / I01 / `RF_I01_EDITOR_OPEN` | P1 authority decision | Published editor text calls the officer **Ilyra Venn**, whereas current character data names **Ella Venn**. Establish any approved identity correction before changing any source or using one as canonical. |
| VIS-C3-002 | Backyard Rockets / E02 / `BR_S1E02_EDITOR_OPEN` | P2 provenance | Published combined-edition editor page 023 and current RexPrompt editorial recipe have different approved content and intended staging. Establish which authored edition applies for future export; do not replace either silently. |
| VIS-C3-003 | Vikings 2026 / I01 / `VIK_S1I01_P01..P18` | P2 mapping | 18 current recipe units versus 26 published daily-page images; determine the exact edition-to-script mapping rather than assuming missing artwork or extra pages. |
| VIS-C3-004 | Azure Reach / E01 / `AZR_S1E01_P03` | P2 recipe metadata | Existing validator exposes 10 declared panels versus five panel-plan entries; first reconcile the script with released page geometry and editorial approval. |
| VIS-C3-005 | Backyard Rockets / E02 / `BR_S1E02_EDITOR_OPEN` (candidate page mapping) | P2 local lettering | Low-contrast white paragraph on public `page-023.jpg`; consider lettering-only proof, not art regeneration. |

**Active production-completeness gates established by exact manifests (not proof images never existed):**
- Rex Fleet I03: 5 missing approved entries: `RF_I03_P28`, `RF_I03_P29`, `RF_I03_P30`, `RF_I03_EDITOR_ENDMATTER`, `RF_I03_EDITOR_CLOSE`.
- Vikings 2026 E02: 19 missing approved entries: `VIK_S1E02_P05`–`VIK_S1E02_P23`.
- Stardust Station E02: 21 missing approved entries: `SDS_S1E02_COVER`, `SDS_S1E02_EDITOR`, `SDS_S1E02_P01`, `SDS_S1E02_P05`, `SDS_S1E02_P07`–`SDS_S1E02_P22`, `SDS_S1E02_TEASER`.

## Visual samples / qualified passing findings

- **Azure Reach E01:** pages 002–003, 009–010 and 018–019 share recognizable Maya/model, facility palette and ensemble (observed); exact dialogue not compared.
- **Backyard Rockets E01:** pages 010–011 keep the central woman's sidecut and consistent Mojave hardware language (observed); the combined E02 pages 022–024 and 033–034 were inspected separately.
- **Rex Fleet E01:** pages 012–013 and 017–018 maintain the council-room geography, Fleet navy/gold uniforms and central female officer's facial identity. Pages 001–003 also visually sampled; full issue not passed.
- **Stardust E01:** pages 002–003, 010–011 and 021 retain the established colorful crew and station design. Page 020 is present but did not successfully render through this inspection tool in one attempt, so is excluded from passing scope.
- **Vikings E01:** pages 010–011 and 019–020 preserve rooftop setting and two foreground character identities; pages 001–003 were also inspected. Edition-to-recipe mapping remains unresolved.

## Published-image geometry and structural QC

Independent `StarSplitterVisions` PR #141 scans the actual 157 released JPEG page files (136 bitwise distinct files; 21 intentional repeats in the Backyard Rockets combined edition). It reports no missing published daily-page paths or missing linked collected PDFs.

**Exact released-image source issues (P2 source inspection; do not replace artwork without approval):**
- Rex Fleet Issue 1: `page-002.jpg`, `page-004.jpg`, `page-009.jpg`, `page-011.jpg`, `page-015.jpg` have no terminal JPEG EOI marker.
- Stardust Station Issue 1: `page-020.jpg` lacks EOI. That same original file did not render through the image-inspection bridge on one attempt. This warrants a targeted source decode and PDF comparison, not an assumption that canon is invalid.
- Azure Reach Issue 1, Rex Fleet Issue 1, and Vikings Issue 1 contain mixed page-image geometries. Digital previews should not be mistaken for print-native masters. Resolve resolution and consistency through the separately owned issue-mastering workflow.

These six page-path findings are individually recorded with evidence and required correction in the machine-readable visual review manifest.

## Series-by-series disposition

| Series | Registered units | Keeper refs | RexPrompt approved drafts | Current QC disposition |
| --- | ---: | ---: | ---: | --- |
| Azure Reach | 150 | 2 | 11 | E01 sampled, P03 script panel discrepancy; E02 11 stored PNGs uninspected; later issues unreviewed |
| Backyard Rockets | 178 | 2 | 0 | Released E01/E02 selected pixels inspected; combined reprints intentional; E02 editorial discrepancy; E03–E08 not visually inspected |
| Division Threshold | 228 | 6 | 0 | Exact source recipes load; Keeper character sources indexed; Project-source images outside approved-draft manifest uninspected |
| Echoes of a Forgotten War | 157 | 17 | 0 | Character/location pack indexed; no original image pixels inspected; image recovery required |
| Low Tide Signal | 199 | 0 | 0 | Recipe inventory passes; historical generated pixels and visual canon must be recovered/verified |
| Rex Fleet | 314 | 4 | 76 | E01 released pages sampled; E01/E02 draft manifests structurally complete; E03 5-unit recovery gate; E04–E12 unreviewed |
| Rex Fleet Academy: Anomalies | 24 | 0 | 0 | Issue 1 recipes load; images/references unreviewed |
| Rex Fleet Academy: Between Beacons | 27 | 0 | 0 | Registered configurations load; images/references unreviewed |
| Rex Fleet Academy: Core Worlds | 24 | 0 | 0 | Issue 1 recipes load; images/references unreviewed |
| Rex Fleet Academy: Doctrine of Many Crowns | 24 | 0 | 0 | Issue 1 recipes load; images/references unreviewed |
| Rex Fleet Academy: Navigating Mirrorfold | 24 | 0 | 0 | Issue 1 recipes load; images/references unreviewed |
| Rex Fleet Academy: Physics of the Lattice | 24 | 0 | 0 | Issue 1 recipes load; images/references unreviewed |
| Rex Fleet: Aegis Vigil | 24 | 0 | 0 | Issue 1 recipes load; images/references unreviewed |
| Rex Fleet: Crimson Warden | 28 | 0 | 0 | Issue 1 recipes load; images/references unreviewed |
| Rex Fleet: Ghostwind Arrow | 22 | 0 | 0 | Issue 1 recipes load; images/references unreviewed |
| Rex Fleet: Glass Horizon | 24 | 0 | 0 | Issue 1 recipes load; images/references unreviewed |
| Rex Fleet: Slip Knife | 22 | 0 | 0 | Issue 1 recipes load; images/references unreviewed |
| Rex Fleet: Stormwell Archive | 22 | 0 | 0 | Issue 1 recipes load; images/references unreviewed |
| Rex Fleet Academy: Reach and Resolve | 24 | 0 | 0 | Issue 1 recipes load; images/references unreviewed |
| Shattering | 150 | 0 | 0 | 7 registered configurations load; original IMG material not visually inspected in this audit |
| Stardust Station | 249 | 2 | 4 | Released E01 sampled; E02 4 stored PNGs uninspected, 21 book units without draft entries; later issues unreviewed |
| The Sun Comes Through (musical) | 16 | 0 | 0 | Non-comic: comic image/lettering QC not applicable; included to avoid inventory omission |
| Sunforge Outlaw | 296 | 6 | 0 | Character/world concepts indexed, 12 issues scripted; artwork not inspected |
| Vikings 2026 | 296 | 2 | 22 | E01 released sample passes limited identity/staging; 18 current recipes vs 26 publication pages; E02 19 book units not in draft manifest |

## Current book-inventory boundary

The book-export lane has since registered **74** source-verified issue inventories. The expanded inventory has **1,796** units not recorded as approved RexPrompt draft images, of which **45** are currently actionable approved-production recovery gaps in Rex Fleet I03, Vikings E02 and Stardust E02. The remaining **1,751** are unapproved production backlog/unknown external-art status—not defects and not evidence that the user never generated those images. Historical recovered art and released pages must be reconciled before classification changes.

## All 126 registered production issues

The **machine-readable output** of `node tools/build_cross_series_quality_register.cjs` enumerates all 126 show IDs with exact script unit counts, per-issue draft coverage, Keeper coverage, candidate recovery IDs, issue-specific findings, book inventory gaps, and exact evidence URLs. No unreviewed issue is silently labeled passed.

## Defect classification and protection

- `P1-authorship-decision`: published-versus-current canonical source conflict requiring approved identity/editorial decision, **not** automatic repair.
- `P2-recipe` or `P2-provenance`: metadata and edition mapping issue, not a claim the released image is wrong.
- `P2-local`: bounded visual defect proposal; preserve the art and seek approved lettering-only correction.
- `MISSING_APPROVED_RECORD`: known book inventory unit lacks a RexPrompt approved-draft entry. Recover original artwork or establish its true production status; never invent replacement pixels or silently mark approved.
- All other registered units: `UNREVIEWED` or `UNVERIFIED_EXTERNAL_ASSETS`, not failed.

**Required separate visual work:** conduct systematic original pixel-to-recipe and visual-reference comparison for every unit; check names, faces, ship silhouettes, faction uniforms, spatial/prop state, panel-to-panel storytelling, every exact balloon, palette and mastered resolution. Issue approval must remain separate from technical storage check.
