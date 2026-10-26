# Complete book export (B3)

`production/book-manifests.json` defines authoritative reading order, including cover, opening editorial, cast, story, closing editorial, and all end matter. Never derive a final issue solely from the scene selector or silently omit missing units.

## Offline complete-book builder

Requires Python 3.11+, Pillow and ReportLab:

```bash
python -m pip install Pillow reportlab
python tools/build_complete_book.py --series rex-fleet --issue rex-fleet-i01 --out /tmp/rex-i01-export
```

The builder:
- Fails if any inventory unit lacks an **approved** production draft, if paths escape approved storage, if image signatures conflict with MIME, or if original pixels cannot be decoded.
- Writes an exact-original-image ZIP with source SHA-256 and canonical reading-order metadata.
- Writes a full-resolution review PDF with one PDF page per inventory unit at the *explicit* trim dimensions (default 6.625 × 10.25 inches); it never upscales or edits approved source binaries. Images are proportionally fitted, not cropped, to the PDF page box.
- Re-opens and verifies the ZIP member count and original pixel hashes.
- Does not assert print readiness, mastering, color grading, or publication approval. Those require the B2 mastering review and the manual issue-wide visual and lettering gate.

The browser preserves explicit **INCOMPLETE-DRAFT** previews when some approved images are missing and includes a gap list and integrity manifest. An issue without a complete-book inventory is conspicuously labeled **UNVERIFIED-BOOK-DRAFT**. Neither state may be released. Complete release staging requires a complete-book inventory and zero missing approved units. Offline full-book builder remains strict: it will never create a partial package.

## Adding other series

Add each issue to `production/book-manifests.json` using **actual** approved RexPrompt production-unit IDs in the intended book order. Do not invent editorial units just to fill a convention. Missing images remain missing until recovered.

## Verification

Compare PDF page count and order to the complete-book manifest, visually inspect rendered spreads/pages, review lettering and trims, and validate links on the eventual released Visions site. The package alone cannot establish print-grade source resolution; B2 audits native pixel geometry against the chosen trim size.
