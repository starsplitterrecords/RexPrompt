# Cross-series recipe-scope reconciliation

This change selectively recovers the still-unmerged page-scoped sanitation work from PR #273 against current main. It adds strict recipe-scope overlays for Backyard Rockets Issues 3–8 and Stardust Station Issue 3, page-local policies for Division Threshold Issues 1–8, and human-readable labels for existing setting shelf records. Scripted panels, dialogue, story action, current composition overlays, artwork and released issues must remain unchanged.

Integration rules: preserve the current Stardust Issue 3 density overlay, which the old branch predates. Division Threshold's 21 story and 20 dialogue polish changes were mechanically matched, page for page, to the historical flattened package (204/204 identical effective page objects). The effective polish is now compiled directly into the 8 flat page files and the obsolete assembler overlay registrations removed. The original overlay files remain in Git for provenance; no dialogue, summaries, panel plans or effective story content were lost. Preserve contemporary Rex Fleet, Azure, Vikings and other later sanitation work.

Validation: `node tools/test_recipe_scope_rollout.cjs`, existing prompt assembly and series validators. Changes to rendered image quality still require actual image inspection; this is a recipe-scope regression, not an image approval.
