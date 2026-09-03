# Approved production drafts

This directory is durable storage for the **current user-approved production draft** associated with a RexPrompt recipe.

It is not released canon. Released canon remains in `starsplitterrecords/StarSplitterVisions`.

## State contract

The active production states are intentionally simple:

- recipe exists, no draft entry: no approved durable production image is stored in RexPrompt
- draft entry exists: a current approved production draft is stored in RexPrompt
- released canon mapping exists: released material is available in StarSplitterVisions

Generated attempts, rejected images, and chat-only work do not belong in this directory or manifest.

## Explicit-write rule

Nothing is stored here automatically. A draft is written only after an explicit user action, such as:

- selecting **Upload Approved Draft** / **Replace Approved Draft** in RexPrompt, or
- explicitly instructing a GitHub-capable production workflow to post a specific image to RexPrompt.

Approval language alone does not imply a repository write unless the user also directs the image to be stored in RexPrompt.

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
    "updatedAt": "2026-09-03T10:00:00.000Z"
  }
}
```

The active manifest contains only the current approved draft. Replacing a draft replaces the active file/mapping; Git history provides durable history without cluttering current production state.

## Chat/GitHub posting contract

A GitHub-capable workflow posting an approved image should:

1. Resolve the selected RexPrompt `seriesId`, `issueId`, and `recipeId`.
2. Write the image to `production/drafts/<series>/<issue>/<recipe>.<ext>` using safe lowercase path components.
3. Replace the corresponding `manifest.json` entry in the same commit.
4. Remove the previous active image path in that same commit if the extension/path changed.
5. Set status to `approved-production-draft`.
6. Never publish or copy the image to StarSplitterVisions unless the user separately requests release/publish.

The image and manifest update should be one Git commit so draft existence remains a reliable production-state indicator.
