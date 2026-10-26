#!/usr/bin/env python3
"""Complete-book export: exact ordered source ZIP plus review PDF.

The complete-book manifest is authoritative. No missing page may be silently
omitted. Exported PDFs are proof packages, not mastering or release approval.
Requires Pillow and ReportLab.
"""
import argparse
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path
from PIL import Image, ImageOps
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import ImageReader

ROOT=Path(__file__).resolve().parents[1]
DRAFTS=(ROOT/"production/drafts").resolve()
MIMES={"image/png":"PNG","image/jpeg":"JPEG","image/webp":"WEBP"}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--series",required=True)
    parser.add_argument("--issue",required=True)
    parser.add_argument("--out",required=True)
    parser.add_argument("--trim-width",type=float,default=6.625)
    parser.add_argument("--trim-height",type=float,default=10.25)
    args=parser.parse_args()
    if args.trim_width<=0 or args.trim_height<=0:
        parser.error("Trim must be positive")
    inventory=json.loads((ROOT/"production/book-manifests.json").read_text())["issues"]
    drafts=json.loads((ROOT/"production/drafts/manifest.json").read_text())["drafts"]
    key=args.series+"::"+args.issue
    book=inventory.get(key)
    if not book or book.get("seriesId")!=args.series or book.get("issueId")!=args.issue:
        parser.error("Complete-book inventory not defined for "+key)
    units=book.get("units",[])
    if not units or len(units)!=len(set(units)):
        parser.error("No units or duplicate units in complete-book inventory")
    missing=[unit for unit in units if drafts.get(key+"::"+unit,{}).get("status")!="approved-production-draft"]
    if missing:
        parser.error("Incomplete book, missing approved units: "+", ".join(missing))
    out=Path(args.out).resolve()
    if out==DRAFTS or out.is_relative_to(DRAFTS):
        parser.error("Output cannot be inside approved drafts")
    out.mkdir(parents=True,exist_ok=True)
    stem=re.sub(r"[^a-z0-9-]+","-",args.series+"-"+args.issue).strip("-")
    pdf_file=out/(stem+".pdf")
    zip_file=out/(stem+".zip")
    page_w,page_h=args.trim_width*72,args.trim_height*72
    proof=Canvas(str(pdf_file),pagesize=(page_w,page_h),pageCompression=1,invariant=1)
    sources=[]; names=[]
    try:
        for index,unit in enumerate(units,1):
            entry=drafts[key+"::"+unit]
            source=(ROOT/entry.get("image","")).resolve()
            if not source.is_relative_to(DRAFTS) or not source.is_file():
                raise ValueError("Unsafe or missing source for "+unit)
            data=source.read_bytes()
            if data.startswith(b"version https://git-lfs.github.com/spec/v1"):
                raise ValueError("LFS pointer, not actual pixels: "+unit)
            digest=hashlib.sha256(data).hexdigest()
            if entry.get("sha256") and digest!=entry["sha256"].lower():
                raise ValueError("Source hash differs from manifest: "+unit)
            with Image.open(io.BytesIO(data)) as im:
                if im.format!=MIMES.get(entry.get("mimeType")):
                    raise ValueError("Image signature/MIME mismatch: "+unit)
                im.verify()
            with Image.open(io.BytesIO(data)) as im:
                width,height=im.size
                if width<1 or height<1:
                    raise ValueError("Zero image dimension: "+unit)
                # ImageReader preserves original JPEG stream when possible; other formats
                # are passed through as decoded pixels for PDF only. Original bytes go to ZIP.
                visual=ImageOps.exif_transpose(im)
                if visual.mode not in ("RGB","L"):
                    rgb=Image.new("RGB",visual.size,"white")
                    if "A" in visual.getbands():
                        rgb.paste(visual.convert("RGBA"),mask=visual.getchannel("A"))
                    else:
                        rgb.paste(visual.convert("RGB"))
                    visual=rgb
                view_w,view_h=visual.size
                scale=min(page_w/view_w,page_h/view_h)
                draw_w,draw_h=view_w*scale,view_h*scale
                proof.setFillColorRGB(1,1,1)
                proof.rect(0,0,page_w,page_h,fill=1,stroke=0)
                proof.drawImage(ImageReader(visual), (page_w-draw_w)/2,(page_h-draw_h)/2,
                                width=draw_w,height=draw_h)
                proof.showPage()
            ext=source.suffix.lower()
            name=f"pages/page-{index:03d}{ext}"
            if name in names:
                raise ValueError("Output name collision")
            names.append(name)
            sources.append((name,data,{
                "readingOrder":index,"recipeId":unit,"source":entry["image"],"outputFile":name,
                "nativeWidth":width,"nativeHeight":height,"mimeType":entry["mimeType"],
                "sha256":digest,
            }))
        proof.save()
        manifest={"schemaVersion":1,"seriesId":args.series,"issueId":args.issue,
                  "pageCount":len(units),"trimInches":[args.trim_width,args.trim_height],
                  "masteringStatus":"NOT APPROVED — review export only",
                  "pages":[metadata for _,_,metadata in sources]}
        with zipfile.ZipFile(zip_file,"w",allowZip64=True) as z:
            z.write(pdf_file,arcname=pdf_file.name,compress_type=zipfile.ZIP_STORED)
            z.writestr("book-export-manifest.json",json.dumps(manifest,indent=2)+"\n")
            for filename,data,_ in sources:
                z.writestr(filename,data,compress_type=zipfile.ZIP_STORED)
        with zipfile.ZipFile(zip_file) as z:
            if z.testzip() is not None:
                raise ValueError("ZIP integrity verification failed")
            parsed=json.loads(z.read("book-export-manifest.json"))
            if len(parsed["pages"])!=len(units) or len([n for n in z.namelist() if n.startswith("pages/")])!=len(units):
                raise ValueError("Packaged issue unit count mismatch")
            for name,data,meta in sources:
                if hashlib.sha256(z.read(name)).hexdigest()!=meta["sha256"]:
                    raise ValueError("Packed source differs from approved original: "+name)
        (out/"book-export-report.json").write_text(json.dumps(manifest,indent=2)+"\n")
    except BaseException:
        proof._pageNumber=max(proof._pageNumber,1)
        for temp in (pdf_file,zip_file):
            temp.unlink(missing_ok=True)
        raise
    print("Complete book exported:",key,len(units),"units")
    print("PDF:",pdf_file)
    print("ZIP:",zip_file)
    print("Mastering approval: NOT GRANTED")

if __name__=="__main__":
    main()
