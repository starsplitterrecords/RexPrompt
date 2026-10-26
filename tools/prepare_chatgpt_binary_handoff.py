#!/usr/bin/env python3
"""Prepare exact, unmodified PNG/JPEG/WebP bytes for ChatGPT Files→GitHub Git Data handoff.

The resulting Base64 text file can be uploaded using ChatGPT Files Library,
read by functions.exec through tools.files__read, and passed without any
model transcription to tools.mcp__GitHub__create_blob(..., encoding='base64').
This utility does NOT approve or publish artwork or require a GitHub token.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path, help="Existing original image file")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--line-width", type=int, default=10000)
    args = parser.parse_args()
    if args.line_width < 4 or args.line_width % 4:
        parser.error("--line-width must be divisible by four and at least four")
    original = args.image.read_bytes()
    if not (24 <= len(original) <= 50 * 1024 * 1024):
        parser.error("Original file byte count out of approved persistence bounds")
    ext = args.image.suffix.lower()
    if ext == ".png" and original.startswith(b"\x89PNG\r\n\x1a\n"):
        mimetype = "image/png"
    elif ext in (".jpg", ".jpeg") and original.startswith(b"\xff\xd8") and original.endswith(b"\xff\xd9"):
        mimetype = "image/jpeg"
    elif ext == ".webp" and original[:4] == b"RIFF" and original[8:12] == b"WEBP":
        mimetype = "image/webp"
    else:
        parser.error("Image file type does not match its original binary signature")
    sha256 = hashlib.sha256(original).hexdigest()
    git_sha = hashlib.sha1(f"blob {len(original)}\0".encode() + original).hexdigest()
    encoded = base64.b64encode(original).decode("ascii")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    payload = args.output_dir / f"{sha256[:16]}.base64.txt"
    lines = [encoded[i:i + args.line_width] for i in range(0, len(encoded), args.line_width)]
    payload.write_text("\n".join(lines) + "\n", encoding="ascii")
    # Re-read and verify the actual persisted staging text before advertising it.
    if base64.b64decode("".join(payload.read_text(encoding="ascii").split()), validate=True) != original:
        raise RuntimeError("Staging payload failed exact original-byte verification")
    result = {
        "source": str(args.image.resolve()),
        "payload": str(payload.resolve()),
        "mimeType": mimetype,
        "originalBytes": len(original),
        "sha256": sha256,
        "gitBlobSha": git_sha,
        "base64Characters": len(encoded),
        "base64Lines": len(lines),
        "lineWidth": args.line_width,
        "approved": False,
        "note": "Transport preparation only; separate quality and Git commit verification required",
    }
    output = args.output_dir / f"{sha256[:16]}.handoff.json"
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()