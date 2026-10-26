# GitHub historical contribution dispositions — 2026-10-25

**Authority:** current main of RexPrompt and StarSplitterVisions; integration overlap decisions in [RexPrompt Issue #316](https://github.com/starsplitterrecords/RexPrompt/issues/316). This document records the evaluated files and tests; it is not an authorization to revise released art, approved references, or unapproved writing.

## Scope and method

API inventory: RexPrompt 311 pull requests (286 merged, 25 closed without merge, none open), 412 retained branches including main; Visions 136 PRs (117 merged, 19 closed without merge, none open), 40 retained branches including main. Original closed-PR branch tips were compared against current main by commit ancestry and per-file diffs, not assumed missing merely because commits remain ahead. Branches lacking PR association are included in the companion full-ref branch divergence artifact. Latest main checks passing at audit: RexPrompt dashboard/security/source audits and Visions both-site build/deep-link validation.

**Caution:** a historical branch with ahead commits and changed files may be superseded, never approved, or intentionally rejected. Do not equate git ahead count with missing product features. PR squash merges often leave historical heads divergent. A closed PR remains closed unless a *specific* compatible missing change can be proven against modern code and tests.

## RexPrompt — all 25 closed-unmerged PRs

| PR | Disposition | Evidence and action |
|---|---|---|
| [#300](https://github.com/starsplitterrecords/RexPrompt/pull/300) | incorporated | All four proposed files have identical Git blob SHAs on main; #298/#307/#311 retain canonical readback. No cherry-pick. |
| [#273](https://github.com/starsplitterrecords/RexPrompt/pull/273) | superseded | Selective merged #290; subsequent #291/#294 guard page layout source of truth; historic mass rollback conflicts with modern overlays. |
| [#265](https://github.com/starsplitterrecords/RexPrompt/pull/265) | superseded | PR body identifies merged #266 as successor for Rex Fleet Issue 5 dialogue. |
| [#258](https://github.com/starsplitterrecords/RexPrompt/pull/258) | superseded | PR body identifies merged #262 as successor for Rex Fleet Issue 4 dialogue. |
| [#251](https://github.com/starsplitterrecords/RexPrompt/pull/251) | superseded | Merged #286/#291 and deduplicated by #294; stale runtime architecture rejected. |
| [#226](https://github.com/starsplitterrecords/RexPrompt/pull/226) | incorporated-by-history | Branch tip is ancestor of main (ahead 0; no tip/main tree differences). |
| [#224](https://github.com/starsplitterrecords/RexPrompt/pull/224) | retained editorial exception | Issue 5 encoded story file differs on tip/main; closure alone does not prove its causality revision was accepted. Do not replace later script without editorial comparison. |
| [#197](https://github.com/starsplitterrecords/RexPrompt/pull/197) | superseded | Merged #198 implements newer issue-by-issue Vikings cover blocking; historical cover/direction files differ from main. |
| [#185](https://github.com/starsplitterrecords/RexPrompt/pull/185) | superseded-with-divergence | Modern Azure cover shelf exists and includes released Issue 1 canon; old cover branch differs. No bulk rollback. |
| [#182](https://github.com/starsplitterrecords/RexPrompt/pull/182) | superseded | Merged #186 installs Between the Beacons cover; #199 replaces its visual approach with Academy demonstration. |
| [#181](https://github.com/starsplitterrecords/RexPrompt/pull/181) | superseded | Merged #183 establishes current Stardust cover shelf and released Issue 1 trade dress. |
| [#159](https://github.com/starsplitterrecords/RexPrompt/pull/159) | superseded | Merged #160 rebases Echoes editorial bookends into modern 145-unit production design. |
| [#124](https://github.com/starsplitterrecords/RexPrompt/pull/124) | retained normalization alternative | Old Vikings Issues 2-5 normalized page files and shows registry differ from main; modern active page/assembly contract takes precedence. Editorial comparison required for any claimed missing beat. |
| [#104](https://github.com/starsplitterrecords/RexPrompt/pull/104) | intentionally superseded | Closed PR explicitly labeled superseded; merged #105 normalizes Low Tide. Old temporary recovery scratch should not return. |
| [#96](https://github.com/starsplitterrecords/RexPrompt/pull/96) | retained legacy design | Stardust writing/chef separation branch diverges in encoded story files and shelves; modern assembler and later approved continuity supersede mechanics. Do not overwrite current script. |
| [#75](https://github.com/starsplitterrecords/RexPrompt/pull/75) | superseded | Merged #76 handles Low Tide normalization in current contract; related Division Threshold checks have newer validator/scoped overlay implementation. |
| [#56](https://github.com/starsplitterrecords/RexPrompt/pull/56) | retained legacy recovery | Old Stardust Issue 4 page file differs; current series has later complete recipe and visual density work. Do not promote this historical variant automatically. |
| [#39](https://github.com/starsplitterrecords/RexPrompt/pull/39) | incorporated-by-history | Stardust Kreeb visual-canon branch tip is ancestor of main. |
| [#35](https://github.com/starsplitterrecords/RexPrompt/pull/35) | superseded | Legacy Rex Fleet context sanitation includes older index.html and compressed scripts; later clean assembly/continuity takes precedence. |
| [#34](https://github.com/starsplitterrecords/RexPrompt/pull/34) | superseded | Legacy page-generation readiness touches older assembler and encoded sources; modern page-scoped assembly/tests replace it. |
| [#33](https://github.com/starsplitterrecords/RexPrompt/pull/33) | superseded | Early Rex Fleet sanitation predecessor; later package/renderer repairs supersede. |
| [#24](https://github.com/starsplitterrecords/RexPrompt/pull/24) | retained legacy bible alternative | Earlier Echoes character/bible files still differ on branch; main later developed episode scripts and approved identities. No authorized replacement. |
| [#22](https://github.com/starsplitterrecords/RexPrompt/pull/22) | retained legacy writing alternative | Stardust Issues 4-10 writing differs from current encoded/page structures. Preserve branch as noncanonical historical draft. |
| [#10](https://github.com/starsplitterrecords/RexPrompt/pull/10) | intentionally excluded | Temporary Stardust page-extraction workflow; not production implementation or approved asset. |
| [#6](https://github.com/starsplitterrecords/RexPrompt/pull/6) | superseded | Historical Azure Issue 1 page recipe prototype; released Issue 1 and newer RexPrompt package control canon. |

## StarSplitterVisions — all 19 closed-unmerged PRs

| PR | Disposition | Evidence and action |
|---|---|---|
| [#106](https://github.com/starsplitterrecords/StarSplitterVisions/pull/106) | superseded | Records cleanup branch explicitly superseded by merged #107 consolidated site. |
| [#98](https://github.com/starsplitterrecords/StarSplitterVisions/pull/98) | retained cosmetic exception | Pre-consolidation root src CSS differs. Current site lives under sites/visions and has later responsive design; no blind CSS transplant. |
| [#93](https://github.com/starsplitterrecords/StarSplitterVisions/pull/93) | superseded | Merged #94 wired Azure cover in current asset contract. |
| [#91](https://github.com/starsplitterrecords/StarSplitterVisions/pull/91) | retained product-design exception | ContextProduct schema remains absent from current site architecture; unrelated closed alternative, not approved for auto-introduction. |
| [#89](https://github.com/starsplitterrecords/StarSplitterVisions/pull/89) | superseded | Merged #90 replaced Vikings reader preview stub; later published release canon controls. |
| [#73](https://github.com/starsplitterrecords/StarSplitterVisions/pull/73) | functionally incorporated | Current sites/visions/src/components/PressPage.jsx and /press navigation exist; older root src implementation is obsolete. |
| [#72](https://github.com/starsplitterrecords/StarSplitterVisions/pull/72) | retained product-design exception | Legacy News detail/index system not reproduced as standalone pages in current Visions site; remains closed product proposal, not silently merged. |
| [#70](https://github.com/starsplitterrecords/StarSplitterVisions/pull/70) | partially incorporated | Current SoundtrackCard supports content display, but old standalone soundtrack index/detail architecture is not restored. Requires product decision. |
| [#69](https://github.com/starsplitterrecords/StarSplitterVisions/pull/69) | partially incorporated | Current ExtrasRail supports content display; old standalone Extras index/detail architecture is not restored. Requires product decision. |
| [#68](https://github.com/starsplitterrecords/StarSplitterVisions/pull/68) | functionally incorporated | Live /read reader route and released browsing are present; old root src code displaced by new sites/visions App. |
| [#67](https://github.com/starsplitterrecords/StarSplitterVisions/pull/67) | functionally incorporated | Current site has SeriesIndex and direct /series routing; old root src component path is not canonical. |
| [#66](https://github.com/starsplitterrecords/StarSplitterVisions/pull/66) | functionally incorporated | Current site has homepage editorial structure; obsolete root src implementation not copied. |
| [#65](https://github.com/starsplitterrecords/StarSplitterVisions/pull/65) | functionally incorporated | AboutPage, ContactPage, PressPage and route navigation exist in current sites/visions. |
| [#64](https://github.com/starsplitterrecords/StarSplitterVisions/pull/64) | intentionally not revived | Legacy root src barrel exports and architecture are incompatible with current two-site structure. No supported need for that architectural rewrite. |
| [#61](https://github.com/starsplitterrecords/StarSplitterVisions/pull/61) | partially incorporated | Current reader route/order utilities are present; historical alternative selectors were not ported verbatim. |
| [#59](https://github.com/starsplitterrecords/StarSplitterVisions/pull/59) | superseded | Current React site and content checks replace old root src extras/soundtrack crash handling. |
| [#57](https://github.com/starsplitterrecords/StarSplitterVisions/pull/57) | superseded | Current bounded reader routing and merged #138/#139 deep-link validation replace early root App.jsx patch. |
| [#56](https://github.com/starsplitterrecords/StarSplitterVisions/pull/56) | superseded | Live release asset validation in #136 tests actual site assets; old root scripts/validate-content.js alternative not restored. |
| [#48](https://github.com/starsplitterrecords/StarSplitterVisions/pull/48) | superseded | Old root App.jsx soundtracksBySeries crash workaround predates current sites/visions architecture. |

## Concurrent implementation architecture — Issue #316 decisions

1. **A1 skills/loaders:** owned by the separate active implementation lane. This reconciliation must not duplicate or replace its loaders.
2. **Keeper A2/A4:** one production/references/reference-keeper-manifest.json; retain valid SHA-matched #285/#293/#297/#306/#317, follow #305/#310 UI resolver; do not re-add the truncated Checkpoint 9 image rejected by #304.
3. **A3 pages:** #287 Azure image mappings and #308 evidence-only Shattering/Rex Fleet recovery retained; no automatic new approval.
4. **B1:** #298/#307 plus canonical prepare_img_readback.cjs and single-image workflow; #311 removes #299 Python/workflow duplicate and adds original-image issue bundles. Closed #300's workflow, runtime docs and JS test integration are already exact SHA matches to main.
5. **B2:** #289 native preflight + #301 contact-sheet proofing + merged #322 evidence-gated mastering, publication profiles and approval verification are one compatible current-main pipeline. #322 passed mastering CI but does **not** certify existing artwork for print; profiles require actual printer approval.
6. **B3:** #288/#295 browser/export guards + #302 strict offline ZIP/PDF builder + #318 and newly merged #324 curated portfolio book inventories. Work/b3-complete-book-rebase-20261025 remains divergent, including a stale story-recipe fallback in its test text, contrary to the no-incomplete-release decision. Do not merge as-is; salvage only proven stronger validations independently.
7. **C1/C2/C3:** #286/#290/#291/#294, #292, #296/#303/#309 plus merged #323 strict portfolio assembler regression and #333 source-byte lock remain complementary. #321 fixes the dashboard config count per #316; unit count requires assembled recipe inventory, not data/shows.json length.
8. **D1/D2/D3:** Dashboard PRs #328 and #329 are overlapping assembler-backed revisions and should be reconciled into one validated implementation, not blindly merged sequentially. Merged #330 supplies the distinct C3 visual/provenance defect register. Notion remains editorial/status authority; StarSplitterVisions release approval remains separate. Visions #136/#138/#139 enforce releases and deployed deep links. Their passing GitHub CI is not proof of mastering/lettering visual pass.
9. **Autonomous production:** last.

## Important retained branches without a current PR

| Branch or cohort | Verified tip/main evidence | Disposition |
|---|---|---|
| work/b2-production-mastering-gates-20261025 | Merged through #322 after issue-level proof and approval-gate tests; the historical branch is retained | **Incorporated through merged PR**, not a missing capability. Current profile status remains working until actual printer/human signoff. |
| work/b3-complete-book-rebase-20261025 | Divergent: five exporter/docs/test files; code and test reference legacy story-unit fallback | **Unresolved implementation conflict.** Do not merge unless rewritten to strictly enforce curated book manifests and tested with #318 inventories. |
| work/img-universal-readback-persistence-20261025 | Divergent: persist_approved_draft.cjs and cross-transport test, plus changes to canonical readback scripts | **Missing compatible write path candidate.** Requires B1 byte-preserving atomic-persistence testing, approval and hash checks; do not overwrite active B1 transport. |
| docs/verified-library-artwork-recovery-20261025 | Rex Fleet I03 SVG/PNG originals and Shattering File Library mappings; recovery provenance was merged in #308 and extended in #327 | **Incorporated as evidence**, not automatically approved draft images. Verify originals/pixels before any further approval or publishing. |
| debug-reference-keeper-delete-20261009 | Divergent deletes/replaces Keeper reference file and manifest | **Rejected as unsafe to replay** without explicit identity/approval decision and current byte verification. |
| complete/rex-fleet-issue-03 | Divergent earlier Issue 3 story recipes and recovery utility | **Retained historical candidate**; later current story/editing authority wins. Requires editorial proof before transplant. |
| rex-fleet-rewrite-recover* (11 variants) | Divergent temporary base64 tool payloads and recovery workflows, multiple aliases/attempts | **Historical probe only**; do not promote temporary .b64 files to production canon. |
| echoes-recovery-* / echoes-recovery-ready* | Multiple branch tips are exact ancestors of current main, including final/ready variants | **Incorporated by history**; retain branches, no cherry-pick. |
| Sunforge dialogue/script/causality variants, Echoes editorial variants, Vikings season alternatives, Backyard Rockets revisions | Older branches differ from newer authored page/script files | **Retained unapproved editorial alternatives.** The current assembler's script and released canon control. Individual beats require proof and editorial approval, not bulk merging. |
| img-decode-azr-p13, img-artifact-bridge-test, lts-recovery-inspect-20260905, stardust-issues4-10-drama-final-20260823 | Temporary extraction workflow, staged binary files, or probe-only paths | **Historical transport/probe**, not approved source content. |
| StarSplitterVisions Stardust preview v1/v2/v3 | Divergent temporary staging chunks, image-materialization workflows, older Stardust release JSON | **Superseded by released Issue 1**; do not change released metadata from preview branches. |
| StarSplitterVisions img-extract-* and img-artifact-bridge-azure-canon | Only old, one-off artifact extraction workflows differ | **Historical recovery tooling**, not a new reader/release source. |
| StarSplitterVisions release/stardust-station-issue-01(-clean) | Both branch tips are ancestors of current main | **Incorporated by history**; retain branch refs. |

## Regression protection and safe work merged

- Historical Issue 2 layout conflict: #291/#294 enforce one pageLayout overlay authority; #286 and associated tests avoid changing already-approved Vikings pages.
- B1 duplicate readback: #311 removes the obsolete Python/workflow path; #307/#300 regression tests and binary readback runtime guide remain main's accepted workflow.
- Keeper byte identity: #317 verifies approved retrieved sources, #325/#331 protect Keeper intake/display, while #304 rejects the invalid truncated image.
- Dashboard contract: merged #321 renames registered show configuration counts; exact assembled unit coverage comes from #309/#323. Do not merge both #328 and #329 unchanged.
- B3 complete-book gate: #288/#295/#302/#318/#324 and validation prevent silent omissions and distinguish review-only packages.
- Published Visions: #136/#138/#139 validate deployed reader paths and linked release files.

## Retained exceptions and further proof required

**Technical:** PR #326's B1 atomic approved-draft persistence/readback hardening remains under review against canonical byte transport. B2's human/press gate was merged in #322 but existing books remain unmastered until real approval. B3 alternative exporter branch still has stale fallback and should not supersede current browser/offline plus #324 curated inventory. PRs #328 and #329 remain competing dashboard implementations in the observed snapshot; reconcile into one compatible integration and retain both histories. Merged #330 is the distinct C3 visual/provenance quality register, not another dashboard source of truth. The presence of branch differences is not authorization to merge.

**Creative/recovery:** Rex Fleet Issue 5 old #224, Vikings old normalized #124, Stardust old #22/#56/#96, Echoes old #24, and multiple Sunforge/recovery candidate refs have unproven unique authored beats or incomplete provenance. Existing approved or released versions must remain untouched pending specific source/editorial review.

**Visions product concepts:** old closed #91 ContextProduct architecture, #72 News standalone site, #69 Extras and #70 Soundtrack separate index/detail experiences, and #98 cosmetic shell changes are not certified as fully implemented. No current user-approved requirement justifies restoring an obsolete root-src implementation. Retain as explicit exceptions rather than claiming they were fully incorporated.

**Whole-history evidence:** download both JSON reports from the Audit historical Git branch contributions action. They enumerate every retained branch, not only open PRs; status incorporated-by-history/tree-equivalent can be safely regarded as no unique tip content. Divergent-retained-pending-evidence remains an explicit exception until the owner records a semantic decision.

Historical branches are deliberately retained; do not delete for housekeeping. This ledger makes no new canon or artwork approvals.
