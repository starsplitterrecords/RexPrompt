#!/usr/bin/env python3
"""Synthetic passing and adversarial negative checks for mastering approval gate."""
import copy
import hashlib
import io
import json
import tempfile
from pathlib import Path
from PIL import Image, ImageCms
from verify_mastering_approval import CHECKS, ISSUE_CHECKS, verify

def write_json(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2)+"\n")

def valid(root):
    root=Path(root)
    image=root/"production/drafts/test-series/test-issue/UNIT1.png"
    image.parent.mkdir(parents=True,exist_ok=True)
    icc=ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
    im=Image.new("RGB",(2100,3200),"#323747")
    im.save(image,icc_profile=icc)
    press=root/"production/mastering/press-icc/srgb-fixture.icc"
    press.parent.mkdir(parents=True,exist_ok=True)
    press.write_bytes(icc)
    sha=hashlib.sha256(image.read_bytes()).hexdigest()
    profile={"status":"printer-approved","trimInches":{"width":6.625,"height":10.25},
             "bleedInches":0.125,"minNativeDpi":300}
    write_json(root/"production/mastering/publication-profiles.json",{"profiles":{"synthetic":profile}})
    write_json(root/"production/book-manifests.json",{"issues":{"test-series::test-issue":{"units":["UNIT1"]}}})
    write_json(root/"production/drafts/manifest.json",{"drafts":{"test-series::test-issue::UNIT1":{
             "status":"approved-production-draft","image":"production/drafts/test-series/test-issue/UNIT1.png"}}})
    review={k:{"status":"pass","reviewer":"Synthetic Test Reviewer","evidence":"Fixture review only"} for k in CHECKS}
    issue={k:{"status":"pass","reviewer":"Synthetic Test Reviewer","evidence":"Fixture review only"} for k in ISSUE_CHECKS}
    record={
      "schemaVersion":2,"state":"reviewed","issue":"test-series::test-issue",
      "publicationProfile":"synthetic","machine":{"errors":[]},
      "pages":[{"recipeId":"UNIT1","sourceSha256":sha,"machineDeficiencies":[],
                "review":review,"proposedColorDecision":"approved-unchanged"}],
      "issueReviews":issue,
      "pressProof":{"printer":"Synthetic print fixture", "outputIccFile":"production/mastering/press-icc/srgb-fixture.icc",
                    "outputIccSha256":hashlib.sha256(icc).hexdigest(),
                    "printSpecificationApproval":"Fixture only; technical gate test"},
      "approval":{"status":"approved","reviewer":"Synthetic Test Reviewer",
                  "approvedAt":"2026-10-25","fullIssueEvidence":"Fixture only"}
    }
    return record,image

def main():
    with tempfile.TemporaryDirectory() as tmp:
        r,image=valid(tmp)
        assert verify(r,Path(tmp))==[], "Valid synthetic fixture must pass documentary gate"
        print("PASS synthetic full signoff with matching actual source pixels")
        cases=[
          ("missing-lettering",lambda x:x["pages"][0]["review"]["letteringExact"].update(status="pending")),
          ("no-whole-book",lambda x:x["issueReviews"]["wholeBookFlow"].update(status="pending")),
          ("no-approval",lambda x:x["approval"].update(status="not-approved")),
          ("pending-press-profile",lambda x:x.update(publicationProfile="unapproved")),
          ("source-defect",lambda x:x["pages"][0]["machineDeficiencies"].append("native-resolution-deficit")),
          ("changed-hash",lambda x:x["pages"][0].update(sourceSha256="bad-hash")),
          ("wrong-page-order",lambda x:x["pages"][0].update(recipeId="WRONG")),
          ("intentional-variation-without-review",lambda x:x["pages"][0]["review"]["gradeIntent"].update(status="pending")),
          ("missing-proof",lambda x:x["pages"][0].update(proposedColorDecision="approved-graded",gradeProofSha256=None))
        ]
        for name,mutate in cases:
            bad=copy.deepcopy(r);mutate(bad)
            assert verify(bad,Path(tmp)),name+" accidentally passed"
            print("BLOCKED",name)
        r["pages"][0]["machineDeficiencies"]=["palette-variation-requires-intent-review",
                                                "geometry-aspect-review"]
        assert verify(r,Path(tmp))==[], "Documented intentional grading/geometry variance must be accepted"
        print("PASS intentional artistic variance with actual reviewer signoff")
        image.write_bytes(b"corrupt")
        assert verify(r,Path(tmp)), "Source corruption must be detected"
        print("BLOCKED changed source bytes")
if __name__=="__main__":main()
