# Issue mastering workbench (B2)

A complete issue must be audited **in reading order** using the exact `production/book-manifests.json` inventory. This pipeline supplements (and does not replace) `tools/audit_issue_mastering.cjs`.

Requirements: Python 3.11+ and Pillow.

```bash
python3 -m pip install Pillow
node tools/audit_issue_mastering.cjs --series rex-fleet --issue rex-fleet-i01
python3 tools/master_issue_proofs.py --series rex-fleet --issue rex-fleet-i01 --out /tmp/mastering/rex-fleet-i01
```

The output is a `mastering-report.json` (file identity, source SHA-256, intrinsic dimensions, ICC hints, print DPI at specified trim, relative brightness and saturation, errors, warnings) and a **reading-order contact sheet** for an issue-wide visual grade/consistency review. Source images are not edited, resized, recompressed or overwritten. Trim defaults are explicit assumptions (6.625 × 10.25 inches, 300 DPI minimum); use `--trim-width`, `--trim-height` and `--min-dpi` for the actual publication format.

The pipeline **fails incomplete issues by default**; `--allow-incomplete` permits audit-only output but cannot grant mastering or publishing approval.

## Native-res, non-destructive grading proofs

Write an intentional look plan such as:

```json
{"RF_I01_P04":{"brightness":1.02,"saturation":0.96}}
```

Then use `--look /path/to/look.json --render-proofs`. All grade factors must be between 0.5 and 1.5. Proof PNGs retain the source's exact pixel geometry and live **outside** approved-draft storage. No automatic color equalization is performed, and lighting/palette outliers are warnings, not invitations to erase deliberate art direction.

These are **review proofs**, not replacements, mastered-authority records or published canon. Never promote them automatically. An image below native resolution requirements must be re-rendered appropriately; an enlarged image is not treated as a genuine native master.

## Mandatory remaining approval gates

Inspect full-resolution pixels and the complete issue for color intent, printed black/white endpoints, character and setting continuity, linework consistency, exact lettering, panel flow, deliberate differences between scenes, covers and editorial pages. A color profile not embedded in the source must be explicitly resolved for the intended output; the report never assumes sRGB. Keep an approved selection/grade record before using proof assets for final release.

## CI

The `Validate Mastering Workbench` workflow generates a downloadable report/contact-sheet artifact from a complete existing issue without creating or promoting mastered art. Final issue PDF and archive assembly is independently owned by B3.
