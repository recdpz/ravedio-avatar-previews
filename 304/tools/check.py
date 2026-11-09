"""Verify only requested components resolve differently and measure braid clearances."""
import json
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parent))
from braids import REV
from fit import geometry, local_path, read_glb, surface, tree


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def verify(before, after):
    assert len(before)==len(after)==60
    assets={}
    for previous,current in zip(before,after,strict=True):
        assert previous["features"]==current["features"] and previous["build"]==current["build"]
        a,b=previous["components"],current["components"]
        assert a.keys()==b.keys()
        f=current["features"]
        hair,hat,color=f["hair"],f["headwear"],f["hairColor"]
        edits=(hair=="box-braids" and hat in {"none","pashmina"}) or (hair=="ponytail" and color=="ombre")
        expected={"hair"} if edits else set()
        assert {role for role in a if local_path(a[role])!=local_path(b[role])}==expected,(f,a,b)
        if edits:
            assets[local_path(b["hair"])]=(local_path(a["hair"]),hair)
    assert len(assets)==12
    for target,(source,style) in assets.items():
        old_doc,old=read_glb(source)
        new_doc,new=read_glb(target)
        assert old_doc["nodes"]==new_doc["nodes"]
        assert old_doc["meshes"]==new_doc["meshes"]
        for a,b in zip(geometry(old_doc,old),geometry(new_doc,new),strict=True):
            assert np.array_equal(a[-1],b[-1])
            assert np.isfinite(b[2]).all() and np.isfinite(b[3]).all()
            assert np.max(abs(np.linalg.norm(b[3],axis=1)-1))<.005
            if style=="ponytail":
                assert np.array_equal(a[2],b[2]) and np.array_equal(a[3],b[3])
        if style=="box-braids":
            assert old_doc["materials"]==new_doc["materials"]


def lower_fit(rows):
    audits=[]
    for hat in ("none","pashmina"):
        choices=[row for row in rows if row["features"]["hair"]=="box-braids"
            and row["features"]["headwear"]==hat and row["features"]["hairColor"]=="default"]
        parts=[]
        for _,_,p,_,rotation,offset,faces in geometry(*read_glb(local_path(choices[0]["components"]["hair"]))):
            world=p@rotation.T+offset
            front=faces[(world[faces,1].min(axis=1)<1.90)&(world[faces,2].mean(axis=1)>0)]
            parts.append(tree(world,front))
        for row in choices:
            receipt={}
            for role in ("base","top","headgear"):
                source=row["components"].get(role)
                if not source:
                    continue
                neighbor=surface(local_path(source))
                count=0
                for hair in parts:
                    ids={a for a,_ in hair.overlap(neighbor)}
                    count+=len(ids)
                receipt[role]=count
            if hat=="pashmina":
                assert receipt["headgear"]==receipt["top"]==0,(row["features"],receipt)
            audits.append({"headwear":hat,"top":row["features"]["top"],"front_triangle_contacts":receipt})
    return audits


if __name__=="__main__":
    before,after=map(load,map(Path,sys.argv[-2:]))
    verify(before,after)
    results={"browser_selections":len(after),"revised_hair_glbs":12,"braid_contact_checks":lower_fit(after)}
    (REV/"verification/fit.json").write_text(json.dumps(results,indent=2)+"\n",encoding="utf-8")
    print("Verified 60 selections, 12 revised exports and 16 braid and top fits")
