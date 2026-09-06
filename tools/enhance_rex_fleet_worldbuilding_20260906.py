#!/usr/bin/env python3
import base64
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data" / "shows" / "rex-fleet-s1"
MANIFEST = ROOT / "data" / "shows.json"

def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def write_json(path, data, compact=False):
    if compact:
        text = json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n"
    else:
        text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    path.write_text(text, encoding="utf-8")

def load_issue(entry):
    overlay = entry["sceneOverlays"][0]
    path = SHOW / overlay["file"]
    if overlay.get("encoding") == "gzip-base64":
        raw = base64.b64decode("".join(path.read_text(encoding="utf-8").split()), validate=True)
        return path, overlay, json.loads(gzip.decompress(raw).decode("utf-8"))
    return path, overlay, load_json(path)

def write_issue(path, overlay, pages):
    if overlay.get("encoding") == "gzip-base64":
        payload = json.dumps(pages, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        path.write_text(base64.b64encode(gzip.compress(payload, mtime=0)).decode("ascii"), encoding="utf-8")
    else:
        write_json(path, pages)

def patch_page(pages, page_id, patch):
    page = next((p for p in pages if p.get("id") == page_id), None)
    if page is None:
        raise SystemExit(f"Missing Rex Fleet page: {page_id}")
    page.update(patch)

def dlg(*items):
    out = []
    for handle, speaker, text in items:
        item = {"handle": handle, "speaker": speaker, "text": text}
        out.append(item)
    return out

characters = load_json(SHOW / "characters.json")
characters["C_commodore_ella_venn"]["voice"] = "Calm, deliberate, unshowy; authority through steadiness and operational clarity."
characters["C_commodore_ella_venn"]["promptContinuity"] = [
    "Fleet Academy-trained in standard reciprocal-field navigation; she understands operational inversion limits but defers to specialists on unexplained phenomena.",
    "Reach and Resolve is practical command doctrine about maintaining viable communities and reconnecting separated ones, not memorial ritual."
]
characters["C_captain_naomi_sol"]["promptContinuity"] = [
    "Veteran Verge pilot whose damaged-corridor knowledge comes from repeated real crossings; empirical technique can complement formal Core physics without overriding measured physical law."
]
characters["C_jex_marrin"]["promptContinuity"] = [
    "Route knowledge is practical: timing windows, shear markers, anchor behavior, traffic intelligence, and local observations. Avoid mystical navigation or secret-knowledge ritual."
]
selene = characters["C_archivist_selene_stormwell"]
selene.update({
    "role": "Fleet — historical analyst, Stormwell research office",
    "voice": "Precise, patient, evidence-first; distinguishes sources, claims, measurements, and uncertainty.",
    "arc": "Builds a cross-faction historical record from competing evidence without flattening disagreement into one institutional story.",
    "visualAnchor": "Older Fleet historical analyst with silver hair in a disciplined braid, a calm lined face, and practical research-duty clothing built for consoles, interviews, and field records rather than ceremonial display.",
    "wardrobe": "Restrained dark Fleet research uniform with working pockets, portable slate, and small service insignia; no robes, memorial regalia, lanterns, or sacred-record iconography.",
    "promptContinuity": [
        "Archives are research infrastructure. Selene compares provenance, telemetry, testimony, and conflicting accounts; she is not a priest or keeper of sacred names.",
        "When sources disagree, preserve the disagreement and test claims against evidence rather than harmonizing them for ceremony."
    ]
})
liora = characters["C_liora_virelia"]
liora.update({
    "role": "Shattering-era reciprocal-field physicist / technical witness",
    "visualAnchor": "Adult High Era physicist in clean practical engineering and research clothing, shown around corridor models, transit telemetry, and working technical systems rather than archival ceremony.",
    "promptContinuity": [
        "Treat Liora as a scientist: models are provisional, measurements are objective, and unexplained behavior remains unexplained until evidence supports a mechanism."
    ]
})
jia = characters["C_jia_morgan"]
jia.update({
    "role": "Fleet reciprocal-field physicist / technical analyst",
    "promptContinuity": [
        "Formally trained in asymptotic-inversion and reciprocal-field transit at Fleet Academy; uses reciprocal gap, shear, phase, anchor, and timing measurements as operational quantities.",
        "She separates established physics from hypotheses. Cultural disagreement cannot change measured physical law, but local pilot experience can reveal regimes formal models have not sampled."
    ]
})
write_json(SHOW / "characters.json", characters, compact=True)

factions = {
    "F_Fleet": {
        "name": "Fleet / Reach and Resolve",
        "description": "Core-aligned military and relief fleet operating heavy cruisers, escorts, survey support, rescue missions, and corridor protection across a civilization still being reconnected after the Shattering.",
        "symbols": ["crown insignias", "Reach and Resolve service mark", "ship and squadron registry markings"],
        "politicalNotes": "Resolve means sustaining viable communities and infrastructure when connection fails; Reach means restoring contact, trade, rescue capacity, and coexistence. Core pride in what the Fleet preserved can conflict with communities that experienced the same era as abandonment."
    },
    "F_Verge": {
        "name": "The Verge",
        "description": "Frontier trade worlds, farms, freeports, escorts, and civilian governments whose institutions evolved under long periods of unreliable or absent interstellar connection.",
        "symbols": ["green-and-gold trade colors", "route marks", "escort and local-registry markings"],
        "politicalNotes": "Demands practical autonomy, reliable trade, food, and dignity. Verge communities often preserve empirical corridor practices and historical accounts that differ from Core institutional narratives."
    },
    "F_Shards": {
        "name": "The Shards / Confederacy",
        "description": "Shard settlements, salvagers, raiders, captains, engineers, civilians, and survival blocs formed in wreckage zones and scarcity after the Shattering.",
        "symbols": ["salvaged armor", "shard-glass", "breached-armor tokens", "bright-red ship and faction markings"],
        "politicalNotes": "Internally divided between survival pragmatists, local governments, captains, raiders, and the Silent Triarch. Grievances about abandonment may be historically grounded even when later leaders weaponize them."
    },
    "F_Trade": {
        "name": "Independent Trade / Veil Market",
        "description": "Brokers, smugglers, merchants, route specialists, and information traders operating between formal factions.",
        "symbols": ["ledgers", "route tokens", "market chits"],
        "politicalNotes": "Transactional neutrality becomes harder to sustain as corridor instability turns route data, timing, and access into survival."
    },
    "F_Lattice": {
        "name": "Lattice Research / Corridor Exploration",
        "description": "Physicists, survey crews, pilots, and anomaly observers studying reciprocal-field transit, damaged corridor geometry, timing irregularities, and post-Shattering phenomena.",
        "symbols": ["survey markers", "instrument plots", "anchor and shear maps"],
        "politicalNotes": "Technical cooperation crosses political boundaries because physical law does not respect factional borders. Core Academy models, Verge pilot practice, and Shard field experience can contribute different evidence without making physics culturally relative."
    }
}
write_json(SHOW / "factions.json", factions, compact=True)

regions = {
    "Core": {
        "name": "The Core",
        "environment": "Bright, ordered civic, Admiralty, Fleet Academy, shipyard, research, and command environments with polished stone, etched metal, disciplined infrastructure, and mature transit instrumentation.",
        "tone": "Institutional confidence under growing political and scientific strain.",
        "political": "Fleet and Crown authority, technical standards, central infrastructure, and pride in the systems the Core managed to preserve after the Shattering.",
        "era": "Season One, post-Shattering order."
    },
    "Verge": {
        "name": "The Verge",
        "environment": "Frontier docks, markets, farms, freeports, patched textiles, working ships, crowded civilian infrastructure, local route boards, and repair yards.",
        "tone": "Lived-in pragmatism, scarcity, trade pressure, and stubborn independence.",
        "political": "Civil government, traders, escorts, and local communities bargaining for survival after generations in which Core access could not be assumed.",
        "era": "Season One."
    },
    "Shards": {
        "name": "The Shards",
        "environment": "Salvage cities, scarred decks, warrens, debris corridors, repair docks, improvised engineering, patched armor, and settlements built inside the physical wreckage of lost connection.",
        "tone": "Hard survival, factional rivalry, anger, and emerging solidarity.",
        "political": "Warlords, captains, civilians, engineers, raiders, blocs, and the Silent Triarch compete for legitimacy; no single Shard experience represents the whole region.",
        "era": "Season One."
    },
    "Lattice": {
        "name": "The Lattice",
        "environment": "Reciprocal-field corridors, echo space, survey stations, anchor infrastructure, and regions where geometry, timing, and reference frames become unreliable.",
        "tone": "Scientific awe mixed with physically objective but incompletely explained risk.",
        "political": "Exploration and technical necessity force cross-faction cooperation; observations may be disputed, measurements must still be tested.",
        "era": "Season One."
    },
    "Corridors": {
        "name": "Inter-faction Corridors",
        "environment": "Reciprocal-field lanes, rifts, gates, convoy routes, anchor points, shear windows, orbit, docking approaches, and transit space connecting Core, Verge, Shards, and Lattice.",
        "tone": "Movement under threat; protection, piracy, difficult navigation, and fragile cooperation.",
        "political": "Control of passage determines food, legitimacy, and survival. Reopening a route reconnects societies that changed while separated; it does not restore the old political order automatically.",
        "era": "Season One."
    }
}
write_json(SHOW / "regions.json", regions, compact=True)

lighting = load_json(SHOW / "lighting.json")
lighting["fleetCeremonial"]["description"] = "Bright ordered Fleet light with readable faces, etched metal, polished working surfaces, and restrained institutional formality."
lighting["vergeLivedIn"]["description"] = "Practical dock and market illumination: worklights, daylight, storefront spill, maintenance lamps, worn textiles, and clear human-scale detail."
write_json(SHOW / "lighting.json", lighting, compact=True)

mood = load_json(SHOW / "mood.json")
mood["reachAndResolve"]["keywords"] = ["institutional restraint", "reconnection under pressure", "protection over spectacle", "competing histories"]
mood["latticeAwe"]["keywords"] = ["scientific wonder", "physical danger", "objective uncertainty", "geometry and timing behaving incorrectly"]
write_json(SHOW / "mood.json", mood, compact=True)

P = {}
P["RF_I02_P09"] = {"directionInline": ["Enter with Jex possessing the only path that can recover Auric’s supplies and Halev possessing nothing with which to purchase it. The route data is concrete navigation information—timing windows, shear markers, anchor fixes and the second turn needed to keep the ships inside the usable reciprocal gradient—not mystical secret knowledge. Jex first tries to surrender only enough information to retain control, but the scribe exposes that half a route is a death sentence. The turn is Jex stripping every seal himself. Exit on his priceless map becoming public while the people who trusted him erase their ties."]}
P["RF_I02_P10"] = {"directionInline": ["Stage this as a six-panel multi-location intercut connected by radio, not as five people sharing one room. Paul is alone inside the supply spine’s improvised engineering blister, steering it from his repair slate. Richard is aboard the separate passenger hull, treating patients in its damaged medical hold. Naomi pilots her Verge escort alongside the passenger hull and calls course corrections to Paul over comms. Tess remains inside Gravefire while using her ship’s hull to push the supply spine. Venn remains on Thunderbreak’s bridge outside the passage and appears only in the dedicated Thunderbreak panel. Make the Shatterwake physically legible: rotating moon fragments and damaged corridor geometry shift the local reciprocal gradient; Naomi’s instruction to choose the slowest-moving fracture is an empirical way of choosing the least violent shear. Thunderbreak’s mass and field envelope cannot safely fit the usable gap. Never render a colorful hyperspace tunnel or mystical portal. The emotional line is Paul continuing to steer when the passenger hull carrying his father vanishes from view."]}
P["RF_I03_P05"] = {
    "summary": "Richard discovers medical and infrastructure evidence that the Triarch manufactured the refugee crisis by cutting heat and medicine to disloyal districts.",
    "panelPlan": ["Richard treats locals and refugees side by side.", "He compares identical tissue damage across clinical records with district power and medicine shutdown logs.", "Paul recognizes districts where official reports claimed unrelated shortages.", "Tess sees the deliberate sequence in the timestamps.", "Richard holds duplicated clinic and utility records as dangerous evidence, not a ceremonial archive object."],
    "dialogueInline": dlg(("@starsplit.tessa.banks","Tess","Same exposure?"),("@starsplit.richard.secundo","Richard","Same shutdown."),("@starsplit.paul.secundo","Paul","Those districts didn't fail together."),("@starsplit.richard.secundo","Richard","No. They were turned off one at a time."),("@starsplit.tessa.banks","Tess","Triarch punishment."),("@starsplit.richard.secundo","Richard","Triarch policy."),("@starsplit.paul.secundo","Paul","You kept the records?"),("@starsplit.richard.secundo","Richard","Clinic copies. Power logs. The official versions changed twice."),("@starsplit.tessa.banks","Tess","If this leaves the room, they come for you."),("@starsplit.richard.secundo","Richard","They already came for everyone else.")),
    "directionInline": ["Evidence emerges through patients, clinical records, power logs and timestamps rather than archive mystique. Richard is not preserving names as ritual; he kept the working evidence because the official explanation did not match what happened to his patients."]}
P["RF_I03_P14"] = {"panelPlan": ["An independent evidence-and-broadcast booth waits dark.", "Halev warns that a transmission from Auric makes the station a target.", "Richard sets conditions limiting how his evidence may be used.", "Paul refuses the seat beside him and Richard accepts the decision.", "Dain activates the tamper-evident public feed and places Richard’s conditions at its beginning."], "directionInline": ["Father and son love each other without agreeing; Richard owns his evidence. Treat the booth as practical public-record infrastructure—camera, source files, provenance and tamper checks—not as a solemn archive space."]}
P["RF_I03_P15"] = {"panelPlan": ["Richard sits alone before the camera with the source records available beside the feed.", "An infant’s clinical entry is paired with the remembered face of the patient Richard actually treated.", "A Shard engine crew stops work to listen.", "Paul hears familiar people and districts named outside the booth.", "Anonymous hands retransmit the testimony and supporting data before authorities can suppress the channel."], "directionInline": ["Each case links a specific person to a documented policy action and triggers someone else’s response. The power comes from evidence tied to human consequence, not ceremonial recitation of names."]}
P["RF_I03_P28"] = {"dialogueInline": dlg(("@starsplit.sera.dain","Dain","The ring holds."),("@starsplit.halev","Halev","Barely."),("@starsplit.naomi.sol","Naomi","Barely counts."),("@starsplit.abby.saville","Abby","Tess."),("@starsplit.tessa.banks","Tess","Not yet."),("@starsplit.richard.secundo","Richard","The evidence crossed Tal Corvus."),("@starsplit.soren.kerr","Kerr","The finding is removal from command."),("@starsplit.cael.dominion","Dominion","Effective immediately."),("@starsplit.ella.venn","Venn","It already was."))}
P["RF_I04_P03"] = {"summary": "Thunderbreak exits a reciprocal transit lane over Tal Corvus with Starfire Sentinel, Voidward Ardent and Silver Fang settling into their distinct positions around the humanitarian corridor.", "panelPlan": ["Open on the starfield geometrically unbending as Thunderbreak comes off inversion over Tal Corvus; show gravitational/metric lensing relaxing around the hull, not a colorful hyperspace tunnel.", "Starfire Sentinel, Voidward Ardent and Silver Fang emerge on different vectors and settle into roles suited to their established size and mission instead of forming four interchangeable hero ships.", "From the civilian viewpoint below, Thunderbreak’s heavy hull eclipses part of the sky before sliding clear of the green humanitarian markers.", "The final image should feel protective and intimidating at once: old institutions arriving with real capability and political weight."], "directionInline": ["Show reciprocal transit as space returning to ordinary geometry around ships that have been riding an inversion gradient. No warp streak tunnel. Thunderbreak’s heavy-cruiser identity should be recognizable from hull geometry, scale, refit history and the way other ships organize around it; the vessel is an institution larger than its current captain."]}
P["RF_I04_P31"] = {"directionInline": ["Close on different retellings of the same rescue happening simultaneously: Pike’s dock crowd credits his tow; Fleet officers study the formation breach and rescue geometry; Verge loaders count actual arrivals and lost cargo; Tess’s crew scrape heat damage off Gravefire; civilians redraw the ships from what they saw below. The underlying event happened once, but each community selects different facts and meanings from it. No narrator decides which inherited account is the whole truth."]}
P["RF_I05_P20"] = {"summary": "INT. VEIL MARKET — SERVICE CORRIDOR — NIGHT. Fresh route chalk turns an ordinary ration corridor into a working civilian information network.", "settingText": "INT. VEIL MARKET — SERVICE CORRIDOR — NIGHT", "panelPlan": ["Under ordinary market worklights and storefront spill, a woman follows fresh chalk arrows to an unexpectedly open ration door and calls back to people behind her.", "When asked who told her, she points at the wall and keeps moving.", "Workers and families alter course using the same practical route marks while freight continues around them.", "The network has become ordinary enough to be mildly funny without becoming a civic ritual."], "directionInline": ["Use practical service lighting, signage, worn surfaces, ration doors and moving freight. No lanterns or invented ceremony. The chalk matters because it carries useful current information."]}
P["RF_I09_P01"] = {"summary": "INT. VEIL MARKET — UPPER BALCONY — NIGHT. Worklights, signs and storefront spill flicker over crowded ration lines and route traffic.", "panelPlan": ["Establish Veil Market at night from the upper balcony: ration lines, route chalk, practical worklights, signs and storefront spill, traders shouting over one another.", "Jex crosses the balcony with a stack of manifests and two guards half a step behind.", "The crowd below is busy and noisy enough that the assassin can get close without dramatic foreshadowing."], "directionInline": ["Keep the Market vivid because it is working infrastructure under pressure, not because it has invented rituals. No lantern imagery; light comes from ordinary market, maintenance and commercial sources."]}
P["RF_I06_P10"] = {"summary": "At Auric Gate, the first usable reciprocal-field window opens under pressure and Sunlash leads two food freighters through before the shear envelope closes.", "panelPlan": ["Establish Auric Gate’s first window through instrumentation and geometry: anchor markers align, the reciprocal-gap display enters the usable band, and lensing along the lane briefly steadies.", "Sunlash dives through Jex’s narrow timing window with two food freighters while Shard pickets begin turning toward them.", "Fleet shields shift outside the civilian path; the escorts do not create the window, they exploit the measurable one that exists.", "One freighter scrapes a physical marker but keeps moving as the field begins drifting out of tolerance."], "directionInline": ["The Gate window is a measurable reciprocal-field transit condition. Use changing star geometry, anchor lights, shear plots and ship behavior rather than a glowing fantasy portal. The crossing succeeds by timing, escort discipline and inches."]}
P["RF_I06_P13"] = {"directionInline": ["The second convoy reaches a newly usable Gate window as Abby-aligned ships rotate their bows away and stop enforcing the Triarch interdiction. Keep the political choice separate from the physics: the pickets can open the traffic corridor, but they do not create or vote the reciprocal-field window into existence. Billie blocks a loyalist ship without firing; civilians cross while the measured window remains viable."]}
P["RF_I07_P01"] = {"summary": "A survey group crosses a genuinely stable reciprocal-field corridor before the first impossible echo appears.", "panelPlan": ["Open wide on the Calm Corridor operating normally: survey ships ride a shallow reciprocal gradient while distant starfields show restrained gravitational lensing and anchor instrumentation marks a stable lane.", "Keep RFG behavior visually subtle—no colorful tunnel. Ships look as though local geometry is doing part of the work.", "Let the normal, measured serenity occupy enough space that the first impossible reflection on the next page feels like a violation of understood physics."], "directionInline": ["Establish the known science before the anomaly. The Calm Corridor is not mysterious because it is a corridor; trained crews understand reciprocal-field transit here. What follows is disturbing because the instruments remain inside familiar limits while something unfamiliar happens anyway."]}
P["RF_I07_P02"] = {"panelPlan": ["On the survey bridge, standard RFG telemetry remains calm: reciprocal gap inside the expected envelope, shear low, anchor solution steady.", "Crew reflections begin appearing on screens a beat late despite the nominal transit readings.", "A technician sees his own duplicate complete a motion at the wrong time and tells the captain not to move.", "Nobody explains the phenomenon; the known corridor instruments are not showing a conventional inversion failure.", "End on the crew frozen while delayed copies finish movements already made."], "directionInline": ["The crucial contradiction is visual and technical: familiar transit physics looks healthy while timing/reflection behavior is impossible. Do not imply supernatural causation and do not let the characters invent a mechanism before they have evidence."]}
P["RF_I07_P04"] = {"summary": "Jia compares the survey telemetry to standard Academy reciprocal-field models and finds the first measurable difference between a real ship and its apparent echo.", "panelPlan": ["Jia overlays the current survey data against a standard Fleet Academy asymptotic-inversion envelope: reciprocal gap and shear remain nominal.", "She scrubs to an unscheduled manual burn; the real survey ship changes vector.", "The apparent duplicate follows one-point-seven seconds later. Jia marks the lag as an observation, not an explanation.", "Venn tests whether this is a bad inversion; Jia shows that the ship’s own field stayed inside known limits.", "Selene preserves raw telemetry, source provenance and the competing initial interpretations without turning any of them into a conclusion."], "dialogueInline": dlg(("@starsplit.jia.morgan","Jia","Reciprocal gap is inside the Academy envelope. Shear is clean."),("@starsplit.jia.morgan","Jia","There. Manual burn. Real ship turns. Echo follows one-point-seven seconds later."),("@starsplit.ella.venn","Venn","Bad inversion?"),("@starsplit.jia.morgan","Jia","No. A bad inversion changes the ship. This changes what follows it."),("@starsplit.ella.venn","Venn","Every time?"),("@starsplit.jia.morgan","Jia","Every unscheduled change in this sample."),("@starsplit.ella.venn","Venn","Then don't name it yet."),("@starsplit.jia.morgan","Jia","Wasn't going to.")), "directionInline": ["Use the Academy reference as ordinary professional knowledge, not lore exposition. Jia establishes what accepted physics can rule out, then stops. Selene’s job is source discipline: raw measurements stay distinguishable from later stories about what the measurements meant."]}
P["RF_I07_P08"] = {"directionInline": ["Sunlash and Gravefire enter the Calm Corridor with refugee skiffs between them on normal reciprocal coupling. Their formation begins tightly synchronized because common timing is established safety practice. The danger is not that corridor travel itself is mystical; the danger is that the unexplained echoes appear to exploit the very regularity crews normally depend on."]}
P["RF_I07_P11"] = {"summary": "Jia recognizes that the echoes phase-lock to synchronized ship inputs; Venn turns to Naomi’s manual Verge flying before the anomaly can convert their discipline into a trap.", "dialogueInline": dlg(("@starsplit.jia.morgan","Jia","The echoes phase-lock when our commands do."),("@starsplit.ella.venn","Venn","Meaning?"),("@starsplit.jia.morgan","Jia","Same burn, same targeting, same timing. We keep handing the field one solution."),("@starsplit.ella.venn","Venn","Naomi."),("@starsplit.naomi.sol","Naomi","Yeah. Kill the boards.")), "directionInline": ["Jia identifies a correlation, not a complete theory. Venn immediately pairs formal analysis with Naomi’s empirical pilot practice. Naomi’s method is useful because Verge crews have learned to fly damaged and irregular corridors by hand; it is new evidence about this phenomenon, not a cultural exception to physics."]}
P["RF_I07_P12"] = {"directionInline": ["The convoy deliberately breaks synchronized control. One escort burns early, another late, one civilian skiff coasts and Gravefire rolls off-axis. Their apparent duplicates continue the old common solution for one beat before separating from the real ships. Make the mechanics readable through vectors, timing and geometry rather than captions or supernatural effects."]}
P["RF_I07_P13"] = {"directionInline": ["Naomi conducts the convoy by hand signs and deliberately assigns different timing to different ships. Tess is already offsetting Gravefire’s burns. Their practical technique is not opposed to Jia’s science; it is the field test Jia needs. The tiny joke relieves pressure because they are actively flying."]}
P["RF_I07_P15"] = {"directionInline": ["The last real skiff clears the Lattice while its apparent duplicate continues along the obsolete vector and dissolves against empty space. No one fires. The ugly unsynchronized formation worked because it denied the phenomenon a clean repeated input; do not claim this proves what the echoes are."]}
P["RF_I07_P16"] = {"directionInline": ["Jex watches the convoy clear, then closes the three route listings he defended earlier. He now has operational evidence that yesterday’s safe reciprocal window can behave differently today. His scribe is more shocked by the refunds than by the anomaly. Jex defers reopening until Jia can define a testable operating envelope."]}
P["RF_I10_P12"] = {"directionInline": ["Above the Spire, Scythe of Saville tilts into the furnace plume. Make the ship recognizable before Abby appears: its broad shield geometry, accumulated repairs, drive placement and working scars distinguish the vessel as an institution with a service history, not merely Abby’s current vehicle. Its configuration makes the relief maneuver physically possible."]}
P["RF_I11_P12"] = {"summary": "Overlapping weapons fire and Gate stabilization pulses push Auric’s reciprocal-field geometry into the same echo behavior first measured in the Calm Corridor.", "directionInline": ["The Rift shudders as synchronized weapons fire overlays the Gate’s stabilization cycle. Anchor and shear displays remain readable while duplicate hull states begin appearing at the edges of repeated formations—first one, then several. Treat this as the dangerous recurrence of a measured physical phenomenon, not ghosts materializing because people believe in them."]}
P["RF_I11_P13"] = {"summary": "Jia recognizes that synchronized weapons fire is phase-locking the Gate echoes to the battle and gives Venn an immediate falsifiable intervention: stop feeding the field the same pattern.", "dialogueInline": dlg(("@starsplit.jia.morgan","Jia","Venn, stop the synchronized fire."),("@starsplit.ella.venn","Venn","Why?"),("@starsplit.jia.morgan","Jia","The Gate field is phase-locking to the volleys. Every repeated pattern gives the echoes the same solution."),("@starsplit.ella.venn","Venn","All batteries cold."),("@starsplit.ella.venn","Venn","Naomi, I need your hands."),("@starsplit.naomi.sol","Naomi","You have them.")), "directionInline": ["Jia overlays the Gate battle with Calm Corridor telemetry and sees duplicate density spike after synchronized volleys. She does not claim a final ghost-ship theory; she identifies a controllable input. Venn shuts Thunderbreak’s batteries down and calls Naomi. Verge hand signs replace common targeting clocks across the lane."]}
P["RF_I11_P14"] = {"directionInline": ["A scarred, partially blackened Scythe of Saville emerges from the outer Rift with jury-rigged thrust. The same broad shield geometry and distinctive refit pattern established at Shatterforge make the ship identifiable before anyone sees or names Abby. Its institutional identity has survived damage, crew loss and political change."]}
P["RF_I11_P19"] = {"dialogueInline": dlg(("@starsplit.selene.stormwell","Selene","Verge escorts dropped target lock first."),("@starsplit.cael.dominion","Dominion","Thunderbreak followed."),("@starsplit.selene.stormwell","Selene","Then Saville's ships."),("@starsplit.cael.dominion","Dominion","And the Gate held."),("@starsplit.selene.stormwell","Selene","Then that is the sequence the logs support.")), "directionInline": ["Selene and Dominion reconstruct the event from timestamped combat logs. The point is historiography in real time: institutional narratives may disagree about who deserves credit, but the shared telemetry constrains the order of events."]}
P["RF_I12_P07"] = {"summary": "The final Accord terms encode the behavior that actually saved the Gate: shared transit windows, mixed escorts, no unilateral civilian closure, and a common evidence record.", "charactersInline": [{"name":"Archivist Selene Stormwell","handle":"@starsplit.selene.stormwell"},{"name":"Commodore Ella Venn","handle":"@starsplit.ella.venn"},{"name":"Captain Naomi Sol","handle":"@starsplit.naomi.sol"},{"name":"Governor Chris Halev","handle":"@starsplit.halev"},{"name":"Admiral Cael Dominion","handle":"@starsplit.cael.dominion"},{"name":"Abby Saville","handle":"@starsplit.abby.saville"}], "panelPlan": ["The Accord is written in real time on a shared projected draft; the room is working, not ceremonial.", "Venn reads a weapons clause; Naomi catches dangerous ambiguity and edits it.", "Halev adds civilian cargo priority.", "Dominion tests emergency closure while the draft shows the measured Gate-failure exception separately from political discretion.", "Selene adds a shared-log clause: all parties receive the same raw transit timestamps, incident telemetry and amendments even when their narrative reports disagree.", "Dominion limits the trial by physically entering '30 DAYS / AURIC GATE ONLY.'"], "dialogueInline": dlg(("@starsplit.ella.venn","Venn","Published windows. Mixed escorts. Weapons cold inside the civilian perimeter unless fired on."),("@starsplit.naomi.sol","Naomi","No. 'Unless fired on' starts an argument every time somebody sees a ghost."),("@starsplit.ella.venn","Venn","Fair. No first fire."),("@starsplit.halev","Halev","Civilian cargo before military repositioning."),("@starsplit.cael.dominion","Dominion","Emergency closure?"),("@starsplit.halev","Halev","Two parties."),("@starsplit.naomi.sol","Naomi","Unless the Gate itself is failing."),("@starsplit.selene.stormwell","Selene","Shared logs. Same raw timestamps for everyone. Keep your own conclusions."),("@starsplit.cael.dominion","Dominion","Thirty days. Auric Gate only."),("@starsplit.abby.saville","Abby","Thirty days is enough to find out if we're lying.")), "directionInline": ["The Accord is written as an operating document. Shared records exist so later history has common evidence, not so anyone can perform remembrance. Different parties may interpret the same crossing differently; none gets a private set of physical measurements."]}
P["RF_I12_P10"] = {"summary": "The first Accord convoy waits for a reciprocal-field window independently confirmed by Fleet, Verge and Shard instruments rather than moving on Fleet authority alone.", "panelPlan": ["The first Accord convoy waits at Auric Gate while three independent instrument sets watch the same anchor alignment and reciprocal-gap window.", "Venn calls the countdown from Thunderbreak; Naomi and Abby each confirm the same physical mark from their own ships before anyone moves.", "The displays need not look identical, but their measured window agrees.", "The convoy crosses only after all three confirmations are visible, making cooperation operational rather than symbolic."], "directionInline": ["Make the distinction explicit visually: authority is shared, physics is not negotiated. Fleet, Verge and Shard crews can use different interfaces and procedures while measuring the same transit condition."]}
P["RF_I12_P13"] = {"summary": "EXT. GATE LANE — CONTINUOUS. The First Accord Convoy moves through under genuinely mixed escort.", "panelPlan": ["The First Accord Convoy passes through the measured Gate window under genuinely mixed escort.", "Civilian cargo is visibly ahead of military repositioning ships waiting their turn.", "The formation is heterogeneous because different ship institutions and regional practices are cooperating rather than being standardized into a Fleet tableau.", "The route works without implying the political differences are solved."], "directionInline": ["This is an operational success, not a memorial procession. Preserve distinct ship silhouettes, markings and working habits. The shared procedure coordinates them without erasing where they came from."]}
P["RF_I12_P16"] = {"summary": "After the first Accord crossing, Selene reconciles Fleet, Verge and Shard records and finds that their explanations differ even where the hard transit evidence agrees.", "settingText": "BASTION SPIRE — RELIC COURT — WORKING ANALYSIS DESK — NIGHT", "regionText": "The Core", "charactersInline": [{"name":"Archivist Selene Stormwell","handle":"@starsplit.selene.stormwell"}], "panelPlan": ["Selene works alone at an ordinary analysis desk with Fleet, Verge and Shard after-action files open side by side.", "Their annotations disagree about who led, who yielded and why the crossing worked, but raw Gate-exit timestamps and ship tracks align.", "She tags the disagreements instead of rewriting them into one account.", "A display locks the shared telemetry while leaving each source report attached to its provenance.", "Selene closes the working file with unresolved questions still visible."], "dialogueInline": dlg(("@starsplit.selene.stormwell","Selene","Three accounts. One crossing."),("DISPLAY","DISPLAY","GATE EXIT — 04:18:22 / FLEET · VERGE · SHARD"),("@starsplit.selene.stormwell","Selene","Keep the disagreements. Lock the telemetry.")), "directionInline": ["This is historical method, not archive culture. Selene preserves provenance and contradiction because later investigators need to know what each source claimed. The measurable crossing constrains the history without deciding every political interpretation."]}
P["RF_I12_P19"] = {"summary": "EXT. AURIC GATE — DAWN. The Second Accord Convoy forms with less hesitation than the first.", "directionInline": ["At dawn, the second Accord convoy forms with less hesitation. Crews still check one another’s clocks and field marks, but nobody needs the shared procedure explained. Civilian freighters take the front positions while military ships wait behind. This is routine beginning to grow from successful cooperation, not ritual."]}
P["RF_I12_P21"] = {"directionInline": ["Wide orbit. The second convoy threads the lane while unrelated traffic waits, turns and resumes around it. Keep the vessels visibly different in age, mission, refit history and faction origin; a complete world should feel capable of supporting stories aboard any one of them. No victory tableau, memorial framing or closing narration. The system is functioning provisionally because people are using it."]}

shows = load_json(MANIFEST)
rex_entries = {int(entry["id"][-2:]): entry for entry in shows if entry.get("id", "").startswith("rex-fleet-i")}
if set(rex_entries) != set(range(2, 13)):
    raise SystemExit(f"Unexpected Rex Fleet issue manifest: {sorted(rex_entries)}")

by_issue = {}
for page_id, patch in P.items():
    issue = int(page_id[4:6])
    by_issue.setdefault(issue, []).append((page_id, patch))

for issue, patches in sorted(by_issue.items()):
    path, overlay, pages = load_issue(rex_entries[issue])
    for page_id, patch in patches:
        patch_page(pages, page_id, patch)
    write_issue(path, overlay, pages)
    print(f"Enhanced Issue {issue}: {len(patches)} page patches -> {path.relative_to(ROOT)}")

print(f"Enhanced reusable world rules and {len(P)} Rex Fleet pages.")
