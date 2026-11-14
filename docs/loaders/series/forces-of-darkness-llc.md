# IMG The Forces of Darkness, LLC. — shared skill loader

**Project identity:** The Forces of Darkness, LLC. **Canonical seriesId:** `forces-of-darkness-llc`. **Selector:** use the registered series/issue collection; never infer separate cover-only selectors. Verified candidate show IDs: `forces-of-darkness-llc`.

**Activation:** Set `SKILLS_COMMIT_SHA` to an independently tested immutable RexPrompt commit SHA, then read `docs/skills/registry.json` and required dependencies from that exact commit. Inaccessible or unverified source blocks production use.

**Intent routing:** “next”, “continue”, “finish issue” → `img-sequential-production`; “render”, “redo”, “fix page” → `img-page-production`; “audit issue” → `img-issue-audit`; “save selected reference” → `reference-keeper-ingest`.

**Universal IMG contract:** use the exact currently assembled recipe, approved same-series references, `production/approval-policy.json`, `production/drafts/manifest.json`, and atomic image+manifest persistence. Do not equate generated drafts with approved pages. Preserve existing strip numbering, series identity, approved masthead and artwork. Do not silently publish, delete or overwrite existing approved work.
