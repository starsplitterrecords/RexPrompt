# Division Threshold — Production Data Audit
Date: 2026-08-24
Status: development diagnostic, not canon

## Purpose
Audit the package for the failure mode where persistent style/world scaffolding overwhelms page-specific story information during comic generation.

## Findings

### 1. Page uniqueness
The 26-page Issue 1 draft has strong beat differentiation: medical origin, Organic origin, Intelligence awakening, Stack splash, checkpoint, rescue, bureaucracy, clinic, Organic home ground, investigation, undercity action, white-site reveal, purge, and political hook. The long-form draft is more page-specific than the older compact scene encoding.

Risk found: `scenes_e01.json` currently compresses pages 5–26 into 11 production records. Several records therefore carry multiple page functions. This is acceptable as story-scene data but should NOT be treated as one-record-per-generated-page data.

Recommendation: before image generation, encode Issue 1 into explicit page records P01–P26 (and panel beats where needed), referencing persistent data rather than copying it.

### 2. Scope correctness
Persistent series rules are correctly concentrated in `series_bible.json`, characters in `characters.json`, and locations/regions in their reference files. However, global blocking/mood/lighting text was phrased as if it should control every scene, and direction records contained repeated generic prestige/grounded/staging language.

Action taken: rewrote blocking, mood and lighting as persistent reference constraints only; rewrote scene direction to retain only scene-specific staging, evidence, action geography and dramatic turns.

### 3. Identity residue
`continuity_matrix.json` still contained retired principal identities after the active character and scene data had been renamed.

Action taken: normalized the continuity matrix to John Mercer, Kellen Cartwright, AX10M, Nico-14 and Nathan Price. Repository search now returns no results for the retired full names Ryen Hale, Kera Dalen, Tessera, Lume Kirin or Drex Malin.

### 4. Visual sequencing
Issue 1 already contains useful visual contrast:
- P1 intimate medical procedure
- P2 hazardous-zone scale
- P3 restrained information-space beat
- P4 city splash
- P5–10 escalating civic rescue / institutional reaction
- P11 clinic normalcy
- P12–14 quiet repair and investigation
- P15 machine cognition
- P16–17 distrust/convergence
- P18 infrastructure scale
- P19–20 targeted action
- P21 silent reveal
- P22 evidence discovery
- P23–24 ideological contact under purge pressure
- P25 political aftermath
- P26 threat hook

The sequence should preserve these contrasts. Do not allow a global mood, palette, panel density or camera grammar to flatten them.

### 5. Story-to-image ratio
The long-form Issue 1 draft generally leads with page action and purpose. The compact scene layer is also concise after sanitization. The remaining production risk is assembly: if an assembler concatenates full character notes + series bible + global mood + lighting + blocking + negatives for every page, repetition will return even though source files are scoped correctly.

Recommendation: assembled image prompts should include:
1. page-specific story/panel data first;
2. only the character reference fields for characters actually present;
3. only the location reference for the active setting;
4. compact series-level visual constraints once;
5. no repeated arc/theme/political-doctrine prose unless directly required by the page.

## Comparison to successful earlier method
A repository search did not locate a package named `Shattering of the Corridors` or `shattering`, so no direct structural comparison could be made from RexPrompt. The audit therefore uses the stated successful-method principle: unique page intention must dominate persistent scaffolding. If that earlier package exists under another slug/title, compare its assembled prompt output before finalizing the Division Threshold assembler.

## Production gate before image generation
Do not generate sequential Issue 1 pages from the current 11 scene records as if they were page records.

Required next production transformation:
- create P01–P26 explicit page data from `issue_01_draft_01.md`;
- give each page a distinct visual job and panel/action sequence;
- reference rather than duplicate persistent character/world/style data;
- assemble a review PDF from the exact generation-facing data;
- read the PDF in sequence and flag repeated prose, repeated compositions, excessive panel density, and any page where global scaffolding is more prominent than the unique beat;
- revise the data before first image generation.

## Sanitization result
Story content preserved. Identity residue corrected. Global defaults narrowed. Scene direction de-boilerplated. No released canon changed.
