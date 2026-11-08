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

The portfolio now has **114 registered, curated complete-book issue orders** and **154 assembler configurations** across **25 production series**. The issue-structure audit identifies a cover ordered in position 1 for **all 114**. This closes the previously tracked **8 shelf-only cover integrations** and **32 absent cover-recipe definitions**.

- Existing `Echoes of a Forgotten War` covers (`EFW_S1E01_COVER` through `EFW_S1E08_COVER`) were reused without altering their content; the eight new issue selectors assemble each cover followed by that episode's original story units.
- `Backyard Rockets` retains its complete Season 1 source and now has eight issue-level selections and eight new source-grounded commercial-cover recipes. The existing **published** Issue 1 and Issues 1–2 combined edition covers in StarSplitterVisions remain authoritative and must **not** be overwritten or assumed to match future independent issue covers.
- `Rex Fleet — Full Performance` has its own twelve distinct new cover recipes, registered ahead of its existing editorial and story pages. These are **not** regular Rex Fleet cover variants or merged production records.
- Twelve separate Rex Fleet/Academy single-issue stories have source-grounded cover recipes registered first. No original authored story page is removed or rewritten.
- For newly authored covers, `scene.generationLine` is a cover-scoped override; the original `show.generationLine` still applies to every unchanged interior story page.

**Source readiness is not image readiness.** These 32 newly authored cover recipes are original *production prompts*, not approved rendered image files. The cover artwork must pass the Comic Production Continuity Skill's actual-pixel reference gate, generation, artistic review, approval, and mastering before a collected book can be released. The existing book-export coverage report independently measures approved image completeness. As of this repair, that report flags **110 of 114** curated books as missing one or more approved image binaries; four have full approved-draft coverage, which itself does not assert mastering or release approval.

The two legacy season selectors (`backyard-rockets-s1` and `echoes-forgotten-war-s1`) are retained as aggregate working sources and are **not** additional books. Their real eight-issue selectors are the authoritative book-unit production selections.


## November 8, 2026 — Cover shelf retirement

**Every cover belongs to its issue configuration.** All 114 curated issue manifests must be recoverable from the issue's own source load, with the cover at position 1. `covers.json` remains a legitimate internal source file and is retained unmodified; a `COVER` assembler configuration is **not** a legitimate separate menu entry.

The 29 original cover-only registry entries were permanently saved, verbatim, in `production/archives/legacy-cover-selectors-20261108.json` before retirement. These archived selectors are **not active shows** and must not be reinstated to inflate series or configuration counts.

The existing cover files are now loaded directly through the appropriate issue selector's `scenesFiles` array (or an issue-local, explicitly filtered cover overlay for other series). All existing cover IDs, artwork, and source instructions remain unchanged. Legacy `scenesFile` fields on these records can remain for old tooling, but `scenesFiles` is authoritative for actual assembly.

A source audit must never synthesize an issue's cover from a separate cover selector or discover one solely in a historical book manifest. Missing issue-local cover or incorrect order is a **blocking production integrity error**. No cover-only configurations may exist in active `data/shows.json`.

