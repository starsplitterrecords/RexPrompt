#!/usr/bin/env python3
"""Convert known Vikings 2026 chef-layer abstractions into drawable staging.

Narrow branch-only migration. Preserves IDs, panel counts/order, dialogue and
released Issue 1. Operates only on active Issues 2-5 overlays.
"""
from __future__ import annotations
import base64, copy, gzip, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SHOWS=ROOT/'data/shows.json'
BASE=ROOT/'data/shows/vikings-2026-s1'

SUMMARY={
'VIK_S1I02_P02':'The three Kin enter the one-room studio together and immediately begin making it usable while Gunnar discovers the fire escape before Carrie can finish explaining the placement.',
'VIK_S1I02_P03':'Gunnar tests the pipes and hot-water tap; the household stops at the discovery of reliable hot water while Bjorn asks who controls it.',
'VIK_S1I02_P05':'Carrie reads out the apartment restrictions; Bjorn and Gunnar test each rule against the room, ending with Gunnar focused on the fire escape.',
'VIK_S1I02_P06':'Gunnar and Bjorn test the fire escape and rig a pigeon snare while Astrid and the two male Kin remain together inside the apartment window, helping from the sill; Carrie notices the rope from inside.',
'VIK_S1I02_P07':'The pigeon snare catches one bird; Silas films from outside while Carrie makes Gunnar and Bjorn release it and clear the fire escape.',
'VIK_S1I02_P10':'While Carrie works at the table, Gunnar, Bjorn, Astrid and the two male Kin arrange bedding, food and a clear path through the one-room studio.',
'VIK_S1I02_P12':'Carrie rereads the acknowledgement rules; Gunnar rotates the packet and asks what the mark must prove, and Bjorn agrees to give a truthful mark the city will accept.',
'VIK_S1I02_P15':'Carrie gets confirmation that DTI accepts the witnessed thumbprint and conditional occupancy; the household reacts to having a temporary legal foothold.',
'VIK_S1I02_P16':'Carrie places the brass apartment key in Bjorn’s hand for the first time; he asks what the key allows him to control and she answers in literal tenant terms.',
'VIK_S1I02_P17':'Bjorn challenges the idea of rent as tribute; Carrie lists what the household owes, and Gunnar turns the lease into a simple two-sided ledger of tenant and building obligations.',
'VIK_S1I02_P21':'The radiator clangs hard enough to alarm Astrid and the two male Kin together; Gunnar checks the pipe, the heat steadies, and Bjorn gives modern life an unforced compliment.',
'VIK_S1I02_P23':'At the apartment threshold Carrie tells Bjorn the household may shut the door after she leaves; he closes and locks it with the brass key while the longer-term status remains unresolved.',
'VIK_S1E03_P08':'A subway train roars into the station; Bjorn braces at the unfamiliar machine until Carrie identifies it and the doors open for ordinary commuters.',
'VIK_S1E03_P23':'Carrie gets the housing confirmation stamped and then hands Gunnar the route home instead of leading him back.',
'VIK_S1E02_P03':'Bjorn studies the bank security guard as if he were a warrior guarding a vault, then discovers Gary is an ordinary man helping customers at the ATM.',
'VIK_S1E02_P11':'Bjorn refuses the fifty dollars as charity until Carrie makes clear it is a DTI advance that must be repaid.',
'VIK_S1E02_P14':'Silas films from outside the bank and tells his livestream that Gunnar’s hand-drawn map is evidence of a planned raid; Gunnar spots him through the glass.',
'VIK_S1E02_P16':'Henderson arrives after the silent alarm and tries to understand why the branch is trending while Kevin, Carrie and Bjorn give incompatible explanations.',
'VIK_S1E05_P01':'Carrie enters the Safe Cave with a plan for the day and finds Astrid and the two male Kin already preparing separate errands while Bjorn drinks his usual coffee.',
'VIK_S1E05_P06':'At the coffee cart, Gunnar reads a free newspaper for interest rather than navigation while Bjorn notices that it contains no route information.'
}

ACTIONS={
('VIK_S1I02_P01',5):"Carrie inserts the brass key into the lock and begins opening the apartment herself. Bjorn's gaze drops from the door to the key in her hand and stays there as the lock turns.",
('VIK_S1I02_P02',5):'Astrid and the two male Kin remain clustered together at the main window. Astrid lifts the sash while the two men peer past her at the iron fire escape; Gunnar looks from the stairs to Carrie.',
('VIK_S1I02_P03',1):'Gunnar kneels by the exposed radiator pipe while Astrid and the two male Kin remain together at the kitchenette; Astrid tests the sink tap as the two men watch the water and Gunnar follows the pipe into the wall.',
('VIK_S1I02_P03',3):"Bjorn looks from the running tap to Carrie and asks who commands the water. Carrie leans against the counter and answers him literally, without smiling at the question.",
('VIK_S1I02_P04',1):"The tiny kitchen table is crowded with Carrie's thick DTI packet, temporary badge, cheap pen and the brass key still in her hand. Bjorn sits opposite her; Gunnar and the three Kin remain close enough to follow the exchange.",
('VIK_S1I02_P06',1):'From inside the studio, the open main window frames the old iron fire escape, neighboring brick walls, tar roofs, water towers and ordinary Bushwick skyline. Gunnar is already outside; Astrid and the two male Kin remain together just inside the window.',
('VIK_S1I02_P06',2):'Gunnar tests the fire-escape railing and stair load. At the open window, Astrid and the two male Kin stay together; one of the men feeds rope through the opening while Astrid and the other man hold the coil inside.',
('VIK_S1I02_P06',3):'Pigeons cluster on the neighboring parapet. Gunnar works the small improvised loop outside while Astrid and the two male Kin watch together from the apartment window; one of them points out the birds.',
('VIK_S1I02_P06',4):'Bjorn joins Gunnar on the fire escape and both crouch behind the parapet with complete hunting seriousness. The three Kin remain visible together through the open apartment window behind them.',
('VIK_S1I02_P06',5):'Carrie reaches the apartment window from inside and follows the rope line out to Gunnar and Bjorn. Astrid and the two male Kin stand together beside her at the sill. Gunnar answers without turning.',
('VIK_S1I02_P07',1):'The improvised loop has caught one ordinary city pigeon without gore or injury. Gunnar steadies the bird on the fire escape while Astrid and the two male Kin remain together just inside the open window, watching; Bjorn studies the catch as possible food.',
('VIK_S1I02_P09',4):'Gunnar rotates the form ninety degrees on the table and traces the printed boxes, labels and signature line with one finger.',
('VIK_S1I02_P10',1):'Overhead view of the studio as the household reorganizes it: bedding along one wall, bags and food grouped near the kitchenette, a clear path to the door and fire escape, modern fixtures left intact.',
('VIK_S1I02_P10',3):'Astrid and the two male Kin work side by side at the kitchenette and table: Astrid divides food into neat household portions, one man clears the door path, and the other folds bedding against the wall.',
('VIK_S1I02_P10',4):'Gunnar points to Bjorn’s gear blocking the route to the door. Bjorn starts to object, checks the narrow path himself, then lifts the gear and moves it aside.',
('VIK_S1I02_P15',5):'Carrie immediately circles the review date on the DTI packet. Bjorn looks around the room and closes his hand around the temporary paperwork. Astrid and the two male Kin settle back into the household arrangement together, visibly relieved they can remain tonight.',
('VIK_S1I02_P16',3):'Bjorn holds the brass key up between himself and Carrie, looks around the walls, and asks what the key allows him to control. Carrie points to the door and answers literally.',
('VIK_S1I02_P19',5):'Silas notices the brass key clenched in Bjorn’s hand, lowers his phone a few inches, and looks from the key to the occupied apartment behind him. Bjorn answers without moving toward him.',
('VIK_S1I02_P20',5):'Bjorn points to the earliest sleeping position near the door and settles there for first watch / earliest rising. Carrie gives him one tired look, decides not to argue, and returns to what she was doing.',
('VIK_S1I02_P21',2):'The old radiator CLANGS. Astrid and the two male Kin react together; one man crouches to inspect it while Astrid and the other man stay immediately behind him. Gunnar listens with one hand on the pipe.',
('VIK_S1I02_P24',2):'Astrid and the two male Kin gather together at the radiator. One man tests the steady warmth with his palm while Astrid and the other man look around the cramped room they have finished arranging.',
('VIK_S1E03_P04',5):'Bjorn steps close to the locked turnstile and studies its steel bars with the same grave attention he would give a person blocking passage.',
('VIK_S1E03_P22',5):'The blue pen chained to the desk pulls taut as Bjorn signs. He lifts the pen and chain to eye level; the receptionist points at the desk fitting and answers without looking surprised.',
('VIK_S1E03_P24',5):'They emerge into familiar Bushwick daylight. Gunnar recognizes the same subway globe and street corner from departure and turns toward home before Carrie points the way; Bjorn looks back once at the station entrance.',
('VIK_S1E02_P03',1):'Wide Chase vestibule. Bjorn notices Gary beside the ATM and studies the security uniform, radio and position near the inner doors before looking toward Carrie.',
('VIK_S1E02_P03',2):'Carrie gestures toward Gary helping an ordinary customer at the ATM while Bjorn continues to watch him.',
('VIK_S1E02_P03',3):'Gary looks up from the ATM area and gives Bjorn a casual morning greeting, relaxed and unthreatened.',
('VIK_S1E02_P03',4):'Close insert on Gary shifting his weight off a stiff knee as Bjorn notices the guarded movement and addresses him seriously.',
('VIK_S1E02_P11',1):'At the teller counter, Carrie offers Bjorn the fifty-dollar DTI advance. He leaves the bills on the counter and pulls his hand back.',
('VIK_S1E02_P11',2):'Carrie pushes the bills back toward Bjorn and taps the DTI paperwork that records the advance.',
('VIK_S1E02_P11',3):'Bjorn looks from the money to the paperwork and asks what repayment is owed, still refusing to pick the bills up.',
('VIK_S1E02_P11',4):'Carrie points to the printed fifty-dollar amount and answers deadpan. Bjorn finally takes the bills without gratitude or embarrassment.',
('VIK_S1E02_P14',1):'Across the sidewalk from the bank, Silas holds his phone upright in livestream mode with the bank entrance and Vikings visible behind him.',
('VIK_S1E02_P14',2):'Silas zooms his phone toward Gunnar’s hand-drawn map visible through the bank glass and points at it for his viewers.',
('VIK_S1E02_P14',3):'Inside the bank, Gunnar looks up from the map and fixes his gaze through the window directly on Silas across the street.',
('VIK_S1E02_P14',4):'Carrie sees Gunnar looking toward the door, steps into his path and holds one palm toward his chest while Silas remains visible outside with the phone raised.',
('VIK_S1E02_P16',1):'Henderson arrives at the manager desk holding a phone that shows the branch appearing in a social-media feed; he looks from the screen to the group.',
('VIK_S1E02_P16',2):'Kevin stands beside the teller area and indicates the Viking silver on the counter while Henderson listens.',
('VIK_S1E02_P16',3):'Carrie immediately holds up the DTI identification and paperwork between Henderson and the silver.',
('VIK_S1E02_P16',4):'Bjorn points toward the teller station as he describes the refused tribute; Henderson stares at him for one dry beat.',
('VIK_S1E05_P12',4):'The librarian gives the book and its call label one brief glance, gestures toward the feedback desk, and keeps walking. Bjorn watches her continue down the aisle without stopping.'
}

LOCATIONS={
('VIK_S1I02_P03',5):'Bushwick studio kitchenette beside the sink and radiator',
('VIK_S1I02_P06',1):'studio interior at the open main window, looking onto the fire escape',
('VIK_S1I02_P06',2):'fire escape immediately outside the studio window; three Kin remain inside at the sill',
('VIK_S1I02_P06',3):'studio window and fire escape with neighboring parapet visible',
('VIK_S1I02_P06',4):'fire escape immediately outside the studio window',
('VIK_S1I02_P06',5):'studio window / fire-escape threshold',
('VIK_S1I02_P10',1):'Bushwick studio, full-room overhead',
('VIK_S1I02_P10',2):'Bushwick studio sleeping area beside the radiator',
('VIK_S1I02_P10',3):'Bushwick studio kitchenette, table and door path',
('VIK_S1I02_P10',4):'Bushwick studio path between sleeping area and entry door',
('VIK_S1I02_P10',5):'Bushwick studio, viewed from Carrie’s kitchen-table position',
('VIK_S1I02_P15',5):'Bushwick studio around the kitchen table',
('VIK_S1E03_P23',1):'DTI service counter',
('VIK_S1E03_P23',2):'DTI service counter',
('VIK_S1E03_P23',3):'DTI service counter',
('VIK_S1E03_P23',4):'DTI service counter and receptionist desk',
('VIK_S1E03_P23',5):'DTI service counter and receptionist desk',
('VIK_S1E03_P23',6):'DTI service counter / departure side',
('VIK_S1E05_P03',2):'recurring bodega counter',
('VIK_S1E05_P03',3):'recurring bodega counter',
('VIK_S1E05_P03',4):'recurring bodega counter',
('VIK_S1E05_P03',5):'recurring bodega counter'
}


def load(path, enc):
    if enc=='gzip-base64':
        b64=''.join(path.read_text(encoding='utf-8').split())
        return json.loads(gzip.decompress(base64.b64decode(b64)).decode('utf-8'))
    return json.loads(path.read_text(encoding='utf-8'))

def save(path, enc, raw):
    text=json.dumps(raw,ensure_ascii=False,indent=2)+'\n'
    if enc=='gzip-base64':
        packed=gzip.compress(text.encode('utf-8'),mtime=0)
        path.write_text(base64.b64encode(packed).decode('ascii')+'\n',encoding='utf-8')
    else:
        path.write_text(text,encoding='utf-8')

def pages(raw):
    if isinstance(raw,list): return raw
    if isinstance(raw,dict) and isinstance(raw.get('pages'),list): return raw['pages']
    if isinstance(raw,dict): return [dict({'id':k},**v) for k,v in raw.items()]
    return []

def snapshot(rows):
    return {p.get('id'):{'count':len(p.get('panelPlan') or []),'nums':[x.get('panel') for x in p.get('panelPlan') or []],'dialogue':copy.deepcopy(p.get('dialogueInline'))} for p in rows if p.get('id')}

shows=json.loads(SHOWS.read_text(encoding='utf-8'))
touched=pages_changed=fields=0
for show in shows:
    sid=str(show.get('id') or '')
    if sid not in {'vikings-2026-s1-e02','vikings-2026-s1-e03','vikings-2026-s1-e04','vikings-2026-s1-e05'}: continue
    for ov in show.get('sceneOverlays') or []:
        path=BASE/ov['file']; enc=ov.get('encoding'); raw=load(path,enc); rows=pages(raw); before=snapshot(rows); changed=False
        for p in rows:
            pid=str(p.get('id') or '')
            page_changed=False
            if pid in SUMMARY and p.get('summary')!=SUMMARY[pid]:
                p['summary']=SUMMARY[pid]; fields+=1; page_changed=True
            for panel in p.get('panelPlan') or []:
                if not isinstance(panel,dict): continue
                n=panel.get('panel'); key=(pid,n)
                if key in ACTIONS and panel.get('action')!=ACTIONS[key]:
                    panel['action']=ACTIONS[key]; fields+=1; page_changed=True
                if key in LOCATIONS and panel.get('location')!=LOCATIONS[key]:
                    panel['location']=LOCATIONS[key]; fields+=1; page_changed=True
            if page_changed:
                pages_changed+=1; changed=True
        after=snapshot(rows)
        if set(before)!=set(after): raise AssertionError(f'page IDs changed in {path}')
        for pid,state in before.items():
            if after[pid]['count']!=state['count'] or after[pid]['nums']!=state['nums']: raise AssertionError(f'panel structure changed {pid}')
            if after[pid]['dialogue']!=state['dialogue']: raise AssertionError(f'dialogue changed {pid}')
        if changed:
            save(path,enc,raw); touched+=1

# Keep the human-readable Issue 5 source aligned with the production shelf.
source=BASE/'issue_05_skaldic_interface_enhanced.md'
text=source.read_text(encoding='utf-8')
anchor='Do not explain the Kin payoff yet. Seed it visually. Do not turn recurring civilians into sitcom sidekicks. Keep recognition casual and earned.\n'
insert=(anchor+'\nKin continuity for this issue: The Kin are exactly three recurring people—Astrid and two men whose names remain unresolved. Issue 5 is where the audience begins seeing them as separate people around the neighborhood. Name Astrid when the established woman is individually visible; do not invent names for the two men and do not add additional Kin.\n')
if anchor in text and 'Kin continuity for this issue:' not in text:
    text=text.replace(anchor,insert)
text=text.replace('the woman from the Kin','Astrid').replace('The woman from the Kin','Astrid')
source.write_text(text,encoding='utf-8')
print(f'Patched {fields} recipe fields across {pages_changed} pages in {touched} active overlay files.')
