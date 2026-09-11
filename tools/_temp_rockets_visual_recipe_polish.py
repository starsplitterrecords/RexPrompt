#!/usr/bin/env python3
import base64, gzip, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data' / 'shows' / 'backyard-rockets-s1'
SHOWS = json.loads((ROOT / 'data' / 'shows.json').read_text())
SHOW = next(x for x in SHOWS if x.get('id') == 'backyard-rockets-s1')

R = {
'BR_S1E05_A01_SC02': {
'summary': "Rhonda spreads handwritten reservoir and well ledgers from communities that were never connected to Public Sky beside Milo's basin-decline graph. The dated measurements show the same falling levels before the expanded network came online; Arvin leaves the cause column blank.",
'panels': [
"Wide worktable view: Rhonda lays several worn handwritten well ledgers beside Milo's digital basin graph while Arvin leans in from the far side.",
"Overhead close-up: dated water-level entries from separate communities line up against the same downward curve on Milo's screen; the earliest dates predate Public Sky expansion.",
"Medium three-shot: Milo marks matching measurements, Rhonda holds open another ledger, and Arvin checks the dates while their existing dialogue runs over the work.",
"Final insert: a comparison sheet shows matching decline columns and an empty box labeled CAUSE, with Arvin's pen resting beside it rather than filling it in."
]},
'BR_S1E05_A01_SC04': {
'summary': "Arvin places the verified low-basin reading on the community board while the cause remains marked UNKNOWN. He proposes a ten-percent reduction in discretionary draw; Rhonda rewrites it as a community vote item instead of a Launch-Shop order, with Lucia checking the wording.",
'panels': [
"Wide coordination-table view: the low-basin gauge and map sit beside incomplete cause notes; Arvin points only to the measured level.",
"Close on the board: BASIN LOW / CAUSE UNKNOWN above a proposed 10% DISCRETIONARY DRAW REDUCTION, with no culprit named.",
"Medium view: Rhonda crosses out an imperative heading and rewrites the reduction as a community vote item while Lucia reads over her shoulder.",
"Final panel: copied vote sheets and radio call cards leave the table for separate communities, while the Launch-Shop crew remain outside the decision boxes."
]},
'BR_S1E05_DOC_TG05': {
'summary': "Reservoir gauges drop through orange warning bands while a basin map develops widening pressure gaps. Unauthorized satellite icons are layered over the same decline, and a formal Tethergrid emergency seal replaces ordinary Tetherwell branding with a midnight restriction notice.",
'panels': [
"Documentary panel: paired reservoir gauges descend into orange warning bands, with dates and tick marks clearly visible.",
"Basin-map panel: widening pressure gaps spread across the network while unauthorized satellite icons appear over the affected region.",
"Graphic close-up: the ordinary Tetherwell mark is replaced by a formal Tethergrid emergency seal in graphite, cyan and amber.",
"Final full-width notice: EMERGENCY RESTRICTIONS — MIDNIGHT sits over the declining basin map as the existing narrator line is lettered."
]},
'BR_S1E05_A01_SC05': {
'summary': "Angry community delegates crowd Milo's allocation board after Tethergrid announces emergency restrictions. Milo adds a reserve-margin column that leaves part of every shared source deliberately unused; Rhonda studies the new column while the delegates compare it with their requested increases.",
'panels': [
"Wide community-room view: delegates crowd a large allocation board covered with requested draw increases while Milo and Rhonda hold the center of the table.",
"Close on Milo's hand drawing a new RESERVE MARGIN column beside each shared source, leaving a visible unused band below the available total.",
"Medium view: one delegate points at unused water, Milo keeps the column in place, and Rhonda studies the board during their exact dialogue.",
"Final overhead: drinking, clinic, livestock, household and reserve columns share the same board; the reserve band remains visibly unallocated."
]},
'BR_S1E05_A02_SC01': {
'summary': "Inside Tethergrid, Cyrus places an internal basin forecast dated weeks before the first Public Sky expansion beside the current emergency graph; the projected decline matches the present drop. A board directive next to it exempts premium industrial and agricultural contracts from the first round of restrictions.",
'panels': [
"Wide Tethergrid command-platform view: Cyrus stands alone at a clean console with an internal forecast, current emergency graph and board directive open side by side.",
"Over-shoulder close: the forecast date predates the first Public Sky relay and its projected decline curve aligns with the current reservoir drop.",
"Insert on the adjacent board directive: premium industrial and agricultural contracts are highlighted as exempt while residential restriction tiers sit below them.",
"Medium close on Cyrus, silent and unsmiling, with the forecast and exemption directive still visible on the console as his existing two lines are lettered."
]},
'BR_S1E05_DOC_DL05': {
'summary': "Dryline places raw reservoir telemetry beneath Tethergrid's public graph. The raw decline begins weeks before the first unauthorized satellite marker, while premium draw contracts continue through the same period as residential restrictions deepen.",
'panels': [
"Documentary split-screen: Tethergrid's public decline graph above, raw reservoir telemetry below, sharing the same date axis.",
"Close on the date axis: the raw decline begins before the first unauthorized-satellite marker, which appears later on the timeline.",
"Second evidence panel: premium industrial draw contracts remain active while residential restriction bands deepen on the adjacent record.",
"Final composite keeps the raw telemetry, contract status and public claim visible together beneath the exact Dryline narration."
]},
'BR_S1E05_A02_SC03': {
'summary': "Community delegates fill Milo's reserve-margin board with basin-wide emergency allocations for drinking water, clinic cooling, livestock, food production and household use. Rhonda makes each increase point to a matching reduction elsewhere while Arvin remains standing away from the chair.",
'panels': [
"Wide meeting-room view: delegates surround the reserve-margin board; the central chair is occupied by a community delegate while Arvin stands against the wall.",
"Overhead board close-up: drinking water, clinic cooling, livestock, food production and household use occupy separate rows under one fixed total and reserve band.",
"Medium on Rhonda at the board: one hand points to an increased row and the other to the row that must decrease; Milo writes the balancing number.",
"Final wide panel: several painful revised allocations remain posted at once, with no category erased and Arvin still outside the chair."
]},
'BR_S1E05_A02_SC04': {
'summary': "On a reservoir service road, Lucia and Milo observe a permitted Tethergrid tanker convoy drawing from an industrial loading point while the nearby municipal pipeline remains valved shut. They photograph the valve tag, meter reading and tanker manifest without touching the operating equipment.",
'panels': [
"Long-lens desert service-road view: permitted Tethergrid tankers queue at an active industrial loading point while a separate municipal line runs toward a nearby settlement.",
"Close on the municipal valve: the wheel is fully shut, its tag visible, while the pipe itself is intact and connected.",
"Medium view from cover: Lucia photographs the valve tag and meter while Milo frames the tanker manifest; both keep clear of the live loading hardware.",
"Final evidence insert: three photographs — valve tag, meter, manifest — sit side by side with the active tanker draw visible beyond them."
]},
'BR_S1E05_A02_SC06': {
'summary': "After split community votes, three communities return to Tetherwell and two remain on Public Sky under lower shared limits. Milo removes the departing node cards from the allocation table, reroutes the remaining links and leaves the removed cards intact rather than marking them hostile.",
'panels': [
"Wide coordination table: five community node cards sit on the board after the vote, three marked RETURN TO TETHERWELL and two marked STAY / LOWER LIMIT.",
"Close on Milo lifting the three departing node cards cleanly from their sockets while the cards themselves remain undamaged.",
"Medium on Arvin and Milo as Milo reconnects the two remaining nodes through a smaller allocation table during their existing dialogue.",
"Final overhead: three intact cards rest in a neat stack beside a smaller two-node Public Sky diagram with lower limit numbers still active."
]},
'BR_S1E05_A03_SC02': {
'summary': "Cyrus opens Tetherwell's original conservation film beside the board's new emergency-restriction package. The serene reservoir footage contains repeated preservation language but no access or allocation terms; Cyrus authorizes the old cut unchanged.",
'panels': [
"Wide Tethergrid edit-suite view: Cyrus faces the old conservation film on one monitor and the emergency-restriction package on another.",
"Film-frame close-up: a serene blue reservoir and immaculate tower carry old PRESERVE / RESERVE language in the corporate caption track.",
"Transcript insert: preservation phrases repeat down the page while searches for ACCESS and ALLOCATION return blank results.",
"Medium close: Cyrus taps APPROVE ORIGINAL CUT without altering the timeline; the unchanged film frame remains frozen beside him."
]},
'BR_S1E05_DOC_TG06': {
'summary': "A vast blue reservoir reflects sunrise between pale desert ridges. The corporate camera glides toward an immaculate control tower as the old Tetherwell emblem appears over the calm water.",
'panels': [
"Very wide sunrise reservoir: glassy blue water fills the foreground between pale desert ridges, pristine and calm.",
"Long lateral view across the water toward an immaculate Tetherwell control tower with no settlements or distribution lines in frame.",
"Closer corporate composition: the tower and perfect water reflection center symmetrically under soft golden light.",
"Final branded frame: the old Tetherwell emblem fades over the reservoir as the existing conservation narration finishes."
]},
'BR_S1E05_DOC_DL06': {
'summary': "Dryline widens the same reservoir view beyond the corporate crop. Tethergrid tankers draw from an industrial loading point on one shore while the municipal pipeline toward a nearby settlement remains physically valved shut.",
'panels': [
"Begin with the same serene reservoir crop used by Tetherwell, matching horizon and tower position.",
"Wider frame reveals the industrial loading point just outside the corporate crop, with Tethergrid tankers actively filling.",
"Pan farther to the municipal branch: an intact pipeline runs toward a settlement but stops at a visibly closed tagged valve.",
"Final wide evidence frame includes reservoir, tankers, closed municipal valve and distant settlement together under the exact Dryline narration."
]},
'BR_S1E05_A03_SC03': {
'summary': "After Dryline publishes the uncropped reservoir evidence, Public Sky communities post Tethergrid premium allocations beside their own reduced draw schedules. Rhonda, Milo and Lucia place both sets of numbers on the same public board.",
'panels': [
"Wide community posting area: residents gather around a board already carrying Public Sky's reduced draw schedule and reserve bands.",
"Close on Lucia pinning a Tethergrid premium-allocation sheet directly beside the reduced community schedule at the same scale.",
"Medium on Rhonda and Milo aligning the two columns while their existing dialogue labels the low-basin reduction and premium contract draw.",
"Final frontal board view: COMMUNITY REDUCED DRAW and PREMIUM CONTRACT DRAW sit side by side with source documents attached beneath each number."
]},
'BR_S1E05_A03_SC05': {
'summary': "Cyrus opens Tethergrid's emergency orbital-authority console, marks the corridor used by Launch-Shop's short-lived relays CLOSED AT MIDNIGHT and signs the order under shared-infrastructure protection. A Tetherwell commercial routing map remains open on the adjacent display.",
'panels': [
"Wide Tethergrid command view: Cyrus stands before an orbital map with the Launch-Shop relay corridor highlighted among licensed traffic lanes.",
"Close on the authority panel: EMERGENCY LOAD AUTHORITY is selected and the corridor state changes to CLOSED — 00:00.",
"Medium on Cyrus signing the closure order while a second monitor still shows Tetherwell's commercial orbital routes and subscription-linked assets.",
"Final over-shoulder: the red corridor closure and intact commercial routing map remain visible together as Cyrus delivers the existing order lines."
]},
'BR_S1E06_A01_SC01': {
'summary': "Days after the orbital corridor closes, Rhonda arrives with three paper ledgers from neighboring basins. Their water quantities remain within local limits, but the update timestamps differ by hours; Milo spreads the ledgers across the table beside an offline regional map.",
'panels': [
"Wide Launch-Shop worktable: Rhonda drops three handwritten basin ledgers beside an offline regional map while Milo and Arvin make room among tools and radios.",
"Overhead close: nearly matching water totals carry timestamps separated by hours, with arrows showing updates arriving out of order.",
"Medium three-shot: Milo compares the three clocks, Rhonda holds one ledger open, and Arvin points to the delayed regional reconciliation during their dialogue.",
"Final insert: pencils, ledgers and a hand-drawn timing chart replace the dark orbital-link icon on the regional board."
]},
'BR_S1E06_A01_SC04': {
'summary': "Cyrus activates interference across the remaining unlicensed radio bands while keeping Tetherwell well-telemetry channels excluded from the sweep. On the spectrum display, unauthorized carriers disappear while protected well telemetry continues reporting basin data.",
'panels': [
"Wide Tethergrid spectrum-control station: Cyrus faces a regional radio map divided into unauthorized carriers and protected well-telemetry channels.",
"Close on the interference sweep moving across the unlicensed bands; several carrier traces collapse to black.",
"Adjacent display close-up: Tetherwell well-telemetry traces continue pulsing green through the same sweep, explicitly excluded from the jam list.",
"Medium on Cyrus pointing at the protected telemetry row while giving the exact 'carriers, not wells' order to his team."
]},
'BR_S1E06_A01_SC05': {
'summary': "Arvin locates a decommissioned hydroelectric service gallery whose old mechanical governor contains the pressure-switch design they need. Lucia marks a route through retired service spaces and blocks every path that crosses active flood-control equipment.",
'panels': [
"Wide table view: an old hydroelectric plan is spread under a portable lamp with the decommissioned governor gallery circled in grease pencil.",
"Close on Arvin's reference photo of the old mechanical governor and pressure-switch housing, scarred but intact after decades in damp service.",
"Lucia draws the retrieval path through retired corridors while crossing out active flood-control rooms in heavy red marks.",
"Final overhead map: one narrow approved route reaches the old gallery; active gates, spillway controls and live service areas remain visibly outside it."
]},
'BR_S1E06_A02_SC01': {
'summary': "Inside the decommissioned gallery, Arvin and Lucia cross a wet service ledge toward the old governor cabinet. Lucia's boot slips on moss beside the spillway edge; Arvin catches her wrist against the railing while Milo clips a safety line to her harness.",
'panels': [
"Wide damp gallery: a narrow service ledge runs beside dark spillway water toward the old governor cabinet; portable work lights throw hard reflections on wet concrete.",
"Low close-up: Lucia's boot slides across green moss at the ledge edge while one hand snaps toward the railing.",
"Tight action panel: Arvin's natural left hand grips the rail while his synthetic right catches Lucia's wrist; Milo reaches in with the safety line.",
"Final medium: Lucia is clipped to the line and back on stable footing, breathing hard but upright, with the governor cabinet still ahead."
]},
'BR_S1E06_A02_SC02': {
'summary': "At the old governor cabinet, the pressure switch is still connected to a dormant emergency gate circuit beside the modern controller. Milo leaves it installed and measures the spring geometry, contact travel and diaphragm housing while Arvin photographs every mechanical interface.",
'panels': [
"Wide hydro gallery work view: the old mechanical governor and pressure-switch branch remain physically connected beside the newer controller; Arvin, Milo and Lucia work under portable lights.",
"Close on the linkage and labeled emergency circuit: Milo's wrench stops short of the mounting bolts once the backup path is traced.",
"Medium detail: Milo measures spring length, contact travel and diaphragm housing with calipers while Arvin photographs each terminal, bracket and interface; Lucia holds the light.",
"Final close: the pressure switch remains installed and untouched; a measurement sheet and photo index beside it contain the copied dimensions."
]},
'BR_S1E06_A02_SC04': {
'summary': "Cyrus reviews a draft Tethergrid warning about disconnected wells. He keeps the basin diagram showing delayed aggregate draw, deletes the sentence claiming only Tethergrid can coordinate shared water, and approves the narrower phrase ISOLATION RISK.",
'panels': [
"Wide Tethergrid review desk: Cyrus faces a draft safety piece with a disconnected-well diagram and several blocks of legal copy.",
"Close on the basin diagram: individually green pump icons turn amber only when their delayed combined draw reaches the shared model.",
"Text-edit insert: Cyrus deletes ONLY TETHERGRID CAN COORDINATE SHARED WATER and leaves ISOLATION RISK highlighted in the approved copy.",
"Medium close on Cyrus sending the revised draft to legal, the narrower warning visible beside his exact dialogue line."
]},
'BR_S1E06_DOC_TG07': {
'summary': "A precise basin diagram separates into disconnected local clusters. Individually safe pump icons remain green in isolation, then turn amber when their delayed combined draw reaches the shared resource model.",
'panels': [
"Clean technical diagram: one basin begins as a connected network of green pump icons and synchronized timing marks.",
"The diagram separates into three local clusters; each cluster still shows locally safe green draw numbers.",
"A delayed aggregate line arrives at the shared-basin model and the combined total crosses the amber warning threshold.",
"Final documentary frame holds the isolated clusters and amber basin total together under the exact Tetherwell narration."
]},
'BR_S1E06_A02_SC05': {
'summary': "Rhonda, Milo and Arvin redraw the ground-loop rules on a working board. Any cross-community change gets a fast path and a separate witness path; if both paths disappear, the isolated site's local reserve limit automatically tightens.",
'panels': [
"Wide workbench view: Rhonda and Milo cover a board with three community nodes, physical relay boxes and two differently marked communication paths between each shared change.",
"Close on one proposed change leaving a node along a FAST PATH while a second WITNESS PATH travels a different route.",
"Medium on Rhonda cutting both path markers from one isolated node while Arvin moves that node's reserve slider downward during their existing dialogue.",
"Final overhead rule board: TWO PATHS FOR SHARED CHANGE / NO PATHS = STRICTER LOCAL LIMIT is represented with arrows, keys and reserve bands rather than prose paragraphs."
]},
'BR_S1E06_DOC_DL07': {
'summary': "Dryline compares paper ledgers, physical trip flags and ridge-relay status lamps across three communities. One delayed update is marked in red and corrected before the next draw period begins.",
'panels': [
"Three-column evidence layout: a paper ledger, mechanical trip flag and relay status lamp represent three different communities.",
"Close on timestamps: one ledger update arrives late and is circled red while the other two paths already agree.",
"Correction panel: the delayed value is copied across, the red mismatch clears and all three trip flags settle to the same draw period.",
"Final frame shows the next draw window beginning with synchronized timestamps and lower combined draw beneath the exact Dryline narration."
]},
'BR_S1E06_A03_SC01': {
'summary': "The crew bolts the first permanent ground relay to a limestone ridge. A Tethergrid interference sweep knocks out the ordinary carrier, the relay shifts to its slower alternate path, and the mechanical pressure trip remains fixed through repeated pump-start surges.",
'panels': [
"Wide limestone-ridge view: Arvin, Milo and Lucia anchor a compact relay cabinet beside a small antenna against hard desert sky.",
"Close on the radio display: the primary carrier trace vanishes under an interference sweep and the alternate-path lamp changes from amber to green.",
"Medium on Milo watching a mechanical pressure-trip flag while a nearby pump-start surge rattles the cabinet; the flag stays on its marked setpoint.",
"Final wide: the ridge relay remains online on the slower path, cabinet vibrating lightly in the wind while Launch-Shop packs its tools."
]},
'BR_S1E06_A03_SC03': {
'summary': "Lucia drives the most conspicuous Launch-Shop vehicle along an exposed desert route while Rhonda's community crews move duplicate relay components toward two other ridges in plain utility boxes. Tethergrid pursuit follows the visible Launch-Shop vehicle.",
'panels': [
"Wide desert-road panel: Lucia drives the recognizable Launch-Shop vehicle across open ground, deliberately visible beneath a distant Tethergrid surveillance track.",
"Cut to a quieter service road: community workers load plain duplicate relay boxes into two ordinary utility vehicles heading in different directions.",
"Overhead map-style action panel: Tethergrid markers converge on Lucia's exposed route while the two utility vehicles peel toward separate ridges outside that line.",
"Final split composition: Lucia glances at the pursuers in her mirror; elsewhere the plain boxes disappear behind two different ridge lines."
]},
'BR_S1E06_A03_SC04': {
'summary': "Arvin physically removes the Launch-Shop master-override module from the ground-loop controller and replaces it with recovery authority divided among community-held keys. Rhonda tests Arvin's own credential; the console returns DENIED until the required local confirmations are present.",
'panels': [
"Wide worktable: the open ground-loop controller sits between Arvin, Rhonda and Milo with the old master-override module exposed.",
"Close on Arvin unplugging the master-override module and setting it aside while multiple keyed recovery ports remain in the controller.",
"Medium on Rhonda inserting Arvin's credential alone; the console flashes DENIED as empty confirmation slots remain visible beside it.",
"Final insert: several separate community keys sit in different hands around the controller while the removed master module lies powerless on the table."
]},
'BR_S1E06_A03_SC05': {
'summary': "Tethergrid removes one ground-relay cabinet and places it in custody. On Cyrus's basin display, traffic immediately reroutes through neighboring nodes using duplicate trips, utility conduit and scheduled physical updates; the seized cabinet icon goes dark while the surrounding network remains active.",
'panels': [
"Wide Tethergrid field/custody view: technicians lift a seized relay cabinet onto a transport pallet, its cables capped and tagged as evidence.",
"Close on Cyrus's basin map as the seized cabinet icon turns black at the center of one local cluster.",
"The same map redraws live routes around the dark icon through two neighboring relays, a utility conduit marker and a scheduled hand-carry update.",
"Medium close on Cyrus watching the rerouted traffic continue while the physical seized cabinet sits inert behind glass or on the adjacent feed."
]},
'BR_S1E07_A01_SC04': {
'summary': "Cyrus replaces a target board centered on Launch-Shop rockets with a logistics board tracking workshops, freight movements, public coordinators and documented approvals. He strikes several speculative settlement markers and orders investigators to work only from evidence-backed routes.",
'panels': [
"Wide Tethergrid briefing wall: old photos of rockets and launch hardware occupy one side while Cyrus turns to a new board of workshops, freight records and public approvals.",
"Close on Cyrus moving strings from rocket photos to documented freight manifests, machine-shop receipts and coordinator records.",
"Insert: several settlement pins with question marks are crossed out and removed from the active target map.",
"Medium briefing shot: Cyrus points to the evidence-backed logistics chain while investigators take down the unsupported markers behind him."
]},
'BR_S1E07_A01_SC05': {
'summary': "Lucia shows Rhonda a Tethergrid recognition file built from her increasingly public appearances. Rhonda transfers sensitive coordination tasks to a rotating delegate list but keeps her name on the public work she intends to defend openly.",
'panels': [
"Wide roadside or coordination-space view: Lucia places a Tethergrid identification image of Rhonda beside recent public postings while Rhonda studies it without theatrics.",
"Close on the file: several public appearances and travel timestamps make Rhonda's pattern easy to follow.",
"Medium on Rhonda crossing her name off a sensitive coordination roster and writing several rotating delegate names into the empty slots while Lucia watches.",
"Final split tabletop: Rhonda's name remains on a public statement at left; the sensitive schedule at right now lists rotating community delegates."
]},
'BR_S1E07_A02_SC01': {
'summary': "At a decommissioned furnace complex, the crew recovers intact refractory panels and sealed drums of documented high-temperature compound from an approved disposal lot. They work in respirators under portable ventilation while Milo checks drum seals, exposure time and container condition.",
'panels': [
"Wide abandoned furnace bay: intact refractory panels and sealed labeled drums sit in a documented disposal area while portable ventilation ducts snake toward the crew.",
"Close on Milo in respirator checking a drum seal and matching its disposal-lot number to the paper manifest before opening anything.",
"Medium on Arvin and Lucia lifting intact panels onto padded carriers while Milo starts an exposure timer beside the ventilation monitor.",
"Final staging area: accepted panels and unopened drums are tagged and isolated; damaged material remains behind with red rejection marks."
]},
'BR_S1E07_A02_SC03': {
'summary': "Cyrus reviews a Tethergrid safety edit built around Launch-Shop's failed burn test. He keeps the lifted ceramic edge, temperature curve and visible ABORT marker in the cut and rejects an edit that would end on the failure without showing the shutdown.",
'panels': [
"Wide Tethergrid edit suite: Cyrus watches burn-test footage with the glowing nose cone, temperature trace and edit timeline visible on separate monitors.",
"Close on the failed frame: a ceramic edge lifts under heat while an ABORT marker appears on the temperature curve.",
"Timeline insert: an editor's cut point before the abort is dragged later so the visible shutdown remains in sequence.",
"Medium on Cyrus approving the version that ends with the test stopped and hardware cooling rather than on an isolated failure frame."
]},
'BR_S1E07_DOC_TG08': {
'summary': "A test nose cone glows under heat as one ceramic strip begins to peel. The image freezes on the lifted edge while a red ABORT marker appears beside the rising temperature curve.",
'panels': [
"Tight test-frame view: the nose cone glows orange-white under heat, with ceramic tiles and seams clearly visible.",
"Macro insert: one ceramic strip lifts at its edge while the neighboring tiles remain bonded.",
"Graphic split: the frozen lifted edge sits beside the temperature curve at the exact point the red ABORT marker appears.",
"Final documentary frame holds failure image and abort marker together under the exact Tetherwell safety narration."
]},
'BR_S1E07_A02_SC04': {
'summary': "Rhonda and Milo prepare Dryline's response using Launch-Shop's complete burn-test record. The failed tile, temperature trace, bond data and abort threshold remain visible together, while a second column lists the interception-test data Tethergrid does not publish.",
'panels': [
"Wide worktable: Rhonda and Milo face a screen showing the failed burn frame beside the complete temperature and bond record.",
"Close on the ugly failure graph left intact, including the bond drop and the clearly marked abort threshold.",
"Medium on Rhonda pointing to the graph while Milo leaves every data layer enabled during their existing dialogue.",
"Final evidence layout: Launch-Shop's published temperature/bond/abort data fills one column; a second column lists missing Tethergrid interception-test fields with blanks rather than invented values."
]},
'BR_S1E07_DOC_DL08': {
'summary': "Dryline runs the failed burn footage beside the full temperature trace, bond data and visible abort threshold. A second panel lists the comparable interception-test fields that Tethergrid does not release.",
'panels': [
"Documentary frame: the peeling ceramic test image plays beside the complete temperature trace instead of a cropped failure still.",
"Data close-up: bond strength falls while the abort threshold and shutdown point remain marked on the same axis.",
"Second evidence panel: a labeled list of interception-test fields appears with NOT PUBLISHED entries under Tethergrid.",
"Final split-screen holds Launch-Shop's full record and the unpublished comparison fields together under the exact Dryline narration."
]},
'BR_S1E07_A02_SC06': {
'summary': "The second burn test runs through the full profile. Several ceramic tiles char and erode on the surface while temperature sensors beneath the shield remain within limits; afterward, replacement tiles from three community workshops pass the same physical gauge.",
'panels': [
"Wide night or shaded test-stand view: the second nose-cone shield glows under a sustained burn while Arvin, Milo and Rhonda watch instruments from the safe station.",
"Close split detail: tile surfaces blacken and erode while embedded backside temperature sensors remain below the marked structural limit.",
"Post-test medium: Milo lifts a charred sacrificial tile to reveal the intact cooler structure beneath as the existing dialogue runs.",
"Final tabletop close: replacement tiles from three differently labeled workshops all slide through the same go/no-go gauge."
]},
'BR_S1E07_A03_SC01': {
'summary': "Tethergrid analysts correlate Rhonda's public burn-test update with travel records and isolate the community coordination site she is using. Cyrus signs a detention order naming Rhonda alone and removes broader settlement-search language from the execution brief.",
'panels': [
"Wide Tethergrid analysis room: a public burn-test post, travel timestamps and a regional map converge on one community coordination site.",
"Close on Rhonda's public post and matching travel record, linked by timestamps rather than anonymous speculation.",
"Medium on Cyrus signing a warrant page with RHONDA as the sole named subject while a broader sweep paragraph is struck through.",
"Final briefing insert: ONE WARRANT / ONE PERSON sits above the site map; surrounding homes remain outside the highlighted search boundary."
]},
'BR_S1E07_A03_SC02': {
'summary': "Lucia warns Rhonda that Tethergrid units are minutes away. Rhonda remains at the coordinator console long enough to copy the new shield-verification tables to other delegates and rotate her remaining authority keys before closing her session.",
'panels': [
"Wide coordination room: Rhonda works at the console while Lucia's urgent call is open and distant Tethergrid vehicle lights approach on a road map.",
"Close on the countdown/time display and Lucia's call as she says Rhonda has minutes, not hours.",
"Medium on Rhonda sending shield-verification tables to several delegate addresses while physical authority keys are reassigned on the console.",
"Final insert: transfer confirmations turn green one by one as Rhonda reaches for the console cover and the vehicle markers draw nearer."
]},
'BR_S1E07_A03_SC03': {
'summary': "Rhonda completes the authority transfer, closes the coordinator console, leaves copied keys and procedure sheets with the community team, then walks outside alone. Tethergrid detains her at the building entrance while the closed console inside already shows AUTHORITY TRANSFERRED.",
'panels': [
"Wide coordination-room view: Rhonda hands copied keys and procedure sheets across the table while the console behind her displays AUTHORITY TRANSFERRED.",
"Medium from inside: Rhonda closes the console and walks alone toward the exterior door; community members remain around the table behind her.",
"Exterior threshold view: Tethergrid personnel wait outside; Rhonda stops beyond the doorway with empty visible hands and no neighbors following her out.",
"Final split-depth panel: Rhonda is calmly taken into custody in the foreground while, through the open doorway, copied keys remain on the community table beside the closed transferred console."
]},
'BR_S1E07_A03_SC04': {
'summary': "From the ridge above the settlement, Lucia watches Rhonda's detention convoy leave along a road bordered by occupied houses. She lowers her weapon, marks the convoy route on her map and turns back toward Launch-Shop.",
'panels': [
"Long-lens ridge view: Lucia arrives above the settlement as the Tethergrid detention convoy pulls onto the main road below.",
"Through Lucia's optic or binocular frame: the convoy is visually bracketed by occupied houses, parked civilian vehicles and people near the roadside.",
"Medium profile: Lucia lowers the weapon away from the road and uses a grease pencil to trace the convoy's route on a paper map.",
"Final wide: the convoy disappears toward the horizon while Lucia turns back toward her own vehicle with the marked route folded in one hand."
]},
'BR_S1E08_A01_SC02': {
'summary': "In Tethergrid detention, Cyrus questions Rhonda beside a Public Sky control display. Each time he asks for a central authority, the console returns distributed community keys, local trip limits and multiple ground-loop routes; no single master credential appears.",
'panels': [
"Wide detention interview room: Cyrus and Rhonda sit across a bare table while a Public Sky topology display glows on the wall between them.",
"Close on the console after Cyrus's first question: six separate community keys appear around the basin map, none labeled MASTER.",
"Medium two-shot: Cyrus asks who can overrule the basin while Rhonda points to physical trip limits and distributed routes rather than to a person.",
"Final console close: SIX KEYS / LOCAL LIMITS / MULTIPLE ROUTES remain on screen with no central-credential field anywhere in the interface."
]},
'BR_S1E08_A01_SC04': {
'summary': "Cyrus records Tethergrid's emergency launch warning in front of a restricted-corridor map. He keeps the phrases HEAVY UNLICENSED VEHICLE and STORM-OBSCURED TRACKING, and strikes the board's unsupported word WEAPON before recording the final statement.",
'panels': [
"Wide Tethergrid recording space: Cyrus stands before a restricted orbital-corridor map with storm tracking gaps and ground exclusion zones visible behind him.",
"Script close-up: HEAVY UNLICENSED VEHICLE and corridor-risk language remain in black while WEAPON is crossed out in Cyrus's hand.",
"Medium recording shot: Cyrus delivers the statement directly to camera with the restricted path graphic beside him, controlled and non-theatrical.",
"Final monitor view: the approved caption reads HEAVY UNLICENSED VEHICLE; the rejected WEAPON wording remains visible only on the marked-up draft off-camera."
]},
'BR_S1E08_DOC_TG09': {
'summary': "A heavy unlicensed launch path crosses a restricted orbital corridor while storm-obscured tracking widens uncertainty cones around the vehicle and ground exclusion zones.",
'panels': [
"Orbital diagram: a heavy launch trajectory rises toward a clearly marked restricted corridor containing other asset tracks.",
"Tracking panel: storm cover obscures several ground stations and the vehicle's positional uncertainty cone widens along the path.",
"Ground-safety panel: exclusion zones below the uncertain track expand over desert service areas while population markers remain outside the intended zone.",
"Final technical composition holds restricted corridor, uncertainty cone and exclusion zones together beneath the exact Tetherwell narration."
]},
'BR_S1E08_A01_SC05': {
'summary': "Dryline places Tethergrid's launch-safety warning beside one month of Public Sky allocation records. Community draw bars remain below their former Tetherwell contract limits while reserve bands stay intact; the launch warning remains on screen as a separate record.",
'panels': [
"Documentary evidence wall: Tethergrid's heavy-launch warning occupies the left side while a month of Public Sky water-allocation data fills the right.",
"Close on the water chart: each participating community's actual draw bar remains below its former contracted Tetherwell allowance, with reserve bands still visible.",
"Separate close on the launch warning: restricted corridor, tracking uncertainty and exclusion-zone graphics remain unchanged rather than being dismissed.",
"Final split-screen keeps LAUNCH SAFETY and WATER ALLOCATION under separate headings with both records visible at once."
]},
'BR_S1E08_DOC_DL09': {
'summary': "Community draw bars remain below their prior Tetherwell contract volumes while reserve bands stay visible. Tethergrid's launch-safety warning remains beside the separate water-allocation record under different headings.",
'panels': [
"Clean chart panel: prior Tetherwell contract volumes form pale upper bars; current Public Sky draws sit lower beneath each one.",
"Reserve-band close-up: emergency reserve segments remain intact at the bottom of each community column.",
"Adjacent panel preserves Tethergrid's launch-safety warning with the corridor and uncertainty cone unchanged.",
"Final Dryline frame labels the two columns WATER ALLOCATION and LAUNCH SAFETY, visually separated by a clear rule beneath the exact narration."
]},
'BR_S1E08_A01_SC06': {
'summary': "Community delegates run the regional allocation board without Arvin, Milo or Lucia present; Rhonda's rotated keys continue working despite her detention. Elsewhere at Launch-Shop, the three founders monitor a silent routine-allocation channel while preparing Sky-Piercer hardware.",
'panels': [
"Wide community coordination room: delegates occupy the allocation table without any Launch-Shop founders; six distributed key slots and current basin limits are active on the board.",
"Close on one rotated Rhonda key now held by another delegate as a routine cross-basin allocation is approved and the board advances normally.",
"Cut to Launch-Shop: Arvin, Milo and Lucia work around Sky-Piercer hardware while a routine-allocation radio channel sits silent on the bench.",
"Final medium on the crew continuing their mechanical work as the untouched radio clock passes forty minutes with no incoming allocation call."
]},
'BR_S1E08_A02_SC02': {
'summary': "At a storm-damaged Tethergrid service transfer point, Lucia triggers a legitimate maintenance closure that routes Rhonda's detention transport into a low-speed inspection lane. Lucia releases the external door lock from the stopped vehicle; Rhonda pulls the interior release and exits under her own power.",
'panels': [
"Wide storm-damaged service road: maintenance barricades and an active closure sign funnel the Tethergrid transport away from the main lane toward a slow inspection spur.",
"Overhead or long view: the transport follows the only open marked path into the inspection lane while civilian traffic remains separated behind the closure.",
"Tight exterior action: Lucia reaches the stopped vehicle's external door-lock mechanism and disables it without attacking the cabin or nearby road equipment.",
"Interior/exterior split: Rhonda pulls the interior release herself, the door opens, and she steps out toward Lucia as storm rain and warning lamps flash around them."
]},
'BR_S1E08_A02_SC03': {
'summary': "At Tethergrid command, Rhonda's detention-transport icon drops from the network on the same service corridor leading toward the mobile launch cradle. Cyrus boards an interceptor and keeps the remaining pursuit route on the service corridor, away from storm-darkened community roads.",
'panels': [
"Wide Tethergrid command view: the detention transport icon blinks out on a regional map while the mobile launch-cradle route glows farther along the same service corridor.",
"Close on the map: a direct service-corridor line connects the lost transport position to the launch route; nearby settlement roads are shaded for low storm visibility.",
"Medium on Cyrus moving toward an interceptor while issuing the exact order to keep pursuit off blind community crossings.",
"Final aerial map view: Cyrus's interceptor follows the service corridor; other Tethergrid units stop short of the dark settlement-road branches."
]},
'BR_S1E08_A02_SC05': {
'summary': "At the mobile launch site, Cyrus reaches Arvin before fueling is complete and orders Sky-Piercer stood down. A Tethergrid board command arrives on Cyrus's wrist/console ordering immediate remote lockout of every nonpaying Tetherwell community, including basins whose live reserves remain within limits.",
'panels': [
"Wide launch-site confrontation: unfinished fueling lines and the mobile Sky-Piercer cradle sit behind Arvin as Cyrus and Tethergrid personnel establish control of the pad perimeter.",
"Medium two-shot: Cyrus orders the vehicle stood down while Arvin remains beside the fueling console, hands clear of controls.",
"Alert close-up on Cyrus's device: BOARD ORDER — REMOTE LOCKOUT / NONPAYING ACCOUNTS appears beside live basin rows still showing compliant reserve levels.",
"Final three-layer panel: Cyrus reads the lockout order in foreground, Arvin watches him, and the not-yet-fueled rocket remains stationary behind both men."
]},
'BR_S1E08_A02_SC06': {
'summary': "Cyrus places the board's blanket account-lockout order beside live Public Sky basin data showing compliant draw, intact reserves and local trip protection. He rejects the lockout command, leaves the corridor-safety order active and enters separate authorization requirements for any account-status shutoff.",
'panels': [
"Over-shoulder on Cyrus: the board's blanket lockout order fills one side of the console while live basin rows with green draw, reserve and trip indicators fill the other.",
"Close on his controls: ACCOUNT LOCKOUT is marked DENIED / SEPARATE AUTHORITY while CORRIDOR SAFETY remains ACTIVE.",
"Medium confrontation: Cyrus states the separation to Arvin and Lucia with the two order categories still visible behind him; nobody changes position into an alliance pose.",
"Final insert: two distinct command lines remain on screen — FLIGHT SAFETY: ENFORCE and ACCOUNT LOCKOUT: NOT AUTHORIZED BY SAFETY ORDER."
]},
'BR_S1E08_A03_SC01': {
'summary': "The Tethergrid board sends an automated kinetic-intercept request toward Cyrus's console. Storm-obscured tracking shows confidence below release threshold and an uncertain ground exclusion zone; Cyrus presses DENY and the firing authorization remains locked.",
'panels': [
"Wide Tethergrid interceptor-control view: an automated KINETIC INTERCEPT REQUEST flashes over the launch corridor map while storm cells obscure several tracking nodes.",
"Close on tracking confidence: the percentage sits below the marked RELEASE threshold and the projected ground exclusion zone overlaps uncertain terrain.",
"Tight hand/control panel: Cyrus presses DENY; the firing authorization changes to LOCKED while the target solution remains incomplete.",
"Medium close on Cyrus under the red request light as he demands a clean shot or stand-down, with the locked firing status still visible."
]},
'BR_S1E08_A03_SC04': {
'summary': "From the launch site, Rhonda joins the regional allocation board long enough to test her rotated authority. Her key appears as one of six equal community keys; delegates in separate locations approve the first cross-basin schedule carried by the new bridge.",
'panels': [
"Wide launch-site work area: Rhonda stands at a portable allocation terminal near Sky-Piercer while Arvin works nearby and separate community windows fill the screen.",
"Close on the authority display: RHONDA is one of six equal key slots with identical weight and no master badge.",
"Multi-location panel: six community delegates insert or confirm their keys on separate local terminals as the same cross-basin schedule advances through approvals.",
"Final terminal close: the new bridge carries the approved schedule across the basin map while Rhonda removes her key and the other five remain active."
]},
'BR_S1E08_A03_SC05': {
'summary': "Cyrus watches a Tethergrid basin map redraw around the new bridge. Multiple ground loops, local trip modules and six independent community keys remain active; the map contains no command-center icon and no single uplink carries all traffic.",
'panels': [
"Wide quiet Tethergrid command view: Cyrus faces the basin map as the new bridge appears between several already-active ground loops.",
"Close on the topology: local trip modules sit beside each basin and six separate key icons are distributed around the map rather than clustered at one hub.",
"System-map insert: traffic divides among several ground links and the new bridge; no line converges on a command-center symbol and no uplink carries all routes.",
"Medium profile on Cyrus watching the distributed map while delivering his two short existing lines, the topology remaining the dominant object in frame."
]},
'BR_S1E08_A03_SC07': {
'summary': "In a quiet Tethergrid office, Cyrus edits the orders under his authority. He leaves basin-safety limits intact, removes account-status lockouts from the safety command path and signs a separate-authorization requirement with his own name.",
'panels': [
"Wide late-night Tethergrid office: Cyrus sits alone at a clean desk with two order categories open on the wall display — BASIN SAFETY and ACCOUNT STATUS.",
"Close on the edit: safety-limit language remains unchanged while account lockouts are moved into a separate authorization branch.",
"Tight signature panel: Cyrus signs the revised order beneath SEPARATE AUTHORITY REQUIRED FOR ACCOUNT LOCKOUTS.",
"Final quiet composition: the signed order rests on the desk under cool office light, Cyrus's name visible beneath the separation he has entered into the command chain."
]},
}

expected = set(R)
found = set()
changed_files = []
for ov in SHOW.get('sceneOverlays', []):
    if ov.get('encoding') != 'gzip-base64':
        continue
    path = BASE / ov['file']
    raw = ''.join(path.read_text().split())
    obj = json.loads(gzip.decompress(base64.b64decode(raw)).decode())
    rows = obj.get('scenes', obj) if isinstance(obj, dict) else obj
    touched = False
    for scene in rows:
        sid = scene.get('id')
        if sid not in R:
            continue
        spec = R[sid]
        scene['summary'] = spec['summary']
        scene['panelPlan'] = spec['panels']
        scene.pop('directionInline', None)
        found.add(sid)
        touched = True
    if touched:
        payload = json.dumps(obj, ensure_ascii=False, separators=(',', ':')).encode()
        path.write_text(base64.b64encode(gzip.compress(payload, mtime=0)).decode() + '\n')
        changed_files.append(str(path))

missing = expected - found
if missing:
    raise SystemExit('Missing mapped scenes: ' + ', '.join(sorted(missing)))
if len(found) != 53:
    raise SystemExit(f'Expected 53 mapped scenes, found {len(found)}')

banned = re.compile(
    r"\b(?:physical story information|clear facial reaction space|actual changed hardware|end on the actual|"
    r"opening physical state|next scripted action|resulting physical state|visible change named by the scene|"
    r"the page should|this page|the chef should|the page's main pleasure|the climax should reward|"
    r"recurring series engine|dramatic foreground|character beat|story beat|success criterion|so the page feels)\b",
    re.I,
)
for ov in SHOW.get('sceneOverlays', []):
    if ov.get('encoding') != 'gzip-base64': continue
    path = BASE / ov['file']
    obj = json.loads(gzip.decompress(base64.b64decode(''.join(path.read_text().split()))).decode())
    rows = obj.get('scenes', obj) if isinstance(obj, dict) else obj
    for scene in rows:
        m = re.search(r'S1E(\d{2})', scene.get('id', ''))
        if not m or not (3 <= int(m.group(1)) <= 8): continue
        text = ' '.join([scene.get('summary','')] + [str(x) for x in scene.get('panelPlan', [])] + [str(x) for x in scene.get('directionInline', [])])
        hit = banned.search(text)
        if hit: raise SystemExit(f"{scene['id']}: residual compiler/editorial phrase {hit.group(0)!r}")
        if len(scene.get('panelPlan') or []) < 4: raise SystemExit(f"{scene['id']}: short panel plan")

print('Mapped scenes:', len(found))
print('Changed payloads:')
for path in changed_files: print(' ', path)
