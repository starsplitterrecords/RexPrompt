#!/usr/bin/env python3
import base64, gzip, json, re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
shows = json.loads((ROOT / 'data/shows.json').read_text())
show = next(s for s in shows if s.get('id') == 'backyard-rockets-s1')
base = ROOT / show['basePath']


def norm(raw):
    if isinstance(raw, list):
        return raw
    return [
        {'id': k, **v} if isinstance(v, dict) else {'id': k, 'value': v}
        for k, v in (raw or {}).items()
    ]


def read_overlay(path, encoding=None):
    if encoding == 'gzip-base64':
        b64 = ''.join(path.read_text().split())
        return json.loads(gzip.decompress(base64.b64decode(b64, validate=True)).decode())
    return json.loads(path.read_text())


def episode(scene):
    if scene.get('episode'):
        return scene['episode']
    match = re.search(r'S1E\d{2}', scene.get('id', '') or '')
    return match.group(0) if match else 'UNKNOWN'


def has_text(value):
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return any(has_text(v) for v in value)
    if isinstance(value, dict):
        return any(has_text(v) for v in value.values())
    return False


def panel_count(scene):
    for key in ('panelPlan', 'panelsInline', 'panels'):
        value = scene.get(key)
        if isinstance(value, list):
            return len(value)
    return 0


def dialogue_count(scene):
    value = scene.get('dialogueInline') or scene.get('dialogue') or []
    return len(value) if isinstance(value, list) else 0


def field_present(scene, field):
    if field == 'setting':
        return bool(str(scene.get('setting') or scene.get('settingText') or '').strip())
    if field == 'panelPlan':
        return panel_count(scene) > 0
    if field == 'dialogueInline':
        return dialogue_count(scene) > 0
    return has_text(scene.get(field))


groups = []
base_file = show.get('scenesFile', 'scenes_base.json')
groups.append({
    'file': base_file,
    'encoding': None,
    'scenes': norm(json.loads((base / base_file).read_text())),
})
for overlay in show.get('sceneOverlays', []):
    raw = read_overlay(base / overlay['file'], overlay.get('encoding'))
    excluded = set(overlay.get('excludeIds', []))
    scenes = [s for s in norm(raw) if s.get('id') not in excluded]
    groups.append({
        'file': overlay['file'],
        'encoding': overlay.get('encoding'),
        'scenes': scenes,
    })

all_scenes = [scene for group in groups for scene in group['scenes']]
quality_fields = (
    'summary',
    'directionInline',
    'dialogueInline',
    'panelPlan',
    'continuityFrom',
    'setting',
)
quality = {}
for ep in sorted(set(episode(scene) for scene in all_scenes)):
    scenes = [scene for scene in all_scenes if episode(scene) == ep]
    panels = [panel_count(scene) for scene in scenes]
    dialogue = [dialogue_count(scene) for scene in scenes]
    coverage = {
        field: sum(1 for scene in scenes if field_present(scene, field))
        for field in quality_fields
    }
    sparse = []
    for scene in scenes:
        reasons = []
        if panel_count(scene) < 4:
            reasons.append(f'panels={panel_count(scene)}')
        if dialogue_count(scene) < 3:
            reasons.append(f'dialogue={dialogue_count(scene)}')
        if not field_present(scene, 'directionInline'):
            reasons.append('no-direction')
        if not field_present(scene, 'setting'):
            reasons.append('no-setting')
        if reasons:
            sparse.append({'id': scene.get('id'), 'reasons': reasons})
    quality[ep] = {
        'sceneCount': len(scenes),
        'fieldCoverage': coverage,
        'panelCount': {
            'min': min(panels) if panels else 0,
            'max': max(panels) if panels else 0,
            'total': sum(panels),
            'scenesWithFourOrMore': sum(1 for count in panels if count >= 4),
        },
        'dialogueCount': {
            'min': min(dialogue) if dialogue else 0,
            'max': max(dialogue) if dialogue else 0,
            'total': sum(dialogue),
            'scenesWithThreeOrMore': sum(1 for count in dialogue if count >= 3),
        },
        'sparseScenes': sparse,
    }

payload = {
    'groups': groups,
    'quality': quality,
    'sceneCount': len(all_scenes),
    'episodeCounts': dict(sorted(Counter(episode(scene) for scene in all_scenes).items())),
}
(ROOT / 'backyard-rockets-scene-payloads.json').write_text(
    json.dumps(payload, indent=2, ensure_ascii=False)
)
print(len(all_scenes), 'scenes exported from', len(groups), 'source groups')
for ep, stats in quality.items():
    print(
        ep,
        'scenes=', stats['sceneCount'],
        'panelized>=4=', stats['panelCount']['scenesWithFourOrMore'],
        'dialogue>=3=', stats['dialogueCount']['scenesWithThreeOrMore'],
        'sparse=', len(stats['sparseScenes']),
    )
