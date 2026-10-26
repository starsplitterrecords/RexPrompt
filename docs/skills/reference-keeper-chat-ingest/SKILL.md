---
name: reference-keeper-chat-ingest
description: Import explicitly selected or approved visual images from a ChatGPT conversation into the correct RexPrompt Reference Keeper series library through GitHub, storing original image bytes and updating the keeper manifest atomically.
---

# Reference Keeper — Chat Image Ingest Skill

## Trigger and scope

Use when the user says **"Run Reference Keeper ingest on this chat"**, **"Save these references to Reference Keeper"**, or names a specific accessible chat or selection of images to preserve as RexPrompt visual references.

The selected conversation is the source of candidate images; it is **not** authorization to store every image. Import explicitly approved, identified, or clearly user-selected visual references only. A general instruction to process a chat permits an inventory and a conservative selection pass, not the promotion of experimental, rejected, failed, superseded, or merely attractive outputs to canonical reference status.

Repository: `starsplitterrecords/RexPrompt`. Use its connected GitHub tools. Do not request, expose, or store a GitHub personal access token in chat. Use the current repository code and data, never remembered assumptions, as the storage contract.

This is a **storage-only** operation. It does not modify RexPrompt assembled prompts, `visual-reference-pack.json`, issue recipes, GitHub release assets, or published StarSplitterVisions canon unless the user independently asks for those changes.

## Required live contract read

Before each batch, inspect these files on the current `main`:

1. `reference-keeper.js` — current allowed types, MIME types, maximum size, slug function, series mapping, storage path, and manifest transaction behavior.
2. `data/shows.json` — current series display names and available series choices.
3. `production/references/reference-keeper-manifest.json` — existing IDs, series, names, image paths, and collisions.
4. `production/references/REFERENCE_KEEPER.md` — documented storage/retrieval behavior.

As verified on 2026-10-25, the contract is:

- Image types: `character`, `setting`, `vehicle`, `item`.
- MIME types: `image/jpeg`, `image/png`, `image/webp`; per-image limit 50 MiB.
- Image path: `production/references/<seriesId>/keeper/<type>/<slug(name)>.<ext>`.
- Manifest path: `production/references/reference-keeper-manifest.json`.
- Manifest top-level shape: `{"schemaVersion":1,"references":{...}}`.
- Reference key: `<seriesId>::<type>::<slug(name)>`.
- Slug logic: lower-case string; replace runs of characters outside `[a-z0-9._-]` with `-`; trim leading/trailing hyphens; use `item` for an empty slug.
- Each entry has exactly the existing Keeper fields: `id`, `seriesId`, `seriesName`, `type`, `name`, `image`, `mimeType`, `sourceFilename`, `updatedAt`.

**Re-read before use.** The live application may change. Do not add fields or invent a parallel manifest.

## 1. Identify the source chat and actual image bytes

Operate in the specific chat where the command is given, or on images explicitly supplied/accessible from a named chat. Inspect the available conversation context, attached files, and generated images.

Never imply that a link, transcript, thumbnail, markdown preview, filename, conversation summary, or remembered generated image gives access to the original binary. If original image bytes are not accessible in the active execution environment, report those images as blocked and request that the user provide the image files or invoke the skill in a chat where the originals are actually available. Do not recreate images or use screenshots of thumbnails as substitutes.

For each candidate, record the concrete source/image identity, source filename if available, original byte size, MIME format, intended series, proposed type and display name, and evidence of approval/selection. Prefer full original generation or uploaded file bytes. Do not crop, resize, color-grade, recompress, or alter the stored image without explicit instruction.

## 2. Scope, select, and classify

Determine the target series **as the Reference Keeper UI resolves it**, not from an issue slug or guess. The present UI derives series options from `seriesName` in `data/shows.json` (or fallback name/ID), strips a trailing ` — ...` issue suffix and ` Cover(s)`, and applies its `safe()` slug function. Match existing manifest series identifiers and names; verify the visible label. If a chat contains images for several series, separate and commit each to the matching series.

For each chosen image, classify:

- `character` — stable character appearances / approved model sheets.
- `setting` — stable environments, recurring locations and architecture.
- `vehicle` — ships, craft, vehicles and their consistent designs.
- `item` — props, devices, uniforms/equipment details and discrete objects.

Use specific descriptive names such as `Thunderbreak bridge`, not meaningless upload UUIDs. Preserve user-given approved naming and identity. A collage is one image unless the user explicitly requests extracting separate references and that extraction can preserve approved content. Do not assert that an image changes released canon simply because it is newly stored.

If approval or category is materially ambiguous, conservatively skip that image and report it rather than promote it by inference.

## 3. De-duplicate and plan

Check existing manifest keys, target paths, names, and available content hashes. For each candidate decide **add**, **skip unchanged**, **replace explicitly approved**, or **blocked**.

- Existing key: never overwrite just because a new file looks newer. Replacement requires explicit approval.
- Same pixels already stored under the same intended reference: skip rather than duplicate.
- Key/slug collisions for distinct subjects: choose an unambiguous name, never silently overwrite.
- Ambiguous existing reference (especially a UUID-labelled one): identify the actual visual content before renaming or replacing.
- Preserve unrelated manifest entries byte-for-byte in meaning and avoid unrelated reordering or edits.

An inventory is useful but is **not completion**. A successful ingest includes stored pixels and the correct manifest entries.

## 4. Write through GitHub as one coherent change

Prefer the connected GitHub write operations and the repository's existing atomic Git-data transaction pattern:

1. Fetch fresh current `main` head, commit/tree and manifest, not an earlier cached copy.
2. Create binary blobs from **actual original bytes**, base64 encoded, using GitHub Git Data blob creation. A text-only file operation must not be used to upload raw images.
3. Add the image blob paths to a Git tree based on the fetched head tree.
4. Update the in-memory manifest using the exact current schema; preserve unrelated entries. Set `updatedAt` to the actual commit-time ISO-8601 timestamp, and `sourceFilename` to the original filename (or accurate generated filename if that is the source).
5. Add the manifest JSON blob to the **same tree** as the images. If replacing with a new extension/path, delete the prior image path in that same tree.
6. Create a Git commit with the original HEAD as parent and fast-forward `main` without force.
7. On a concurrent-head conflict, fetch new HEAD and manifest, replay the intended add/replace/skip decisions, and retry safely. Never force-push or overwrite someone else's newly written references.

If direct binary transport through the available connector is not feasible for an image, use an established approved binary upload/bridge workflow capable of preserving the **same bytes** and return to the atomic commit when possible. If that cannot be executed, **stop that image**; do not create a manifest pointer to a missing file. A manifest-only commit is not successful ingest.

Do not split image and manifest across separate commits when the atomic Git-data path is available.

## 5. Verify each imported reference

Read the resulting `main` manifest and tree after commit. Check for each entry:

- The exact key, display name, type and series ID are present.
- The referenced repository image object exists and matches the intended original binary (hash and/or verifiable byte identity).
- The image path is inside its series Keeper folder, MIME/extension agree, and `updatedAt` is valid.
- Existing unrelated manifest records remain intact.
- The current Keeper UI's series and type filters would include it, using the actual `reference-keeper.js` logic.
- When browser/UI access is available, refresh and verify the image renders under **Reference Keeper → Series → Type**; otherwise report structural verification explicitly, without claiming a visual browser check.

Keep approved reference storage separate from **released canon** and from **approved draft production**. References can assist later visual production only after actual pixel readback when a production workflow requires it.

## Result format

Report: selected chat or source, target series, items **added / replaced / unchanged / blocked**, final displayed reference names and types, GitHub commit SHA or link, manifest path, and whether UI rendering was directly verified. Be explicit about inaccessible originals or uncertain approval. Do not say 'done' when only a manifest entry or an inventory exists.

## Reusable invocation examples

- **Run Reference Keeper ingest on this chat. Import only the approved character and setting references to Rex Fleet.**
- **Run Reference Keeper ingest on this chat for Sunforge Outlaw; keep the original full-resolution PNGs.**
- **Inventory this chat for Reference Keeper candidates. Do not commit yet.**
- **Replace the existing Thunderbreak bridge reference with the approved image in this chat.**

The skill can operate from an accessible named chat if its original image files can be retrieved, but a chat title or URL by itself does not guarantee binary access. For dependable execution on historical chat images, invoke it from that chat or provide the original files.
