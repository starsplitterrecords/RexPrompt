#!/usr/bin/env python3
import base64, gzip, io, json, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REL = 'data/shows/backyard-rockets-s1/encoded/scenes_e07_ablative_armor.json.gzb64'
PATH = ROOT / REL

EDITS = {
    'BR_S1E07_A01_SC01': {
        'Then we stop pretending material availability is a design constant.': 'Then design around what we can actually buy.',
    },
    'BR_S1E07_A01_SC02': {
        "Decommissioned furnace, documented waste stream, controlled exposure. We are not turning somebody else's workplace into our supply cabinet.": 'Decommissioned furnace. Documented waste stream. No live process. Fine.',
    },
    'BR_S1E07_A01_SC03': {
        'If the tile cannot pass the gauge, it does not fly. I do not care who made it.': "Doesn't pass the gauge, it goes in the reject bin. I don't care whose initials are on it.",
    },
    'BR_S1E07_A01_SC04': {
        'The rocket is an output now, not the organization.': 'Stop counting rockets. Count workshops, freight and approvals.',
        'Find the people coordinating material and authority. Use evidence.': 'Bring me evidence, not a map full of guesses.',
    },
    'BR_S1E07_A01_SC05': {
        'I do. I am not volunteering to be careless. I am also not volunteering to become a ghost.': "I know. I'm not going to be stupid. I'm also not disappearing because they noticed me.",
    },
    'BR_S1E07_A02_SC03': {
        'They stopped the test.': 'Keep the abort in.',
        'If you remove that, you are not documenting a hazard. You are manufacturing one.': 'Cut it and Dryline puts it back by lunch.',
    },
    'BR_S1E07_A03_SC01': {
        'One warrant. One person. No theater.': "One warrant. One person. Don't turn a pickup into a sweep.",
        'If the settlement is not named in the order, leave it alone.': "If it's not in the order, don't touch it.",
    },
    'BR_S1E07_A03_SC03': {
        'The board is closed. Nobody touches the pumps because of me.': "Board's closed. Pump authority is transferred.",
    },
    'BR_S1E07_A03_SC04': {
        'I can stop that convoy here.': 'I can stop it here.',
        'And make every house below it part of the fight. No.': 'Not with those houses behind it.',
    },
}

text = subprocess.check_output(['git', 'show', f'origin/main:{REL}'], cwd=ROOT, text=True)
raw = base64.b64decode(''.join(text.split()))
scenes = json.loads(gzip.decompress(raw).decode('utf-8'))
replaced = 0
for scene in scenes:
    mapping = EDITS.get(scene.get('id'), {})
    for line in scene.get('dialogueInline', []):
        old = line.get('text')
        if old in mapping:
            line['text'] = mapping[old]
            replaced += 1
if replaced != 13:
    raise SystemExit(f'Expected 13 Issue 7 dialogue replacements, got {replaced}')
data = (json.dumps(scenes, indent=2, ensure_ascii=False) + '\n').encode('utf-8')
buf = io.BytesIO()
with gzip.GzipFile(fileobj=buf, mode='wb', compresslevel=9, mtime=0) as z:
    z.write(data)
PATH.write_text(base64.b64encode(buf.getvalue()).decode('ascii'), encoding='utf-8')
print('Rebuilt Issue 7 with 13 dialogue replacements')
