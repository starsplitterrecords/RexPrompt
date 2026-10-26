# Portfolio assembler regression gate

Runs the **actual** RexPrompt browser `loadShow` and `assembleScene` functions in a Node 22 VM with local file-backed `fetch`. Assembles every recipe in every registered configuration, rather than accepting a green build based on selected issues. Inspect the GitHub Actions `portfolio-regression-report` JSON artifact for exact per-configuration coverage and risk lists.

Structural assertions cover scene loading (arrays, object maps, gzipped/base64 overlays, replacement and strict merges), unique IDs, panel/layout validation, dialogue text preservation, speaker-panel mapping, visible reference lists, sanctioned prompt suppression, and protection of approved draft recipe IDs. Negative mutation tests represent known IMG failure classes: high dialogue density, misplaced dialogue mapping/balloon speaker, stale setting suppression, irrelevant visual character references, malformed strict merges, incorrect layout references, and lost dialogue indices.

Strong distinction: high density or weakly mapped historical dialogue is **reported** as a risk, not automatically rewritten or classified as script failure. No artwork files, story text, original panel plans or publishing manifests are changed. The test cannot prove generated images depict correct scenes, physical balloon tails, palette, likeness or print fidelity.

Strict scene merge now rejects orphan/duplicate IDs rather than quietly appending stray story pages. Existing strict overlay data should be regression-verified before merging.

CI triggers on the entire show tree and assembler changes, with `workflow_dispatch` for audit on demand.
