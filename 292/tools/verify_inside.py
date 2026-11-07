"""Check the corrected GLBs for lower folds, color parity, and clearance."""
import json
import sys
from pathlib import Path

import numpy as np
from mathutils.bvhtree import BVHTree

REV = Path(__file__).resolve().parents[1]
ROOT = REV.parent
sys.path.insert(0, str(ROOT / "291/tools"))
from verify_fits import CAT, FIT, HATS, STYLE, cloth_paths, digest, geometry, surface


def load_pair(directory, files):
    paths = {key: (directory / file).resolve() for key, file in files.items()}
    ordinary, ombre = (geometry(paths[key]) for key in ("default", "ombre"))
    assert ordinary.keys() == ombre.keys()
    assert len(ordinary) == 1
    for key, arrays in ordinary.items():
        assert all(np.array_equal(a, b) for a, b in zip(arrays, ombre[key])), paths
    return paths, next(iter(ordinary.values()))


def lower_overlaps(coords, triangles):
    # Merge GLB vertices duplicated for normals before excluding neighbors.
    points, ids = np.unique(coords.round(7), axis=0, return_inverse=True)
    faces = ids[triangles]
    lower = points[faces, 1].mean(axis=1) < 1.68
    faces = faces[lower].tolist()
    tree = BVHTree.FromPolygons(points, faces, all_triangles=True)
    return sum(i < j and not (set(faces[i]) & set(faces[j]))
               for i, j in tree.overlap(tree))


def verify(rev=REV, previous=ROOT / "291"):
    after = json.loads((rev / "hair-fits.json").read_text(encoding="utf8"))["Feminine"]
    before = json.loads((previous / "hair-fits.json").read_text(encoding="utf8"))["Feminine"]
    assert after["space-buns"] == before["space-buns"]
    assert set(after[STYLE]["fits"]) == set(HATS)
    wardrobe = {}
    for top, entry in CAT["builds"]["Feminine"]["tops"].items():
        relative = entry["path"]
        fitted = FIT["components"].get(relative, {}).get("path", relative)
        wardrobe[top] = surface(ROOT / "270" / fitted)

    report = {}
    for hat, pair in after[STYLE]["fits"].items():
        paths, (coords, _, triangles) = load_pair(rev, pair)
        _, (old_coords, _, old_triangles) = load_pair(previous, before[STYLE]["fits"][hat])
        assert len(triangles) == len(old_triangles), hat
        overlap = lower_overlaps(coords, triangles)
        old_overlap = lower_overlaps(old_coords, old_triangles)
        tree = surface(paths["default"])
        headwear = [len(tree.overlap(surface(path))) for path in cloth_paths(hat)] if hat != "none" else []
        tops = {top: len(tree.overlap(item)) for top, item in wardrobe.items()}
        print(hat, "lower overlaps", old_overlap, "->", overlap, "headwear", headwear, "tops", tops)
        assert overlap == 0, (hat, overlap)
        assert not any(headwear), (hat, headwear)
        assert not any(tops.values()), (hat, tops)
        report[hat] = {
            "triangle_count": len(triangles),
            "same_geometry_both_colors": True,
            "lower_self_intersections_before": old_overlap,
            "lower_self_intersections_after": overlap,
            "headwear_intersections": headwear,
            "top_intersections": tops,
            "sha256": {color: digest(path) for color, path in paths.items()},
        }
    (rev / "verification/assets.json").write_text(json.dumps(report, indent=2) + "\n",
                                                   encoding="utf8", newline="\n")


if __name__ == "__main__":
    if "--" in sys.argv:
        revision, baseline = sys.argv[sys.argv.index("--") + 1:]
        verify(Path(revision).resolve(), Path(baseline).resolve())
    else:
        verify()
