# Cross-repository branch reconciliation audit

Issue #316 is the decision authority for concurrent workstream overlap. This audit establishes repeatable evidence, not permission to merge.

Run the **Audit historical Git branch contributions** Action to fetch all retained branches from RexPrompt and StarSplitterVisions, anchor to current origin/main, and emit JSON reports with exact branch names, tip SHAs, ahead/behind counts, and every file whose content differs from main.

Statuses: **incorporated-by-history** means branch tip is an ancestor of main. **tree-equivalent-to-main** means a distinct tip with exactly the same tree. **divergent-retained-pending-evidence** means current file contents differ; this is NOT a finding that the old implementation is useful, unique, or approved. Compare PR decisions, current code, tests, approved canon and explicit successors. Aliases sharing a commit are grouped by SHA.

Historical refs are deliberately retained. Do not bulk-merge, delete branches, or turn this scanner into approval/canon authority.

The manual adjudication ledger is in docs/reconciliation/2026-10-25-contribution-dispositions.md.