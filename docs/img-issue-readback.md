# Original issue readback

Use **IMG Complete Issue Binary Readback** to download an ordered original-image bundle from approved RexPrompt drafts.

- Enter exact `series_id` and `issue_id` from `production/book-manifests.json`.
- It uses each book-manifest slot; no story-only selector is trusted. Every source image is validated by the existing canonical `tools/prepare_img_readback.cjs`, then copied without rasterization, recompression, or resizing.
- `issue-readback.json` maps page position, recipe ID, original path, Git SHA and SHA-256. By default incomplete books fail; setting `allow_incomplete=true` explicitly creates **review-only** partial originals with a missing-page list.
- GitHub Actions artifact is temporary transport. The original approved asset paths remain authoritative. Extract and visually audit native source images before mastering. No artifact is automatically a final book.

The pull-request test uses all 22 approved Rex Fleet Issue 1 sources so it exercises full original-binary transport. The single-asset canonical readback workflow `img-binary-readback.yml` remains the preferred route for references and individual production images.
