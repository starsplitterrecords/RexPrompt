#!/usr/bin/env python3
"""Validate RexPrompt approved-draft and released-canon visual state."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DRAFT_MANIFEST = ROOT / "production" / "drafts" / "manifest.json"
RELEASED_LINKS = ROOT / "production" / "released-links.json"
VISUAL_SOURCES = ROOT / "production" / "visual-sources.json"
INDEX = ROOT / "index.html"
VISUALS_JS = ROOT / "visuals.js"

SAFE_PART = re.compile(r"^[a-z0-9._-]+$")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise AssertionError(f"{path.relative_to(ROOT)} is not valid JSON: {exc}") from exc
    assert isinstance(value, dict), f"{path.relative_to(ROOT)} must contain a JSON object"
    return value


def validate_drafts() -> list[str]:
    data = load_json(DRAFT_MANIFEST)
    assert data.get("schemaVersion") == 1, "draft manifest schemaVersion must be 1"
    drafts = data.get("drafts")
    assert isinstance(drafts, dict), "draft manifest drafts must be an object"
    image_paths: set[str] = set()
    errors: list[str] = []

    for key, entry in drafts.items():
        if not isinstance(entry, dict):
            errors.append(f"draft {key!r}: entry must be an object")
            continue
        series_id = entry.get("seriesId")
        issue_id = entry.get("issueId")
        recipe_id = entry.get("recipeId")
        expected_key = f"{series_id}::{issue_id}::{recipe_id}"
        if key != expected_key:
            errors.append(f"draft {key!r}: key does not match {expected_key!r}")
        if entry.get("status") != "approved-production-draft":
            errors.append(f"draft {key!r}: status must be approved-production-draft")
        image = entry.get("image")
        if not isinstance(image, str) or not image:
            errors.append(f"draft {key!r}: image path is required")
            continue
        path = Path(image)
        if path.is_absolute() or ".." in path.parts:
            errors.append(f"draft {key!r}: image path must be repository-relative")
        if path.suffix.lower() not in ALLOWED_EXTENSIONS:
            errors.append(f"draft {key!r}: unsupported image extension {path.suffix!r}")
        expected_prefix = Path("production") / "drafts" / str(series_id).lower() / str(issue_id).lower()
        try:
            path.relative_to(expected_prefix)
        except ValueError:
            errors.append(f"draft {key!r}: image must live under {expected_prefix.as_posix()}/")
        for part in path.parts[2:]:
            stem = Path(part).stem if Path(part).suffix else part
            if not SAFE_PART.fullmatch(stem):
                errors.append(f"draft {key!r}: unsafe path component {part!r}")
        if image in image_paths:
            errors.append(f"draft {key!r}: image path {image!r} is shared by multiple entries")
        image_paths.add(image)
        if not (ROOT / path).is_file():
            errors.append(f"draft {key!r}: image file {image!r} does not exist")
        mime = entry.get("mimeType")
        if mime not in ALLOWED_MIME:
            errors.append(f"draft {key!r}: unsupported mimeType {mime!r}")
        if not isinstance(entry.get("updatedAt"), str) or not entry.get("updatedAt"):
            errors.append(f"draft {key!r}: updatedAt is required")
    return errors


def validate_released_links() -> list[str]:
    data = load_json(RELEASED_LINKS)
    assert data.get("schemaVersion") == 1, "released-links schemaVersion must be 1"
    links = data.get("links")
    assert isinstance(links, dict), "released-links links must be an object"
    errors: list[str] = []

    for key, raw in links.items():
        if len(key.split("::")) != 3 or any(not part for part in key.split("::")):
            errors.append(f"released link {key!r}: key must be <seriesId>::<issueId>::<recipeId>")
        if isinstance(raw, list):
            items = raw
        elif isinstance(raw, dict) and isinstance(raw.get("images"), list):
            items = raw["images"]
        else:
            items = [raw]
        if not items:
            errors.append(f"released link {key!r}: at least one image is required")
        for item in items:
            value = item if isinstance(item, str) else item.get("path") or item.get("image") or item.get("url") if isinstance(item, dict) else None
            if not isinstance(value, str) or not value:
                errors.append(f"released link {key!r}: image path/url is required")
                continue
            if value.startswith("/"):
                if not value.startswith("/images/"):
                    errors.append(f"released link {key!r}: Visions runtime path must begin /images/")
            else:
                parsed = urlparse(value)
                if parsed.scheme != "https" or not parsed.netloc:
                    errors.append(f"released link {key!r}: external canon URL must be HTTPS")
    return errors


def validate_sources() -> list[str]:
    data = load_json(VISUAL_SOURCES)
    assert data.get("schemaVersion") == 1, "visual-sources schemaVersion must be 1"
    errors: list[str] = []
    for field in ("visionsSiteBase", "visionsSeriesRawBase"):
        value = data.get(field)
        parsed = urlparse(value if isinstance(value, str) else "")
        if parsed.scheme != "https" or not parsed.netloc:
            errors.append(f"visual-sources {field} must be an HTTPS URL")
    series = data.get("series")
    if not isinstance(series, dict):
        return errors + ["visual-sources series must be an object"]
    for series_id, entry in series.items():
        if not SAFE_PART.fullmatch(series_id):
            errors.append(f"visual-sources series id {series_id!r} is unsafe")
        if not isinstance(entry, dict) or not isinstance(entry.get("visionsSlug"), str) or not entry.get("visionsSlug"):
            errors.append(f"visual-sources {series_id!r}: visionsSlug is required")
    return errors


def validate_integration() -> list[str]:
    errors: list[str] = []
    if not VISUALS_JS.is_file():
        errors.append("visuals.js is missing")
    index = INDEX.read_text(encoding="utf-8")
    if '<script src="visuals.js"></script>' not in index:
        errors.append("index.html does not load visuals.js")
    return errors


def main() -> int:
    errors: list[str] = []
    for validator in (validate_drafts, validate_released_links, validate_sources, validate_integration):
        try:
            errors.extend(validator())
        except AssertionError as exc:
            errors.append(str(exc))
    if errors:
        print("Visual-state validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    drafts = len(load_json(DRAFT_MANIFEST)["drafts"])
    links = len(load_json(RELEASED_LINKS)["links"])
    print(f"Visual-state validation passed: {drafts} approved draft(s), {links} explicit canon link(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
