"""Fit the uncovered curved Ponytail under the beanie using one rigid pose."""
import importlib.util
from itertools import product
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"300/tools"))
from tailor import compact

spec=importlib.util.spec_from_file_location("updos274",ROOT/"274/tools/fit_updos.py")
updos=importlib.util.module_from_spec(spec)
spec.loader.exec_module(updos)


def attachment(name):
    return "rounded tail220" in name or "tie220" in name


def fitted_crown(name):
    return "roots220" in name or "front locks222" in name


def isolate(source, target, keep):
    model,data=updos.read_glb(source)
    for node in model["nodes"]:
        if "mesh" in node and not keep(node.get("name","")):
            del node["mesh"]
    assert any("mesh" in node for node in model["nodes"])
    model.setdefault("images",[])
    payload=compact(model,data)
    if not model["images"]:
        del model["images"]
    updos.write_glb(target,model,payload)


def pose_tail(uncovered, beanie_hair, beanie):
    _,_,parts=updos.load_parts(uncovered,"ponytail")
    vertices,faces=updos.group_geometry(parts,1)
    elastic=next(p["points"].mean(0) for p in parts if "tie220" in p["name"])
    scalp=updos.surface(beanie_hair,lambda n:"roots220" in n)
    hat=updos.surface(beanie)
    options=[]
    for tie_pitch,yaw,slope,roll in product(
        (-.87,-.92,-.97,-1.02,-1.07,-1.12,-1.17),
        (0.,-.10,.10,-.20,.20),
        (-.14,-.20,-.26,-.32,-.38,-.44,-.50),
        (0.,-.12,.12),
    ):
        # Rotate the tie to the nape, then orient the existing bundle about
        # that tie. Keeping both transforms rigid preserves all lock shapes.
        place=updos.axis_rotation("y",yaw)@updos.axis_rotation("x",tie_pitch)
        root=updos.apply(elastic,place,np.zeros(3))
        rotation=updos.axis_rotation("y",yaw)@updos.axis_rotation("x",slope)
        rotation=updos.axis_rotation("z",roll)@rotation
        offset=root-updos.apply(elastic,rotation,np.zeros(3))
        moved=updos.apply(vertices,rotation,offset)
        if moved[:,1].min()<1.49 or moved[:,2].min()<-.62:
            continue
        score=abs(slope+.20)*1.8+abs(yaw)+abs(roll)+.5*abs(tie_pitch+.94)
        options.append((score,tie_pitch,yaw,slope,roll,root,rotation,offset))
    for _,tie_pitch,yaw,slope,roll,root,rotation,offset in sorted(options,key=lambda x:x[:5]):
        moved=updos.apply(vertices,rotation,offset)
        tail=updos.tree(moved,faces)
        scalp_contact=len(tail.overlap(scalp))
        if scalp_contact<3 or tail.overlap(hat):
            continue
        return {1:(rotation,offset)},{"tie_pitch":tie_pitch,"yaw":yaw,"tail_pitch":slope,
            "roll":roll,"tie_center":root.tolist(),"scalp_contacts":scalp_contact}
    raise ValueError("No rigid Ponytail pose cleared the beanie")


def build(uncovered, old_fit, hat, assets):
    pose,report=pose_tail(uncovered["default"],old_fit["default"],hat)
    targets={}
    hat_tree=updos.surface(hat)
    for color in ("default","ombre"):
        cap=assets/f"ponytail-beanie-crown-{color}.glb"
        tail=assets/f"ponytail-beanie-tail-{color}.glb"
        temporary=assets/f".pony-complete-{color}.glb"
        isolate(old_fit[color],cap,fitted_crown)
        updos.write_pose(uncovered[color],temporary,"ponytail",pose)
        isolate(temporary,tail,attachment)
        temporary.unlink()
        assert not updos.surface(tail).overlap(hat_tree),color
        assert updos.surface(tail).overlap(updos.surface(cap,lambda n:"roots220" in n)),color
        targets[color]=(cap,tail)
    return targets,report
