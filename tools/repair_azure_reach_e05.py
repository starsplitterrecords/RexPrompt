#!/usr/bin/env python3
import base64
import gzip
import json
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data/shows/azure-reach-s1/encoded/pages_e05.json.gzb64"


def decode_b64(text):
    raw = "".join(text.split())
    raw += "=" * (-len(raw) % 4)
    return base64.b64decode(raw, validate=True)


def gzip_payload_start(data):
    if data[:3] != b"\x1f\x8b\x08":
        raise SystemExit("Issue 5 payload is not gzip data")
    flags = data[3]
    pos = 10
    if flags & 0x04:
        xlen = int.from_bytes(data[pos:pos + 2], "little")
        pos += 2 + xlen
    for bit in (0x08, 0x10):
        if flags & bit:
            end = data.index(0, pos)
            pos = end + 1
    if flags & 0x02:
        pos += 2
    return pos


def recover_json_bytes(data):
    start = gzip_payload_start(data)
    dec = zlib.decompressobj(-zlib.MAX_WBITS)
    recovered = dec.decompress(data[start:]) + dec.flush()
    if not dec.eof:
        raise SystemExit("Issue 5 DEFLATE stream is incomplete; cannot repair safely")
    parsed = json.loads(recovered.decode("utf-8"))
    if len(parsed) != 22:
        raise SystemExit(f"Recovered Issue 5 page count is {len(parsed)}, expected 22")
    expected_ids = [f"AZR_S1E05_P{i:02d}" for i in range(1, 23)]
    if [p.get("id") for p in parsed] != expected_ids:
        raise SystemExit("Recovered Issue 5 page IDs are not intact")
    if sum(p.get("panelCount", 0) for p in parsed) != 113:
        raise SystemExit("Recovered Issue 5 panel count is not intact")
    if sum(len(p.get("dialogueInline", [])) for p in parsed) != 160:
        raise SystemExit("Recovered Issue 5 lettering count is not intact")
    text = recovered.decode("utf-8")
    for required in (
        "Fifty thousand verified actions in seven days.",
        "Eighteen thousand four hundred twelve.",
        "The gala deck is tomorrow.",
    ):
        if required not in text:
            raise SystemExit(f"Recovered Issue 5 missing continuity line: {required}")
    return recovered


encoded_text = PATH.read_text(encoding="utf-8")
data = decode_b64(encoded_text)
try:
    gzip.decompress(data)
    print("Azure Reach Issue 5 gzip payload already valid; no repair needed")
except (gzip.BadGzipFile, EOFError):
    recovered = recover_json_bytes(data)
    repaired = gzip.compress(recovered, compresslevel=9, mtime=0)
    normalized = base64.b64encode(repaired).decode("ascii") + "\n"
    PATH.write_text(normalized, encoding="utf-8")
    verify = json.loads(gzip.decompress(base64.b64decode(normalized)).decode("utf-8"))
    assert len(verify) == 22
    print("Azure Reach Issue 5 gzip payload repaired and verified")
