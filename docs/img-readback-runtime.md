# Exact IMG readback — operational bridge

The readback procedure in `production/IMG_BINARY_READBACK.md` now has a reusable GitHub Actions implementation.

1. Go to **Actions → IMG Exact Binary Readback → Run workflow** on the required RexPrompt revision.
2. Supply **exact** series, issue, and recipe IDs from `production/drafts/manifest.json` (for example `rex-fleet`, `rex-fleet-i01`, `RF_I01_P01`).
3. Download the `img-exact-readback` Actions artifact, extract it, and inspect the actual PNG/JPEG/WebP pixels in the active IMG session.
4. Compare `readback.json` SHA-256 or Git blob SHA to the extracted original file. Do not treat JSON metadata alone as visual inspection.
5. Keep the extracted image as transient session input; the durable approved source stays in RexPrompt. Do not publish it just by downloading it.

The reusable workflow fails closed for unknown, non-approved, corrupt, MIME-mismatched, or escaping paths and preserves exact bytes. No image transformation is involved. An artifact's GitHub retention window is **not** a production archive.

Draft persistence remains the atomic Git Data image+manifest commit described in `production/drafts/README.md`. After writeback, verify both the manifest entry and actual binary by running the readback bridge; do not infer persistence from a successful commit response alone.
