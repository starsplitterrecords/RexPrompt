# Cross-series RexPrompt production coverage audit

Run \`node tools/audit_all_series_production.cjs --out all-series-production-inventory.json\` to reconstruct registered recipe IDs using the same scene base, encoded overlay, merge/replace, dialogue overlay, and include-pattern conventions as the RexPrompt assembler. GitHub Actions also produces a machine-readable downloadable JSON artifact.

The audit reports for **every registered configuration** the recipe unit count, its approved draft entries in the same \`seriesId::issueId\` scope, Keeper reference counts, RexPrompt released-link count, and complete-book manifest coverage (when one is explicitly defined). Missing approved drafts are recorded as *unrepresented in RexPrompt draft storage*, never as proof no art exists in IMG, StarSplitterVisions, or elsewhere. Reference Keeper is not the only location of visual canon.

The script checks duplicate assembled recipe IDs and orphan IDs in strict scene overlays, without editing any recipe, manifest, page image, or approval status. Some \`data/shows.json\` entries omit explicit \`seriesId\`; for reporting only, the audit derives those names from \`basePath\` (removing the conventional trailing \`-s1\`). Authored show configuration is not changed.

This is **coverage metadata**, not artistic or release approval. Publication-ready C3 requires original image review for face and setting continuity, panel/dialogue/lettering accuracy, native resolution, color grading, bleed, and the full cover/editorial/story/end matter export. Structural and binary-health checks are separate and run through the existing integrity validators.
