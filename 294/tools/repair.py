"""Repair visible defects found in the catalogue's lower-angle review."""
import json
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse

import numpy as np

REV = Path(__file__).resolve().parents[1]
ROOT = REV.parent
sys.path.insert(0, str(ROOT / "291/tools"))
from build_fits import clearance_map, interpolate_map
from build_bandanas import CENTER, ease, surface, triangles
from bake_catalogue import node_transforms, read_glb, warp_normals, write_glb

LINER_STYLES = {"bob", "straight", "curls"}


def local_path(uri):
    relative = Path(urlparse(urljoin("http://preview/294/", uri)).path.lstrip("/"))
    assert ".." not in relative.parts
    path = ROOT / relative
    assert path.is_relative_to(ROOT)
    return path


def accessor(model, data, index, columns):
    acc = model["accessors"][index]
    view = model["bufferViews"][acc["bufferView"]]
    assert acc["componentType"] == 5126
    return np.ndarray((acc["count"], columns), dtype="<f4", buffer=data,
                      offset=view.get("byteOffset", 0) + acc.get("byteOffset", 0),
                      strides=(view.get("byteStride", 4 * columns), 4))


def tuck_coverage(points, normals, uv):
    # In glTF v=0 is the lower end of the coverage layer. Guide its lip
    # into the head near the nape and keep coverage higher under the locks.
    height = points[:, 1]
    weight = (1 - ease(uv[:, 1] / .23)) * (1 - ease((height - 1.71) / .15))
    relative = points - CENTER
    radius = np.linalg.norm(relative, axis=1)
    radial = relative / radius[:, None]
    inset = np.maximum(radius - .3765, 0) * weight
    return points - radial * inset[:, None], normals


def islands(points, faces):
    # The exporter splits some vertices for UVs. Use shared positions to
    # identify the original woven strands and their cuffs.
    vertices, inverse = np.unique(points.round(5), axis=0, return_inverse=True)
    welded = inverse[faces]
    starts = welded.ravel()
    ends = np.roll(welded, 1, axis=1).ravel()
    labels = np.arange(len(vertices))
    while True:
        old = labels.copy()
        np.minimum.at(labels, old[starts], old[ends])
        np.minimum.at(labels, old[ends], old[starts])
        while not np.array_equal(labels, labels[labels]):
            labels = labels[labels]
        if np.array_equal(labels, old):
            return labels[inverse]


def close_braid_gap(points, normals, faces, height_limit):
    labels = islands(points, faces)
    angle = np.arctan2(points[:, 0], CENTER[2] - points[:, 2])
    centers = {}
    for label in np.unique(labels[np.abs(angle) < .40]):
        member = labels == label
        height = points[member, 1]
        lower = height <= np.quantile(height, .35)
        center = np.median(angle[member][lower])
        if abs(center) < .40:
            centers[label] = center
    assert any(abs(center) < .055 for center in centers.values())

    moved, updated = points.copy(), normals.copy()
    for label, center in centers.items():
        member = labels == label
        middle = abs(center) < .055
        drift = -np.sign(center) * .031 * np.exp(-((abs(center) - .153) / .095)**2)
        if middle:
            drift = 0.

        def fit(coords):
            x, y, z = (coords - CENTER).T
            radius = np.hypot(x, z)
            angle = np.arctan2(x, -z)
            influence = ease((coords[:, 1] - 1.24) / .14)
            influence *= 1 - ease((coords[:, 1] - (height_limit - .071)) / .071)
            turn = angle + influence * (.51 * angle if middle else drift)
            return CENTER + np.column_stack((radius * np.sin(turn), y, -radius * np.cos(turn)))

        moved[member] = fit(points[member])
        updated[member] = warp_normals(fit, points[member], normals[member])
    return moved, updated


def cap_fit(path):
    field = clearance_map([path], .012, .58)

    def settle(points):
        relative = points - CENTER
        radius = np.linalg.norm(relative, axis=1)
        direction = relative / radius[:, None]
        limit = interpolate_map(field, direction)
        # Compress the loft smoothly while retaining depth between locks.
        radius -= .009 * np.logaddexp(0, (radius - limit) / .009)
        return CENTER + direction * radius[:, None]

    return settle


def patch(source, destination, style, hat, cloth):
    model, binary = read_glb(source)
    cap = cap_fit(cloth) if style == "flow" else None
    changed = 0
    for node, rotation, offset in node_transforms(model):
        if "mesh" not in node:
            continue
        mesh = model["meshes"][node["mesh"]]
        if style in LINER_STYLES and "continuous recessed" not in mesh["name"]:
            continue
        for primitive in mesh["primitives"]:
            attributes = primitive["attributes"]
            assert "TANGENT" not in attributes
            position = accessor(model, binary, attributes["POSITION"], 3)
            normal = accessor(model, binary, attributes["NORMAL"], 3)
            xyz, n = position @ rotation.T + offset, normal @ rotation.T
            if style in LINER_STYLES:
                uv = accessor(model, binary, attributes["TEXCOORD_0"], 2)
                fitted, fitted_normal = tuck_coverage(xyz, n, uv)
            elif style == "box-braids":
                faces = triangles(model, binary, primitive["indices"])
                ceiling = 1.795 if hat in {"cap", "beanie", "bucket", "cowboy"} else 1.887
                fitted, fitted_normal = close_braid_gap(xyz, n, faces, ceiling)
            else:
                fitted, fitted_normal = cap(xyz), warp_normals(cap, xyz, n)
            position[:], normal[:] = (fitted - offset) @ rotation, fitted_normal @ rotation
            model["accessors"][attributes["POSITION"]].update(
                min=position.min(axis=0).tolist(), max=position.max(axis=0).tolist())
            assert np.isfinite(position).all() and np.isfinite(normal).all()
            changed += np.count_nonzero(np.linalg.norm(xyz - fitted, axis=1) > 1e-6)
    assert changed > 0, source
    write_glb(destination, model, binary)
    return changed


def build(receipt):
    baseline = json.loads(receipt.read_text(encoding="utf8"))
    assert baseline["revision"] == "293"
    catalogue = json.loads((ROOT / "293/hair-fits.json").read_text(encoding="utf8"))
    for build in catalogue.values():
        for style in build.values():
            for fit in style["fits"].values():
                for color, path in fit.items():
                    if path.startswith("./"):
                        fit[color] = "../293/" + path[2:]
    assets = {}
    for row in baseline["rows"]:
        build, style, hat, color = (row[key] for key in ("build", "hair", "headwear", "hairColor"))
        if style not in LINER_STYLES | {"box-braids"} and (style, hat) != ("flow", "cap"):
            continue
        source = local_path(row["parts"]["hair"])
        cloth = local_path(row["parts"]["headgear"]) if style == "flow" else None
        key = (style, source)
        if key not in assets:
            target = REV / "assets" / f"{style}-{hat}-{color}.glb"
            count = patch(source, target, style, hat, cloth)
            assets[key] = {"source": source.relative_to(ROOT).as_posix(),
                           "path": "./" + target.relative_to(REV).as_posix(),
                           "changed_vertices": int(count)}
            print(assets[key]["path"], count, flush=True)
        entries = catalogue.setdefault(build, {})
        item = entries.setdefault(style, {
            "label": row["label"],
            "note": {"box-braids": "Woven braids with a closer rear fall.",
                     "flow": "Layered side flow with a covered cap fit."}.get(style, "Shaped locks with a tucked inner edge."),
            "fits": {},
        })
        item["fits"].setdefault(hat, {})[color] = assets[key]["path"]
    for path, data in (("hair-fits.json", catalogue), ("verification/exports.json", list(assets.values()))):
        (REV / path).write_text(json.dumps(data, indent=2) + "\n", encoding="utf8", newline="\n")


if __name__ == "__main__":
    build(Path(sys.argv[-1]))