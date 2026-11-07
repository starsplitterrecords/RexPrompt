# Method and limits

## Source

This audit runs RexPrompt main index.html loadShow, expandIssues, assembleScene, validatePageLayout and pageLayoutWarnings in Node. The exported CSV contains one row per registered unit within its assembled issue. It reads the actual visible panel and setting sections rather than trusting unused metadata alone. The first previous page is reset at issue boundaries.

## Rules

- Composition: validated layout passes; explicit one-panel splash passes; shot cues without layout hierarchy require review; invalid layouts are blockers; musical scenes are not page layouts.
- Image detail: authored panel visual words PLUS concrete shot, geography and physical/lighting cues. Generic generationLine boilerplate is excluded from specificity.
- Setting: detailed emitted setting passes, otherwise same setting or explicit continuityFrom on immediate prior page is acceptable carryover; sparse new environment needs review or fails.
- Blocking: character physical movement, location and props; dense lettering without explicit assignment is review; no acting required on environment-only pages.
- Emotional performance: expression, gaze, posture, meaningful reactions and subtext; lack of any with dialogue or visible cast is a gap. Does NOT measure true dramatic impact.
- Each row includes the evidence explaining the score and the first panel excerpt for human follow-up.

## Limits

- Editorial heuristics are NOT a substitute for reading the entire sequence and its actual references. They can overestimate adequacy of long generic descriptions and underestimate economy or artful silence.
- No image pixel inspection, actual face consistency, palette, lettering or print quality assessed. Neither a passing score nor approved draft record is final art approval.
- A reported unapproved page may exist elsewhere outside the approved RexPrompt manifest.
- This audit modifies NO source scripts, dialogue, images, approvals, published material or continuity canon.

## Inventory

Registered configurations: 138
Expanded issues: 152
Unit rows: 2971
Load errors: 0

Errors: []
