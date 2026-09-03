# RexPrompt production visual state

RexPrompt may display two durable visual states for a selected recipe:

- **Approved production draft** — mutable production data stored in this RexPrompt repository.
- **Released canon** — read-only visual material sourced from `starsplitterrecords/StarSplitterVisions`.

These states are intentionally separate. A draft never becomes canon merely because it is stored in RexPrompt.

## Released canon resolution

`visual-sources.json` identifies the StarSplitterVisions series metadata source for released series.

For page-based RexPrompt issues, the UI may map released pages automatically only when all of these are true:

1. the selected RexPrompt issue reports `PAGE` units,
2. a numeric issue number can be resolved,
3. StarSplitterVisions exposes released pages for that same issue, and
4. the released page count exactly matches the RexPrompt recipe count.

This count check prevents ordinal guessing when production structure and release structure differ.

Scene-based or otherwise non-1:1 material uses `released-links.json`. Each key uses the same `<seriesId>::<issueId>::<recipeId>` contract as draft storage and may point to one or more StarSplitterVisions images. `released-links.json` is only a cross-repository mapping; the images and canonical authority remain in StarSplitterVisions.

Example:

```json
{
  "rex-fleet::rex-fleet-s1-issue-1::RF_S1E01_S04": {
    "images": [
      {
        "path": "/images/pages/rex-fleet/issue-01/page-005.jpg",
        "label": "Issue 01 · Page 5"
      }
    ]
  }
}
```

Do not populate released links by guessing from scene order.
