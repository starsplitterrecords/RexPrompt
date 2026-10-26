# Universal IMG image readback and durable approved-artwork persistence

Canonical authority: RexPrompt main contains approved unpublished image binaries and manifests; StarSplitterVisions contains released canon. Existing scripts are the ONLY image-transport implementation. These operations do not create a new archive, approval state, or production cursor.

## Exact single-image readback

Run the existing GitHub Actions workflow **IMG Binary Readback**, selecting kind draft/reference and the exact manifest key. Authorized IDs come from production/drafts/manifest.json and production/references/reference-keeper-manifest.json. The canonical prepare_img_readback.cjs checks current approved-state, manifest identity, storage confinement (including realpaths), MIME, byte counts, PNG chunk CRCs, WebP RIFF boundaries, and expected SHA-256 when recorded. It copies the original file with no transformations. readback.json contains original path, ID, MIME, byte count, SHA-256, Git blob SHA, repository source revision, and pixelInspectionVerified=false.

Download and extract the GitHub Actions artifact, verify the checksum against the extracted original, and load the **actual image pixels** into the destination IMG conversation. An artifact, hash, filename, path or successful workflow check is NOT equivalent to visual inspection.

## Exact complete-issue readback

Run the existing **IMG Complete Issue Binary Readback** workflow using exact series and issue IDs from production/book-manifests.json. prepare_issue_readback.cjs delegates every page to the same original-image helper. No separate transport format exists. Output image files follow the complete-book reading order and are mapped by recipe ID, book page, exact original path, byte length, MIME, SHA-256 and Git blob SHA in issue-readback.json.

Default incomplete-issue policy: fail before copying any images when required approved slots are absent. Setting allow_incomplete=true permits an explicitly review-only partial bundle, preserving missing-page positions. Corrupt approved files fail even in partial-review mode; they are not quietly skipped. Bundle metadata sets pixelInspectionVerified=false.

## Verified regression scope

CI: .github/workflows/validate-img-readback.yml. Local equivalent:

    python3 -m pip install Pillow
    node tools/test_img_readback.cjs
    node tools/test_img_transport_matrix.cjs
    node tools/test_atomic_img_persistence.cjs

The matrix checks actual PNG drafts and PNG/JPEG Keeper files from each indexed series; SHA-256 and Git blob SHA; exact original bytes; and full Pillow image decoding. It checks complete Rex Fleet Issues 1 and 2, incomplete-review Vikings and Stardust Issue 2, and failure of incomplete Rex Fleet Issue 3 when complete source is required. Sandboxed fixtures check missing binaries, corrupted PNG CRCs, wrong hashes and MIME types, rejected images, parent-directory symlink escapes, and synthetic JPEG/WebP original-byte transport.

A test that Pillow decodes a file on a CI runner is a binary image-integrity test; it is **not** proof that an IMG chat inspected that image.

## Durable approved-artwork persistence

The existing authorized operation is direct Git Data image-plus-manifest atomic persistence, defined in production/drafts/README.md and production/approval-policy.json. The optional implementation tools/persist_approved_draft.cjs consumes an already-reviewed original image available as a local file in an authorized runtime; it requires actual approval evidence and a runtime-provided GitHub token. Never send a token in chat text or commit it.

Required environment variables: GITHUB_REPOSITORY, GITHUB_TOKEN, TARGET_BRANCH, SOURCE_IMAGE, SERIES_ID, ISSUE_ID, RECIPE_ID, APPROVAL_METHOD, EVALUATION_SUMMARY, REVIEWED_APPROVAL=true. ALLOW_MAIN_WRITE=true is separately required for main. REPLACE_APPROVED=true is required for replacing an existing approved page. EXPECTED_HEAD_SHA can pin the preflight revision.

The utility:
1. Reads the current target-branch commit, tree and approved-draft manifest.
2. Creates a Git blob from the **exact** original image bytes (no recompression/resizing) and a second blob for the approved-draft manifest update.
3. Creates one tree containing image and manifest entries plus any superseded-path removal; creates one commit based on the original head.
4. Advances the ref once with force=false, rejecting concurrent non-fast-forward updates.
5. Independently fetches the committed manifest and image blob from GitHub to confirm the recorded original-image SHA-256 and the full image bytes.

tools/test_atomic_img_persistence.cjs exercises those operations against a disposable local Git API mock (including rejected overwrite, rejected nonapproved generation and branch race). No real production image/manifest is modified in the mock tests. Follow any real write with the **normal** readback workflow from an independent fresh session to prove durability.

## Session/connector limit and mandatory multimodal gate

GitHub Actions artifact ZIPs are temporary transport, not durable archives. Some GitHub connector APIs expose a connector-local ZIP reference but no extracted PNG/JPEG attachment into the model context; direct GitHub binary fetch can fail while UTF-8 decoding. A successful workflow and artifact download cannot be represented as actual image vision.

The target IMG chat must verify that the original pixels are accessible **in that conversation**, and visually examine them before generating related art. If the tool chain stops at an opaque ZIP reference, record the visual-reference gate as BLOCKED, not PASSED; use an actual supported image attachment path. No workflow may claim this final gate merely from metadata or Pillow decoding in Actions.

All source images remain unchanged. Mastering, creative approval and publishing are separate gates.

## Verified ChatGPT connector-to-pixel handoff — October 25, 2026

This capability was exercised in the engineering ChatGPT conversation using **the existing GitHub connector's download_workflow_artifact action**, not a new image service. The downloaded Action artifact automatically materialized as a ZIP in that conversation's working filesystem; the ZIP was extracted there and Pillow fully decoded actual original images. The assistant then opened those extracted source files with its image-inspection capability and directly inspected their visible content.

Evidence:
- Complete issue: GitHub workflow run 40266184729 / artifact 12626318168. Rex Fleet Issue 1 returned **22/22** exact original pages, SHA-256 and Git blob SHA verified for each, full image decode for all 22, inspected the actual page RF_I01_P01 visually.
- Single-image proof: run 40266576305 / artifact 12626692364. Azure Reach approved draft AZR_S1E02_P09 delivered original **1024 × 1536 PNG**, 2,597,968 bytes, SHA-256 **847b90678c57f012d46515eb6288e665c730badd01dc34a63f367df4f50bc9fc**. Division Threshold Keeper reference Axiom delivered exact **160 × 240 JPEG**, 6,527 bytes, SHA-256 **9d25f7cae2c194bb2979d1f854ab045e132d240f4231088b7111087029ab0a4d**. Both original files decoded and were inspected as actual pixels in the conversation.
- The Keeper reference is a genuine small canonical JPEG file, **not a transport downsample**. Reference-recovery work should locate a higher-quality approved original if required; B1 must never enlarge or fabricate one.
- The live Git Data API was separately exercised in a noncanonical test-only branch revision: image and JSON metadata blobs appeared in **one** tree and one commit, both independently re-fetched; the temporary files were removed from the active branch afterward. This verified real atomic Git Data semantics without approving or altering production artwork.

**Scope of proof:** actual image pixels reached and were visually inspected in the **engineering conversation that executed this test**. A future or different IMG conversation must run the bridge and verify visible pixels independently. Connector permissions, transient artifact retention, and attachment behavior are session-specific. A GitHub download success alone does not pass this final gate. An actual newly generated *approved* page was not available to this test, so new-production persistence is supported by the production utility, mocked end-to-end tests, the live Git Data atomic probe, and existing durable artwork re-retrieval—not a falsely claimed new artwork approval.
