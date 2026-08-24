#!/usr/bin/env python3
"""Semantically sanitize Echoes of a Forgotten War RexPrompt data.

Preserves authored story, dialogue, scene order, reveal order, and intentional
staging while removing duplicated production scaffolding, stale correction
history, and identity/behavior prose stored at the wrong scope.

The migration is intentionally idempotent.
"""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data" / "shows" / "echoes-forgotten-war-s1"
MANIFEST = ROOT / "data" / "shows.json"

SCENE_FILES = [SHOW / f"scenes_e{i:02d}.json" for i in range(1, 9)]

SHOW_ENTRY = {
    "id": "echoes-forgotten-war-s1",
    "name": "Echoes of a Forgotten War — Season 1",
    "basePath": "data/shows/echoes-forgotten-war-s1",
    "scenesFiles": [f"scenes_e{i:02d}.json" for i in range(1, 9)],
    "unitLabel": "SCENE",
    "generationLine": (
        "Prestige cosmic science-fiction graphic-novel scenes grounded in human-scale acting "
        "and clear physical storytelling. Erased history returns through memory, matter, "
        "institutions and relationships; mythic scale appears through consequence and lived "
        "experience rather than technical explanation. Fictional production."
    ),
}

POSITIVE_SETTINGS = {
    "EFW_OlyriaTrench": "Working excavation cut into black bedrock on Olyria-Prime; heavy drills, work lamps, dust, ladders, shift gear and tired crews.",
    "EFW_ZenithArchives": "Institutional archive high in Zenith Spire; ordered shelves, old ledgers, current records, secure desks and long views over the planet.",
    "EFW_SectorFour": "Newly opened excavation section where the Desert Marker emerges from black bedrock amid work platforms, dust and temporary lighting.",
    "EFW_GridRuins": "Damaged excavation tier after the first memory rupture, with broken platforms, dust, abandoned tools and stunned workers.",
    "EFW_TelemetryRoom": "Secure Zenith records room with controlled access, workstations, archive terminals and institutional oversight.",
    "EFW_TriageTent": "Temporary field medical tent with cots, paper forms, ordinary supplies, tired workers and bad coffee.",
    "EFW_LowerArchives": "Older archive stacks beneath the polished public levels, filled with physical books, sealed records and infrequently used storage rooms.",
    "EFW_ObservationDeck": "High-altitude observation deck overlooking Zenith Spire and the planet below, with quiet public space and ordinary disposal infrastructure.",
    "EFW_AbandonedTrench": "Shut-down excavation cut with sparse work lights, scrap, deep shadow and enough loose material to conceal the reopened site.",
    "EFW_CompactedEarth": "Surface above buried Sector Four beneath silent excavators and open stars, exposed and still after the work crews leave."
}

POSITIVE_REGIONS = {
    "EFW_OlyriaPrime": "Industrial excavation colony organized around deep field cuts, worker support spaces and survey infrastructure.",
    "EFW_ZenithSpire": "Administrative and archival center where institutional authority is expressed through controlled access, sealed records and elevated public spaces."
}

REVEAL_ORDER = ["Starbreaker", "Redlin", "Atlas", "Arbiter", "Afterlight", "Flux", "Oryon", "Kyn"]

TECHNICAL_MARKERS = (
    "readout", "diagnostic", "scanner", "measurement", "instrumentation",
    "engineering", "technical explanation", "technical language", "mechanism",
    "hologram", "probability jargon", "pseudo-scientific", "invented physics",
    "tolerance", "percentage", "percent", "frequency", "calibration",
)

META_STARTS = (
    "this is the reader's clearest experience",
    "this is the first time the reader",
    "this is the clue",
    "this is the finale",
    "this is the causal climax",
    "this is the ensemble payoff",
    "this is ancient adrian's full reveal",
    "this is atlas's debut",
    "this is arbiter's human center",
    "seed the finale",
    "issue 7 will",
    "issue 8 will",
    "the series should",
)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    return re.split(r"(?<=[.!?])\s+(?=[A-Z0-9@\"'“])", text)


def is_scaffolding_sentence(sentence: str) -> bool:
    lower = sentence.strip().lower()
    if not lower:
        return True
    if any(lower.startswith(prefix) for prefix in META_STARTS):
        return True

    directive = lower.startswith(("do not ", "don't ", "avoid ", "strip all ", "no "))
    if directive and any(marker in lower for marker in TECHNICAL_MARKERS):
        return True

    if ("ancient theo" in lower or "ancient rae" in lower) and lower.startswith(("do not ", "don't ", "no ")):
        return True
    if lower.startswith("do not show redlin"):
        return True
    if lower.startswith("do not reveal") and any(term in lower for term in ("ancient", "identity", "midpoint")):
        return True
    return False


def clean_direction_text(text: str) -> str:
    kept = [s.strip() for s in split_sentences(text) if not is_scaffolding_sentence(s)]
    return " ".join(kept).strip()


def story_fingerprint(scene: dict) -> dict:
    """Everything except directionInline must remain byte-equivalent as data."""
    return {k: copy.deepcopy(v) for k, v in scene.items() if k != "directionInline"}


def sanitize_scenes() -> tuple[int, int]:
    scene_count = 0
    removed_sentences = 0
    for path in SCENE_FILES:
        scenes = load(path)
        if not isinstance(scenes, list):
            raise RuntimeError(f"Expected scene list: {path}")
        before = [story_fingerprint(scene) for scene in scenes]
        for scene in scenes:
            scene_count += 1
            blocks = scene.get("directionInline")
            if not blocks:
                continue
            cleaned_blocks = []
            for block in blocks:
                if not isinstance(block, dict) or not isinstance(block.get("text"), str):
                    cleaned_blocks.append(block)
                    continue
                original = block["text"]
                cleaned = clean_direction_text(original)
                removed_sentences += max(0, len(split_sentences(original)) - len(split_sentences(cleaned)))
                if cleaned:
                    new_block = copy.deepcopy(block)
                    new_block["text"] = cleaned
                    cleaned_blocks.append(new_block)
            if cleaned_blocks:
                scene["directionInline"] = cleaned_blocks
            else:
                scene.pop("directionInline", None)
        after = [story_fingerprint(scene) for scene in scenes]
        if before != after:
            raise RuntimeError(f"Story fingerprint changed in {path.name}")
        dump(path, scenes)
    return scene_count, removed_sentences


def sanitize_direction_dictionary() -> int:
    path = SHOW / "direction.json"
    data = load(path)
    removed = 0
    for entry in data.values():
        if not isinstance(entry, dict) or not isinstance(entry.get("text"), str):
            continue
        original = entry["text"]
        cleaned = clean_direction_text(original)
        removed += max(0, len(split_sentences(original)) - len(split_sentences(cleaned)))
        entry["text"] = cleaned
    dump(path, data)
    return removed


def sanitize_characters() -> int:
    path = SHOW / "characters.json"
    data = load(path)
    removed = 0
    for key, entry in list(data.items()):
        if not isinstance(entry, dict):
            continue
        keep = {k: entry[k] for k in ("name", "handle", "role") if entry.get(k)}
        removed += len(entry) - len(keep)
        data[key] = keep
    dump(path, data)
    return removed


def sanitize_settings_and_regions() -> None:
    settings_path = SHOW / "settings.json"
    settings = load(settings_path)
    for key, text in POSITIVE_SETTINGS.items():
        if key not in settings:
            raise RuntimeError(f"Missing expected setting {key}")
        settings[key]["text"] = text
    dump(settings_path, settings)

    regions_path = SHOW / "regions.json"
    regions = load(regions_path)
    for key, text in POSITIVE_REGIONS.items():
        if key not in regions:
            raise RuntimeError(f"Missing expected region {key}")
        regions[key]["text"] = text
    dump(regions_path, regions)


def sanitize_revision_charter() -> None:
    data = {
        "series": "Echoes of a Forgotten War",
        "mode": "enhance",
        "storyRule": "Each discovery advances what is returning, who the ancient people were, what they chose, or what restored continuity could cost.",
        "phenomenonLanguage": "Ancient phenomena are described through observable consequence, recognition, memory, atmosphere and character reaction. Ordinary practical measurements appear only when immediate action genuinely requires them.",
        "historicalDrama": "Memory vignettes are complete dramatic scenes driven by personal wants, relationships, grief, affection, rivalry, judgment and consequence.",
        "humanScale": "Ordinary work, fatigue, humor, irritation, care, silence and mundane objects provide contrast for cosmic events.",
        "spectacle": "Recurring mythic imagery is reserved for meaningful turns so large events retain scale and impact.",
        "voiceScope": "Durable character voice and psychology live in Notion's Echoes character reference; RexPrompt character records carry production identity and role only.",
        "revealStructure": {
            "champions": REVEAL_ORDER,
            "ancientTheoRae": "Their remembered physical presence becomes visible only after Adrian's Issue 4 identity reveal.",
            "form": "Distinct past/present structures progressively converge through Issues 5–8."
        },
        "continuityTest": "A scene must change knowledge, relationship, choice, consequence or present-day state; anomaly behavior alone is not a dramatic turn."
    }
    dump(SHOW / "revision_charter.json", data)


def sanitize_identity_reset() -> None:
    data = {
        "series": "Echoes of a Forgotten War",
        "status": "locked",
        "identityRule": "Theo and Rae are literally the same people who lived during the forgotten war; their present lives continue those same identities across the Reset.",
        "resetEffect": "The Reset severed lived identity from historical continuity, removing the connective sense of 'I was there' and 'I did this' while people, matter, consequences and reality remained.",
        "apparentHistory": "Reality healed around the erased history and produced a coherent apparent continuity, so the forgotten war can seem vastly ancient even though its participants still exist in the present.",
        "earlyMemoryGrammar": "Through Issue 4, Theo and Rae experience complete historical scenes without their remembered selves attached, so the memories read as recovered history rather than autobiography.",
        "midpointReveal": "At the end of Issue 4, Adrian reveals that Theo served Mero and Rae served Arbiter during the forgotten war.",
        "revisitRule": "From Issue 5 onward, earlier memories reopen from wider or continuing angles and reveal Theo or Rae inside scenes the reader already knows; each revisit adds new dramatic information.",
        "secondHalfEscalation": ["I was there.", "I knew these people.", "I made choices there.", "The present is presenting the same moral choice again."],
        "adrianFunction": "Adrian remembers more because of his role in the Reset and withholds continuity from Theo and Rae as an ethical and personal choice.",
        "consequenceOfReturn": "As replacement history fails, people, places, institutions and relationships can recover contradictory lived histories, including different loyalties, loves, losses, origins and remembered selves.",
        "mysteryFocus": "The Reset is understood through what was erased, who made the choice, what survived, and what restored continuity changes in the present.",
        "formEscalation": "Past and present begin clearly separated, move through split issues and shorter intercuts, alternate at page scale in Issue 7, and converge in Issue 8."
    }
    dump(SHOW / "identity_reset.json", data)


def sanitize_warrior_gods() -> None:
    path = SHOW / "warrior_gods.json"
    data = load(path)
    data["status"] = "current-development-reference"
    data["storyFunction"] = "The ancient champions form a second dramatic cast whose relationships and choices reveal the forgotten war through memory scenes."
    data["revealRule"] = "One previously unseen champion is fully introduced per issue in this order: " + " → ".join(REVEAL_ORDER) + ". Previously introduced champions may recur."
    data["interactionRule"] = "Early issues present the ancient story as recovered history. Theo and Rae's autobiographical presence becomes visible after Adrian's Issue 4 reveal."
    data.pop("memoryBearers", None)

    for name, entry in (data.get("characters") or {}).items():
        if not isinstance(entry, dict):
            continue
        entry.pop("visualDevelopment", None)
        entry.pop("developmentGap", None)
        entry.pop("nameNote", None)
        entry.pop("constraint", None)
        entry.pop("historyNote", None)
        entry.pop("relationships", None)
        if name == "General Mero":
            entry["nature"] = "Human general serving among cosmic champions."
        if name == "Kyn":
            entry["identity"] = "Individual empath who experiences suffering at civilization scale."

    data["unresolved"] = [
        "Flux's disappearance before the Reset remains unexplained.",
        "Regent is historically real but remains unrevealed in the first eight issues.",
        "The exact personal betrayal associated with the Desert Marker remains unresolved.",
        "Later arcs must determine how uneven restored continuity reshapes societies without erasing the reality of present lives."
    ]
    dump(path, data)


def sanitize_relationships() -> None:
    path = SHOW / "ancient_relationships_v1.json"
    data = load(path)
    if "rule" in data:
        data["relationshipPrinciple"] = "Ancient ideology is expressed through existing relationships, immediate personal wants and accumulated history."
        data.pop("rule", None)
    for rel in data.get("relationships", []):
        if isinstance(rel, dict):
            rel.pop("revealRule", None)
    data["scenePrinciple"] = "Write the immediate personal want first, relationship history second and ideological disagreement third."
    data.pop("sceneRule", None)
    dump(path, data)


def sanitize_timeline() -> None:
    path = SHOW / "ancient_war_timeline_v1.json"
    data = load(path)
    data.pop("rule", None)
    data["purpose"] = "Causal chronology of the ancient war used by the eight-issue memory structure."
    data["unresolved"] = [
        "The exact personal betrayal associated with the Desert Marker remains unresolved.",
        "Flux's disappearance remains intentionally unexplained.",
        "Regent is historically real but its decisive later-arc event remains undeveloped.",
        "Theo's and Rae's final ancient choices are revealed through the scripted second half rather than summarized ahead of the story."
    ]
    dump(path, data)


def sanitize_season_architecture() -> None:
    path = SHOW / "season_architecture_v2.json"
    data = load(path)
    data["status"] = "current working architecture"
    for entry in data.get("revealOrder", []):
        if isinstance(entry, dict):
            entry.pop("basis", None)
    dump(path, data)


def sanitize_page_spine() -> None:
    path = SHOW / "comic_page_spine_v1.json"
    data = load(path)
    data["globalRules"] = [
        "Readability first, scale second, spectacle third.",
        "Early memory transitions remain unmistakable; later issues allow the visual grammar to become increasingly implicit.",
        "Ancient Theo and Rae become visible only after the Issue 4 identity reveal.",
        "Champion debuts receive enough page space to establish personality and relationship.",
        "Page turns prioritize changed meaning, character revelation and consequence.",
        "Issue 7 uses deliberate present/past page alternation; Issue 8 progressively converges those structures."
    ]
    for issue in data.get("issues", []):
        for page in issue.get("pages", []):
            for field in ("beat", "turn"):
                value = page.get(field)
                if isinstance(value, str):
                    cleaned = clean_direction_text(value)
                    if cleaned:
                        page[field] = cleaned
    dump(path, data)


def sanitize_development_status() -> None:
    path = SHOW / "development_status.json"
    data = load(path)
    data["status"] = "sanitized working season architecture; eight issue-level scene drafts active; graphic-novel page scripting next"
    data.pop("supersededMaterial", None)
    data["sanitization"] = {
        "state": "clean",
        "storyPreserved": True,
        "dialoguePreserved": True,
        "scope": "Persistent identity and behavioral truth is kept in Notion/reference architecture; scene files retain story-specific action, dialogue and staging."
    }
    dump(path, data)


def sanitize_manifest() -> None:
    data = load(MANIFEST)
    if not isinstance(data, list):
        raise RuntimeError("data/shows.json must be a list")
    data = [entry for entry in data if entry.get("id") != SHOW_ENTRY["id"]]
    data.append(copy.deepcopy(SHOW_ENTRY))
    dump(MANIFEST, data)


def verify_clean() -> None:
    chars = load(SHOW / "characters.json")
    for key, entry in chars.items():
        if isinstance(entry, dict) and "notes" in entry:
            raise RuntimeError(f"Character behavior prose remains in RexPrompt registry: {key}")

    scan_paths = [SHOW / "direction.json", SHOW / "settings.json", SHOW / "revision_charter.json", SHOW / "warrior_gods.json"] + SCENE_FILES
    forbidden = (
        "engineering-tolerance", "pseudo-technical teleplay", "earlier 'redline' spelling was rejected",
        "reveal order was not recovered", "floating tactical diagrams", "interactive hologram",
        "invented physics", "diagnostic readout"
    )
    for path in scan_paths:
        text = path.read_text(encoding="utf-8").lower()
        for term in forbidden:
            if term in text:
                raise RuntimeError(f"Sanitization residue {term!r} remains in {path.name}")

    architecture = load(SHOW / "season_architecture_v2.json")
    order = [entry.get("newChampion") for entry in architecture.get("revealOrder", [])]
    if order != REVEAL_ORDER:
        raise RuntimeError(f"Champion reveal order changed: {order!r}")

    scenes = []
    for path in SCENE_FILES:
        payload = load(path)
        if len(payload) != 12:
            raise RuntimeError(f"Expected 12 scenes in {path.name}, found {len(payload)}")
        scenes.extend(payload)
    ids = [scene.get("id") for scene in scenes]
    if len(ids) != 96 or len(set(ids)) != 96:
        raise RuntimeError("Echoes scene count or IDs changed during sanitization")

    manifest = load(MANIFEST)
    matches = [entry for entry in manifest if entry.get("id") == SHOW_ENTRY["id"]]
    if len(matches) != 1 or matches[0].get("scenesFiles") != SHOW_ENTRY["scenesFiles"]:
        raise RuntimeError("Echoes manifest registration is missing or malformed")


if __name__ == "__main__":
    scene_count, scene_removed = sanitize_scenes()
    dict_removed = sanitize_direction_dictionary()
    character_removed = sanitize_characters()
    sanitize_settings_and_regions()
    sanitize_revision_charter()
    sanitize_identity_reset()
    sanitize_warrior_gods()
    sanitize_relationships()
    sanitize_timeline()
    sanitize_season_architecture()
    sanitize_page_spine()
    sanitize_development_status()
    sanitize_manifest()
    verify_clean()
    print(f"Sanitized {scene_count} Echoes scenes")
    print(f"Removed {scene_removed + dict_removed} repeated/meta direction sentences")
    print(f"Removed {character_removed} character-scope fields from RexPrompt registry")
