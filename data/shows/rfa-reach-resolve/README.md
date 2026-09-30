# Rex Fleet Academy: Reach and Resolve

## Current production state

This package initiates **Rex Fleet Academy: Reach and Resolve** as a separate RexPrompt series.

- Series ID: `rfa-reach-resolve`
- Active show: `rfa-reach-resolve-i01`
- Active issue: Issue 1 — *The Two Failures*
- Production unit: `PAGE`
- Active page recipes: 24
- Structure: 1 opening Academy splash + 22 story pages + 1 closing teaser
- Future issues: planned in `series_architecture.json` but intentionally **not registered** in `data/shows.json` until they have real production recipes
- Visual reference baseline: not yet established

## Series purpose

Reach and Resolve is an Academy doctrine/history line, not another Thunderbreak political plot.

The recurring Academy cohort learns by working through historical records, simulations, and field problems. The story engine is:

1. an instructor poses a practical problem;
2. cadets expose different assumptions;
3. a historical or operational case is dramatized as a real story;
4. the class returns to the problem with fewer easy answers.

The Academy framing must never become static exposition. Historical material is shown as lived action with finite cargo, failing machinery, route windows, consent, and human consequences.

## Doctrine lock

- **Reach**: restore contact, trade, rescue capacity, knowledge exchange, and coexistence.
- **Resolve**: sustain viable communities, infrastructure, memory, and decision-making when connection fails.
- Reach is not automatically expansion.
- Resolve is not automatically isolation.
- Resolve makes Reach possible; Reach gives Resolve purpose.
- The practical question is how much of each a situation requires under uncertainty.

## Issue 1 canon bridge

Issue 1 deliberately grows out of the end of *Rex Fleet Academy: Shattering of the Corridors*.

It uses the first multiworld rescue vessel launched from the Resolve Circle and preserves Ava Seltos and Ruben Markham as their established historical selves. The new Orison and Varda cases extend that early-relief period without turning it into the mature Rex Fleet or importing later faction uniforms.

## Production IDs

- Page IDs: `RFA_RR_I01_P01` through `RFA_RR_I01_P24`
- Source-scene groups: `RFA_RR_I01_S01` onward
- Teaser: `RFA_RR_I01_TEASER`

## Registration boundary

Only Issue 1 is assembler-visible at this checkpoint. The remaining five issues are planning data, not generation units. This is intentional: RexPrompt should not contain placeholder pages that look production-ready merely because they are selectable.
