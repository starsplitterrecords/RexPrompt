# RexPrompt

RexPrompt is a lightweight, browser-based prompt assembler for **Star Splitter** scene production. It takes structured scene, character, dialogue, setting, faction, region, and direction data from JSON files and assembles it into a consistent, ready-to-copy generation prompt.

The current prompt format is aimed at short fictional video scenes and includes the scene summary, character handles, dialogue and subtext, setting, region, factions, characters, and direction.

## Use it

**Live app:** https://starsplitterrecords.github.io/RexPrompt/

**GitHub repository:** https://github.com/starsplitterrecords/RexPrompt

## How it works

RexPrompt has no backend and no build process. The application is contained in `index.html`, with its source material stored as JSON under `data/`.

When the page loads:

1. `index.html` loads the JSON data files in `data/`.
2. `data/scenes_prequel.json` provides the scene recipes shown in the **Scene** dropdown.
3. Selecting a scene resolves the IDs in that recipe against the supporting data files.
4. Character IDs are converted to their Star Splitter handles.
5. Dialogue is assembled with the speaker handle, spoken line, and subtext when present.
6. Setting, region, factions, characters, and direction are added as formatted prompt sections.
7. The assembled result is displayed in the output area and can be copied directly to the clipboard.

A generated prompt currently follows roughly this structure:

```text
@character.handle

=== SCENE: 2 ===
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

### Build

Rebuilds the prompt for the currently selected scene.

Changing the scene selection also automatically rebuilds the prompt.

### Copy Assembled Text

Copies the complete assembled prompt to the system clipboard so it can be pasted into the generation workflow.

### Commit Scene

Moves the current scene to the end of the scene list and advances to the next scene.

Despite the name, **Commit Scene does not commit or write anything to GitHub or to the JSON files**. The reordered queue exists only in the current browser session. Reloading the page restores the original order from `scenes_prequel.json`.

## Data files

The application currently loads these files:

- `data/scenes_prequel.json` — scene recipes and summaries
- `data/characters.json` — characters, names, handles, roles, and notes
- `data/dialogue.json` — dialogue lines and character subtext
- `data/direction.json` — scene direction entries
- `data/settings.json` — locations/settings
- `data/regions.json` — regional context
- `data/factions.json` — faction information
- `data/blocking.json` — blocking patterns
- `data/lighting.json` — lighting guidance
- `data/mood.json` — mood and tension guidance
- `data/negatives.json` — negative visual guidance

The scene recipe is the central piece. A scene points to the IDs it needs, and the assembler looks those IDs up in the appropriate data files when building the final text.

## Deployment

RexPrompt is a static site. There is:

- no package manager
- no compile/build step
- no application server
- no database
- no server-side API

Deployment consists of serving `index.html` and the `data/` directory from the repository root.

The project can therefore be hosted directly with **GitHub Pages** from the `main` branch at the repository root. The resulting project URL follows GitHub Pages' standard project-site format:

```text
https://starsplitterrecords.github.io/RexPrompt/
```

Changes pushed to the published branch become part of the deployed static site once GitHub Pages publishes the updated files.

## Running locally

Because the application loads JSON with `fetch()`, run it through a local web server rather than opening `index.html` directly with a `file://` URL.

For example, from the repository directory:

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

## Editing RexPrompt

Most content changes do not require changing the application code. Add or revise entries in the JSON files and reference their IDs from the appropriate scene recipe.

Changes to the generated prompt format, scene-queue behavior, or UI controls are handled in `index.html`.