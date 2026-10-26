# Issue mastering — non-destructive preflight

The first gate for issue mastering is source integrity. Execute:

```bash
node tools/audit_issue_mastering.cjs --series rex-fleet --issue rex-fleet-i01
node tools/audit_issue_mastering.cjs --series rex-fleet --issue rex-fleet-i02 --json
node tools/audit_issue_mastering.cjs --series rex-fleet --issue rex-fleet-i03
node tools/audit_issue_mastering.cjs --series rex-fleet --issue rex-fleet-i01 --min-width 2400 --min-height 3840
```

The dimensions in the final command are an illustrative *explicit* production threshold, not a default or a claim that any current page meets it. The audit never resizes or recompresses images.

## Checks performed

- Image exists and can be decoded from its original PNG/JPEG/WebP signature and header
- Intrinsic width, height, format, file size, SHA-256
- Image path, MIME type, identity key consistency, color-profile indicators
- Aspect-ratio deviations from a requested target (default 5:8)
- Exact complete-book units (when `production/book-manifests.json` defines them)
- Optional minimum native pixel dimensions

Warnings and errors are reported separately. Missing required book units and file corruption fail the run. Color-profile uncertainty is *not* silently declared sRGB.

## Gates that remain manual or require full pixel readback

- Visual continuity and render detail at native resolution
- Exact dialogue, captions and lettering
- Compare palette and saturation across the complete issue
- Confirm source art is truly adequate for chosen trim and print DPI
- Correct or regenerate low-resolution artwork **at native target resolution**, not by simple upscaling
- Create approved, color-consistent masters without rewriting the original approved draft
- Visually inspect the assembled PDF and image package before publication

A passing machine preflight is **not** equivalent to a mastered book. The approved production-draft manifest remains untouched by this script.
