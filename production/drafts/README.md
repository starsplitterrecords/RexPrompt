# Approved production drafts

This directory is durable storage for the **current approved production draft** associated with a RexPrompt recipe.

It is not released canon. Released canon remains in `starsplitterrecords/StarSplitterVisions`.

## State contract

The active production states are intentionally simple:

- recipe exists, no draft entry: no approved durable production image is stored in RexPrompt
- draft entry exists: a current approved production draft is stored in RexPrompt
- released canon mapping exists: released material is available in StarSplitterVisions

Generated attempts, rejected images, and chat-only work do not belong in this directory or manifest.

## Automatic approval rule

Sequential IMG production uses `production/approval-policy.json`.

When a generated page substantially passes the production evaluation, the production workflow should approve it automatically unless the user has rejected, superseded, or requested repair/replacement of that page. The user does not need to issue a separate storage command.

A substantially passing page must have no material defect that would justify regeneration before advancing. The required evaluation covers recipe fidelity, character identity, immediate continuity, composition/readability, lettering, output hygiene, and material generation defects.

Approval of a normal page does not redefine an existing visual identity. A first strong production image may establish a previously unestablished recurring identity. Replacing an existing released or approved identity requires explicit user intent.

## Persistence transaction

Image-generation chat cannot reliably write binary image bytes through the GitHub text-file interface, so approved images use a stage-then-vendor transaction:

1. The production workflow uploads the approved image to the configured staging provider. Staging is transport only and is not visual authority.
2. The workflow appends one approval record to `production/drafts/intake.json` containing the exact `seriesId`, `issueId`, `recipeId`, staged HTTPS image URL, approval method, and approval time.
3. Committing `intake.json` triggers `.github/workflows/ingest-approved-drafts.yml`.
4. `tools/ingest_approved_drafts.py` validates the staging host and image bytes, vendors the PNG/JPEG/WebP image to `production/drafts/<series>/<issue>/<recipe>.<ext>`, replaces the active `manifest.json` entry, removes a superseded active image if necessary, and removes the processed intake record.
5. GitHub Actions commits the image and manifest update together. RexPrompt is then the durable authority; the staging URL is no longer required for production continuity.

The default staging host is `res.cloudinary.com`. Additional hosts must be explicitly configured in the workflow environment rather than accepted generically.

The manual **Upload Approved Draft** / **Replace Approved Draft** path remains valid as an override or recovery path, but it is no longer the normal IMG-production approval mechanism.

## Manifest key

`manifest.json` keys use:

```text
<seriesId>::<issueId>::<recipeId>
```

Example entry:

```json
{
  "rex-fleet::rex-fleet-s1-issue-3::RF_S1E03_A14": {
    "seriesId": "rex-fleet",
    "issueId": "rex-fleet-s1-issue-3",
    "recipeId": "RF_S1E03_A14",
    "status": "approved-production-draft",
    "image": "production/drafts/rex-fleet/rex-fleet-s1-issue-3/rf_s1e03_a14.jpg",
    "mimeType": "image/jpeg",
    "updatedAt": "2026-09-03T10:00:00.000Z",
    "approvalMethod": "automatic-substantial-pass"
  }
}
```

The active manifest contains only the current approved draft. Replacing a draft replaces the active file/mapping; Git history provides durable history without cluttering current production state.

## Direct/manual GitHub posting contract

A workflow that already has direct access to the approved image bytes may bypass staging and should:

1. Resolve the selected RexPrompt `seriesId`, `issueId`, and `recipeId`.
2. Write the image to `production/drafts/<series>/<issue>/<recipe>.<ext>` using safe lowercase path components.
3. Replace the corresponding `manifest.json` entry in the same commit.
4. Remove the previous active image path in that same commit if the extension/path changed.
5. Set status to `approved-production-draft`.
6. Never publish or copy the image to StarSplitterVisions unless the user separately requests release/publish.

The image and manifest update should be one Git commit so draft existence remains a reliable production-state indicator.
