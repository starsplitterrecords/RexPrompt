# Backyard Rockets — complete published-pixel sequence audit

Date: 2026-10-26. Sources: `starsplitterrecords/StarSplitterVisions/main/sites/visions/public/images/pages/backyard-rockets/issue-01/` and `issue-02/`.

## Verified visual inspection scope
- **Combined Issue 02: every original JPEG page, P001–P047, inspected in order** using full file bytes in multimodal context.
- **Standalone Issue 01: 21/21 image files covered** because their respective JPEG Git object SHA values are exactly equal to P001–P021 of the combined edition. This intentional reuse is consistent with release metadata identifying Issue 02 as the “Issues 01–02: Combined Edition”; do not flag the shared bytes as undesired duplicate images.
- These are **visible-pixel layout, character, page-to-page and text readability checks**. Script-to-rendered lettering for every line, canonical visual-reference pack comparison, native/mastering pixel adequacy and PDF page-order inspection have not been completed.

## Broad visual continuity — evidence-limited
Arvin is consistently recognizable by short gray hair, lined face, olive/black technical wardrobe and mechanical hand; Milo by voluminous black curls, facial markings and richly patterned brown jacket; Lucia by asymmetrical black shaved-side haircut, black jacket and blue trim. The Mojave desert rock formations, rocket/tank assemblies, Launch-Shop workspaces, Tethergrid monitoring and improvised relay equipment recur through the two-volume sequence. Character costumes vary with contexts but are mostly recognizable. The launch follows iterative maintenance and failures; combined-edition cover and editorial separate the second arc at P022–P023. The P034 two digital clock readings (10:17:48 and 10:17:16) and 32-second dialogue are internally arithmetically consistent.

## Exact-file defect and review register

| Finding ID | Series / issue / published page | Severity | Evidence | Required correction / verification |
|---|---|---|---|---|
| C3-BYR-001 | Backyard Rockets Issue 01 P001 and combined Issue 02 P001 | **Blocker, confirmed typography** | `page-001.jpg` shows severe intra-word spacing/corrupted kerning throughout the editorial intro, impairing legibility. Image is the exact same Git blob in both editions. | Re-typeset *the existing approved editorial text* from authoritative source. Verify against copy and layout; rebuild both collected issues once the shared page is corrected. Preserve all other page art; no blanket regeneration. |
| C3-BYR-012 | Backyard Rockets Issue 01 P012 and combined Issue 02 P012 | **Local production-layout review** | Large empty white top and bottom regions surround two small center comic strips, unlike P011/P013. | Confirm intended layout and underlying native image, determine whether designed negative space or erroneous letterboxing. No automated artwork replacement. |
| C3-BYR-019 | Backyard Rockets Issue 01 P019 and combined Issue 02 P019 | **Local production-layout review** | Large blank white margins surround a comparatively small sunset image and inset panels with tiny letterforms, unlike adjacent P018/P020. | Compare source resolution/approved layout and correct only if this is unintended; preserve story content. |
| C3-BYR-023 | Backyard Rockets combined Issue 02 P023 | **Advisory, contrast/readability** | Second-story editorial `The Copper Lattice` has small pale copy placed over an illustrated brown/tan landscape in the lower portion, reducing reading contrast. | Review against accessible print and screen typography standards; improve typography/contrast only if user reopens approved editorial. |
| C3-BYR-035-036 | Backyard Rockets combined Issue 02 P035–P036 | **Review, repeated staging** | A long workshop exchange reuses nearly the same three-person staging and central copper coil across many consecutive panels. Dialogue differs and the prop/action appears progressive, so **not a confirmed duplicated-story defect**. | Compare against exact source panels and production-approved pacing before considering composition changes. |
| C3-BYR-041 | Backyard Rockets combined Issue 02 P041 | **Advisory, panel repetition** | A five-panel exchange between Arvin and Lucia keeps almost identical truck-bed staging and camera distance; character placement and costume remain consistent. | Reader-test pacing, but do not redo approved layouts absent demonstrable story/clarity failure. |

### Known protected scope
- First 21 page images reused in combined edition are intentionally shared; do not alter one edition without updating any other release that contains the changed image.
- P022 is the interior Issue 02 cover; P023 is second-part editorial. Neither is an erroneously repeated story page.
- Pages P027 (diagram), P034 (clock comparison), P045–P046 (multi-node network diagrams) use explanatory graphics in narrative context; no evident source-level mathematical or label inconsistency found from these images alone.
- The visible letterform approach shifts from all-capitals in first arc to mixed case in second arc. Whether that was an intentional release-level design change is unverified. Do not normalize automatically.
- No original published image was edited, replaced or promoted to a new approval state.

## Outstanding actions
1. Resolve the confirmed P001 editorial lettering blocker and verify both affected release packages.
2. Compare P012/P019 against approved compositions and inspect native resolution / margins.
3. Reconcile published P001–P047 index with the original issue-level RexPrompt unit IDs and exact panel/dialogue scripts.
4. Compare actual full assembled PDFs against all required story and bookend units; no conclusion of mastering-grade correctness yet.
