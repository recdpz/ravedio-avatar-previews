"""Shape a more pronounced sweep and stacked layers into the jaw-length Bob."""
from argparse import ArgumentParser
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "327/tools"))
from build_lob import cartesian, ease, keep_head_room, package, polar
from drape import accessor, islands, node_transforms, read_glb, triangles, warp_normals, write_glb

# The sweep and the kick describe different parts of a lock. The first
# turns the body of the lock, the second changes direction near the tip.
# Tip angle, lift, mid sweep, tip sweep, mid fullness, tip fullness.
LAYERS = (
    (-1.33, .023, .190, -.135, .029, .013),
    (-1.51, .079, .190, -.090, .026, .022),
    (-1.61, .041, .105, -.08, .017, .006),
    (-1.77, .010, .070, -.07, .010, .013),
    (-1.93, .028, .105, -.060, .010, .022),
    (-2.02, .016, -.065, -.19, .012, .011),
    (-2.19, .085, .055, -.10, .017, .020),
    (-2.21, .012, -.031, -.115, .009, .012),
    (-2.44, .007, .045, -.05, .012, .013),
    (-2.72, .068, .046, -.09, .015, .014),
    (-2.90, .003, .027, .045, .009, .012),
    (3.07, .024, -.030, -.023, .012, .012),
    (2.81, .069, -.063, -.073, .019, .018),
    (2.43, .010, .036, .095, .007, .011),
    (2.32, .053, -.058, -.064, .016, .018),
    (2.11, .054, -.085, .055, .024, .025),
    (1.97, .015, -.065, .10, .012, .004),
    (1.67, .020, -.095, .18, .012, -.007),
    (1.54, .077, -.143, .147, .024, .019),
    (1.41, .023, -.129, .225, .020, -.006),
)


def sculpt(source, target, scarf, free_crown):
    if scarf:
        return None
    doc, binary = read_glb(source)
    distance = 0.
    selected = set()
    for node, rotation, offset in node_transforms(doc):
        if "mesh" not in node:
            continue
        mesh = doc["meshes"][node["mesh"]]
        if "Bob / side sweep" not in mesh["name"]:
            continue
        # The inner and outer locks have nearby tip angles on the left.
        if "side sweep 9" in mesh["name"]:
            layers = [entry for entry in LAYERS if entry[0] != -2.21]
        elif "side sweep 8" in mesh["name"]:
            layers = [entry for entry in LAYERS if entry[0] not in (-2.19, -2.02)]
        else:
            layers = LAYERS
        for primitive in mesh["primitives"]:
            attrs = primitive["attributes"]
            p = accessor(doc, binary, attrs["POSITION"], 3)
            n = accessor(doc, binary, attrs["NORMAL"], 3)
            points = p @ rotation.T + offset
            normals = n @ rotation.T
            labels = islands(points, triangles(doc, binary, primitive["indices"]))
            for index in np.unique(labels):
                ids = np.flatnonzero(labels == index)
                lock = points[ids]
                end_height = np.quantile(lock[:, 1], .04)
                tip = lock[lock[:, 1] <= end_height].mean(axis=0, keepdims=True)
                angle = polar(tip)[0][0]
                layer = min(layers, key=lambda layer: abs(layer[0] - angle))
                tip_angle, lift, mid_turn, end_turn, fullness, flick = layer
                if abs(tip_angle - angle) > .035:
                    continue

                assert tip_angle not in selected, (source, tip_angle)
                selected.add(tip_angle)
                start = 1.91 if free_crown else 1.805
                strength = 1. if free_crown else .86

                def flow(coords):
                    theta, y, radius = polar(coords)
                    along = np.clip((start - coords[:, 1]) / (start - end_height), 0, 1)
                    body = np.sin(np.pi * along)**2
                    end = ease((along - .23) / .77)
                    theta += strength * (body * mid_turn + end * end_turn)
                    radius += strength * (body * fullness + end * flick)
                    y += strength * end * lift
                    return keep_head_room(coords, cartesian(theta, y, radius))

                updated = flow(lock)
                change = np.linalg.norm(updated - lock, axis=1)
                moved = change > 1e-6
                p[ids[moved]] = (updated[moved] - offset) @ rotation
                n[ids[moved]] = warp_normals(flow, lock[moved], normals[ids[moved]]) @ rotation
                distance = max(distance, float(change.max()))
            doc["accessors"][attrs["POSITION"]].update(min=p.min(axis=0).tolist(), max=p.max(axis=0).tolist())

    assert len(selected) == len(LAYERS), (source, selected)
    assert .07 < distance < .16, (source, distance)
    write_glb(target, doc, binary)
    return distance


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("base", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    package(args.base, args.output, base_revision=329, revision=330, label="Bob",
            note="Jaw-length bob with a sweeping front and stacked, turned layers.", edit_asset=sculpt)
