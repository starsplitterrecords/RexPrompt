#!/usr/bin/env python3
"""Export phone-readable review PDFs from RexPrompt show packages.

The exporter uses data/shows.json and the same overlay semantics as index.html.
It groups registry entries by package basePath, so one PDF represents one production.
Repeated persistent reference data is printed once in appendices; page/scene summaries,
panel plans, dialogue, direction, and nonstandard unit fields remain in reading order.
"""

from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import html
import json
import os
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import inch
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch as INCH
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data" / "shows.json"
STANDARD_FILES = [
    "blocking.json",
    "characters.json",
    "dialogue.json",
    "direction.json",
    "factions.json",
    "lighting.json",
    "mood.json",
    "negatives.json",
    "regions.json",
    "settings.json",
]
UNIT_KEYS = {
    "id",
    "summary",
    "episode",
    "setting",
    "settingText",
    "region",
    "regionText",
    "factions",
    "characters",
    "charactersInline",
    "panelPlan",
    "dialog",
    "dialogueInline",
    "direction",
    "directionInline",
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_scene_data(path: Path, encoding: str | None = None) -> Any:
    if not encoding:
        return read_json(path)
    if encoding != "gzip-base64":
        raise ValueError(f"Unsupported scene encoding: {encoding}")
    raw = re.sub(r"\s+", "", path.read_text(encoding="utf-8"))
    return json.loads(gzip.decompress(base64.b64decode(raw)).decode("utf-8"))


def normalize_scenes(raw: Any) -> list[dict[str, Any]]:
    if isinstance(raw, list):
        return [dict(x) if isinstance(x, dict) else {"summary": str(x)} for x in raw]
    if isinstance(raw, dict):
        out: list[dict[str, Any]] = []
        for key, value in raw.items():
            if isinstance(value, dict):
                out.append({"id": key, **value})
            else:
                out.append({"id": key, "summary": str(value)})
        return out
    return []


def scene_episode(scene: dict[str, Any]) -> str | None:
    if scene.get("episode"):
        return str(scene["episode"])
    match = re.match(r"^RF_(S1E\d{2})_", str(scene.get("id", "")))
    return match.group(1) if match else None


def apply_overlay(
    scenes: list[dict[str, Any]], incoming: list[dict[str, Any]], overlay: dict[str, Any]
) -> list[dict[str, Any]]:
    targets = overlay.get("replaceEpisodes") or (
        [overlay["replaceEpisode"]] if overlay.get("replaceEpisode") else []
    )
    if targets:
        target_set = set(targets)
        first = next((i for i, s in enumerate(scenes) if scene_episode(s) in target_set), -1)
        if first >= 0:
            insert_at = sum(1 for s in scenes[:first] if scene_episode(s) not in target_set)
            kept = [s for s in scenes if scene_episode(s) not in target_set]
            return kept[:insert_at] + incoming + kept[insert_at:]
    if overlay.get("afterId"):
        after_id = overlay["afterId"]
        pos = next((i for i, s in enumerate(scenes) if s.get("id") == after_id), -1)
        insert_at = pos + 1 if pos >= 0 else len(scenes)
        return scenes[:insert_at] + incoming + scenes[insert_at:]
    return scenes + incoming


def load_entry_units(entry: dict[str, Any]) -> list[dict[str, Any]]:
    base = ROOT / entry.get("basePath", "data")
    scene_files = entry.get("scenesFiles") or [entry.get("scenesFile", "scenes.json")]
    scenes: list[dict[str, Any]] = []
    for filename in scene_files:
        scenes.extend(normalize_scenes(read_scene_data(base / filename)))
    for overlay in entry.get("sceneOverlays", []):
        incoming = normalize_scenes(
            read_scene_data(base / overlay["file"], overlay.get("encoding"))
        )
        excluded = set(overlay.get("excludeIds", []))
        if excluded:
            incoming = [s for s in incoming if s.get("id") not in excluded]
        scenes = apply_overlay(scenes, incoming, overlay)
    return scenes


def load_store(base_path: str) -> dict[str, Any]:
    base = ROOT / base_path
    store: dict[str, Any] = {}
    for filename in STANDARD_FILES:
        path = base / filename
        store[filename] = read_json(path) if path.exists() else {}
    return store


def current_commit() -> str:
    env_sha = os.getenv("GITHUB_SHA")
    if env_sha:
        return env_sha
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return "unknown"


def production_title(base_path: str, entries: list[dict[str, Any]]) -> str:
    names = [str(e.get("name") or e.get("id") or "") for e in entries]
    if len(names) == 1:
        name = names[0]
        name = re.sub(r"\s+[—-]\s+Season\s+\d+.*$", "", name, flags=re.I)
        name = re.sub(r"\s+[—-]\s+Issue\s+\d+.*$", "", name, flags=re.I)
        return name.strip()
    split_names = [re.split(r"\s+[—-]\s+", n, maxsplit=1)[0].strip() for n in names]
    if len(set(split_names)) == 1:
        return split_names[0]
    slug = Path(base_path).name
    slug = re.sub(r"-s\d+$", "", slug)
    return " ".join(word.capitalize() for word in slug.split("-"))


def safe_slug(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def esc(value: Any) -> str:
    text = str(value)
    return html.escape(text).replace("\n", "<br/>")


def human(key: str) -> str:
    key = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", key)
    return key.replace("_", " ").strip().title()


def identity(record: Any, fallback: str = "Reference") -> str:
    if isinstance(record, dict):
        for key in ("name", "handle", "id", "title", "role"):
            if record.get(key):
                return str(record[key])
    if isinstance(record, str) and record.strip():
        return record.strip().splitlines()[0][:80]
    return fallback


def dict_lookup(store: dict[str, Any], filename: str, key: Any) -> Any:
    data = store.get(filename, {})
    if isinstance(data, dict):
        return data.get(key)
    return None


def format_ref_name(store: dict[str, Any], filename: str, key: Any) -> str:
    record = dict_lookup(store, filename, key)
    if isinstance(record, dict):
        return str(record.get("name") or record.get("handle") or record.get("title") or key)
    if isinstance(record, str) and record.strip():
        return record.strip().splitlines()[0][:80]
    return str(key)


def canonical_blob(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def register_fonts() -> tuple[str, str]:
    regular = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    if Path(regular).exists() and Path(bold).exists():
        pdfmetrics.registerFont(TTFont("ReviewSans", regular))
        pdfmetrics.registerFont(TTFont("ReviewSansBold", bold))
        return "ReviewSans", "ReviewSansBold"
    return "Helvetica", "Helvetica-Bold"


REGULAR_FONT, BOLD_FONT = register_fonts()


def make_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle(
            "ReviewTitle",
            parent=base["Title"],
            fontName=BOLD_FONT,
            fontSize=23,
            leading=27,
            spaceAfter=12,
            alignment=TA_CENTER,
        ),
        "subtitle": ParagraphStyle(
            "ReviewSubtitle",
            parent=base["BodyText"],
            fontName=REGULAR_FONT,
            fontSize=9.6,
            leading=13,
            alignment=TA_CENTER,
            textColor="#444444",
            spaceAfter=9,
        ),
        "h1": ParagraphStyle(
            "ReviewH1",
            parent=base["Heading1"],
            fontName=BOLD_FONT,
            fontSize=16,
            leading=20,
            spaceBefore=9,
            spaceAfter=7,
        ),
        "h2": ParagraphStyle(
            "ReviewH2",
            parent=base["Heading2"],
            fontName=BOLD_FONT,
            fontSize=12.7,
            leading=16,
            spaceBefore=9,
            spaceAfter=5,
        ),
        "h3": ParagraphStyle(
            "ReviewH3",
            parent=base["Heading3"],
            fontName=BOLD_FONT,
            fontSize=10.7,
            leading=14,
            spaceBefore=7,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "ReviewBody",
            parent=base["BodyText"],
            fontName=REGULAR_FONT,
            fontSize=9.25,
            leading=12.5,
            spaceAfter=4,
        ),
        "small": ParagraphStyle(
            "ReviewSmall",
            parent=base["BodyText"],
            fontName=REGULAR_FONT,
            fontSize=8.2,
            leading=11,
            textColor="#444444",
            spaceAfter=3,
        ),
        "dialogue": ParagraphStyle(
            "ReviewDialogue",
            parent=base["BodyText"],
            fontName=REGULAR_FONT,
            fontSize=9.25,
            leading=12.5,
            leftIndent=11,
            firstLineIndent=-5,
            spaceAfter=4,
        ),
        "label": ParagraphStyle(
            "ReviewLabel",
            parent=base["BodyText"],
            fontName=BOLD_FONT,
            fontSize=8.4,
            leading=11,
            textColor="#555555",
            spaceBefore=3,
            spaceAfter=2,
        ),
    }
    return styles


STYLES = make_styles()


def add_record(story: list[Any], value: Any, level: int = 0) -> None:
    if value is None or value == "" or value == [] or value == {}:
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if item is None or item == "" or item == [] or item == {}:
                continue
            if isinstance(item, (dict, list)):
                story.append(Paragraph(f"<b>{esc(human(str(key)))}</b>", STYLES["small"]))
                add_record(story, item, level + 1)
            else:
                story.append(
                    Paragraph(f"<b>{esc(human(str(key)))}:</b> {esc(item)}", STYLES["body"])
                )
        return
    if isinstance(value, list):
        for i, item in enumerate(value, 1):
            if isinstance(item, dict):
                label = item.get("panel") or item.get("id") or item.get("name") or f"Item {i}"
                story.append(Paragraph(f"<b>{esc(label)}</b>", STYLES["body"]))
                add_record(story, item, level + 1)
            else:
                story.append(Paragraph(f"• {esc(item)}", STYLES["body"]))
        return
    story.append(Paragraph(esc(value), STYLES["body"]))


def add_key_value(story: list[Any], label: str, value: Any, style: str = "body") -> None:
    if value is None or value == "" or value == [] or value == {}:
        return
    if isinstance(value, (dict, list)):
        story.append(Paragraph(f"<b>{esc(label)}</b>", STYLES["label"]))
        add_record(story, value)
    else:
        story.append(Paragraph(f"<b>{esc(label)}:</b> {esc(value)}", STYLES[style]))


def resolve_dialogue(unit: dict[str, Any], store: dict[str, Any]) -> list[dict[str, Any]]:
    if unit.get("dialogueInline"):
        return [dict(x) if isinstance(x, dict) else {"text": str(x)} for x in unit["dialogueInline"]]
    out: list[dict[str, Any]] = []
    for key in unit.get("dialog", []) or []:
        record = dict_lookup(store, "dialogue.json", key)
        if isinstance(record, dict):
            speaker_id = record.get("speakerId")
            speaker = format_ref_name(store, "characters.json", speaker_id) if speaker_id else "Speaker"
            out.append({"speaker": speaker, **record})
    return out


def resolve_direction(unit: dict[str, Any], store: dict[str, Any]) -> list[Any]:
    if unit.get("directionInline"):
        return list(unit["directionInline"])
    out: list[Any] = []
    for key in unit.get("direction", []) or []:
        record = dict_lookup(store, "direction.json", key)
        if record is not None:
            out.append(record)
    return out


def collect_entry_inline_refs(units: list[dict[str, Any]]) -> tuple[dict[str, str], dict[str, Any]]:
    mapping: dict[str, str] = {}
    records: dict[str, Any] = {}
    counters = defaultdict(int)
    prefixes = {"settingText": "S", "regionText": "R", "charactersInline": "C"}
    for unit in units:
        for key, prefix in prefixes.items():
            value = unit.get(key)
            if not value:
                continue
            values: Iterable[Any] = value if key == "charactersInline" and isinstance(value, list) else [value]
            for item in values:
                blob = canonical_blob(item)
                if blob in mapping:
                    continue
                counters[prefix] += 1
                ref = f"{prefix}{counters[prefix]}"
                mapping[blob] = ref
                records[ref] = item
    return mapping, records


def render_entry_inline_refs(story: list[Any], records: dict[str, Any]) -> None:
    if not records:
        return
    story.append(Paragraph("Entry-specific visual references", STYLES["h2"]))
    story.append(
        Paragraph(
            "Inline setting, region, and character descriptions are collected here once so repeated page recipes do not force the same art reference to be reread.",
            STYLES["small"],
        )
    )
    for ref, record in records.items():
        story.append(Paragraph(f"{esc(ref)} - {esc(identity(record))}", STYLES["h3"]))
        add_record(story, record)


def inline_ref_labels(unit: dict[str, Any], mapping: dict[str, str]) -> list[str]:
    labels: list[str] = []
    for key in ("settingText", "regionText"):
        value = unit.get(key)
        if value:
            ref = mapping.get(canonical_blob(value))
            if ref:
                labels.append(ref)
    value = unit.get("charactersInline")
    if isinstance(value, list):
        for item in value:
            ref = mapping.get(canonical_blob(item))
            if ref:
                labels.append(ref)
    return labels


def render_unit(
    story: list[Any],
    unit: dict[str, Any],
    index: int,
    store: dict[str, Any],
    unit_label: str,
    inline_mapping: dict[str, str],
) -> None:
    unit_id = unit.get("id") or str(index)
    story.append(Paragraph(f"{esc(unit_label.title())} {index}: {esc(unit_id)}", STYLES["h2"]))
    if unit.get("summary"):
        add_key_value(story, "Story beat", unit["summary"])

    refs = inline_ref_labels(unit, inline_mapping)
    if refs:
        add_key_value(story, "Visual refs", ", ".join(refs), "small")

    if unit.get("setting"):
        add_key_value(
            story,
            "Setting",
            format_ref_name(store, "settings.json", unit["setting"]),
            "small",
        )
    if unit.get("region"):
        add_key_value(
            story,
            "Region",
            format_ref_name(store, "regions.json", unit["region"]),
            "small",
        )
    if unit.get("factions"):
        names = [format_ref_name(store, "factions.json", x) for x in unit["factions"]]
        add_key_value(story, "Factions", ", ".join(names), "small")
    if unit.get("characters"):
        names = [format_ref_name(store, "characters.json", x) for x in unit["characters"]]
        add_key_value(story, "Cast", ", ".join(names), "small")
    elif unit.get("charactersInline"):
        names = [identity(x, "Character") for x in unit["charactersInline"]]
        add_key_value(story, "Cast", ", ".join(names), "small")

    if unit.get("panelPlan"):
        story.append(Paragraph("Panel plan / art description", STYLES["h3"]))
        add_record(story, unit["panelPlan"])

    dialogue = resolve_dialogue(unit, store)
    if dialogue:
        story.append(Paragraph("Script / dialogue", STYLES["h3"]))
        for line in dialogue:
            speaker = line.get("handle") or line.get("speaker") or line.get("speakerId") or "Speaker"
            text = line.get("text", "")
            story.append(
                Paragraph(f"<b>{esc(speaker)}</b> — “{esc(text)}”", STYLES["dialogue"])
            )
            if line.get("subtext"):
                story.append(Paragraph(f"<i>Subtext:</i> {esc(line['subtext'])}", STYLES["small"]))

    direction = resolve_direction(unit, store)
    if direction:
        story.append(Paragraph("Direction / staging", STYLES["h3"]))
        add_record(story, direction)

    extras = {k: v for k, v in unit.items() if k not in UNIT_KEYS and v not in (None, "", [], {})}
    if extras:
        story.append(Paragraph("Additional production data", STYLES["h3"]))
        add_record(story, extras)

    story.append(Spacer(1, 0.07 * INCH))


def render_persistent_reference(story: list[Any], store: dict[str, Any]) -> None:
    nonempty = [(filename, store.get(filename)) for filename in STANDARD_FILES if store.get(filename)]
    if not nonempty:
        return
    story.append(PageBreak())
    story.append(Paragraph("Persistent production reference", STYLES["h1"]))
    story.append(
        Paragraph(
            "These records are loaded by RexPrompt as reusable production reference. They appear once here rather than being repeated under every page or scene.",
            STYLES["small"],
        )
    )
    for filename, data in nonempty:
        story.append(Paragraph(human(Path(filename).stem), STYLES["h2"]))
        if isinstance(data, dict):
            for key, record in data.items():
                story.append(Paragraph(f"{esc(key)} - {esc(identity(record, str(key)))}", STYLES["h3"]))
                add_record(story, record)
        else:
            add_record(story, data)


def extra_package_files(base_path: str, entries: list[dict[str, Any]]) -> list[Path]:
    base = ROOT / base_path
    excluded = set(STANDARD_FILES)
    for entry in entries:
        if entry.get("scenesFile"):
            excluded.add(entry["scenesFile"])
        excluded.update(entry.get("scenesFiles", []))
    return sorted(
        p for p in base.glob("*.json") if p.name not in excluded and p.name not in {"pages_base.json", "scenes_base.json"}
    )


def render_extra_package_data(story: list[Any], base_path: str, entries: list[dict[str, Any]]) -> None:
    files = extra_package_files(base_path, entries)
    if not files:
        return
    story.append(PageBreak())
    story.append(Paragraph("Development and planning data", STYLES["h1"]))
    for path in files:
        story.append(Paragraph(human(path.stem), STYLES["h2"]))
        add_record(story, read_json(path))


class InvariantCanvas(canvas.Canvas):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs["invariant"] = 1
        super().__init__(*args, **kwargs)


def page_decor(canvas_obj: canvas.Canvas, doc: SimpleDocTemplate) -> None:
    canvas_obj.saveState()
    canvas_obj.setFont(REGULAR_FONT, 7.2)
    canvas_obj.setFillColorRGB(0.35, 0.35, 0.35)
    canvas_obj.drawString(0.45 * INCH, 0.26 * INCH, "RexPrompt production review")
    canvas_obj.drawRightString(5.55 * INCH, 0.26 * INCH, f"{doc.page}")
    canvas_obj.restoreState()


def build_pdf(
    base_path: str,
    entries: list[dict[str, Any]],
    output_path: Path,
    commit_sha: str,
) -> dict[str, Any]:
    store = load_store(base_path)
    title = production_title(base_path, entries)
    loaded: list[tuple[dict[str, Any], list[dict[str, Any]]]] = [
        (entry, load_entry_units(entry)) for entry in entries
    ]

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=(6 * inch, 9 * inch),
        leftMargin=0.43 * INCH,
        rightMargin=0.43 * INCH,
        topMargin=0.48 * INCH,
        bottomMargin=0.44 * INCH,
        title=f"{title} - RexPrompt Production Review",
        author="Star Splitter Visions / RexPrompt",
        subject=f"Deterministic review export from RexPrompt commit {commit_sha}",
    )
    story: list[Any] = []
    story.append(Spacer(1, 1.05 * INCH))
    story.append(Paragraph(esc(title), STYLES["title"]))
    story.append(Paragraph("RexPrompt Production Review", STYLES["subtitle"]))
    story.append(
        Paragraph(
            f"Source commit: <b>{esc(commit_sha)}</b><br/>Package: <b>{esc(base_path)}</b>",
            STYLES["subtitle"],
        )
    )
    story.append(Spacer(1, 0.25 * INCH))
    story.append(
        Paragraph(
            "Reading export: story beats, page/panel art direction, dialogue, staging, and nonstandard production fields are kept in sequence. Reusable reference dictionaries are moved to one appendix so they are not repeated page after page.",
            STYLES["body"],
        )
    )
    story.append(PageBreak())

    story.append(Paragraph("Production index", STYLES["h1"]))
    total_units = 0
    for entry, units in loaded:
        total_units += len(units)
        label = entry.get("unitLabel", "SCENE").lower()
        story.append(
            Paragraph(
                f"<b>{esc(entry.get('name') or entry.get('id'))}</b><br/>{len(units)} {esc(label)} units",
                STYLES["body"],
            )
        )
    story.append(
        Paragraph(
            f"<b>Total assembled units:</b> {total_units}",
            STYLES["body"],
        )
    )

    for entry, units in loaded:
        story.append(PageBreak())
        story.append(Paragraph(esc(entry.get("name") or entry.get("id")), STYLES["h1"]))
        if entry.get("generationLine"):
            add_key_value(story, "Production line", entry["generationLine"])
        inline_mapping, inline_records = collect_entry_inline_refs(units)
        render_entry_inline_refs(story, inline_records)
        unit_label = str(entry.get("unitLabel") or "SCENE")
        for i, unit in enumerate(units, 1):
            render_unit(story, unit, i, store, unit_label, inline_mapping)

    render_extra_package_data(story, base_path, entries)
    render_persistent_reference(story, store)

    doc.build(story, onFirstPage=page_decor, onLaterPages=page_decor, canvasmaker=InvariantCanvas)
    digest = hashlib.sha256(output_path.read_bytes()).hexdigest()
    return {
        "production": title,
        "basePath": base_path,
        "file": output_path.name,
        "sha256": digest,
        "entries": len(entries),
        "units": total_units,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="dist/review-pdfs", help="Output directory")
    parser.add_argument(
        "--include-legacy-root",
        action="store_true",
        help="Also export the legacy root data/ prequel package",
    )
    args = parser.parse_args()

    manifest = read_json(MANIFEST_PATH)
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entry in manifest:
        base_path = entry.get("basePath", "data")
        if base_path == "data" and not args.include_legacy_root:
            continue
        groups[base_path].append(entry)

    out_dir = ROOT / args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    for stale in out_dir.glob("*.pdf"):
        stale.unlink()

    commit_sha = current_commit()
    results: list[dict[str, Any]] = []
    for base_path in sorted(groups):
        entries = groups[base_path]
        title = production_title(base_path, entries)
        path = out_dir / f"{safe_slug(title)}-production-review.pdf"
        results.append(build_pdf(base_path, entries, path, commit_sha))

    manifest_out = {
        "sourceCommit": commit_sha,
        "rule": "One PDF per non-legacy RexPrompt package basePath referenced by data/shows.json.",
        "productions": results,
    }
    (out_dir / "review-manifest.json").write_text(
        json.dumps(manifest_out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    index_lines = [
        "# RexPrompt Production Review PDFs",
        "",
        f"Source commit: `{commit_sha}`",
        "",
    ]
    for result in results:
        index_lines.append(
            f"- {result['production']}: {result['units']} assembled units - `{result['file']}`"
        )
    (out_dir / "README.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")

    print(json.dumps(manifest_out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
