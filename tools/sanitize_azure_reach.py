#!/usr/bin/env python3
"""Semantically sanitize Azure Reach RexPrompt production data.

Preserves authored story/page content while moving repeated production guidance
out of page scope and into reusable persistent direction references.
Idempotent: rerunning a sanitized package performs verification only.
"""
from __future__ import annotations

import base64
import copy
import gzip
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data" / "shows" / "azure-reach-s1"
ENCODED = SHOW / "encoded"
INDEX = ROOT / "index.html"

LEGACY_PREFIXES = (
    "AZURE REACH VISUAL LANGUAGE:",
    "PAGE ACTION — SOURCE-LOCKED:",
    "CHARACTER CONTINUITY —",
    "LOCATION / PROP / STATE CONTINUITY —",
    "COMIC PAGE / LETTERING —",
)

CORE_DIRECTIONS = {
    "AZR_PRODUCTION_CORE": {
        "text": (
            "AZURE REACH PRODUCTION CORE — Bright, glossy, well-funded contemporary marine park; "
            "public wonder over clean backstage competence. Workplace warmth under pressure. Animals "
            "remain safe, calm, behaviorally credible, and never the joke; human systems, interpretation, "
            "and conflicting professional priorities create the comedy."
        )
    },
    "AZR_LETTERING": {
        "text": (
            "LETTERING — Use clean professional integrated comic lettering. Preserve exact dialogue, "
            "captions, and scripted signage; keep balloon order and speaker attribution unambiguous; "
            "never invent, duplicate, omit, or corrupt text. Compose art with intentional room for lettering."
        )
    },
    "AZR_VIS_BRINE": {
        "text": (
            "BRINE SQUAD VISUAL — Dark navy / black-blue technical workwear with cyan functional accents, "
            "radios and practical gear; sturdy, work-ready silhouettes; no hot pink."
        )
    },
    "AZR_VIS_GUEST_RELATIONS": {
        "text": (
            "GUEST RELATIONS VISUAL — Lighter blue / teal hospitality wear; tablet, badge, headset or small "
            "radio where appropriate; neat, approachable, mobile, socially open; no Finfluencer glamour."
        )
    },
    "AZR_VIS_FINFLUENCERS": {
        "text": (
            "FINFLUENCER VISUAL — Camera-ready azure uniforms with hot-pink status accents, polished branded "
            "silhouettes and content gear. Julian and Fleur read as public-facing stars; Kyler reads as media support."
        )
    },
    "AZR_VIS_CORPORATE": {
        "text": (
            "CORPORATE VISUAL — Pale blue / slate tailored executive wear, structured silhouettes, minimal "
            "accessories, polished and expensive rather than flashy."
        )
    },
    "AZR_VIS_MAYA_PIP_SEPARATION": {
        "text": (
            "MAYA / PIP SEPARATION — Maya is dark-navy Brine Squad: practical dark hair, technical radio/utility "
            "gear, guarded posture. Pip is lighter blue/teal Guest Relations: tablet/headset/badge, warmer expression, "
            "animated posture. Do not merge their face, hair, silhouette, palette, props, or body language."
        )
    },
}

FACTION_DIRECTIONS = {
    "AZR_BrineSquad": "AZR_VIS_BRINE",
    "AZR_GuestRelations": "AZR_VIS_GUEST_RELATIONS",
    "AZR_Finfluencers": "AZR_VIS_FINFLUENCERS",
    "AZR_Corporate": "AZR_VIS_CORPORATE",
}

GENERIC_DESIGN_SENTENCES = (
    "Compose with intentional negative space for balloons/captions before lettering.",
    "Use clean professional integrated comic lettering, preserve exact dialogue/signage, keep balloon reading order unambiguous, and do not duplicate text.",
)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def decode(path: Path):
    raw = "".join(path.read_text(encoding="utf-8").split())
    return json.loads(gzip.decompress(base64.b64decode(raw, validate=True)).decode("utf-8"))


def encode(path: Path, value) -> None:
    raw = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    packed = gzip.compress(raw, compresslevel=9, mtime=0)
    path.write_text(base64.b64encode(packed).decode("ascii"), encoding="utf-8")


def story_fingerprint(page: dict) -> dict:
    """Creative/story fields that this migration is forbidden to change."""
    return {
        "id": page.get("id"),
        "episode": page.get("episode"),
        "issue": page.get("issue"),
        "page": page.get("page"),
        "pageTitle": page.get("pageTitle"),
        "panelCount": page.get("panelCount"),
        "summary": page.get("summary"),
        "setting": page.get("setting"),
        "region": page.get("region"),
        "factions": copy.deepcopy(page.get("factions")),
        "charactersInline": copy.deepcopy(page.get("charactersInline")),
        "panelPlan": copy.deepcopy(page.get("panelPlan")),
        "dialogueInline": copy.deepcopy(page.get("dialogueInline")),
    }


def split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text.strip())
    if not text:
        return []
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def direction_body(page: dict, prefix: str) -> str:
    for item in page.get("directionInline", []) or []:
        if not isinstance(item, dict):
            continue
        text = str(item.get("text", ""))
        if text.startswith(prefix):
            return text[len(prefix):].strip()
    return ""


def common_episode_sentences(pages: list[dict]) -> dict[str, list[str]]:
    by_episode: dict[str, list[list[str]]] = defaultdict(list)
    prefix = "LOCATION / PROP / STATE CONTINUITY —"
    for page in pages:
        body = direction_body(page, prefix)
        by_episode[str(page.get("episode"))].append(split_sentences(body))

    result: dict[str, list[str]] = {}
    for episode, sentence_lists in by_episode.items():
        if not sentence_lists or any(not seq for seq in sentence_lists):
            result[episode] = []
            continue
        other_sets = [set(seq) for seq in sentence_lists[1:]]
        common = [s for s in sentence_lists[0] if all(s in bag for bag in other_sets)]
        # Do not promote a single generic fragment merely because it repeats. A reusable
        # issue-level rule must contain at least two complete sentences, or one substantial
        # sentence carrying explicit issue continuity/state (>120 chars).
        if len(common) >= 2 or (len(common) == 1 and len(common[0]) > 120):
            result[episode] = common
        else:
            result[episode] = []
    return result


def clean_page_design(body: str) -> str:
    body = re.sub(r"^\s*\d+\s+panels?\.\s*", "", body, flags=re.I)
    for sentence in GENERIC_DESIGN_SENTENCES:
        body = body.replace(sentence, "")
    parts = split_sentences(body)
    kept = []
    for sentence in parts:
        lower = sentence.lower()
        if (
            "professional integrated comic lettering" in lower
            or "balloon reading order" in lower
            or "preserve exact dialogue" in lower
            or "intentional negative space" in lower
        ):
            continue
        # Repeated generic layout doctrine belongs to the show-level generation line.
        if "varied, readable modern prestige-comic layout" in lower and "key image:" not in lower and "page feel:" not in lower:
            continue
        kept.append(sentence)
    return " ".join(kept).strip()


def persistent_refs(page: dict, issue_ref: str | None) -> list[str]:
    refs = ["AZR_PRODUCTION_CORE", "AZR_LETTERING"]
    for faction in page.get("factions", []) or []:
        ref = FACTION_DIRECTIONS.get(faction)
        if ref and ref not in refs:
            refs.append(ref)
    handles = {
        c.get("handle")
        for c in page.get("charactersInline", []) or []
        if isinstance(c, dict)
    }
    if handles & {"@azr.Maya", "@azr.Pip"}:
        refs.append("AZR_VIS_MAYA_PIP_SEPARATION")
    if issue_ref:
        refs.append(issue_ref)
    return refs


def sanitize_page(page: dict, common: list[str], issue_ref: str | None) -> tuple[dict, int, int]:
    before = story_fingerprint(page)
    out = copy.deepcopy(page)

    legacy_count = sum(
        1
        for item in out.get("directionInline", []) or []
        if isinstance(item, dict) and str(item.get("text", "")).startswith(LEGACY_PREFIXES)
    )
    if not legacy_count:
        # Already sanitized: recompute only persistent references so stale scoped
        # production guidance can be removed without touching creative fields.
        out["direction"] = persistent_refs(out, issue_ref)
        after = story_fingerprint(out)
        if before != after:
            raise RuntimeError(f"Story fingerprint drift on {page.get('id')}")
        return out, 0, len(out.get("directionInline", []) or [])

    location_body = direction_body(out, "LOCATION / PROP / STATE CONTINUITY —")
    design_body = direction_body(out, "COMIC PAGE / LETTERING —")

    local_items: list[dict] = []
    location_sentences = split_sentences(location_body)
    if common:
        common_set = set(common)
        location_sentences = [s for s in location_sentences if s not in common_set]
    local_location = " ".join(location_sentences).strip()
    if local_location:
        local_items.append({"text": "PAGE CONTINUITY — " + local_location})

    local_design = clean_page_design(design_body)
    if local_design:
        local_items.append({"text": "PAGE DESIGN — " + local_design})

    out["direction"] = persistent_refs(out, issue_ref)
    if local_items:
        out["directionInline"] = local_items
    else:
        out.pop("directionInline", None)

    after = story_fingerprint(out)
    if before != after:
        raise RuntimeError(f"Sanitization changed story content on {page.get('id')}")
    return out, legacy_count, len(local_items)


def patch_assembler() -> bool:
    """Allow persistent direction refs and page-local direction to assemble together."""
    text = INDEX.read_text(encoding="utf-8")
    old = 'if(s.directionInline?.length){out.push("\\n[DIRECTION]");s.directionInline.forEach(x=>out.push(formatEntry(x)))}else if(s.direction?.length){out.push("\\n[DIRECTION]");s.direction.forEach(k=>{const e=store["direction.json"]?.[k];if(e)out.push(formatEntry(e))})}'
    new = 'if(s.direction?.length||s.directionInline?.length){out.push("\\n[DIRECTION]");if(s.direction?.length)s.direction.forEach(k=>{const e=store["direction.json"]?.[k];if(e)out.push(formatEntry(e))});if(s.directionInline?.length)s.directionInline.forEach(x=>out.push(formatEntry(x)))}'
    if new in text:
        return False
    if old not in text:
        raise RuntimeError("RexPrompt assembler direction block no longer matches expected structure")
    INDEX.write_text(text.replace(old, new), encoding="utf-8")
    return True


def sanitize() -> tuple[int, int, int, bool]:
    paths = sorted(ENCODED.glob("pages_e*.json.gzb64"))
    if not paths:
        raise RuntimeError("No Azure Reach encoded payloads found")

    payloads = {path: decode(path) for path in paths}
    pages = [page for data in payloads.values() for page in data]
    if len(pages) != 132:
        raise RuntimeError(f"Expected 132 Azure Reach pages, found {len(pages)}")

    common_by_episode = common_episode_sentences(pages)
    registry = load(SHOW / "direction.json")
    registry.update(CORE_DIRECTIONS)

    # Repetition alone is not authority. Remove machine-derived issue entries and
    # retain only issue-level production truth independently supported by canon.
    for key in list(registry):
        if re.fullmatch(r"AZR_E\d{2}_CONTINUITY", key):
            registry.pop(key)
    registry["AZR_E02_CONTINUITY"] = {
        "text": (
            "ISSUE 2 CONTINUITY — Dolphins retrieve guest-dropped objects and guests project meaning "
            "onto that behavior. Shellabration Saturdays is only a background Corporate roadmap gag, "
            "not the issue premise."
        )
    }
    issue_refs: dict[str, str | None] = {episode: None for episode in common_by_episode}
    issue_refs["S1E02"] = "AZR_E02_CONTINUITY"

    removed = 0
    local_count = 0
    page_count = 0
    for path, data in payloads.items():
        cleaned = []
        changed = False
        for page in data:
            fixed, removed_here, locals_here = sanitize_page(
                page,
                common_by_episode.get(str(page.get("episode")), []),
                issue_refs.get(str(page.get("episode"))),
            )
            cleaned.append(fixed)
            removed += removed_here
            local_count += locals_here
            page_count += 1
            changed = changed or fixed != page
        if changed:
            encode(path, cleaned)

    dump(SHOW / "direction.json", registry)
    assembler_changed = patch_assembler()
    verify_clean()
    return page_count, removed, local_count, assembler_changed


def verify_clean() -> None:
    registry = load(SHOW / "direction.json")
    required = set(CORE_DIRECTIONS)
    missing = required - set(registry)
    if missing:
        raise RuntimeError(f"Missing persistent Azure Reach directions: {sorted(missing)}")

    total = 0
    for path in sorted(ENCODED.glob("pages_e*.json.gzb64")):
        data = decode(path)
        for page in data:
            total += 1
            refs = page.get("direction", []) or []
            if "AZR_PRODUCTION_CORE" not in refs or "AZR_LETTERING" not in refs:
                raise RuntimeError(f"{page.get('id')}: missing persistent production refs")
            unknown = [ref for ref in refs if ref not in registry]
            if unknown:
                raise RuntimeError(f"{page.get('id')}: unknown direction refs {unknown}")
            for item in page.get("directionInline", []) or []:
                text = str(item.get("text", "")) if isinstance(item, dict) else str(item)
                if text.startswith(LEGACY_PREFIXES):
                    raise RuntimeError(f"{page.get('id')}: legacy production scaffolding remains")
                if text and not text.startswith(("PAGE CONTINUITY —", "PAGE DESIGN —")):
                    raise RuntimeError(f"{page.get('id')}: unscoped local direction {text!r}")
            local_text = json.dumps(page.get("directionInline", []), ensure_ascii=False)
            if page.get("summary") and page["summary"] in local_text:
                raise RuntimeError(f"{page.get('id')}: summary duplicated into local direction")
    if total != 132:
        raise RuntimeError(f"Expected 132 pages during verification, found {total}")

    index = INDEX.read_text(encoding="utf-8")
    marker = 'if(s.direction?.length||s.directionInline?.length){out.push("\\n[DIRECTION]")'
    if marker not in index:
        raise RuntimeError("Assembler does not combine persistent and page-local direction")


if __name__ == "__main__":
    pages, removed, locals_kept, assembler_changed = sanitize()
    print(f"Sanitized {pages} Azure Reach pages")
    print(f"Removed {removed} legacy page-scope production blocks")
    print(f"Retained {locals_kept} scoped page-local direction entries")
    print("Assembler updated" if assembler_changed else "Assembler already supports scoped directions")
