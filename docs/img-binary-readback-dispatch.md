# IMG binary readback — universal dispatch

Run the `IMG Binary Readback` GitHub Actions workflow in RexPrompt at the required repository revision. Select `draft` or `reference` and supply the **exact manifest key** in `production/drafts/manifest.json` or `production/references/reference-keeper-manifest.json`. No arbitrary path input is accepted.

The artifact contains byte-exact `original.png`, `original.jpg`, or `original.webp` and `readback.json` with the exact source path, SHA-256, and Git blob SHA. Download through the GitHub Actions artifact interface, extract the original binary and inspect the **actual pixels in the IMG conversation**. Artifact metadata or a hash alone does not satisfy visual-continuity inspection.

Run `node tools/test_img_readback.cjs` for offline parity and rejection tests. The workflow never modifies an approved asset, manifest, or release. If the artifact cannot be loaded into current multimodal context, do not proceed with continuity-sensitive generation.
