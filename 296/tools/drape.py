"""Author the lower scarf drape and the long-hair exit together."""
import json
import sys
from pathlib import Path

import numpy as np

REV = Path(__file__).resolve().parents[1]
ROOT = REV.parent
sys.path.insert(0, str(ROOT / "294/tools"))
from repair import CENTER, accessor, ease, islands, local_path, node_transforms, read_glb, triangles, warp_normals, write_glb
from build_bandanas import CAT, ordinary, surface


LONG_HAIR = {"curls", "straight", "box-braids"}


def polar(points):
    x, y, z = (points - CENTER).T
    return np.arctan2(x, z), y, np.hypot(x, z)


def cartesian(theta, y, radius):
    return CENTER + np.column_stack((radius * np.sin(theta), y, radius * np.cos(theta)))


SUPPORT_Y0, SUPPORT_Y1 = 1.10, 1.64
SUPPORT_ROWS, SUPPORT_COLS = 109, 192


def garment_envelope(paths):
    trees = [surface(path, include) for path, include in paths]
    yaw = np.linspace(-np.pi, np.pi, SUPPORT_COLS, endpoint=False)
    rays = np.column_stack((np.sin(yaw), np.zeros(SUPPORT_COLS), np.cos(yaw)))
    field = np.zeros((SUPPORT_ROWS, SUPPORT_COLS))
    for row, height in enumerate(np.linspace(SUPPORT_Y0, SUPPORT_Y1, SUPPORT_ROWS)):
        origin = np.array([0, height, CENTER[2]])
        for col, direction in enumerate(rays):
            for tree in trees:
                if tree is None:
                    continue
                _, _, _, depth = tree.ray_cast(origin + .48 * direction, -direction, .48)
                if depth is not None:
                    field[row, col] = max(field[row, col], .48 - depth)
    # Bridge narrow garment details and taper the shoulder support vertically.
    for _ in range(4):
        field = np.maximum.reduce((
            field, np.roll(field, 1, axis=1) - .012, np.roll(field, -1, axis=1) - .012,
            np.vstack((field[:1], field[:-1])) - .012,
            np.vstack((field[1:], field[-1:])) - .012,
        ))
    return field


def support_radius(field, theta, height):
    u = (theta + np.pi) / (2 * np.pi) * SUPPORT_COLS
    v = np.clip((height - SUPPORT_Y0) / (SUPPORT_Y1 - SUPPORT_Y0), 0, 1) * (SUPPORT_ROWS - 1)
    i = np.floor(u).astype(int)
    j = np.minimum(np.floor(v).astype(int), SUPPORT_ROWS - 2)
    x, y = u - i, v - j
    left, right = i % SUPPORT_COLS, (i + 1) % SUPPORT_COLS
    return ((field[j, left] * (1 - x) + field[j, right] * x) * (1 - y)
            + (field[j + 1, left] * (1 - x) + field[j + 1, right] * x) * y)


def keep_shoulder_room(field, before, after):
    theta, y, r = polar(before)
    a, b, s = polar(after)
    original = support_radius(field, theta, before[:, 1])
    target = support_radius(field, a, after[:, 1])
    gap = np.minimum(.010, r - original)
    minimum = target + gap
    changed = np.linalg.norm(after - before, axis=1) > 1e-7
    return cartesian(a, b, np.where(changed, np.maximum(s, minimum), r))


def neck_cloth(points, style=None):
    theta, y, radius = polar(points)
    height = points[:, 1]
    low = 1 - ease((height - 1.418) / .365)
    side = ease((np.abs(theta) - .60) / .60)
    rim = ease((radius - .161) / .247)
    back = ease((np.abs(theta) - 1.53) / .98)
    # The widest fold roots come in with the hood; the crossed panels
    # are anchored on the chest below them.
    roots = np.maximum(ease((height - 1.368) / .099),
                       ease((radius - .31) / .060) * ease((height - 1.355) / .045))
    seat = low * side * rim * (roots + back * (1 - roots))
    pull = (.092 + .044 * back) * seat
    if style == "twin-braids":
        # The two front braids set the width of the side exits.
        braid = np.exp(-((np.abs(theta) - 1.27) / .56)**4)
        above_wrap = ease((height - 1.405) / .065)
        pull *= 1 - .89 * braid * above_wrap
    if style == "box-braids":
        pull *= .68 + .32 * back
    front_corner = np.exp(-((np.abs(theta) - 1.04) / .45)**2)
    front_corner *= np.exp(-((height - 1.51) / .13)**2) * rim
    if style != "twin-braids":
        pull += .030 * front_corner
        y -= .022 * front_corner
    skin = np.sqrt(np.maximum(0, .384**2 - y**2))
    limit = np.minimum(radius, skin + .013)
    clearance = np.maximum(radius - limit, 0.0)
    new_radius = radius - clearance * (1 - np.exp(-pull / np.maximum(clearance, 1e-5)))
    # The back hangs a little below the side exits and rejoins the wrap.
    rear_fold = back * ease((radius - .245) / .11)
    lower_edge = 1 - ease((height - 1.44) / .21)
    y -= .011 * back * seat + (.040 if style else .020) * rear_fold * lower_edge
    if style == "ponytail":
        # The tucked tail no longer needs a high, empty rear opening.
        nape = np.exp(-((np.pi - np.abs(theta)) / .39)**2)
        y -= .054 * nape * np.exp(-((height - 1.49) / .060)**2) * rim
    return cartesian(theta, y, new_radius)


def route_hair(points, style):
    theta, y, radius = polar(points)
    height = points[:, 1]
    fitted = neck_cloth(points, style=style)
    _, fitted_y, fitted_radius = polar(fitted)
    if style not in LONG_HAIR:
        return fitted

    start = .95 if style != "box-braids" else 1.61
    side = ease((np.abs(theta) - start) / .47)
    back = ease((np.abs(theta) - 1.62) / 1.03)
    gather = (1 - ease((height - 1.407) / .31)) * side
    # Route each bank through the nape. Shorten its covered travel enough
    # to keep the ends above the shoulders, with the front braids free.
    short = {"curls": .083, "straight": .114, "box-braids": .156}[style]
    rise = short * side * (.72 + .28 * back) * ease((1.646 - height) / .35)
    pull = np.maximum((radius - fitted_radius) * (side if style == "box-braids" else 1), (.103 + .046 * back) * gather)
    pull += .016 * side * np.exp(-((height - 1.469) / .108)**2)
    turn = (.13 if style == "curls" else .10) * gather * (1 - back)
    if style == "box-braids":
        fitted_y = y + side * (fitted_y - y)
    skin = np.sqrt(np.maximum(0, .384**2 - (fitted_y + rise)**2))
    return cartesian(theta + np.sign(theta) * turn, fitted_y + rise,
                     np.maximum(radius - pull, np.minimum(radius, skin + .008)))


def seat_over_hair(points, drape, field):
    theta, y, radius = polar(drape)
    original = polar(points)[2]
    support = support_radius(field, theta, drape[:, 1])
    around_head = ease((np.abs(theta) - 1.00) / .40)
    hem = ease((points[:, 1] - 1.345) / .035) * (1 - ease((points[:, 1] - 1.565) / .085))
    fabric = ease((original - .259) / .043)
    reserve = np.clip(support + .015 - radius, 0, .078) * hem * around_head * fabric
    return cartesian(theta, y, radius + reserve)


def soften_field(field, passes):
    for _ in range(passes):
        field = (.48 * field + .13 * (np.roll(field, 1, axis=1) + np.roll(field, -1, axis=1)
                                      + np.vstack((field[:1], field[:-1]))
                                      + np.vstack((field[1:], field[-1:]))))
    return field


def turn_along_path(vectors, tangent, target_tangent):
    axis = np.cross(tangent, target_tangent)
    cosine = np.sum(tangent * target_tangent, axis=1, keepdims=True)
    cross = np.cross(axis, vectors)
    return vectors + cross + np.cross(axis, cross) / np.maximum(1 + cosine, .2)


def follow_lock_centers(points, normals, uv, indices, warp):
    """Move original sculpted cross-sections along the revised lock paths."""
    labels = islands(points, indices)
    result, shading = points.copy(), normals.copy()
    for label in np.unique(labels):
        selected = labels == label
        _, ring = np.unique(uv[selected, 1].round(5), return_inverse=True)
        count = np.bincount(ring)
        assert len(count) >= 60
        origin = np.column_stack([np.bincount(ring, weights=axis) / count
                                  for axis in points[selected].T])
        target = warp(origin)
        theta, y, radius = polar(target)
        tip = origin[0] - CENTER
        exit_angle = abs(np.arctan2(tip[0], tip[2]))
        # Gather toward the two side exits. The front and center banks
        # remain under the wrap as they turn toward the nape.
        side_exit = np.exp(-((exit_angle - 1.90) / .38)**4)
        under_wrap = 1 - ease((origin[:, 1] - 1.36) / .30)
        front_bank = 1 - ease((exit_angle - 1.35) / .30)
        y += (.119 * (1 - side_exit) + .029 * front_bank - .027 * side_exit) * under_wrap
        radius -= (.038 + .024 * side_exit) * under_wrap
        delta = cartesian(theta, y, radius) - origin
        for _ in range(6):
            delta[1:-1] = (.30 * delta[:-2] + .40 * delta[1:-1] + .30 * delta[2:])
        target = origin + delta
        before, after = np.gradient(origin, axis=0), np.gradient(target, axis=0)
        before /= np.maximum(np.linalg.norm(before, axis=1, keepdims=True), 1e-8)
        after /= np.maximum(np.linalg.norm(after, axis=1, keepdims=True), 1e-8)
        offset = points[selected] - origin[ring]
        result[selected] = target[ring] + turn_along_path(offset, before[ring], after[ring])
        shading[selected] = turn_along_path(normals[selected], before[ring], after[ring])
    return result, shading


def deform(source, target, warp, locks=False):
    model, binary = read_glb(source)
    maximum = 0.
    for node, rotation, offset in node_transforms(model):
        if "mesh" not in node:
            continue
        mesh = model["meshes"][node["mesh"]]
        for primitive in mesh["primitives"]:
            attrs = primitive["attributes"]
            p = accessor(model, binary, attrs["POSITION"], 3)
            n = accessor(model, binary, attrs["NORMAL"], 3)
            points, normals = p @ rotation.T + offset, n @ rotation.T
            if locks and "side sweep" in mesh["name"]:
                uv = accessor(model, binary, attrs["TEXCOORD_0"], 2)
                indices = triangles(model, binary, primitive["indices"])
                updated, shading = follow_lock_centers(points, normals, uv, indices, warp)
            else:
                updated = warp(points)
                shading = warp_normals(warp, points, normals)
            distance = np.linalg.norm(updated - points, axis=1)
            moved = distance > 1e-6
            p[moved] = (updated[moved] - offset) @ rotation
            n[moved] = shading[moved] @ rotation
            model["accessors"][attrs["POSITION"]].update(min=p.min(axis=0).tolist(), max=p.max(axis=0).tolist())
            assert np.isfinite(p).all() and np.isfinite(n).all(), source
            maximum = max(maximum, float(distance.max()))
    write_glb(target, model, binary)
    return maximum


def relative(path):
    return "./" + path.relative_to(REV).as_posix()


def build(receipt):
    (REV / "assets").mkdir(exist_ok=True)
    baseline = json.loads(receipt.read_text(encoding="utf8"))
    assert baseline["revision"] == "295"
    catalogue = json.loads((ROOT / "295/hair-fits.json").read_text(encoding="utf8"))
    for build in catalogue.values():
        for style in build.values():
            for choice in style["fits"].values():
                for color, path in choice.items():
                    if path.startswith("./"):
                        choice[color] = "../295/" + path[2:]

    garment_fields = {}
    for build, catalog in CAT["builds"].items():
        base = ordinary(catalog["pantsBases"]["clothed"])
        torso = lambda name: name.startswith("Skin / rounded torso")
        shirt = lambda name: not any(token in name.lower() for token in ("sleeve", "cuff", "cord", "string"))
        for top, entry in catalog["tops"].items():
            paths = [(base, torso)]
            if entry["path"]:
                paths.append(((ROOT / "263" / entry["path"]).resolve(), shirt))
            garment_fields[(build, top)] = garment_envelope(paths)
    combined = {build: np.maximum.reduce([field for (b, _), field in garment_fields.items() if b == build])
                for build in CAT["builds"]}

    combined = {build: soften_field(field, 12) for build, field in combined.items()}

    sources = {}
    for row in baseline["rows"]:
        key = (row["build"], row["hair"], row["hairColor"])
        source = local_path(row["parts"]["hair"])
        assert sources.setdefault(key, source) == source
    hair_support = {}
    for (build, style, color), source in sources.items():
        choice = catalogue.setdefault(build, {}).setdefault(style, {
            "label": CAT["builds"][build]["hair"][style]["label"],
            "note": CAT["builds"][build]["hair"][style]["note"], "fits": {},
        })
        target = REV / "assets" / f"{build.lower()}-{style}-pashmina-{color}.glb"
        deform(source, target, lambda p: keep_shoulder_room(combined[build], p, route_hair(p, style)),
               locks=style in {"curls", "straight"})
        choice["fits"].setdefault("pashmina", {})[color] = relative(target)
        if style in LONG_HAIR and color == "default":
            field = garment_envelope([(target, lambda _: True)])
            hair_support[style] = soften_field(field, 11)

    cloth_fits, edited = {}, {}
    for build, styles in CAT["pashminaHairFamilies"].items():
        cloth_fits[build] = {}
        for style, family in styles.items():
            cloth_fits[build][style] = {}
            for top, file in CAT["pashminaVariants"][build][family].items():
                source = ordinary(file)
                mode = style if style in LONG_HAIR | {"ponytail", "twin-braids"} else None
                key = (source, mode)
                if key not in edited:
                    target = REV / "assets" / f"scarf-{len(edited)+1:02d}.glb"

                    def drape(points):
                        moved = neck_cloth(points, style=mode)
                        if mode in hair_support:
                            moved = seat_over_hair(points, moved, hair_support[mode])
                        return keep_shoulder_room(garment_fields[(build, top)], points, moved)

                    amount = deform(source, target, drape)
                    assert amount > .05
                    edited[key] = relative(target)
                cloth_fits[build][style][top] = edited[key]
    for file, data in (("hair-fits.json", catalogue), ("pashmina-fits.json", cloth_fits)):
        (REV / file).write_text(json.dumps(data, indent=2) + "\n", encoding="utf8", newline="\n")
    print(f"Exported {len(edited)} scarf fits", flush=True)


if __name__ == "__main__":
    build(Path(sys.argv[-1]))