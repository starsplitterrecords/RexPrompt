# Final recipe-scope sanitation gaps

This integration completes the primary comics prompt-suppression rollout **without duplicating** other teams' recently merged work.

The current main branch already has scoped policies for Rex Fleet, Low Tide Signal, Azure Reach, Sunforge Outlaw, Stardust Issues 4–10, Echoes, and addressed Vikings. Their existing overlays and tests are preserved exactly.

This change supplies the three previously uncovered production areas:

- **Backyard Rockets Issues 3–8:** 118 scripted interior pages in six strict per-issue overlays, after their separate pageLayout instructions. Established cast, regional/faction boilerplate and returning setting definitions are compacted. New people, groups, first location views and unique story directions stay available. Only factual documentary summaries already carried by scripted panels and visual priority are omitted. Original scripts and released Issues 1–2 remain unchanged.
- **Division Threshold Issues 1–8:** issue-scoped cast, setting, population and regional references; new identities and society/group contrasts stay fuller on introduction. All fictional population/physical identity source descriptions remain intact. No page, dialogue, or source canon changed.
- **Stardust Station Issue 3:** returning released cast and the established Admin Hub can use concise names instead of eight simultaneous complete model descriptions. The 22 full creative summaries remain intact.

Additionally, short labels derived from existing durable setting descriptions were added to Rockets, Division Threshold, and Rex Fleet. These are useful for label-mode assembly and prevent machine IDs from reaching the chef; the complete visual design text is untouched.

**Already compact and not force-edited:** Vikings' later issues. **Non-comic scene format excluded:** The Sun Comes Through. Existing related improvements on main are not superseded by duplicate policy records.

## Verification

Run node tools/test_recipe_scope_rollout.cjs. The test reconstructs each affected recipe from the live RexPrompt assembler, first without and then with the new profiles. It compares scripted PANEL PLAN, PAGE COMPOSITION, DIALOGUE, CONTINUITY and DIRECTION verbatim; it checks no source page/scene count changes, invalid IDs, unsupported scope fields or missing human-readable labels. The rest of RexPrompt's existing tests still run in CI.

This passes the **recipe and data-assembly gate**, not finished-image approval. Image production still needs actual canon/reference pixels and independent composition and lettering QA.
