# Sunforge Outlaw — Recipe suppression and sanitation

**Scope:** 260 story interiors across Issues 1–12. Editorial introductions, covers, teasers and closing units are unchanged.

## Authoritative layers

The authored story stays in pages_eNN.json. The separately approved dramatic page composition stays in editorial/page_layouts_eNN.json. The new editorial/page_assembly_eNN.json overlay runs afterward and stores only chef-facing suppression and reference modes. All overlays are strict merge-by-ID; raw story dialogue, panel actions, and page count remain untouched. The one explicit correction is Issue 3 page 1's setting reference: the trio is still on a Sunfields road, not inside the Mirage Club.

## What gets through

| Ingredient | Editorial decision |
| --- | --- |
| Dialogue, panels, continuity, pageLayout, production brief | Retain fully, without rewriting |
| Character references | Full descriptions at select true introductions; concise cast names otherwise. The distant Rider remains visually anonymous |
| Locations | Full establishing/return views; short named setting on consecutive pages |
| Repeated generic Sunfields region | Omit in all 260 story recipes; the production brief and page geography already establish it |
| Summaries | Omit where rich panels and pageLayout already express the beat in Issues 1–3; retain on critical turns and throughout the more lightly scripted Issues 4–12 |
| Recurring performance direction | Selective on the richly staged Issues 1–3; retain on Issues 4–12 because their shorter panel outlines still benefit from it |
| Exact quoted dialogue embedded in visual panel prose | Safely deduplicate in 40 pages of Issues 2–3, preserving canonical dialogue and panel ownership |

## Strict duplicate-lettering sanitation

The page-specific field `promptPanelLetteringMode: "indexed"` invokes the deterministic `preparePanelLettering(scene)` routine. It parses the `EXACT SCRIPTED LETTERING:` suffix on each panel and requires every speaker and quoted word to match the next canonical `dialogueInline` item exactly. `NO LETTERING` panels remain silent. On success the panel retains its complete *visual* prose followed by a short reference such as `LETTERING: dialogue lines 3–5`, and the unchanged exact dialogue appears once in `[DIALOGUE]` prefixed with its actual panel number. Any missing line, changed speaker, unparseable suffix, or unmapped line causes assembly to fail. Other pages and series remain unchanged.

## Continuity exceptions

- Issue 3 P01: correct the road location to Sunfields at assembly only; P02 introduces the Mirage Club.
- Issue 8: retain unusually frequent full location/terrain references because the Rider's distance depends on believable repeated landmarks and precise spatial continuity.
- Issues 9, 11 and 12: re-establish locations at consequential human or prop/chronology transitions, rather than every Nth page.
- Issues 4–12: retain issue summaries and global acting direction, which the shorter panel plans cannot replace safely.

## Tests and workflow

Run `node tools/test_sunforge_recipe_sanitation.cjs`, followed by the established page-assembly tests. CI validates the 260-page inventory; all 1,073 scripted panel beats; all 1,388 dialogue/caption items; location references; complete panel-dialogue mapping; unchanged `pageLayout`; and preserved production brief. It reports the source-vs-chef recipe length change. Invalid or missing data must fail rather than be silently suppressed.

This is a **production recipe cleanup**, not a rewrite of story, character canon, or source documents; nor does it replace actual rendered-page quality review.
