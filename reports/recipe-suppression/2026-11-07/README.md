# RexPrompt — All-series, issue-by-issue, page-by-page ingredient suppression audit

Source: current RexPrompt repository, AFTER applying all configured scene and dialogue overlays, including compressed sources. Assembled output uses the actual pageAssembly and assembleScene functions from index.html. No creative source or suppression setting changed.

Interpretation: PAGE means authored per-page setting; CONFIG means series/configuration inheritance; DEFAULT means assembler fallback. An empty promptSuppress means no page-specific suppression, NOT proof that the section is emitted. No ingredient content is different from an actively suppressed ingredient.

Flags identify candidates for inspection, not editorial findings or permission to suppress. Full content and neighboring beats require human review before changing any page. Full Performance is kept separate from Rex Fleet.

## Coverage

- 138 registered configurations; 2971 configured appearances; 2971 unique series/unit pairs; 25 distinct production series.
- 0 source loading failures; 3 assembly failures.

## Results by series

| Series | Issues | Unique units | Explicit suppression list | Nonempty suppression | Entirely inherited page policy | Flagged units | Detailed audit |
|---|---:|---:|---:|---:|---:|---:|---|
| Azure Reach | 6 | 150 | 101 | 101 | 49 | 23 | [Every page](azure-reach.md) |
| Backyard Rockets | 8 | 178 | 112 | 112 | 66 | 67 | [Every page](backyard-rockets.md) |
| Division Threshold | 24 | 228 | 186 | 186 | 34 | 0 | [Every page](division-threshold.md) |
| Echoes of a Forgotten War | 8 | 157 | 0 | 0 | 54 | 7 | [Every page](echoes-forgotten-war.md) |
| Low Tide Signal | 7 | 199 | 178 | 178 | 21 | 2 | [Every page](low-tide-signal.md) |
| Rex Fleet | 12 | 314 | 256 | 157 | 58 | 33 | [Every page](rex-fleet.md) |
| Rex Fleet Academy: Anomalies of Broken Space | 1 | 24 | 0 | 0 | 24 | 14 | [Every page](rex-fleet-academy-anomalies.md) |
| Rex Fleet Academy: Between the Beacons | 1 | 27 | 0 | 0 | 27 | 17 | [Every page](rex-fleet-academy-between-beacons.md) |
| Rex Fleet Academy: The Core Worlds | 1 | 24 | 0 | 0 | 24 | 15 | [Every page](rex-fleet-academy-core-worlds.md) |
| Rex Fleet Academy: Doctrine of Many Crowns | 1 | 24 | 0 | 0 | 24 | 4 | [Every page](rex-fleet-academy-doctrine-many-crowns.md) |
| Rex Fleet Academy: Navigating the Mirrorfold | 1 | 24 | 0 | 0 | 24 | 7 | [Every page](rex-fleet-academy-navigating-mirrorfold.md) |
| Rex Fleet Academy: Physics of the Lattice | 1 | 24 | 0 | 0 | 24 | 20 | [Every page](rex-fleet-academy-physics-lattice.md) |
| Rex Fleet: Aegis Vigil | 1 | 24 | 0 | 0 | 24 | 5 | [Every page](rex-fleet-aegis-vigil.md) |
| Rex Fleet: Crimson Warden | 1 | 28 | 0 | 0 | 28 | 6 | [Every page](rex-fleet-crimson-warden.md) |
| Rex Fleet — Full Performance | 12 | 425 | 63 | 63 | 362 | 3 | [Every page](rex-fleet-full-performance.md) |
| Rex Fleet: Ghostwind Arrow | 1 | 22 | 0 | 0 | 22 | 13 | [Every page](rex-fleet-ghostwind-arrow.md) |
| Rex Fleet: Glass Horizon | 1 | 24 | 0 | 0 | 24 | 2 | [Every page](rex-fleet-glass-horizon.md) |
| Rex Fleet: Slip Knife | 1 | 22 | 0 | 0 | 22 | 6 | [Every page](rex-fleet-slip-knife.md) |
| Rex Fleet: Stormwell Archive | 1 | 22 | 0 | 0 | 22 | 5 | [Every page](rex-fleet-stormwell-archive.md) |
| Rex Fleet Academy: Reach and Resolve | 1 | 24 | 0 | 0 | 24 | 12 | [Every page](rfa-reach-resolve.md) |
| Shattering | 6 | 150 | 0 | 0 | 150 | 82 | [Every page](shattering.md) |
| Stardust Station | 10 | 249 | 162 | 162 | 52 | 86 | [Every page](stardust-station.md) |
| Sun Comes Through — The Musical | 8 | 16 | 0 | 0 | 16 | 16 | [Every page](sun-comes-through-musical.md) |
| Sunforge Outlaw | 12 | 296 | 260 | 260 | 36 | 31 | [Every page](sunforge-outlaw.md) |
| Vikings 2026! | 12 | 296 | 16 | 16 | 31 | 0 | [Every page](vikings-2026.md) |

## Flag explanation

- ASSEMBLY_ERROR / PANEL_NOT_EMITTED / DIALOGUE_NOT_EMITTED / CONTINUITY_NOT_EMITTED: verify assembler correctness; page does not have a validated complete output.
- VISUAL_CAST_SUPPRESSED: explicitly suppressed cast despite visible-only character references; inspect visual reference sufficiency.
- FULL_CAST_BY_DEFAULT / REPEATED_FULL_CAST: full-character prose is implicit or repeated, potentially unnecessary alongside established identities.
- REPEATED_FULL_SETTING / REPEATED_SETTING_CONTINUITY: adjacent same-setting pages include duplicate persistent environment descriptions.
- TEMPLATE_SUMMARY / DUPLICATE_SUMMARY: repeated or formulaic summary may duplicate actual panel/action writing.
- CROSS_CONFIGURATION_CONFLICT: same unit resolves differently across production configurations; investigate before making policy assumptions.

## Verification and caveats

- Exact entry paths for each page/scene/cast unit are included in the CSV; all units are listed in the series pages.
- The report assesses effective ingredient delivery and obvious duplication. It cannot declare a suppression artistically appropriate without reading the distinctive content and adjacent context.
- No approved artwork, dialogue, story, released canon, or suppression configuration is edited.

## Errors

None.
