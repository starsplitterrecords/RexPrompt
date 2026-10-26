# Production Asset Integrity Audit (C3)

Run `node tools/audit_production_asset_integrity.cjs --strict` from the repository root. The GitHub Actions workflow runs automatically when canonical draft or Reference Keeper assets/records change.

The audit verifies that the production draft and Reference Keeper manifests use their established keys and status/type contracts; saved assets exist at the required series/issue/type path; MIME types match extensions and binary signatures; PNG images have valid IHDR dimensions; and no two manifest entries accidentally share one image path. The audit prints authoritative counts by series and issue or reference type.

The script is **read-only**. It does not alter approved images, make release/canon decisions, recover missing assets, or reclassify user approvals. A strict run fails if references are missing or corrupt. Resolve failures through the appropriate recovery workflow, not by weakening the manifest or fabricating placeholder art.

This structural verification does **not** prove composition, identity continuity, lettering accuracy, image sharpness, mastered resolution, print quality, or issue completeness. Those require actual source-pixel inspection and issue-level review after asset recovery. Existing `tools/validate_visual_state.py` continues to validate metadata and source mappings separately.
