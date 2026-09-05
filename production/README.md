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

## Curated continuity reference packs

A released series may also define an optional `referencePack` path in its `visual-sources.json` entry.

A reference pack is **not another canon layer**. It is a curated index pointing to the strongest existing visual authorities for production startup and per-unit reference selection. It may combine:

- selected released interior-story images from StarSplitterVisions,
- explicitly approved current-production identity/corrective references from RexPrompt,
- character-to-reference and setting-to-reference selection order,
- explicit exclusions identifying assets that must not be used as page-style authority.

Production workflows should load a configured reference pack at the start of an IMG production session and use the smallest relevant subset before every generation call. The pack does not replace the exact assembled recipe, released canon, approved draft state, or immediate continuity.

Do not use `released-links.json` to point an unreleased recipe at an earlier issue merely for visual continuity. That would falsely imply that the selected recipe itself has released canon. Cross-issue continuity belongs in a curated reference pack instead.
