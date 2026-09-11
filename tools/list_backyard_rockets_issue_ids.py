#!/usr/bin/env python3
import base64, gzip, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/shows/backyard-rockets-s1/encoded'
FILES = [
    'scenes_e03_public_sky.json.gzb64',
    'scenes_e04_trip_point.json.gzb64',
    'scenes_e05_reserve_margin.json.gzb64',
    'scenes_e06_ground_loop.json.gzb64',
    'scenes_e07_ablative_armor.json.gzb64',
    'scenes_e08_sky_piercer.json.gzb64',
]
for name in FILES:
    path = BASE / name
    raw = ''.join(path.read_text(encoding='utf-8').split())
    scenes = json.loads(gzip.decompress(base64.b64decode(raw, validate=True)).decode('utf-8'))
    print(name)
    for i, scene in enumerate(scenes, 1):
        summary = ' '.join(str(scene.get('summary') or '').split())
        if len(summary) > 240:
            summary = summary[:237] + '...'
        print(f"  {i:02d} {scene.get('id')} :: {summary}")
