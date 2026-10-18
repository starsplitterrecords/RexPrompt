# RexPrompt page-composition contract (architecture v1)

RexPrompt authors **story beats** in `panelPlan`, dialogue in `dialogueInline` or `dialog`, and optional **visual hierarchy** in `pageLayout`. This composition field expresses the *relative importance and arrangement* of existing scripted panels. It is not a new story, a synthetic drawing, or a requirement to add pages.

## Page-local data

```json
{
  "id": "EXAMPLE_P04",
  "panelPlan": ["Beat 1", "Beat 2", "Beat 3"],
  "pageLayout": {
    "composition": "splash-with-insets",
    "visualPriority": "The wide environmental image dominates; human reactions add context.",
    "readingFlow": "Read the large image first, then the two insets in script order.",
    "primaryPanel": 1,
    "panels": [
      {"panel": 1, "role": "dominant", "scale": "splash",
       "placement": "Large full-height environment, leaving room for inset details."},
      {"panel": 2, "role": "inset", "scale": "small", "insetOf": 1,
       "placement": "First small reaction inset in the top-right of the large panel."},
      {"panel": 3, "role": "inset", "scale": "small", "insetOf": 1,
       "placement": "Second inset lower than the first; retain legible reading order."}
    ],
    "negativeSpace": [
      {"where": "upper-left dark structure", "purpose": "legible opening caption"}
    ],
    "lettering": {
      "strategy": "Keep captions and balloon tails separate from the key action.",
      "reservedZone": "Clear margin above the faces"
    }
  }
}
```

The live assembler in `index.html` is the authority for field names and output. The first implementation emits `[PAGE COMPOSITION]` **before** `[PANEL PLAN]` to prioritize page architecture without duplicating dialogue or actions. This emission is used unchanged by the preview, Copy Prompt, issue/series text and Markdown exports, and print/PDF export.

### Properties

- `composition` (required): `splash`, `splash-with-insets`, `asymmetric`, `grid`, `vertical`, `montage`, `open`, `quiet`, or `freeform`. These are **editorial architectures**, not templates or fixed geometric grids.
- `visualPriority` (required): what should carry the reader's attention. Choose for dramatic meaning, not decoration.
- `readingFlow` (required): how the reader moves through the composition. **Scripted panel order remains 1 → 2 → ... N.**
- `panels` (required): one visual assignment per scripted panel, with no extra, missing, or duplicate numbers. Panels are **1-based positions** in the existing `panelPlan` array, even when an existing panel object also carries a `panel` label. Entries require:
  - `panel`: integer in 1..N.
  - `role`: `dominant`, `supporting`, `inset`, `detail`, or `quiet`. All panels do **not** need a dominant role.
  - `scale`: `splash`, `large`, `medium`, `small`, or `micro`. Scale is qualitative, not a forced size percentage.
  - `placement`: visual relationship or location on the page, described in concise text.
  - `insetOf` (only for `inset`): number of the preceding parent panel. Nested insets and self-references are rejected.
- `primaryPanel` (optional): the principal focal panel, which must exist and carry role `dominant`. Omit for quiet or balanced layouts.
- `negativeSpace` (optional): array of `{where, purpose}` zones; reserve visual calm and/or legible captions. Preserve established series color language.
- `lettering` (optional): `{strategy, reservedZone?}`; reserve dialogue/captions without rewriting their contents or balloon ownership.

Any unknown or structurally invalid fields cause **assembly to fail loudly**, not a silent fallback to a generic grid. A `splash` must be a one-panel page; multi-panel dominant images use `splash-with-insets` or another architecture. Other shape choices remain editorial rather than artificially locked.

## Scope and editorial safeguards

- No `pageLayout`: **the assembled recipe stays identical** to prior output.
- The page-level suppression system cannot suppress `pageLayout`, scripted panels, dialogue, or continuity. The complete production data stays intact.
- Do not introduce, delete, or reorder scripted panels. Insets are a *visual relationship* between separate scripted beats, not a collapsed story beat.
- Dense text is a separate potential writing/lettering problem. `pageLayoutWarnings()` surfaces conservative, **advisory-only** diagnostics in the production UI; it does not alter, delete, or condense any dialogue and is not an artistic score. Review warnings manually, including intentional full-page caption designs.
- A quiet scene may use equal-size or understated panels; never demand a dominant splash simply to increase visual variety.
- The contract does not decide artistic layouts automatically. That requires the following **editorial phase B**: issue-by-issue review of character and dramatic beats, adjacent pages, and visual canon. No blanket rollout of one design to every page.

## Testing and examples

Five prototype data records are at `tools/fixtures/page_layout_cases.json`. They reference real scripted Vikings, Stardust Station, and Rex Fleet pages without editing the production page files.

Run:

```sh
node tools/test_page_layout.cjs
node tools/test_prompt_assembly.cjs
node tools/test_editorial_page_scopes.cjs
```

The tests extract and execute the **actual browser assembler**, check five distinct composition forms, verify all original dialogue, panels, and downstream recipe sections stay byte-identical, and reject broken panel references, illegal insets, unknown fields, unsupported suppressions, and unexpected defaults.

## Editorial handoff to phase B

Review the entire issue and chosen visual references. Create a page-specific `pageLayout` alongside authored story data (or as a strict `mergeById` overlay after the current story revisions). Prototype contrasting pages first, render with actual established references, and review caption readability, the dominant beat, page-turn effect, and reader eye path. Only then encode broader per-page plans. Keep the issue page count fixed unless an independent writing decision changes it.
