"""Check exported poses and cloth clearance on 275's two hairstyle families."""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_hair import HATS, REV, TOPS, base_buns, cloth_for, ordinary, surface
from build_bandanas import sha, triangles
from bake_catalogue import node_transforms, read_glb, vectors


def geometry(path):
    gltf, data = read_glb(path)
    meshes = {}
    for node, rotation, offset in node_transforms(gltf):
        if "mesh" not in node:
            continue
        for index, part in enumerate(gltf["meshes"][node["mesh"]]["primitives"]):
            p,n = (vectors(gltf,data,part["attributes"][k]) for k in ("POSITION","NORMAL"))
            assert np.isfinite(p).all() and np.isfinite(n).all(), path
            assert np.max(np.abs(np.linalg.norm(n,axis=1)-1.)) < .004, path
            ids = triangles(gltf,data,part["indices"])
            assert ids.max() < len(p), path
            meshes[(node["name"],index)] = (p @ rotation.T+offset,n @ rotation.T,ids)
    return meshes


def verify(revision=REV):
    fits = json.loads((revision/"hair-fits.json").read_text(encoding="utf8"))["Feminine"]
    report = {}
    for style,entry in fits.items():
        assert set(entry["fits"]) == set(HATS)
        for hat,fit in entry["fits"].items():
            paths = {color:(revision/file).resolve() for color,file in fit.items()}
            assert all(path.parent == revision/'assets' for path in paths.values())
            original, ombre = (geometry(paths[color]) for color in ("default","ombre"))
            assert original.keys() == ombre.keys(), (style,hat)
            for part, arrays in original.items():
                assert all(np.array_equal(a,b) for a,b in zip(arrays,ombre[part])), (style,hat,part)
            if style == "space-buns":
                baseline = geometry(base_buns(hat,False))
                for name, (p,n,ids) in original.items():
                    bp,bn,bi = baseline[name]
                    # The buns and upper crown keep their existing headwear-specific placement.
                    protected = bp[:,1] >= 1.984
                    assert np.array_equal(p[protected],bp[protected]), (style,hat,name)
                    assert np.array_equal(n[protected],bn[protected]), (style,hat,name)
                    assert np.array_equal(ids,bi), (style,hat,name)
            item = {
                "triangle_count": sum(len(mesh[2]) for mesh in original.values()),
                "same_geometry_both_colors": True,
                "sha256": {k:sha(v) for k,v in paths.items()},
            }
            if hat == "pashmina":
                hair = surface(paths["default"])
                clearance = {top:len(hair.overlap(surface(ordinary(file)))) for top,file in TOPS[style].items()}
                assert all(count == 0 for count in clearance.values()), (style,clearance)
                item["pashmina_overlap_by_top"] = clearance
            if style == "space-buns" and hat == "headband":
                pairs = len(surface(paths["default"]).overlap(surface(cloth_for(style,hat))))
                assert pairs == 0, pairs
                item["bandana_overlap_pairs"] = pairs
            report[style+"--"+hat] = item
    (revision/"verification/assets.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf8",newline="\n")
    print(f"Verified {len(report)} GLB fit pairs and all pashmina top variants")


if __name__ == "__main__":
    verify(Path(sys.argv[-1]).resolve() if '--' in sys.argv else REV)
