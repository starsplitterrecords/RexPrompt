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

When a generated page substantially passes the production evaluation, the production workflow should approve and persist it automatically unless the user has rejected, superseded, or requested repair/replacement of that page. The user does not need to issue a separate storage command.

A substantially passing page must have no material defect that would justify regeneration before advancing. The required evaluation covers recipe fidelity, character identity, immediate continuity, composition/readability, lettering, output hygiene, and material generation defects.

Approval of a normal page does not redefine an existing visual identity. A first strong production image may establish a previously unestablished recurring identity. Replacing an existing released or approved identity requires explicit user intent.

## Direct GitHub persistence transaction

Approved image persistence uses GitHub directly. No external staging service is required.

For each approved unpublished recipe-level image:

1. Resolve the exact `seriesId`, `issueId`, and `recipeId`.
2. Preserve the approved image bytes exactly; do not redraw, recompress, or transform merely for storage.
3. Base64-encode the image bytes for transport to GitHub's Git Data `create_blob` API.
4. Create the image blob.
5. Create an updated `manifest.json` blob containing the current `approved-production-draft` entry.
6. Build one Git tree from the current branch tree containing both the image path and manifest update. If a replacement changes the active image path or extension, remove the superseded path in this same tree.
7. Create one Git commit from that tree and the current branch head.
8. Advance the target branch ref only after the complete commit exists.
9. Verify the committed image and manifest entry.

The image and manifest update are therefore atomic production state. Git history provides durable replacement history without creating competing active drafts.

Do not publish or copy an approved draft to StarSplitterVisions unless the user separately requests release/publish.

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

## Recovery

IMG recovery uses the same direct persistence transaction. Historical generated images that are correctly mapped to an exact recipe and pass recovery evaluation should be written directly into the normal approved-draft storage and manifest. Recovery must not create a second cursor, staging authority, or parallel image state.
