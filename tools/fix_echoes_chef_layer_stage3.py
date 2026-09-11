#!/usr/bin/env python3
"""Deep cleanup of Echoes panel plans: replace editorial interpretation with drawable staging."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data" / "shows" / "echoes-forgotten-war-s1"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def apply(path: Path, changes: dict[tuple[str, int], str]) -> None:
    records = load(path)
    by_id = {record["id"]: record for record in records}
    for (scene_id, panel_number), text in changes.items():
        plan = by_id[scene_id]["panelPlan"]
        assert 1 <= panel_number <= len(plan), (scene_id, panel_number)
        plan[panel_number - 1]["text"] = text
    dump(path, records)


SOURCE = {
    1: {
        ("EFW_S1E01_S01", 2): "Panel 2 — Vark comes down the metal access stairs toward Theo with an overtime form tucked under one arm. Theo keeps both hands on the drill controls, shoulders high and tense, eyes fixed on the cut instead of Vark.",
        ("EFW_S1E01_S01", 6): "Panel 6 — Large final panel. The drill bites into a smooth dark manufactured surface beneath the black bedrock; work lamps flicker across it. Theo freezes over the controls and says, 'That's it.' Vark stops several steps behind him, staring first at the object and then at Theo's frightened face.",
        ("EFW_S1E01_S02", 2): "Panel 2 — Insert on the archive interface as an erased Olyria-Prime location begins repopulating line by line. A restricted line appears clearly and exactly: REDLIN PROTOCOL. Rae's hand stops over the controls; her eyes stay on the word and her mouth tightens.",
        ("EFW_S1E01_S02", 4): "Panel 4 — Two-shot for 'I didn't ask what the report says.' / 'Then you should ask the people who wrote it.' Rae sits back with one eyebrow raised and one hand covering the recovered entry; Caelum remains upright, hands clasped behind him, expression controlled.",
        ("EFW_S1E01_S02", 7): "Panel 7 — Caelum says he wants the screen behind Rae; she answers, 'That's a different request.' After he moves on, end with Rae alone between her handwritten dream notes and the screen still showing the forbidden Olyria entry and REDLIN PROTOCOL. Her eyes move between the same repeated name in both places.",
        ("EFW_S1E01_S03", 8): "Panel 8 — Final close in the present. Theo is on the trench floor, empty hand curled as if it still held something. Vark has dropped to one knee beside him and no longer reaches for the radio. Theo stares past him toward the Marker, breathing hard.",
        ("EFW_S1E01_S04", 7): "Panel 7 — Final close on Adrian answering exactly, 'Yes.' Theo's grip loosens on the bed rail; his eyes stay locked on Adrian while Adrian finally looks toward the Marker behind him.",
        ("EFW_S1E01_S05", 5): "Panel 5 — Caelum holds out his hand for the drive. Rae keeps it against her chest and repeats the demand for the name. Caelum answers only, 'Rae.' She stops moving and studies his face before closing her fingers around the drive.",
        ("EFW_S1E01_S06", 1): "Panel 1 — Field triage tent. Theo sits on a cot while an overworked medic wraps his injured hand. The nearby network terminal is dark; Vark fills out a paper incident form beside a stained coffee cup, spare bandages and worker boots.",
        ("EFW_S1E01_S09", 7): "Panel 7 — Rae feeds the copied record into an ordinary secure disposal slot and watches the last physical sheet disappear. Caelum lunges one step too late, hand out toward the empty tray. Rae turns away from him and exits carrying nothing.",
        ("EFW_S1E01_S11", 3): "Panel 3 — Adrian: 'I did.' Rae: 'I destroyed the trail.' Rae drops her archive badge and identification crystal onto the damaged desk beside the erased records; Adrian looks from the objects to her packed coat and bag.",
        ("EFW_S1E01_S11", 7): "Panel 7 — Rae: 'How do you know about the dreams?' Adrian: 'Because you aren't the first.' End tight on Rae: her eyes widen slightly, then shift toward the sealed archive door as she grips the strap of her bag.",
        ("EFW_S1E01_S12", 6): "Panel 6 — Theo: 'You heard it too.' Adrian: 'Put the shard down.' Adrian has already stepped backward from the warming fragment, one hand braced against the wall. Theo watches that involuntary movement instead of the shard."
    },
    2: {
        ("EFW_S1E02_S01", 3): "Panel 3 — Close alternating reactions for 'I didn't see that.' / 'I did.' Theo taps one sketch; Rae immediately points to a different note on the same table. Both keep steady eye contact until Adrian leans between the two sets of papers: 'Stop. You saw different parts of it.'",
        ("EFW_S1E02_S03", 2): "Panel 2 — Redlin enters dusty and already helping an injured civilian through the doorway: 'Still talking about me like I'm late to my own funeral?' Starbreaker answers, 'You are late.' Mero stays at the table and looks from one to the other before speaking.",
        ("EFW_S1E02_S03", 3): "Panel 3 — Starbreaker: 'People were leaving.' Redlin: 'People are always leaving when you arrive.' Redlin adds, 'Because they're still alive,' while tightening the injured civilian's support strap. Starbreaker looks away toward the evacuation route for one beat.",
        ("EFW_S1E02_S03", 5): "Panel 5 — Final two-shot. Redlin: 'Maybe because you keep burning them.' Redlin's anger drops into exhaustion; Starbreaker's jaw tightens and his gaze falls to the damaged floor between them. Neither advances.",
        ("EFW_S1E02_S04", 3): "Panel 3 — 'I don't need that lesson.' / 'Then learn their names anyway.' Redlin stops beside a seated family and crouches to their eye level; one child reaches toward a familiar mark on his armor. No additional lettering.",
        ("EFW_S1E02_S04", 4): "Panel 4 — Mero asks, 'And if you can't hold it?' Redlin keeps one hand on the civilian's shoulder and looks toward the crowded exit instead of turning back to Mero.",
        ("EFW_S1E02_S05", 4): "Panel 4 — Starbreaker looks toward a distant evacuation column: 'I think there can still be places left to fix.' His shoulders sag, damaged armor hangs open at one side and the weapon light around his hand remains unformed.",
        ("EFW_S1E02_S06", 2): "Panel 2 — Mero places himself physically between Starbreaker and Redlin: 'One hour. Both of you stand down.' Starbreaker and Redlin answer from opposite sides without looking at Mero; all three hold positions they have clearly occupied before.",
        ("EFW_S1E02_S06", 3): "Panel 3 — Use close opposing profiles as Redlin and Starbreaker trade the evacuation/delay lines. Redlin flinches at the word 'spread'; Starbreaker's eyes flick toward the transports when Redlin says people remain inside the blast.",
        ("EFW_S1E02_S08", 4): "Panel 4 — Starbreaker: 'I used to trust you to know when enough was enough.' Redlin answers, 'I used to trust you to know when you were moving too soon.' Both lower their voices; Redlin looks down first, Starbreaker toward the distant civilian line.",
        ("EFW_S1E02_S09", 1): "Panel 1 — Wide battlefield. Distant structures bow into impossible light, dust rises upward and civilians turn toward the sky before any visible impact reaches them. Keep the phenomenon entirely in the environment and human reactions; no diagram or interface appears.",
        ("EFW_S1E02_S09", 5): "Panel 5 — Large final panel. Starbreaker's fractured stellar light meets Redlin's holding field and the sky breaks into hard unnatural geometry above them. Mero and fleeing civilians occupy a tiny lower strip of the composition beneath the enormous fracture.",
        ("EFW_S1E02_S11", 4): "Panel 4 — Rae: 'I don't remember the ridge.' Theo slides his sketch beside hers. The two drawings overlap in the central event but show different foreground terrain; both lean over the mismatch in silence."
    },
    3: {
        ("EFW_S1E03_S01", 5): "Panel 5 — Rae: 'That hasn't worked for either of us yet.' She is already walking down the crowded corridor toward the disturbance, weaving between workers and supply carts while Theo hesitates one step behind.",
        ("EFW_S1E03_S02", 4): "Panel 4 — 'No.' / 'You didn't hesitate.' Theo's raised finger stops in mid-gesture. He looks down at the route he identified instantly, then back at Rae with his certainty visibly shaken.",
        ("EFW_S1E03_S03", 5): "Panel 5 — Adrian: 'Then help them. Leave the history alone.' Rae turns and runs toward the service exit with two port workers; Theo follows while Adrian remains beside the exposed old structure.",
        ("EFW_S1E03_S05", 1): "Panel 1 — Rae snaps back into the present service corridor with one hand still on old stone. Workers push carts, lift a child over a jammed barrier and clear access around a stalled service vehicle while alarms flash along the ordinary ceiling.",
        ("EFW_S1E03_S07", 3): "Panel 3 — Rae and two workers wrench a manual gate fully open. A family, a medical cart and several port workers immediately move through the new space while another crew drags the stalled vehicle aside.",
        ("EFW_S1E03_S09", 3): "Panel 3 — 'There's a ship under the city.' Rae, still guiding workers: 'Of course there is.' She does not stop moving; Theo stares at the exposed hull with exhausted disbelief while a worker squeezes past carrying emergency supplies.",
        ("EFW_S1E03_S10", 3): "Panel 3 — Rae, Theo and Adrian stand inside the same frightened civilian crowd. Rae: 'Everyone can see it.' Adrian: 'Yes.' Behind him multiple people point phones, lights and bare hands toward the exposed hull; Adrian has nowhere private to move the conversation.",
        ("EFW_S1E03_S10", 4): "Panel 4 — Theo: 'Good.' His shoulders drop and he exhales while looking at the openly visible hull. Adrian turns the opposite direction and watches a frightened parent pull a child closer.",
        ("EFW_S1E03_S11", 3): "Panel 3 — Theo: 'You couldn't let me have that, could you?' Rae: 'I had to tell the truth.' They face each other at close range; Rae's free hand still supports an injured refugee and Theo's irritation softens when he notices.",
        ("EFW_S1E03_S11", 4): "Panel 4 — Theo watches Rae steady the refugee as workers pass them toward shelter and says, 'Atlas would like you.' Rae glances at him but keeps both hands on the person she is helping.",
        ("EFW_S1E03_S12", 3): "Panel 3 — Rae looks from the occupied modern buildings to Adrian and says, 'You erased what it meant.' Adrian answers, 'Yes.' Hold close on Adrian's weathered face; he cannot maintain eye contact after the answer.",
        ("EFW_S1E03_S12", 4): "Panel 4 — Theo: 'And you thought that was enough.' Frame Theo beneath ordinary apartments and utility lines visibly anchored into the forgotten dreadnought hull."
    },
    4: {
        ("EFW_S1E04_S02", 3): "Panel 3 — Mero, dryly: 'That was easy.' Redlin: 'Don't get used to it.' Atlas almost smiles; Redlin gives Mero a tired sideways look while transport crews continue working beyond the open doors.",
        ("EFW_S1E04_S03", 1): "Panel 1 — Arbiter enters alone in pale/dark judicial armor with restrained gold structure. Her shoulders are slightly rounded under the armor, one gauntlet carries a worn physical case and her face shows fatigue; Mero, Atlas and Redlin turn toward her.",
        ("EFW_S1E04_S03", 4): "Panel 4 — Arbiter: 'No. I prefer when the person making a promise stays in the room.' Atlas stops pacing and squares his feet beside the table; Arbiter keeps her eyes on him until he gives a small nod.",
        ("EFW_S1E04_S04", 3): "Panel 3 — Arbiter: 'I came prepared to admit that might be the choice.' She keeps both hands flat on the stone sill and looks down at the evacuation lanes while she says it; her face remains tense and tired.",
        ("EFW_S1E04_S05", 3): "Panel 3 — Mero, exhausted: 'I missed both of you.' Starbreaker and Redlin both glance at him; Redlin gives the smallest involuntary half-smile before Arbiter answers.",
        ("EFW_S1E04_S05", 5): "Panel 5 — Mero: 'No. I really didn't.' A brief rueful look passes between Mero, Redlin and Starbreaker, then all three turn toward the worsening alarm and the civilians moving beyond the doors.",
        ("EFW_S1E04_S07", 2): "Panel 2 — Mero steps closer to Arbiter and lowers his voice: 'Can you live with it?' His command posture is gone; one hand rests heavily on the table and he waits for her face rather than a formal ruling.",
        ("EFW_S1E04_S07", 3): "Panel 3 — Arbiter: 'That is not the standard.' Mero: 'It should be somewhere on the list.' Arbiter's eyes drop to his exhausted hand on the table, then return to his face before she answers.",
        ("EFW_S1E04_S08", 1): "Panel 1 — Evacuation concourse under an impossible sky. Atlas lifts a collapsed barrier, Redlin supports an injured civilian under one arm and Starbreaker carries two heavy baggage cases while moving with the crowd. No ancient Theo or Rae appears.",
        ("EFW_S1E04_S09", 3): "Panel 3 — Atlas: 'No.' Arbiter: 'I know.' Arbiter looks at Atlas for a long beat, then turns back to the decision sheet without asking him to agree.",
        ("EFW_S1E04_S11", 1): "Panel 1 — Hard return to the same quiet present-day vault composition as the opening page. Theo and Rae are shaken and off-balance. Adrian immediately steps toward them when he sees Rae gripping the chair and Theo touching his temple.",
        ("EFW_S1E04_S11", 2): "Panel 2 — Rae keeps her eyes on the empty chair: 'Arbiter crossed out the first line.' Theo watches Rae rather than the chair and asks, 'What line?' No flashback occupies the panel.",
        ("EFW_S1E04_S11", 4): "Panel 4 — Theo: 'Mero said he hadn't slept in three days.' Rae: 'That wasn't in the room.' Theo stops speaking and looks toward Adrian; Rae turns from the chair to Theo, both visibly unsettled by the private detail.",
        ("EFW_S1E04_S12", 5): "Panel 5 — Adrian: 'Because that was the last thing the Reset took.' Rae: 'What did we do?' Adrian: 'That's what I'm afraid you'll remember next.' End on Theo and Rae standing shoulder-width apart at the black table, both staring at Adrian; keep only their present-day bodies in frame."
    },
    5: {
        ("EFW_S1E05_S02", 3): "Panel 3 — Wider still: ancient Theo is fully visible behind Mero, younger in bearing but unmistakably the same person, dressed as a junior attaché with plain staff layers, dispatch satchel and worn papers. He stands naturally inside the command group.",
        ("EFW_S1E05_S03", 2): "Panel 2 — Theo: 'He knew my name.' He sits on the edge of the cot with both palms pressed against his knees, eyes wet and fixed on the floor; his breathing is shallow and he cannot look at Rae yet.",
        ("EFW_S1E05_S03", 3): "Panel 3 — Rae: 'You knew his voice.' Theo finally looks up at her. His expression changes abruptly and one hand lifts in the same attentive half-gesture ancient Theo used beside Mero.",
        ("EFW_S1E05_S05", 2): "Panel 2 — Rae stops mid-corridor: 'I wrote it down.' Adrian: 'Yes.' Rae's pace breaks completely; she looks at her own writing hand and then closes it into a fist.",
        ("EFW_S1E05_S05", 5): "Panel 5 — Adrian: 'I don't know anymore.' End with Adrian physically isolated between Theo and Rae. His shoulders sag, his hands hang empty and he looks toward the floor instead of either of them.",
        ("EFW_S1E05_S06", 1): "Panel 1 — Ancient aftermath at human scale: shelters, patched roofs, burned streets, injured vegetation, survivors cooking and carrying water. Afterlight kneels beside one damaged living thing in the foreground while many other unfinished repairs remain visible across the settlement.",
        ("EFW_S1E05_S06", 3): "Panel 3 — Compose several needs in one frame around Afterlight: a wounded survivor waiting on a cot, a broken shelter roof, a dead patch of ground and a child carrying water. Afterlight can reach only the living plant immediately under her hands.",
        ("EFW_S1E05_S06", 4): "Panel 4 — Atlas: 'What do you need?' Afterlight looks up at him: 'For nothing else to happen.' Atlas's raised hand stops before touching her shoulder; both look out at the unfinished settlement.",
        ("EFW_S1E05_S07", 4): "Panel 4 — Afterlight: 'Don't do that.' Starbreaker: 'Do what?' Starbreaker genuinely pauses mid-step, brows drawn and open hands slightly raised; Afterlight turns fully toward him.",
        ("EFW_S1E05_S07", 5): "Panel 5 — Afterlight faces Starbreaker: 'Turn what I can mend into permission for what you break.' Leave a full body's width between them; the restored patch beside Afterlight and distant battle damage behind Starbreaker occupy opposite sides of the panel.",
        ("EFW_S1E05_S09", 1): "Panel 1 — Night restoration camp. Occupied shelter beds, damaged plants, stacked names, repair materials and people sleeping in shifts surround Afterlight. Atlas sits on a low crate several feet away, keeping watch at her level.",
        ("EFW_S1E05_S09", 4): "Panel 4 — Atlas: 'No one can.' Afterlight: 'That's what I'm telling you.' Atlas starts to answer, then closes his mouth and looks across the rows of unfinished work instead.",
        ("EFW_S1E05_S11", 4): "Panel 4 — Mero: 'Because you notice when the rest of us are.' Mero gives Theo the smallest tired smile and takes the dispatch from his hand; Theo remains beside him at the same shoulder position established in the earlier memory."
    }
}

OVERLAY = {
    6: {
        ("EFW_S1E06_S02", 5): "Panel 5 — Flux: 'Mero needs permission. That's different.' Afterlight looks from Flux to the closed council-room door, then pulls out the chair opposite him and sits instead of urging him toward it.",
        ("EFW_S1E06_S03", 4): "Panel 4 — Theo: 'That's worse somehow.' Rae lays two reused records side by side and traces matching physical repairs, handwriting and ownership marks across them; no hidden screen or archive mechanism appears.",
        ("EFW_S1E06_S03", 5): "Panel 5 — Rae: 'Because nobody preserved it. They just kept using it.' End tight on layers of old paper: erased headings, later annotations, patched tears and fresh present-day handling marks occupying the same sheets.",
        ("EFW_S1E06_S04", 1): "Panel 1 — Ancient council room after the argument has emptied out. Chairs stand crooked around abandoned papers; Mero remains at the table and Flux is the only other person still in the room.",
        ("EFW_S1E06_S04", 4): "Panel 4 — Flux: 'Then stop asking me to dream for you.' Mero grips the back of an empty chair until his knuckles whiten, then releases it and steps away from the table instead of answering immediately.",
        ("EFW_S1E06_S05", 2): "Panel 2 — Adrian: 'That's not what was removed.' He keeps descending the stairs while Theo and Rae stop above him. Adrian does not turn toward the museum labels or offer any visual aid.",
        ("EFW_S1E06_S07", 3): "Panel 3 — Theo: 'That's your answer?' Rae: 'It's the part you keep skipping.' Rae points through the public window toward families crossing the plaza below; Theo follows her finger instead of looking back at the monument.",
        ("EFW_S1E06_S08", 1): "Panel 1 — Return to the ancient kitchen late at night. Flux packs one small bag on the chair. The same cold cup from the morning remains untouched on the table beside a dried ring of spilled drink.",
        ("EFW_S1E06_S08", 2): "Panel 2 — Afterlight: 'You're leaving.' Flux: 'I'm trying.' Afterlight steps sideways out of the doorway and leaves a clear path to the hall; her hands stay at her sides.",
        ("EFW_S1E06_S08", 3): "Panel 3 — Afterlight: 'Where?' Flux stops with one hand on the doorframe and the packed bag hanging from the other. He stares into the empty corridor before answering.",
        ("EFW_S1E06_S09", 2): "Panel 2 — Rae: 'Which parts are real?' Adrian answers, 'All of them.' Keep all three at the physical table with books and records between them; Rae presses one palm onto the open pages while Adrian meets her eyes.",
        ("EFW_S1E06_S11", 1): "Panel 1 — Present transit platform among ordinary commuters. Theo grips a rail and briefly assumes the same shoulder angle as his ancient staff posture; Rae's hand pauses over a ticket as her gaze fixes on a passing stranger. No visual effect surrounds either of them.",
        ("EFW_S1E06_S11", 5): "Panel 5 — Rae: 'About what we called the people inside it.' End on an old record open between Theo and Rae, with their own ancient handwriting or classifications visible beside names of ordinary people; both stare down at the marks they once made.",
        ("EFW_S1E06_S12", 1): "Panel 1 — Same ordinary transit platform. A worker pauses mid-announcement and says, 'No. That's not what it was called.' Nearby commuters stop walking and look toward the worker while the departure flow continues behind them."
    },
    7: {
        ("EFW_S1E07_S02", 1): "Panel 1 — Ancient Neo-Vectra command balcony above a populated city already preparing for war. Oryon stands at the rail with his gaze fixed on specific families and evacuation crews below; Arbiter watches Oryon's face instead of the tactical display.",
        ("EFW_S1E07_S02", 2): "Panel 2 — Oryon: 'If we wait, this city becomes the beginning.' Arbiter: 'Of what?' Oryon's shoulders are rigid, both hands locked around the rail and his eyes remain on the people below.",
        ("EFW_S1E07_S02", 4): "Panel 4 — Arbiter: 'You've said that before.' Oryon: 'Because it keeps being true.' Arbiter delivers the line without turning from the balcony; Oryon gives a tired sideways glance before answering.",
        ("EFW_S1E07_S02", 5): "Panel 5 — Arbiter: 'Or because you keep looking for the same ending.' Oryon releases the rail with one hand and turns away from the tactical display, face unsettled and silent.",
        ("EFW_S1E07_S03", 3): "Panel 3 — Rae: 'They deserve not to get killed while we're explaining it.' Two strangers in the foreground argue over a recovered emblem one recognizes and the other does not; neither has any physical evidence beyond the emblem and their reactions.",
        ("EFW_S1E07_S04", 1): "Panel 1 — Ancient residential concourse under evacuation. Atlas physically shields civilians while Oryon arrives with Mero urging withdrawal. Surround them with distinct people: a parent with two children, an older medic, a worker carrying a pet carrier and a wounded transit officer.",
        ("EFW_S1E07_S04", 4): "Panel 4 — Atlas: 'Then help me save both.' Oryon: 'There is no both.' Atlas stops moving for one beat; Oryon cannot meet his eyes and looks instead at the civilians passing between them.",
        ("EFW_S1E07_S04", 6): "Panel 6 — Mero: 'That false choice keeps ruining us.' Atlas and Oryon stand on opposite sides of the same evacuation lane, each physically helping people move through while neither answers Mero.",
        ("EFW_S1E07_S05", 1): "Panel 1 — Return to the same concourse footprint in the present. The arguing couple fills the foreground with shared bags and keys between them; Theo stands farther back near the architectural spot where Atlas once stood.",
        ("EFW_S1E07_S05", 2): "Panel 2 — The man recoils from the woman he loves: 'You were with them.' She answers, 'With who?' Keep their shared key ring looped around her finger, matching travel bags at their feet and his half-raised hand still close to hers.",
        ("EFW_S1E07_S07", 1): "Panel 1 — Municipal shelter after several fights. Volunteers separate two arguing people, wrap a minor injury and keep a family together. Theo carries folded blankets, Rae kneels beside a cot and Adrian holds a water container while they continue talking.",
        ("EFW_S1E07_S08", 1): "Panel 1 — Ancient Mero staff room during Neo-Vectra. Senior voices argue behind a closed door. Mero closes the inner office door, pulls a plain chair beside junior Theo and sits at the same level rather than summoning him to the command table.",
        ("EFW_S1E07_S10", 5): "Panel 5 — Arbiter asks, 'And the north?' Rae's pen stops directly over the next neighborhood name. She looks at the unmarked north list, then at Arbiter, without writing.",
        ("EFW_S1E07_S10", 6): "Panel 6 — Rae: 'I know.' End on the physical list with several chosen names marked and the unchosen north names still fully visible beside Rae's motionless pen."
    },
    8: {
        ("EFW_S1E08_S01", 2): "Panel 2 — Theo steps ahead of Rae and blocks Adrian's path deeper into the chamber: 'You brought us here to do it again.' Adrian stops at the threshold with both hands visible and empty.",
        ("EFW_S1E08_S01", 3): "Panel 3 — Adrian: 'I brought you here because I don't know what else stops this.' His back stays against the doorway, shoulders tight and face pale; he does not move toward the central scar.",
        ("EFW_S1E08_S02", 4): "Panel 4 — Kyn describes the spread while the page shows specific close human memories: one person recoils from an old faction mark on a stranger, another carries a dead companion through a doorway and a third clutches someone whose name has just returned to them. Keep each memory grounded in faces and touch.",
        ("EFW_S1E08_S03", 5): "Panel 5 — Theo: 'I hated that door.' Rae: 'I used to wait outside it.' In matching present/ancient compositions, Theo's body leans away from the same doorway while Rae occupies the same waiting spot against the opposite wall.",
        ("EFW_S1E08_S04", 5): "Panel 5 — Arbiter: 'So is pretending this room can make one without blood on it.' Arbiter places both hands on the table; around her the others avoid eye contact, and no empty seat offers a clean center to the composition.",
        ("EFW_S1E08_S04", 6): "Panel 6 — Kyn: 'Then stop asking for a clean choice.' End on the full silent group with Flux's established empty chair still plainly visible among occupied seats.",
        ("EFW_S1E08_S05", 4): "Panel 4 — Theo: 'They were stolen from them.' Rae's eyes move from Theo to Adrian while both men stand on opposite sides of the central scar. Rae steps one pace toward the space between them.",
        ("EFW_S1E08_S06", 3): "Panel 3 — Kyn: 'That's all?' Afterlight: 'That's always all.' They sit close beside the same exhausted survivor; Kyn's hand remains under the survivor's while Afterlight keeps one hand on the repaired ground.",
        ("EFW_S1E08_S06", 4): "Panel 4 — Kyn: 'I keep wanting more than that.' Afterlight looks at Kyn, then at her own tired hands. Kyn follows the gaze and their shoulders settle into the same exhausted posture.",
        ("EFW_S1E08_S07", 3): "Panel 3 — Arbiter: 'You disagree.' Rae: 'I disagree with calling it mercy.' Ancient Rae and Arbiter stand close over the same marked ruling sheet, both hands sharing the edge of the table instead of facing off across the room.",
        ("EFW_S1E08_S07", 4): "Panel 4 — Arbiter: 'What would you call it?' Ancient Rae looks down at the ruling before answering. In the present layer of the matched composition, Theo watches Rae's remembered face and grips the same table edge.",
        ("EFW_S1E08_S08", 1): "Panel 1 — After the council, Mero and ancient Adrian remain alone in a plain room with two chairs, a table and an open doorway. No machine, schematic, controls or glowing apparatus is visible anywhere in the room.",
        ("EFW_S1E08_S11", 1): "Panel 1 — The scar chamber remains exactly as it was: overlapped masonry, split floor and imperfect seams. Theo, Rae and Adrian stand apart while ordinary human voices and footsteps continue outside the open doorway; nothing flashes or resets.",
        ("EFW_S1E08_S12", 2): "Panel 2 — Theo points through the observation window: 'Were those always gone?' A familiar star cluster has a clean dark gap where several stars should be; render it as ordinary black sky with missing points of light and no glow or distortion.",
        ("EFW_S1E08_S12", 3): "Panel 3 — Rae: 'No.' She steps close to the glass and fixes on the dark gap, face still and certain; Adrian watches Rae instead of the sky."
    }
}

for issue, changes in SOURCE.items():
    apply(SHOW / f"scenes_e{issue:02d}.json", changes)
for issue, changes in OVERLAY.items():
    apply(SHOW / f"enhance_e{issue:02d}.json", changes)

print("Echoes deep chef-layer cleanup applied")
print("Replaced editorial interpretation with visible blocking, acting, props, geography and state changes")
