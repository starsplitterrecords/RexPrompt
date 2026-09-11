#!/usr/bin/env python3
import base64
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data" / "shows" / "rex-fleet-s1"


def load_issue(issue: int):
    path = SHOW / "encoded" / f"pages_i{issue:02d}.json.gzb64"
    raw = "".join(path.read_text().split())
    return path, json.loads(gzip.decompress(base64.b64decode(raw)))


def write_issue(path: Path, pages):
    payload = (json.dumps(pages, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    encoded = base64.b64encode(gzip.compress(payload, mtime=0)).decode("ascii")
    path.write_text(encoded + "\n")


def page_map(pages):
    return {page["id"]: page for page in pages}


def require(mapping, page_id):
    if page_id not in mapping:
        raise RuntimeError(f"Missing expected Rex Fleet page {page_id}")
    return mapping[page_id]


issues = {}
for number in (4, 6, 10, 12):
    path, pages = load_issue(number)
    issues[number] = (path, pages, page_map(pages))

# ISSUE 4 — make the dramatic engine performance vs conduct, not lane management.
m = issues[4][2]
p = require(m, "RF_I04_P06")
p["summary"] = "Abby tries to keep civilians outside Shard faction theater while Billie tests whether her authority still means anything and Pike treats the evacuation as an audience."
p["directionInline"] = [
    "Abby has the stolen window schedule pinned to the war table and marks the third civilian slot off-limits with a knife. Billie challenges the word 'nobody' because Abby's authority over her is already fraying; Pike is fastening a broadcast cloak and checking camera drones because he hears 'civilian window' as a stage. The scene is fundamentally about whether either captain still accepts Abby's authority when obedience costs leverage or spectacle. Abby's final answer is directed at Pike's drones rather than his ego."
]
p["panelPlan"] = [
    "Abby pins the stolen window schedule to the gantry table and puts a knife through the third civilian slot.",
    "Billie challenges being included in 'nobody'; hold on Abby registering that the objection is about who still gets to command whom.",
    "Pike fastens his broadcast cloak and checks camera drones while offering to give the Crowns a parade.",
    "Abby answers toward the drones: 'That's what I'm afraid of.' The civilians remain visible below the gantry as the reason for the boundary."
]

p = require(m, "RF_I04_P15")
p["summary"] = "Abby forces Pike to choose between being seen as a hero and doing the unglamorous thing that keeps civilians alive."
p["directionInline"] = [
    "Pike has Broken Oath broadside to the cameras and half inside the route geometry. Abby calls him and waits until he notices the actual civilian track cutting behind him. He admits the performance is deliberate: he is giving the audience something to look at. Abby's order makes the useful action visually humiliating for a showman—turn the glamorous profile away and give the cameras his stern. Let Pike hesitate for one beat before obeying."
]

p = require(m, "RF_I04_P22")
p["summary"] = "Dominion and Selene argue over what a saved civilian means when the saving act was also disobedience, turning one rescue into a fight over the story the institution will tell about itself."
p["directionInline"] = [
    "Dominion and Selene watch the same recovery replay from different screens. Dominion freezes on the instant the escort leaves formation; Selene advances the feed three seconds to the tow line connecting to the refugee tug. Neither disputes the facts. The disagreement is over which fact deserves to define the act. Selene records both while Dominion watches, making the archive itself a quiet contest over institutional memory."
]

p = require(m, "RF_I04_P28")
p["summary"] = "Pike returns ready to perform the rescue for a cheering dock; Abby makes him face the civilians behind the legend, and he chooses to help before he speaks."
p["directionInline"] = [
    "Pike steps off Broken Oath to a cheering dock and instinctively starts to raise both arms. Abby is waiting beside the disabled refugee tug while civilians are still being helped out. She does not rebuke him or praise him; she simply looks from Pike to the people his ship actually saved. Pike sees them, lowers one arm, and uses the other to help a dockhand with the tow line. Keep the cameras present. The choice matters because he knows they are still watching. No speech."
]

p = require(m, "RF_I04_P31")
p["summary"] = "The same rescue becomes five different stories at once: heroism, breach of discipline, successful evacuation, costly protection, and simple survival."

# ISSUE 6 — make the Gate operation the setting for Abby and Tess choosing rebellion.
m = issues[6][2]
p = require(m, "RF_I06_P05")
p["summary"] = "Abby discovers that obeying the Triarch now means starving Shard patients too, forcing her to decide whether loyalty to the institution still deserves loyalty from her captains."

p = require(m, "RF_I06_P06")
p["summary"] = "The Triarch turn the blockade into a loyalty test by ordering Tess to enforce it; Tess refuses before Abby can protect her, and Abby starts counting which captains she can take with them."
p["charactersInline"] = [
    {"name": "Triarch", "handle": "@starsplit.silent.triarch"},
    {"name": "Tessa Banks", "handle": "@starsplit.tessa.banks"},
    {"name": "Abby Saville", "handle": "@starsplit.abby.saville"},
    {"name": "Courier"}
]
p["dialogueInline"] = [
    {"handle": "TRIARCH", "speaker": "Triarch", "text": "Gravefire will enforce the second window.", "subtext": "Panel 2"},
    {"handle": "@starsplit.tessa.banks", "speaker": "Tess", "text": "No.", "subtext": "Panel 2"},
    {"handle": "@starsplit.abby.saville", "speaker": "Abby", "text": "How many of my captains are on the Gate?", "subtext": "Panel 3"},
    {"handle": "COURIER", "speaker": "Courier", "text": "Seven.", "subtext": "Panel 3"},
    {"handle": "@starsplit.abby.saville", "speaker": "Abby", "text": "Good.", "subtext": "Panel 4"}
]
p["directionInline"] = [
    "The Triarch stop arguing policy and order Tess personally to enforce the second civilian interdiction. Tess says 'No' before Abby can answer for her. A courier arrives with the live Gate clock and current picket roster. Abby does not defend Tess with a speech; she looks at the seven captains still carrying her authority and asks how many are on the Gate. Her 'Good' is the instant she decides the argument will become a rebellion."
]
p["panelPlan"] = [
    "In the Arena Vault, the Triarch turn from Abby to Tess and order Gravefire to enforce the second window.",
    "Tess answers 'No.' Hold on Abby: surprise first, then recognition that her sister has made the choice public.",
    "A courier brings the live Gate clock and roster. Abby asks how many of her captains are on the Gate; the answer is seven.",
    "Abby looks at Tess, then at the seven identifiers. 'Good.' The Triarch understand a beat too late what she is counting."
]

p = require(m, "RF_I06_P07")
p["summary"] = "Abby gives Tess one last chance to step away from her treason; Tess makes clear that whatever happens next, her sister will not do it alone."
p["charactersInline"] = [
    {"name": "Abby Saville", "handle": "@starsplit.abby.saville"},
    {"name": "Tessa Banks", "handle": "@starsplit.tessa.banks"}
]
p["dialogueInline"] = [
    {"handle": "@starsplit.abby.saville", "speaker": "Abby", "text": "Tess. You can still walk back in.", "subtext": "Panel 2"},
    {"handle": "@starsplit.tessa.banks", "speaker": "Tess", "text": "So can you.", "subtext": "Panel 3"},
    {"handle": "@starsplit.abby.saville", "speaker": "Abby", "text": "Not anymore.", "subtext": "Panel 3"},
    {"handle": "@starsplit.tessa.banks", "speaker": "Tess", "text": "Good.", "subtext": "Panel 4"}
]
p["directionInline"] = [
    "The Triarch lower their hands behind the sisters to issue the interdiction order. Abby is already walking out, then stops just long enough to give Tess an honest exit from the consequences of what they are doing. Tess returns the choice to Abby. Abby admits the decision has already been made; Tess's 'Good' is quiet, not triumphant. They leave together while the seven captain identifiers remain lit behind them."
]
p["continuityFrom"] = "RF_I06_P06"
p["panelPlan"] = [
    "The Triarch begin the interdiction gesture as Abby and Tess walk away from the chamber.",
    "Abby stops at the threshold and tells Tess she can still walk back in.",
    "Tess says Abby can too. Abby: 'Not anymore.' Let the sisters hold each other's gaze rather than the Triarch's.",
    "Tess: 'Good.' They leave together; the seven captain identifiers remain lit on the wall behind them."
]

p = require(m, "RF_I06_P12")
p["summary"] = "Abby commits treason in ordinary command language, asking seven captains to decide whether their loyalty belongs to the Triarch order or to the civilians in front of them."
p["directionInline"] = [
    "Abby broadcasts directly to the seven captains as their pickets line the second window. Do not stage this as a revolutionary speech. One captain challenges her on an open channel while the civilian convoy approaches behind the tactical overlay. Abby confirms that she heard the Triarch order and leaves her contradictory order standing. The captains have to choose in public, ship by ship."
]

p = require(m, "RF_I06_P13")
p["summary"] = "Abby's rebellion becomes real one ship at a time as seven Shard captains rotate away from the civilians; Billie chooses the break too without pretending she has joined anyone's cause."
p["directionInline"] = [
    "The second convoy reaches the Shard picket line. Make the political split readable through individual ship behavior: the first Abby-aligned captain rotates away, then another, then another, each committing after seeing the previous choice survive. A loyalist begins to close the gap; Ashfang slides across its bow without firing. Billie does not salute Abby or the Fleet. Civilians cross through a corridor created by people refusing the same order for different reasons. Keep the reciprocal-field window itself physically measurable and independent of their politics."
]

p = require(m, "RF_I06_P14")
p["summary"] = "Venn realizes the decisive event was not a battle but seven captains refusing an order without firing, and makes sure the Fleet record cannot erase that fact."
p["directionInline"] = [
    "On Thunderbreak, the second convoy clears and the tactical board settles. Venn's first question is whether anyone fired. When Tactical says no, Venn looks at the seven Shard transponders that opened the line before saying 'Log it.' The record she wants is not simply a successful crossing; it is that the balance changed because people declined to shoot."
]

# ISSUE 10 — let Abby's apparent sacrifice land through her sister, not only the machinery.
m = issues[10][2]
p = require(m, "RF_I10_P23")
p["summary"] = "Abby gets proof of the Triarch sabotage into Venn's record, then spends her last clear transmission making sure Tess has the civilians before Scythe disappears into the furnace bloom."
p["charactersInline"] = [
    {"name": "Abby Saville", "handle": "@starsplit.abby.saville"},
    {"name": "Commodore Ella Venn", "handle": "@starsplit.ella.venn"},
    {"name": "Tessa Banks", "handle": "@starsplit.tessa.banks"}
]
p["dialogueInline"] = [
    {"handle": "@starsplit.abby.saville", "speaker": "Abby", "text": "Venn. Record packet coming.", "subtext": "Panel 2"},
    {"handle": "@starsplit.ella.venn", "speaker": "Venn", "text": "Receiving.", "subtext": "Panel 2"},
    {"handle": "@starsplit.abby.saville", "speaker": "Abby", "text": "Vent locks were Triarch. Deliberate.", "subtext": "Panel 3"},
    {"handle": "@starsplit.abby.saville", "speaker": "Abby", "text": "Tess. Are the skiffs clear?", "subtext": "Panel 3"},
    {"handle": "@starsplit.tessa.banks", "speaker": "Tess", "text": "Last one just crossed.", "subtext": "Panel 4"},
    {"handle": "@starsplit.abby.saville", "speaker": "Abby", "text": "Dock them.", "subtext": "Panel 4"},
    {"handle": "@starsplit.tessa.banks", "speaker": "Tess", "text": "Abby—", "subtext": "Panel 5"},
    {"handle": "@starsplit.abby.saville", "speaker": "Abby", "text": "Dock them.", "subtext": "Panel 5"}
]
p["directionInline"] = [
    "Scythe's transmission is breaking up inside the furnace plume. Abby pushes the sabotage packet to Venn first so the evidence survives whatever happens to her ship. Only then does she open Tess's channel and ask whether the last civilian skiffs are clear. Tess confirms it. Abby gives her sister a practical order instead of a farewell. Tess starts to say Abby's name; Abby repeats 'Dock them,' and static takes the channel. Do not confirm Scythe's destruction."
]
p["panelPlan"] = [
    "Inside Scythe, warning light and furnace glare overwhelm the bridge while Abby forces the sabotage record packet out to Thunderbreak.",
    "Venn confirms receipt; the packet visibly completes before the transmission worsens.",
    "Abby switches to Tess: 'Are the skiffs clear?' Gravefire is already carrying the last civilians away below.",
    "Tess confirms the last skiff crossed. Abby: 'Dock them.'",
    "Tess starts 'Abby—'. Abby repeats 'Dock them.' The signal collapses into static before either sister can turn it into a goodbye."
]

p = require(m, "RF_I10_P26")
p["summary"] = "Tess cannot find Scythe, refuses to let uncertainty become a funeral, and carries out Abby's last order by docking the civilians first."
p["directionInline"] = [
    "On Gravefire, the helm officer keeps searching the furnace haze for Scythe while Tess watches the same blank sector. She answers the factual question—no transponder—and cuts off the invitation to speculate. 'Dock the civilians' is not emotional avoidance in the abstract; it is Abby's last order, which Tess chooses to obey before allowing herself anything else. Keep the unanswered search display visible as Gravefire turns toward the dock."
]

# ISSUE 12 — pay off Venn/Naomi personally, then return to ordinary shared work.
m = issues[12][2]
p = require(m, "RF_I12_P20")
p["summary"] = "As the second Accord convoy forms, Naomi finally gets the answer to the demand she made before Venn's tribunal: Venn came back with something real, and neither woman pretends that resolves everything between them."
p["charactersInline"] = [
    {"name": "Commodore Ella Venn", "handle": "@starsplit.ella.venn"},
    {"name": "Captain Naomi Sol", "handle": "@starsplit.naomi.sol"}
]
p["dialogueInline"] = [
    {"handle": "@starsplit.naomi.sol", "speaker": "Naomi", "text": "You came back.", "subtext": "Panel 2"},
    {"handle": "@starsplit.ella.venn", "speaker": "Venn", "text": "With more than a wish.", "subtext": "Panel 2"},
    {"handle": "@starsplit.naomi.sol", "speaker": "Naomi", "text": "Barely.", "subtext": "Panel 3"},
    {"handle": "@starsplit.ella.venn", "speaker": "Venn", "text": "Your confirmation?", "subtext": "Panel 3"},
    {"handle": "@starsplit.naomi.sol", "speaker": "Naomi", "text": "Sent.", "subtext": "Panel 4"},
    {"handle": "@starsplit.ella.venn", "speaker": "Venn", "text": "Open the next window.", "subtext": "Panel 5"}
]
p["directionInline"] = [
    "The Gate clock reaches the scheduled mark with Verge and Shard confirmations already lit. Naomi appears on Venn's working comm tile, not in a private romantic setting. Her 'You came back' pays off the demand she made before Venn's tribunal. Venn answers with Naomi's own language—'With more than a wish.' Let the intimacy exist in the fact that they both remember. Naomi's 'Barely' prevents easy reconciliation. Venn asks for her confirmation, Naomi has already sent it, and Venn returns to the ordinary command that the whole season has made possible: open the next window."
]
p["panelPlan"] = [
    "Thunderbreak command at the scheduled mark; Verge and Shard confirmations are already lit on the shared Gate board.",
    "Naomi appears on Venn's working comm tile. Naomi: 'You came back.' Venn: 'With more than a wish.' Hold the recognition rather than romanticizing it.",
    "Naomi: 'Barely.' Venn lets that stand, then asks: 'Your confirmation?'",
    "Naomi: 'Sent.' The shared control board shows her mark already present.",
    "Venn turns back to the bridge: 'Open the next window.' The personal beat feeds directly into ordinary work rather than replacing it."
]

p = require(m, "RF_I12_P21")
p["summary"] = "The convoy moves through while Thunderbreak, Sunlash, Gravefire and unrelated traffic resume separate lives around it; the Accord works without becoming the only story left to tell."
p["directionInline"] = [
    "Wide orbit. The second convoy threads the lane while unrelated traffic waits, turns and resumes around it. Sunlash peels away on Verge business, Gravefire carries its own people, Thunderbreak holds the shared perimeter, and independent hulls continue toward destinations the story has not followed. Keep the vessels visibly different in age, mission, refit history and faction origin. No victory tableau, memorial framing or closing narration. The point is not that the system has become the protagonist; it is that these people have made enough room for many different lives and future stories to continue."
]

for issue, (path, pages, _) in issues.items():
    write_issue(path, pages)
    print(f"updated Rex Fleet issue {issue:02d}: {path.relative_to(ROOT)}")
