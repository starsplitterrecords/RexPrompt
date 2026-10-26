#!/usr/bin/env python3
"""Explicit color-managed grading comparisons. Never rewrites approved art."""
import argparse
import hashlib
import io
import json
from pathlib import Path
from PIL import Image,ImageCms,ImageEnhance,ImageOps

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--grade",type=Path,required=True,help="JSON {brightness, contrast, saturation}; values 0.5..1.5")
    p.add_argument("--untagged-srgb-evidence",help="Specific human evidence permitting sRGB interpretation for untagged source")
    args=p.parse_args()
    src=args.source.resolve()
    raw=src.read_bytes()
    grade=json.loads(args.grade.read_text())
    if not isinstance(grade,dict) or not grade or set(grade)-{"brightness","contrast","saturation"}:
        p.error("Grade must contain only supported brightness, contrast, saturation controls")
    if any(type(v) not in (float,int) or not 0.5<=v<=1.5 for v in grade.values()):
        p.error("Grade controls must be numeric factors from 0.5 to 1.5")
    with Image.open(io.BytesIO(raw)) as im:
        im.load()
        original=ImageOps.exif_transpose(im)
        embedded=im.info.get("icc_profile")
        if embedded:
            src_profile=ImageCms.ImageCmsProfile(io.BytesIO(embedded))
            normalized=ImageCms.profileToProfile(original.convert("RGB"),src_profile,
                        ImageCms.createProfile("sRGB"),outputMode="RGB",renderingIntent=0)
            source_class="ICC-transformed-to-sRGB"
        else:
            if not args.untagged_srgb_evidence or len(args.untagged_srgb_evidence.strip())<12:
                p.error("Untagged source blocked: provide --untagged-srgb-evidence documenting source-space identification")
            normalized=original.convert("RGB")
            source_class="sRGB-explicitly-interpreted-with-evidence"
        result=normalized.copy()
        for name,op in (("brightness",ImageEnhance.Brightness),
                        ("contrast",ImageEnhance.Contrast),("saturation",ImageEnhance.Color)):
            if name in grade:result=op(result).enhance(grade[name])
        if result.size != normalized.size:
            raise ValueError("Proof geometry changed")
        if src.read_bytes()!=raw:
            raise ValueError("Source changed during proof operation")
    out=args.out.resolve()
    if out==src or out.is_relative_to(src.parent) and out.name==src.name:
        p.error("Proof may not overwrite its source")
    out.parent.mkdir(parents=True,exist_ok=True)
    profile=ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
    result.save(out,format="PNG",icc_profile=profile)
    sidecar={"state":"PROPOSED-UNAPPROVED-REVIEW-PROOF","source":str(src),
             "sourceSha256":hashlib.sha256(raw).hexdigest(),"originalPixels":list(result.size),
             "sourceColorHandling":source_class,"untaggedSourceEvidence":args.untagged_srgb_evidence,
             "grade":grade,"proofSha256":hashlib.sha256(out.read_bytes()).hexdigest(),
             "proofColorProfile":"embedded sRGB","pressReady":False}
    out.with_suffix(".json").write_text(json.dumps(sidecar,indent=2)+"\n")
    # Contact sheet comparison only; native proof remains untouched at full pixel geometry.
    width=580
    left=ImageOps.contain(normalized,(width,880))
    right=ImageOps.contain(result,(width,880))
    sheet=Image.new("RGB",(1180,max(left.height,right.height)+50),"#222222")
    sheet.paste(left,(10,40));sheet.paste(right,(600,40))
    from PIL import ImageDraw
    d=ImageDraw.Draw(sheet);d.text((12,12),"ORIGINAL (working sRGB)",fill="white")
    d.text((602,12),"PROPOSED GRADE - NOT APPROVED",fill="white")
    sheet.save(out.with_name(out.stem+"-compare.jpg"),quality=90)
    print(json.dumps(sidecar,indent=2))
if __name__=="__main__":main()
