# October 2026 — Mechanical Production QC and Regression Reconciliation

The C1 replacement PRs restore approved page-layout and scoped recipe data without changing image assets or released story canon. This C2 pass aligns the Python validators with the live deterministic RexPrompt assembly contract:

* Slip Knife and Between the Beacons now validate their canonical source page overlay **and** their strict page-visible faction overlay; neither story data nor faction profiles are rewritten.
* Azure Reach's validator now separately loads compressed authored pages and applies strict page-scoped editorial JSON by matching page IDs, disallowing unknown profile fields, duplicate IDs and orphan patches. Story-page order is retained.
* Azure Reach published Issue 1 already contains panelCount/panelPlan metadata discrepancies in the compressed production source. The validator reports those historical mismatches explicitly, without rewriting released canon or relaxing panel structure validation on unreleased issues.

This is **mechanical** QA, not a visual pass. Image approval, continuity of faces/props/lettering, print resolution, and issue mastering must be checked using actual rendered pixels once canonical assets are available in the appropriate IMG/recovery lanes.
