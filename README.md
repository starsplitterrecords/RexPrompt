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

## How assembly works

When a show is selected:

1. RexPrompt loads that show's JSON dictionaries.
2. The selected scene recipe resolves IDs against those dictionaries.
3. Character IDs become Star Splitter handles.
4. Dialogue is assembled with the speaker handle, spoken line, and subtext when present.
5. Setting, region, factions, characters, and direction are appended as formatted prompt sections.
6. The assembled result is displayed and can be copied directly to the clipboard.

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

[DIALOGUE]
@character.handle says "..."
  (subtext...)

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

## Data files

Each show supplies:

- `scenes_prequel.json` (or the configured `scenesFile`) — scene recipes and summaries
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

The scene recipe is the central piece. It points to the IDs needed for that generation unit; RexPrompt performs deterministic lookup and assembly rather than interpreting the story itself.

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
├── README.md
└── data/
    ├── shows.json
    ├── ...prequel data...
    └── shows/
        └── <show-id>/
            └── ...show JSON package...
```

## Design principle

RexPrompt should remain a small deterministic assembler. New shows should add data, not application logic.
