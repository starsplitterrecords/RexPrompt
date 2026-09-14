#!/usr/bin/env python3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/'data/shows/vikings-2026-s1'
REPL={
'pages_i06_p01_p06.json':[
("The participant keeps steady eye contact. Bjorn's certainty drops from his face; after a beat he answers the literal wording.","The participant keeps steady eye contact. Bjorn’s eyes widen slightly and his jaw relaxes; after a beat he answers the literal wording.")
],
'pages_i06_p07_p12.json':[
('The facilitator answers from the same kind of chair as everyone else, relaxed and unceremonial.','The facilitator answers from the same kind of chair as everyone else, leaning back with hands loose on their lap.'),
("Bjorn's attention sharpens and he answers before the participant asks for anything.","Bjorn sits forward with brows drawn and answers immediately after the participant’s line."),
('The participant stiffens as Bjorn states what he thinks they are afraid of.','The participant’s shoulders rise and their elbows pull inward as Bjorn says, “You fear saying so…”'),
('The facilitator raises one hand from their chair and cuts Bjorn off without standing over him.','The facilitator remains seated and raises one hand toward Bjorn as they say, “Stop.”')
],
'pages_i06_p19_p24.json':[
("Gunnar reads at the table. First Male Kin repairs a bag. Second Male Kin enters carrying a small purchase; Bjorn's eyes follow him with brief surprise. Astrid is not present.","Gunnar reads at the table. First Male Kin repairs a bag. Second Male Kin enters carrying a small purchase; Bjorn’s eyes widen briefly and track him across the room. Astrid is not present."),
("Gunnar notices Bjorn's repeated glance and looks up from his book.","Gunnar catches Bjorn looking toward the empty doorway and looks up from his book."),
('Gunnar compares two library books. First Male Kin wrestles with a stubborn clamp on a small repair. Second Male Kin sorts groceries. Bjorn enters, notices all three tasks, and stops near the door without reaching for any tool or bag.','Gunnar compares two library books. First Male Kin wrestles with a stubborn clamp on a small repair. Second Male Kin sorts groceries. Bjorn enters; his eyes move from the books to the clamp to the groceries, then he stops near the door with both hands empty.')
]
}
for fn,reps in REPL.items():
    p=ROOT/fn; text=p.read_text()
    for old,new in reps:
        if old not in text: raise SystemExit(f'missing in {fn}: {old[:100]}')
        text=text.replace(old,new)
    p.write_text(text)
print('applied final Issue 6 artist-readability fixes')
