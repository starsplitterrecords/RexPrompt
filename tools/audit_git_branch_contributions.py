#!/usr/bin/env python3
"""Read-only PR-aware comparison of every retained branch against current main."""
import argparse,collections,json,os,pathlib,subprocess,urllib.request
def git(repo,*args,check=True):
    p=subprocess.run(["git","-C",str(repo),*args],capture_output=True,text=True)
    if check and p.returncode:raise RuntimeError("git "+" ".join(args)+": "+p.stderr[:700])
    return p
def fetch_prs(slug):
    records=[]; page=1
    while True:
        uri="https://api.github.com/repos/"+slug+"/pulls?state=all&per_page=100&page="+str(page)
        headers={"Accept":"application/vnd.github+json","User-Agent":"StarSplitter-COS-reconciliation"}
        if os.getenv("GITHUB_TOKEN"):headers["Authorization"]="Bearer "+os.environ["GITHUB_TOKEN"]
        with urllib.request.urlopen(urllib.request.Request(uri,headers=headers),timeout=30) as response:batch=json.load(response)
        if not isinstance(batch,list):raise RuntimeError("Invalid PR response")
        records.extend(batch)
        if len(batch)<100:break
        page+=1
        if page>30:raise RuntimeError("PR pagination exceeded bound")
    return records
def scan(repo,slug,decisions):
    repo=repo.resolve();baseline_ref="refs/remotes/origin/main"
    git(repo,"fetch","--no-tags","--quiet","origin","+refs/heads/*:refs/remotes/origin/*")
    baseline=git(repo,"rev-parse",baseline_ref).stdout.strip()
    prs=fetch_prs(slug)
    bybranch=collections.defaultdict(list)
    for pr in prs:
        name=(pr.get("head") or {}).get("ref")
        if name:bybranch[name].append(pr)
    closed=[p for p in prs if p["state"]=="closed" and not p.get("merged_at")]
    missing=[p["number"] for p in closed if str(p["number"]) not in decisions]
    if missing:raise RuntimeError("Closed PR dispositions missing: "+str(missing))
    names=git(repo,"for-each-ref","--format=%(refname:short)","refs/remotes/origin").stdout.splitlines()
    rows=[]
    for name in sorted(set(names)):
        if not name.startswith("origin/") or name in ("origin/main","origin/HEAD"):continue
        branch=name.removeprefix("origin/");head=git(repo,"rev-parse",name).stdout.strip()
        ancestor=git(repo,"merge-base","--is-ancestor",head,baseline,check=False).returncode==0
        same=git(repo,"diff","--no-renames","--quiet",baseline,head,check=False).returncode==0
        parts=git(repo,"rev-list","--left-right","--count",baseline_ref+"..."+name).stdout.split()
        behind,ahead=(int(parts[0]),int(parts[1])) if len(parts)==2 else (-1,-1)
        files=[{"status":line.split("\t",1)[0],"path":line.split("\t",1)[1]}
               for line in git(repo,"diff","--no-renames","--name-status",baseline,head).stdout.splitlines() if "\t" in line]
        related=[]
        for pr in bybranch.get(branch,[]):
            merge=pr.get("merge_commit_sha")
            onmain=bool(merge and git(repo,"merge-base","--is-ancestor",merge,baseline,check=False).returncode==0)
            related.append({"number":pr["number"],"title":pr["title"],"state":pr["state"],
                            "mergedAt":pr.get("merged_at"),"mergeCommitOnMain":onmain,
                            "recordedHeadMatchesBranch":(pr.get("head") or {}).get("sha")==head,
                            "manualDisposition":decisions.get(str(pr["number"]))})
        merged=next((p for p in related if p["mergedAt"] and p["mergeCommitOnMain"] and p["recordedHeadMatchesBranch"]),None)
        closed_match=next((p for p in related if p["state"]=="closed" and not p["mergedAt"] and p["recordedHeadMatchesBranch"]),None)
        if ancestor:status="incorporated-by-history"
        elif same:status="tree-equivalent-to-main"
        elif merged:status="incorporated-via-merged-pr"
        elif closed_match:status="closed-pr-"+closed_match["manualDisposition"]
        elif related:status="related-pr-divergence-retained"
        else:status="unlinked-divergence-retained"
        rows.append({"branch":branch,"head":head,"status":status,"aheadCommits":ahead,
                     "behindCommits":behind,"differentFileCount":len(files),"files":files,"relatedPullRequests":related})
    groups=collections.defaultdict(list)
    for r in rows:groups[r["head"]].append(r["branch"])
    return {"repo":slug,"baseline":"origin/main","baselineSha":baseline,
            "branchCount":len(rows),"prsAnalyzed":len(prs),"closedUnmergedPrsReviewed":len(closed),
            "classifications":dict(collections.Counter(x["status"] for x in rows)),
            "identicalTipGroups":[v for v in groups.values() if len(v)>1],
            "branches":rows,"disclaimer":"Divergence alone does not prove missing or approved work."}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo",type=pathlib.Path,required=True)
    p.add_argument("--slug",required=True)
    p.add_argument("--decisions",type=pathlib.Path,required=True)
    p.add_argument("--out",type=pathlib.Path,required=True)
    a=p.parse_args();d=json.loads(a.decisions.read_text())[a.slug];r=scan(a.repo,a.slug,d)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    print(a.slug,r["baselineSha"],"branches",r["branchCount"],"PRs",r["prsAnalyzed"],"classification",r["classifications"])
    if r["branchCount"]<30:raise SystemExit("Incomplete history")
if __name__=="__main__":main()
