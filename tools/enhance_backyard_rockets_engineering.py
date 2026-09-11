#!/usr/bin/env python3
"""
Developmental rewrite of unreleased Backyard Rockets S1E03-S1E08.

The pass preserves issue/page IDs and existing season order while rewriting selected
assembler-visible page fields so the production chef receives:
- a different real engineering problem in each issue,
- concrete supply/scavenging constraints,
- nomadic pressure caused by Cyrus,
- character development during work and travel,
- varied technical failure modes rather than repeated system/governance debates.

This script is intentionally idempotent and writes directly back into the existing
gzip-base64 issue payloads consumed by RexPrompt.
"""
from __future__ import annotations

import base64
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/shows/backyard-rockets-s1/encoded"

FILES = {
    "S1E03": BASE / "scenes_e03_public_sky.json.gzb64",
    "S1E04": BASE / "scenes_e04_trip_point.json.gzb64",
    "S1E05": BASE / "scenes_e05_reserve_margin.json.gzb64",
    "S1E06": BASE / "scenes_e06_ground_loop.json.gzb64",
    "S1E07": BASE / "scenes_e07_ablative_armor.json.gzb64",
    "S1E08": BASE / "scenes_e08_sky_piercer.json.gzb64",
}

def d(speaker, text):
    return {"speaker": speaker, "handle": f"@brk.{speaker.replace(' ', '')}", "text": text}

def dirs(*items):
    return [{"text": item} for item in items]

def page(summary, panels, dialogue, *direction):
    return {
        "summary": summary,
        "panelPlan": panels,
        "dialogueInline": dialogue,
        "directionInline": dirs(*direction),
    }

PATCHES = {
    "S1E03": {
        "BR_S1E03_A01_SC01": page(
            "Before dawn, Arvin and Milo weigh the Public Sky payload, the upper-stage hardware and the propellant they can actually carry. Milo suggests adding more fuel; Arvin makes him walk the mass ledger backward until the trap is obvious: every extra kilogram of propellant requires structure and still more propellant to lift it. They recover margin by redesigning a heavy mounting frame instead of pretending the vehicle can simply grow.",
            [
                "Wide pre-dawn work deck: improvised scale, payload crate, upper-stage hardware and handwritten mass ledger spread around Arvin and Milo.",
                "Milo adds a fuel-canister symbol to the ledger; Arvin silently adds the structure and tankage that the extra mass would also require.",
                "They remove an overbuilt steel payload cradle and compare it with a lighter trussed replacement assembled from known stock.",
                "Quiet beat while they file and fit the new cradle; Milo asks an unrelated personal question and Arvin answers without stopping work.",
                "Final close-up: the new ledger has a narrow but believable payload margin, not a miraculous surplus."
            ],
            [
                d("Milo", "I keep wanting the answer to be more fuel."),
                d("Arvin", "More fuel has to lift more fuel. Then it has to lift the tank and structure that hold the fuel. The vehicle charges interest."),
                d("Milo", "So we lose weight somewhere that is not doing useful work."),
                d("Arvin", "Now you are designing a rocket."),
                d("Milo", "Were you this cheerful when you taught Lucia?"),
                d("Arvin", "Lucia never asked permission to learn.")
            ],
            "Treat mass fraction as a physical design constraint visible in the parts and ledger, not as a lecture or formula dump. No exact propellant recipe is needed.",
            "Let the conversation breathe through measuring, filing, carrying and fitting. The work continues while Arvin and Milo reveal familiarity and irritation."
        ),
        "BR_S1E03_A01_SC03": page(
            "Cyrus studies Launch-Shop's discarded stage hardware and tire tracks rather than a generic map. The rocket debris tells him what Arvin will need next: a narrow class of bearings, telemetry connectors and clean pressure-rated hardware that cannot be fabricated in the field. He orders surveillance on likely salvage sources instead of searching the whole desert.",
            [
                "Cyrus kneels beside a recovered stage ring and scorched telemetry harness laid on a clean field tarp.",
                "He rotates a damaged bearing and compares its dimensions to a supply map of aircraft yards, irrigation depots and old aerospace facilities.",
                "A technician proposes another broad drone sweep; Cyrus dismisses it and circles three supply locations.",
                "Cyrus notices Arvin preserved an expensive connector while abandoning heavier metal, revealing Launch-Shop's next scarcity.",
                "Final panel: one of the circled salvage locations is already being watched as the sun rises."
            ],
            [
                d("Cyrus", "Stop searching for the people. Search for the part they cannot make."),
                d("Cyrus", "The frame is disposable. The bearing is not. Neither is that connector."),
                d("Cyrus", "He will trade distance for certainty. Give him three places to choose from and watch all three.")
            ],
            "Cyrus is an engineer hunting another engineer. His pursuit should arise from material evidence and supply-chain prediction, not omniscience.",
            "Keep him calm and technically credible; the threat is that he understands why Launch-Shop must move."
        ),
        "BR_S1E03_A01_SC04": page(
            "The crew lowers the rebuilt payload cradle into place while rationing their clean water. Fine desert grit has contaminated a guidance connector and a machined sealing face; the normal shop answer would be a thorough wash and clean-room handling, but the camp cannot spend drinking water that way. Arvin, Lucia and Milo improvise a dry cleaning and inspection sequence, accepting slower work and more rejects.",
            [
                "Arvin catches Milo reaching toward the clean-water container, then points to the crew's drinking allotment beside it.",
                "Macro view of grit in a connector and on a machined sealing face; the defect is tiny but mission-critical.",
                "Lucia holds inspection light and clean cloths while Milo uses dry air and brushes; Arvin rejects the first attempt.",
                "During the slow cleaning, Lucia asks Arvin where he learned to hate contamination this much; his answer touches his old professional life without stopping the task.",
                "They cap the cleaned hardware immediately and mark the water container untouched."
            ],
            [
                d("Milo", "At a real shop we would wash this until it forgot the desert existed."),
                d("Arvin", "At a real shop the technicians are not choosing between cleaning hardware and drinking tomorrow."),
                d("Lucia", "You say that like you have made the other choice before."),
                d("Arvin", "I have worked for organizations with enough water to waste and still found ways to waste people."),
                d("Milo", "Dry clean, inspect, cap it. I can live with boring."),
                d("Arvin", "Boring hardware reaches orbit.")
            ],
            "Make water scarcity affect fabrication directly: cleaning, contamination control and reject rate. Do not turn the page into another water-policy debate.",
            "The character material happens because three people are stuck doing slow meticulous work together."
        ),
        "BR_S1E03_A02_SC01": page(
            "A cold-side seal begins to leak during a ground check. Arvin aborts immediately and isolates the line rather than gambling on launch. The failure exposes a material-compatibility problem in a salvaged seal whose service history is unknown. They now need a replacement from a specific class of industrial hardware before Cyrus closes the area.",
            [
                "A small frost pattern appears where it should not during the check; Arvin sees it before anyone else.",
                "Arvin calls the abort and everyone backs away in practiced order; no heroics around the live system.",
                "After the system is safe, Milo flexes the removed seal and finds it hardened and cracked.",
                "Arvin marks the failed part and its unknown provenance on the bench rather than throwing it away.",
                "Lucia unfolds the route map: the nearest plausible replacement source is already close to a Cyrus search corridor."
            ],
            [
                d("Arvin", "Abort. We learned enough."),
                d("Milo", "It looked fine yesterday."),
                d("Arvin", "Appearance is not service history."),
                d("Lucia", "The replacement lives forty miles toward the people hunting us."),
                d("Arvin", "Then the seal has chosen today's route.")
            ],
            "Show materials compatibility and unknown salvage history as the engineering problem. Keep procedures high-level and safety-minded rather than instructional.",
            "The failed component drives movement; Cyrus does not need to arrive on the page for his pressure to shape the decision."
        ),
        "BR_S1E03_A02_SC04": page(
            "Milo and Arvin run a low-energy pressure and fit check on the replacement hardware while Lucia packs the workshop around them. The test is intentionally incomplete because a full-duration noisy test would expose their location. Milo wants one more run; Arvin must decide what uncertainty they can carry into flight and what uncertainty is unacceptable.",
            [
                "Half the workshop is already packed while a small instrument panel records a cautious component check.",
                "The needle rises; Milo listens to the fitting and calls a subtle chatter.",
                "Lucia loads cases into the tanker while watching the ridgeline clock and their departure window.",
                "Arvin ends the test before the ideal data set is complete, then identifies the one remaining condition that still requires verification later.",
                "They label the component with what is known and unknown and load it last for easy access."
            ],
            [
                d("Milo", "Another run and I can tell you whether that chatter is the seat or the mount."),
                d("Lucia", "Another run and Cyrus gets another chance to tell us where we are."),
                d("Arvin", "We do not need perfect knowledge. We need to know which unknown can kill the flight."),
                d("Milo", "I hate that being hunted has become part of the test plan."),
                d("Arvin", "So do I. Pack the instruments.")
            ],
            "Testing itself has a signature—noise, heat, emissions, time in one place. Make the pursuit constrain engineering practice.",
            "Keep the disagreement practical, not philosophical; each person is right about a different risk."
        ),
        "BR_S1E03_A03_SC04": page(
            "During the final prelaunch run, vibration walks through the frame and intermittently corrupts one telemetry channel even though the propulsion hardware remains healthy. Milo wants to chase the bad reading; Arvin distinguishes between a sensor problem and a vehicle problem. Lucia forces them to decide what information is essential before the launch window closes.",
            [
                "The frame vibrates under test while one telemetry trace breaks into noise and the others remain coherent.",
                "Milo physically checks the suspect sensor mount; Arvin compares independent readings instead of trusting a single screen.",
                "Lucia calls the shrinking launch window while continuing to secure the mobile shop for departure.",
                "They isolate the bad channel from the go/no-go decision but mark it as a known blind spot.",
                "Quiet final panel: Arvin and Milo exchange a look over a machine that is good enough to fly but not perfectly knowable."
            ],
            [
                d("Milo", "The channel is lying."),
                d("Arvin", "Or the mount is shaking. Either way, the other measurements agree the vehicle is not."),
                d("Lucia", "Can you fly without that answer?"),
                d("Arvin", "Yes. I dislike it. Those are different statements."),
                d("Milo", "I am writing that on your grave."),
                d("Arvin", "Use legible lettering.")
            ],
            "Telemetry is information, not control. A failed sensor should not automatically become a failed rocket.",
            "Let humor appear under pressure without making the engineering unserious."
        ),
        "BR_S1E03_A03_SC06": page(
            "Immediately after the attempt, Arvin orders the crew to strip only the sensors, flight computer, scarce bearings and clean hardware from the test setup. They leave recoverable steel behind because Cyrus is closing. Milo hates abandoning material they could use; Lucia points out that mobility is now a design constraint on the entire Launch-Shop operation.",
            [
                "Distant pursuit lights appear while the crew is still reading post-test data.",
                "Arvin names the few components worth the minutes needed to remove them; everyone moves without debate.",
                "Milo looks back at useful steel and tooling they have to abandon.",
                "Lucia physically pulls the last case into the tanker as Cyrus's search aircraft cross the far ridge.",
                "The convoy leaves; abandoned heavy hardware becomes evidence Cyrus can read, but the irreplaceable parts are gone."
            ],
            [
                d("Arvin", "Sensors, computer, bearings, clean fittings. Leave the steel."),
                d("Milo", "I can use the steel."),
                d("Lucia", "You cannot use anything from a cell."),
                d("Arvin", "I love you both. I would also love to finish the failure analysis alive."),
                d("Milo", "Clear, human, still somehow a work order.")
            ],
            "Mobility creates a recurring inventory discipline: what is valuable enough to carry, what is replaceable, and what becomes a clue for Cyrus.",
            "End the issue on movement and unfinished engineering rather than a completed policy argument."
        ),
    },
    "S1E04": {
        "BR_S1E04_A01_SC01": page(
            "At a temporary limestone work site, Arvin and Milo hang the new payload and avionics on a crude balance fixture and discover the center of gravity has shifted aft. The rocket is not merely heavier; its mass is in the wrong place. Lucia arrives with news that their preferred salvage yard is under surveillance, forcing them to solve stability with the parts already on hand.",
            [
                "Rocket section suspended on a simple balance fixture; Arvin marks the actual balance point against the design mark.",
                "Milo shifts a payload box forward and watches the balance point move, realizing placement matters as much as total mass.",
                "Arvin sketches the relationship between center of gravity and aerodynamic pressure with two simple arrows directly on a removable panel.",
                "Lucia reports the salvage yard is compromised while helping relocate a battery module forward.",
                "They settle on a less convenient internal arrangement that restores stability without adding ballast."
            ],
            [
                d("Milo", "Same weight. Different place. Suddenly it wants to fly backward."),
                d("Arvin", "Weight tells you how hard gravity pulls. Placement tells you how the vehicle argues with the air."),
                d("Lucia", "Your actuator yard is being watched."),
                d("Milo", "So the battery moves."),
                d("Arvin", "The battery moves. Every cable complains. The rocket survives.")
            ],
            "Introduce center of gravity versus center of pressure visually and conceptually, without equations or procedural build instructions.",
            "The salvage threat should force a design compromise rather than pause the story for exposition."
        ),
        "BR_S1E04_A01_SC03": page(
            "At the quarry, Cyrus examines a discarded control-surface hinge and a worn actuator bearing. He recognizes that Arvin can rebalance the vehicle but will still need control authority in thin, fast airflow. Instead of searching caves indiscriminately, Cyrus orders quiet surveillance on an aircraft boneyard and two agricultural yards that stock rugged actuators.",
            [
                "Cyrus turns a recovered hinge in his gloved hand, measuring wear with his eyes before checking a compact gauge.",
                "A technician shows heat signatures from dozens of caves; Cyrus ignores them.",
                "Cyrus overlays three salvage sources that could plausibly supply actuators and bearings.",
                "He points out that a farm actuator is strong but slow and an aircraft actuator is fast but scarce; either choice reveals Arvin's next compromise.",
                "Final panel: surveillance vehicle parks outside the aircraft boneyard while appearing abandoned."
            ],
            [
                d("Cyrus", "He solved balance. Now he needs authority."),
                d("Technician", "We have forty-three possible camps."),
                d("Cyrus", "Camps move. Requirements do not."),
                d("Cyrus", "Watch the parts.")
            ],
            "Cyrus should infer the next engineering need from evidence. He is dangerous because he understands the sequence of problems.",
            "Do not make him omniscient; show the reasoning chain in objects and maps."
        ),
        "BR_S1E04_A01_SC05": page(
            "A gusty dry-lake test exposes a new problem: the improvised control surfaces have enough movement at low speed but not enough useful authority once the vehicle is loaded and the wind shifts. Arvin aborts the planned launch. Milo is furious at losing the window until Arvin shows that a rocket can have a functioning actuator and still lack enough aerodynamic leverage.",
            [
                "Wind snaps range flags around the loaded rocket while Milo cycles a control surface through its full travel.",
                "Arvin watches the surface move correctly, then looks at the gusts and the altered mass distribution.",
                "He calls the abort before fueling proceeds further.",
                "Milo points at the moving fin—nothing is broken; Arvin demonstrates that functioning movement is not the same as sufficient control.",
                "They roll the vehicle back toward cover as the sunset launch window disappears."
            ],
            [
                d("Milo", "It moves. Full travel. No binding."),
                d("Arvin", "Movement is not authority."),
                d("Milo", "That sentence feels designed to ruin my evening."),
                d("Arvin", "The air will ruin more than your evening."),
                d("Lucia", "We lose the window, not the vehicle. Move it.")
            ],
            "Vary failure mode: an abort caused by inadequate control margin, not an explosion or obvious broken part.",
            "Make the lost launch window emotionally costly; competence sometimes means refusing to launch."
        ),
        "BR_S1E04_A02_SC01": page(
            "The crew scavenges a rugged position sensor, shielded cable and mechanical linkage from a decommissioned tracking array and nearby farm equipment rather than finding a magical rocket part. Milo combines durable agricultural hardware with a precise aerospace sensor, while Arvin worries about response lag and Lucia watches for Cyrus.",
            [
                "Wide abandoned tracking array with old dish drives, service cabinets and windblown maintenance sheds.",
                "Milo frees a durable linkage from a farm-service actuator while Arvin inspects a smaller precision position sensor from the array.",
                "They compare the parts on the tailgate: one is rugged but imprecise, the other precise but delicate.",
                "Lucia sees a distant surveillance glint and starts the departure clock while still holding the work light.",
                "They leave with only the compact components they can test elsewhere, not the entire mechanism."
            ],
            [
                d("Milo", "The farm actuator has spent twenty years eating dust and ignoring complaints."),
                d("Arvin", "And it responds like a barn door."),
                d("Milo", "Then let the barn door carry the delicate part."),
                d("Lucia", "You have six minutes to finish insulting agriculture."),
                d("Arvin", "Pack both.")
            ],
            "Supply sourcing should combine real categories of salvage with redesign around what exists; never treat salvage as unlimited inventory.",
            "Use the work to show Arvin and Milo's different engineering instincts while Lucia contributes operational pressure."
        ),
        "BR_S1E04_A02_SC04": page(
            "A bench test in blowing sand reveals the new linkage survives load but its exposed bearing accumulates grit and begins to drag. Milo builds a simple sacrificial dust shield from replaceable material while Arvin accepts the added friction and inspection burden. Their solution is intentionally maintainable rather than elegant.",
            [
                "Linkage cycles on a crude fixture near the open tanker; airborne grit visibly reaches the exposed bearing.",
                "The current draw rises and the motion slows even though nothing catastrophically fails.",
                "Milo opens the bearing cover and shows a fine ring of abrasive dust.",
                "He adds a replaceable outer shield and a visible inspection witness mark rather than a sealed exotic component they cannot replace.",
                "Second test: slightly heavier motion but repeatable travel; Arvin signs off with a maintenance interval."
            ],
            [
                d("Milo", "The desert has entered the bearing."),
                d("Arvin", "The desert will enter everything. Design for the visit."),
                d("Milo", "Ugly shield, cheap fasteners, ten-minute replacement."),
                d("Arvin", "I withdraw every complaint I was preparing."),
                d("Lucia", "Save one. We are moving again.")
            ],
            "Treat sand as abrasion and contamination that changes friction and maintenance, not generic atmosphere.",
            "Prefer repairable rugged solutions to miracle materials."
        ),
        "BR_S1E04_A03_SC05": page(
            "The revised vehicle finally flies cleanly through the regime that defeated the previous attempt. Control authority improves as planned, but one telemetry antenna blanks during a roll and the ground crew temporarily loses a clean attitude read. The onboard guidance continues; Arvin refuses to confuse loss of visibility with loss of control.",
            [
                "Launch and early climb with clearly readable control-surface corrections in gusty air.",
                "Ground telemetry display loses one attitude channel as the vehicle rolls.",
                "Milo panics at the blank trace; Arvin points to independent data and the planned behavior of the onboard guidance.",
                "The signal returns after the geometry changes; the vehicle remains stable.",
                "Arvin writes two separate postflight notes: control solution passed; antenna coverage did not."
            ],
            [
                d("Milo", "We lost attitude."),
                d("Arvin", "We lost our view of attitude."),
                d("Lucia", "Important distinction?"),
                d("Arvin", "The rocket thinks so."),
                d("Milo", "Telemetry redesign goes on tomorrow's misery list.")
            ],
            "Separate control, guidance and telemetry as distinct systems with distinct failure modes.",
            "Success should produce the next engineering problem rather than reset the series."
        ),
        "BR_S1E04_A03_SC07": page(
            "Postflight inspection lasts only minutes because Cyrus has correctly predicted the test corridor. Arvin wants the control data; Milo wants the new actuator; Lucia insists they cannot recover both before pursuit arrives. They take the data package and the rare sensor, abandon the bulky linkage, and leave with a reproducible sketch.",
            [
                "Crew reaches the landed hardware while distant aircraft noise grows.",
                "Arvin downloads the compact flight recorder as Milo starts unbolting the large actuator.",
                "Lucia gives a hard departure time and points to incoming dust on the access road.",
                "Milo stops, measures the mounting pattern, photographs wear marks and leaves the bulky assembly.",
                "Cyrus arrives later to find the abandoned actuator—and realizes they learned enough not to need it."
            ],
            [
                d("Milo", "I just made that work."),
                d("Lucia", "Then you can make it work twice."),
                d("Arvin", "Take the sensor and the data. Measure the mount."),
                d("Milo", "I hate becoming the kind of person who leaves a good actuator in the desert."),
                d("Arvin", "You are becoming the kind who knows what is actually scarce.")
            ],
            "End Trip Point on knowledge becoming more portable than hardware.",
            "Cyrus pressure should force them to distinguish design knowledge from physical inventory."
        ),
    },
    "S1E05": {
        "BR_S1E05_A01_SC01": page(
            "At a dawn fuel-and-payload review, Arvin shows the crew that their desired reserve margin cannot simply be added on top of the existing vehicle. Extra propellant raises liftoff mass and steals payload; extra structure needed to carry it steals more. Lucia wants enough reserve for a guidance correction, Milo wants margin for an inefficient engine, and Arvin forces them to choose what uncertainty they are buying.",
            [
                "Handwritten load board beside the partially assembled rocket: payload, structure and reserve are separate movable tags.",
                "Lucia adds reserve for a possible course correction; Arvin moves the payload tag downward to show the trade.",
                "Milo argues the engine may underperform in desert heat; he is not wrong.",
                "The crew debates which uncertainty matters while physically reconfiguring cargo rather than standing around a table.",
                "They settle on a smaller payload and explicit reserve, leaving one desired instrument behind."
            ],
            [
                d("Lucia", "I want enough reserve to correct if guidance puts us long."),
                d("Milo", "I want enough reserve for the engine to be itself."),
                d("Arvin", "And the rocket wants us to stop pretending reserve is free."),
                d("Lucia", "Which instrument stays on the ground?"),
                d("Arvin", "The one that tells us the least about whether we can do this again.")
            ],
            "Make reserve margin a mass-allocation problem, not simply 'more fuel.' Keep it conceptual rather than numerical.",
            "The technical decision should reveal priorities: Lucia buys mission flexibility, Milo buys hardware uncertainty, Arvin buys repeatability."
        ),
        "BR_S1E05_A01_SC03": page(
            "A salvage stop at an abandoned mining maintenance yard produces a tempting lightweight pressure vessel and several structural members, but none has trustworthy fatigue history. Milo finds an older, heavier part with inspection records still stamped into its service case. Arvin chooses the heavier known component and must recover the mass elsewhere.",
            [
                "Rows of retired mining and industrial equipment under desert sun; the crew works fast while Tamz watches the access road.",
                "Milo finds a beautifully light component with surface damage and no traceable service history.",
                "Arvin studies it, then opens a battered storage case containing a heavier part with legible inspection records.",
                "Milo objects to carrying dead weight; Arvin points to hidden fatigue as an unknown they cannot inspect away in the field.",
                "They load the heavier component and leave the attractive lightweight one behind."
            ],
            [
                d("Milo", "This one is lighter by enough to buy back the instrument."),
                d("Arvin", "And old enough to have lived a life nobody wrote down."),
                d("Milo", "The ugly one has paperwork."),
                d("Arvin", "The ugly one has history."),
                d("Tamz", "You can continue this romance from the truck.")
            ],
            "Unknown fatigue history is a real salvage penalty. A component's past can matter as much as its dimensions.",
            "Use a mundane supply stop for character texture and a choice that propagates back into the mass budget."
        ),
        "BR_S1E05_A02_SC02": page(
            "Tethergrid interference makes external navigation unreliable along the intended corridor. Lucia demonstrates that a location fix can be plausible and wrong; Arvin refuses to make the rocket dependent on a single external source. They plan a layered guidance scheme in which onboard inertial sensing carries the vehicle through denial and independent references are used to bound drift when available.",
            [
                "Lucia shows two apparently credible position solutions disagreeing by enough to ruin the mission.",
                "Milo asks which display is broken; Lucia answers that neither has to look broken to be untrustworthy.",
                "Arvin checks the self-contained inertial package and notes that independence trades spoofing risk for accumulating drift.",
                "They map where independent references can correct uncertainty without making the vehicle dependent on constant contact.",
                "Final panel: the guidance plan has multiple sources with no single source labeled 'truth.'"
            ],
            [
                d("Milo", "Which one is lying?"),
                d("Lucia", "That is the problem. Both know how to look honest."),
                d("Arvin", "External fixes can correct drift. They do not get to own the vehicle."),
                d("Lucia", "And inertial guidance gets worse the longer we leave it alone."),
                d("Milo", "Excellent. Two kinds of wrong that can check each other.")
            ],
            "Differentiate guidance from telemetry and control. External navigation can be denied or spoofed; onboard inertial sensing is independent but drifts.",
            "Keep this as system architecture and decision-making, not instructions for defeating real-world navigation systems."
        ),
        "BR_S1E05_A02_SC05": page(
            "On a slow night drive between camps, Milo steadies the inertial package on a padded bench while Arvin compares its accumulated error against independent references. Lucia drives. The technical calibration becomes a long, mundane conversation about why Arvin stopped designing for organizations that could afford redundancy and why Milo joined someone who cannot.",
            [
                "Interior tanker at night; suspension movement gently disturbs a padded instrument bench while desert lights pass outside.",
                "Milo notes the inertial estimate wandering from an independent reference; Arvin records the rate rather than pretending to eliminate it.",
                "Lucia drives in silence for several panels while their technical talk drifts into Arvin's past employment.",
                "Milo asks why Arvin left before he knew whether this alternative would work.",
                "Arvin gives an incomplete but human answer, then immediately asks Milo to read the next error value."
            ],
            [
                d("Milo", "It drifts even sitting still."),
                d("Arvin", "Everything measures the world through its own imperfections."),
                d("Milo", "That is either engineering or therapy."),
                d("Lucia", "With him it is usually engineering pretending not to be therapy."),
                d("Milo", "Why did you leave before you had this figured out?"),
                d("Arvin", "Because knowing the old thing was wrong came before knowing I could build the new one. Read me the next value.")
            ],
            "Use long character conversation during necessary travel and work; the instrument keeps needing attention throughout.",
            "Character development does not pause the practical business of surviving."
        ),
        "BR_S1E05_A03_SC01": page(
            "Final loading reveals that the heavier known component from the mining yard consumed most of the planned reserve margin. Rather than secretly accepting it, the crew reopens the payload decision. Tamsin argues for the part of the payload communities can use immediately; Arvin removes a prestige experiment he personally wanted.",
            [
                "Loaded rocket on scales reads above target; no mystery, just accumulated choices.",
                "Arvin traces the excess to the heavier certified component and several small additions that seemed harmless alone.",
                "Tamsin separates immediately useful payload from experimental hardware.",
                "Arvin removes his own experiment and physically carries it back to the truck.",
                "New load check passes with a narrow reserve that everyone understands."
            ],
            [
                d("Tamsin", "Which box changes someone's week, and which box proves something to us?"),
                d("Arvin", "Mine proves something to me."),
                d("Milo", "That sounded painful."),
                d("Arvin", "Good engineering often sounds like equipment being removed."),
                d("Lucia", "Margin is back. Close the vehicle.")
            ],
            "Show cumulative mass creep: many small reasonable additions can consume reserve.",
            "The engineering choice should cost Arvin personally without becoming a speech about sacrifice."
        ),
        "BR_S1E05_A03_SC04": page(
            "During flight, the vehicle remains stable but enters a planned communications blind region. Telemetry disappears while the onboard guidance continues. The ground crew can either command an unnecessary intervention based on fear or trust the autonomy they deliberately built. Arvin chooses not to touch it.",
            [
                "Clean ascent telemetry approaches a known gap in ground coverage.",
                "All ground traces vanish together; Milo reaches for a command control.",
                "Arvin stops his hand and points to the preflight logic: simultaneous loss of ground channels was expected here.",
                "Long silent panel on the empty display while Lucia watches the clock.",
                "Telemetry returns later with the vehicle still on course and a complete onboard record waiting."
            ],
            [
                d("Milo", "Nothing."),
                d("Lucia", "Expected nothing or bad nothing?"),
                d("Arvin", "Expected. Do not turn uncertainty into a command."),
                d("Milo", "I preferred problems I could hit with a wrench."),
                d("Arvin", "You still have several waiting for you.")
            ],
            "Use telemetry dropout as an information problem, not a control failure.",
            "Let the long quiet interval create tension; restraint is the competent action."
        ),
        "BR_S1E05_A03_SC06": page(
            "The mission succeeds but not perfectly: the reserve is smaller than planned, one external navigation source was discarded as inconsistent, and the payload will have a shorter operational life because of the mass compromise. The crew's postflight conversation is practical and tired. Their success is a measured set of tradeoffs, not a victory reset.",
            [
                "Postflight data laid across a folding table while the crew eats from simple bowls with tools still scattered nearby.",
                "Arvin circles reserve usage; Lucia marks the rejected navigation fix; Milo notes an engine inefficiency that cost margin.",
                "Tamsin asks the only question communities care about first: what service will actually be available and for how long.",
                "They answer honestly, then immediately start a list for the next vehicle.",
                "Final panel: the rejected Arvin experiment sits unopened beside the new problem list."
            ],
            [
                d("Tamsin", "How long does this one help before we have to do it again?"),
                d("Arvin", "Less than I wanted. Long enough to matter."),
                d("Lucia", "Guidance rejected one bad fix exactly as designed."),
                d("Milo", "Engine ate more margin than predicted."),
                d("Arvin", "Then tomorrow has a list."),
                d("Milo", "Tomorrow always has a list.")
            ],
            "Close on accumulated engineering knowledge and ordinary fatigue, not another abstract declaration about the network.",
            "Success should narrow uncertainty and generate specific next work."
        ),
    },
    "S1E06": {
        "BR_S1E06_A01_SC02": page(
            "Milo's new ground relay survives dust and travel, then dies the instant a nearby pump motor starts. The same electrical noise that threatens community communications would also corrupt Launch-Shop's rocket telemetry if they reused the architecture. Arvin reframes the failure as an electromagnetic compatibility and grounding problem: the signal must survive the ugly electrical environment it actually lives in.",
            [
                "Rugged relay operating normally on a bench beside a working community pump installation.",
                "Pump motor starts; the relay display glitches and one telemetry test trace collapses into noise.",
                "Milo opens the unit expecting a burned component; Arvin first checks what the ground reference did during startup.",
                "They reproduce the disturbance with a safe bench simulation and see the same corrupted measurement without destroying another unit.",
                "Arvin labels the problem 'ground/reference/noise' beside both water-relay and rocket-telemetry sketches."
            ],
            [
                d("Milo", "It survived the desert, the dust and me. Then a pump starter killed it in one blink."),
                d("Arvin", "Maybe it did not kill anything. Maybe it moved the electrical ground and convinced the sensor the world moved with it."),
                d("Milo", "So the box can be healthy and the measurement can still be nonsense."),
                d("Arvin", "Welcome to telemetry.")
            ],
            "Make 'ground loop' an electrical engineering problem as well as an issue title: reference potentials, interference and sensor noise in concept, not a wiring tutorial.",
            "Tie the community system and rocket system together through shared harsh-environment engineering, not through repeated governance language."
        ),
        "BR_S1E06_A01_SC03": page(
            "Tamsin maps low-tech routes that already move medicine, repair parts and people between communities. Launch-Shop quietly uses the same traffic to disperse small rocket sensors, cable and bearings so no single convoy reveals a launch site. While sorting boxes with Milo, Tamsin learns exactly how particular he is about labeling after years of pretending to be chaotic.",
            [
                "Tamsin's route map beside ordinary maintenance schedules, not a futuristic command display.",
                "Milo divides compact rocket components among several normal service loads instead of one suspicious shipment.",
                "Tamsin catches his obsessively specific labels and teases the supposed improviser.",
                "They discuss who taught Milo to inventory parts while continuing to wrap and tag hardware.",
                "Final panel: multiple mundane vehicles leave in different directions carrying pieces that only become a rocket later."
            ],
            [
                d("Tamsin", "For a man who claims to work by instinct, you have three kinds of label."),
                d("Milo", "Four. Red means Arvin thinks I will lose it."),
                d("Tamsin", "Does that work?"),
                d("Milo", "I have never lost a red one."),
                d("Tamsin", "Then Arvin understands incentives.")
            ],
            "Use existing community movement as believable logistics for a nomadic aerospace shop, not as a magical distributed factory.",
            "The page's main pleasure is mundane work and character texture while the supply problem quietly advances."
        ),
        "BR_S1E06_A02_SC03": page(
            "Back at Launch-Shop, Milo reproduces the rugged pressure-switch idea with a spare governor, ceramic contact block and a spring seat he can actually machine. Arvin uses the same bench session to separate a noisy ground reference from a sensitive telemetry measurement path. Tamsin insists both systems need visible local failure indicators that a field mechanic can understand without a laptop.",
            [
                "Bench crowded with rugged mechanical parts on one side and delicate sensor wiring on the other.",
                "Milo assembles the mechanical switch while Arvin traces the source of a false sensor offset.",
                "Tamsin asks what a mechanic sees when the electronics lie; silence forces a redesign.",
                "They add a simple mechanical state indicator and a separate test point that exposes disagreement between physical state and telemetry.",
                "Final panel: two different technologies now fail legibly instead of failing mysteriously."
            ],
            [
                d("Tamsin", "What does the person at the pump see when your screen is wrong?"),
                d("Arvin", "At the moment, the screen."),
                d("Tamsin", "Then fix the answer, not the question."),
                d("Milo", "Mechanical flag. Hard to spoof, easy to swear at."),
                d("Arvin", "And the telemetry gets its own reference path.")
            ],
            "Show Tamsin's engineering contribution as maintainability and legibility, not generic civic wisdom.",
            "The chef should see both physical mechanisms and telemetry architecture on the same workbench."
        ),
        "BR_S1E06_A02_SC06": page(
            "They test the relay architecture by mounting one unit in the noisiest maintenance truck they own and another on a ridge. The truck alternator, motors and vibration create the electrical ugliness a pristine bench cannot. Milo drives washboard road while Arvin watches the rocket sensor test stream; Tamsin calls ordinary route stops. The link is slower than desired but the data remains distinguishable from noise.",
            [
                "Maintenance truck rattling along washboard road with relay and test sensors secured inside.",
                "Milo deliberately turns ordinary vehicle loads on and off while Arvin watches the trace for false jumps.",
                "Tamsin calls a route stop over the practical comms channel; the experiment has to coexist with real work.",
                "A burst of noise appears but no longer masquerades as a physical event.",
                "They accept lower data rate in exchange for a signal they can trust."
            ],
            [
                d("Milo", "If it survives this truck, orbit will be offended."),
                d("Arvin", "Orbit is quieter than your alternator."),
                d("Tamsin", "Next stop in six minutes. Your laboratory has to deliver filters."),
                d("Milo", "Science bows to plumbing."),
                d("Arvin", "Science is riding in a plumbing truck.")
            ],
            "Testing should happen in the actual dirty environment whenever possible; avoid pristine-lab logic.",
            "Use lower performance but higher robustness as a credible trade, not an upgrade in every dimension."
        ),
        "BR_S1E06_A03_SC02": page(
            "Cyrus correlates several short RF emissions with a moving maintenance route and notices one burst contains the timing signature of Launch-Shop flight telemetry. He cannot locate the shop from a single transmission, but repeated tests will give him a track. He orders teams to watch where the route can support a hidden static test rather than simply jamming harder.",
            [
                "Cyrus compares sparse RF time stamps against ordinary vehicle movement; most points are useless.",
                "One burst has a distinctive timing pattern matching recovered Launch-Shop flight hardware.",
                "A technician asks to jam the whole band; Cyrus refuses because it would erase the evidence.",
                "Cyrus marks likely places a moving shop could safely stop long enough for a test.",
                "Final panel: one site overlaps the crew's intended next stop."
            ],
            [
                d("Technician", "We can drown the band."),
                d("Cyrus", "And become deaf with them."),
                d("Cyrus", "They have to test. Testing takes time, power and a place to stand still."),
                d("Cyrus", "Find the places.")
            ],
            "Cyrus uses emissions as probabilistic evidence, not magical instant geolocation.",
            "The engineering need to test becomes the reason the crew must keep moving."
        ),
        "BR_S1E06_A03_SC06": page(
            "At dawn, the ground-loop relay scheme is working well enough for ordinary service and Launch-Shop's own field telemetry. Milo rolls out a heat-damaged nose-cone panel from the previous flight. He and Arvin inspect blistering, seam recession and discoloration while eating breakfast standing up. The next issue begins because the vehicle survived guidance and communications long enough for thermal protection to become the limiting problem.",
            [
                "Ridge relay continues ordinary traffic in the background; nobody celebrates at a control console.",
                "Milo drags a scorched nose-cone panel onto two crates beside breakfast cups.",
                "Arvin reads the heat damage pattern while Milo points to a seam that receded before the surrounding material.",
                "Lucia walks up already holding the departure map; they have limited time at this site.",
                "Final close-up: Arvin circles the damaged edge and writes 'material / attachment / expansion' on tape."
            ],
            [
                d("Milo", "Good news. The telemetry told us exactly how hot it got."),
                d("Arvin", "Better news would be the panel not agreeing."),
                d("Lucia", "You can hate the panel from the road in twenty minutes."),
                d("Milo", "Breakfast and failure analysis. We are becoming civilized."),
                d("Arvin", "Do not spread that rumor.")
            ],
            "Transition by engineering causality: solving one class of problem reveals the next limiting mechanism.",
            "Keep the closing conversation ordinary and affectionate while the crew works."
        ),
    },
    "S1E07": {
        "BR_S1E07_A01_SC01": page(
            "Tethergrid has blocked legitimate purchase of aerospace heat-shield tiles and bonding materials. Arvin also refuses a simple 'add more shielding' answer because every kilogram of thermal protection consumes payload and reserve. The crew inventories what they can actually source, including industrial refractory material, mechanical retainers and the limited clean water available for surface preparation.",
            [
                "Workbench inventory of unavailable aerospace parts crossed off beside industrial substitutes that are physically present.",
                "Arvin places a heavy sample on the mass ledger and removes an equivalent payload tag.",
                "Milo points to the community water ration needed for people and fabrication; wet cleaning cannot be assumed.",
                "Lucia asks what can be made repeatedly at scattered shops rather than perfectly once.",
                "They choose to investigate modular industrial ceramic with mechanical retention instead of a monolithic exotic shield."
            ],
            [
                d("Milo", "We can always add more tile."),
                d("Arvin", "We can always add more mass. The atmosphere will invoice us."),
                d("Lucia", "What can three different shops make without asking Tethergrid for permission?"),
                d("Arvin", "That is the useful question."),
                d("Milo", "And preferably without drinking the cleaning water.")
            ],
            "Combine thermal protection, mass penalty and water-limited fabrication in the same design decision.",
            "The constraint is repeatable field manufacture, not merely corporate access."
        ),
        "BR_S1E07_A01_SC02": page(
            "At a decommissioned industrial furnace site, Arvin identifies refractory ceramic that survived years of thermal cycling. The material can take heat, but its old mounting system and surface contamination make direct reuse unsafe. Milo salvages intact panels and attachment hardware while Arvin records how they were allowed to expand when hot.",
            [
                "Tall decommissioned furnace interior showing layered refractory panels and expansion joints.",
                "Arvin points to deliberate gaps and sliding retainers that let hot material grow without tearing itself apart.",
                "Milo rejects a cracked panel even though the center looks perfect; the attachment edge matters.",
                "They dry-brush and bag samples because water for washing is scarce and the ceramic must remain traceable by source.",
                "Lucia calls the departure as a distant Tethergrid patrol enters the industrial road."
            ],
            [
                d("Milo", "The ceramic survived."),
                d("Arvin", "Because the mounting let it move."),
                d("Milo", "So stealing the tile without stealing the idea would be the stupid version."),
                d("Arvin", "Correct. Please salvage the intelligent version."),
                d("Lucia", "Intelligent version has eight minutes.")
            ],
            "Use differential thermal expansion as the key observation: materials survive partly because attachments accommodate growth.",
            "Scavenging includes learning from existing machinery, not only taking parts."
        ),
        "BR_S1E07_A01_SC03": page(
            "Three small community workshops make sample tiles from the same pattern, but their results vary. Tamsin and Milo spend an afternoon gauging thickness, edge condition and fit while talking about jobs they had before any of this. Rejects pile up. The point is not that distributed fabrication is magical; it becomes viable only because the part is simple enough to inspect and reject locally.",
            [
                "Table covered with nearly identical ceramic samples from several workshops, each tagged by source.",
                "Tamsin uses a simple pass/fail gauge while Milo records rejects and resists 'fixing' marginal pieces by eye.",
                "They talk about old work lives while measuring dozens of boring parts.",
                "A rejected pile grows visibly larger than anyone likes.",
                "They identify which dimension causes most failures and simplify the pattern for the next batch."
            ],
            [
                d("Tamsin", "You used to repair amusement rides?"),
                d("Milo", "Three months. Children are excellent vibration sensors."),
                d("Tamsin", "That explains more than I wanted explained."),
                d("Milo", "This one almost passes."),
                d("Tamsin", "Almost is why the reject bin has a label."),
                d("Milo", "You and Arvin would have been unbearable coworkers.")
            ],
            "Show quality control, variability and reject rate as the price of decentralized fabrication.",
            "Use repetitive inspection work as space for dense, mundane character conversation."
        ),
        "BR_S1E07_A02_SC02": page(
            "The first full-scale thermal test fails without an explosion: the ceramic face survives, but a row of attachments binds as the hot shield expands. Several tiles lift at their edges and Arvin aborts the test. The failure proves the material choice may be sound while the attachment design is not.",
            [
                "Thermal test begins with instrumented tile field and clear expansion gaps.",
                "As heating continues, one row bows subtly because the retainers cannot slide as intended.",
                "Tile edges begin to lift; Arvin calls the abort before pieces depart.",
                "Cooldown inspection shows intact ceramic but polished witness marks where hardware bound.",
                "Milo lays the good tile beside the failed clip: the weak design is the attachment, not the heat material."
            ],
            [
                d("Milo", "The tile lived."),
                d("Arvin", "The attachment did not let it."),
                d("Lucia", "Can you fix the mounting without adding a new supply problem?"),
                d("Milo", "Give me boring metal and room for it to move."),
                d("Arvin", "That is the first encouraging sentence today.")
            ],
            "Vary failure: thermal material succeeds while attachment geometry fails under expansion.",
            "Keep the test visually readable and safety-conscious, without exact temperatures or hazardous process instructions."
        ),
        "BR_S1E07_A02_SC05": page(
            "Milo redesigns the shield as many small independently retained tiles with visible expansion gaps and replaceable edge clips. The new system is slightly heavier and aerodynamically less tidy, but a damaged tile can be replaced without rebuilding the nose. Arvin accepts the mass penalty because maintainability now has flight value.",
            [
                "Milo spreads small tiles and simple clips across a bench instead of one elegant large panel.",
                "He demonstrates how one tile can expand and be removed without disturbing its neighbors.",
                "Arvin adds the clip mass to the ledger and grimaces at the payload cost.",
                "Tamsin swaps a deliberately damaged tile using ordinary tools to prove the maintenance concept.",
                "Final panel: hundreds of plain numbered tiles await installation, impressive through repetition rather than exotic technology."
            ],
            [
                d("Milo", "Two hundred boring tiles."),
                d("Arvin", "And two hundred clips I now have to lift."),
                d("Tamsin", "One damaged tile no longer grounds the whole vehicle."),
                d("Arvin", "Fine. I will complain about the mass while approving the design."),
                d("Milo", "That is basically affection from you.")
            ],
            "Make maintainability an engineering trade with a real mass cost.",
            "The solution should look reproducible and inspectable, not like advanced magic."
        ),
        "BR_S1E07_A03_SC05": page(
            "News of Tamsin's detention reaches the crew while they are still fitting and gauging tiles. Nobody stops working for a dramatic circle. Lucia wants to divert immediately; Arvin wants the vehicle closed because an unfinished rocket cannot support any rescue route. Milo keeps passing tiles between them as the argument becomes personal.",
            [
                "Milo calls out tile numbers while Arvin gauges gaps and Lucia listens to the detention message.",
                "Lucia starts packing rescue gear with one hand while still handing over fasteners with the other.",
                "Arvin refuses to leave the shield half-installed because the vehicle may be their only way to force a safe corridor later.",
                "Milo makes them specify a concrete threshold: how many minutes until the vehicle can move and what rescue action begins then.",
                "They agree while continuing the same physical task; no one gets a clean emotional pause."
            ],
            [
                d("Lucia", "They took her because she stayed visible for us."),
                d("Arvin", "And if we leave this open, the vehicle cannot move."),
                d("Milo", "Stop making me choose which one of you is right. How many minutes?"),
                d("Arvin", "Twelve to close the shield."),
                d("Lucia", "Then in twelve minutes we are moving."),
                d("Milo", "Tile one ninety-one. Keep arguing.")
            ],
            "Character conflict occurs during necessary fabrication; work is not paused for a separate relationship scene.",
            "Make the twelve-minute threshold a practical compromise, not a moral resolution."
        ),
        "BR_S1E07_A03_SC06": page(
            "The rescue route and Sky-Piercer movement route become the same route because the crew cannot afford two convoys or two exposures to Cyrus. The thermal-shielded vehicle leaves before cosmetic work is finished, carrying spare tiles, gauges and the minimum launch hardware. Every object they take has to justify its weight and volume.",
            [
                "Crew loads rescue equipment beside launch hardware into the same limited vehicles.",
                "Milo tries to add a crate of extra tiles; Lucia asks what gets left behind to make room.",
                "They reduce the spares to the failure pattern actually observed in testing.",
                "Arvin straps the gauges and flight recorder where they can be reached without unloading the convoy.",
                "The convoy departs with primer marks and unfinished surfaces—the machine is ready enough, not polished."
            ],
            [
                d("Milo", "I want the whole spare crate."),
                d("Lucia", "Then name what we abandon for it."),
                d("Milo", "I hate logistics."),
                d("Arvin", "Logistics is engineering that has learned to drive."),
                d("Lucia", "Save the line. Move.")
            ],
            "Merge rescue and launch movement through volume, mass and exposure constraints rather than plot convenience.",
            "Preserve the nomadic visual identity: a functioning aerospace program that is always one departure away from becoming cargo."
        ),
    },
    "S1E08": {
        "BR_S1E08_A01_SC01": page(
            "Sky-Piercer sits complete on its mobile cradle, but the page reads as an accumulation of solved problems rather than a generic hero reveal. Tile 198 came from a school maintenance shop; a control linkage combines farm hardware with a precision sensor; the telemetry harness carries the grounding lessons from the pump-yard failure. Arvin, Milo and Lucia perform final provenance and access checks while talking like people who have done this too many times together.",
            [
                "Full vehicle on mobile cradle in bright dawn light; distinct subsystems visibly carry different material histories.",
                "Milo taps tile 198 and names its mundane source while Arvin checks the gap gauge.",
                "Lucia verifies access panels open without removing neighboring hardware—maintainability from prior failures.",
                "Arvin traces a telemetry cable route away from noisy power hardware and signs the final inspection tape.",
                "The three stand back only for a second before Milo notices one ordinary loose cover fastener and everyone returns to work."
            ],
            [
                d("Milo", "Tile one ninety-eight came from a school maintenance shop."),
                d("Arvin", "It passed the gauge."),
                d("Lucia", "Access panel clears. Steering linkage clears. Telemetry route?"),
                d("Arvin", "Separated and tested in the truck."),
                d("Milo", "Then it flies."),
                d("Lucia", "After you tighten the cover you are pretending not to see.")
            ],
            "Make Sky-Piercer visually legible as accumulated engineering knowledge and supply history.",
            "Avoid treating the rocket as a symbol before treating it as a machine people must inspect."
        ),
        "BR_S1E08_A01_SC03": page(
            "Lucia combines the rescue and launch plans while Arvin refuses one last request for extra propellant. The vehicle is already at its mass limit; carrying more reserve would require removing payload or changing the flight plan. Milo proposes offloading a nonessential ground spare instead. The conversation moves fluidly between Tamsin, mass, route timing and who is driving which truck.",
            [
                "Route map pinned beside the final mass ledger on the side of the tanker.",
                "Lucia moves the rescue timing and asks for more flight reserve; Arvin points to the closed mass budget.",
                "Milo identifies a bulky ground spare that can stay cached rather than fly or ride the launch convoy.",
                "They assign drivers and retrieval roles while physically shifting labeled cases between vehicles.",
                "Final panel: rescue route and launch route share one dangerous corridor because they have deliberately chosen the same moving footprint."
            ],
            [
                d("Lucia", "I want another correction margin if the storm moves."),
                d("Arvin", "Then choose what comes off the vehicle."),
                d("Milo", "Ground spare stays cached. It does not need to ride with us."),
                d("Lucia", "Good. I drive the lead. You two stay with the cradle."),
                d("Arvin", "And nobody adds anything after the final weigh."),
                d("Milo", "He means me.")
            ],
            "Reinforce the rocket equation/mass-budget lesson at the climax without repeating the earlier explanation.",
            "The plan is a lived crew conversation full of assignments and objects, not a strategic monologue."
        ),
        "BR_S1E08_A02_SC01": page(
            "The mobile cradle enters the sandstorm because it hides them from Cyrus, but concealment costs engineering margin. Grit abrades exposed surfaces, clogs cooling paths and reduces optical visibility. Arvin orders slower travel; Lucia accepts the delay because arriving with a damaged rocket is not arriving. Milo begins rotating sacrificial covers and filters from the moving support truck.",
            [
                "Convoy disappears into blowing sand; visibility collapses around the mobile cradle.",
                "Close views of sacrificial covers taking abrasion while protected mechanisms remain cleaner.",
                "A cooling indicator trends warmer as filters load; Arvin calls for reduced speed and load.",
                "Milo swaps an accessible sacrificial filter/cover during a sheltered stop while Lucia watches the pursuit clock.",
                "They resume slower, trading time for hardware survival."
            ],
            [
                d("Lucia", "The storm is hiding us."),
                d("Arvin", "It is also sanding the vehicle."),
                d("Milo", "Filter is loading. I have another."),
                d("Lucia", "How much slower?"),
                d("Arvin", "Slow enough that we still have a rocket when Cyrus finds the road.")
            ],
            "Sand is an engineering load: abrasion, contamination, cooling restriction and sensor visibility.",
            "Concealment and survivability pull in opposite directions; neither side of the trade is free."
        ),
        "BR_S1E08_A02_SC04": page(
            "A steering actuator begins to bind after grit gets past a worn outer seal. Milo does not declare the whole system broken. He compares commanded position with actual position, isolates the mechanical drag, replaces the sacrificial seal and cleans the protected bearing. Arvin checks that the actuator still meets the control margin established in Trip Point.",
            [
                "Steering test shows commanded movement and actual movement diverging under load.",
                "Milo feels the linkage and identifies mechanical drag rather than a guidance error.",
                "He opens only the serviceable outer section and finds grit beyond a worn sacrificial seal.",
                "After replacement and cleaning, the actuator moves freely; Arvin repeats the control-authority check rather than trusting 'it moves.'",
                "Final panel: Milo pockets the failed seal for later inspection as the convoy starts moving again."
            ],
            [
                d("Milo", "Command is clean. Position is late. That is drag, not guidance."),
                d("Arvin", "Fix the drag, then prove we still have authority."),
                d("Milo", "I miss when sand was scenery."),
                d("Lucia", "You have four minutes to become nostalgic."),
                d("Milo", "Failed seal is coming with us. I want to know why it lost.")
            ],
            "Remove the old meta line 'See? Infrastructure.' Keep the scene about diagnosis: command, actual position, mechanical drag and control margin.",
            "Carry forward prior lessons so the season feels cumulative rather than episodically reset."
        ),
        "BR_S1E08_A03_SC02": page(
            "During pressurization, one booster feed begins to oscillate. The crew does not chase it into catastrophe. Arvin isolates the suspect path and accepts an eight-percent performance loss; Lucia immediately recalculates what that does to reserve and abort options. Milo confirms the remaining feed is stable. The vehicle will fly with less margin or not fly at all.",
            [
                "Prelaunch instrument traces show one feed oscillating while the paired path remains stable.",
                "Arvin calls isolation of the suspect path before the oscillation grows.",
                "Milo confirms the remaining hardware settles; no one tries to 'tune through' an unstable condition.",
                "Lucia moves the new performance estimate against the flight reserve and weather corridor.",
                "They choose a reduced-performance flight profile that still meets the minimum mission requirement."
            ],
            [
                d("Arvin", "Isolate it. We are not negotiating with an oscillation."),
                d("Milo", "Remaining feed is steady."),
                d("Lucia", "We just spent eight percent of the performance margin."),
                d("Arvin", "Then tell me whether the remaining mission still closes."),
                d("Lucia", "Barely."),
                d("Arvin", "Barely is a number. Heroic is not.")
            ],
            "Use controlled loss as competent engineering: isolate an unstable subsystem and recompute the mission rather than forcing full performance.",
            "Keep this conceptual and fictional; no propellant composition or hazardous tuning details."
        ),
        "BR_S1E08_A03_SC03": page(
            "Sky-Piercer launches through the sandstorm. The early control surfaces work hard in gusts; onboard inertial guidance carries the vehicle when external navigation becomes unreliable; ground telemetry blanks behind the storm and terrain, then returns. The heat shield flexes and sheds sacrificial surface material without losing tiles. Every major season problem appears briefly as a system doing its job under stress.",
            [
                "Ignition and liftoff through blowing sand; control surfaces visibly correct against gusts without exaggerated aerobatics.",
                "Onboard guidance display remains coherent as an external position source is flagged inconsistent and ignored.",
                "Ground crew loses telemetry; Milo watches the blank screen but does not confuse it with loss of vehicle control.",
                "High-altitude view shows thermal shield intact, small sacrificial surface changes, and no magical pristine finish.",
                "Telemetry returns with Sky-Piercer on course; the crew's reaction is relief followed immediately by checking the next parameter."
            ],
            [
                d("Milo", "External fix disagrees."),
                d("Lucia", "Guidance rejected it."),
                d("Arvin", "Leave it rejected."),
                d("Milo", "Telemetry is gone."),
                d("Arvin", "Our view is gone. The vehicle still has a job."),
                d("Lucia", "Signal in three... two..."),
                d("Milo", "There.")
            ],
            "Integrate control, guidance, telemetry and thermal protection as distinct systems. The climax should reward the reader for learning the differences.",
            "Do not make all systems perfect; make them robust enough that one degraded input does not erase the whole vehicle."
        ),
        "BR_S1E08_A03_SC06": page(
            "At sunrise, the crew stands beside the cooling mobile cradle eating whatever breakfast survived the drive. Milo inspects the failed steering seal; Arvin reviews the isolated booster data; Lucia cleans sand from her boots and asks who is sleeping first. Tamsin joins them. Their conversation is mostly ordinary, with the enormous launch treated as work that now has maintenance attached.",
            [
                "Cooling cradle at sunrise with scuffed, used hardware; no ceremonial hero pose.",
                "Milo slices open the failed outer seal for inspection while eating one-handed.",
                "Arvin compares the seal wear to the sand route notes; Lucia sits on a case and removes grit from a boot.",
                "Tamsin arrives and asks whether anyone has slept; nobody answers immediately.",
                "They assign sleep, maintenance and next retrieval tasks with the ease of a crew that has become a household."
            ],
            [
                d("Tamsin", "Has anyone slept?"),
                d("Lucia", "Define slept."),
                d("Milo", "The seal failed from abrasion before the bearing did. I was right to bring it."),
                d("Arvin", "You were right. I dislike the precedent."),
                d("Lucia", "Milo sleeps first."),
                d("Milo", "I withdraw my finding."),
                d("Tamsin", "Too late. Science has spoken.")
            ],
            "Give the climax a long exhale through mundane maintenance and household-like banter.",
            "Character development should feel accumulated through shared labor, not delivered as a closing speech."
        ),
        "BR_S1E08_A03_SC08": page(
            "The season ends with Public Sky carrying useful traffic, but the final image belongs to Launch-Shop work rather than infrastructure governance. A maintenance message reports an intermittent relay problem; another community asks for a future launch window. Arvin listens while Milo rolls a battered replacement engine component onto the deck. Lucia sees Cyrus's distant aircraft changing course. Nobody says they have won. They start a new problem list and move.",
            [
                "Public Sky relay passes ordinary traffic in the background while local crews handle it without Launch-Shop.",
                "A maintenance message reports a mundane intermittent fault and is acknowledged by someone other than Arvin.",
                "Milo rolls a battered engine component onto the Launch-Shop deck with obvious enthusiasm.",
                "Lucia spots a distant Cyrus aircraft and taps the departure clock.",
                "Final panel: the mobile shop pulls away across the desert, new component strapped down, handwritten problem list fluttering under a clip."
            ],
            [
                d("Milo", "I found our next problem."),
                d("Arvin", "That is an engine part."),
                d("Milo", "Exactly."),
                d("Lucia", "Cyrus is turning south. We move in nine."),
                d("Tamsin", "Public Sky can handle tonight without us."),
                d("Arvin", "Good. Milo, tie down your problem.")
            ],
            "End on the recurring series engine: another hard machine problem, another move, another launch to earn.",
            "Infrastructure remains the reason the work matters, but the dramatic foreground is people building impossible hardware while being hunted."
        ),
    },
}

def decode(path: Path):
    raw = "".join(path.read_text(encoding="utf-8").split())
    return json.loads(gzip.decompress(base64.b64decode(raw, validate=True)).decode("utf-8"))

def encode(path: Path, payload):
    text = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    path.write_text(base64.b64encode(gzip.compress(text, mtime=0)).decode("ascii"), encoding="utf-8")

def apply_episode(ep, path):
    scenes = decode(path)
    index = {scene.get("id"): scene for scene in scenes}
    missing = [sid for sid in PATCHES[ep] if sid not in index]
    if missing:
        raise SystemExit(f"{ep}: missing target scene ids: {missing}")
    for sid, patch in PATCHES[ep].items():
        index[sid].update(patch)
    for sid in PATCHES[ep]:
        scene = index[sid]
        for field in ("summary", "panelPlan", "dialogueInline", "directionInline"):
            if not scene.get(field):
                raise SystemExit(f"{sid}: patched chef-visible field {field} is empty")
        if len(scene["panelPlan"]) < 4:
            raise SystemExit(f"{sid}: patched page has fewer than four planned panels")
        if len(scene["dialogueInline"]) < 3:
            raise SystemExit(f"{sid}: patched page has fewer than three dialogue lines")
    encode(path, scenes)
    return len(PATCHES[ep]), len(scenes)

def main():
    total = 0
    for ep, path in FILES.items():
        changed, count = apply_episode(ep, path)
        total += changed
        print(f"{ep}: rewrote {changed} of {count} production pages")
    print(f"Backyard Rockets developmental engineering pass complete: {total} page recipes rewritten")

if __name__ == "__main__":
    main()
