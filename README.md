# RexPrompt

RexPrompt is a lightweight, browser-based prompt assembler for **Star Splitter** scene production. It takes structured scene, character, dialogue, setting, faction, region, and direction data from JSON files and assembles them into a consistent, ready-to-copy generation prompt.

The assembler is intentionally simple: the application code stays the same while different shows provide different data packages.

## Use it

**Live app:** https://starsplitterrecords.github.io/RexPrompt/

**GitHub repository:** https://github.com/starsplitterrecords/RexPrompt

## Multi-show model

Available shows are defined in:

```text
data/shows.json
```

Each entry points RexPrompt at a data directory and tells it which scene-recipe file to load.

Example:

```json
[
  {
    "id": "prequel",
    "name": "Star Splitter Prequel",
    "basePath": "data",
    "scenesFile": "scenes_prequel.json"
  },
  {
    "id": "rex-fleet-s1",
    "name": "Rex Fleet — Season One",
    "basePath": "data/shows/rex-fleet-s1",
    "scenesFile": "scenes_prequel.json"
  }
]
```

The **Show** dropdown is built from this manifest. Changing shows unloads the current dataset, loads the selected show's JSON files, rebuilds the Scene dropdown, and resets that show's in-browser scene queue.

The last selected show is remembered in browser local storage.

## Adding a show

A show data directory uses the same simple files RexPrompt has always used:

```text
data/shows/my-show/
├── blocking.json
├── characters.json
├── dialogue.json
├── direction.json
├── factions.json
├── lighting.json
├── mood.json
├── negatives.json
├── regions.json
├── scenes_prequel.json
└── settings.json
```

The scene file can have another name; set that name in `shows.json` as `scenesFile`.

After copying the JSON package into its directory, add one entry to `data/shows.json`. **No assembler code needs to change for the new show.**

The original prequel remains in the root `data/` directory for backward compatibility.

## Package-local production configuration

A show may optionally provide `assembler.json` in its `basePath`. This augments or overrides the manifest entry without adding show-specific logic to `index.html`.

Use it when a production package has multiple authoritative page/scene files or needs deterministic overlays:

```json
{
  "scenesFiles": [
    "pages_e01_compiled.json",
    "pages_e02_compiled.json"
  ],
  "sceneOverlays": [
    {
      "file": "issue_01_rebuild.json",
      "mergeById": true,
      "strict": true
    }
  ],
  "dialogueOverlays": [
    {
      "file": "issue_01_scene_dialogue.json",
      "strict": true
    }
  ]
}
```

`sceneOverlays` with `mergeById` replace only the fields supplied for matching production IDs while preserving the rest of each page/scene recipe. `dialogueOverlays` replace the matched recipe's `dialogueInline` with either `dialogueInline` or `sceneDialogue` from the overlay. They do **not** create detached generation units.

Set `strict: true` for production overlays. Strict overlays fail when they reference an ID that is not present in the assembled production set. RexPrompt also rejects duplicate base/assembled IDs. This prevents development data from silently existing outside the generation path.

The authoritative generation unit remains the assembled page/scene recipe: summary, setting/region, factions, characters, panel plan, dialogue, continuity, and direction are emitted together.

## How assembly works

When a show is selected:

1. RexPrompt loads that show's JSON dictionaries.
2. If present, `assembler.json` loads the package's production file list and deterministic overlays.
3. Page/scene overlays are applied to the production recipes by configured rules.
4. Dialogue overlays are merged into those same recipes by page/scene ID.
5. The selected assembled recipe resolves IDs against the show dictionaries.
6. Character IDs become Star Splitter handles.
7. Dialogue is assembled with the speaker handle, spoken line, and subtext when present.
8. Setting, region, factions, characters, panel plan, continuity, and direction are appended as formatted prompt sections.
9. The assembled result is displayed and can be copied directly to the clipboard.

A generated prompt follows roughly this structure:

```text
@character.handle

=== SCENE: SCENE_ID ===
Scene summary...
10-second vertical clip. 8K modern-futuristic prestige TV style. Fictional production.

[SETTING]
...

[REGION]
...

[FACTIONS]
...

[CHARACTERS]
...

[PANEL PLAN]
...

[DIALOGUE]
@character.handle says "..."
  (subtext...)

[CONTINUITY]
...

[DIRECTION]
...
```

## Controls

### Show

Selects the data package currently loaded by RexPrompt.

### Scene

Selects a recipe from the active show.

### Build

Rebuilds the prompt for the selected scene. Changing the scene selection also rebuilds automatically.

### Copy Assembled Text

Copies the complete assembled prompt to the clipboard.

### Commit Scene

Moves the current scene to the end of the active show's in-browser queue and advances to the next scene.

Despite the name, **Commit Scene does not write anything to GitHub or the JSON files**. Reloading the show restores its original order.

## Production visuals

RexPrompt displays durable production visuals beside the selected recipe without changing the recipe assembler.

Two visual states are kept deliberately separate:

- **Approved production draft** — mutable production data stored in this RexPrompt repository.
- **Released canon** — read-only material sourced from `starsplitterrecords/StarSplitterVisions`.

An approved draft is stored only through an explicit action. Use **Upload Approved Draft** / **Replace Approved Draft** in the UI, or use a GitHub-capable workflow after explicitly directing it to post a specific image to RexPrompt. Generations, rejected attempts, and approval language by themselves do not write images to the repository.

The browser upload path uses a fine-grained GitHub token with Contents read/write permission. The token is entered in a masked field and retained only in browser `sessionStorage` for the current tab. Each upload commits the current image and its manifest entry together. Replacing a draft replaces the active production image; Git history retains earlier versions.

Drafts are visibly marked **DRAFT · NOT RELEASED**. Recipe options are annotated with `[DRAFT]` and `[CANON]` when those durable states are known.

For page-based issues, released canon can be resolved automatically only when the Visions issue page count exactly matches the current RexPrompt recipe count. Scene-based or otherwise non-1:1 material requires an explicit cross-repository mapping in `production/released-links.json`; RexPrompt does not guess scene-to-page relationships.

See `production/README.md` and `production/drafts/README.md` for the complete visual-state contract.

## Data files

Each show supplies:

- `scenes_prequel.json` (or the configured `scenesFile` / `scenesFiles`) — production scene/page recipes and summaries
- `assembler.json` (optional) — package-local production file and overlay configuration
- `characters.json` — characters, names, handles, roles, and notes
- `dialogue.json` — dialogue lines and character subtext
- `direction.json` — scene direction entries
- `settings.json` — locations/settings
- `regions.json` — regional context
- `factions.json` — faction information
- `blocking.json` — blocking patterns
- `lighting.json` — lighting guidance
- `mood.json` — mood and tension guidance
- `negatives.json` — negative visual guidance

The assembled scene/page recipe is the central piece. RexPrompt performs deterministic lookup and assembly rather than interpreting the story itself.

## Deployment

RexPrompt is a static site: no package manager, build step, application server, database, or server-side API is required.

It can be hosted directly with GitHub Pages from `main`.

## Running locally

Because RexPrompt loads JSON with `fetch()`, use a local web server rather than opening `index.html` with a `file://` URL.

```bash
python -m http.server 8000
```

Then open:

```text
http://localhost:8000/
```

## Repository structure

```text
RexPrompt/
├── index.html
├── visuals.js
├── README.md
├── production/
│   ├── README.md
│   ├── released-links.json
│   ├── visual-sources.json
│   └── drafts/
│       ├── README.md
│       └── manifest.json
└── data/
    ├── shows.json
    ├── ...prequel data...
    └── shows/
        └── <show-id>/
            ├── assembler.json
            └── ...show JSON package...
```

## Design principle

RexPrompt should remain a small deterministic assembler. New shows should add data, not application logic. Development notes or dialogue drafts are not generation-authoritative until the package configuration merges them into an actual production page/scene recipe.
