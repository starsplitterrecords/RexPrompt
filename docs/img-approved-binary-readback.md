# IMG Approved Binary Readback

Run **IMG Approved Binary Readback** from GitHub Actions with exact series, issue and recipe IDs from `production/drafts/manifest.json`. The job accepts only a currently approved draft, verifies its path, format, hash and unchanged file bytes, then uploads an exact original image plus `provenance.json`.

The ZIP is temporary transport, not a new approval or replacement visual canon. Retrieve the artifact, extract the PNG/JPEG/WebP unchanged, verify the hash, and inspect its **actual pixels** inside the IMG session before generation. Do not substitute manifest text for image inspection.

A pull-request smoke test uses already-approved Azure Reach P11 to validate the bridge without generating or modifying artwork. This bridge alone does not guarantee ChatGPT can import the artifact; that must be verified separately.
