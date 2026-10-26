# Rex Fleet Issue 2 composition: single source of truth

A historical integration introduced 19 editorial layouts into `pages_i02.json` while the current assembler already loads a strict ID-merge overlay, `page_layout_i02.json`, later synchronized by PR #291. Both sets of 19 layouts were compared and found byte-equivalent as parsed JSON before this cleanup.

To avoid two competing authorities, `pages_i02.json` now holds only source story and script material; `page_layout_i02.json` owns the 19 editorial compositions. The production manifest's strict overlay merge remains unchanged.

The updated `tools/test_issue2_layout_rollout.cjs` verifies the registered overlay, one-to-one page coverage, absence of source-embedded duplicate layouts, and that the assembled composition leaves panel plans, dialogue and continuity unchanged.

No approved art, page content, publication state, dialogue or page order was changed.
