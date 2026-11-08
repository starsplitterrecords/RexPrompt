# Issue reading order and editorial production roles

## Authority

The canonical publishing hierarchy is Universe → Series → Issue/Chapter → Production Unit. Distinct production series remain distinct: **`rex-fleet` and `rex-fleet-full-performance` must never be merged**.

- `data/shows.json` and the registered source recipes establish the available production units and their order.
- `production/book-manifests.json` is the **curated complete-book reading order** where one exists.
- `production/issue-structure.json` is the generated, evidence-labeled registry of cover, cast, editorial, teaser, extra end matter, and interstitial roles. It is not a new source of story or an approval to release.
- `production/book-export-coverage.json` records approved source image coverage independently of creative quality, mastery, and release state.
- StarSplitterVisions `main` remains the authority for anything already published.

## Meaning of the structural fields

`readingOrder: curated-complete-book` means the exact source-backed book sequence has been verified and can be used as the issue export inventory. `source-order-only` means the registered recipe sequence has been preserved, **not** that cover/editorial/cast pages exist or that release can proceed.

`specialUnits` gives the exact existing unit ID, 1-based position, editorial role, and evidence source. **The cover must be part of the issue assembler's source sequence, in position 1; book audits must not prepend it from a separate shelf.** Source files such as `covers.json` may be shared internally, but `data/shows.json` must register only the issue, not a standalone cover selection. Do not invent covers or any other pages to satisfy a template.

Embedded comic pages keep their existing IDs. In Vikings 2026!, for example, P01 is the cover, P02 is an editorial intro, and the last numbered page is a closing editorial or teaser. This is source-derived classification, **not** a rename, resequence, or new page.

Backyard Rockets and Echoes of a Forgotten War each have eight registered, cover-first issue selectors. The original season selectors remain as non-book source archives, not extra published issues. Each episode's cover is baked into the source sequence of the real issue selector.

## Cast-page options

A cast unit is distinct from an ordinary story page. The browser review PDF/ZIP interface permits explicit omission of a cast page, with a distinct `-NO-CAST-DRAFT` filename and `complete: false` in the export manifest. The offline exporter offers the same **review-only** behavior with `--omit-cast-for-review`, provided the source-evidenced issue structure marks the unit as cast. The full curated issue still includes cast pages by default. **Release preparation cannot silently omit them**; any canonical release-order change must be a separate approved editorial decision.

## Refresh and validation

The current `refresh-production-dashboard.yml` workflow runs:

1. `node tools/audit_portfolio_books.cjs --write` to regenerate the book manifest, issue structure, book-export coverage, and human report from current registered sources and approved original images.
2. `node tools/test_book_export_manifest.cjs` to verify all curated orders and source-backed special roles.
3. `node tools/audit_all_series_production.cjs --out production/portfolio-recipe-inventory.json` and the raster source inspection.
4. Dashboard validation and an atomic branch commit of the derived snapshots.

The read-only book audit workflow checks these artifacts after committed changes. Neither successful data validation nor an approved draft count establishes artistic acceptance, print-ready mastering, or a public release.

## Unresolved content versus resolved data defects

A missing cover, unapproved art, no curated order, and missing publication metadata are actual production prerequisites. Record them explicitly rather than supplying new creative content without approval. A stale snapshot, unidentified embedded editorial page, or hidden season issue is a data/automation defect and should be fixed mechanically.

## November 8, 2026 cover-source completion

At the initial cover-source completion checkpoint, the portfolio had **114 registered, curated complete-book issue orders** and **154 assembler configurations** across **25 production series**. All 114 books had a cover ordered first, but 29 redundant cover-only selectors still existed in the registry. Those were retired in the following normalization.

- Existing `Echoes of a Forgotten War` covers (`EFW_S1E01_COVER` through `EFW_S1E08_COVER`) were reused without altering their content; the eight new issue selectors assemble each cover followed by that episode's original story units.
- `Backyard Rockets` retains its complete Season 1 source and now has eight issue-level selections and eight new source-grounded commercial-cover recipes. The existing **published** Issue 1 and Issues 1–2 combined edition covers in StarSplitterVisions remain authoritative and must **not** be overwritten or assumed to match future independent issue covers.
- `Rex Fleet — Full Performance` has its own twelve distinct new cover recipes, registered ahead of its existing editorial and story pages. These are **not** regular Rex Fleet cover variants or merged production records.
- Twelve separate Rex Fleet/Academy single-issue stories have source-grounded cover recipes registered first. No original authored story page is removed or rewritten.
- For newly authored covers, `scene.generationLine` is a cover-scoped override; the original `show.generationLine` still applies to every unchanged interior story page.

**Source readiness is not image readiness.** These 32 newly authored cover recipes are original *production prompts*, not approved rendered image files. The cover artwork must pass the Comic Production Continuity Skill's actual-pixel reference gate, generation, artistic review, approval, and mastering before a collected book can be released. The existing book-export coverage report independently measures approved image completeness. As of this repair, that report flags **110 of 114** curated books as missing one or more approved image binaries; four have full approved-draft coverage, which itself does not assert mastering or release approval.

The two legacy season selectors (`backyard-rockets-s1` and `echoes-forgotten-war-s1`) are retained as aggregate working sources and are **not** additional books. Their real eight-issue selectors are the authoritative book-unit production selections.

## November 8, 2026 — no standalone cover configurations

The source registry is normalized to **125 configurations: 114 curated issues plus 11 non-book technical/season/editorial selections**. The **29 cover-only selectors** formerly included in the 154-configuration registry have been permanently archived, unchanged, in `production/migrations/retired-cover-selectors-2026-11-08.json` for historical provenance. No raw cover recipes, original approved images, assets, character references, or dialogue files are deleted.

The 29 retired configurations covered **46 distinct cover recipes**. Of those, **38 covers have now been baked into their issue's `scenesFiles` before the existing story source**: six Shattering issues, eight Division Threshold issues, seven Low Tide Signal chapters, six Azure Reach issues, ten Stardust Station issues and one Between the Beacons issue. The other **eight Echoes of a Forgotten War covers were already embedded in their individual issue source sequences**. All 46 cover IDs remain preserved and issue-owned.

The cover is now a normal **first production unit of the issue assembler**, not an audit-time supplement, a separate menu entry, or an independently tracked release. The book audit explicitly rejects attempts to create a complete book by finding a cover outside the registered issue source. Regression tests assert that the retired cover IDs are found in exactly one issue each and occupy position 1. A shared `covers.json` source file remains permitted as an internal storage detail, never as a separate production configuration.

