#!/usr/bin/env python3
"""Mechanical gate for a human-reviewed issue mastering record.

A passing verifier checks evidence completeness and source integrity, but is
NOT a substitute for actual human visual, lettering or print review.
"""
import argparse
import hashlib
import json
import math
from PIL import Image
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DRAFTS=(ROOT/"production/drafts").resolve()
CHECKS=["nativePixels","printGeometry","colorProfile","gradeIntent","letteringExact",
"letteringSpeakerAndBalloonOrder","letteringAtPrintSize","continuity",
"readerFlow","safeAreaAndBleed"]
ISSUE_CHECKS=["wholeBookFlow","crossPageCharacterAndCostume","crossPagePaletteIntent",
"letteringAndEditorialContent","printTrimAndBleed","colorManagedProof",
"frontBackCoverProduction","finalProofAtIntendedSize"]

def verify(data,root=ROOT):
    errors=[]
    if data.get("schemaVersion")!=2:errors.append("Unknown mastering record schema")
    if data.get("state")!="reviewed":errors.append("Mastering session state must be reviewed, not draft")
    issue=data.get("issue","")
    bm=json.loads((root/"production/book-manifests.json").read_text())["issues"]
    approved=json.loads((root/"production/drafts/manifest.json").read_text())["drafts"]
    book=bm.get(issue)
    if not book:
        return ["Complete-book inventory not present for "+issue]
    profiles=json.loads((root/"production/mastering/publication-profiles.json").read_text())["profiles"]
    config=profiles.get(data.get("publicationProfile"))
    if not config:errors.append("Publication profile unresolved")
    elif config.get("status")!="printer-approved":
        errors.append("Publication profile is a working target, not printer-approved")
    geometry=config["trimInches"] if config else None
    need_w=math.ceil((geometry["width"]+2*config["bleedInches"])*config["minNativeDpi"]) if geometry else 0
    need_h=math.ceil((geometry["height"]+2*config["bleedInches"])*config["minNativeDpi"]) if geometry else 0
    expected=book["units"]
    records=data.get("pages",[])
    if [x.get("recipeId") for x in records]!=expected:
        errors.append("Mastering record page inventory/order differs from canonical complete book")
    if len({x.get("recipeId") for x in records})!=len(records):
        errors.append("Duplicate page unit")
    if data.get("machine",{}).get("errors"):
        errors.append("Machine preflight still contains errors")
    for item in records:
        unit=item.get("recipeId");key=issue+"::"+str(unit)
        source=approved.get(key)
        if not source or source.get("status")!="approved-production-draft":
            errors.append(str(unit)+": canonical approval status invalid");continue
        path=(root/source["image"]).resolve()
        if not path.is_relative_to((root/"production/drafts").resolve()) or not path.is_file():
            errors.append(str(unit)+": canonical image missing or unsafe");continue
        hash=hashlib.sha256(path.read_bytes()).hexdigest()
        if item.get("sourceSha256")!=hash:
            errors.append(str(unit)+": source image changed since recorded review")
        try:
            with Image.open(path) as im:
                if im.width<need_w or im.height<need_h:
                    errors.append(str(unit)+f": actual pixels {im.width}x{im.height} below native print canvas {need_w}x{need_h}")
                if not im.info.get("icc_profile"):
                    errors.append(str(unit)+": approved source still lacks embedded ICC; establish an independently approved color-managed replacement master")
        except Exception as exc:
            errors.append(str(unit)+": source cannot be decoded: "+str(exc))
        if item.get("machineDeficiencies"):
            errors.append(str(unit)+": unresolved source or machine deficiencies: "+",".join(item["machineDeficiencies"]))
        for name in CHECKS:
            check=item.get("review",{}).get(name,{})
            if check.get("status")!="pass" or not check.get("reviewer") or not check.get("evidence"):
                errors.append(f"{unit}: {name} requires documented human pass")
        if item.get("proposedColorDecision") not in ("approved-unchanged","approved-graded"):
            errors.append(str(unit)+": grading intent decision not approved")
        if item.get("proposedColorDecision")=="approved-graded" and not item.get("gradeProofSha256"):
            errors.append(str(unit)+": graded proof source/approval checksum missing")
    for k in ISSUE_CHECKS:
        check=data.get("issueReviews",{}).get(k,{})
        if check.get("status")!="pass" or not check.get("reviewer") or not check.get("evidence"):
            errors.append("Whole issue: "+k+" requires documented human pass")
    press=data.get("pressProof",{})
    if not all(press.get(x) for x in ("printer","outputIccFile","outputIccSha256","printSpecificationApproval")):
        errors.append("Printer, verified press ICC, and publication specification approval required")
    else:
        icc=(root/press["outputIccFile"]).resolve()
        if not icc.is_relative_to(root.resolve()) or not icc.is_file():
            errors.append("Press ICC file missing or unsafe")
        elif hashlib.sha256(icc.read_bytes()).hexdigest()!=press["outputIccSha256"]:
            errors.append("Press ICC SHA mismatch")
    sign=data.get("approval",{})
    if sign.get("status")!="approved" or not all(sign.get(k) for k in ("reviewer","approvedAt","fullIssueEvidence")):
        errors.append("Signed issue-wide final approval absent")
    return errors

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--record",required=True)
    a=p.parse_args()
    rec=json.loads(Path(a.record).read_text())
    errors=verify(rec)
    for e in errors:print("BLOCK "+e)
    print(f"Mastering gate: {'PASS (documentary and source-integrity gate only)' if not errors else f'BLOCKED ({len(errors)} requirements)'}")
    raise SystemExit(bool(errors))
if __name__=="__main__":main()
