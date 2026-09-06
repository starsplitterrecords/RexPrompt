# IMG Binary Readback

This document defines the canonical method for retrieving RexPrompt production images into a fresh IMG session as actual image pixels.

## Core rule

A manifest entry, repository path, Git SHA, filename, prior-chat description, or claim that an image exists is not visual inspection.

When continuity requires an existing production image, the actual image pixels must be transported into the active ChatGPT session and visually inspected before image generation.

## Canonical RexPrompt retrieval method

For an approved RexPrompt production draft:

1. Resolve the exact image from `production/drafts/manifest.json`.
2. Resolve its repository path and recipe identity.
3. Do not rely on normal GitHub text-file/blob fetch for PNG/JPEG retrieval when that path attempts UTF-8 decoding.
4. Use a GitHub Actions artifact bridge:
   - check out the required RexPrompt revision,
   - select the exact approved draft image,
   - upload the image or a small reference bundle with `actions/upload-artifact`,
   - retrieve the artifact with the GitHub binary artifact-download capability,
   - extract the image into the active session/runtime.
5. Open and inspect the extracted image as actual pixels.
6. Verify identity against the manifest and, when available, verify reconstructed bytes against the expected Git blob SHA.
7. Only after the actual pixels have been inspected may the image be used as immediate continuity/reference input.

The artifact bridge is transport only. RexPrompt remains the durable authority for approved unpublished production drafts. StarSplitterVisions remains the authority for released canon.

## Exactness

The artifact bridge must preserve the original file bytes. It is not a visual recreation, screenshot, raster approximation, or metadata reconstruction.

If a ZIP artifact is used, extract the original file unchanged.

If a base64 bridge is required as a fallback, it must encode the original image bytes losslessly. Chunking is allowed if necessary; concatenate exactly, decode locally, and verify the resulting Git blob SHA or cryptographic digest when available.

Do not store base64 copies in RexPrompt production data merely to support readback.

## Mandatory inspection gate

Before generation, if the selected unit depends on an existing production image for immediate continuity:

- retrieve the predecessor/reference image pixels,
- place them in active multimodal context,
- visually inspect them,
- then generate.

If the image can be identified but its pixels cannot be transported into the active session, generation is blocked. State the resolved current unit, the exact predecessor/reference image that must be inspected, and the transport failure. Do not silently fall back to memory, summaries, paths, SHAs, or textual descriptions.

The immediately preceding image is never the sole style/identity authority; combine it with released canon and curated identity/world references as applicable.

## Session independence

A fresh IMG chat must be able to recover visual continuity from durable sources without depending on another chat. The user should not normally have to re-upload a RexPrompt production image manually.

Manual attachment is a last-resort recovery path only after the canonical artifact bridge has been attempted and genuinely cannot transport the image.

## Proven reference case

The method was proven end-to-end on:

- repository: `starsplitterrecords/RexPrompt`
- image: `production/drafts/azure-reach/azure-reach-s1-e02/azr_s1e02_p11.png`
- recipe: `AZR_S1E02_P11`
- Git blob SHA: `1d02c6157318d0662f3222d671952ab406e3c805`

The downloaded artifact reconstructed the exact original PNG bytes and the Git blob SHA matched.
