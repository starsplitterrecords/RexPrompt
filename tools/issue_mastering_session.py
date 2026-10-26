#!/usr/bin/env python3
"""Issue-wide, non-destructive production mastering session.

Reuses master_issue_proofs.py, reads all pages in complete-book order, generates
source correction requirements and a locked-review template. No auto-approval.
"""
import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps

ROOT=Path(__file__).resolve().parents[1]
DRAFTS=(ROOT/"production/drafts").resolve()
FIELDS=["nativePixels","printGeometry","colorProfile","gradeIntent","letteringExact",
        "letteringSpeakerAndBalloonOrder","letteringAtPrintSize","continuity",
        "readerFlow","safeAreaAndBleed"]

def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def role(unit):
    s=unit.upper()
    if "COVER" in s or s.endswith("_P01") and s.startswith("VIK"):return "cover"
    if "CAST" in s:return "cast"
    if "ENDMATTER" in s:return "endmatter"
    if "EDITOR" in s:return "editorial"
    if "TEASER" in s:return "teaser"
    return "story"

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--series",required=True)
    parser.add_argument("--issue",required=True)
    parser.add_argument("--out",required=True)
    parser.add_argument("--profiles",default="production/mastering/publication-profiles.json")
    parser.add_argument("--profile",help="Explicit configured profile ID; overrides series mapping")
    parser.add_argument("--grade-plan",help="Optional explicit grade proposal; NEVER a release master")
    parser.add_argument("--native-tiles",action="store_true",help="Produce 1:1 pixel four-tile lettering inspection sheets")
    args=parser.parse_args()
    target=Path(args.out).resolve()
    if target==DRAFTS or target.is_relative_to(DRAFTS):
        parser.error("Output must be outside approved drafts")
    target.mkdir(parents=True,exist_ok=True)
    cfg=load(ROOT/args.profiles)
    profile_id=args.profile or cfg.get("seriesProfiles",{}).get(args.series)
    if profile_id not in cfg["profiles"]:
        parser.error("No explicit series publication profile; select and approve profile first")
    profile=cfg["profiles"][profile_id]
    trim=profile["trimInches"]
    bleed=profile["bleedInches"]
    dpi=profile["minNativeDpi"]
    req_w=math.ceil((trim["width"]+2*bleed)*dpi)
    req_h=math.ceil((trim["height"]+2*bleed)*dpi)
    safe=profile["safeInches"]
    if any(x<=0 for x in (trim["width"],trim["height"],dpi)) or bleed<0 or safe<0:
        parser.error("Invalid publication geometry")
    key=args.series+"::"+args.issue
    books=load(ROOT/"production/book-manifests.json")["issues"]
    book=books.get(key)
    if not book or not book.get("units") or len(book["units"])!=len(set(book["units"])):
        parser.error("Missing or duplicate complete-book units for "+key)
    cmd=[sys.executable,str(ROOT/"tools/master_issue_proofs.py"),
         "--series",args.series,"--issue",args.issue,"--out",str(target),
         "--trim-width",str(trim["width"]+2*bleed),
         "--trim-height",str(trim["height"]+2*bleed),
         "--min-dpi",str(dpi),"--allow-incomplete"]
    # This generates read-only statistics and contact sheet; any existing
    # ungraded look plan is NOT silently re-used as a master.
    task=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
    if task.returncode:
        parser.error("Underlying mastering preflight failed:\n"+task.stderr+"\n"+task.stdout)
    machine=load(target/"mastering-report.json")
    by_unit={x["recipeId"]:x for x in machine["pages"]}
    draft=load(ROOT/"production/drafts/manifest.json")["drafts"]
    warnings=machine["warnings"]; records=[]; corrections=[]
    look=load(args.grade_plan) if args.grade_plan else {}
    if not isinstance(look,dict) or set(look)-set(book["units"]):
        parser.error("Grade plan must use existing unit IDs only")
    swatches=[]
    for index,unit in enumerate(book["units"],1):
        item=by_unit.get(unit)
        info=draft.get(key+"::"+unit)
        issues=[]; instructions=[]
        if not item:
            issues.append("missing-or-undecodable-approved-image")
            instructions.append("Recover approved original binary or produce a separately reviewed replacement; do not substitute another page.")
        else:
            w=item["nativeWidth"];h=item["nativeHeight"]
            # An image may have adequate pixels yet lack bleed content;
            # geometry and safe lettering still demand visual approval.
            if w<req_w or h<req_h:
                issues.append("native-resolution-deficit")
                instructions.append(f"Locate an existing true native-resolution original or regenerate with genuine detail at >= {req_w}x{req_h} px for {trim['width']}x{trim['height']} in trim + {bleed} in bleed, {dpi} DPI. No enlargement, resampling, AI-upscale or sharpening as substitute.")
            expected_ratio=(trim["width"]+2*bleed)/(trim["height"]+2*bleed)
            if abs(w/h-expected_ratio)>profile["aspectTolerance"]:
                issues.append("geometry-aspect-review")
                instructions.append("Verify designed full-bleed crop and safe margins against publication geometry; do not automatically stretch, crop or distort.")
            if not item["iccEmbedded"]:
                issues.append("source-color-profile-unresolved")
                instructions.append("Determine source color interpretation from production evidence; never silently assign sRGB or CMYK.")
            if role(unit)=="cover":
                instructions.append("Verify front-cover typography/trim separately; spine/back-cover printer wrap remains unverified.")
            if args.native_tiles:
                source=(ROOT/info["image"]).resolve()
                if not source.is_relative_to(DRAFTS):parser.error("Image escaped approved drafts")
                with Image.open(source) as raw:
                    raw.load()
                    rgb=ImageOps.exif_transpose(raw).convert("RGB")
                    tile_dir=target/"lettering-tiles"/unit
                    tile_dir.mkdir(parents=True,exist_ok=True)
                    W,H=rgb.size
                    # Four exact native pixel crops; no resampling.
                    for t,(x0,y0,x1,y1) in enumerate([(0,0,math.ceil(W*.55),math.ceil(H*.55)),
                       (int(W*.45),0,W,math.ceil(H*.55)),
                       (0,int(H*.45),math.ceil(W*.55),H),
                       (int(W*.45),int(H*.45),W,H)],1):
                        rgb.crop((x0,y0,x1,y1)).save(tile_dir/f"tile-{t}.png")
        deviations=[x for x in warnings if x.startswith(unit+":") and ("outlier" in x)]
        if deviations:
            issues.append("palette-variation-requires-intent-review")
            instructions.append("Compare with adjacent pages, setting and scene lighting; record intentional difference or approve a specific restrained grade. Do not normalize to issue median.")
        if unit in look:
            grade=look[unit]
            if not isinstance(grade,dict) or any(k not in ("brightness","contrast","saturation") for k in grade):
                parser.error("Invalid grade plan for "+unit)
            if any(type(v) not in (int,float) or not 0.5<=v<=1.5 for v in grade.values()):
                parser.error("Grade factors must be in [0.5,1.5]")
            instructions.append("Grade adjustment is proposed ONLY. Make a comparison proof, confirm scene intent, and keep approved original untouched.")
        if not instructions:
            instructions.append("Inspect native pixels, full issue continuity, exact lettering, and print geometry; no automatic correction required.")
        # A present ICC is not proof of the intended press ICC.
        review={k:{"status":"pending","reviewer":None,"evidence":None} for k in FIELDS}
        rec={"readingOrder":index,"recipeId":unit,"role":role(unit),
             "source":item["source"] if item else None,"sourceSha256":item["sha256"] if item else None,
             "nativePixels":[item["nativeWidth"],item["nativeHeight"]] if item else None,
             "effectiveDpiOnBleedCanvas":item["effectiveDpiAtTrim"] if item else None,
             "machineDeficiencies":issues,"machineCorrectionRequirements":instructions,
             "gradeProposal":look.get(unit),"gradeProofSha256":None,"proposedColorDecision":"unreviewed",
             "review":review}
        records.append(rec)
        corrections.append((index,unit,rec["role"],issues,instructions))
        if item:
            swatches.append((unit,role(unit),item["meanLuminance"],item["meanSaturation"]))
    # Issue compare sheet per page class, not a numerical auto-grade policy
    canvas=Image.new("RGB",(1040,max(240,len(swatches)*26+88)),"#1d2229")
    draw=ImageDraw.Draw(canvas)
    draw.text((20,16),f"{key} — luminance/saturation diagnostic (not grade approval)",fill="white")
    draw.text((20,38),"Each bar is derived from a page thumbnail; visual intent is determined by reviewers.",fill="#bbc7d5")
    for i,(unit,category,luma,sat) in enumerate(swatches):
        y=68+i*26
        draw.text((20,y),unit[:29],fill="white")
        draw.text((245,y),category,fill="#c9d2db")
        draw.rectangle((335,y,335+int(luma*1.1),y+10),fill="#b4b7c0")
        draw.rectangle((655,y,655+int(sat*1.1),y+10),fill="#548fb0")
        draw.text((955,y),f"{luma:.0f}/{sat:.0f}",fill="white")
    canvas.save(target/"palette-diagnostic.png")
    report={
      "schemaVersion":2,"state":"needs-review","issue":key,
      "publicationProfile":profile_id,"profileDefinition":profile,
      "publicationGeometry":{"trimInches":[trim["width"],trim["height"]],
       "bleedInches":bleed,"safeInsetInches":safe,"minimumTrueNativeDpi":dpi,
       "minimumBleedCanvasPixels":[req_w,req_h]},
      "machine":{"expected":len(book["units"]),"inspected":len(by_unit),
       "errors":machine["errors"],"warnings":warnings,
       "sourceArtDeficiencies":sum(bool(set(x["machineDeficiencies"])&{"native-resolution-deficit","missing-or-undecodable-approved-image"}) for x in records),
       "toolsDefects":[]},
      "issueReviews":{k:{"status":"pending","reviewer":None,"evidence":None} for k in
          ["wholeBookFlow","crossPageCharacterAndCostume","crossPagePaletteIntent",
           "letteringAndEditorialContent","printTrimAndBleed","colorManagedProof",
           "frontBackCoverProduction","finalProofAtIntendedSize"]},
      "pressProof":{"printer":None,"outputIccFile":None,"outputIccSha256":None,
                    "printSpecificationApproval":None,"status":"unresolved"},
      "approval":{"status":"not-approved","reviewer":None,"approvedAt":None,
                  "fullIssueEvidence":None},
      "pages":records
    }
    (target/"mastering-session.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    def md(s):return str(s).replace("|","\\|").replace("\n"," ")
    lines=[f"# {key} — issue mastering corrections",
           f"\n**NOT MASTERED**. Full-book inventory: {len(records)} units; decoded sources {len(by_unit)}.",
           f"Working print canvas: {req_w} × {req_h} native px at {dpi} DPI including bleed.",
           "Machine source defects are distinct from implementation failures and manual visual review.","",
           "| Order | Unit / role | Machine findings | Exact corrective requirement |",
           "|---:|---|---|---|"]
    for index,unit,category,issues,instructions in corrections:
        lines.append(f"| {index} | {md(unit)} ({md(category)}) | {md(', '.join(issues) or 'no machine blocker')} | {md('; '.join(instructions))} |")
    lines+=["","\nAll lettering, dialogue ownership, intended grading and character continuity remain unapproved until native-pixel and complete-book review are recorded.","Original production draft files and approval states were not modified."]
    (target/"corrective-requirements.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps({"issue":key,"expectedUnits":len(records),"inspected":len(by_unit),
      "nativeSourceDeficiencies":report["machine"]["sourceArtDeficiencies"],
      "unresolvedSourceProfiles":sum("source-color-profile-unresolved" in x["machineDeficiencies"] for x in records),
      "correctiveReport":str(target/"corrective-requirements.md"),
      "masteringRecord":str(target/"mastering-session.json"),
      "status":"NOT MASTERED"},indent=2))
if __name__=="__main__":main()
