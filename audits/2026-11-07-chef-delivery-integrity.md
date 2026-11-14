# RexPrompt source-to-chef integrity study — 2026-11-07

Source baseline: `main` commit `2f8c964df06fd404a022fab53ee25897b7feb938`. Audit-only; NO creative production changes.
Scope: 25 distinct production series (Rex Fleet and Rex Fleet — Full Performance remain separate), 138 configurations, 2,971 unit occurrences.
Method: execute the actual `index.html` loader and assembler in Node VM against all JSON and encoded `.gzb64` source overlays; compare effective scene fields and referenced shelves with exact chef-facing assembled text. Prior basic regression alone was insufficient.

## Outcome

- Configurations loaded: 138/138.
- Assemble: 2,968; rejected: **3**.
- Units with clear assembly blocker / source-to-chef instruction loss / absent page plan: **130 distinct units**.
  - Blockers: **3** (Full Performance I01 `RFFP_I01_EDITOR_V8_OPEN_05`, `RFFP_I01_P001`, `RFFP_I01_P002`; composition identifiers `three-panel` / `four-panel` unsupported).
  - Clearly truncated panel descriptions: **41 panels / 39 units**, exclusively Full Performance I01–I12. Examples: `RFFP_I01_P003` “evident in the.”, `RFFP_I02_P019` “Abby sees the.”, `RFFP_I11_P013` “she isn't a.” **All 41 are recoverable in their complete original `sourceActionBeats` entries; the defect is in their compiled `panelPlan`, not the original writing.**
  - Source direction explicitly suppressed: **50 units**, Vikings I02 (15) and Sunforge I01–I03 (35). Their `direction` or `directionInline` source exists, but `promptSuppress` prevents the direction block from reaching chef; sometimes some content is repeated in other sections.
  - Vikings covers I02–I12: **44** free-form lettering-placement `dialogueInline.subtext` instructions silently lost on **11** units by `compactDialogue`; visible lettering still delivered.
  - Backyard Rockets S1E01 and S1E02: **25** units contain dialogue but no `panelPlan` (20 in E01 and 5 in E02).
  - Unresolved `@vik.Arche` character handle: Vikings I04 `VIK_S1E04_P09` and `VIK_S1E04_P15`.
  - Vikings I02 `VIK_S1E02_P15`: `offPanelSpeakers` is not an assembler-consumed field, so the explicit off-panel instruction is missing.
- External/review-only routes (overlapping; DO NOT sum as defective-page counts):
  - **2,022** units with at least some dialogue not assigned a deterministic numeric panel owner. Earlier regression warned on 1,034 pages under its narrower heuristic. The actual dialogue text remains present; visual placement requires separate inspection.
  - Character shelf **performance** instruction not carried as exact text on **1,313** units; character appearance expects an external real-pixel reference or equivalent on **2,092** units. Those external image handoffs were NOT inspected here.
  - Explicit faction references not expanded into chef sections on **889** units; setting label mode and summary/region suppression are further source-to-chef dependency risks. Redundant or intentionally scoped material needs case-by-case determination, not automatic rewriting.
  - Backyard Rockets `assetReuse` instructions exist on **44** units but the assembler does not consume them; reuse/reletter action might belong to an external workflow, requiring explicit routing.
  - Stardust Station `relationshipFocus` not consumed on 50 units; further ignored specialized fields include documentary channel and musical song titles.
- Source/validator false-positive calibrations:
  - **164** Sunforge indexed-lettering panel source strings were transformed safely: panel action prefix and exact canonical dialogue both remain in chef output. Literal string mismatch does NOT imply loss.
  - Generic `shotType: SEQUENTIAL` is intentionally suppressed in clean panel output and does not by itself lose action.
  - Metadata classifier `directionInline.type` omitted on 18 Vikings I01 pages while full authored `text` survives.
  - Low Tide shelf `description` is often duplicated into emitted `text`; do not count as lost solely because description string is absent.
- Not audited: actual rendered image pixels, real character-reference attachment, balloon-tail geometry, narrative/artistic validity, user approval, release readiness. A successful assembly is not a quality approval.

## Decisions and repair gates

1. Correct rejected composition enums without rewriting dialogue or changing creative design.
2. Restore truncated Full Performance panel action from original `sourceActionBeats` and associated authored script; do not invent missing endings.
3. For Vikings/Sunforge suppressed directions, establish equivalent surviving content per page, then route material production instructions into the current assembler.
4. Preserve exact cover lettering/subtext while using compact dialogue.
5. Give the 25 Backyard Rockets scenes explicit page/beat plans or a verified alternative production contract; preserve the `assetReuse` provenance and source artwork.
6. Resolve `@vik.Arche` identity and off-panel speaker delivery.
7. Classify dialogue-owner uncertainty and character/faction/setting delivery by creative authority before implementing any global formatter changes.
8. Re-run a source-to-chef comparison and production regression per issue after repairs; NO creative content or published assets were modified by this audit.

Supporting full series/issue/unit CSVs, 9,000+ field-specific finding records, actual chef prompt archive and Excel workbook were generated in the corresponding ChatGPT audit turn. This Markdown is a permanently stored checkpoint; it is not a substitute for the per-unit evidence artifacts.
