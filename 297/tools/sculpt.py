"""Rebuild the lower lock paths and fit the pashmina over the finished cuts."""
import json
import sys
from pathlib import Path

import numpy as np

REV = Path(__file__).resolve().parents[1]
ROOT = REV.parent
sys.path.insert(0, str(ROOT / "296/tools"))
from drape import (CENTER, accessor, cartesian, deform, ease, islands, local_path,
                   node_transforms, polar, read_glb, surface,
                   triangles, turn_along_path, write_glb)

TAU = 2 * np.pi
HEIGHTS = np.linspace(1.29, 2.24, 181)
ANGLES = np.linspace(-np.pi, np.pi, 256, endpoint=False)


def unit(v):
    return v / np.maximum(np.linalg.norm(v, axis=1, keepdims=True), 1e-8)


def centerline(points, uv):
    parameter, ring = np.unique(uv[:, 1].round(5), return_inverse=True)
    count = np.bincount(ring)
    assert len(count) == 65
    centers = np.column_stack([np.bincount(ring, weights=c) / count for c in points.T])
    return parameter, ring, centers


def lay_lock(origin, style, order, tuck, inner=False):
    theta, h, radius = polar(origin)
    height = origin[:, 1]
    t = np.clip((1.91 - height) / .62, 0, 1.15)
    # Match the existing angle where the lock leaves the head. Redraw
    # the free fall as a continuous path measured by physical height.
    idx = np.argmin(np.abs(height - 1.68))
    angle = theta[idx] % TAU
    spread = np.clip((angle - 1.20) / (TAU - 2.40), 0, 1)
    baseline = 1.20 + (TAU - 2.40) * (.60 * order + .40 * spread)
    direction = np.arctan2(np.sin(baseline - theta), np.cos(baseline - theta))
    blend = ease((1.87 - height) / .31)
    nape = ease((np.abs(theta) - 1.19) / 1.22)
    length_var = np.sin(24 * order + 1.2)
    h += (.011 + .016 * length_var) * ease((1.68 - height) / .36)
    if style == "curls":
        phase = TAU * (2.08 * t + .13 * t * t) + 24.7 * order + .23 * np.sin(16 * order)
        amp = ease(t / .37) * (.86 + .14 * np.cos(17 * order))
        if inner:
            phase += 1.57
        new_angle = theta + blend * direction + (.045 if inner else .110) * amp * np.sin(phase)
        target_radius = .368 + (.026 if inner else .037) * amp * np.cos(phase + .18)
        # Curve the broad center lock before its first lower turn.
        middle = np.exp(-((order - .45) / .035)**2)
        crown_turn = ease((2.16 - height) / .17) * ease((height - 1.71) / .18)
        new_angle += .120 * middle * crown_turn
        if inner:
            new_angle += .091 * blend
            target_radius -= .022
            h += .041 * ease((1.67 - height) / .37)
    else:
        new_angle = theta + blend * (direction + .021 * length_var * ease(t))
        target_radius = .378 - .035 * np.clip(t, 0, 1) - .014 * ease((t - .78) / .25)
        target_radius += .009 * length_var * ease(t)
    new_radius = radius + blend * (target_radius - radius)
    if tuck:
        # Sweeping the free lengths back gives the collar breathing room
        # without folding over the tips or changing their cross-sections.
        gather = ease((1.56 - height) / .25)
        side = ease((np.abs(theta) - .84) / .62)
        new_angle += np.sign(theta) * .21 * gather * side * (1 - nape)
        new_radius -= (.020 + .012 * nape) * gather * side
    return cartesian(new_angle, h, new_radius)


def sculpt_lock(points, normals, uv, style, order, tuck=False, inner=False):
    parameter, ring, origin = centerline(points, uv)
    target = lay_lock(origin, style, order, tuck, inner)
    shift = target - origin
    for _ in range(2):
        shift[1:-1] = .22 * shift[:-2] + .56 * shift[1:-1] + .22 * shift[2:]
    target = origin + shift
    old_tangent = unit(np.gradient(origin, axis=0))
    tangent = unit(np.gradient(target, axis=0))
    offset = turn_along_path(points - origin[ring], old_tangent[ring], tangent[ring])
    normal = turn_along_path(normals, old_tangent[ring], tangent[ring])
    if style == "straight":
        return target[ring] + offset, normal

    # Replace the ribbon sections on the free lengths with a soft oval.
    # A near-vertical frame leaves each turn round, even on the inside.
    def frame(centers, axis):
        r = centers - CENTER
        r[:, 1] = 0
        radial = unit(r - np.sum(r * axis, axis=1, keepdims=True) * axis)
        return radial, np.cross(axis, radial)

    old_r, old_across = frame(origin, old_tangent)
    guide = np.argmin(abs(origin[:, 1] - 1.82))
    sample = ring == guide
    q = points[sample] - origin[guide]
    previous = np.arctan2(q @ old_r[guide], q @ old_across[guide])
    phase = np.angle(np.mean(np.exp(1j * (previous + TAU * uv[sample, 0] / 1.25))))
    around = phase - TAU * uv[:, 0] / 1.25
    rising = unit(tangent * .56 + np.array([0., .44, 0.]))
    radial, across = frame(target, rising)
    tip = np.clip(1 - parameter / .084, 0, 1)[ring]
    cap = np.sqrt(1 - tip * tip)
    blend = ease((1.95 - origin[ring, 1]) / .32)
    width = (.036 + .004 * np.sin(15 * order + 1.3)) * cap
    depth = (.023 + .003 * np.cos(17 * order)) * cap
    if inner:
        width *= .73
        depth *= .74
        offset *= .76
    c, d = np.cos(around), np.sin(around)
    section = width[:, None] * c[:, None] * across[ring] + depth[:, None] * d[:, None] * radial[ring]
    round_normal = unit(cap[:, None] * (c[:, None] * across[ring] + 1.45 * d[:, None] * radial[ring])
                        - tip[:, None] * rising[ring])
    weight = blend[:, None]
    return target[ring] + offset * (1 - weight) + section * weight, unit(normal * (1 - weight) + round_normal * weight)


def add_buffer(model, binary, data, role, template):
    values = np.ascontiguousarray(data)
    binary.extend(bytes((-len(binary)) % 4))
    offset = len(binary)
    binary.extend(values.tobytes())
    view = len(model["bufferViews"])
    model["bufferViews"].append({"buffer": 0, "byteOffset": offset,
                                 "byteLength": values.nbytes, "target": role})
    accessors = model["accessors"]
    index = len(accessors)
    acc = {k: v for k, v in template.items() if k in {"componentType", "type", "normalized"}}
    acc.update(bufferView=view, count=len(values))
    if "min" in template:
        acc.update(min=np.min(values, axis=0).reshape(-1).tolist(),
                   max=np.max(values, axis=0).reshape(-1).tolist())
    accessors.append(acc)
    return index


def inspect_locks(model, binary):
    locks = []
    for node, rotation, offset in node_transforms(model):
        if "mesh" not in node:
            continue
        mesh = model["meshes"][node["mesh"]]
        if "side sweep" not in mesh["name"]:
            continue
        primitive, = mesh["primitives"]
        attrs = primitive["attributes"]
        points = accessor(model, binary, attrs["POSITION"], 3) @ rotation.T + offset
        normals = accessor(model, binary, attrs["NORMAL"], 3) @ rotation.T
        uv = accessor(model, binary, attrs["TEXCOORD_0"], 2).copy()
        faces = triangles(model, binary, primitive["indices"]).copy()
        welded = islands(points, faces)
        for label in np.unique(welded):
            members = np.flatnonzero(welded == label)
            _, _, center = centerline(points[members], uv[members])
            idx = np.argmin(abs(center[:, 1] - 1.68))
            theta = polar(center[idx:idx + 1])[0][0] % TAU
            locks.append((theta, mesh, rotation, offset, members, points, normals, uv, faces))
    assert len(locks) == 21
    return sorted(locks, key=lambda row: row[0])


def rebuild(source, target, style, tuck=False):
    model, binary = read_glb(source)
    locks = inspect_locks(model, binary)
    # Copy the existing strand UVs and color ramp onto narrower interior
    # locks. These fill the larger rear gaps without a visible flat liner.
    inner_rows = {4, 6, 7, 8, 10, 11, 12, 14, 16}
    pending = {}
    for i, (_, mesh, rot, off, take, points, normals, uv, faces) in enumerate(locks):
        primitive = mesh["primitives"][0]
        attrs = primitive["attributes"]
        p, n = sculpt_lock(points[take], normals[take], uv[take], style, i / 20, tuck)
        accessor(model, binary, attrs["POSITION"], 3)[take] = (p - off) @ rot
        accessor(model, binary, attrs["NORMAL"], 3)[take] = n @ rot
        if style != "curls" or i not in inner_rows:
            continue
        p, n = sculpt_lock(points[take], normals[take], uv[take], style, i / 20, tuck, inner=True)
        local_indices = np.full(len(points), -1, dtype=np.int32)
        local_indices[take] = np.arange(len(take))
        chosen = local_indices[faces]
        new_faces = chosen[np.all(chosen >= 0, axis=1)].astype("<u2").ravel()
        new_attrs = {"POSITION": (p - off) @ rot, "NORMAL": n @ rot}
        for name, index in attrs.items():
            if name in new_attrs:
                continue
            components = {"VEC2": 2, "VEC3": 3, "VEC4": 4}[model["accessors"][index]["type"]]
            new_attrs[name] = accessor(model, binary, index, components)[take]
        pending.setdefault(mesh["name"], []).append((mesh, primitive, new_faces, new_attrs))

    for sections in pending.values():
        mesh, primitive, _, attrs = sections[0]
        indices = []
        offset = 0
        for _, _, faces, section_attrs in sections:
            indices.append(faces + offset)
            offset += len(section_attrs["POSITION"])
        assert offset < 65536
        faces = np.concatenate(indices)
        attrs = {name: np.concatenate([section[3][name] for section in sections]) for name in attrs}
        new = {k: v for k, v in primitive.items() if k not in {"attributes", "indices"}}
        new["indices"] = add_buffer(model, binary, faces, 34963, {"componentType": 5123, "type": "SCALAR"})
        new["attributes"] = {
            name: add_buffer(model, binary, p.astype("<f4"), 34962,
                             model["accessors"][primitive["attributes"][name]])
            for name, p in attrs.items()
        }
        mesh["primitives"].append(new)

    for mesh in model["meshes"]:
        for primitive in mesh["primitives"]:
            attrs = primitive["attributes"]
            idx = attrs["POSITION"]
            p = accessor(model, binary, idx, 3)
            n = accessor(model, binary, attrs["NORMAL"], 3)
            assert np.isfinite(p).all() and np.isfinite(n).all()
            model["accessors"][idx].update(min=p.min(0).tolist(), max=p.max(0).tolist())
    model["buffers"][0]["byteLength"] = len(binary)
    write_glb(target, model, binary)


def envelope(path):
    tree = surface(path)
    direction = np.column_stack((np.sin(ANGLES), np.zeros(len(ANGLES)), np.cos(ANGLES)))
    field = np.zeros((len(HEIGHTS), len(ANGLES)))
    for row, y in enumerate(HEIGHTS):
        origin = np.array([0, y, CENTER[2]])
        for col, ray in enumerate(direction):
            _, _, _, depth = tree.ray_cast(origin + .59 * ray, -ray, .59)
            if depth is not None:
                field[row, col] = .59 - depth
    return field


def smooth(field, spread_y, spread_angle):
    # Bridge individual hair grooves with a soft cloth-scale contour.
    for axis, spread in ((0, spread_y), (1, spread_angle)):
        width = int(np.ceil(2.5 * spread))
        weights = np.exp(-.5 * (np.arange(-width, width + 1) / spread)**2)
        weights /= weights.sum()
        if axis == 0:
            padded = np.pad(field, ((width, width), (0, 0)), mode="edge")
            field = sum(w * padded[i:i + len(field)] for i, w in enumerate(weights))
        else:
            field = sum(w * np.roll(field, i - width, axis=1) for i, w in enumerate(weights))
    return field


def sample(field, theta, height):
    u = (theta + np.pi) / TAU * len(ANGLES)
    v = np.clip((height - HEIGHTS[0]) / (HEIGHTS[-1] - HEIGHTS[0]), 0, 1) * (len(HEIGHTS) - 1)
    col = np.floor(u).astype(int)
    row = np.minimum(np.floor(v).astype(int), len(HEIGHTS) - 2)
    x, z = u - col, v - row
    a, b = col % len(ANGLES), (col + 1) % len(ANGLES)
    return ((1 - z) * ((1 - x) * field[row, a] + x * field[row, b])
            + z * ((1 - x) * field[row + 1, a] + x * field[row + 1, b]))


def cloth_drop(theta, height):
    back = ease((np.abs(theta) - 1.78) / .98)
    edge = np.exp(-((height - 1.393) / .124)**2)
    return .039 * back * edge


def cloth_room(path, hair):
    outside = envelope(path)
    # The continuous lower edge can lie between sample rows. Extend the
    # last measured contour to the rim, then move both cloth surfaces together.
    for col in range(len(ANGLES)):
        valid = np.flatnonzero(outside[:, col] > .02)
        if valid.size:
            outside[:valid[0], col] = outside[valid[0], col]
    theta = np.tile(ANGLES, len(HEIGHTS))
    height = np.repeat(HEIGHTS, len(ANGLES))
    dropped = height - cloth_drop(theta, height)
    target = sample(hair, theta, dropped).reshape(outside.shape)
    need = np.where(outside > .025, np.maximum(target + .014 - outside, 0), 0.)
    # Hold enough room for the neighboring curls, then soften that room
    # across the fabric. The inner and outer layers share this displacement.
    for _ in range(9):
        need = np.maximum.reduce((need, np.roll(need, 1, axis=1) - .003,
                                  np.roll(need, -1, axis=1) - .003,
                                  np.vstack((need[:1], need[:-1])) - .005,
                                  np.vstack((need[1:], need[-1:])) - .005))
    return smooth(np.minimum(need, .070), 3.3, 5.7)


def fit_cloth(points, field, hair):
    theta, y, radius = polar(points)
    outer = ease((radius - .193) / .070)
    y -= cloth_drop(theta, points[:, 1]) * outer
    room = sample(field, theta, points[:, 1])
    hair_edge = sample(hair, theta, y + CENTER[1])
    side = ease((np.abs(theta) - .93) / .57)
    neck = ease((points[:, 1] - 1.31) / .062)
    # The authored trim stays below the side lengths. Allow a little
    # extra space for the higher surface where a curl meets the cloth.
    finish = .006 * np.logaddexp(0, (hair_edge + .014 - radius - room) / .006)
    nape_ease = ease((np.abs(theta) - 1.90) / .63)
    clearance = .019 * nape_ease * np.exp(-((points[:, 1] - 1.465) / .123)**2)
    outward = room + np.minimum(finish, .044) + clearance
    return cartesian(theta, y, radius + outward * side * neck * outer)


def read(name):
    return json.loads((ROOT / "296" / name).read_text(encoding="utf8"))


def dump(name, value):
    (REV / name).write_text(json.dumps(value, indent=2) + "\n", encoding="utf8", newline="\n")


def build(receipt):
    rows = json.loads(receipt.read_text(encoding="utf8"))
    assert rows["revision"] == "296"
    out = REV / "assets"
    out.mkdir(exist_ok=True)
    catalogue, cloth = read("hair-fits.json"), read("pashmina-fits.json")
    for styles in catalogue.values():
        for entry in styles.values():
            for fit in entry["fits"].values():
                for color, p in fit.items():
                    if p.startswith("./"):
                        fit[color] = "../296/" + p[2:]
    for styles in cloth.values():
        for tops in styles.values():
            for top, p in tops.items():
                tops[top] = "../296/" + p[2:]
    records = {}
    for style in ("curls", "straight"):
        entry = catalogue["Feminine"][style]
        entry["note"] = ("Layered curls with rounded turns and a fuller rear fall."
                         if style == "curls" else "Straight lengths with a soft inward taper at the ends.")
        source = {}
        for row in rows["rows"]:
            if row["hair"] == style and row["top"] == "open":
                source[(row["headwear"], row["hairColor"])] = local_path(row["parts"]["hair"])
        exports = {}
        for (hat, color), p in source.items():
            input_path = source[("none", color)] if hat == "pashmina" else p
            key = (input_path, hat == "pashmina")
            if key not in exports:
                target = out / f"{style}-{hat}-{color}.glb"
                rebuild(input_path, target, style, tuck=hat == "pashmina")
                exports[key] = "./assets/" + target.name
                records[target.name] = input_path.relative_to(ROOT).as_posix()
            entry["fits"].setdefault(hat, {})[color] = exports[key]
        covered = (REV / entry["fits"]["pashmina"]["default"]).resolve()
        hair = envelope(covered)
        for _ in range(5):
            hair = np.maximum(hair, np.maximum(np.roll(hair, 1, 1), np.roll(hair, -1, 1)) - .006)
        hair = smooth(hair, 2.5, 3.7)
        for top, p in cloth["Feminine"][style].items():
            source_cloth = (REV / p).resolve()
            target = out / f"scarf-{style}-{top}.glb"
            field = cloth_room(source_cloth, hair)
            deform(source_cloth, target, lambda points: fit_cloth(points, field, hair))
            cloth["Feminine"][style][top] = "./assets/" + target.name
            records[target.name] = source_cloth.relative_to(ROOT).as_posix()
        print(style, len(exports), flush=True)
    dump("hair-fits.json", catalogue)
    dump("pashmina-fits.json", cloth)
    dump("verification/sources.json", records)


if __name__ == "__main__":
    build(Path(sys.argv[-1]))
