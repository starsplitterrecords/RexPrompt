#!/usr/bin/env python3
"""Transport an already-approved original image, unchanged."""
import hashlib, json, os, shutil, subprocess
from pathlib import Path
root = Path(__file__).resolve().parent.parent
series, issue, recipe = (os.environ[k] for k in ("SERIES_ID","ISSUE_ID","RECIPE_ID"))
key = "::".join((series, issue, recipe))
data = json.loads((root/"production/drafts/manifest.json").read_text())
entry = data["drafts"].get(key)
if not entry or entry.get("status") != "approved-production-draft":
    raise SystemExit("No approved source for " + key)
rel = Path(entry["image"])
if rel.is_absolute() or ".." in rel.parts or not rel.is_relative_to(Path("production/drafts")/series/issue):
    raise SystemExit("Unsafe or mis-scoped image path")
source = (root/rel).resolve()
if not source.is_file() or not source.is_relative_to(root):
    raise SystemExit("Original source binary missing")
content = source.read_bytes()
mime = ("image/png" if content.startswith(bytes.fromhex("89504e470d0a1a0a"))
        else "image/jpeg" if content.startswith(bytes.fromhex("ffd8ff"))
        else "image/webp" if content[:4] == b"RIFF" and content[8:12] == b"WEBP"
        else "")
if not mime or mime != entry.get("mimeType"):
    raise SystemExit("Corrupt image or MIME mismatch")
git_sha = subprocess.check_output(["git","hash-object",str(source)],cwd=root,text=True).strip()
target = root/"img-readback"; target.mkdir(exist_ok=True)
destination = target/source.name
shutil.copyfile(source,destination)
if destination.read_bytes() != content:
    raise SystemExit("Transport changed original image bytes")
meta = {"manifestKey":key,"originalPath":str(rel),"fileName":source.name,
    "gitBlobSha":git_sha,"sha256":hashlib.sha256(content).hexdigest(),
    "sourceCommit":os.environ.get("SOURCE_COMMIT",""),
    "mimeType":mime,"bytes":len(content),"approvalStatus":entry["status"]}
(target/"provenance.json").write_text(json.dumps(meta,indent=2)+"\n")
print("Exact original verified",key,git_sha,meta["sha256"],len(content))
