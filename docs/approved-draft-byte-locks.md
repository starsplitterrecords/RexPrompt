# Approved production draft byte locks

The portfolio regression suite protects **every approved production draft** in `production/drafts/manifest.json` by comparing the saved image file to its content-addressed Git blob SHA-1 (the exact SHA-1 algorithm Git uses for blob objects). This detects accidental replacement of a valid PNG/JPEG at the same path, not merely broken headers or lost recipe registration.

The baseline `tools/fixtures/approved-draft-blob-locks.json` is a **reviewed lock**, not an independent approval system. When production recovery adds a genuinely newly approved image, or intentionally replaces an approved image with explicit authorization, its workflow must update the baseline in the same PR, record the approval evidence, and run the entire portfolio regression. The checker intentionally fails on untracked approvals, stale lock keys, altered paths, or changed bytes.

This guard does not assess image composition or likeness, nor does it govern already published binary assets in the separate StarSplitterVisions release repository. It also does not confer creative approval on previously indexed assets.
