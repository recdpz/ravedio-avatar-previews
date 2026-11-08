"""Route long covered hair under the authored pashmina, with room below the hem."""
import json
import sys
from pathlib import Path

import numpy as np
from mathutils.bvhtree import BVHTree

REV = Path(__file__).resolve().parents[1]
ROOT = REV.parent
sys.path.insert(0, str(ROOT / "294/tools"))
from repair import (CENTER, accessor, ease, local_path, node_transforms, read_glb, surface,
                    triangles, warp_normals, write_glb)


STYLES = {"curls", "straight", "box-braids"}
START, END = 1.30, 2.35
WIDTH, HEIGHT = 384, 211
TAU = 2 * np.pi


def hood_tree(path):
    model, binary = read_glb(path)
    vertices, faces = [], []
    for node, rotation, offset in node_transforms(model):
        if "mesh" not in node:
            continue
        mesh = model["meshes"][node["mesh"]]
        if "joined hood wrap" not in mesh["name"]:
            continue
        for primitive in mesh["primitives"]:
            attributes = primitive["attributes"]
            position = accessor(model, binary, attributes["POSITION"], 3)
            uv = accessor(model, binary, attributes["TEXCOORD_0"], 2)
            indices = triangles(model, binary, primitive["indices"]).astype(np.int32)
            # The joined scarf places its hood in the first UV tile.
            panel = np.all((uv >= -.001) & (uv <= 1.001), axis=1)
            hood = indices[np.all(panel[indices], axis=1)]
            faces.extend((hood + len(vertices)).tolist())
            vertices.extend((position @ rotation.T + offset).tolist())
    assert faces, path
    return BVHTree.FromPolygons(vertices, faces, all_triangles=True)


def hood_envelope(paths):
    trees = [hood_tree(path) for path in paths]
    yaw = np.linspace(-np.pi, np.pi, WIDTH, endpoint=False)
    directions = np.column_stack((np.sin(yaw), np.zeros(WIDTH), np.cos(yaw)))
    field = np.full((HEIGHT, WIDTH), .67)
    for row, height in enumerate(np.linspace(START, END, HEIGHT)):
        if height < 1.445:
            continue
        origin = (0, height, CENTER[2])
        for col, direction in enumerate(directions):
            for tree in trees:
                _, _, _, distance = tree.ray_cast(origin, direction, .64)
                if distance is not None:
                    field[row, col] = min(field[row, col], distance - .012)
    # Carry the constraint a little past the free edge so the visible hair
    # leaves as one continuous curve instead of a pinched ring at the hem.
    dy = (END - START) / (HEIGHT - 1)
    dx = TAU / WIDTH
    for _ in range(32):
        above = np.vstack((field[:1], field[:-1]))
        below = np.vstack((field[1:], field[-1:]))
        field = np.minimum.reduce((field, above + .77 * dy, below + .77 * dy,
                                   np.roll(field, 1, axis=1) + .22 * dx,
                                   np.roll(field, -1, axis=1) + .22 * dx))
    # Smooth the inner envelope before fitting so its sampling grid cannot
    # leave narrow highlights on the curls or individual braids.
    for _ in range(3):
        field = (.64 * field + .09 * (np.roll(field, 1, axis=1) + np.roll(field, -1, axis=1)
                                      + np.vstack((field[:1], field[:-1]))
                                      + np.vstack((field[1:], field[-1:]))))
    return field


def sampled_limit(field, azimuth, height):
    u = (azimuth + np.pi) * (WIDTH / TAU)
    v = np.clip((height - START) / (END - START) * (HEIGHT - 1), 0, HEIGHT - 1)
    col = np.floor(u).astype(int)
    row = np.minimum(np.floor(v).astype(int), HEIGHT - 2)
    a, b = u - col, v - row
    left, right = col % WIDTH, (col + 1) % WIDTH
    return ((field[row, left] * (1 - a) + field[row, right] * a) * (1 - b)
            + (field[row + 1, left] * (1 - a) + field[row + 1, right] * a) * b)


def fit(field, points):
    x, y, z = (points - CENTER).T
    height = points[:, 1]
    theta = np.arctan2(x, z)
    radius = np.hypot(x, z)
    raw = sampled_limit(field, theta, height)
    skin = np.sqrt(np.maximum(0, .384**2 - y**2))
    limit = np.maximum(raw, skin + .006)
    cover = ease((np.abs(theta) - .72) / .45) * ease((height - 1.28) / .15)
    inset = .010 * np.logaddexp(0, (radius - limit) / .010)
    # Reduce inward travel at the loose end. A deep compression near the
    # opening pulls the ends into the top and puts a kink across the locks.
    low = ease((height - 1.395) / .065)
    side = np.exp(-((np.abs(theta) - 1.57) / .40)**2)
    hem = .012 * side * ease((height - 1.365) / .08) * (1 - ease((height - 1.46) / .14))
    movement = cover * np.minimum(inset, .085) * low + hem
    settled = np.maximum(radius - movement, np.minimum(radius, skin + .004))
    return CENTER + np.column_stack((settled * np.sin(theta), y, settled * np.cos(theta)))


def write_fit(source, destination, field):
    model, binary = read_glb(source)
    modified, maximum = 0, 0.
    for node, rotation, offset in node_transforms(model):
        if "mesh" not in node:
            continue
        for primitive in model["meshes"][node["mesh"]]["primitives"]:
            attrs = primitive["attributes"]
            assert "TANGENT" not in attrs
            p = accessor(model, binary, attrs["POSITION"], 3)
            n = accessor(model, binary, attrs["NORMAL"], 3)
            points, normals = p @ rotation.T + offset, n @ rotation.T
            updated = fit(field, points)
            delta = np.linalg.norm(updated - points, axis=1)
            changed = delta > 1e-6
            p[changed] = (updated[changed] - offset) @ rotation
            n[changed] = warp_normals(lambda x: fit(field, x), points[changed], normals[changed]) @ rotation
            model["accessors"][attrs["POSITION"]].update(min=p.min(axis=0).tolist(),
                                                        max=p.max(axis=0).tolist())
            assert np.isfinite(n).all()
            modified += int(np.count_nonzero(changed))
            maximum = max(maximum, float(delta.max()))
    assert modified > 0
    write_glb(destination, model, binary)
    return {"moved_vertices": modified, "max_displacement": maximum}


def build(receipt):
    baseline = json.loads(receipt.read_text(encoding="utf8"))
    assert baseline["revision"] == "294"
    catalogue = json.loads((ROOT / "294/hair-fits.json").read_text(encoding="utf8"))
    for build in catalogue.values():
        for style in build.values():
            for fit_paths in style["fits"].values():
                for color, path in fit_paths.items():
                    if path.startswith("./"):
                        fit_paths[color] = "../294/" + path[2:]
    report = {}
    for style in sorted(STYLES):
        rows = [row for row in baseline["rows"] if row["hair"] == style]
        covers = sorted({local_path(row["parts"]["headgear"]) for row in rows})
        field = hood_envelope(covers)
        for color in ("default", "ombre"):
            sources = {local_path(row["parts"]["hair"]) for row in rows if row["hairColor"] == color}
            source, = sources
            path = REV / "assets" / f"{style}-pashmina-{color}.glb"
            stats = write_fit(source, path, field)
            catalogue["Feminine"][style]["fits"]["pashmina"][color] = "./assets/" + path.name
            report[path.name] = {"source": source.relative_to(ROOT).as_posix(), **stats}
            print(path.name, stats, flush=True)
    for file, data in (("hair-fits.json", catalogue), ("verification/fits.json", report)):
        (REV / file).write_text(json.dumps(data, indent=2) + "\n", encoding="utf8", newline="\n")


if __name__ == "__main__":
    build(Path(sys.argv[-1]))