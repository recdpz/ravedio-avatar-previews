"""Sculpt a softer Box Braids silhouette using the existing woven meshes."""
import json
from pathlib import Path
import sys

import numpy as np

REV = Path(__file__).resolve().parents[1]
ROOT = REV.parent
sys.path.insert(0, str(ROOT / "304/tools"))
from braids import braid_groups, old_center, smooth_profile
from fit import CENTER, ease, geometry, local_path, read_glb, warp_normals, write_glb

Y = np.linspace(1.06, 2.25, 260)


def groups_for(basis):
    _, _, points, _, groups, cuffs, labels = braid_groups(*read_glb(basis))
    ranked = {-1: [], 1: []}
    for label in labels:
        vertices = points[groups == label]
        center = vertices[abs(vertices[:, 1] - 1.88) < .025].mean(axis=0)
        angle = np.arctan2(abs(center[0]), center[2] + .015)
        side = int(np.sign(center[0]))
        ranked[side].append((angle, label))
    return groups, cuffs, ranked


def lower_shape(original, end, rank, angle, side, covered):
    # Keep weight in the lengths and let the tips narrow over the final third.
    y = Y
    drop = ease((1.71 - y) / .45)
    taper = .16 * ease((1.90 - y) / .38) + (.17 + .025 * np.cos(2.1 * rank)) * ease((1.46 - y) / .22)
    offset = np.zeros((len(y), 3))

    if rank < 3:
        if not covered:
            knots = np.array([1.14, 1.24, 1.36, 1.48, 1.61, 1.74, 1.89])
            x = np.array([.177,.178,.185,.198,.215,.229,.24]) + rank * np.array([.046,.046,.045,.040,.034,.034,.038])
            z = np.array([.256,.263,.265,.260,.253,.275,.31]) - rank * np.array([.003,.003,.005,.011,.017,.023,.037])
            guide = smooth_profile(knots, np.column_stack((side*x,z)), y, .032)
            blend = ease((1.85 - y) / .31)
            radial = guide - [0., CENTER[2]]
            radius = np.linalg.norm(radial, axis=1)
            head = np.sqrt(np.maximum(.405**2 - (y - CENTER[1])**2, 0))
            clearance = np.maximum(0., head / np.maximum(radius, .001) - 1.)
            offset[:, [0, 2]] = (guide - original + radial * clearance[:, None]) * blend[:, None]
        else:
            # Keep the authored turn around the scarf, then separate the ends.
            hang = ease((1.40 - y) / .17)
            offset[:, 0] = side * (.010 * (rank - 1) - .004) * hang
            offset[:, 2] = -.004 * hang
        offset[:, 1] = ([-.029, .015, -.009][rank] + .008 * side) * drop
    else:
        shoulder = np.exp(-((angle - 1.39) / .55)**2)
        rear = ease((angle - 1.86) / .85)
        layer = .018 * np.cos(1.3 * rank + .53 * side)
        offset[:, 1] = (.054 * shoulder - .013 * rear + layer) * drop
        if covered:
            # Tuck most of the back layers into the existing hem. Several
            # staggered tips remain visible below the cloth.
            offset[:, 1] += (.020 + .031 * shoulder + .027 * rear) * ease((1.50 - y) / .24)
            offset[:, 2] -= (.018 * shoulder + .030 * rear) * ease((1.345 - y) / .090)
            side_room = .020 * np.exp(-((rank - 4.7) / 2.25)**2)
            offset[:, 0] += side * side_room * ease((1.44 - y) / .18)
        else:
            fall = ease((1.67 - y) / .35)
            offset[:, 0] = -side * (.014 + .029 * shoulder) * fall
            split = .025 * np.exp(-((rank - 3.3) / 1.25)**2) - .039 * np.exp(-((rank - 7) / 2.9)**2)
            offset[:, 2] = (split - .026 * rear) * fall
            lift = .115 * np.exp(-((rank - 7.5) / 2.35)**2)
            offset[:, 1] += lift * ease((1.81 - y) / .48)

    # Shorten the plugs below the bands, with the bands moving with the plaits.
    offset[:, 1] += .020 * ease((end - .012 - y) / .040)
    taper += .26 * ease((end - .018 - y) / .039)
    return offset, taper


def seat_crown(p):
    """Press down the exposed crossings near the part and the rear roots."""
    x, height, z = p.T
    part = ease((.086 - abs(x)) / .067) * ease((height - 1.99) / .139)
    back = ease((-.17 - z) / .14) * ease((height - 1.94) / .18)
    radial = p - CENTER
    radius = np.linalg.norm(radial, axis=1)
    inset = (.36 * part + .28 * back) * np.maximum(0., radius - .386)
    result = p - radial * (inset / np.maximum(radius, .001))[:, None]
    result[:, 0] -= np.sign(x) * np.clip((abs(x) - .006) * .47, 0., .018) * part
    return result


def sculpt(source, target, layout, covered, bare):
    model, data = read_glb(source)
    braid, cuff = geometry(model, data)
    labels, cuffs, ranked = layout
    for part, group in ((braid, labels), (cuff, cuffs)):
        assert len(part[2]) == len(group) and not np.ptp(group[part[-1]], axis=1).any(), source
    points, tips = (part[2] @ part[4].T + part[5] for part in (braid, cuff))

    for side, ordered in ranked.items():
        for rank, (angle, label) in enumerate(sorted(ordered)):
            original = old_center(points[labels == label], Y)
            end = tips[cuffs == label, 1].mean()
            offset, taper = lower_shape(original, end, rank, angle, side, covered)

            def warp(p):
                height = p[:, 1]
                moved = p + np.column_stack([np.interp(height, Y, column) for column in offset.T])
                center = np.column_stack([np.interp(height, Y, column) for column in original.T])
                moved[:, [0, 2]] -= (p[:, [0, 2]] - center) * np.interp(height, Y, taper)[:, None]
                return moved

            for part, world, mask in ((braid, points, labels == label), (cuff, tips, cuffs == label)):
                _, _, pos, normals, rotation, translation, _ = part
                ids = mask & (world[:, 1] < 1.90)
                p = world[ids]
                pos[ids] = (warp(p) - translation) @ rotation
                normals[ids] = warp_normals(warp, p, normals[ids] @ rotation.T) @ rotation

    if bare:
        _, _, pos, normals, rotation, translation, _ = braid
        ids = points[:, 1] > 1.94
        p = points[ids]
        pos[ids] = (seat_crown(p) - translation) @ rotation
        normals[ids] = warp_normals(seat_crown, p, normals[ids] @ rotation.T) @ rotation

    for _, bounds, pos, *_ in (braid, cuff):
        bounds.update(min=pos.min(axis=0).tolist(), max=pos.max(axis=0).tolist())
    write_glb(target, model, data)


def main(receipt):
    rows = json.loads(receipt.read_text(encoding="utf-8-sig"))
    source_paths = {(row["features"]["headwear"], row["features"]["hairColor"]):
                    local_path(row["components"]["hair"]) for row in rows
                    if row["features"]["hair"] == "box-braids" and row["features"]["top"] == "open"}
    layout = groups_for(source_paths["none", "default"])
    fits = json.loads((ROOT / "305/hair-fits.json").read_text(encoding="utf-8")
                      .replace('"./assets/', '"../305/assets/'))
    box_braids = fits["Feminine"]["box-braids"]
    box_braids["note"] = "Layered Box Braids with tapered tips and a fitted pashmina drape."
    built = {}
    for (hat, color), source in source_paths.items():
        key = (source, hat == "pashmina")
        if key not in built:
            target = REV / "assets" / f"box-braids-{hat}-{color}.glb"
            sculpt(source, target, layout, covered=key[1], bare=hat == "none")
            built[key] = "./assets/" + target.name
            print(target.name, flush=True)
        box_braids["fits"][hat][color] = built[key]
    (REV / "hair-fits.json").write_text(json.dumps(fits, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main(Path(sys.argv[-1]))
