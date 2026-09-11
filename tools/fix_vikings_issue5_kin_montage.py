#!/usr/bin/env python3
"""Fix Vikings 2026 Issue 5 page 14 Kin montage continuity.

Narrow one-page production-data patch. Preserves page ID, panel count/order,
and dialogue while ensuring the montage depicts exactly the three established
Kin: Astrid and two men. One man may appear twice at different times.
"""

from __future__ import annotations

import base64
import copy
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OVERLAY = ROOT / "data" / "shows" / "vikings-2026-s1" / "encoded" / "pages_e05_p13_p18.json.gzb64"
PAGE_ID = "VIK_S1E05_P14"


def load_overlay() -> list[dict]:
    encoded = "".join(OVERLAY.read_text(encoding="utf-8").split())
    payload = gzip.decompress(base64.b64decode(encoded)).decode("utf-8")
    data = json.loads(payload)
    if not isinstance(data, list):
        raise TypeError("Expected list overlay")
    return data


def save_overlay(data: list[dict]) -> None:
    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    packed = gzip.compress(text.encode("utf-8"), mtime=0)
    OVERLAY.write_text(base64.b64encode(packed).decode("ascii") + "\n", encoding="utf-8")


def main() -> None:
    pages = load_overlay()
    page = next((p for p in pages if p.get("id") == PAGE_ID), None)
    if page is None:
        raise SystemExit(f"{PAGE_ID} not found")

    original_dialogue = copy.deepcopy(page.get("dialogueInline"))
    original_panel_numbers = [p.get("panel") for p in page.get("panelPlan") or []]
    if original_panel_numbers != [1, 2, 3, 4, 5]:
        raise AssertionError(f"Unexpected panel structure: {original_panel_numbers}")

    page["summary"] = (
        "The three Kin are now encountered around Bushwick as separate regulars: one man at the laundromat, "
        "the other in the park, Astrid with the upstairs neighbor, and later the first man at the bodega before "
        "all three return to apartment 5B from their separate errands."
    )
    page["panelPlan"] = [
        {
            "panel": 1,
            "location": "Bushwick laundromat",
            "shotType": "medium",
            "action": "One of the two male Kin folds the household laundry at a plastic table while watching the laundromat television with two regular patrons. He is comfortable enough to work without Carrie, Bjorn, Gunnar, Astrid, or the other male Kin present.",
            "dialogueIndices": [],
            "captionIndices": []
        },
        {
            "panel": 2,
            "location": "Bushwick neighborhood park",
            "shotType": "medium",
            "action": "The other male Kin sits alone on a park bench eating a packaged snack while studying a nearby public sculpture and painted wall. Joggers and parents pass without treating him as an event.",
            "dialogueIndices": [],
            "captionIndices": []
        },
        {
            "panel": 3,
            "location": "apartment-building hallway outside the upstairs neighbor's door",
            "shotType": "insert",
            "action": "Astrid and the upstairs neighbor exchange packaged snacks in the hallway. Their partial shared language is carried by familiar gestures; neither needs Carrie to mediate the exchange.",
            "dialogueIndices": [],
            "captionIndices": []
        },
        {
            "panel": 4,
            "location": "neighborhood bodega",
            "shotType": "medium",
            "action": "Later, the same male Kin seen at the laundromat enters the bodega carrying the folded laundry bag. The owner has already set a familiar item on the counter for him before he reaches it.",
            "dialogueIndices": [],
            "captionIndices": []
        },
        {
            "panel": 5,
            "location": "fifth-floor hallway outside apartment 5B",
            "shotType": "wide",
            "action": "Near dusk, the three Kin converge at apartment 5B from separate errands: Astrid approaches with the neighbor's packaged snack, one man carries the folded laundry and small bodega bag, and the other arrives with the park snack wrapper tucked into a pocket. The brass apartment door waits between them; they have plainly spent the day apart and returned home independently.",
            "dialogueIndices": [],
            "captionIndices": []
        }
    ]

    if page.get("dialogueInline") != original_dialogue:
        raise AssertionError("Dialogue changed")
    if [p.get("panel") for p in page["panelPlan"]] != original_panel_numbers:
        raise AssertionError("Panel order changed")

    save_overlay(pages)
    print(f"Patched {PAGE_ID}: exactly Astrid + two male Kin; one male repeats chronologically; Panel 5 is drawable.")


if __name__ == "__main__":
    main()
