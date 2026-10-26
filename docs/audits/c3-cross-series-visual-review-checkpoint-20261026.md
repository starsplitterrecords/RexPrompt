# C3 cross-series visual audit — evidence checkpoint (2026-10-26)

## Audit authority and scope
This is a **read-only progress and defect register**. Released art in `starsplitterrecords/StarSplitterVisions` remains visual canon; approved corrective references override only their intended element. RexPrompt assembled recipes control production intent. Uninspected material is not marked as passing. No artwork or source data was altered.

Audit source: StarSplitterVisions `main`, canonical site asset paths; exact individual page paths below. Original JPEG pixels were successfully retrieved through GitHub base64 file readback after stripping line breaks and inspected in active multimodal context.

## Visually inspected: provisional findings, not whole-issue approval

| Series | Issue | Released image / recipe mapping | Evidence and assessment | Review status |
|---|---|---|---|---|
| Vikings 2026 | 01 | `page-001.jpg`, cover (recipe ID needs mapping) | Native pixels inspected. Two contrasting male warrior designs and municipal waiting room establish released appearance. | Cover-only visual reference inspected; not full lettering/recipe fidelity audit |
| Vikings 2026 | 01 | `page-002.jpg`, editorial (recipe ID needs mapping) | Native pixels inspected. Embedded cover thumbnail uses same visual as page 001; readable designed editorial page. | Editorial spot-check; exact text vs production script not yet checked |
| Vikings 2026 | 01 | `page-003.jpg`, story image (recipe ID needs mapping) | Native pixels inspected. Short-haired warrior and blond face-painted warrior appear consistent with cover in broad distinguishing traits; longship bow, shield and sea staging observable. | First-story-page visual continuity spot-check only; exact cast and staging vs assembled recipe not yet checked |
| Azure Reach | 01 | `page-001.jpg` | Native pixels inspected. Multi-panel aquarium entrance scene and dialogue are legible at inspection resolution; person and location identities need reference and adjacent-page comparison. | Single page inspected, no whole-sequence approval |
| Rex Fleet | 01 | `page-001.jpg` (editorial) | Native pixels inspected. Typographic introductory page; no character/ship continuity can be assessed from this page. | Editorial page inspected, exact copy pending cross-check |
| Stardust Station | 01 | `page-001.jpg` | Native pixels inspected. A crowded ensemble sequence with multiple character models, readable balloon text, and five numbered panels observed. Requires precise recipe, character reference and adjacent-page checks before quality pass. | Single page inspected, not approved by audit |

Evidence paths use `sites/visions/public/images/pages/<series>/issue-01/page-###.jpg` in `starsplitterrecords/StarSplitterVisions`.

## Cross-edition provenance finding

| Register ID | Series / issue | Evidence | Severity / disposition | Required action |
|---|---|---|---|---|
| C3-BYR-CROSS-001 | Backyard Rockets, Issue 01 vs Issue 02 combined edition; pages 001–021 | All 21 JPEG Git blob SHAs from `issue-01/page-001.jpg` through `page-021.jpg` equal their same-numbered `issue-02` counterparts. Release metadata explicitly titles Issue 2 `Issues 01–02: Combined Edition`. | **Intentional reuse candidate; NOT classified as defect** | Verify reading order at transition from page 021 to 022 and that combined PDF and series descriptions agree. Protect reused art from duplicate-driven replacement. |

## Confirmed portfolio audit boundaries / recovery register

- RexPrompt mechanical cross-series audit: 126 configurations, 2,546 assembled units across 24 series, 113 draft records, 36 Keeper references at the earlier verified checkpoint. This does not establish actual image completeness.
- Released page-image inventory: Azure Reach I01 (22 files), Backyard Rockets I01 (21), Backyard Rockets combined I02 (47), Rex Fleet I01 (19), Stardust Station I01 (22), Vikings I01 (26); source `StarSplitterVisions/main`.
- Actual source-pixel review completed here for **6 individual published page-image files** only. The remaining **151 published page entries** were **not yet visually inspected** in this checkpoint. No other series' issue imagery has been visually approved by this checkpoint.
- The 21 Backyard Rockets image duplicates across the two releases reflect a deliberately combined edition and are not counted as 21 defects.
- Missing Rex Fleet Issue 3 draft units previously identified by the book-manifest check: `P28`, `P29`, `P30`, `EDITOR_ENDMATTER`, `EDITOR_CLOSE` (exact RexPrompt recipe IDs must be read from the live complete-book manifest before issue-specific issue creation); do not assume no source was generated in IMG.
- For unrepresented approved-draft series, search historical IMG, Project-source artwork, Visions released assets and external reference packs before declaring anything missing.
- **Not verified:** precise script-to-balloon transcription, speaker assignment, character identities against all canonical references, ship/faction/prop continuity between every pair of pages, image mastering/resolution adequacy, full-PDF inclusion and trim, and historical IMG-only artwork without pixel readback.

## Next gates
1. Establish released-page to exact RexPrompt recipe ID mapping per edition.
2. Inspect all remaining released pages sequentially and compare each applicable page with neighboring art and original assembled recipe; record exact series/issue/recipe ID, severity, evidence URL, and smallest correction.
3. Use IMG Binary Readback for approved drafts and Keeper references; never infer visual approval from manifests or file signatures.
4. Continue into unreleased issues once their images can be retrieved. Preserve already-approved artwork. No changes to artwork are authorized by this document.
