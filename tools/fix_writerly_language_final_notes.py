#!/usr/bin/env python3
"""One-shot cleanup of the final two page-level writerly notes."""
import base64, gzip, json, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "shows" / "backyard-rockets-s1"
RULES = {
    "Use the strongest successful-ascent image as the only true launch payoff.": "Use the strongest successful-ascent image as the one full launch image.",
    "Move the best existing payoff page from old Issue 2 into Issue 1, where the pilot needs to prove the launch changed something on the ground.": "Move the existing Esperanza result page from old Issue 2 into Issue 1 so the pilot shows the launch changing conditions on the ground.",
}

def walk(obj, counts):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str):
                for old, new in RULES.items():
                    if old in v:
                        counts[old] = counts.get(old, 0) + v.count(old)
                        v = v.replace(old, new)
                obj[k] = v
            else: walk(v, counts)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if isinstance(v, str):
                for old, new in RULES.items():
                    if old in v:
                        counts[old] = counts.get(old, 0) + v.count(old)
                        v = v.replace(old, new)
                obj[i] = v
            else: walk(v, counts)

def main():
    total = {}; changed = []
    for p in BASE.rglob('*'):
        if not p.is_file() or {"source","raw","archive"} & set(p.relative_to(BASE).parts): continue
        original = p.read_text(encoding='utf-8')
        counts = {}
        if p.name.endswith('.json.gzb64'):
            try:
                raw = re.sub(r'\s+','',original).rstrip('='); raw += '='*((4-len(raw)%4)%4)
                obj = json.loads(gzip.decompress(base64.b64decode(raw)).decode('utf-8'))
            except Exception: continue
            walk(obj, counts)
            if counts:
                payload=json.dumps(obj,ensure_ascii=False,separators=(',',':')).encode('utf-8')
                p.write_text(base64.b64encode(gzip.compress(payload,mtime=0)).decode('ascii'),encoding='utf-8')
        elif p.suffix == '.json':
            text=original
            for old,new in RULES.items():
                if old in text:
                    counts[old]=counts.get(old,0)+text.count(old); text=text.replace(old,new)
            if counts:
                json.loads(text); p.write_text(text,encoding='utf-8')
        if counts:
            changed.append(p.relative_to(ROOT).as_posix())
            for k,n in counts.items(): total[k]=total.get(k,0)+n
    print('Changed',len(changed),'files; replacements',sum(total.values()),total)
    if set(total) != set(RULES): raise SystemExit('Expected both final notes to match')
if __name__ == '__main__': main()
