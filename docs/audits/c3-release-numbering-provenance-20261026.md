# C3 release numbering to RexPrompt recipe mapping — confirmed and qualified
Date 2026-10-26. Read-only continuity/provenance analysis based on direct published pixels and live RexPrompt page-source data.

## Rex Fleet Issue 01
The public daily-page image set contains 19 JPEGs. The first published JPEG, `page-001.jpg`, is an editorial page, consistent with `RF_I01_EDITOR_OPEN`. The 18 story JPEGs therefore occupy `page-002.jpg`–`page-019.jpg` and correspond **in apparent script sequence** to `RF_I01_P01`–`RF_I01_P18` (published number = script story page number + 1).

Independent content alignment:
- Released `page-010.jpg` shows Jex covertly handing Shard captain Billie route/favor information, corresponding to current **`RF_I01_P09`** summary/intent.
- Released `page-016.jpg` shows Auric Verge commerce, civilian crossing autonomy, maps and Fleet support discussion, corresponding in broad plot function to current **`RF_I01_P15`**.
- Thus preliminary soft-lettering flags previously listed against released `page-009.jpg` and `page-015.jpg` **must not be assigned to `RF_I01_P09` and `RF_I01_P15` respectively**. Those published files are *likely* `RF_I01_P08` and `RF_I01_P14`. The reader-facing JPEG paths are exact even when recipe assignment remains subject to released-edition authoring history.
- The current full-book manifest includes cover, opening editorial, cast page, 18 story pages, closing editorial. The 19 public daily images are not the complete PDF inventory, so do not assert missing published bookends without PDF inspection.

## Vikings 2026 Issue 01
The live `data/shows/vikings-2026-s1/pages_i01_reordered.json` contains **18 numbered `VIK_S1I01_P01`–`P18` records**. The published daily image series has **26 numbered JPEGs**. Released P01 is an illustrated cover, P02 an editorial notice; both also correspond to current first two production units. P03–P15 plot sequence and characters broadly align by same numeric ID (e.g. P07 harbor orange synthetic cord and P14 DTI thumbprint).

**First clearly observed divergence occurs at released P16:**
- Current `VIK_S1I01_P16` describes ONE FULL-PAGE splash at DTI glass doors at dusk, no way back / always way back / not this time.
- Published `page-016.jpg` has THREE rooftop panels of paperwork, city roof hardware and additional warriors.
- Published P17–P26 extend this rooftop / municipal interference plot and closing credit, with no matching `P19`–`P26` entries in the current 18-record issue package. Later issue content may have been intentionally condensed/rewritten in RexPrompt after release; no such revision approval has been verified.

**Classification:** blocker for **production-to-published canon/version provenance**, not a defect authorizing redrawing or deletion of released image P16. Recover versioned original release scripts, verify creative decisions, then preserve released continuity in any follow-on story.

## Azure Reach and Stardust Station Issue 01
- Azure Reach has 22 published story-page JPEGs and 22 current `AZR_S1E01_Pxx` story IDs, with cover/intro/outro maintained as separate bookend units. Direct content comparisons support same-number story mapping. Released P18 versus current P18 is therefore a credible scene-fidelity mismatch (separate detailed defect record).
- Stardust Station has 22 published story-page JPEGs and 22 current `SDS_S1E01_Pxx` story IDs, plus separate editorials/covers. Exact mapping of flagged P08 and P17 is supported by scene content.
- Backyard Rockets combined edition has 47 published JPEGs comprising reused Issue 1 pages and later Issue 2; source `backyard-rockets-s1` is a multi-issue assembler with encoded episode overlays. Do not assign `page-###` to arbitrary RexPrompt recipe IDs until the original edition build mapping is recovered.

## Canon and safety
Live RexPrompt recipes may have changed since the public book was approved. Where they conflict, retain StarSplitterVisions released visual canon as historical authority, and record the production version mismatch for reconciliation; do not silently “correct” released images to current scripts. This mapping supersedes tentative numeric-ID assumptions in older audit checkpoints.
