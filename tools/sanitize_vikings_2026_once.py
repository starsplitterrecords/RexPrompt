#!/usr/bin/env python3
"""One-time semantic cleanup for active Vikings 2026 RexPrompt production data.

Preserves page story data while removing repeated assembler-level scaffolding from
page directionInline records and reducing character shelves to durable,
character-specific generation information.
"""

from __future__ import annotations

import base64
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data/shows/vikings-2026-s1"
MANIFEST = ROOT / "data/shows.json"
CHARACTERS = SHOW / "characters.json"

DROP_DIRECTION_TYPES = {"story", "tone", "continuity", "location", "lettering"}

CANONICAL_GENERATION_LINE = (
    "Finished full-color portrait interior story comic page in the established Vikings 2026 sequential-art language. "
    "Bright ordinary-2026 documentary-sitcom realism; treat every character as a real person. Vikings are intelligent and dignified; "
    "comedy comes from incompatible systems, practical consequences, and New York indifference rather than stupidity or fantasy spectacle. "
    "Use actual selected released Issue 1 story-art references as strict visual canon for recurring identity and world appearance; use approved "
    "current-production artwork only for newer continuity state. Preserve scripted panel count and order, physical geography, causal action, "
    "natural character acting, and dialogueInline exactly with clear speaker attribution, natural left-to-right balloon order, readable balloon "
    "volume, and no invented, duplicated, omitted, or corrupted words. Interior story page only; no cover, promotional, municipal-editorial, "
    "dossier, credits, header, or character-label language unless scripted. A normal story page contains only text required by the assembled recipe."
)

CHARACTER_UPDATES = {
    "qwtivx28x": {
        "visualAnchor": "Massive, broad-shouldered late-30s Norse man with a broad severe rectangular face, square jaw, short sandy-brown hair, thick sandy-brown beard with lighter natural highlights, deep-set light eyes, weathered skin, and a heavy grounded posture.",
        "promptContinuity": ["Do not average his face, hair, beard, or build with Gunnar or other Norse characters"],
    },
    "ywg8bdjvl": {
        "visualAnchor": "Massive, barrel-chested late-30s Norse man with a rugged square jaw, thick swept-back wavy blond hair, heavy golden-blond beard, light eyes, weathered fair skin, and a powerful broad frame.",
        "promptContinuity": ["Preserve the visible differences between Gunnar and Bjorn; they are not interchangeable Viking archetypes"],
    },
    "19020mp40": {
        "visualAnchor": "Early-40s woman with a heart-shaped face, fair lived-in complexion, tired light eyes, textured ash-blond hair streaked with silver and usually pulled into a loose practical bun, and a medium practical build with an unglamorous public-servant presence.",
        "promptContinuity": ["Preserve her practical DTI workwear and identification details when the story has not changed them"],
    },
    "bvfeqb22e": {
        "visualAnchor": "Lean younger man with a narrow oval face, short carefully styled ash-blond hair, pale eyes, fair indoor complexion, clear-framed glasses, restless kinetic posture, and contemporary startup/tech wardrobe and devices.",
        "promptContinuity": ["Keep him visually contemporary to ordinary 2026 New York; do not turn his technology into cyberpunk design"],
    },
    "magister": {
        "visualAnchor": "Clinical, birdlike academic presence with restrained professional dress and invasive stillness around artifacts and living historical subjects.",
        "promptContinuity": ["Keep him grounded in an ordinary contemporary museum context; do not redesign him as a fantasy mystic because of the Magister handle"],
    },
    "dfh4bu71y": {
        "visualAnchor": "Plain municipal administrator in restrained officewear with controlled grooming, badge, folders, and precise desk posture; the human equivalent of a filing cabinet.",
        "promptContinuity": ["Keep him grounded in ordinary municipal-office realism rather than stylized authoritarian imagery"],
    },
    "tnvx3hlo0": {
        "visualAnchor": "Small group of grounded 9th-century Norse adults with authentic physical weight, practical historical clothing, and distinct individual faces and builds.",
        "promptContinuity": ["Preserve individually established Kin appearances; do not duplicate or average Bjorn or Gunnar into the group"],
    },
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def decode_payload(path: Path):
    encoded = "".join(path.read_text(encoding="utf-8").split())
    raw = gzip.decompress(base64.b64decode(encoded, validate=True))
    return json.loads(raw.decode("utf-8"))


def encode_payload(path: Path, payload) -> None:
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    encoded = base64.b64encode(gzip.compress(raw, mtime=0)).decode("ascii")
    path.write_text(encoded + "\n", encoding="utf-8")


def clean_page_payload(path: Path) -> tuple[int, int]:
    payload = decode_payload(path)
    assert isinstance(payload, list), f"expected page list: {path}"
    removed = 0
    retained = 0
    for page in payload:
        directions = page.get("directionInline")
        if not isinstance(directions, list):
            continue
        kept = []
        for item in directions:
            kind = item.get("type") if isinstance(item, dict) else None
            if kind in DROP_DIRECTION_TYPES:
                removed += 1
            else:
                kept.append(item)
                retained += 1
        if kept:
            page["directionInline"] = kept
        else:
            page.pop("directionInline", None)
    encode_payload(path, payload)
    return removed, retained


def main() -> None:
    characters = load_json(CHARACTERS)
    characters["visualCanonSource"] = (
        "Released Vikings 2026 Issue 1 story art in StarSplitterVisions is the exact authority for established recurring visual identity and world appearance; "
        "approved current-production artwork controls only newer continuity state."
    )
    for character_id, patch in CHARACTER_UPDATES.items():
        record = characters.get(character_id)
        assert isinstance(record, dict), f"missing Vikings character: {character_id}"
        record.update(patch)
    CHARACTERS.write_text(json.dumps(characters, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    shows = load_json(MANIFEST)
    active = [show for show in shows if str(show.get("id", "")).startswith("vikings-2026-s1")]
    assert active, "no active Vikings shows"

    overlay_paths: list[Path] = []
    seen: set[Path] = set()
    for show in active:
        show["generationLine"] = CANONICAL_GENERATION_LINE
        for overlay in show.get("sceneOverlays", []):
            if overlay.get("encoding") != "gzip-base64":
                continue
            path = SHOW / overlay["file"]
            if path not in seen:
                seen.add(path)
                overlay_paths.append(path)

    MANIFEST.write_text(json.dumps(shows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    removed_total = 0
    retained_total = 0
    for path in overlay_paths:
        removed, retained = clean_page_payload(path)
        removed_total += removed
        retained_total += retained
        print(f"{path.relative_to(ROOT)}: removed {removed}, retained {retained} page-specific directions")

    print(f"Vikings cleanup complete: {len(overlay_paths)} active encoded payloads")
    print(f"Removed generic direction records: {removed_total}")
    print(f"Retained page-specific direction records: {retained_total}")


if __name__ == "__main__":
    main()
