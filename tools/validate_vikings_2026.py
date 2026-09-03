#!/usr/bin/env python3
import base64
import gzip
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data/shows/vikings-2026-s1"
MANIFEST = ROOT / "data/shows.json"

CORE_FILES = [
    "characters.json",
    "settings.json",
    "regions.json",
    "pages_base.json",
]

PRODUCTION_RESIDUE = [
    "Reader Function",
    "readerFunction",
    "Advance the beat clearly; preserve speaker identity and natural balloon order.",
]


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def decode_gzip_base64(path):
    encoded = "".join(path.read_text(encoding="utf-8").split())
    allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=")
    bad = [(index, char) for index, char in enumerate(encoded) if char not in allowed]
    assert not bad, f"non-base64 characters in {path.name}: {bad[:12]}"
    raw = gzip.decompress(base64.b64decode(encoded, validate=True))
    return json.loads(raw.decode("utf-8"))


def load_payload(path, encoding=None):
    if encoding == "gzip-base64" or path.suffix == ".gzb64":
        return decode_gzip_base64(path)
    return load_json(path)


def main():
    for name in CORE_FILES:
        path = SHOW / name
        assert path.exists(), f"missing core Vikings production file: {name}"
        if path.suffix == ".json":
            load_json(path)

    characters = load_json(SHOW / "characters.json")
    for key, record in characters.items():
        if key == "visualCanonSource":
            continue
        assert isinstance(record, dict), f"bad character record: {key}"
        assert record.get("name"), f"character missing name: {key}"
        assert record.get("handle"), f"character missing handle: {key}"

    shows = load_json(MANIFEST)
    active = [
        show for show in shows
        if str(show.get("id", "")).startswith("vikings-2026-s1")
    ]
    assert active, "no active Vikings shows in data/shows.json"

    issue2_show = next((show for show in active if show.get("id") == "vikings-2026-s1-e02"), None)
    assert issue2_show, "current Vikings Issue 2 is not registered"
    assert issue2_show.get("issueLabel") == "Issue 2 — Landfall Bushwick", "Vikings Issue 2 label drift"

    active_pages = []
    active_files = []
    for show in active:
        assert show.get("unitLabel") == "PAGE", f"Vikings show is not page production: {show.get('id')}"
        assert show.get("basePath") == "data/shows/vikings-2026-s1", f"unexpected Vikings basePath: {show.get('id')}"

        base = SHOW / show.get("scenesFile", "pages_base.json")
        assert base.exists(), f"missing Vikings base payload: {base.name}"
        base_payload = load_payload(base)
        assert isinstance(base_payload, list), f"base payload is not a list: {base.name}"
        active_pages.extend(base_payload)
        active_files.append(base.name)

        for overlay in show.get("sceneOverlays", []):
            rel = overlay.get("file")
            assert rel, f"overlay missing file: {show.get('id')}"
            path = SHOW / rel
            assert path.exists(), f"active Vikings overlay missing: {rel}"
            payload = load_payload(path, overlay.get("encoding"))
            assert isinstance(payload, list), f"overlay is not a page list: {rel}"
            active_pages.extend(payload)
            active_files.append(rel)

    ids = []
    for page in active_pages:
        assert isinstance(page, dict), "active Vikings page is not an object"
        page_id = page.get("id")
        assert page_id, "active Vikings page missing id"
        ids.append(page_id)

        number = page.get("page")
        assert isinstance(number, int) and number > 0, f"bad page number: {page_id}"

        panel_plan = page.get("panelPlan")
        assert isinstance(panel_plan, list) and panel_plan, f"panelPlan missing: {page_id}"
        if page.get("panelCount") is not None:
            assert len(panel_plan) == page.get("panelCount"), f"panel mismatch: {page_id}"

        dialogue = page.get("dialogueInline")
        assert isinstance(dialogue, list), f"dialogueInline missing or malformed: {page_id}"
        for line in dialogue:
            assert isinstance(line, dict), f"malformed dialogue entry: {page_id}"
            assert isinstance(line.get("text"), str), f"dialogue text missing: {page_id}"
            assert line.get("characterHandle") != "UNKNOWN", f"unknown speaker: {page_id}"
            if line.get("characterHandle"):
                assert line.get("handle") == line.get("characterHandle"), f"unnormalized speaker handle: {page_id}"
            subtext = line.get("subtext")
            if isinstance(subtext, str) and subtext.startswith("Panel "):
                match = re.fullmatch(r"Panel (\d+)", subtext)
                assert match, f"malformed panel assignment: {page_id}"
                panel_number = int(match.group(1))
                assert 1 <= panel_number <= len(panel_plan), f"dialogue panel out of range: {page_id}"

    assert len(ids) == len(set(ids)), "duplicate active Vikings page ids"

    issue3_show = next((show for show in active if show.get("id") == "vikings-2026-s1-e03"), None)
    assert issue3_show, "Vikings Issue 3 is not registered"
    assert issue3_show.get("issueLabel") == "Issue 3 — The Iron Worm", "Vikings Issue 3 label drift"

    issue2_pages = [page for page in active_pages if str(page.get("id", "")).startswith("VIK_S1I02_P")]
    expected_issue2_ids = [f"VIK_S1I02_P{number:02d}" for number in range(1, 25)]
    actual_issue2_ids = [page.get("id") for page in sorted(issue2_pages, key=lambda page: page.get("page", 0))]
    assert actual_issue2_ids == expected_issue2_ids, "Vikings Issue 2 must expose exactly VIK_S1I02_P01-P24 in page order"
    assert [page.get("page") for page in sorted(issue2_pages, key=lambda page: page.get("page", 0))] == list(range(1, 25)), "Vikings Issue 2 page numbering drift"

    issue3_pages = [page for page in active_pages if str(page.get("id", "")).startswith("VIK_S1E03_P")]
    expected_issue3_ids = [f"VIK_S1E03_P{number:02d}" for number in range(1, 25)]
    actual_issue3_ids = [page.get("id") for page in sorted(issue3_pages, key=lambda page: page.get("page", 0))]
    assert actual_issue3_ids == expected_issue3_ids, "Vikings Issue 3 must expose exactly VIK_S1E03_P01-P24 in page order"
    assert [page.get("page") for page in sorted(issue3_pages, key=lambda page: page.get("page", 0))] == list(range(1, 25)), "Vikings Issue 3 page numbering drift"

    decoded_text = json.dumps(active_pages, ensure_ascii=False)
    for residue in PRODUCTION_RESIDUE:
        assert residue not in decoded_text, f"production residue in active Vikings pages: {residue}"

    print("Vikings 2026 production-hygiene validation passed")
    print("Issue 2 page records:", len(issue2_pages))
    print("Issue 3 page records:", len(issue3_pages))
    print("Active page records:", len(active_pages))
    print("Active production files:", len(set(active_files)))


if __name__ == "__main__":
    main()
