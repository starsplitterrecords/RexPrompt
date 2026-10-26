# IMG Rex Fleet Academy: Reach and Resolve — shared skill loader

**Project identity:** Rex Fleet Academy: Reach and Resolve. **Selector:** verify exact relevant live `data/shows.json` entries rather than treating this display title as a stable seriesId. Verified candidate show IDs: `rfa-reach-resolve-i01`.

**Activation:** In the project instruction, set `SKILLS_COMMIT_SHA` to an independently tested immutable RexPrompt commit SHA. Then retrieve `docs/skills/registry.json` from `starsplitterrecords/RexPrompt` at THAT SHA; read matching skill files and all mandatory dependencies, not merely their URLs. A literal placeholder, inaccessible SHA, missing permissions or disconnected connector **blocks operational use**, not a silent fallback.

**Intent routing:** “next”, “continue”, “finish issue” → `img-sequential-production`; “render”, “redo”, “fix page/balloon” → `img-page-production`; “recover lost images” → `img-production-recovery`; “inspect original pixels” → `img-binary-readback`; “audit issue” → `img-issue-audit`; “match color” → `img-color-normalization`; “master/export issue” → `img-issue-mastering`; “save selected visual reference” → `reference-keeper-ingest`. Use semantic intent and scope; explanatory/quoted examples do not trigger actions.

**Universal IMG contract:** same Rex Fleet-derived workflow for ALL series. Exact current assembled recipe; released *same-series* StarSplitterVisions baseline; approved unpublished `production/drafts/manifest.json`; approved scoped Keeper or corrective refs; actual image pixels inspected in THIS session before generation; shared `production/approval-policy.json` and atomic image+manifest Git commit; frontier derived from released+approved recipe IDs. No project-local cursor, alternate approval model, guessed checkpoint, cross-series visual authority or publication without separate instruction. Preserve all existing work, including later approved pages when gaps exist.

**Cutover guard:** Legacy Project Sources and prior chat files are historical evidence only; do not discard them until their original bytes and approvals are reconciled into canonical GitHub-backed drafts. Any missing source/approval blocks the relevant asset migration, not the preservation of other progress.

**Completion evidence:** return exact recipe ID, relevant original-byte and approval checks, resulting commit SHA and remaining blockers. A loader is only instructions; it is neither a background agent nor an automatic GitHub fetch without tools.
