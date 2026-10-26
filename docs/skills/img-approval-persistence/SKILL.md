---
name: img-approval-persistence
description: Shared Star Splitter img-approval-persistence operating procedure.
skillVersion: 1.0.0-recovery
---
# img-approval-persistence

## Trigger
save approved draft atomically. Do not trigger for quoted examples or non-operational discussion.

## Authority
Inspect the live relevant repository files before work. RexPrompt assembled recipes, released StarSplitterVisions canon, approved unpublished production and Keeper references are DIFFERENT authorities. Follow explicit current user instructions and approvals. Same Rex Fleet-derived workflow for every IMG series; no Division Threshold exception.

## Steps
Read production/approval-policy.json and production/drafts/README.md live. Automatic-on-substantial-pass requires all quality gates and no user rejection/supersession. For PNG/JPEG/WebP produced or attached in ChatGPT, use the VERIFIED host-to-connector binary handoff documented in production/IMG_BINARY_READBACK.md: use tools/prepare_chatgpt_binary_handoff.py on the ORIGINAL mounted file, upload its unchanged Base64 payload file as temporary ChatGPT Library text, read that file from functions.exec and pass the recovered full Base64 directly to GitHub create_blob with encoding=base64. Validate exact line/length and the returned blob SHA against the locally computed Git blob SHA. Then commit that image blob and the approved manifest entry in ONE Git Data tree with key <seriesId>::<issueId>::<recipeId>, advance the target branch non-force, verify the committed file's blob SHA and manifest record, and independently read back original bytes when supported. For files >1 MB the GitHub Contents connector may return empty inline Base64: do not misreport that as a byte readback pass; use the IMG Actions artifact bridge for independent pixels/bytes verification. Never put a rejected, unreviewed, or failed image in production/drafts/manifest.json. Do not claim persistence until the Git ref points to the complete image+manifest commit. Clean temporary Library transport only after durable storage has been verified; never delete the original image. Never publish from this operation.

## Failure and completion
Check real files, original pixels, source identities, approval, commit/ref and end result as applicable; reject unverified claims. Report exact blockers. Preserve all previously approved work and never delete an artifact before permanent saving. Do not imply that a GitHub skill has been executed merely because its text exists, or that an image has been inspected merely because its manifest is readable.
