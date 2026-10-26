# Reference Keeper — portfolio-wide intake and retrieval

Keeper stores visual reference images in RexPrompt; it does not grant creative approval, assemble references into recipes, or publish anything to StarSplitterVisions.

## Inventory and authority

- Canonical series IDs follow RexPrompt index.html seriesId(show): use an explicit seriesId when present; for legacy shows without one, derive the ID from the normalized seriesName (not individual issue titles). All registered series can use Keeper, including those with no entries yet.
- The sole manifest is production/references/reference-keeper-manifest.json (schemaVersion 1). Each entry has a stable key, seriesId, seriesName, type, name, image, mimeType, sourceFilename and updatedAt.
- Categories: character, setting, vehicle, item.
- Files: production/references/SERIES_ID/keeper/CATEGORY/REFERENCE_NAME.png (or .jpg/.webp).
- Existing valid identity corrections, approved references and released canon remain unchanged; historical keys may differ from current name slugs. Never register the known malformed Division Threshold Checkpoint 9 image.

## One safe intake contract for new recovery work

1. Establish the exact series, category, identity, original durable source and explicit approval. A discovered image is not automatically canonical.
2. Retrieve original binary bytes. Do not upload a thumbnail, URL, chat text, base64 text file, recompressed stand-in or resampled image.
3. Store a reference from the Keeper UI. Enter a nonempty name (maximum 120 characters), correct registered series and category, and select the JPEG, PNG or WebP. Image must be at most 50 MB. The actual magic/signature, MIME label and filename extension must match.
4. The shared reference-keeper-contract.js enforces ID construction, safe paths, duplicate identities, file destination collision checks, canonical series IDs and binary checks. Existing IDs are stable: use the card's Replace control to replace an already registered identity.
5. The UI reads fresh GitHub main and the current manifest inside the serialized write lane; validates the entire manifest, stores the original bytes as a Git blob, and commits the binary and manifest atomically. A concurrent non-fast-forward update retries from fresh main; it never silently recreates a missing manifest.
6. Refresh Library to verify the correct series and category, search by name/ID/source filename, and enlarge the original preview. A failed preview is explicitly reported instead of counted as a success.
7. Run the asset-recovery CI checks before merging any chat-based import PR. Do not create a second manifest format or overwrite an unrelated stored image.

## Exact-byte retrieval

1. Resolve a record using its exact manifest key, series and category.
2. Dispatch the existing IMG Binary Readback workflow with asset_kind=reference and asset_key=EXACT_KEEPER_KEY. It invokes tools/prepare_img_readback.cjs against the authoritative manifest.
3. Download its artifact containing original.png, original.jpg, or original.webp plus readback.json. Confirm the SHA-256, Git blob SHA, byte count, series, path and MIME against the stored original.
4. Bring actual pixels into the IMG session before visual continuity work. GitHub text API output, metadata, remembered images or a URL alone are not image-pixel inspection.

## Validation and scope

Run:
- node tools/validate_reference_keeper.cjs
- node tools/test_reference_keeper_series.cjs
- node tools/test_keeper_curated_byte_identity.cjs
- node tools/test_keeper_portfolio.cjs

The portfolio validator checks all existing entries for missing files, symlinks, stale or unknown series associations, unsafe or incorrect paths, duplicate identities and images, mismatched MIME/signatures/extensions and incorrect categories. It also verifies portfolio UI selection semantics.

The portfolio tests simulate original-image intake, manifest update, search/category filtering, reload, and byte-exact readback through the existing readback bridge for representative references from each category present in each populated series. This tests the reusable contract for current and future registered series. The workflow .github/workflows/validate-asset-recovery.yml enforces the checks for relevant PRs and main pushes.

## Distinguish registered integrity from outstanding historical recovery

A passing audit means every *registered Keeper reference* resolves correctly. It does not prove that every historical original exists. Missing or unavailable source references, exploratory generations, and recovered images without explicit approval remain separately tracked under the portfolio recovery backlog (RexPrompt issue #315); never manufacture replacements or promote unclassified work.
