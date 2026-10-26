# Portfolio production dashboard — source, semantics, and operations

**Dashboard:** `production-dashboard.html`, linked from RexPrompt's main assembler.

## Evidence and authority

- `data/shows.json` contains **show configurations**, not a count of pages or individual generated production units.
- `tools/audit_all_series_production.cjs` reconstructs **all 126 registered configurations** from the same base scenes, encoded gzip-base64 overlays, replacement/merge rules, exclusions, dialogue overlays, and ID filters as the browser assembler. Its exact recipe IDs and error report are cached as `production/portfolio-recipe-inventory.json`.
- The displayed **assembled recipe denominator** is the number of distinct reconstructed IDs. Where `production/book-manifests.json` defines a complete book, that curated inventory controls the *full-book denominator* (including cover, editorial, cast, and back matter), even if the corresponding configuration is missing.
- `production/drafts/manifest.json` establishes a specific **approved draft record**, not independent artistic, source-quality, mastering, or publication approval.
- `production/references/reference-keeper-manifest.json` counts Keeper images, not every reference in IMG projects, Project files, personal Library, visual packs, or released canon.
- `production/portfolio-source-quality.json` records intrinsic raster pixel dimensions, format, color-profile indicators, hashes, and directly tested binary integrity from **all indexed approved draft binaries**. Its observations do not establish 300-DPI suitability for an unspecified trim size, artwork correctness, color-grade acceptance, or mastering.
- `production/portfolio-quality-evidence.json` holds scoped, source-linked findings and unresolved original-asset recovery leads. An unspecified series/issue has unknown quality/recovery status; it is never treated as passing automatically.
- `production/released-links.json` points from selected recipe IDs to released Visions images where such a link exists; it is not a complete published-page inventory.
- **StarSplitterVisions** series JSON is authoritative for collected-edition publication metadata, matched *only by series and explicit issue number*. A PDF release record is not independent evidence that an unpublished RexPrompt page has been mastered.

### Distinct states

- **Unknown/unavailable:** no usable source evidence or a publishing metadata fetch failed.
- **Not indexed:** recipe/book unit lacks an approved draft *in RexPrompt*. This is **not proof the image was never generated or is missing outside RexPrompt**.
- **Recovery candidate:** scoped historical asset evidence exists, but original bytes, approval, or native-resolution suitability remain to be reconciled. Do not promote automatically.
- **Approved draft indexed:** manifest marks `approved-production-draft`; visual/lettering and mastering approval remain separate.
- **Native review required:** an explicit source-quality finding establishes a concern.
- **Mastered:** reserved for separately recorded, approved mastering evidence. No row may enter this state just because it has adequate pixel dimensions or an approved draft manifest.
- **Inventory complete, not mastered:** all curated book unit IDs have approved draft records, but there is no final grade/export release approval.
- **Published edition recorded:** an authoritative StarSplitterVisions collected-edition record exists with exact issue-number match. Historical draft coverage remains independent.

Issue drill-down shows exact IDs, editorial slots, known recovery candidates, approved image paths, source-file evidence, collected edition records, image native dimensions/profile, and image links (where established). Series without current drafts and books with no registered show configuration are **retained**.

### Keeping it current

When production recipes, overlays, approved-image manifests, reference manifests or curated books change, regenerate both read-only derived snapshots **from current main/branch**:

```bash
node tools/audit_all_series_production.cjs --out production/portfolio-recipe-inventory.json
node tools/build_portfolio_source_quality.cjs --out production/portfolio-source-quality.json
node tools/test_production_dashboard.cjs
```

The dashboard CI reconstructs and compares the complete snapshots against the real files and will fail on a stale inventory, including newly added editorial pages or new book manifests. The files are data caches, **not** a replacement for the assembler. Do not edit snapshot counts manually. If another chat changes `production/book-manifests.json` concurrently, rebase and regenerate the snapshots before merging.

### Verification

1. Run `node tools/test_production_dashboard.cjs` and the all-series audit in GitHub Actions.
2. Verify 126 registered configurations, 24 series (or current live values), real compiled recipe counts, source raster inspection, zero-draft series, book-only issues, and correct scope of published editions.
3. Confirm Rex Fleet Issue 3 retains all 35 required book slots, including the five not yet indexed as approved drafts; no absent art is described as definitively lost.
4. Review the main dashboard in a browser and open several exact recipe IDs; verify labels, links, reading order and the user-visible state separation.
5. Check the live Pages deployment responds with current `production-dashboard.html`, `production-dashboard-core.js`, both production snapshots and fresh `data/shows.json`. Do not call the deployment visually verified solely because GitHub Actions passed.

The dashboard is a **read-only operational accounting tool**. It never approves, regenerates, masters, exports, or publishes artwork.
