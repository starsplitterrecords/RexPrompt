#!/usr/bin/env python3
"""One-shot semantic cleanup of unearned writerly language in active RexPrompt data."""

from __future__ import annotations

import base64
import gzip
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

# These are deliberately exact, path-scoped semantic rewrites.  They do not ban
# vocabulary.  Legitimate in-world legal/media/technical language and the
# intentionally sparse literary caption voice in Low Tide Signal are preserved.
RULES = {
    "rex-fleet-s1": {
        "She has bait. You dying does not turn it into mercy.": "She's baiting you. Dying for it won't help anyone.",
        "Auric gets the consequences. The Core gets your conscience.": "Auric lives with what happened. You get to leave and explain it.",
        "The truth before the promise.": "Tell them what we know before we tell them what we can do.",
        "Truth is not self-executing.": "If you say it plainly, they'll use it against you before anyone else hears it.",
        "They called these shortages. They were choices.": "They called them shortages. The logs show who was denied power and when.",
        "Still cleaning up Abby's conscience?": "Still cleaning up Abby's mess?",
        "No witness belongs to a government.": "Nobody who testified gets handed back to a government that wants them.",
        "Truth first.": "Tell them what actually happened first.",
        "That sounded like a lie with a witness.": "You're asking me to say that in front of the person who knows it isn't true.",
        "The riot is a logistics problem before it is a political metaphor.": "Treat the riot first as a physical crowd-control and supply problem: bodies, exits, bottlenecks, heat, water, and movement.",
        "without dramatic foreshadowing": "without visually telegraphing the attack in advance",
        "Kerr is an ally, not a coward; Venn chooses moral clarity over acquittal.": "Kerr is trying to keep Venn from being stripped of command; Venn rejects the prepared defense and enters without notes.",
        "Both Halev and Dain are morally serious; his inability to name who pays is the turn.": "Halev wants more shelter opened; Dain forces him to identify which already-crowded district will lose heat or space to make that possible.",
        "The tribunal produces immediate human consequences.": "As the withdrawal order lands, Thunderbreak moves beyond the boundary and the clinic loses Fleet power.",
        "Distrust changes into provisional coexistence through action.": "The families share blankets, heater space, and medical help despite visible distrust.",
        "End with restrained intimacy and political consequence; Venn has lost rank, not agency.": "End with Venn and Naomi keeping physical distance while Venn commits to returning; Venn is no longer in command but still makes her own decision.",
    },
    "echoes-forgotten-war-s1": {
        "Both of you stop trying to make the other one wrong.": "Stop. You saw different parts of it.",
        "Because some things only stop when somebody does.": "Because if nobody stops it, it keeps spreading.",
        "And every time you cut it short.": "And every time you move before the evacuation is finished.",
        "Every time you mistake delay for mercy.": "Because every delay gives it more time to spread.",
        "Every time you mistake an ending for a solution.": "And every strike leaves people inside the blast.",
        "Do either of you remember how to speak to each other without a battlefield between you?": "Can either of you talk for one minute without turning this into the last fight?",
        "I used to trust you to know the difference between courage and impatience.": "I used to trust you to know when you were moving too soon.",
        "That's how this war keeps us.": "And that's why the two of you keep ending up back here.",
        "Because a day doesn't belong to one person.": "Because you weren't standing in the same place.",
        "You don't get to make them debris because that is easier to manage.": "They're people, Adrian. Stop talking about them like wreckage.",
        "Who built their life on top of it.": "Ask who lives above it now.",
        "Neither is calling every refusal mercy.": "Refusing the order doesn't make the danger go away.",
        "I will live with it if I choose it. I will also live with what happens if I don't.": "If I give the order, those deaths are mine. If I refuse and this spreads, those deaths are mine too.",
        "You don't get to call responsibility redemption.": "Taking responsibility now doesn't make what you did right.",
        "Rae's ancient position should foreshadow her present solution.": "In the ancient scenes, keep Rae close enough to Arbiter to witness and record the rulings.",
        "Atlas's theme lands through present people surviving, not": "Keep Atlas's influence visible through present-day rescue choices and people surviving, not",
        "Formal Payoff: Past and present compositions merge.": "Final visual: match past and present compositions so the modern rescue repeats specific physical gestures from the ancient sequence.",
    },
    "division-threshold-s1": {
        "I gave them the truth.": "I told them exactly what happened.",
        "I said we weren't them. I was right about the biology.": "I said we were biologically different. That part was true.",
        "I was wrong about what that protected.": "I was wrong that the difference would keep the same rules from reaching us.",
        "They made my choice into evidence against my choices.": "I chose once, and now they're using that to narrow what I'm allowed to choose next.",
        "You do not require broader authority. You require standing.": "You already have the legal power. What you lack is a way to make anyone answer for ignoring you.",
        "Truth doesn't get safer while we wait.": "Waiting won't make the evidence easier to defend.",
        "We stop asking permission from systems built to classify us.": "Then we stop routing every appeal through the same system that flagged us.",
        "Tell me what you know. Don't turn knowing into permission.": "Tell me what you know. Don't make me file a request just to hear it.",
        "Regulate the consequence. Not the category.": "If something is dangerous, regulate that. Stop regulating the label.",
        "A decision without consequence is not authority.": "If nobody is bound by the ruling, then I am not actually deciding anything.",
        "Allow emotional weight. This reform matters even though the story knows its cost.": "Let the affected Organics react to the legal recognition before the immediate administrative cost arrives.",
        "State the season mechanism through character recognition, not exposition about theme.": "Have the characters identify the repeated policy mechanism from the evidence in front of them; do not add abstract explanatory dialogue.",
        "Axiom's personhood theme is consequence and accountable agency, not freedom from rules.": "Show Axiom treating personhood as responsibility for decisions: she accepts review, names the consequences of her choices, and does not claim exemption from rules.",
        "Nathan's payoff is shared care, not cure or heroic self-sacrifice.": "Nathan remains impaired; John and the others share the practical work of caring for him rather than resolving his condition through sacrifice.",
        "character-specific page buttons": "character actions, decisions, or discoveries that visibly change what follows",
        "setup/payoff map": "continuity and dependency map",
    },
    "azure-reach-s1": {
        "We find meaning performs very well when properly managed.": "Guests respond better when we give the experience a clear takeaway.",
        "Typography can carry truth.": "Put the actual restriction in type people can read.",
        "Make the person exclusive, not the water.": "Sell the private guide time. Leave the water access the same.",
        "Safety is very photogenic when you light it correctly.": "The safer layout photographs better too.",
        "The less exclusive version.": "The version that doesn't shut everyone else out.",
        "We made exclusivity work by excluding fewer people.": "We kept the premium tier and opened the water access to everyone else.",
        "I can make honesty cinematic.": "Give me the real safety message. I can still make it look good.",
        "The turtle-helmet kid states the clearest version of the theme.": "The turtle-helmet kid asks whether the event is about 'leaving them alone better,' and the adults recognize that he understood the care rule.",
        "Page feel: Backstage decompression; Tuesday payoff setup. Key image: Sea-turtle cupcakes in the break area after a successful day.": "Page feel: Backstage decompression after the successful event. Key image: sea-turtle cupcakes in the break area while the exhausted staff begin joking about doing it again on Tuesday.",
        "Page feel: Hard corporate button wind-up. Key image: Beatrice reads SHELLABRATION SATURDAYS while everyone freezes.": "End on Beatrice reading SHELLABRATION SATURDAYS while everyone freezes.",
        "Page feel: Found-family button; sunset; absurdity continues. Key image: Maya walks away privately smiling as the glowing park remains beautiful and ridiculous.": "At sunset, show the staff relaxed together at the loading-dock edge; Maya walks away privately smiling while the park still glows in the distance.",
        "FULL-WIDTH BOTTOM COMEDY BUTTON": "FULL-WIDTH BOTTOM COMEDY PANEL",
        "FULL-WIDTH BOTTOM BUTTON": "FULL-WIDTH BOTTOM PANEL",
        "WIDE BOTTOM CHARACTER BUTTON": "WIDE BOTTOM CHARACTER PANEL",
        "QUIET WIDE PAYOFF": "QUIET WIDE PANEL",
        "WIDE OBSERVATIONAL PAYOFF": "WIDE OBSERVATIONAL PANEL",
        "7. BUTTON:": "7. FINAL PANEL:",
        "accurate callbacks to the season's earlier public misunderstandings": "the same guest questions and corrections established earlier in the season, now handled accurately",
    },
    "stardust-station": {
        "A routine is a promise the group makes before it is frightened.": "A routine is what people can still follow when they're frightened.",
        "You just built yourself six exits from responsibility.": "You just gave yourself six ways to deny this later.",
        "When something goes wrong, ambiguity becomes memory, then memory becomes blame. Categories keep the blame from breeding.": "When something goes wrong and we don't label it, everyone remembers it differently and the blame starts moving.",
        "So one of you protects people from uncertainty. One protects them from process.": "So Glorp wants everyone to know exactly what happened, and Kreeb wants people to be able to object to how it's classified.",
        "a callback that proves she has learned Astra's language without becoming less honest": "Mira deliberately reuses Astra's preferred wording while remaining factually honest",
        "a callback to Page 3 that shows mutual adaptation rather than simple contradiction": "the wording Astra preferred on Page 3, showing that Mira has adjusted how she communicates without hiding the fact",
        "before the metaphor can become larger than the repair": "and redirects attention to the physical repair",
        "Zib / Jax practical payoff": "Zib / Jax practical resolution",
        "The initiative's real payoff is a montage of ordinary fixes and reconciled process conflicts.": "Show a montage of ordinary fixes and reconciled process conflicts produced by the initiative.",
    },
    "backyard-rockets-s1": {
        "Probably is what power says when it is tired of asking.": "We don't launch on probably. We wait for them to answer.",
        "The reservoir was never empty. Access was. The water is scarce; the truth does not have to be.": "The reservoir was never empty. Public access was shut. Those are different facts.",
        "establish consent before the launch rather than making it a later theme.": "show the community's permission before launch; do not postpone the consent decision to a later page.",
        "Treat the jamming as an action sequence with a conceptual payoff. The crew loses communications but not local safety. The visual climax is wells continuing safely without Launch-Shop, proving the network has become less dependent on its creators.": "Treat the jamming as an action sequence. The crew loses communications but not local safety. End on wells continuing within local limits without Launch-Shop, showing the network can now operate safely without them.",
    },
    "vikings-2026-s1": {
        "Same place. Different meaning.": "So 'contested' doesn't mean what we think it means here.",
        "The city is not a wall. It is many small permissions.": "You don't enter this city once, Bjorn. You keep getting permission: train, building, account, room.",
        "This is the issue’s central object payoff. Use a real scratched brass apartment key, not ornate fantasy metalwork.": "Use a real scratched brass apartment key, not ornate fantasy metalwork. Bjorn should handle it as an ordinary object that now gives him a concrete obligation and a place to return to.",
        "This is the issue's central object payoff. Use a real scratched brass apartment key, not ornate fantasy metalwork.": "Use a real scratched brass apartment key, not ornate fantasy metalwork. Bjorn should handle it as an ordinary object that now gives him a concrete obligation and a place to return to.",
        "This foreshadows later administrative competence without making him modern overnight.": "His attention should be on the reciprocal terms and the practical responsibility they create; do not make him seem fully adapted to modern bureaucracy yet.",
        "Final image must make the story change visible: this is no longer a bare municipal placement. It is a small household with obligations, boundaries, heat, privacy and a deadline.": "Final image: the apartment now contains the concrete signs of a small household with obligations, boundaries, heat, privacy, and a deadline rather than a bare municipal placement.",
        "Carrie warns Bjorn off the metaphor while Gunnar notices": "Carrie tells Bjorn to stay with the literal problem while Gunnar notices",
        "Callback earlier station language:": "Reuse the earlier station language:",
        "Seed Kin independent adaptation visually without explaining the late-season payoff.": "Show Kin independently navigating modern systems in small practical ways without explanatory dialogue.",
    },
    "low-tide-signal": {
        "the theme: nobody actually leaves anymore.": "the practical reality: nobody actually leaves anymore.",
        "No lead should function only as a theme delivery system.": "Every lead needs a concrete personal reason for going, staying, helping, or resisting.",
        "Theme should live in behavior, jokes, habits, missed timing,": "Character differences should show through behavior, jokes, habits, missed timing,",
        "no theme speeches": "no abstract speeches explaining what the Reach means",
        "theme speeches": "abstract speeches explaining what the Reach means",
    },
    "sun-comes-through-musical-s1": {
        "The unfinished score is the concrete payoff to Figure It Out.": "End on the unfinished score as a physical result of Alex choosing to stay present instead of completing the performance alone.",
    },
}


def decode_gzb64(text: str):
    raw = re.sub(r"\s+", "", text).rstrip("=")
    raw += "=" * ((4 - len(raw) % 4) % 4)
    return json.loads(gzip.decompress(base64.b64decode(raw)).decode("utf-8"))


def encode_gzb64(data) -> str:
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return base64.b64encode(gzip.compress(payload, mtime=0)).decode("ascii")


def replace_text(value: str, rules: dict[str, str], counts: dict[str, int]) -> str:
    out = value
    for old, new in rules.items():
        if old in out:
            n = out.count(old)
            out = out.replace(old, new)
            counts[old] = counts.get(old, 0) + n
    return out


def replace_strings(obj, rules, counts):
    if isinstance(obj, dict):
        for key, value in list(obj.items()):
            if isinstance(value, str):
                obj[key] = replace_text(value, rules, counts)
            else:
                replace_strings(value, rules, counts)
    elif isinstance(obj, list):
        for idx, value in enumerate(obj):
            if isinstance(value, str):
                obj[idx] = replace_text(value, rules, counts)
            else:
                replace_strings(value, rules, counts)


def matching_rules(path: pathlib.Path) -> dict[str, str]:
    rel = path.relative_to(DATA).as_posix()
    merged: dict[str, str] = {}
    for marker, rules in RULES.items():
        if marker in rel:
            merged.update(rules)
    return merged


def main():
    changed_files: list[str] = []
    total_counts: dict[str, int] = {}

    for path in sorted(DATA.rglob("*")):
        if not path.is_file():
            continue
        rel_parts = set(path.relative_to(DATA).parts)
        if {"source", "raw", "archive"} & rel_parts:
            continue
        rules = matching_rules(path)
        if not rules:
            continue

        original = path.read_text(encoding="utf-8")
        counts: dict[str, int] = {}

        if path.name.endswith(".json.gzb64"):
            try:
                data = decode_gzb64(original)
            except Exception:
                continue
            replace_strings(data, rules, counts)
            if counts:
                path.write_text(encode_gzb64(data), encoding="utf-8")
        elif path.suffix == ".json":
            rendered = original
            for old, new in rules.items():
                if old in rendered:
                    n = rendered.count(old)
                    rendered = rendered.replace(old, new)
                    counts[old] = counts.get(old, 0) + n
            if counts:
                json.loads(rendered)
                path.write_text(rendered, encoding="utf-8")
        else:
            continue

        if counts:
            changed_files.append(path.relative_to(ROOT).as_posix())
            for old, n in counts.items():
                total_counts[old] = total_counts.get(old, 0) + n

    print(f"Changed {len(changed_files)} files.")
    for rel in changed_files:
        print(f"  {rel}")
    print(f"Applied {sum(total_counts.values())} replacements across {len(total_counts)} matched patterns.")
    print("Matched patterns:")
    for old, n in sorted(total_counts.items()):
        print(f"  {n} x {old}")
    print("Unmatched candidates (review manually if still present in assembled output):")
    for marker, rules in RULES.items():
        for old in rules:
            if old not in total_counts:
                print(f"  {marker}: {old}")

    if not changed_files:
        raise SystemExit("No writerly-language candidates matched active data")


if __name__ == "__main__":
    main()
