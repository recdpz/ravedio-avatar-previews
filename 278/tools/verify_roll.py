"""Measure the curve and tucked tips in the exported bare fringe."""
import json
import sys
from pathlib import Path

import numpy as np

REV = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(REV.parent/"275/tools"))
from verify_assets import geometry
from build_hair import CENTER, RADIUS


def strands(points, faces):
    # Join split normals at the end caps for the connectivity check.
    _, seam = np.unique(points.round(6),axis=0,return_inverse=True)
    parent = np.arange(seam.max()+1)

    def root(index):
        while index != parent[index]:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    for a,b,c in seam[faces]:
        lead = root(a)
        parent[root(b)] = lead
        parent[root(c)] = lead
    groups = np.array([root(index) for index in seam])
    return [points[groups==index] for index in np.unique(groups)]


parts = geometry(REV/"assets/side-sweep-none.glb")
[(points,_,faces)] = [part for (name,_),part in parts.items() if name.startswith("Fringe / fine strands")]
measurements = []
for strand in strands(points,faces):
    relative = strand-CENTER
    low = relative[relative[:,1] <= relative[:,1].min()+.0016]
    tip = low.mean(axis=0)
    horizontal = np.linalg.norm(relative[:,[0,2]],axis=1)
    crest = relative[horizontal.argmax()]
    height = relative[:,1].max()-tip[1]
    return_depth = horizontal.max()-np.linalg.norm(tip[[0,2]])
    crest_progress = (relative[:,1].max()-crest[1])/height
    clearance = np.linalg.norm(tip)-RADIUS
    assert return_depth > .012 and .60 < crest_progress < .92, (return_depth,crest_progress)
    assert .002 < clearance < .009, clearance
    measurements.append((return_depth,crest_progress,clearance))
assert len(measurements) == 32
data = np.array(measurements)
metrics = {"strands":len(data),"fringe_meshes":1}
for index,label in enumerate(("profile_return_depth","crest_progress","tip_clearance")):
    metrics[label] = [round(float(f(data[:,index])),6) for f in (np.min,np.max)]
(REV/"verification/fringe-roll.json").write_text(json.dumps(metrics,indent=2)+"\n",encoding="utf8",newline="\n")
print("Verified 32 exported curves batched into one fringe mesh")
