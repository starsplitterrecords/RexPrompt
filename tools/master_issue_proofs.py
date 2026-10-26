#!/usr/bin/env python3
"""Non-destructive issue mastering workbench. Requires Pillow.

Creates native-resolution inspection facts, a contact sheet, and optional
color-adjusted *proofs*. Never overwrites approved production artwork.
"""
import argparse
import hashlib
import io
import json
import math
import statistics
from pathlib import Path
from PIL import Image, ImageEnhance, ImageOps, ImageStat, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
DRAFTS = (ROOT / "production/drafts").resolve()
IMAGE_TYPES = {"image/png": "PNG", "image/jpeg": "JPEG", "image/webp": "WEBP"}

def fail(message):
    raise SystemExit("ERROR: " + message)

def load_json(file):
    return json.loads(file.read_text(encoding="utf-8"))

def bounded_factor(value, key):
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not 0.5 <= value <= 1.5:
        fail(f"Look factor {key} must be between 0.5 and 1.5")
    return float(value)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--series", required=True)
    parser.add_argument("--issue", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--trim-width", type=float, default=6.625, help="Target trim width (inches), for DPI calculation only")
    parser.add_argument("--trim-height", type=float, default=10.25, help="Target trim height (inches), for DPI calculation only")
    parser.add_argument("--min-dpi", type=int, default=300)
    parser.add_argument("--allow-incomplete", action="store_true", help="Audit only, never marks a book ready")
    parser.add_argument("--look", type=Path, help="Explicit manual per-page grade plan; proofs only")
    parser.add_argument("--render-proofs", action="store_true", help="Write proof PNGs with original pixel dimensions")
    a = parser.parse_args()
    if min(a.trim_width, a.trim_height, a.min_dpi) <= 0:
        fail("Trim dimensions and minimum DPI must be positive")
    approved = load_json(ROOT / "production/drafts/manifest.json").get("drafts", {})
    books = load_json(ROOT / "production/book-manifests.json").get("issues", {})
    key = a.series + "::" + a.issue
    book = books.get(key)
    if not book:
        fail("No complete-book manifest for " + key + "; do not assume story selection is complete")
    units = book["units"]
    if len(units) != len(set(units)):
        fail("Book inventory has duplicate unit IDs")
    out = Path(a.out).resolve()
    if out == DRAFTS or out.is_relative_to(DRAFTS):
        fail("Output directory cannot be inside approved draft storage")
    out.mkdir(parents=True, exist_ok=True)
    raw_look = load_json(a.look) if a.look else {}
    if not isinstance(raw_look, dict) or any(x not in units for x in raw_look):
        fail("Look plan must be {recipeId: {brightness,contrast,saturation}} for this issue")
    entries = []
    warnings, errors = [], []
    thumbs = []
    for position, unit in enumerate(units, 1):
        entry = approved.get(key + "::" + unit)
        if not entry or entry.get("status") != "approved-production-draft":
            errors.append(f"{unit}: missing approved artwork")
            continue
        raw_path = ROOT / entry.get("image", "")
        resolved = raw_path.resolve()
        if not resolved.is_relative_to(DRAFTS) or not resolved.is_file():
            errors.append(f"{unit}: unsafe or missing source image")
            continue
        source = resolved.read_bytes()
        sha = hashlib.sha256(source).hexdigest()
        if entry.get("sha256") and entry["sha256"].lower() != sha:
            errors.append(f"{unit}: SHA-256 differs from manifest")
            continue
        try:
            with Image.open(io.BytesIO(source)) as image:
                if image.format != IMAGE_TYPES.get(entry.get("mimeType")):
                    errors.append(f"{unit}: MIME/image signature mismatch")
                    continue
                image.verify()
            with Image.open(io.BytesIO(source)) as image:
                native_width, native_height = image.size
                if native_width < 1 or native_height < 1:
                    errors.append(f"{unit}: invalid native resolution")
                    continue
                if image.mode in ("P", "RGBA", "LA") and "transparency" in image.info:
                    warnings.append(f"{unit}: transparency requires visual review of background")
                icc = image.info.get("icc_profile")
                if not icc:
                    warnings.append(f"{unit}: no embedded ICC profile; color space must be confirmed")
                if image.mode not in ("RGB", "RGBA", "P"):
                    warnings.append(f"{unit}: unusual source mode {image.mode}")
                dpi = min(native_width / a.trim_width, native_height / a.trim_height)
                if dpi < a.min_dpi:
                    errors.append(f"{unit}: native {dpi:.1f} DPI below required {a.min_dpi} at target trim; re-render at adequate source resolution")
                ratio_diff = abs(native_width/native_height-a.trim_width/a.trim_height)
                if ratio_diff > 0.03:
                    warnings.append(f"{unit}: source aspect ratio deviates from trim by {ratio_diff:.3f}")
                thumb = ImageOps.contain(image.convert("RGB"), (370, 575), Image.Resampling.LANCZOS)
                stat = ImageStat.Stat(thumb)
                mean_luma = round(sum(stat.mean[i]*weight for i,weight in enumerate((0.2126,0.7152,0.0722))), 2)
                sat = ImageStat.Stat(thumb.convert("HSV")).mean[1]
                entries.append({
                    "recipeId": unit, "readingOrder": position, "source": entry["image"],
                    "sha256": sha, "nativeWidth": native_width, "nativeHeight": native_height,
                    "effectiveDpiAtTrim": round(dpi, 1), "sourceMode": image.mode,
                    "iccEmbedded": bool(icc), "iccSha256": hashlib.sha256(icc).hexdigest() if icc else None,
                    "meanLuminance": mean_luma, "meanSaturation": round(sat, 2),
                    "status": "needs-manual-visual-review"
                })
                thumbs.append((unit, thumb.copy()))
                if a.render_proofs:
                    values = raw_look.get(unit, {})
                    if not isinstance(values, dict) or any(k not in ("brightness", "contrast", "saturation") for k in values):
                        fail("Invalid look settings for " + unit)
                    params = {k:bounded_factor(v,k) for k,v in values.items()}
                    proof = image.convert("RGB")
                    for factor,cls in (("brightness", ImageEnhance.Brightness), ("contrast", ImageEnhance.Contrast), ("saturation", ImageEnhance.Color)):
                        if factor in params:
                            proof = cls(proof).enhance(params[factor])
                    proof_file = out / "proofs" / (f"{position:03d}-"+unit.lower()+".png")
                    proof_file.parent.mkdir(parents=True, exist_ok=True)
                    proof.save(proof_file,format="PNG",compress_level=6)
                    if proof.size != (native_width,native_height):
                        fail("Proof changed native geometry for " + unit)
        except (OSError, ValueError, SyntaxError) as exc:
            errors.append(f"{unit}: cannot decode image: {exc}")
    if entries:
        luminance = statistics.median(x["meanLuminance"] for x in entries)
        saturation = statistics.median(x["meanSaturation"] for x in entries)
        for item in entries:
            if abs(item["meanLuminance"]-luminance) > 35:
                warnings.append(item["recipeId"]+": luminance outlier; inspect intended scene lighting before grading")
            if abs(item["meanSaturation"]-saturation) > 45:
                warnings.append(item["recipeId"]+": saturation outlier; inspect intended palette before grading")
    else:
        luminance = saturation = None
    columns = 4
    tile_width, tile_height = 394, 635
    rows = max(1, math.ceil(len(thumbs)/columns))
    canvas = Image.new("RGB", (columns*tile_width, rows*tile_height), "#24272b")
    draw = ImageDraw.Draw(canvas)
    for i,(unit,thumb) in enumerate(thumbs):
        x=(i%columns)*tile_width+12; y=(i//columns)*tile_height+15
        canvas.paste(thumb,(x+(370-thumb.width)//2,y))
        draw.text((x+4,y+584),f"{i+1:02d}  {unit}",fill="white")
    canvas.save(out / "contact-sheet.jpg", quality=90)
    report = {
        "schemaVersion": 1, "issue": key, "expectedUnits": len(units),
        "inspectedUnits": len(entries), "sourceArtworkModified": False,
        "targetTrimInches": [a.trim_width,a.trim_height], "requiredNativeDpi": a.min_dpi,
        "medianLuminance": luminance,"medianSaturation": saturation,
        "errors": errors, "warnings": warnings,"pages": entries,
        "completion": "incomplete" if errors or len(entries)!=len(units) else "machine-preflight-only",
        "publicationApproval": "not granted; manual native-pixel, color, continuity and lettering signoff required"
    }
    (out / "mastering-report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(f"{key}: {len(entries)}/{len(units)} pages inspected; {len(errors)} errors, {len(warnings)} warnings")
    print("Report: ",out/"mastering-report.json")
    print("Contact sheet: ",out/"contact-sheet.jpg")
    if errors and not a.allow_incomplete:
        fail("Issue is not mastering-ready; see report")
    if errors and a.allow_incomplete:
        print("INCOMPLETE: audit-only report; cannot imply a mastered or releasable issue")

if __name__=="__main__":
    main()
