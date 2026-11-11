"""Refine selected Bob locks and the gloss of the approved revision 328 hair."""
from argparse import ArgumentParser
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "327/tools"))
from build_lob import cartesian, ease, keep_head_room, package, polar
from drape import accessor, islands, node_transforms, read_glb, triangles, warp_normals, write_glb

# Select broad locks by the angle of their tips. Lift a few into the layer
# above and let their neighbors keep the original length and profile.
# Tip angle, lift, sweep, radial change.
LAYERS = (
    (-1.47, .014, -.036, -.005),
    (-2.14, .024, -.049, .007),
    (-2.67, .018, -.048, .003),
    (-2.91, .006, .015, .006),
    (2.77, .021, .045, .009),
    (2.06, .021, .050, .005),
    (1.52, .013, .024, -.006),
)


def refine(source, target, scarf, _free_crown):
    doc, binary = read_glb(source)
    # Widen the reflections slightly so the larger locks still look glossy
    # and their grooves remain visible through the highlight.
    for material in doc["materials"]:
        material["pbrMetallicRoughness"]["roughnessFactor"] = .26
        coat = material["extensions"]["KHR_materials_clearcoat"]
        coat.update(clearcoatFactor=.54, clearcoatRoughnessFactor=.21)

    distance = 0.
    selected = set()
    for node, rotation, offset in node_transforms(doc):
        if scarf or "mesh" not in node:
            continue
        mesh = doc["meshes"][node["mesh"]]
        if "Bob / side sweep" not in mesh["name"]:
            continue
        for primitive in mesh["primitives"]:
            attrs = primitive["attributes"]
            p = accessor(doc, binary, attrs["POSITION"], 3)
            n = accessor(doc, binary, attrs["NORMAL"], 3)
            points = p @ rotation.T + offset
            normals = n @ rotation.T
            labels = islands(points, triangles(doc, binary, primitive["indices"]))
            for index in np.unique(labels):
                member = labels == index
                lock = points[member]
                end_height = np.quantile(lock[:, 1], .04)
                tip = lock[lock[:, 1] <= end_height].mean(axis=0, keepdims=True)
                angle = polar(tip)[0][0]
                nearest = min(LAYERS, key=lambda layer: abs(layer[0] - angle))
                tip_angle, lift, sweep, spread = nearest
                if abs(tip_angle - angle) > .035:
                    continue

                assert tip_angle not in selected, (source, tip_angle)
                selected.add(tip_angle)

                def flow(coords):
                    theta, y, radius = polar(coords)
                    lower = ease((1.70 - coords[:, 1]) / (1.70 - end_height))
                    # Turn the complete lock toward its end, then let the
                    # highest part of this change fade into the original sweep.
                    updated = cartesian(theta + lower * sweep, y + lower * lift,
                                        radius + lower * spread)
                    return keep_head_room(coords, updated)

                updated = flow(lock)
                change = np.linalg.norm(updated - lock, axis=1)
                moved = change > 1e-6
                moved_ids = np.flatnonzero(member)[moved]
                p[moved_ids] = (updated[moved] - offset) @ rotation
                n[moved_ids] = warp_normals(flow, lock[moved], normals[moved_ids]) @ rotation
                distance = max(distance, float(change.max()))
            doc["accessors"][attrs["POSITION"]].update(min=p.min(axis=0).tolist(), max=p.max(axis=0).tolist())

    assert len(selected) == (0 if scarf else len(LAYERS)), (source, selected)
    assert scarf or .015 < distance < .045
    write_glb(target, doc, binary)
    return distance


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("base", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    package(args.base, args.output, base_revision=328, revision=329, label="Bob",
            note="Jaw-length layers with softly separated ends and a glossy finish.", edit_asset=refine)
