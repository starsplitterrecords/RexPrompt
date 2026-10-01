# Rex Fleet Academy: Between the Beacons — visual reference baseline

Image production has not started.

Before generating P01, establish continuity from released Rex Fleet canon and approved current Rex Fleet production. Use Shattering only for historical BHA/corridor lineage where chronologically appropriate. Use the existing Navigating the Mirrorfold package where the preserved final story page (now P25) and closing teaser P26 touch established Mirrorfold visual language.

Do not use the previous Academy page as the sole reference for a new scene. Preserve the functional color grammar: green civilian/public/ecology; Fleet blue-gold-white; bright-red Shards; purple survey; subtle-cyan blockade runner; yellow maintenance/science; dark-purple/gold Tempest; deep-crimson/gold Crimson.

No Between the Beacons image is approved or durable at this checkpoint.


Editorial pages P01 and P26 are premium full-page splashes. They require deliberate negative space for exact integrated typography; do not use story-panel layouts or treat their copy as in-world signage, UI, or narration boxes.

## Cover reference gate

- Cover recipe authority lives in `data/shows/rex-fleet-academy-between-beacons/covers.json` and is exposed through the existing RexPrompt assembler as a `COVER` production unit.
- Issue 1 is the founding cover. Before generating it, retrieve and visually inspect the released Rex Fleet Issue 1 cover pixels from StarSplitterVisions as parent-family guidance for masthead weight, publisher-lockup logic, issue-number prominence, and premium finish only.
- Once `RFA_BB_I01_COVER` is approved, persist the exact approved pixels at `production/references/rex-fleet-academy-between-beacons/assets/covers/issue-01-cover-trade-dress.png`.
- Then update `cover-production-normalization.json` from `bootstrap-required` to active and mark the founding cover as `approved-trade-dress-reference`.
- For every later cover, the actual approved Issue 1 pixels must be brought into active multimodal context and inspected before generation. Paths, hashes, text descriptions, thumbnails, or memory do not satisfy the pixel-read gate.
- The Issue 1 cover controls recurring trade dress only. The current assembled cover recipe controls each later issue's actual selling image, setting, cast, composition, palette, lighting, action, and spoiler ceiling.
