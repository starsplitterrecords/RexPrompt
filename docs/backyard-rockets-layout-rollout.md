# Backyard Rockets — issue-level page-composition rollout

**Scope:** Season 1, scripted interior pages of Issues 3–8. Art direction is encoded in the exact current RexPrompt `pageLayout` contract directly within each canonical compressed production page. These are **production page-layout choices**, not story rewrites or finalized generated artwork.

**Released boundary:** Issues 1–2 are already published in StarSplitterVisions as an opening combined edition. They use earlier production structures, including some pages with no explicit `panelPlan`. This rollout does not touch their scripts, page layouts, approved artwork, or publication state. The editorial opening and closing splashes in all eight issues already express a single-page design through existing production prose, so they have not been wrongly treated as separate narrative panels.

## Composition strategy by issue

| Issue | Page layouts | Dramatic visual rhythm |
|---|---:|---|
| 03 — Public Sky | 19 | Wide basin routes give way to exact consent, limited tests and the missed launch window; the lost launch is given more visual weight than gratuitous ignition |
| 04 — Trip Point | 18 | Physical stability/control-surface problems alternate with community governance; decisions to respect safeguards remain legible alongside flight |
| 05 — Reserve Margin | 21 | Real ledgers, uncertain data, restricted water, removed payload, quiet character talk and a planned radio blackout; documentary layouts maintain aligned evidence |
| 06 — Ground Loop | 19 | Mundane freight, noisy motors, mechanical cutouts, vulnerable ledges, distributed communications and the surrendered master override; success is visibly decentralized |
| 07 — Ablative Armor | 19 | Salvage and iterative tile testing culminate in human consequences: honest test data, Rhonda's transfer, her quiet detention and an unfinished rescue convoy |
| 08 — Sky-Piercer | 22 | One vehicle unifies separate engineering disciplines, while distributed local control persists without its founders; the sandstorm launch finally earns a large flight image, followed by intimate ordinary aftermath |

The eight allowed production architectures used are `asymmetric`, `montage`, `freeform`, `vertical`, `grid`, `quiet`, `open`, and `splash-with-insets`. The style distribution is intentional rather than a hard quota. No scene gains or loses panels.

## Canonical production sources

The page layouts and chef-facing scope fields are stored directly in the compressed episode data:

```text
data/shows/backyard-rockets-s1/encoded/scenes_e03_public_sky.json.gzb64
data/shows/backyard-rockets-s1/encoded/scenes_e04_trip_point.json.gzb64
data/shows/backyard-rockets-s1/encoded/scenes_e05_reserve_margin.json.gzb64
data/shows/backyard-rockets-s1/encoded/scenes_e06_ground_loop.json.gzb64
data/shows/backyard-rockets-s1/encoded/scenes_e07_ablative_armor.json.gzb64
data/shows/backyard-rockets-s1/encoded/scenes_e08_sky_piercer.json.gzb64
```

There is no separate layout or recipe-scope override. Dialogue, scene membership, cast references, panel plans and production direction remain in those same canonical records. Git history holds the former revision layers.

## Validation and next production gate

Run `node tools/test_backyard_rockets_layouts.cjs` and the general page assembly tests. The issue-wide regression compares each assembled recipe with the unprofiled original. The entire original `[PANEL PLAN]` and every downstream ingredient must remain exactly identical after page-layout addition. It confirms:

- 118 embedded compositions across 118 existing interiors
- all 559 original panel beats, no extra or duplicate references
- exact scripted dialogue/order/continuity preserved
- eight permitted composition architectures
- no production overlay or script changes to the released Issues 1–2
- editorial opener and teaser units remain untouched

**Visual production remains separate:** No image render or artwork approval is implied by schema validation. Before rendering, compare the assembled recipe with the released visual baseline and approved current page images. Check actual characters, location geography, equipment, page-to-page rhythm, balloon legibility and the panel hierarchy at print/mobile size. The first rendered pages may reveal lettering-density problems that require an editorial repair rather than automatically adding pages.

For first visual QA, compare a consent/missed-launch page from Issue 3, a failed thermal-test page and detention page from Issue 7, and the Sky-Piercer launch with a quiet end-of-issue page from Issue 8. These contrast the new hierarchy mechanisms without treating a splash as the default.
