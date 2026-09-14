#!/usr/bin/env python3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/'data/shows/vikings-2026-s1'
REPL={
'pages_i06_p01_p06.json':[
('Gunnar hands Bjorn a paper coffee cup instead of a task while the two male Kin continue moving through their morning.','Gunnar hands Bjorn a paper coffee cup. Bjorn accepts it; behind them First Male Kin clears the breakfast area and Second Male Kin settles the laundry bag on his shoulder.'),
("Bjorn stands holding the coffee while everyone else remains occupied behind him. His stillness reads as genuine disorientation, not comic sulking.","Bjorn stands motionless with the coffee held at chest height. Behind him Gunnar turns back to the table while the two male Kin continue their tasks without looking toward Bjorn."),
('Bjorn turns from the window and gestures once toward the ordinary apartment around them rather than performing the speech theatrically.','Bjorn turns from the window and gives one restrained sweep of his hand toward the apartment, his face serious and still.'),
('Astrid is not visible. The shock comes from Bjorn choosing violence after the electrical danger is already over; do not make the spark or wall impact into an action spectacle.','Astrid is not visible. The electrical fault is one brief minor spark; by Panel 5 the smoke has stopped. The wall strike cracks the plastic casing once, with the household reaction carrying the impact.'),
("The participant answers with controlled anger rather than melodrama.","The participant's mouth tightens; they square their shoulders and hold Bjorn's gaze."),
("The participant holds Bjorn's gaze. Bjorn realizes his ranking system has failed but still argues the literal wording.","The participant keeps steady eye contact. Bjorn's certainty drops from his face; after a beat he answers the literal wording."),
],
'pages_i06_p07_p12.json':[
('Bjorn leans slightly forward, genuinely testing the structure rather than mocking it.','Bjorn leans slightly forward, brow narrowed and eyes fixed on the facilitator.'),
('Another participant describes a visibly unstable housing/family situation while keeping their body closed and insisting they can manage.','An unnamed adult participant in ordinary contemporary clothes sits folded inward, arms close to the body, while describing an unstable housing and family situation and insisting they can manage.'),
('{"handle":"@vik.GroupParticipant","text":"It\'s fine. I can handle it."}','{"speaker":"OTHER PARTICIPANT","text":"It\'s fine. I can handle it."}'),
("Bjorn compares the landlord-painted drywall, the rack and the freestanding shelf before giving a narrow opinion. Second Male Kin sets the drill down rather than being ordered to do so.","Bjorn looks from the landlord-painted drywall to the rack and then to the freestanding shelf before pointing at the shelf. Second Male Kin lowers the drill to the floor."),
],
'pages_i06_p13_p18.json':[
('Carrie realizes Bjorn is not there.','Carrie scans the empty window and sleeping side of the studio where Bjorn would normally be, then looks back to Gunnar.'),
('Panel 5 is an exterior cut to Bjorn on the block; do not imply the apartment characters can clearly see him from inside.','Panel 5 is a direct exterior cut to Bjorn on the block.'),
('Bjorn asks about the result the participant wants rather than whether the dinner is good or bad.','Bjorn opens both hands, looks directly at the participant, asks what they want from the dinner, and waits for the answer.'),
('Participants stack cups and chairs. Bjorn folds one chair because everyone is cleaning up, not because he has taken charge.','Participants stack cups and chairs. Bjorn folds one chair and adds it to the same stack while two other participants clean nearby.'),
('The facilitator answers plainly rather than turning the exchange into a lesson.','The facilitator keeps carrying a folded chair toward the wall while answering Bjorn.'),
('Bjorn interrupts carefully with a question instead of a plan.','Bjorn raises one hand slightly and asks his question before Carrie reaches the next complaint.'),
("Carrie stops walking for half a beat because the question is so unlike his old reflex. Bjorn repeats it exactly.","Carrie stops for half a step and turns to look directly at Bjorn. He meets her eye and repeats the question."),
],
'pages_i06_p19_p24.json':[
('Bjorn looks once more across the functioning room, then sits instead of calling anyone over or asking where Astrid is.','Bjorn looks once more across the room, then lowers himself onto a chair near the wall. The doorway remains quiet.'),
('Astrid remains off-page; do not imply danger or disappearance. Show only the two established male Kin.','Astrid is off-page. Only First Male Kin and Second Male Kin appear among the Kin.'),
('The owner indicates one exact lower corner and demonstrates the small lift needed. Bjorn repeats the limit back.','The owner crouches beside one lower corner, points to the exact handhold and measures a two-inch lift with thumb and forefinger. Bjorn nods and repeats the limit back.'),
("Bjorn approaches alone. 1987 Participant waits by the door holding a takeout container, dressed for an ordinary day rather than a session ritual.","Bjorn approaches alone. 1987 Participant waits by the door holding a takeout container, keys and phone visible in the other hand, coat open over ordinary contemporary clothes."),
('A normal silence settles over the group. Bjorn sits with his eyes down and both hands still on his knees rather than studying another participant.','A normal silence settles over the group. Bjorn sits with both hands flat on his knees and his eyes fixed on the floor.'),
("Gunnar reads. The two male Kin continue separate quiet tasks. Astrid enters in the background carrying one ordinary small bag and is greeted without interrogation. Carrie sits at the table with coffee rather than a folder. Bjorn stands near the window.","Gunnar reads. First Male Kin continues a small repair while Second Male Kin sorts groceries. Astrid enters in the background carrying one small bag; First Male Kin gives her a brief nod and Second Male Kin shifts aside to let her pass. Carrie sits at the table with coffee, no folder visible. Bjorn stands near the window."),
]
}
for fn,reps in REPL.items():
    p=ROOT/fn; text=p.read_text()
    for old,new in reps:
        if old not in text: raise SystemExit(f'missing in {fn}: {old[:80]}')
        text=text.replace(old,new)
    p.write_text(text)
print('applied Issue 6 assembled-output audit fixes')
