#!/usr/bin/env python3
"""One-time migration: separate Echoes writing rationale from image-facing recipes.

Preserves story summaries, cast, dialogue, settings, ordering, continuity IDs and page counts.
Moves developmental direction upstream and rewrites only chef-visible page construction where
reasoning/meta language had displaced drawable visual instruction.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data" / "shows" / "echoes-forgotten-war-s1"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def by_id(items):
    return {item["id"]: item for item in items}


def set_panel(records, scene_id: str, panel_number: int, text: str) -> None:
    scene = by_id(records)[scene_id]
    plan = scene.get("panelPlan")
    assert isinstance(plan, list) and 1 <= panel_number <= len(plan), (scene_id, panel_number)
    plan[panel_number - 1]["text"] = text


ASSEMBLER_LINE = (
    "One finished full-color portrait comic page for Echoes of a Forgotten War. One assembled RexPrompt recipe equals one page only. "
    "Render only the selected recipe; do not repeat or carry story action, layout, or lettering from another recipe. Do not create a contact sheet, montage, issue summary, cover, multi-page spread, page header, title strip, page number, recipe ID, scene ID, credits, production label, or other annotation unless the assembled recipe explicitly supplies that text as story lettering. "
    "Painterly prestige cosmic science-fiction sequential art with strong subject/background value separation and clear left-to-right panel reading. Present-day spaces are tactile and inhabited: practical clothing, worn paper, civic interiors, transit crowds, work lights, repaired masonry and ordinary objects. Ancient spaces are monumental but physically legible: Vanguard uses organic whites, blues and golds; Concordant uses geometric reds, blacks and silver; human figures remain readable against cosmic scale. "
    "Stage emotion through faces, hands, posture, distance, eyelines, touch, carried objects and visible environmental consequence. When past and present echo, match camera position, body placement and architectural geometry precisely. Archives, corridors, monuments, transit spaces, ancient foundations and the Core-Forge appear as stone, metal, paper, repaired seams and occupied rooms; show interfaces or diagrams only when the selected page explicitly scripts one. "
    "Follow the PANEL PLAN as page architecture, preserve exact recurring character identity and continuity, and letter only the exact DIALOGUE supplied by the recipe. Use varied panel sizes when the page plan supports it, reserve larger panels for reveals or changed physical state, and make the final panel visually distinct and readable. No invented dialogue or captions, no character age/design drift, no generic beige or muddy low-contrast grading, no uncontrolled glow/debris, no generic cyberpunk or medieval-fantasy substitution. Fictional production."
)

SOURCE_PANEL_REWRITES = {
    "EFW_S1E01_S02": {
        5: "Panel 5 — Close on Rae in the foreground as she answers, 'I work nights,' without looking away from Caelum. Over her shoulder, the returning Olyria entry and REDLIN PROTOCOL remain visible at the edge of the screen while Caelum watches Rae instead of the text."
    },
    "EFW_S1E01_S04": {
        3: "Panel 3 — Medium two-shot for 'Look at it.' / 'I don't need to.' / 'Then you know what it is.' Theo points past Adrian toward the Marker; Adrian keeps his chin and eyes fixed on Theo, hands still at his sides, refusing to turn around.",
        6: "Panel 6 — Tight on Theo asking exactly, 'Starbreaker was real?' Cut to Adrian: his jaw tightens, his eyes break from Theo for the first time, and one hand closes on the edge of his coat before he answers."
    },
    "EFW_S1E01_S05": {
        3: "Panel 3 — Close two-shot at the terminal for 'You mean you won't.' / 'No. I mean I can't leave it here.' Rae braces one hand on the console and keeps the copied drive in the other; Caelum blocks the doorway but does not touch her."
    },
    "EFW_S1E01_S07": {
        2: "Panel 2 — Medium two-shot across a narrow archive aisle. Rae stands beside an open cart of recovered papers; Adrian stands beside a sealed physical volume already removed from the shelf. Use 'You're in my archive.' / 'Not this part.' with both measuring the distance to the book and to each other.",
        7: "Panel 7 — Rae asks, 'By whom?' Adrian answers exactly, 'By people who remembered what happened when they stayed.' End on Rae looking from Adrian to the empty numbered shelf slot where the missing history should be, fingertips resting on the recovered volume."
    },
    "EFW_S1E01_S08": {
        4: "Panel 4 — Theo kneels in black spoil beside the partly exposed Marker, breathing hard, one injured hand pressed to the ground. 'I have it.' Adrian remains standing a few steps away. 'And now?' Theo looks toward the approaching patrol lights: 'Now I don't want them to have it.'",
        7: "Panel 7 — The Marker is fully hidden beneath rough black spoil and broken work debris. Theo and Adrian crouch in the foreground while the patrol lights recede down the wrong trench. Theo says, 'You could have helped five minutes ago.' Adrian answers, 'Five minutes ago you were still deciding what it belonged to.'"
    },
    "EFW_S1E01_S10": {
        7: "Panel 7 — Final tight close on Adrian against the dark buried trench, the small preserved site record visible in his hand. He says only, 'A beginning.' Theo's industrial cutter remains low and out of focus in the foreground."
    },
    "EFW_S1E02_S02": {
        4: "Panel 4 — Medium close on Starbreaker turned toward the threatened district, shoulders rigid and one hand clenched against damaged armor. Smoke and evacuation movement remain visible behind him as he says, 'Because if nobody stops it, it keeps spreading.'"
    },
    "EFW_S1E02_S11": {
        2: "Panel 2 — Theo sits forward with both hands open in front of him, staring at the same fingers that touched the Marker. Rae watches from across the table. Theo says, 'He was afraid.' Rae: 'Redlin?' Theo: 'Starbreaker.' His expression shifts from alarm to unsettled recognition."
    },
    "EFW_S1E02_S12": {
        3: "Panel 3 — Rae: 'That's not what he asked.' Adrian: 'I know.' Keep Adrian half-turned toward the exit, one hand on the doorframe, eyes lowered instead of meeting Rae's stare.",
        5: "Panel 5 — Final close on Rae watching Adrian from across the room: 'That's not a no.' Adrian stays silent, face turned away. Hold the physical distance between them and the open doorway behind him."
    },
    "EFW_S1E03_S04": {
        5: "Panel 5 — Close on Atlas under impossible weight, knees bent and shoulders compressed, looking past the strain toward civilians still moving behind him. He says, 'It's the only one I can live with.' End before the structure either holds or fails."
    },
    "EFW_S1E03_S05": {
        3: "Panel 3 — 'You don't even know if the ship can land.' Rae is already helping direct a family through the cleared lane; without turning back she answers, 'Neither do they.' Keep her body oriented toward the evacuees.",
        5: "Panel 5 — Rae: 'Don't do that.' She turns away from Theo and rejoins the workers, taking the arm of an older evacuee and guiding them toward the lane while Theo remains behind her."
    },
    "EFW_S1E04_S02": {
        5: "Panel 5 — Mero: 'So am I. That's why I'm grateful for the easy part.' End in a wide panel with Mero, Atlas and Arbiter standing together at the overlook while an evacuation ship lifts away below them, its light crossing all three faces."
    },
    "EFW_S1E04_S06": {
        4: "Panel 4 — Mero: 'I know.' Atlas immediately turns toward him, steps close and says, 'Don't say it like that.' Civilians remain trapped in the damaged passage behind Atlas, visible between the two men.",
        5: "Panel 5 — Tight on Mero's exhausted human face, soot and sleeplessness visible, with trapped civilians blurred behind his shoulder. He asks, 'How would you like me to say it?'"
    },
    "EFW_S1E05_S01": {
        2: "Panel 2 — Medium three-shot. Theo leans forward toward Adrian: 'No. You don't get to say that and make it true.' Rae stays back against the ancient hull, arms tight across herself, and asks, 'Same people for how long?' Adrian remains seated between their two lines of attack.",
        4: "Panel 4 — Theo: 'Prove it.' Adrian: 'I can't.' Rae: 'Convenient.' Adrian does not rise or gesture; he lets both hands rest open on his knees and takes the accusation without looking away.",
        5: "Panel 5 — Adrian: 'Remember it yourself.' Final wide image holds Theo and Rae on opposite sides of the cramped shelter, ancient black hull plating behind both of them and ordinary cots and relief supplies between them."
    },
    "EFW_S1E05_S02": {
        4: "Panel 4 — Mero turns only slightly: 'Theo.' Ancient Theo, already standing in the correct staff position behind him, answers without surprise, 'Sir.' Keep the exchange in a medium two-shot with the dispatch satchel and papers clearly visible.",
        5: "Panel 5 — Mero: 'Stay close.' Theo automatically shifts half a step with him, tucks the dispatch case under one arm and falls into place at Mero's shoulder without hesitation."
    },
    "EFW_S1E05_S04": {
        1: "Panel 1 — Reproduce the Issue 4 post-decision composition: Arbiter alone at the black Pax-Aeterna table after the others leave, same camera height, same chair placement, same light direction and same cropped empty space at frame right.",
        4: "Panel 4 — Arbiter: 'Did you get all of it?' Rae: 'Yes.' Arbiter: 'Even the part I crossed out?' Insert on Rae's physical ruling sheet: the crossed-out line is visibly present but obscured by heavy ink and angle so its wording cannot be read.",
        5: "Panel 5 — Rae: 'Especially that part.' Arbiter: 'Good.' End in a quiet two-shot with Rae continuing to write beside Arbiter, both seated close at the same table amid used pens, folded papers and the crossed-out ruling."
    },
    "EFW_S1E05_S08": {
        3: "Panel 3 — Theo traces the old letters with one fingertip: 'No. I mean I remember writing it like that.' Match his present hand position to the slant and spacing of the handwriting on the page.",
        5: "Panel 5 — Rae turns the page far enough to reveal her own old signature near the bottom margin and says, 'Mine.' End on both of their hands resting beside the two recognizable handwriting samples on ordinary worn paper."
    }
}

OVERLAY_PANEL_REWRITES = {
    "EFW_S1E06_S01": {
        1: "Panel 1 — Wide museum-floor establishing panel: school visitors clustered around brighter exhibits, a tired attendant at a desk, civic display cases and scuffed public flooring. Theo has stopped alone at one small plain case in the foreground while Rae and Adrian are several steps farther down the gallery."
    },
    "EFW_S1E06_S02": {
        2: "Panel 2 — Afterlight stands in the kitchen doorway with one shoulder against the frame. Flux remains seated at the table beside the cold cup, coat still on, gaze fixed on the closed council-room door. 'They're waiting for you.' / 'They've been waiting for me since breakfast.'"
    },
    "EFW_S1E06_S04": {
        2: "Panel 2 — Medium two-shot across the abandoned council table. Mero leans forward with both palms on scattered papers: 'Tell me which choice survives.' Flux looks from the papers to Mero's face, then folds one sheet closed before answering.",
        5: "Panel 5 — Mero: 'I need something.' Flux: 'You need to choose without pretending the future chose for you.' Flux pushes the folded paper back across the table and leaves Mero standing alone among the empty chairs."
    },
    "EFW_S1E06_S05": {
        3: "Panel 3 — Theo stops on the stairs and points upward toward the museum level: 'Then why does everything call us ancient?' Keep the old lower stone courses and newer upper masonry visible in the same vertical frame.",
        5: "Panel 5 — Adrian stops on a landing where dark ancient stone continues directly into pale modern repair with matching worn stair edges: 'It healed around the wound.' Theo stands one step below him, looking at the continuous masonry instead of Adrian."
    },
    "EFW_S1E06_S06": {
        3: "Panel 3 — Starbreaker closes the distance until he and Flux are nearly face-to-face: 'So pick one.' Flux stays against the balcony rail, hands open and empty: 'That's your job.' Refugees continue moving below them."
    },
    "EFW_S1E06_S08": {
        4: "Panel 4 — Flux stands with the small packed bag in hand at the open doorway: 'Somewhere nobody asks me what happens next.' Afterlight remains beside the table and cold cup: 'That place doesn't exist.' Neither moves toward the other."
    },
    "EFW_S1E06_S09": {
        5: "Panel 5 — Adrian: 'I don't think there is one seam.' End in a wide table shot: Rae has two reused volumes open, Theo holds a repaired document, and behind Adrian an old wall patch disappears into newer masonry with no clean dividing line."
    },
    "EFW_S1E06_S12": {
        6: "Panel 6 — Final reaction on Adrian at the edge of the platform, face suddenly still as he watches the grieving worker. Behind him commuters continue boarding, a departure board changes normally and the station staff keep working."
    },
    "EFW_S1E07_S01": {
        5: "Panel 5 — Theo turns from the distressed woman toward Rae: 'What do we tell her?' Rae keeps one hand lightly on the woman's forearm and answers, 'That she's here now.' The stranger she remembers remains several feet away, unsure whether to approach."
    },
    "EFW_S1E07_S03": {
        4: "Panel 4 — Theo: 'So we lie again?' Rae pivots sharply toward him, one hand still extended between two strangers who have begun arguing over the recovered symbols. Her jaw tightens; Theo stops mid-step."
    },
    "EFW_S1E07_S05": {
        4: "Panel 4 — The woman steps directly in front of the man, close enough that their shared bag and interlocked key ring remain visible between them: 'Then look at me.' He forces his eyes from the recovered symbol back to her face.",
        6: "Panel 6 — Rae: 'Fear isn't a plan.' End tight on the couple still facing each other, hands close but not touching, while Adrian and the city recede soft in the background."
    },
    "EFW_S1E07_S06": {
        3: "Panel 3 — Starbreaker: 'Flux left.' Redlin: 'Maybe because none of you listened.' Redlin points once toward Flux's empty chair; Starbreaker looks there instead of back at Redlin.",
        4: "Panel 4 — Oryon: 'Or because looking became unbearable.' Keep Oryon seated nearest the empty place, eyes on the abandoned cup or papers, shoulders lowered before he looks back to the others."
    },
    "EFW_S1E07_S07": {
        5: "Panel 5 — Rae: 'Stop. Both of you. We contain violence. Not memory.' She immediately turns away from Theo and Adrian, kneels beside one of the people she separated and presses a clean cloth to a cut while volunteers steady the other person nearby."
    },
    "EFW_S1E07_S08": {
        5: "Panel 5 — Theo: 'Put the people there.' Mero looks through the half-open door toward the senior council room, then back at Theo. He reaches for the door handle but pauses before opening it."
    },
    "EFW_S1E07_S09": {
        4: "Panel 4 — Theo: 'Then what was the point?' Behind him, one pair of strangers embraces after recognition while another person steps away from someone reaching toward them. Keep both reactions visible in the same plaza frame."
    },
    "EFW_S1E07_S10": {
        3: "Panel 3 — Arbiter: 'I mean both.' Rae: 'Then say both.' Rae taps the physical list of neighborhood names with the end of her pen; Arbiter looks down at the same page before answering."
    },
    "EFW_S1E07_S12": {
        5: "Panel 5 — Rae: 'And you thought forgetting was kinder.' Adrian: 'I thought it was the only thing we hadn't tried.' End on Adrian leaning against the overlook rail, shoulders rounded, while below them scattered people write memories, argue quietly and try to sleep under temporary lights."
    },
    "EFW_S1E08_S01": {
        5: "Panel 5 — Wide threshold panel. Rae stands centered a step ahead of Theo and Adrian; all three face the same scarred chamber entrance but keep visible distance from one another. Old dark masonry and newer construction meet around the doorway."
    },
    "EFW_S1E08_S02": {
        6: "Panel 6 — Arbiter: 'We have been ending threats for years.' Hold the whole exhausted council in a wide still panel: Kyn seated, Mero standing, Oryon rigid, Arbiter looking down at the table, with no one immediately answering."
    },
    "EFW_S1E08_S05": {
        2: "Panel 2 — Adrian stands on an old worn floor mark facing the central scar: 'I can close it.' Theo steps between Adrian and the scar: 'You mean erase it.' Rae remains off to one side, watching both men claim the center of the room.",
        6: "Panel 6 — Rae steps fully between Theo and Adrian and says, 'Theirs.' End in a medium frontal panel with Rae centered, Theo on one side, Adrian on the other, and the scar chamber pushed into the background."
    },
    "EFW_S1E08_S08": {
        4: "Panel 4 — Mero: 'You watched us use every door you opened to find another battlefield.' Mero gestures toward the open council-room door and then back to himself, keeping himself inside the accusation. Adrian does not move.",
        6: "Panel 6 — Mero: 'Nothing about this belongs to one person. That's why I am asking the one who belonged to none of us.' End on Adrian alone in the foreground between two open doorways leading in opposite directions."
    },
    "EFW_S1E08_S09": {
        2: "Panel 2 — Ancient Mero sits heavily on the bench outside the familiar door: 'If they forgot us, could they become something else?' Junior Theo stands beside him with papers tucked under one arm and answers, 'Maybe,' without looking certain."
    },
    "EFW_S1E08_S11": {
        2: "Panel 2 — Theo looks back at the unchanged scar chamber: 'So what happens now?' Rae is already walking toward the exit and answers over her shoulder, 'People remember what they remember.' Nothing in the room changes around them."
    }
}

OVERLAY_DIRECTIONS = {
    "EFW_S1E06_S05": "Use the stairwell itself as visual evidence: lower courses are ancient dark stone, upper repairs are paler modern masonry, and worn stair edges continue across the transition. Keep Theo and Adrian in medium full-body frames moving downward; no screens or diagrams appear.",
    "EFW_S1E06_S09": "Stage Theo, Rae and Adrian at an ordinary archive table surrounded by reused books, repaired walls and mismatched records. Adrian sits for the first time; Rae and Theo face him from opposite sides. Keep explanations grounded in faces, hands and physical records on the table.",
    "EFW_S1E07_S06": "Keep Flux's established place visibly empty at the table: unused chair and the same abandoned cup or papers from earlier scenes. Frame each speaker with that empty place somewhere in the composition at least once.",
    "EFW_S1E07_S07": "Municipal shelter with cots, blankets, first-aid supplies and volunteers physically separating two arguing people while keeping families together. Rae steps between the conflict, then kneels to help one person; Theo and Adrian continue talking while doing useful work.",
    "EFW_S1E08_S01": "Core-Forge threshold is layered masonry and scarred ancient structure under ordinary modern construction, with no operator console in view. Theo, Rae and Adrian remain the foreground subjects; use doorways and wall seams to frame the three-way confrontation.",
    "EFW_S1E08_S04": "Wide exhausted council composition. Flux's established chair remains empty and clearly identifiable. Show only established participants; Regent is absent from the room and from background silhouettes.",
    "EFW_S1E08_S05": "Central scar chamber is a rough overlap of ancient and modern material: split floor, misaligned wall seams and worn surfaces, with no visible control station. Keep Rae spatially between Theo and Adrian as their positions separate across the chamber.",
    "EFW_S1E08_S10": "Match ancient and present camera positions precisely: Adrian occupies the same floor mark and body angle in both times. Rae's hand physically stops Theo; her body then turns across the composition to stop Adrian. No control interface appears.",
    "EFW_S1E08_S12": "Observation window with Theo, Rae and Adrian small against a normal star field containing one obvious dark absence where a familiar cluster should be. Keep the frame free of alarms, overlays, labels and instruments."
}


def main() -> None:
    assembler_path = SHOW / "assembler.json"
    assembler = load(assembler_path)
    assembler["generationLine"] = ASSEMBLER_LINE
    dump(assembler_path, assembler)

    scenes_by_issue = {}
    for issue in range(1, 9):
        path = SHOW / f"scenes_e{issue:02d}.json"
        scenes = load(path)
        scenes_by_issue[issue] = scenes
        if issue == 1:
            for scene in scenes:
                if "direction" in scene:
                    scene["writingDirection"] = scene.pop("direction")
        else:
            for scene in scenes:
                if "directionInline" in scene:
                    scene["writingNotes"] = scene.pop("directionInline")
        dump(path, scenes)

    for scene_id, panel_map in SOURCE_PANEL_REWRITES.items():
        issue = int(scene_id[7:9])
        records = scenes_by_issue[issue]
        for panel_number, text in panel_map.items():
            set_panel(records, scene_id, panel_number, text)
    for issue in range(1, 6):
        dump(SHOW / f"scenes_e{issue:02d}.json", scenes_by_issue[issue])

    for issue in (6, 7, 8):
        path = SHOW / f"enhance_e{issue:02d}.json"
        overlay = load(path)
        for scene_id, panel_map in OVERLAY_PANEL_REWRITES.items():
            if scene_id.startswith(f"EFW_S1E{issue:02d}_"):
                for panel_number, text in panel_map.items():
                    set_panel(overlay, scene_id, panel_number, text)
        overlay_by_id = by_id(overlay)
        for scene_id, text in OVERLAY_DIRECTIONS.items():
            if scene_id.startswith(f"EFW_S1E{issue:02d}_"):
                overlay_by_id[scene_id]["directionInline"] = [{"text": text}]
        dump(path, overlay)

    print("Echoes chef-layer migration applied")
    print("Source developmental direction moved to writingDirection/writingNotes")
    print("Chef-visible panel reasoning replaced with drawable staging")
    print("Assembler generation contract rewritten as direct visual instruction")


if __name__ == "__main__":
    main()
