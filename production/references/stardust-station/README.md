# Stardust Station production references

Use this directory as the curated visual-reference entry point for Stardust Station image production.

## Authority

- Released StarSplitterVisions Issue 1 remains the visual canon.
- `visual-reference-pack.json` selects the strongest released interior-story pages for recurring identity, setting and page-language reference.
- `issue-2-cast-promo-thumb.jpg` is an approved current-production identity reference for the nine core cast members. It is not page-layout, lettering, title, header or story authority.
- Approved recipe-level production images belong in `production/drafts/` and must be explicitly stored there after approval.
- Rejected, failed, superseded or chat-only generations are never continuity references.

## Production startup

Do not store a production cursor here.

Resolve the production frontier from durable state each time:

1. explicit current user direction,
2. approved production drafts in `production/drafts/manifest.json`,
3. released StarSplitterVisions pages,
4. ordered RexPrompt recipes.

For each selected page, use the exact assembled RexPrompt recipe plus the smallest relevant subset of `visual-reference-pack.json`, then add the immediately preceding approved production image when spatial or story state carries forward.

The previous generated page must never be the sole character or visual authority.
