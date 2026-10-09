# RexPrompt Reference Keeper

Reference Keeper is a storage-only visual reference library inside RexPrompt.

It does not feed images or metadata into assembled RexPrompt recipes, and storing a reference does not publish anything to StarSplitterVisions.

## Storage

Keeper-managed images are stored at:

`production/references/<series-slug>/keeper/<type>/<reference-name>.<ext>`

Supported types:

- character
- setting
- vehicle
- item

The inventory is indexed at:

`production/references/reference-keeper-manifest.json`

The manifest records the exact repository path, series, type, display name, MIME type, source filename, and last update time.

## UI

Switch RexPrompt from **Assembler** to **Reference Keeper** in the page header.

Choose a series, name the reference, choose its type, select a JPEG/PNG/WebP image, and use **Store Reference**. Existing cards can be replaced or deleted.

Reference Keeper reuses the existing RexPrompt GitHub fine-grained token stored in `sessionStorage` for the current browser tab. The token requires repository Contents read/write access.

## Retrieval

For continuity work, inspect the manifest or the series Keeper folders through the GitHub connector to locate the exact image. When actual image pixels are required and the connector cannot directly return binary content, use the repository's established IMG Binary Readback workflow with that exact repository path.

Reference Keeper assets are visual-reference storage. They are not released canon unless separately published through the StarSplitterVisions release workflow.
