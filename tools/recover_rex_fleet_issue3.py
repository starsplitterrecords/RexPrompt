#!/usr/bin/env python3
"""Make Rex Fleet Issue 3 readable and begin the production-layout pass."""

import base64
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data" / "shows" / "rex-fleet-s1"
ENCODED = SHOW / "encoded" / "scenes_e03.json.gzb64"
OUTPUT = SHOW / "scenes_e03.json"
MANIFEST = ROOT / "data" / "shows.json"

PANEL_PLANS = {
    "RF_S1E03_A01": [
        "Tall establishing panel: Crownlight Atrium is already occupied by mourning families and uniformed officers beneath blue, gold, red and silver crown glass; the memorial is an event in progress, not ceremonial decoration.",
        "Selene at the lectern reads the three names from an open register while stamped remembrance markers and listening faces make each loss physical.",
        "Close on Selene closing the register after 'Recorded'; no applause, only the weight of the shut cover.",
        "The rear doors open and Dominion, Keating, Kerr and Rhyne pass toward the council chamber through the memorial crowd rather than entering as heroes.",
        "Venn steps aside for a grieving family leaving the atrium, then follows the Admirals at a distance, carrying the human cost into the political scene."
    ],
    "RF_S1E03_A02": [
        "Establish the circular glass-and-steel council around a live Tal Corvus route map; the discussion begins with infrastructure already on the table.",
        "Dominion collapses the primary approach routes with one controlled gesture, removing bright traffic lines from the model.",
        "Keating closes the remaining lines until Tal Corvus is surrounded by a clean blockade ring.",
        "Kerr activates clinic and civilian-traffic overlays; their icons disappear behind the new closure geometry as she asks about the clinics.",
        "Hold the three Admirals across the altered map while Keating narrows her answer to inspected windows and Kerr forces the distinction between 'all' and a survivable blockade."
    ],
    "RF_S1E03_A03": [
        "Rhyne places Halev's written terms beside replay footage of the first green crossing, pairing the political demand with evidence from the Verge.",
        "The replay shows Naomi's manual correction during the anomaly flicker as Venn asks for Verge access to channel and clocks.",
        "Keating freezes the image at its most dangerous instant and challenges scaling one successful crossing into policy.",
        "Aides continue adding casualty, heater and medicine numbers around the argument; the council cannot abstract the consequences away.",
        "Venn rewinds to Naomi's correction, accepts personal command responsibility with 'It's mine,' and leaves her name visually adjacent to the lane plan."
    ],
    "RF_S1E03_A04": [
        "The blockade geometry remains suspended between Dominion and Venn like a literal wall, with one narrow civilian route still open.",
        "Dominion frames the exceptions as structural weakness without leaving the dais.",
        "Venn stays at floor level among working officers rather than advancing toward him or adopting a speech pose.",
        "On her answer, frame Venn through the lone green gap so the road she is defending remains visible.",
        "End on the projected civilian route inside the blockade, not either speaker, making the policy's human consequence the scene's final image."
    ],
    "RF_S1E03_A05": [
        "Wide from the Auric Bazaar governor's balcony: Halev, Wallace and Naomi watch the cracked council feed above dock crews counting depleted stores below.",
        "Halev reads the four-day antibiotic figure from a battered slate while half-empty medical crates move through the background.",
        "Wallace corrects him with the three-day heat-cell count as workers load the last usable cells onto a cargo cart.",
        "Naomi watches that cart depart half empty, grounding her impatience in something she can physically see.",
        "The three turn from the remote council feed toward the live docks when Naomi rejects waiting for a perfect deal."
    ],
    "RF_S1E03_A06": [
        "Continuous on the balcony: Naomi opens a live reply channel while Halev looks down at the supply queues rather than rehearsing for camera.",
        "Halev dictates Verge pilots on every civilian channel; Naomi enters the condition beside the blockade map.",
        "He adds mandatory notification before any window closes as a dock alarm marks another delayed load below.",
        "Naomi pauses over SEND and warns that the Core will resist the demand.",
        "Halev reaches across, sends the terms himself, and answers while the waiting families remain visible past his hand."
    ],
    "RF_S1E03_A07": [
        "Establish Jex at a crowded worktable signing route slates in his weathered pocketed travel cloak; anomaly-glass beads bend nearby light subtly, and the fresh rib bandage is visible where the layers pull apart.",
        "His scribe reads the twelve-percent heater-coil spike from a live market board while Jex keeps one hand moving through contracts.",
        "Jex marks the coils for immediate sale, a clean profitable choice made without performance.",
        "The scribe offers the blanket contract; Jex redirects it to the cheap channel while a Tal Corvus cold-weather feed plays behind them.",
        "Jex covers the flicker of conscience with 'Because I have to sleep somewhere' and signs the next slate before the scribe can answer."
    ],
    "RF_S1E03_A08": [
        "Halev's transmission fills the council display with the Auric dock queues visible behind him.",
        "Keating isolates the closure condition and labels it VETO in hard military typography.",
        "Rhyne edits the label in front of the council to NOTIFICATION / LOCAL PILOT CHANNEL, preserving the operational meaning without surrendering command.",
        "Kerr backs the practical wording while the map shows a Verge pilot connection entering the civilian route.",
        "Dominion watches the language and command structure change on the signed draft, saying nothing as the compromise becomes harder to remove."
    ],
    "RF_S1E03_A09": [
        "Individual vote lights resolve around the council ring until a narrow authorization majority becomes visible.",
        "The final order expands across the central table with published windows, Verge channel access and local notification written into the operating clauses.",
        "Keating finds the concessions first and looks across the table before Venn sees her own command assignment.",
        "Dominion reads the terms and touches Venn's name into the lane-command field without softening his posture.",
        "Venn watches her name appear beside the green route while the blockade authorization locks around it; she accepts without a victory line."
    ],
    "RF_S1E03_A11": [
        "Naomi appears on Thunderbreak's live bridge link from her smaller patched Verge cockpit, demonstrating the first hold signal with deliberate clarity.",
        "A junior Fleet officer repeats the wrong gesture; nearby crew members suppress smiles while Naomi tells him he is ordering her ship to stop.",
        "The officer defensively holds his hands still, earning Naomi's dry correction about holding the ship rather than his hands.",
        "Naomi slows the motion and the officer mirrors each stage while Venn observes behind him without rescuing him.",
        "Venn orders 'Again,' and the whole bridge repeats the Verge signal together as practical training rather than a unity tableau."
    ],
    "RF_S1E03_A12": [
        "The link ends and Naomi's image leaves the bridge displays, but her hand-signal chart remains on one side screen.",
        "Venn orders the navigation overlays killed; the polished bridge abruptly loses its comforting geometry.",
        "Crew look through real windows at stars and neighboring hulls while the junior officer from the prior scene realizes the exercise is live.",
        "Venn gives the first signal without explanation; the officer reads it from memory and responds correctly.",
        "Exterior consequence: Thunderbreak's adjacent escort adjusts precisely on the manual command, proving the learned method can move ships."
    ],
    "RF_S1E03_A10": [
        "Open at dock-worker scale: magnetic boots on Bastion Spire's hull plating as crews pull the final service umbilicals from a heavy cruiser.",
        "The cruiser eases out of its berth while destroyers rotate into the outer screen behind it; the formation is built in visible layers, not as a generic ship cloud.",
        "Tugs and small escorts cross between the larger hulls, emphasizing the working traffic required to move a fleet.",
        "Pull wider as multiple berths empty and the Crown-marked formation turns away from the ordered Core anchorage.",
        "Final wide: Thunderbreak clears last and takes its place behind the departing formation, making Ella's responsibility legible without narration."
    ],
    "RF_S1E03_A13": [
        "A Verge escort corkscrews between projected shell bursts while its pilot watches both the canopy and Naomi's manual signal feed.",
        "Fleet destroyers rotate shield arcs in sequence; one arc arrives late, forcing the next ship to compensate rather than presenting a flawless ballet.",
        "A utility tug catches a tumbling aid pod with its cargo cradle as simulated fire flashes across the drill field.",
        "Inside a bridge, displays deliberately go black; gloved hands repeat the Verge signs across the command pit.",
        "An escort overshoots the safe line by half a hull length, receives a sharp correction, and burns sideways before the simulated strike lands.",
        "End on the rescued aid pod locked into the tug's cradle: the drill succeeds, but scorch scoring and alarm light show how narrow the margin was."
    ],
    "RF_S1E03_A15": [
        "Establish Tal Corvus as a battered inhabited rock-warren: pressure-sealed additions, exposed conduits and catwalk neighborhoods spread across the asteroid while cultivated neon fungi mark breathable routes.",
        "Families step onto narrow balconies and maintenance walks, their faces turned toward the new points of Fleet light in high orbit.",
        "A mechanic checks a nearly depleted power meter beside an exterior work lamp.",
        "The mechanic shuts the lamp down; local metalwork and faces fall into fungal blue-green while the blockade lights remain visible overhead.",
        "Final long view from behind the residents: Tal Corvus is darkened by scarcity, encircled by the much brighter machinery of the Core."
    ],
    "RF_S1E03_A18": [
        "Fleet destroyers settle into the outer ring around Tal Corvus, their spacing precise against the irregular rock-warren below.",
        "Thunderbreak turns broadside at the published green-lane mouth, its position making it both shield and gatekeeper.",
        "Verge escorts take the inner stations using tighter, locally familiar spacing than the Fleet formation.",
        "Navigation geometry paints the humanitarian gap between armed hulls: open, clearly marked and physically narrow.",
        "End down the length of the lane toward Tal Corvus, with every civilian ship forced to pass through an exposed corridor of waiting weapons."
    ],
    "RF_S1E03_A21": [
        "A small Shard skiff noses across the warning boundary, dwarfed by the blockade ships holding position around it.",
        "Fleet tracking geometry acquires the skiff; firing solutions follow its movement but remain amber rather than turning red.",
        "Inside the skiff, the pilot holds the line for one dangerous beat, watching for the first weapon flare.",
        "No one fires. The skiff rolls hard and peels away along the boundary.",
        "Hold on the empty space it leaves between the two formations, with guns still trained and restraint carrying the tension."
    ],
    "RF_S1E03_A23": [
        "Two empty utility tugs enter the live humanitarian lane beneath the fixed guns of both the Fleet ring and Tal Corvus defenses.",
        "The lead tug's display blanks on cue; its pilot looks away from the dead screen to Naomi's hand-signal relay.",
        "A Verge escort repeats the signal through the canopy and the tug corrects by sight.",
        "The second tug overshoots a marker; a Verge pilot waves it back while a Fleet targeting crew visibly holds fire.",
        "Observers on both sides watch the ungainly correction instead of applauding it.",
        "End with both tugs clearing the far marker: an ordinary-looking crossing made difficult enough to show why the routine matters."
    ],
    "RF_S1E03_A27": [
        "Dominion sits alone at the head of the council table while operational reports continue scrolling across the surrounding glass.",
        "Close on the order title, BLOCKADE: ACTIVE, above the smaller binding clauses for published humanitarian windows, Verge integration and local notification.",
        "His stylus stops over the concessions; reflected in the glass, the council chamber's crown geometry divides his face without changing his expression.",
        "Dominion signs across the full order, including the clauses he opposed.",
        "The authorization propagates from the council slate to the Tal Corvus tactical display, turning political language into an active ring of ships."
    ],
    "RF_S1E03_A14": [
        "Dominion and Keating stand behind the observation glass as the drill formation turns across Core orbit below.",
        "A cruiser group breaks synchronization when its simulated displays fail, leaving an ugly gap in the planned geometry.",
        "The group recovers through Verge hand signals and closes the gap before the drill clock expires.",
        "Keating objects to dockside signs as Kerr arrives, placing the institutional argument against the successful recovery outside.",
        "Dominion checks the completed clock instead of defending either position; the formation still finishes on time."
    ],
    "RF_S1E03_A16": [
        "Establish the crowded Warrant Hall as an improvised command space: patched pressure walls, public route boards and captains beneath masked Triarch authority.",
        "The emissary highlights published humanitarian windows on stolen Fleet telemetry and invites the captains to test them.",
        "A captain reaches toward a listed heater convoy whose civilian cargo manifest is plainly visible.",
        "Tess steps between the captain's hand and that route on the map, refusing the target without drawing a weapon.",
        "The emissary shifts to another window and lets the room register Tess's refusal; the heater route remains untouched behind her."
    ],
    "RF_S1E03_A17": [
        "Auric families advance through a supply-hall queue carrying empty heat-cell frames, medkit cases and light-strip housings.",
        "A monitor above them shows the solid blockade circle around Tal Corvus and the hair-thin green civilian gap.",
        "The Luminara Boy traces the wall and asks how their heater passes while his mother moves their empty carrier forward.",
        "She points to the green lights as workers behind the counter count dwindling replacement cells.",
        "The monitor changes to CONVOY DELAYED as the boy asks whether the armed ships understand the lane."
    ],
    "RF_S1E03_A19": [
        "Thunderbreak's bridge tracks a lone Shard skiff approaching the outer ring; the alarm is low and steady rather than battle panic.",
        "Tactical reports no weapons lock while their hand hovers beside the targeting control.",
        "Venn watches the real skiff through the forward display instead of staring at the threat board.",
        "The skiff edges closer and Tactical calls it a probe; Fleet firing geometry follows but weapons remain cold.",
        "Venn orders restraint and Tactical deliberately moves their hand away from the control."
    ],
    "RF_S1E03_A20": [
        "In a cramped Tal Corvus street alcove, two adults and a child crowd around a sputtering heater with an almost-empty charge indicator.",
        "An old wall speaker crackles with the 03:20 civilian window while patched pipes sweat cold condensation overhead.",
        "One adult compares the time to a posted curfew notice and sees that the rules conflict.",
        "The other checks the failing heater charge as its glow visibly weakens across the child's face.",
        "They choose the after-curfew window without declaring it; one lifts the empty heat-cell carrier as the schedule repeats."
    ],
    "RF_S1E03_A22": [
        "Inside Naomi's patched escort cockpit, her fingers tighten over the throttle as the probing skiff rolls away.",
        "A wingman appears off her canopy and begins drifting after the retreating target.",
        "Naomi releases the throttle to flash the learned hold signal, reinforcing the spoken order not to pursue.",
        "The wingman arrests the pursuit and returns to assigned spacing instead of turning the probe into a chase.",
        "On Thunderbreak's link, Venn answers only 'Copy,' leaving the operational decision visibly with Naomi."
    ],
    "RF_S1E03_A24": [
        "Jex works before six feeds: blockade geometry, Auric docks, cold street queues, permit clocks, market prices and Shard traffic.",
        "His scribe holds two contracts for the same heater shipment—legal permit at three and off-books delivery at nine.",
        "Jex studies families waiting with empty heat-cell carriers, his fresh rib bandage tightening as he shifts in the pocketed cloak.",
        "He stamps the heater cargo onto the low-paying permit route and hands it back before conscience becomes performance.",
        "Jex pulls a less essential, more profitable contract toward himself and denies sudden respectability while the heater permit enters the queue."
    ],
    "RF_S1E03_A26": [
        "After-action figures scroll around the council table: zero shots fired, medicine delivered and heater units installed.",
        "Kerr follows the cargo counts while Keating enlarges the anomaly incident instead.",
        "Keating warns that zero incidents does not establish safety; the ghost-destroyer image hangs above the table.",
        "Kerr answers precisely, refusing both panic and triumph.",
        "Dominion advances the schedule to the next civilian window and keeps it open, turning measured result into continued policy."
    ],
    "RF_S1E03_A28": [
        "Venn walks Thunderbreak's maintenance gantry while ordinary tugs unload heater cells and medpods through the green window below.",
        "Crews reset physical beacon clocks for the next crossing; the work resembles a shift change rather than a battle operation.",
        "Venn takes the manifest slate herself and checks arrivals against cargo moving off the tugs.",
        "She asks for the late list; the officer's empty answer is boring enough to become the victory.",
        "Venn returns the slate after her restrained approval and heads inside as the crews continue without ceremony."
    ],
    "RF_S1E03_A29": [
        "At Black Drift Haven, Billie spreads the stolen schedule across a scarred gantry table and marks targets with grease pencil.",
        "Tess arrives as Billie complains that crews already call it the regular window; neither closes the distance between them.",
        "Billie circles tomorrow's third slot with deliberate pleasure rather than random aggression.",
        "Tess turns the schedule enough to expose the evacuation manifest and makes Billie acknowledge who occupies that slot.",
        "Billie answers 'I know'; Tess leaves toward Gravefire before Billie can enjoy the reaction, carrying action into the tag."
    ],
    "RF_S1E03_A30": [
        "Continuous from Billie's marked schedule: Tess has already crossed the gantry and reached Gravefire's cockpit before Billie looks up.",
        "Tess straps in as the threatened third-slot evacuation manifest glows beside Billie's grease-pencil target mark on the copied schedule.",
        "She keys Gravefire's transponder into that same window and delivers the call without a speech.",
        "Gravefire releases from Black Drift Haven and burns toward Tal Corvus while the haven's welded wreckage falls behind it.",
        "Final inset on the route display: Billie's target mark and GRAVEFIRE occupy the same evacuation window, converting their argument into an unavoidable next action."
    ],
}


def main():
    if ENCODED.exists():
        payload = gzip.decompress(base64.b64decode("".join(ENCODED.read_text().split()))).decode()
        scenes = json.loads(payload)
    else:
        scenes = json.loads(OUTPUT.read_text())
    for index, scene in enumerate(scenes):
        if index:
            scene["continuityFrom"] = scenes[index - 1]["id"]
        if scene["id"] in PANEL_PLANS:
            scene["panelPlan"] = PANEL_PLANS[scene["id"]]
    scenes[9]["summary"] = scenes[9]["summary"].replace("SPire", "SPIRE")
    scenes[9]["settingText"] = scenes[9]["settingText"].replace("SPire", "SPIRE")
    OUTPUT.write_text(json.dumps(scenes, indent=2, ensure_ascii=False) + "\n")

    shows = json.loads(MANIFEST.read_text())
    rex = next(show for show in shows if show["id"] == "rex-fleet-s1")
    overlay = next(item for item in rex["sceneOverlays"] if item.get("replaceEpisode") == "S1E03")
    overlay.clear()
    overlay.update({"file": "scenes_e03.json", "replaceEpisode": "S1E03"})
    manifest_rows = ",\n".join(
        f"  {json.dumps(show, ensure_ascii=False, separators=(',', ':'))}" for show in shows
    )
    MANIFEST.write_text(f"[\n{manifest_rows}\n]\n")


if __name__ == "__main__":
    main()
