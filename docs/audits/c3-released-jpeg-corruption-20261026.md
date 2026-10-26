# Published JPEG corruption and resolution audit — verified source bytes (2026-10-26)

## Authority and reproducibility
Source: `starsplitterrecords/StarSplitterVisions`, canonical `main` byte assets. Read-only GitHub Actions **Audit released JPEG completeness**, successful run https://github.com/starsplitterrecords/StarSplitterVisions/actions/runs/40318418205, scans all `sites/visions/public/images/pages/**/*.jpg` and `covers/**/*.jpg`. Source implementation is `sites/visions/scripts/audit-published-jpegs.cjs` (StarSplitterVisions PR #146). It parses JPEG SOI, SOF dimensions and requires complete EOI (`FF D9`) marker. The Git tree's blob lengths matched the cap-like source byte lengths, confirming incomplete canonical source blobs, *not merely a connector display/truncation artifact*.

**Coverage:** 163 published-page-or-cover JPEG files checked; **6 source-incomplete / corrupted**, **157 with proper file start/end and dimensions**. This scan does not prove intermediate scan segments or decoder pixel fidelity; it is materially stronger than checking only file presence/signature.

## Exact production-corruption defects
| Defect ID | Series / issue / published path suffix | Severity | Source bytes and pixel dimensions | Evidence | Required action |
|---|---|---|---|---|---|
| C3-RF-I01-BIN-002 | Rex Fleet / I01 / `page-002.jpg` | **Blocker: truncated published JPEG** | 786,444 bytes; 1440×2160; no EOI | Action run 40318418205 `JPEG CORRUPT` file path `public/images/pages/rex-fleet/issue-01/page-002.jpg` | Recover exact approved complete original/master for this released JPEG; compare visually and reexport affected PDF. |
| C3-RF-I01-BIN-004 | Rex Fleet / I01 / `page-004.jpg` | **Blocker: truncated published JPEG** | 786,444 bytes; 1440×2160; no EOI | Same run / exact path `.../page-004.jpg` | Recover approved complete source; no synthetic JPEG-end padding, resizing or alternate generation. |
| C3-RF-I01-BIN-009 | Rex Fleet / I01 / `page-009.jpg` | **Blocker: truncated published JPEG** | 786,445 bytes; 1440×2160; no EOI | Same run `.../page-009.jpg` | Recover complete source. Previously observed soft text is **not** an isolated mastering claim until full source is restored. |
| C3-RF-I01-BIN-011 | Rex Fleet / I01 / `page-011.jpg` | **Blocker: truncated published JPEG** | 786,444 bytes; 1440×2160; no EOI | Same run `.../page-011.jpg` | Recover complete approved source and verify adjacent page continuity. |
| C3-RF-I01-BIN-015 | Rex Fleet / I01 / `page-015.jpg` | **Blocker: truncated published JPEG** | 786,445 bytes; 1440×2160; no EOI | Same run `.../page-015.jpg` | Recover complete source; prior softness/lettering defects cannot be confidently separated from truncation. |
| C3-SSD-I01-BIN-020 | Stardust Station / I01 / `page-020.jpg` | **Blocker: truncated published JPEG; visual inspection unavailable** | 786,443 bytes; 1024×1536; no EOI | Same run `public/images/pages/stardust-station/issue-01/page-020.jpg` | Retrieve approved complete original via historical IMG, authoritative source ZIP, or recovered generation; then inspect P19→P20→P21 and rebuild issue PDF if necessary. |

**Recipe-ID mapping:** Rex Fleet published P002→approximately script `RF_I01_P01`, P004→`RF_I01_P03`, P009→`RF_I01_P08`, P011→`RF_I01_P10`, P015→`RF_I01_P14` due to released P001 editorial; verify exact historical release manifest before changing anything. Stardust P020 likely matches `SDS_S1E01_P20` but requires original authoring revision confirmation. Exact published paths remain authoritative.

## Print-resolution caution
Scan found 126/163 JPEGs have source width under 200 pixels per inch **under a hypothetical 6.625-inch comic trim**. There is no approved physical trim/bleed specification in this audit, so this **is a nonbinding risk metric**, not an automatic print failure. Common actual source dimensions include 1032×1575 and 1024×1536. Obtain actual native master and target trim, bleed, color profile and printer DPI before making a production-resolution decision. Re-encoding a low-resolution source or resizing it does not restore image detail.

## Relationship to earlier reports
- The previous claim that Stardust P020 could not be inspected because of the GitHub connector cap is **superseded**: its *stored released JPEG itself is truncated*.
- Several visually previewed Rex Fleet pages were incompletely encoded JPEG files, even though forgiving preview rendering showed partial images. Such previews do not count as production-quality passes.
- The earlier Rex Fleet P009/P015 ‘soft-text’ observations are superseded by the stronger binary source-corruption blocker.
- No image files were changed by this audit. Restore originals from known approved provenance and rebuild only affected releases when authorized.
