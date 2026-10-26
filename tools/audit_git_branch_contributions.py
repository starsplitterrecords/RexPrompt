#!/usr/bin/env python3
"""Read-only full-branch divergence inventory; differing trees never imply approval."""
import argparse,collections,json,pathlib,subprocess
def git(repo,*args,check=True):
    p=subprocess.run(["git","-C",str(repo),*args],capture_output=True,text=True)
    if check and p.returncode: raise RuntimeError("git "+" ".join(args)+": "+p.stderr[:700])
    return p
def scan(repo):
    repo=repo.resolve(); base="refs/remotes/origin/main"
    git(repo,"fetch","--no-tags","--quiet","origin","+refs/heads/*:refs/remotes/origin/*")
    baseline=git(repo,"rev-parse",base).stdout.strip()
    names=git(repo,"for-each-ref","--format=%(refname:short)","refs/remotes/origin").stdout.splitlines()
    rows=[]
    for name in sorted(set(names)):
        if not name.startswith("origin/") or name in ("origin/main","origin/HEAD"):continue
        head=git(repo,"rev-parse",name).stdout.strip()
        ancestor=git(repo,"merge-base","--is-ancestor",head,baseline,check=False).returncode==0
        same=git(repo,"diff","--quiet",baseline,head,check=False).returncode==0
        divergence=git(repo,"rev-list","--left-right","--count",base+"..."+name).stdout.split()
        behind,ahead=(int(divergence[0]),int(divergence[1])) if len(divergence)==2 else (-1,-1)
        files=[{"status":line.split("\t",1)[0],"path":line.split("\t",1)[1]} for line in
               git(repo,"diff","--no-renames","--name-status",baseline,head).stdout.splitlines() if "\t" in line]
        status="incorporated-by-history" if ancestor else "tree-equivalent-to-main" if same else "divergent-retained-pending-evidence"
        rows.append({"branch":name.removeprefix("origin/"),"head":head,"status":status,
                     "aheadCommits":ahead,"behindCommits":behind,"differentFileCount":len(files),"files":files})
    bysha=collections.defaultdict(list)
    for r in rows:bysha[r["head"]].append(r["branch"])
    return {"baseline":"origin/main","baselineSha":baseline,"branchCount":len(rows),
            "classifications":dict(collections.Counter(r["status"] for r in rows)),
            "identicalTipGroups":[v for v in bysha.values() if len(v)>1],
            "branches":rows,
            "disclaimer":"Divergent means differing tree content, not necessarily missing or approved work."}
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--repo",type=pathlib.Path,required=True)
    parser.add_argument("--out",type=pathlib.Path,required=True)
    args=parser.parse_args();r=scan(args.repo)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    print(args.repo,r["baselineSha"],"branches",r["branchCount"],r["classifications"])
    if r["branchCount"]<30:raise SystemExit("Incomplete branch history")
if __name__=="__main__":main()
