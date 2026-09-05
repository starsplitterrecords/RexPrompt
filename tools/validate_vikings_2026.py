#!/usr/bin/env python3
import base64
import gzip
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data/shows/vikings-2026-s1"
MANIFEST = ROOT / "data/shows.json"
NORMALIZATION_REFERENCE = ROOT / "production/references/vikings-2026/img-production-normalization.json"
DRAFT_MANIFEST = ROOT / "production/drafts/manifest.json"

CORE_FILES = [
    "characters.json",
    "settings.json",
    "regions.json",
    "pages_base.json",
]

CORE_VISUAL_CHARACTER_IDS = [
    "qwtivx28x",       # Bjorn
    "ywg8bdjvl",       # Gunnar
    "19020mp40",       # Carrie
    "bvfeqb22e",       # Silas
    "magister",        # Dr. Aris Thorne / Magister
    "dfh4bu71y",       # DTI Floor Supervisor
    "tnvx3hlo0",       # The Kin
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


def validate_img_normalization(characters):
    assert NORMALIZATION_REFERENCE.exists(), "missing Vikings IMG production normalization reference"
    reference = load_json(NORMALIZATION_REFERENCE)
    assert reference.get("schemaVersion") == 1, "Vikings IMG normalization schemaVersion drift"
    assert reference.get("seriesId") == "vikings-2026", "Vikings IMG normalization seriesId drift"
    assert reference.get("status") == "normalized-img-production-reference", "Vikings IMG normalization status drift"

    baseline = reference.get("releasedBaseline")
    assert isinstance(baseline, dict), "Vikings IMG normalization missing releasedBaseline"
    assert baseline.get("repository") == "starsplitterrecords/StarSplitterVisions", "Vikings released visual authority drift"
    assert baseline.get("branch") == "main", "Vikings released canon must resolve from StarSplitterVisions main"
    assert baseline.get("visionsSlug") == "vikings-2026", "Vikings Visions slug drift"
    assert baseline.get("issue") == 1, "Vikings released visual baseline must remain Issue 1 until a later issue is actually released"

    scopes = reference.get("referenceScopes")
    assert isinstance(scopes, dict), "Vikings IMG normalization missing referenceScopes"
    story_scope = scopes.get("storyPageLanguage")
    assert isinstance(story_scope, dict), "Vikings IMG normalization missing story-page scope"
    excluded = story_scope.get("exclude")
    assert isinstance(excluded, list) and excluded, "Vikings story-page reference exclusions are missing"

    known_locks = reference.get("knownScopeLocks")
    assert isinstance(known_locks, list) and known_locks, "Vikings IMG normalization missing known scope locks"
    lock_by_path = {item.get("path"): item for item in known_locks if isinstance(item, dict)}
    cover_duplicate = lock_by_path.get("/images/pages/vikings-2026/issue-01/page-001.jpg")
    assert cover_duplicate and cover_duplicate.get("storyPageLayoutAuthority") is False, "released page-001 cover duplicate must never become story-page layout authority"

    untrusted = reference.get("untrustedProductionSources")
    assert isinstance(untrusted, list), "Vikings IMG normalization missing untrusted production sources"
    assert "sites/visions/public/intake/" in untrusted, "Visions intake must remain outside Vikings continuity authority"

    session_gate = reference.get("sessionStartGate")
    page_gate = reference.get("perPageGate")
    assert isinstance(session_gate, list) and len(session_gate) >= 5, "Vikings session-start gate is incomplete"
    assert isinstance(page_gate, list) and len(page_gate) >= 7, "Vikings per-page visual-reference gate is incomplete"

    frontier = reference.get("frontierPolicy")
    assert isinstance(frontier, dict) and frontier.get("mode") == "derived-not-stored", "Vikings production frontier must be derived, not stored as a cursor"

    output_rule = reference.get("storyPageOutputRule")
    assert isinstance(output_rule, str) and "Only text required by the assembled recipe belongs on the story page." in output_rule, "Vikings story-page output scope is incomplete"

    for character_id in CORE_VISUAL_CHARACTER_IDS:
        record = characters.get(character_id)
        assert isinstance(record, dict), f"missing core Vikings visual character record: {character_id}"
        visual = record.get("visualAnchor")
        assert isinstance(visual, str) and len(visual.strip()) >= 80, f"core Vikings character missing useful visualAnchor: {record.get('name', character_id)}"
        continuity = record.get("promptContinuity")
        assert isinstance(continuity, list) and continuity, f"core Vikings character missing promptContinuity: {record.get('name', character_id)}"

    drafts = load_json(DRAFT_MANIFEST)
    assert drafts.get("schemaVersion") == 1 and isinstance(drafts.get("drafts"), dict), "approved production draft manifest is malformed"
    for key, entry in drafts["drafts"].items():
        if not str(key).startswith("vikings-2026::"):
            continue
        assert isinstance(entry, dict), f"bad Vikings approved draft record: {key}"
        assert entry.get("status") == "approved-production-draft", f"unapproved Vikings image stored as production authority: {key}"


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

    validate_img_normalization(characters)

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
    print("IMG production normalization reference: valid")
    print("Core visual anchors:", len(CORE_VISUAL_CHARACTER_IDS))
    print("Issue 2 page records:", len(issue2_pages))
    print("Issue 3 page records:", len(issue3_pages))
    print("Active page records:", len(active_pages))
    print("Active production files:", len(set(active_files)))


if __name__ == "__main__":
    main()
