#!/usr/bin/env python3
"""Vendor staged approved production images into RexPrompt durable draft storage."""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
INTAKE = ROOT / "production" / "drafts" / "intake.json"
MANIFEST = ROOT / "production" / "drafts" / "manifest.json"
MAX_BYTES = 32 * 1024 * 1024
SAFE = re.compile(r"[^a-z0-9._-]+")


@dataclass(frozen=True)
class ImageBlob:
    data: bytes
    extension: str
    mime_type: str


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def slug(value: str) -> str:
    out = SAFE.sub("-", value.strip().lower()).strip("-.")
    if not out or out in {".", ".."}:
        raise ValueError(f"unsafe path component derived from {value!r}")
    return out


def allowed_hosts() -> set[str]:
    raw = os.environ.get("APPROVED_DRAFT_STAGING_HOSTS", "res.cloudinary.com")
    return {host.strip().lower() for host in raw.split(",") if host.strip()}


def assert_allowed_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError("sourceUrl must be an HTTPS URL")
    if parsed.hostname.lower() not in allowed_hosts():
        raise ValueError(f"staging host {parsed.hostname!r} is not allowed")


def detect_image(data: bytes) -> tuple[str, str]:
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png", "image/png"
    if data.startswith(b"\xff\xd8\xff"):
        return ".jpg", "image/jpeg"
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return ".webp", "image/webp"
    raise ValueError("staged asset is not a supported PNG, JPEG, or WebP image")


def fetch_image(url: str) -> ImageBlob:
    assert_allowed_url(url)
    request = Request(url, headers={"User-Agent": "RexPrompt-approved-draft-ingest/1.0"})
    with urlopen(request, timeout=45) as response:
        final_url = response.geturl()
        assert_allowed_url(final_url)
        declared = response.headers.get("Content-Length")
        if declared and int(declared) > MAX_BYTES:
            raise ValueError("staged image exceeds 32 MiB limit")
        data = response.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("staged image exceeds 32 MiB limit")
    extension, mime_type = detect_image(data)
    return ImageBlob(data=data, extension=extension, mime_type=mime_type)


def normalize_approval(approval_id: str, raw: object) -> dict:
    if not isinstance(raw, dict):
        raise ValueError(f"approval {approval_id!r} must be an object")
    required = ("seriesId", "issueId", "recipeId", "sourceUrl")
    missing = [field for field in required if not isinstance(raw.get(field), str) or not raw.get(field).strip()]
    if missing:
        raise ValueError(f"approval {approval_id!r} missing: {', '.join(missing)}")
    method = raw.get("approvalMethod", "automatic-substantial-pass")
    if method not in {"automatic-substantial-pass", "explicit-user-approval", "manual-replacement"}:
        raise ValueError(f"approval {approval_id!r} has unsupported approvalMethod {method!r}")
    return {
        "seriesId": raw["seriesId"].strip(),
        "issueId": raw["issueId"].strip(),
        "recipeId": raw["recipeId"].strip(),
        "sourceUrl": raw["sourceUrl"].strip(),
        "approvalMethod": method,
        "approvedAt": raw.get("approvedAt"),
        "evaluationSummary": raw.get("evaluationSummary"),
    }


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def main() -> int:
    intake = load_json(INTAKE)
    if intake.get("schemaVersion") != 1 or not isinstance(intake.get("approvals"), dict):
        raise ValueError("production/drafts/intake.json has invalid schema")
    manifest = load_json(MANIFEST)
    if manifest.get("schemaVersion") != 1 or not isinstance(manifest.get("drafts"), dict):
        raise ValueError("production/drafts/manifest.json has invalid schema")

    raw_approvals = intake["approvals"]
    if not raw_approvals:
        print("No staged approved drafts to ingest.")
        return 0

    prepared: list[tuple[str, dict, ImageBlob]] = []
    for approval_id, raw in raw_approvals.items():
        approval = normalize_approval(approval_id, raw)
        blob = fetch_image(approval["sourceUrl"])
        prepared.append((approval_id, approval, blob))

    drafts = manifest["drafts"]
    for approval_id, approval, blob in prepared:
        series_id = approval["seriesId"]
        issue_id = approval["issueId"]
        recipe_id = approval["recipeId"]
        key = f"{series_id}::{issue_id}::{recipe_id}"
        dest = Path("production") / "drafts" / slug(series_id) / slug(issue_id) / f"{slug(recipe_id)}{blob.extension}"
        absolute = ROOT / dest
        absolute.parent.mkdir(parents=True, exist_ok=True)

        previous = drafts.get(key)
        if isinstance(previous, dict):
            previous_path = previous.get("image")
            if isinstance(previous_path, str) and previous_path != dest.as_posix():
                old = ROOT / previous_path
                try:
                    old.relative_to(ROOT / "production" / "drafts")
                except ValueError:
                    old = None
                if old and old.is_file():
                    old.unlink()

        absolute.write_bytes(blob.data)
        entry = {
            "seriesId": series_id,
            "issueId": issue_id,
            "recipeId": recipe_id,
            "status": "approved-production-draft",
            "image": dest.as_posix(),
            "mimeType": blob.mime_type,
            "updatedAt": approval["approvedAt"] if isinstance(approval["approvedAt"], str) and approval["approvedAt"] else iso_now(),
            "approvalMethod": approval["approvalMethod"],
        }
        if isinstance(approval["evaluationSummary"], str) and approval["evaluationSummary"].strip():
            entry["evaluationSummary"] = approval["evaluationSummary"].strip()
        drafts[key] = entry
        del raw_approvals[approval_id]
        print(f"Ingested {key} -> {dest.as_posix()}")

    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    INTAKE.write_text(json.dumps(intake, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"Approved-draft ingest failed: {exc}", file=sys.stderr)
        sys.exit(1)
