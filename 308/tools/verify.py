"""Check the jersey opening and neighboring components in the final GLB."""
from hashlib import sha256
import json
from pathlib import Path
import struct
import sys

import numpy as np

REV = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REV.parent / "299/tools"))
from fit import geometry, local_path, read_glb, surface, tree


def meshes(path):
    return {name: (p @ rotation.T + offset, faces)
            for name, _, p, _, rotation, offset, faces in geometry(*read_glb(path))}


def front(surface, x, height):
    hit, _, _, _ = surface.ray_cast((x, height, .7), (0., 0., -1.), 1.2)
    assert hit is not None
    return hit.z


def verify(browser_receipt):
    review = json.loads(browser_receipt.read_text())
    rows = review["rows"]
    old = REV.parent / "213/Feminine-jersey-top.glb"
    new = REV / "assets/Feminine-jersey.glb"
    before, after = map(meshes, (old, new))
    retained = [name for name in before if name.startswith(("Sleeve /", "Shirt / flush hem"))]
    assert len(retained) == 5
    for name in retained:
        assert all(np.array_equal(a,b) for a,b in zip(before[name], after[name], strict=True)), name

    body = surface(local_path(rows[0]["parts"]["base"]))
    previous, jersey = map(surface, (old, new))
    assert front(previous, 0., 1.32) > front(body, 0., 1.32)
    assert front(jersey, 0., 1.32) < front(body, 0., 1.32)
    assert front(jersey, 0., 1.24) > front(body, 0., 1.24)
    assert front(jersey, .12, 1.32) > front(body, .12, 1.32)
    gap = front(jersey, 0., 1.276) - front(body, 0., 1.276)
    assert .005 < gap < .035, gap

    for name, (points, indices) in after.items():
        collar = indices[points[indices, 1].min(axis=1) >= 1.27]
        if len(collar):
            assert not tree(points, collar).overlap(body), name
    scarves = [row for row in rows if row["features"]["headwear"] == "pashmina"]
    for row in scarves:
        scarf = surface(local_path(row["parts"]["headgear"]))
        assert not jersey.overlap(scarf), row["features"]

    atlases = {}
    for key in review["colors"]:
        path = REV / "assets" / f"jersey-{key}.png"
        data = path.read_bytes()
        size = struct.unpack_from(">II", data, 16)
        assert size == (2048, 2048)
        atlases[key] = {"dimensions": list(size), "sha256": sha256(data).hexdigest()}
    return {"browser_cases_per_revision": len(rows), "retained_meshes": retained,
            "neckline_gap_at_center_sample": gap, "tested_scarf_fits": len(scarves),
            "top_sha256": sha256(new.read_bytes()).hexdigest(), "atlases": atlases}


if __name__ == "__main__":
    result = verify(Path(sys.argv[-1]))
    (REV / "verification/fit.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("Verified opening, retained sleeves and hem, three pashmina fits, and nine 2048 px atlases.")
