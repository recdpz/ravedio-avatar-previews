"""Check that 317 changes the fitted crown and shared mustache without collateral edits."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"315/tools"))
from export import read_glb


def points(doc,data,prim,channel):
    spec=doc["accessors"][prim["attributes"][channel]]
    view=doc["bufferViews"][spec["bufferView"]]
    assert spec["componentType"]==5126
    columns=int(spec["type"][-1])
    start=view.get("byteOffset",0)+spec.get("byteOffset",0)
    return np.ndarray((spec["count"],columns),dtype="<f4",buffer=data,offset=start,
                      strides=(view.get("byteStride",columns*4),4))


def indices(doc,data,prim):
    spec=doc["accessors"][prim["indices"]]
    view=doc["bufferViews"][spec["bufferView"]]
    types={5123:"<u2",5125:"<u4"}
    start=view.get("byteOffset",0)+spec.get("byteOffset",0)
    return np.frombuffer(data,dtype=types[spec["componentType"]],offset=start,count=spec["count"]).reshape(-1,3)


def embedded_images(doc,data):
    return [data[v.get("byteOffset",0):v.get("byteOffset",0)+v["byteLength"]]
            for img in doc.get("images",[]) if "bufferView" in img
            for v in [doc["bufferViews"][img["bufferView"]]]]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("output",type=Path)
    a=p.parse_args()
    data=json.loads((a.output/"source.json").read_bytes())
    checks={}
    for path,replacement in data["replacement_assets"].items():
        name=replacement["file"]
        before,old_bin=read_glb((ROOT/path).read_bytes())
        blob=(a.output/"assets"/name).read_bytes()
        assert hashlib.sha256(blob).hexdigest()==replacement["sha256"]
        after,new_bin=read_glb(blob)
        assert embedded_images(before,old_bin)==embedded_images(after,new_bin)
        if name.startswith("sprout-"):
            assert old_bin==new_bin
            checks[name]={"binary_unchanged":True}
            continue
        assert before["nodes"]==after["nodes"]
        y_before,y_after=[],[]
        for old_mesh,new_mesh in zip(before["meshes"],after["meshes"],strict=True):
            if name=="groom-long.glb" and "rounded long" in old_mesh["name"]:
                a_prim,=old_mesh["primitives"]
                opaque,soft=new_mesh["primitives"]
                a_pts=points(before,old_bin,a_prim,"POSITION")
                for b_prim in (opaque,soft):
                    assert np.array_equal(a_pts,points(after,new_bin,b_prim,"POSITION"))
                original=indices(before,old_bin,a_prim)
                joined=np.concatenate([indices(after,new_bin,p) for p in (opaque,soft)])
                assert sorted(map(tuple,original.tolist()))==sorted(map(tuple,joined.tolist()))
                assert after["materials"][opaque["material"]].get("alphaMode","OPAQUE")=="OPAQUE"
                assert after["materials"][soft["material"]]["alphaMode"]=="BLEND"
                alpha=points(after,new_bin,soft,"COLOR_0")[:,3]
                assert .0 < alpha.min() < .5 and alpha.max()==1
                continue
            for a_prim,b_prim in zip(old_mesh["primitives"],new_mesh["primitives"],strict=True):
                assert a_prim["indices"]==b_prim["indices"]
                a_pts=points(before,old_bin,a_prim,"POSITION")
                b_pts=points(after,new_bin,b_prim,"POSITION")
                if name.startswith("beanie-"):
                    mask=a_pts[:,1]<=2.045
                    assert np.array_equal(a_pts[mask],b_pts[mask]),name
                    if "TEXCOORD_0" in a_prim["attributes"]:
                        assert np.array_equal(points(before,old_bin,a_prim,"TEXCOORD_0"),
                                              points(after,new_bin,b_prim,"TEXCOORD_0"))
                    y_before.append(float(a_pts[:,1].max()))
                    y_after.append(float(b_pts[:,1].max()))
                elif "shared mustache" in old_mesh["name"]:
                    assert np.ptp(b_pts[:,0])<np.ptp(a_pts[:,0])
                    checks[name]={"mustache_width_before":float(np.ptp(a_pts[:,0])),
                                  "mustache_width_after":float(np.ptp(b_pts[:,0]))}
                else:
                    assert np.array_equal(a_pts,b_pts),name
                    if name=="groom-short.glb":
                        alpha=points(after,new_bin,b_prim,"COLOR_0")[:,3]
                        assert .0 < alpha.min() < .5 and alpha.max()==1
        if y_before:
            checks[name]={"crown_apex_drop":round(max(y_before)-max(y_after),6),"cuff_exact":True}
    assert len(checks)==37
    (a.output/"asset-checks.json").write_text(json.dumps(checks,indent=2)+"\n",newline="\n")
    print("Verified 37 GLBs, cuff geometry, embedded knit and taper textures, and unrelated beard geometry")


if __name__=="__main__":
    main()
