"""Check catalogue resolution, topology, and low-cloth contact after the rebuild."""
import json
import sys
from pathlib import Path

import numpy as np
from mathutils.bvhtree import BVHTree

sys.path.insert(0,str(Path(__file__).resolve().parent))
from tailor import accessor, local_path, node_transforms, read_glb, triangles
from fit import sha


def read(path):
    return json.loads(path.read_text(encoding="utf8"))


def geometries(path):
    model,binary=read_glb(path)
    for node,rotation,offset in node_transforms(model):
        if "mesh" not in node:
            continue
        mesh=model["meshes"][node["mesh"]]
        for p in mesh["primitives"]:
            a=p["attributes"]
            xyz=accessor(model,binary,a["POSITION"],3)@rotation.T+offset
            normal=accessor(model,binary,a["NORMAL"],3)
            faces=triangles(model,binary,p["indices"])
            assert np.isfinite(xyz).all() and np.isfinite(normal).all()
            yield mesh["name"],xyz,faces


def bvh(points,faces):
    return BVHTree.FromPolygons(points.tolist(),faces.tolist(),all_triangles=True)


def check_overlap(path,cloth):
    count=0
    for _,p,f in geometries(path):
        mask=p[f,1].min(axis=1)<1.66
        if mask.any():
            count+=len({i for i,_ in bvh(p,f[mask]).overlap(cloth)})
    return count


def textile(path):
    name,positions,tri=next((n,p,f) for n,p,f in geometries(path) if "joined hood" in n)
    edges=np.sort(np.concatenate((tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]])),axis=1)
    _,counts=np.unique(edges,axis=0,return_counts=True)
    assert np.all(counts==2), path
    low=tri[positions[tri,1].min(axis=1)<1.60]
    cloth=bvh(positions,low)
    _,weld=np.unique(positions.round(5),axis=0,return_inverse=True)
    faces=weld[low]
    pairs=np.asarray([(a,b) for a,b in cloth.overlap(cloth) if a<b],dtype=int).reshape(-1,2)
    nonlocal_pairs=np.zeros((0,2),dtype=int)
    if len(pairs):
        shared=(faces[pairs[:,0],:,None]==faces[pairs[:,1],None,:]).any(axis=(1,2))
        nonlocal_pairs=pairs[~shared]
    mid=positions[low[np.unique(nonlocal_pairs)]].mean(axis=1) if len(nonlocal_pairs) else np.zeros((0,3))
    return cloth,len(nonlocal_pairs),int(np.sum(mid[:,2]<-.06)),len(tri)


def verify(source, candidate, destination):
    def index(path):
        return {(r["build"],r["hair"],r["top"]):r["parts"] for r in read(path)}
    old,new=index(source),index(candidate)
    assert old.keys()==new.keys() and len(new)==112
    records=[]
    for (build,hair,top),parts in new.items():
        previous=old[build,hair,top]
        assert parts.keys()==previous.keys()
        edited={"headgear"}
        if build=="Feminine" and hair in {"curls","box-braids","bob","straight"}:
            edited.add("hair")
        assert {k for k in parts if parts[k]!=previous[k]}==edited
        path=local_path(parts["headgear"])
        old_model,old_bin=read_glb(local_path(previous["headgear"]))
        new_model,new_bin=read_glb(path)
        assert old_model["materials"]==new_model["materials"]
        def image(model,data):
            view=model["bufferViews"][model["images"][0]["bufferView"]]
            a=view.get("byteOffset",0)
            return data[a:a+view["byteLength"]]
        assert image(old_model,old_bin)==image(new_model,new_bin)
        cloth,contacts,rear,triangles_count=textile(path)
        checked={k:check_overlap(local_path(parts[k]),cloth) for k in ("base","top","hair","hairLengths") if k in parts}
        records.append({"build":build,"hair":hair,"top":top,"sha256":sha(path),
                        "triangles":triangles_count,"lower_self_contact_pairs":contacts,
                        "rear_contact_vertices":rear,"neighbor_contact_triangles":checked})
    destination.write_text(json.dumps({"assemblies":records},indent=2)+"\n",encoding="utf8")
    print("Checked",len(records),"closed assemblies")


if __name__=="__main__":
    verify(*map(Path,sys.argv[-3:]))
