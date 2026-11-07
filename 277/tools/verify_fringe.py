"""Verify the outward arc on the exported fringe, in head coordinates."""
import json
import sys
from pathlib import Path

import numpy as np

REV = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(REV.parent/"275/tools"))
from verify_assets import geometry
from build_hair import CENTER, RADIUS

parts = geometry(REV/"assets/side-sweep-none.glb")
arcs = {}
for (name,_),(points,_,_) in parts.items():
    if not name.startswith("Fringe / arched wisp"):
        continue
    tip = points[points[:,1] <= points[:,1].min()+.002].mean(axis=0)
    return_depth = points[:,2].max()-tip[2]
    tip_clearance = np.linalg.norm(tip-CENTER)-RADIUS
    assert return_depth > .006, (name,return_depth)
    assert .002 < tip_clearance < .008, (name,tip_clearance)
    arcs[name] = {"profile_return_depth":round(float(return_depth),6),
                  "tip_clearance_from_head":round(float(tip_clearance),6)}
assert len(arcs) == 9
(REV/"verification/fringe-arc.json").write_text(json.dumps(arcs,indent=2)+"\n",encoding="utf8",newline="\n")
print("Verified the outward curve and return at all nine exported tips")
