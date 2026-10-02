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

GENERIC_DIRECTION_TYPES = {
    "story",
    "tone",
    "continuity",
    "location",
    "lettering",
}

PRODUCTION_RESIDUE = [
    "Reader Function",
    "readerFunction",
    "Advance the beat clearly; preserve speaker identity and natural balloon order.",
    "Bright ordinary-2026 documentary-sitcom realism. Treat every character as a real person.",
    "Use dialogueInline exactly with clear speaker attribution, natural left-to-right balloon order, readable balloon volume",
    "Released Vikings 2026 Issue 1 is strict visual canon.",
]

CHARACTER_SCOPE_RESIDUE = [
    "Released Vikings 2026 Issue 1 is the exact authority",
    "Match Bjorn to actual released Issue 1 visual references",
    "Match Gunnar to actual released Issue 1 visual references",
    "Match Carrie to actual released Issue 1 visual references",
    "Match released Issue 1 appearance",
    "Use released appearance when established",
    "Keep his apparent age and body proportions stable across every page",
    "Keep her apparent age, face, hair, and body proportions stable across every page",
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

    canon_source = characters.get("visualCanonSource")
    assert isinstance(canon_source, str) and "StarSplitterVisions" in canon_source and "Issue 1" in canon_source, "Vikings global character visual authority is missing"

    for character_id in CORE_VISUAL_CHARACTER_IDS:
        record = characters.get(character_id)
        assert isinstance(record, dict), f"missing core Vikings visual character record: {character_id}"
        # The sanitized character shelf deliberately keeps identity and story roles,
        # while released pixels and approved drafts remain visual authority.
        assert isinstance(record.get("role"), str) and record["role"].strip(), f"core Vikings character missing role: {record.get('name', character_id)}"
        visual = record.get("visualAnchor")
        if visual is not None:
            assert isinstance(visual, str) and visual.strip(), f"malformed visual anchor: {character_id}"
        continuity = record.get("promptContinuity")
        if continuity is not None:
            assert isinstance(continuity, list) and all(isinstance(item, str) and item.strip() for item in continuity), f"malformed character continuity: {character_id}"
        generation_text = json.dumps({"visualAnchor": visual, "promptContinuity": continuity}, ensure_ascii=False)
        for residue in CHARACTER_SCOPE_RESIDUE:
            assert residue not in generation_text, f"global/correction scaffolding leaked into character shelf: {record.get('name', character_id)}: {residue}"

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
    issue_pages_by_id = {}
    for show in active:
        show_id = show["id"]
        assert show.get("unitLabel") == "PAGE", f"Vikings show is not page production: {show_id}"
        assert show.get("basePath") == "data/shows/vikings-2026-s1", f"unexpected Vikings basePath: {show_id}"
        generation_line = show.get("generationLine")
        assert isinstance(generation_line, str) and generation_line.strip(), f"missing generation contract: {show_id}"
        assert "panel order" in generation_line.lower() and "exact dialogue" in generation_line.lower(), f"generation contract must preserve panels and dialogue: {show_id}"
        assert "Legacy S1E02 payload IDs" not in generation_line, "legacy identifier explanation leaked into generation instruction"

        # Match the current loader: flat scenesFiles, or base plus overlays,
        # followed by the show's includeIdPattern (shared covers are filtered).
        files = show.get("scenesFiles") or [show.get("scenesFile", "pages_base.json")]
        selected = []
        for rel in files:
            path = SHOW / rel
            assert path.exists(), f"missing Vikings payload: {rel}"
            payload = load_payload(path)
            assert isinstance(payload, list), f"payload is not a list: {rel}"
            selected.extend(payload)
            active_files.append(rel)
        for overlay in show.get("sceneOverlays", []):
            rel = overlay.get("file")
            assert rel, f"overlay missing file: {show_id}"
            path = SHOW / rel
            assert path.exists(), f"active Vikings overlay missing: {rel}"
            payload = load_payload(path, overlay.get("encoding"))
            assert isinstance(payload, list), f"overlay is not a page list: {rel}"
            selected.extend(payload)
            active_files.append(rel)
        if show.get("includeIdPattern"):
            pattern = re.compile(show["includeIdPattern"])
            selected = [page for page in selected if pattern.search(str(page.get("id", "")))]
        assert selected, f"no assembled pages: {show_id}"
        issue_pages_by_id[show_id] = selected
        active_pages.extend(selected)

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

        directions = page.get("directionInline", [])
        assert isinstance(directions, list), f"directionInline malformed: {page_id}"
        for item in directions:
            assert isinstance(item, dict), f"directionInline entry malformed: {page_id}"
            kind = item.get("type")
            assert kind not in GENERIC_DIRECTION_TYPES, f"generic {kind} scaffolding returned to page scope: {page_id}"

    assert len(ids) == len(set(ids)), "duplicate active Vikings page ids"

    # Current season: Issue 1 is released; Issues 2-12 include a cover,
    # editorial opening, story pages, and closing editorial/teaser.
    expected_counts = {2: 27, 3: 24, 4: 27, 5: 24, 6: 27, 7: 27,
                       8: 24, 9: 27, 10: 24, 11: 27, 12: 27}
    for issue, count in expected_counts.items():
        show_id = f"vikings-2026-s1-e{issue:02d}"
        assert show_id in issue_pages_by_id, f"missing current Vikings issue: {show_id}"
        pages = issue_pages_by_id[show_id]
        expected_ids = [f"VIK_S1E{issue:02d}_P{number:02d}" for number in range(1, count + 1)]
        assert [page.get("id") for page in pages] == expected_ids, f"Issue {issue}: publication page IDs/order drift"
        assert [page.get("page") for page in pages] == list(range(1, count + 1)), f"Issue {issue}: page numbering drift"

    decoded_text = json.dumps(active_pages, ensure_ascii=False)
    for residue in PRODUCTION_RESIDUE:
        assert residue not in decoded_text, f"production residue in active Vikings pages: {residue}"

    print("Vikings 2026 production-hygiene validation passed")
    print("IMG production normalization reference: valid")
    print("Core character identities:", len(CORE_VISUAL_CHARACTER_IDS))
    print("Current season issues:", len(issue_pages_by_id))
    print("Active page records:", len(active_pages))
    print("Active production files:", len(set(active_files)))
    print("Generic page-direction scaffolding: absent")
    print("Series generation contract: normalized")


if __name__ == "__main__":
    main()
