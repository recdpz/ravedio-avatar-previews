"""Verify the exported Ponytail attachments against resolved viewer selections."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import sys

from mathutils.kdtree import KDTree
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parent))
from build import (CENTER, ROOT, REV, Mesh, coverage, geometry, is_tail, is_tie,
                   joined, knit, read, read_glb, spin, updos, write)


@lru_cache(maxsize=25)
def ordinary(path):
    return updos.surface(ROOT/path)


@lru_cache(maxsize=16)
def tail(path):
    parts = [Mesh(*values) for values in geometry(*read_glb(ROOT/path))]
    mesh = joined([(p,p.world) for p in parts if is_tail(p) or is_tie(p)])
    anchor = next(p.world.mean(0) for p in parts if is_tie(p))
    return mesh,anchor


def verify(before,after,wardrobe_before,wardrobe, *, revision=REV, ranges=None):
    assert before.keys()==after.keys() and len(after)==16
    assert wardrobe_before.keys()==wardrobe.keys() and len(wardrobe)==128
    report = read(revision/"verification/fit.json")
    for name,digest in report["assets"].items():
        assert sha256((revision/"assets"/name).read_bytes()).hexdigest()==digest
    for key,parts in after.items():
        previous = before[key]
        head,finish = key.split("/")
        assert previous.keys()==parts.keys()
        expected = {"hair"} if head!="pashmina" else set()
        if head=="beanie":
            expected.add("hairLengths")
        elif head=="headband":
            expected.add("headgear")
        assert {role for role in parts if parts[role]!=previous[role]}==expected,key
        if head=="pashmina":
            continue
        checks = report["fits"][key]
        role = "hairLengths" if head=="beanie" else "hair"
        bundle,anchor = tail(parts[role])
        lower,upper = ranges[head] if ranges is not None else (.052,.125)
        assert lower<anchor[0]<upper and abs(anchor[0]-checks["toX"])<1e-5,(key,anchor[0])
        if "headgear" in parts:
            assert not bundle.overlap(ordinary(parts["headgear"])),key
        crown = updos.surface(ROOT/parts["hair"],lambda n:"roots220" in n)
        head_mesh = updos.surface(ROOT/parts["base"],lambda n:"soft oval head" in n)
        assert bundle.overlap(crown),key
        assert coverage(crown,head_mesh,anchor)[0]==0,key
        old_mesh,new_mesh = [[Mesh(*values) for values in geometry(*read_glb(ROOT/p[role]))]
                             for p in (previous,parts)]
        old_parts,new_parts = [{p.name:p for p in meshes if is_tail(p) or is_tie(p)}
                               for meshes in (old_mesh,new_mesh)]
        assert old_parts.keys()==new_parts.keys()
        pitch = updos.axis_rotation("x",np.deg2rad(checks["pitchDegrees"]))
        for name,old in old_parts.items():
            new = new_parts[name]
            predicted = spin(CENTER+(old.world-CENTER)@pitch.T,np.deg2rad(checks["yawDegrees"]))
            assert np.allclose(new.world,predicted,rtol=0.,atol=1e-5),(key,name)
        if head=="beanie":
            doc,data = read_glb(ROOT/parts["hair"])
            fringe = next(p for p in (Mesh(*values) for values in geometry(doc,data)) if "front locks222" in p.name)
            p = fringe.world
            assert np.isfinite(fringe.nor).all()
            # The visible lengths beyond the initial release retain their sculpt.
            bare = np.concatenate([m.world for m in (Mesh(*v) for v in
                                   geometry(*read_glb(ROOT/before["none/default"]["hair"])))
                                   if "adjustable front" in m.name])
            theta = np.arctan2(p[:,0],p[:,2]-CENTER[2])
            released = p[p[:,1]<knit.old.cap_ring(theta,0.)[:,1]-.115]
            spatial = KDTree(len(bare))
            for i,point in enumerate(bare):
                spatial.insert(point,i)
            spatial.balance()
            distance = max(spatial.find(point)[2] for point in released)
            assert distance<4e-7, (key,distance)

    checked = 0
    for key,parts in wardrobe.items():
        head,finish,_ = key.split("/")
        assert parts.keys()==wardrobe_before[key].keys()
        if head=="pashmina":
            assert parts==wardrobe_before[key]
            continue
        role = "hairLengths" if head=="beanie" else "hair"
        assert parts[role]==after[head+"/"+finish][role],key
        bundle,_ = tail(parts[role])
        for layer in ("top","extra"):
            assert not bundle.overlap(ordinary(parts[layer])),(key,layer)
        checked += 1
    write(revision/"verification/checks.json",{"headwearAndFinishSelections":len(after),
          "outfitSelections":len(wardrobe),"repositionedTailClearanceChecks":checked})
    print("Verified",len(after),"headwear/finish selections and",len(wardrobe),
          "outfits including the sprout and all eight tops",flush=True)


if __name__=="__main__":
    verify(*(read(Path(p)) for p in sys.argv[-4:]))
