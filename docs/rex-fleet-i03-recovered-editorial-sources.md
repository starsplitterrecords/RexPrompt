# Rex Fleet Issue 3 — recovered editorial binary sources (October 25, 2026)

Three original historical File Library assets were recovered and byte-verified; the source images are **not yet committed into the approved-draft manifest**:

- `Rex-Fleet-Issue-3-Editorial-Endmatter.png`: full PNG 2400 × 3840, with embedded ICC profile. Library ID `file_0000000033cc81f5afb10f03273a14f4`. SHA-256: `318b43cc91ddb9951a7e8717698c4b87b66392d0c1cf08a57c6329cf5f1d4c20`. Visually inspected against recipe `RF_I03_EDITOR_ENDMATTER`; intended for its end-matter editorial slot, without fabricating the unavailable Issue 4 inset.
- `Rex-Fleet-Issue-3-Editorial-Endmatter.svg`: original editable source 2400 × 3840, containing two embedded raster elements at 2400-pixel native widths. Library ID `file_000000009b9081f58533d13bbf47320e`.
- `Rex-Fleet-Issue-3-Closing-Teaser.svg`: source SVG 2400 × 3840 linked to recipe `RF_I03_EDITOR_CLOSE`, but its large embedded raster image is only **991 × 1587**. Merely rasterizing this SVG at 2400 × 3840 will not supply a genuinely native-resolution master. Library ID `file_00000000a3f081f58bf442265ec3f701`.

Persistent source archive: `/Star Splitter Visions/Recovered Artwork/Rex_Fleet_I03_editorials_origins.zip`; includes source binaries and exact hashes.

**Preservation does not equal approval.** The recovery files must be committed with the correct original bytes and separately reviewed before the respective RexPrompt draft entries can be added. Issue 3 currently lacks approved draft entries for P28, P29, P30, EDITOR_CLOSE, and EDITOR_ENDMATTER. Do not invent page approvals or regenerate/recompress originals merely for storage. Production release remains blocked until the final approved book inventory is complete and mastered.

The approved-draft persistence contract requires an atomic binary blob plus manifest update; GitHub text-file operations alone are insufficient for uploading multi-megabyte originals recovered to the local execution container.
