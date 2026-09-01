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
