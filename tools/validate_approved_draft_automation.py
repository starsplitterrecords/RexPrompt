#!/usr/bin/env python3
"""Validate automatic approved-image persistence configuration."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "production" / "approval-policy.json"
INTAKE = ROOT / "production" / "drafts" / "intake.json"
INGEST_TOOL = ROOT / "tools" / "ingest_approved_drafts.py"
INGEST_WORKFLOW = ROOT / ".github" / "workflows" / "ingest-approved-drafts.yml"


def load(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"{path.relative_to(ROOT)} must contain an object"
    return data


def main() -> int:
    errors: list[str] = []

    try:
        policy = load(POLICY)
        assert policy.get("schemaVersion") == 1, "approval policy schemaVersion must be 1"
        page = policy.get("pageApproval")
        assert isinstance(page, dict), "approval policy pageApproval must be an object"
        assert page.get("mode") == "automatic-on-substantial-pass", "page approval mode must be automatic-on-substantial-pass"
        checks = page.get("requiredChecks")
        assert isinstance(checks, list) and checks, "page approval requiredChecks must be non-empty"
        required = {
            "recipe-fidelity",
            "character-identity-continuity",
            "immediate-visual-continuity",
            "composition-and-readability",
            "lettering-correctness",
            "output-hygiene",
            "no-material-generation-defect",
        }
        missing = sorted(required.difference(checks))
        assert not missing, f"approval policy missing checks: {', '.join(missing)}"
        persistence = policy.get("persistence")
        assert isinstance(persistence, dict), "approval policy persistence must be an object"
        assert persistence.get("mode") == "stage-then-vendor", "approval persistence must use stage-then-vendor"
        assert persistence.get("finalAuthority") == "production/drafts/manifest.json", "approved draft manifest must remain final authority"
    except Exception as exc:
        errors.append(str(exc))

    try:
        intake = load(INTAKE)
        assert intake.get("schemaVersion") == 1, "draft intake schemaVersion must be 1"
        approvals = intake.get("approvals")
        assert isinstance(approvals, dict), "draft intake approvals must be an object"
        for approval_id, entry in approvals.items():
            assert isinstance(approval_id, str) and approval_id, "draft intake approval id must be non-empty"
            assert isinstance(entry, dict), f"draft intake {approval_id!r} must be an object"
            for field in ("seriesId", "issueId", "recipeId", "sourceUrl"):
                assert isinstance(entry.get(field), str) and entry.get(field), f"draft intake {approval_id!r} missing {field}"
            assert entry["sourceUrl"].startswith("https://"), f"draft intake {approval_id!r} sourceUrl must be HTTPS"
    except Exception as exc:
        errors.append(str(exc))

    try:
        ingest = INGEST_TOOL.read_text(encoding="utf-8")
        for token in ("res.cloudinary.com", "MAX_BYTES", "detect_image", "approvalMethod", "approved-production-draft"):
            assert token in ingest, f"ingest tool missing required behavior marker: {token}"
    except Exception as exc:
        errors.append(str(exc))

    try:
        workflow = INGEST_WORKFLOW.read_text(encoding="utf-8")
        for token in ("production/drafts/intake.json", "contents: write", "ingest_approved_drafts.py", "git push"):
            assert token in workflow, f"ingest workflow missing required behavior marker: {token}"
    except Exception as exc:
        errors.append(str(exc))

    if errors:
        print("Approved-draft automation validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Approved-draft automation validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
