# Cross-series recipe-scope reconciliation

This change selectively recovers the still-unmerged page-scoped sanitation work from PR #273 against current main. It adds strict recipe-scope overlays for Backyard Rockets Issues 3–8 and Stardust Station Issue 3, page-local policies for Division Threshold Issues 1–8, and human-readable labels for existing setting shelf records. Scripted panels, dialogue, story action, current composition overlays, artwork and released issues must remain unchanged.

Integration rules: preserve the current Stardust Issue 3 density overlay, which the old branch predates. Preserve Division Threshold's existing story/dialogue polish source files and assembler overlays; only transplant page-local prompt policy, never the old branch's deletion or rewrite of narrative source. Preserve contemporary Rex Fleet, Azure, Vikings and other later sanitation work.

Validation: `node tools/test_recipe_scope_rollout.cjs`, existing prompt assembly and series validators. Changes to rendered image quality still require actual image inspection; this is a recipe-scope regression, not an image approval.
