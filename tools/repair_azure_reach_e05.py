#!/usr/bin/env python3
import base64
import gzip
import json
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data/shows/azure-reach-s1/encoded/pages_e05.json.gzb64"

HANDLE_NAMES = {
    "@azr.Maya": "Maya Serrano",
    "@azr.Julian": "Julian Heatherington",
    "@azr.Fleur": "Fleur Fontaine",
    "@azr.Pip": "Pip O'Mally",
    "@azr.Sal": "Sal Delgado",
    "@azr.Beatrice": "Beatrice Halstead",
    "@azr.Kyler": "Kyler Chen",
    "@azr.Dora": "Dr. Dora Kwon",
    "@azr.Elliot": "Elliot Richards",
    "@azr.Nia": "Nia Patel",
    "@azr.Raf": "Raf Morales",
    "@azr.Sponsor": "Sponsor Representative",
    "@azr.Educator": "Staff Educator",
    "@azr.Child": "Child",
    "@azr.Everyone": "Everyone",
}

VISUAL_LOCK = (
    "AZURE REACH VISUAL LANGUAGE: Bright aquatic contemporary workplace comedy; glossy public spaces and clean competent backstage areas. "
    "Preserve the established blue-forward palette and role-specific visual language. Keep every animal presence safe, calm, voluntary, and secondary to the workplace conflict."
)
CHARACTER_LOCK = (
    "CHARACTER CONTINUITY — Preserve established faces, hair, uniforms, role-specific props, relative scale, and workplace-group visual distinctions. "
    "Maya remains dark-navy operational gravity and must never visually merge with Pip or the public-facing staff."
)
LOCATION_LOCK = (
    "LOCATION / PROP / STATE CONTINUITY — Preserve Conservation Week signage, the optional physical/digital participation system, traffic state, dashboards, counters, and carried props from the preceding page."
)
LETTERING_LOCK = (
    "COMIC PAGE / LETTERING — Use a varied, readable modern prestige-comic layout with intentional negative space. Use clean professional integrated lettering, preserve exact dialogue, keep balloon order unambiguous, and do not duplicate text."
)


def decode_b64(text):
    raw = "".join(text.split())
    raw += "=" * (-len(raw) % 4)
    return base64.b64decode(raw, validate=True)


def gzip_payload_start(data):
    if data[:3] != b"\x1f\x8b\x08":
        raise SystemExit("Issue 5 payload is not gzip data")
    flags = data[3]
    pos = 10
    if flags & 0x04:
        xlen = int.from_bytes(data[pos:pos + 2], "little")
        pos += 2 + xlen
    for bit in (0x08, 0x10):
        if flags & bit:
            end = data.index(0, pos)
            pos = end + 1
    if flags & 0x02:
        pos += 2
    return pos


def raw_deflate_text(data):
    start = gzip_payload_start(data)
    dec = zlib.decompressobj(-zlib.MAX_WBITS)
    recovered = dec.decompress(data[start:]) + dec.flush()
    if not dec.eof:
        raise SystemExit("Issue 5 DEFLATE stream is incomplete; cannot repair safely")
    return recovered.decode("utf-8")


def line(handle, text):
    return {"speaker": HANDLE_NAMES[handle], "handle": handle, "text": text}


def panel(text):
    return {"text": text}


def page(number, title, setting, factions, summary, panels, dialogue):
    handles = []
    for d in dialogue:
        if d["handle"] not in handles:
            handles.append(d["handle"])
    return {
        "id": f"AZR_S1E05_P{number:02d}",
        "episode": "S1E05",
        "issue": "Issue #5 — Conservation Week",
        "page": number,
        "pageTitle": title,
        "panelCount": len(panels),
        "summary": summary,
        "setting": setting,
        "region": "AZR_MarinePark",
        "factions": factions,
        "charactersInline": [{"name": HANDLE_NAMES[h], "handle": h} for h in handles],
        "panelPlan": [panel(p) for p in panels],
        "dialogueInline": dialogue,
        "directionInline": [
            {"text": VISUAL_LOCK},
            {"text": "PAGE ACTION — SOURCE-LOCKED: " + summary},
            {"text": CHARACTER_LOCK},
            {"text": LOCATION_LOCK},
            {"text": LETTERING_LOCK},
        ],
    }


def replacement_pages():
    specs = []
    specs.append(page(
        10, "Default", "AZR_FoodCourt", ["AZR_GuestRelations", "AZR_Finfluencers"],
        "Raf and Nia redesign several conservation actions as default park operations, reducing guest effort while making verification cleaner and more defensible.",
        [
            "Nia studies the paper passport and app screen beside Raf's normal refill register flow; the redundant confirmation step is visibly the problem.",
            "Raf demonstrates that the refill itself already creates a reliable transaction record without an extra guest scan.",
            "Julian arrives expecting a new activation and instead finds Nia deleting one.",
            "Kyler updates the metric mapping so the existing operational record can verify the conservation action once.",
            "The food-court line moves normally again while the Conservation Week graphics remain present but no longer obstruct the transaction.",
        ],
        [
            line("@azr.Nia", "No."),
            line("@azr.Julian", "That was faster than Maya."),
            line("@azr.Nia", "Phones die. Strollers do not become software."),
            line("@azr.Raf", "Refills already save cups. We don't need a second ceremony."),
            line("@azr.Kyler", "Then the register can verify the refill at the sale."),
            line("@azr.Julian", "So the guest does less and the number gets cleaner."),
            line("@azr.Nia", "The guest does the useful thing. We stop making them prove it twice."),
        ],
    ))
    specs.append(page(
        11, "Denominator", "AZR_OpsRoom", ["AZR_BrineSquad", "AZR_Finfluencers", "AZR_Corporate"],
        "Kyler rebuilds the dashboard around unique participants and nonduplicated actions, revealing how much of the original pace came from counting the same behavior repeatedly.",
        [
            "Kyler replaces the green headline dashboard with a plainer diagnostic view showing unique guests, verified actions and duplicate removals.",
            "Elliot points to one guest journey that had become five separate credits under the old scheme.",
            "Maya asks for staff operations to be separated from public participation before the next count is shown.",
            "Sal discovers that routine staff work had also been swept into a public-engagement bucket and waits for Kyler to notice his expression.",
            "The revised total drops sharply but each remaining number now has a clear definition.",
        ],
        [
            line("@azr.Kyler", "New denominator: unique guests, not scans."),
            line("@azr.Elliot", "And one action cannot become five because five departments saw it."),
            line("@azr.Kyler", "Cruel, but mathematically defensible."),
            line("@azr.Maya", "Can you separate public actions from staff operations?"),
            line("@azr.Kyler", "Yes."),
            line("@azr.Sal", "Then stop counting us as guests."),
            line("@azr.Kyler", "Also cruel. Also fair."),
        ],
    ))
    specs.append(page(
        12, "Two Ways In", "AZR_ConservationHub", ["AZR_GuestRelations", "AZR_Finfluencers"],
        "Nia and the education staff test one conservation action through both paper and digital paths, proving that accessibility and clean verification can coexist without forcing guests into the app.",
        [
            "The Conservation Hub now presents a paper card and an app option side by side with identical language and no hierarchy.",
            "An educator demonstrates the same activity to two guests using different participation paths.",
            "A guest holds up a nearly dead phone while Nia hands over the paper version without changing the experience.",
            "Julian quietly considers turning the moment into promotional copy; Fleur stops him with a look before he starts.",
            "Both participation paths resolve into one identical verified-action mark on Kyler's simple tally display.",
        ],
        [
            line("@azr.Nia", "Physical card or app. Same action, same credit."),
            line("@azr.Educator", "No account required?"),
            line("@azr.Nia", "Correct."),
            line("@azr.Child", "My battery's at two percent."),
            line("@azr.Nia", "Then congratulations on choosing paper."),
            line("@azr.Julian", "We should put that in the ad."),
            line("@azr.Fleur", "No. We should make it normal."),
        ],
    ))
    specs.append(page(
        13, "Show the Work", "AZR_ServiceCorridor", ["AZR_BrineSquad", "AZR_Finfluencers", "AZR_Corporate"],
        "Maya and Dora draw a firm line around animal care while Fleur identifies existing backstage systems that can carry the conservation story without changing animal behavior or adding keeper labor.",
        [
            "Maya, Sal and Dora walk the clean service corridor past ordinary water-testing and food-preparation work already scheduled for the day.",
            "Beatrice asks what Conservation Week can legitimately reveal without creating a new animal program.",
            "Sal points to the existing work rather than any habitat spectacle.",
            "Fleur frames water testing, food preparation, habitat design and waste reduction as the visual story Julian can actually use.",
            "Through the habitat glass, animals remain calm and uninvolved while the staff workflow becomes the subject of the page.",
        ],
        [
            line("@azr.Maya", "No animal behavior changes for Conservation Week."),
            line("@azr.Beatrice", "Agreed."),
            line("@azr.Sal", "No extra keeper passes either."),
            line("@azr.Julian", "What can we show?"),
            line("@azr.Dora", "The work already happening."),
            line("@azr.Fleur", "Water testing, food prep, habitat design, waste reduction."),
            line("@azr.Maya", "Interpret the system. Don't turn the animals into evidence."),
        ],
    ))
    specs.append(page(
        14, "The Headline", "AZR_GuestExperienceSuite", ["AZR_Corporate", "AZR_Finfluencers"],
        "The sponsor asks what happened to the fifty-thousand headline, and the team chooses a smaller number they can explain over a larger one they can only manufacture.",
        [
            "The sponsor representative sits with Beatrice, Elliot, Fleur and Julian in front of the original bright FIFTY THOUSAND campaign slide.",
            "Elliot places the agreement beside the slide and distinguishes the contractual requirement from the internal headline target.",
            "The sponsor asks what the public-facing result will look like if the target is missed.",
            "Fleur replaces the giant target graphic with a restrained VERIFIED ACTIONS methodology slide.",
            "Beatrice leaves the smaller truthful framing on screen rather than asking Kyler to restore the green headline number.",
        ],
        [
            line("@azr.Sponsor", "Fifty thousand was the headline."),
            line("@azr.Beatrice", "It was an internal target attached to a real program."),
            line("@azr.Elliot", "The agreement requires verified engagement."),
            line("@azr.Sponsor", "And what will the public see?"),
            line("@azr.Fleur", "A number we can explain."),
            line("@azr.Julian", "Less confetti. More credibility."),
            line("@azr.Beatrice", "That is the deck we are building."),
        ],
    ))
    specs.append(page(
        15, "Reset", "AZR_ParkPromenade", ["AZR_GuestRelations", "AZR_Finfluencers", "AZR_BrineSquad"],
        "The park relaunches Conservation Week with optional passports, automatic verification where appropriate and clear circulation, sacrificing visible conversion theater for a program that actually fits normal operations.",
        [
            "Nia removes a passport-only stanchion from the promenade and restores the clear accessible route.",
            "Raf's refill point operates normally with a small conservation mark on the receipt instead of a second scan station.",
            "Kyler watches the dashboard show fewer scans while the promenade movement improves in real time.",
            "Julian looks from the declining completion-rate tile to the visibly calmer guest flow.",
            "Sal passes through the restored route with equipment and gives the new layout an understated approval.",
        ],
        [
            line("@azr.Nia", "Passport is optional now."),
            line("@azr.Raf", "Refill credit happens at the register."),
            line("@azr.Kyler", "One scan if they want a digital record. Zero if they don't."),
            line("@azr.Julian", "Our completion rate just fell."),
            line("@azr.Nia", "Our hallway started moving."),
            line("@azr.Sal", "I vote hallway."),
            line("@azr.Julian", "Noted. Hallway is outperforming conversion."),
        ],
    ))
    specs.append(page(
        16, "A Better Question", "AZR_ConservationHub", ["AZR_GuestRelations", "AZR_BrineSquad", "AZR_Finfluencers"],
        "A child's sincere question produces the kind of sustained engagement the original stamp chase could not, giving the team a concrete example of why depth matters more than raw transaction count.",
        [
            "A child pauses at an education station while other guests can move freely around the open Conservation Hub.",
            "The educator invites a real question rather than directing the child toward a stamp or scan.",
            "The child asks where used habitat water goes, pulling Maya into the conversation from a nearby operations demonstration.",
            "Maya gives the beginning of a practical systems answer while the child leans in rather than moving to the next passport stop.",
            "Julian lowers his phone and listens, recognizing that the useful moment is the answer rather than the capture mechanic.",
        ],
        [
            line("@azr.Child", "Does asking a question count?"),
            line("@azr.Educator", "Only if you actually want the answer."),
            line("@azr.Child", "I do."),
            line("@azr.Educator", "Then yes. What do you want to know?"),
            line("@azr.Child", "Where does the old water go?"),
            line("@azr.Maya", "Now we're talking."),
            line("@azr.Julian", "That one gets the long answer."),
        ],
    ))
    specs.append(page(
        17, "The Real Number", "AZR_OpsRoom", ["AZR_Corporate", "AZR_Finfluencers", "AZR_BrineSquad"],
        "Kyler and Elliot finish the deduplicated audit at eighteen thousand four hundred twelve verified actions, forcing Beatrice to choose between the original target and the result the park can actually defend.",
        [
            "Late-day ops: Kyler's rebuilt dashboard finishes processing duplicate removals and staff/public separation.",
            "The final verified-action number settles far below the original target while every audit category remains green for integrity rather than volume.",
            "Elliot shows the unique-participant and verification definitions beside the result.",
            "Maya and Sal confirm the operational reset did not require manufactured traffic or extra animal-care work.",
            "Beatrice asks to see the underlying audit instead of requesting a different headline.",
        ],
        [
            line("@azr.Kyler", "Eighteen thousand four hundred twelve."),
            line("@azr.Beatrice", "That is not fifty thousand."),
            line("@azr.Kyler", "No. It is eighteen thousand four hundred twelve verified actions."),
            line("@azr.Elliot", "Across unique participants, with duplicates removed."),
            line("@azr.Maya", "And without manufacturing traffic."),
            line("@azr.Sal", "Or manufacturing me into a participant."),
            line("@azr.Beatrice", "Show me the audit trail."),
        ],
    ))
    specs.append(page(
        18, "Useful", "AZR_GuestExperienceSuite", ["AZR_Corporate", "AZR_Finfluencers"],
        "The sponsor reviews the smaller audited result and prefers the post-reset evidence—fewer scans, longer education dwell and stronger refill adoption—to the inflated headline total.",
        [
            "Elliot lays out the audit trail with the missed internal target visible rather than hidden in an appendix.",
            "The sponsor representative confirms there is no route back to fifty thousand without restoring duplicate counting.",
            "Fleur leaves the answer unembellished while Kyler opens the before/after operating metrics.",
            "The sponsor compares fewer scans with longer education dwell and higher refill adoption after the reset.",
            "Beatrice watches the sponsor choose the smaller useful result over the larger decorative one.",
        ],
        [
            line("@azr.Elliot", "Here."),
            line("@azr.Sponsor", "So there is no fifty thousand."),
            line("@azr.Fleur", "No."),
            line("@azr.Sponsor", "What changed after the reset?"),
            line("@azr.Kyler", "Fewer scans. Longer education stops. More refill adoption."),
            line("@azr.Beatrice", "It is smaller."),
            line("@azr.Sponsor", "It is useful."),
        ],
    ))
    specs.append(page(
        19, "Say the Number", "AZR_ConservationHub", ["AZR_Finfluencers", "AZR_GuestRelations", "AZR_BrineSquad"],
        "Julian records the public result without inflating it, and the team discovers that accurate framing can still feel polished when the underlying work is strong enough to carry the story.",
        [
            "Julian stands at the Conservation Hub with the final audited number displayed at human scale rather than as a triumphal counter.",
            "Fleur strips away celebratory graphics that would imply the original target was met.",
            "Nia watches the normal open circulation continue behind the recording instead of staging a crowd.",
            "Maya checks Julian's wording before he records the final take.",
            "Julian delivers the accurate line cleanly and lets the working park remain visible behind him.",
        ],
        [
            line("@azr.Julian", "Conservation Week: eighteen thousand four hundred twelve verified actions."),
            line("@azr.Fleur", "No victory music."),
            line("@azr.Julian", "I know."),
            line("@azr.Nia", "You look physically unwell."),
            line("@azr.Julian", "I can make honesty cinematic."),
            line("@azr.Maya", "Try making it accurate first."),
            line("@azr.Julian", "That's what I meant."),
        ],
    ))
    specs.append(page(
        20, "Methodology", "AZR_GuestExperienceSuite", ["AZR_Corporate", "AZR_Finfluencers"],
        "The sponsor asks Azure Reach to preserve the methodology and the missed target in the final report, converting what looked like a campaign failure into a credible operating model worth repeating.",
        [
            "The final sponsor report opens with the audited result and a plain methodology note rather than burying either.",
            "Elliot highlights the verification definitions and duplicate-removal rule.",
            "Beatrice points directly to the missed fifty-thousand internal target.",
            "The sponsor asks for the miss to remain because it explains why the later evidence is credible.",
            "Kyler reluctantly redesigns the charts around fewer, better-defined measures.",
            "Fleur approves the cleaner report while the sponsor signs off on the methodology page.",
        ],
        [
            line("@azr.Sponsor", "Keep the methodology in the final report."),
            line("@azr.Elliot", "Gladly."),
            line("@azr.Beatrice", "And the missed target?"),
            line("@azr.Sponsor", "Include it."),
            line("@azr.Kyler", "That will ruin at least three charts."),
            line("@azr.Sponsor", "Then improve the charts."),
            line("@azr.Fleur", "I like them already."),
        ],
    ))
    specs.append(page(
        21, "Scalable", "AZR_OpsRoom", ["AZR_Corporate", "AZR_GuestRelations", "AZR_Finfluencers", "AZR_BrineSquad"],
        "The ensemble extracts a repeatable process from the week—design the useful action first, define verification before launch and only then build the public experience—while resisting the temptation to turn the lesson into another oversized campaign.",
        [
            "Beatrice writes SCALABLE on the ops-room board and immediately gets a warning look from Maya.",
            "Nia adds DESIGN THE ACTION FIRST beneath it, grounding the lesson in guest reality.",
            "Kyler adds a metric definition only after the action is clear.",
            "Elliot adds verification rules before launch rather than after the dashboard goes green.",
            "Julian reframes the final step as public presentation without changing the work underneath it.",
            "Sal regards the resulting five-line process and accepts it only because it is shorter than the campaign that produced it.",
        ],
        [
            line("@azr.Beatrice", "We learned something scalable."),
            line("@azr.Maya", "Careful."),
            line("@azr.Beatrice", "Not the campaign. The process."),
            line("@azr.Nia", "Design the action first."),
            line("@azr.Kyler", "Choose a metric that measures the action."),
            line("@azr.Elliot", "Define verification before launch."),
            line("@azr.Julian", "Then make it look effortless."),
            line("@azr.Sal", "You had me until the last part."),
        ],
    ))
    specs.append(page(
        22, "Tomorrow's Deck", "AZR_StaffOverlook", ["AZR_Corporate", "AZR_GuestRelations", "AZR_Finfluencers", "AZR_BrineSquad"],
        "At the quiet end-of-week overlook, the team barely finishes absorbing the Conservation Week lesson before Beatrice reveals that the Anniversary Gala deck is due tomorrow, carrying the new process directly into the season finale's prestige pressure.",
        [
            "The ensemble decompresses at the staff overlook while the public park glows beautifully beyond the glass and water.",
            "Beatrice arrives carrying a slim tablet instead of a giant campaign board, which briefly looks like evidence of growth.",
            "She reveals the Anniversary Gala deck is due tomorrow; the group processes the phrase in silence.",
            "Julian lists the gala's sponsors, donors, board presence and livestream requirements with growing professional excitement.",
            "Nia asks the question Conservation Week has taught them to ask before any new promise is added.",
            "Maya and Sal exchange a look as Beatrice claims she has learned, ending on wary confidence rather than reset-to-zero defeat.",
        ],
        [
            line("@azr.Beatrice", "The gala deck is tomorrow."),
            line("@azr.Everyone", "Of course it is."),
            line("@azr.Julian", "Anniversary Gala. Sponsors, donors, board, livestream."),
            line("@azr.Nia", "How many separate promises?"),
            line("@azr.Beatrice", "Currently?"),
            line("@azr.Maya", "That is not an encouraging word."),
            line("@azr.Beatrice", "I have learned."),
            line("@azr.Sal", "That's what worries me."),
        ],
    ))
    assert len(specs) == 13
    assert sum(p["panelCount"] for p in specs) == 68
    assert sum(len(p["dialogueInline"]) for p in specs) == 93
    return specs


def validate_pages(parsed):
    if len(parsed) != 22:
        raise SystemExit(f"Issue 5 page count is {len(parsed)}, expected 22")
    expected_ids = [f"AZR_S1E05_P{i:02d}" for i in range(1, 23)]
    if [p.get("id") for p in parsed] != expected_ids:
        raise SystemExit("Issue 5 page IDs are not intact")
    if sum(p.get("panelCount", 0) for p in parsed) != 113:
        raise SystemExit("Issue 5 panel count is not intact")
    if sum(len(p.get("dialogueInline", [])) for p in parsed) != 160:
        raise SystemExit("Issue 5 lettering count is not intact")
    text = json.dumps(parsed, ensure_ascii=False)
    for required in (
        "Fifty thousand verified actions in seven days.",
        "Eighteen thousand four hundred twelve.",
        "The gala deck is tomorrow.",
    ):
        if required not in text:
            raise SystemExit(f"Issue 5 missing continuity line: {required}")


def salvage_and_rebuild(data):
    text = raw_deflate_text(data)
    marker10 = '{"id":"AZR_S1E05_P10"'
    p10 = text.find(marker10)
    if p10 < 0:
        raise SystemExit("Cannot locate intact Issue 5 page-10 boundary")
    prefix = text[:p10].rstrip().rstrip(",") + "]"
    intact = json.loads(prefix)
    if [p.get("id") for p in intact] != [f"AZR_S1E05_P{i:02d}" for i in range(1, 10)]:
        raise SystemExit("Issue 5 intact prefix is not pages 1-9")
    if sum(p.get("panelCount", 0) for p in intact) != 45:
        raise SystemExit("Issue 5 intact prefix panel count changed")
    if sum(len(p.get("dialogueInline", [])) for p in intact) != 67:
        raise SystemExit("Issue 5 intact prefix lettering count changed")
    rebuilt = intact + replacement_pages()
    validate_pages(rebuilt)
    return json.dumps(rebuilt, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


encoded_text = PATH.read_text(encoding="utf-8")
data = decode_b64(encoded_text)
try:
    recovered = gzip.decompress(data)
    parsed = json.loads(recovered.decode("utf-8"))
    validate_pages(parsed)
    print("Azure Reach Issue 5 gzip payload already valid; no repair needed")
except (gzip.BadGzipFile, EOFError, json.JSONDecodeError):
    rebuilt = salvage_and_rebuild(data)
    repaired = gzip.compress(rebuilt, compresslevel=9, mtime=0)
    normalized = base64.b64encode(repaired).decode("ascii") + "\n"
    PATH.write_text(normalized, encoding="utf-8")
    verify = json.loads(gzip.decompress(base64.b64decode(normalized)).decode("utf-8"))
    validate_pages(verify)
    print("Azure Reach Issue 5 pages 1-9 preserved; pages 10-22 reconstructed, encoded, and verified")
