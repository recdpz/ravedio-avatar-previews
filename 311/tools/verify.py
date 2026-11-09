"""Compare final selected meshes with the previous Ponytail assemblies."""
from hashlib import sha256
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parent))
from build import ROOT, REV, front_parts, knit, read, read_glb, updos


def geometry(path):
    doc,data = read_glb(path)
    result = {}
    for node,rotation,offset in updos.node_transforms(doc):
        if "mesh" not in node:
            continue
        pts = [updos.vectors(doc,data,p["attributes"]["POSITION"])@rotation.T+offset
               for p in doc["meshes"][node["mesh"]]["primitives"]]
        result[node["name"]] = np.concatenate(pts)
    return result


def verify_exposed(bare,covered):
    parts = [(pos@r.T+offset,uv) for pos,_,uv,_,_,r,offset in
             front_parts(*read_glb(bare),"adjustable front")]
    base,uv = [np.concatenate(vals) for vals in zip(*parts,strict=True)]
    p,_,u,_,_,r,o = next(front_parts(*read_glb(covered),"front locks222"))
    fitted = p@r.T+o
    count = 0
    for side in (-1,1):
        a,b = (np.flatnonzero(g[:,0]*side>0) for g in (base,fitted))
        a = a[np.lexsort((uv[a,1],uv[a,0]))]
        b = b[np.lexsort((u[b,1],u[b,0]))]
        assert np.array_equal(uv[a],u[b])
        pts = base[a]
        theta = np.arctan2(pts[:,0],pts[:,2]-knit.CENTER[2])
        hem = knit.old.cap_ring(theta,0.)[:,1]
        visible = pts[:,1]<=hem
        assert np.allclose(pts[visible],fitted[b][visible],rtol=0,atol=3e-7)
        count += int(visible.sum())
    return count


def verify(before,after):
    assert before.keys()==after.keys() and len(after)==16
    report = read(REV/"verification/fit.json")
    checked = {}
    for key,parts in after.items():
        previous = before[key]
        head,finish = key.split("/")
        assert previous.keys()==parts.keys()
        expected = {"hair","hairLengths"} if head=="beanie" else {"hair"} if key in report["ties"] else set()
        assert {role for role in parts if parts[role]!=previous[role]}==expected,key
        if key not in report["ties"]:
            continue
        role = "hairLengths" if head=="beanie" else "hair"
        old,new = [geometry(ROOT/p[role]) for p in (previous,parts)]
        assert old.keys()==new.keys()
        for name in old:
            if "tie220" not in name:
                assert np.array_equal(old[name],new[name]),(key,name)
        if "headgear" in parts:
            tie = updos.surface(ROOT/parts[role],lambda n:"tie220" in n)
            hat = updos.surface(ROOT/parts["headgear"])
            assert not tie.overlap(hat),key
        if head=="beanie":
            crown = ROOT/parts["hair"]
            assert not updos.surface(ROOT/parts[role]).overlap(hat)
            assert updos.surface(ROOT/parts[role]).overlap(updos.surface(crown,lambda n:"roots220" in n))
            checked[finish] = verify_exposed(ROOT/report["fringe"][finish]["bareFringe"],crown)
    for file,digest in report["assets"].items():
        assert sha256((REV/"assets"/file).read_bytes()).hexdigest()==digest
    print("Verified 16 assembled selections and unchanged geometry of",checked,"exposed lock vertices",flush=True)


if __name__=="__main__":
    verify(*(read(Path(p)) for p in sys.argv[-2:]))
