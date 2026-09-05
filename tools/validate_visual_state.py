#!/usr/bin/env python3
"""Validate RexPrompt approved-draft, released-canon, and curated visual-reference state."""

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
REFERENCE_TYPES = {"released-canon", "approved-current-production-reference"}


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
            continue
        reference_pack = entry.get("referencePack")
        if reference_pack is not None:
            if not isinstance(reference_pack, str) or not reference_pack:
                errors.append(f"visual-sources {series_id!r}: referencePack must be a repository-relative path")
            else:
                path = Path(reference_pack)
                expected_prefix = Path("production") / "references" / series_id
                if path.is_absolute() or ".." in path.parts:
                    errors.append(f"visual-sources {series_id!r}: referencePack must be repository-relative")
                else:
                    try:
                        path.relative_to(expected_prefix)
                    except ValueError:
                        errors.append(f"visual-sources {series_id!r}: referencePack must live under {expected_prefix.as_posix()}/")
                    if not (ROOT / path).is_file():
                        errors.append(f"visual-sources {series_id!r}: referencePack file {reference_pack!r} does not exist")
    return errors


def validate_reference_packs() -> list[str]:
    sources = load_json(VISUAL_SOURCES).get("series", {})
    errors: list[str] = []

    for series_id, source in sources.items():
        if not isinstance(source, dict) or not source.get("referencePack"):
            continue
        pack_path = ROOT / source["referencePack"]
        if not pack_path.is_file():
            continue
        try:
            pack = load_json(pack_path)
        except AssertionError as exc:
            errors.append(str(exc))
            continue
        label = str(pack_path.relative_to(ROOT))
        if pack.get("schemaVersion") != 1:
            errors.append(f"{label}: schemaVersion must be 1")
        if pack.get("seriesId") != series_id:
            errors.append(f"{label}: seriesId must be {series_id!r}")
        refs = pack.get("references")
        if not isinstance(refs, list) or not refs:
            errors.append(f"{label}: references must be a non-empty list")
            continue

        ids: set[str] = set()
        for ref in refs:
            if not isinstance(ref, dict):
                errors.append(f"{label}: every reference must be an object")
                continue
            ref_id = ref.get("id")
            if not isinstance(ref_id, str) or not ref_id:
                errors.append(f"{label}: reference id is required")
                continue
            if ref_id in ids:
                errors.append(f"{label}: duplicate reference id {ref_id!r}")
            ids.add(ref_id)
            ref_type = ref.get("type")
            if ref_type not in REFERENCE_TYPES:
                errors.append(f"{label}: reference {ref_id!r} has unsupported type {ref_type!r}")
            image = ref.get("image")
            if not isinstance(image, str) or not image:
                errors.append(f"{label}: reference {ref_id!r} image is required")
                continue
            if ref_type == "released-canon":
                if not image.startswith("/images/"):
                    errors.append(f"{label}: released reference {ref_id!r} must use a Visions /images/ runtime path")
            elif ref_type == "approved-current-production-reference":
                path = Path(image)
                expected_prefix = Path("production") / "references" / series_id
                if path.is_absolute() or ".." in path.parts:
                    errors.append(f"{label}: approved reference {ref_id!r} must be repository-relative")
                else:
                    try:
                        path.relative_to(expected_prefix)
                    except ValueError:
                        errors.append(f"{label}: approved reference {ref_id!r} must live under {expected_prefix.as_posix()}/")
                    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
                        errors.append(f"{label}: approved reference {ref_id!r} has unsupported image extension")
                    if not (ROOT / path).is_file():
                        errors.append(f"{label}: approved reference image {image!r} does not exist")

        for field in ("characterReferenceOrder", "settingReferenceOrder"):
            mapping = pack.get(field, {})
            if mapping is None:
                continue
            if not isinstance(mapping, dict):
                errors.append(f"{label}: {field} must be an object")
                continue
            for key, order in mapping.items():
                if not isinstance(order, list) or not order:
                    errors.append(f"{label}: {field} {key!r} must contain a non-empty reference-id list")
                    continue
                for ref_id in order:
                    if ref_id not in ids:
                        errors.append(f"{label}: {field} {key!r} references unknown id {ref_id!r}")

        page_order = pack.get("pageLanguageReferenceOrder", [])
        if not isinstance(page_order, list):
            errors.append(f"{label}: pageLanguageReferenceOrder must be a list")
        else:
            for ref_id in page_order:
                if ref_id not in ids:
                    errors.append(f"{label}: pageLanguageReferenceOrder references unknown id {ref_id!r}")
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
    for validator in (validate_drafts, validate_released_links, validate_sources, validate_reference_packs, validate_integration):
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
    packs = sum(1 for entry in load_json(VISUAL_SOURCES).get("series", {}).values() if isinstance(entry, dict) and entry.get("referencePack"))
    print(f"Visual-state validation passed: {drafts} approved draft(s), {links} explicit canon link(s), {packs} curated reference pack(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
