#!/usr/bin/env python3
import base64
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data/shows/vikings-2026-s1"

REQUIRED = [
    "characters.json",
    "series_reference.json",
    "settings.json",
    "regions.json",
    "mood.json",
    "lighting.json",
    "season_one_plan.json",
    "issue_04_reference.json",
    "issue_05_skaldic_interface_enhanced.md",
    "issue_06_trial_of_toil_development.json",
    "issue_07_war_council_treatment.md",
    "pages_base.json",
]

FORBIDDEN_READABLE = [
    "stale neo-noir",
    "Atavistic Projection",
    "Functional Congruence",
    "Community College",
    "The Corporate Vestibule",
    "sourceReconciliation",
    "issue_04_enhancement_lock.json",
    "issue_07_war_council_recovered_treatment.md",
    "Recovered and ingested from",
]


def load_json(name):
    return json.loads((SHOW / name).read_text())


def decode_overlay(path):
    encoded = "".join(path.read_text().split())
    raw = gzip.decompress(base64.b64decode(encoded, validate=True))
    return json.loads(raw)


def main():
    for name in REQUIRED:
        assert (SHOW / name).exists(), f"missing required Vikings file: {name}"

    readable_paths = [
        p for p in SHOW.rglob("*")
        if p.is_file() and p.suffix in {".json", ".md", ".txt"}
    ]
    readable_text = "\n".join(p.read_text(errors="replace") for p in readable_paths)
    for forbidden in FORBIDDEN_READABLE:
        assert forbidden not in readable_text, f"sanitization residue: {forbidden}"

    characters = load_json("characters.json")
    assert characters.get("visualCanonSource"), "missing package-level visual canon source"
    for key, record in characters.items():
        if key == "visualCanonSource":
            continue
        assert isinstance(record, dict), f"bad character record: {key}"
        assert "canonRule" not in record, f"per-character canon boilerplate returned: {key}"
        assert "name" in record and "handle" in record, f"incomplete character identity: {key}"

    series = load_json("series_reference.json")
    assert series["coreConflict"] == "Integration versus assimilation."
    assert series.get("visualCanonSource"), "series visual canon source missing"
    assert "guardrails" not in series, "negative correction scaffold returned to series reference"

    settings = load_json("settings.json")
    for stale_key in ("community_college", "corporate_lobby", "executive_elevator"):
        assert stale_key not in settings, f"stale setting returned: {stale_key}"

    regions = load_json("regions.json")
    assert regions["transitNYC"]["function"] == "Recurring city-movement infrastructure"

    plan = load_json("season_one_plan.json")
    issues = {item["issue"]: item for item in plan["issues"]}
    assert issues[4].get("referenceFile") == "issue_04_reference.json"
    assert issues[6].get("developmentFile") == "issue_06_trial_of_toil_development.json"
    assert issues[7].get("treatmentFile") == "issue_07_war_council_treatment.md"
    assert issues[7]["title"] == "War Council"
    assert "sourcePriority" not in plan
    assert "obsoleteMechanisms" not in plan
    assert "teleplayNote" not in plan

    overlays = sorted((SHOW / "encoded").glob("pages_*.json.gzb64"))
    assert overlays, "no encoded Vikings page overlays"
    pages = []
    for path in overlays:
        payload = decode_overlay(path)
        assert isinstance(payload, list), f"overlay is not a page list: {path.name}"
        pages.extend(payload)

    ids = [p["id"] for p in pages]
    assert len(ids) == len(set(ids)), "duplicate encoded page ids"
    assert len(pages) == 72, f"expected 72 encoded production pages, found {len(pages)}"

    expected = {
        "S1E02": list(range(1, 25)),
        "S1E03": list(range(1, 25)),
        "S1E05": list(range(1, 25)),
    }
    for episode, page_numbers in expected.items():
        episode_pages = sorted(p["page"] for p in pages if p.get("episode") == episode)
        assert episode_pages == page_numbers, f"bad page sequence for {episode}: {episode_pages}"

    for p in pages:
        assert len(p.get("panelPlan", [])) == p.get("panelCount"), f"panel mismatch: {p['id']}"
        assert p.get("dialogueInline") is not None, f"dialogue missing: {p['id']}"
        for d in p.get("dialogueInline", []):
            assert d.get("characterHandle") != "UNKNOWN", f"unknown speaker: {p['id']}"

    decoded_text = json.dumps(pages, ensure_ascii=False)
    for forbidden in ("cyberpunk architecture", "neo-noir", "murder-holes"):
        assert forbidden not in decoded_text, f"encoded residue: {forbidden}"

    print("Vikings 2026 validation passed")
    print("Encoded pages:", len(pages))
    print("Readable package files checked:", len(readable_paths))


if __name__ == "__main__":
    main()
