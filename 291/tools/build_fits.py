"""Fit the approved 290 mesh to the existing headwear and bake its ombre ramp."""
import json
import sys
from pathlib import Path

import bpy
import numpy as np

REV = Path(__file__).resolve().parents[1]
ROOT = REV.parent
sys.path.insert(0, str(ROOT / "290/tools"))
from build_locks import make_hair
from build_hair import (BANGS_COLOR, CENTER, GOLD_COLOR, HATS, TOPS, cloth_for,
                        ease, ordinary, read_glb, smooth_max, surface, vectors, write_glb)

STYLE = "side-sweep"
SOURCE = ROOT / "290/assets/long.glb"
TAU = 2 * np.pi


def cloth_paths(hat):
    if hat == "pashmina":
        return [ordinary(path) for path in TOPS[STYLE].values()]
    return [cloth_for(STYLE, hat)]


def clearance_map(paths, margin, max_radius):
    # Sample the inner cloth from the head center. The neighboring samples
    # carry the compression past the contact line for a smooth transition.
    width, height = 384, 181
    yaw = np.linspace(-np.pi, np.pi, width, endpoint=False)
    pitch = np.linspace(-np.pi / 2, np.pi / 2, height)
    ca, sa = np.cos(yaw), np.sin(yaw)
    limits = np.full((height, width), .86)
    trees = [surface(path) for path in paths]
    for i, v in enumerate(pitch):
        cp = np.cos(v)
        directions = np.column_stack((cp * sa, np.full(width, np.sin(v)), cp * ca))
        for j, direction in enumerate(directions):
            for tree in trees:
                _, _, _, distance = tree.ray_cast(CENTER, direction, max_radius)
                if distance is not None:
                    limits[i, j] = min(limits[i, j], distance - margin)

    dy = np.pi / (height - 1)
    dx = TAU / width * np.maximum(.28, np.cos(pitch))[:, None]
    slope = .39 if margin > .010 else .57
    for _ in range(20):
        up = np.vstack((limits[:1], limits[:-1]))
        down = np.vstack((limits[1:], limits[-1:]))
        limits = np.minimum.reduce((limits, up + slope * dy, down + slope * dy,
                                    np.roll(limits, 1, axis=1) + slope * dx,
                                    np.roll(limits, -1, axis=1) + slope * dx))
    return limits


def interpolate_map(field, direction):
    height, width = field.shape
    u = (np.arctan2(direction[:, 0], direction[:, 2]) + np.pi) * (width / TAU)
    v = (np.arcsin(np.clip(direction[:, 1], -1, 1)) + np.pi / 2) * ((height - 1) / np.pi)
    col = np.floor(u).astype(int)
    row = np.minimum(np.floor(v).astype(int), height - 2)
    fx, fy = u - col, v - row
    left, right = col % width, (col + 1) % width
    top = field[row, left] * (1 - fx) + field[row, right] * fx
    bottom = field[row + 1, left] * (1 - fx) + field[row + 1, right] * fx
    return top * (1 - fy) + bottom * fy


def fit_mesh(hat):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    make_hair()
    obj = bpy.context.collection.objects[0]
    coords = np.empty((len(obj.data.vertices), 3), dtype=np.float32)
    obj.data.vertices.foreach_get("co", coords.ravel())
    world = coords[:, (0, 2, 1)].astype(float)
    world[:, 2] *= -1
    if hat == "pashmina":
        y = world[:, 1].copy()
        x, z = world[:, 0], world[:, 2] - CENTER[2]
        theta = np.arctan2(x, z)
        tuck = ease((1.734 - y) / .564)
        side = ease((np.abs(theta) - .71) / .58)
        wrap = ease((1.898 - y) / .37) * side
        # Draw the face-framing panels back into the hood before folding
        # the lower lengths inward near the nape.
        angle = theta + np.sign(theta) * .53 * wrap * (1 - ease((np.abs(theta) - 2.04) / .87))
        rho = np.hypot(x, z) * (1 - .29 * tuck - .055 * wrap)
        world[:, 0] = rho * np.sin(angle)
        world[:, 1] += .277 * tuck
        world[:, 2] = CENTER[2] + rho * np.cos(angle)

    margin = {"cap": .015, "beanie": .015, "headband": .019,
              "ears": .015, "pashmina": .010}.get(hat, .007)
    field = clearance_map(cloth_paths(hat), margin, .58 if hat == "pashmina" else .49)
    relative = world - CENTER
    radius = np.linalg.norm(relative, axis=1)
    direction = relative / radius[:, None]
    limit = interpolate_map(field, direction)
    transition = .031 if hat in {"cap", "beanie", "headband"} else .015
    radius = -smooth_max(-radius, -limit, transition)
    fitted = CENTER + direction * radius[:, None]
    coords[:, 0], coords[:, 1], coords[:, 2] = fitted[:, 0], -fitted[:, 2], fitted[:, 1]
    obj.data.vertices.foreach_set("co", coords.ravel())
    obj.data.update()

    path = REV / "assets" / f"long-{hat}.glb"
    bpy.ops.export_scene.gltf(filepath=str(path), export_format="GLB",
                              export_apply=True, export_materials="EXPORT")
    return path


def ombre(source, hat):
    model, data = read_glb(source)
    # The approved cut and all fitted exports are one mesh in shared glTF
    # coordinates. Only the color accessor and base factor are changed.
    primitive, = model["meshes"][0]["primitives"]
    xyz = vectors(model, data, primitive["attributes"]["POSITION"])
    assert "COLOR_0" not in primitive["attributes"]
    height = xyz[:, 1]
    a = np.arctan2(xyz[:, 0], xyz[:, 2] - CENTER[2])
    start, length = (1.87, .67) if hat != "pashmina" else (1.72, .32)
    progress = (start - height) / length
    progress += .064 * np.sin(7 * a + .57) * ease(progress / .55)
    blend = ease(progress)[:, None]
    shade = 1 + .046 * np.sin(17 * a + 1.8 * progress) * ease(progress / .7)
    colors = ((1 - blend) * BANGS_COLOR + blend * GOLD_COLOR) * shade[:, None]
    colors = np.clip(colors, 0, 1).astype("<f4")
    offset = len(data)
    data.extend(colors.tobytes())
    view = len(model["bufferViews"])
    model["bufferViews"].append({"buffer": 0, "byteOffset": offset,
                                 "byteLength": colors.nbytes, "target": 34962})
    accessors = model["accessors"]
    primitive["attributes"]["COLOR_0"] = len(accessors)
    accessors.append({"bufferView": view, "componentType": 5126,
                      "count": len(colors), "type": "VEC3"})
    material = model["materials"][primitive["material"]]
    material["name"] = "Hair / chestnut ombre"
    material["pbrMetallicRoughness"]["baseColorFactor"] = [1, 1, 1, 1]
    model["buffers"][0]["byteLength"] = len(data)
    path = REV / "assets" / f"long-{hat}-ombre.glb"
    write_glb(path, model, data)
    return path


def catalogue():
    fits = json.loads((ROOT / "280/hair-fits.json").read_text(encoding="utf8"))
    for pair in fits["Feminine"]["space-buns"]["fits"].values():
        assert all(path.startswith("../276/") for path in pair.values())
    variants = {}
    for hat in HATS:
        default = SOURCE if hat == "none" else fit_mesh(hat)
        colored = ombre(default, hat)
        variants[hat] = {
            "default": "../290/assets/long.glb" if hat == "none" else f"./assets/{default.name}",
            "ombre": f"./assets/{colored.name}",
        }
    fits["Feminine"][STYLE] = {
        "label": "Long Bangs",
        "note": "Rounded bangs with longer, separated layers behind the shoulders.",
        "fits": variants,
    }
    (REV / "hair-fits.json").write_text(json.dumps(fits, indent=2) + "\n",
                                       encoding="utf8", newline="\n")


if __name__ == "__main__":
    catalogue()
