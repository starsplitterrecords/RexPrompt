# Exact IMG binary readback — operational workflow

The existing **IMG Binary Readback** GitHub Action retrieves either an **approved production draft** or a **Reference Keeper image** from its canonical manifest, copies its exact original bytes, and attaches `readback.json` with SHA-256 and Git blob SHA.

1. Open **Actions → IMG Binary Readback → Run workflow** in RexPrompt at the desired revision.
2. Choose `draft` or `reference`, and supply the **exact full manifest key** from `production/drafts/manifest.json` or `production/references/reference-keeper-manifest.json`.
3. Download the artifact, extract the unchanged image, and verify its digest against `readback.json`.
4. Bring the extracted image **pixels** into the active IMG session; file names, hashes, descriptions and prior-chat recollections are not visual inspection.
5. Use the verified original only for its approved role; do not promote a draft to released canon or treat readback as mastering approval.

The exact-byte readback implementation is in `tools/prepare_img_readback.cjs`. Its existing integration test `tools/test_img_readback.cjs` exercises two approved production images, two Keeper reference images, hash identity, and rejection of invalid keys. The targeted `Validate IMG Binary Readback` workflow runs that regression automatically.

For persistence, follow the atomic image + approved-draft manifest transaction in `production/drafts/README.md`. A successful write response alone is insufficient; verify that the committed manifest resolves and that its **actual image binary** can be retrieved intact. Artifacts are temporary transport, not durable archives.
