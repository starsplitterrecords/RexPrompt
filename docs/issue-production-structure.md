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

`specialUnits` gives the exact existing unit ID, 1-based position, editorial role, and evidence source. A cover can be `ordered`, `available-in-separate-shelf`, or `not-established`. A cover in a separate shelf is **not** silently added to a book. Do not invent a cover, cast page, editor's note, or teaser merely to satisfy a template.

Embedded comic pages keep their existing IDs. In Vikings 2026!, for example, P01 is the cover, P02 is an editorial intro, and the last numbered page is a closing editorial or teaser. This is source-derived classification, **not** a rename, resequence, or new page.

Episode source sequences inside Backyard Rockets and Echoes of a Forgotten War are indexed separately with `selectorRegistered: false`. These entries are **not new assembler configurations** and they are not published issues. Echoes' separate cover shelf is reported as available, but not yet book-ordered.

## Cast-page options

A cast unit is distinct from an ordinary story page. The review PDF/ZIP interface now permits explicit omission of a cast page, with a distinct `-NO-CAST-DRAFT` filename and `complete: false` in the export manifest. The full curated issue still includes cast pages by default. **Release preparation cannot silently omit them**; any canonical release-order change must be a separate approved editorial decision.

## Refresh and validation

The current `refresh-production-dashboard.yml` workflow runs:

1. `node tools/audit_portfolio_books.cjs --write` to regenerate the book manifest, issue structure, book-export coverage, and human report from current registered sources and approved original images.
2. `node tools/test_book_export_manifest.cjs` to verify all curated orders and source-backed special roles.
3. `node tools/audit_all_series_production.cjs --out production/portfolio-recipe-inventory.json` and the raster source inspection.
4. Dashboard validation and an atomic branch commit of the derived snapshots.

The read-only book audit workflow checks these artifacts after committed changes. Neither successful data validation nor an approved draft count establishes artistic acceptance, print-ready mastering, or a public release.

## Unresolved content versus resolved data defects

A missing cover, unapproved art, no curated order, and missing publication metadata are actual production prerequisites. Record them explicitly rather than supplying new creative content without approval. A stale snapshot, unidentified embedded editorial page, or hidden season issue is a data/automation defect and should be fixed mechanically.
