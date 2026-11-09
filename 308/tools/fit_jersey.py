"""Lower the feminine jersey's front opening on its original cloth surface."""
import math
from pathlib import Path
import sys

import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

CENTER = np.array([0., .02])
ROWS, COLS = 78, 128
FRONT = 3 * math.pi / 2
CLOTH = "Clothing / closed torso201 jersey"
BINDING = "Neckline / jersey binding203"
PLACKET = "Jersey / continuous placket202"


def positions(obj):
    return np.array([obj.matrix_world @ v.co for v in obj.data.vertices])


def update(obj, points):
    inverse = obj.matrix_world.inverted()
    for vertex, p in zip(obj.data.vertices, points, strict=True):
        vertex.co = inverse @ Vector(p)
    obj.data.update()


def collar_drop(theta):
    distance = abs(math.remainder(theta - FRONT, 2 * math.pi))
    # Round the base of the opening and ease it into the original collar.
    inner = math.hypot(distance, .095) - .095
    return .112 * max(0., 1 - inner / .94)**1.42


def angle(point):
    return math.atan2(point[1] - CENTER[1], point[0]) % (2 * math.pi)


def radial_sample(grid, height, theta):
    index = theta * COLS / (2 * math.pi)
    column = int(index) % COLS
    weight = index - int(index)
    columns = grid[:, [column, (column + 1) % COLS], :]
    radii = np.linalg.norm(columns[:, :, :2] - CENTER, axis=2)
    a, b = [np.interp(height, columns[:, i, 2], radii[:, i]) for i in (0, 1)]
    return (1 - weight) * a + weight * b


def torso_support(torso):
    vertices = positions(torso)
    polygons = [list(poly.vertices) for poly in torso.data.polygons]
    return BVHTree.FromPolygons(vertices.tolist(), polygons)


def seat_edge(tree, xyz, theta, drop):
    outward = np.array([math.cos(theta), math.sin(theta)])
    start = CENTER + outward
    hit, _, _, _ = tree.ray_cast((*start, xyz[2]), (*(-outward), 0.), 1.)
    if hit is None:
        return np.zeros(2)
    radius = np.linalg.norm(xyz[:2] - CENTER)
    skin = np.linalg.norm(np.array(hit[:2]) - CENTER)
    blend = min(1., drop / .078)
    return outward * (max(0., radius - skin - .019) * blend)


def neckline(cloth, torso):
    old = positions(cloth).reshape(ROWS, COLS, 3)
    updated = old.copy()
    anchor = 1.220
    support = torso_support(torso)
    for j in range(COLS):
        theta = j * 2 * math.pi / COLS
        drop = collar_drop(theta)
        if drop == 0:
            continue
        z = old[:, j, 2]
        assert np.all(np.diff(z) > 0), j
        upper = z > anchor
        factor = (z[-1] - anchor - drop) / (z[-1] - anchor)
        new_height = anchor + (z[upper] - anchor) * factor
        for axis in (0, 1):
            updated[upper, j, axis] = np.interp(new_height, z, old[:, j, axis])
        updated[upper, j, 2] = new_height
        seat = seat_edge(support, updated[-1, j], theta, drop)
        weight = np.clip((new_height - 1.233) / .060, 0., 1.)
        weight /= max(weight[-1], .0001)
        weight = weight**2 * (3 - 2*weight)
        updated[upper, j, :2] -= weight[:, None] * seat
    update(cloth, updated.reshape(-1, 3))
    return old, updated


def cloth_edge(obj, old, new):
    points = positions(obj)
    for p in points:
        theta = angle(p)
        drop = collar_drop(theta)
        if drop == 0:
            continue
        h = p[2] - drop
        offset = np.linalg.norm(p[:2] - CENTER) - radial_sample(old, p[2], theta)
        radius = radial_sample(new, h, theta) + offset
        p[:2] = CENTER + radius * np.array([math.cos(theta), math.sin(theta)])
        p[2] = h
    update(obj, points)


def placket(obj, old, new):
    points = positions(obj)
    anchor = 1.233
    seam_top = new[-1, 96, 2] + .002
    max_height = points[:, 2].max()
    for p in points:
        if p[2] <= anchor:
            continue
        theta = angle(p)
        h = anchor + (p[2] - anchor) / (max_height - anchor) * (seam_top - anchor)
        # The closed placket remains seated on the curved chest.
        offset = np.clip(np.linalg.norm(p[:2] - CENTER) - radial_sample(old, p[2], theta), .001, .004)
        radius = radial_sample(new, h, theta) + offset
        p[:2] = CENTER + radius * np.array([math.cos(theta), math.sin(theta)])
        p[2] = h
    update(obj, points)


def print_uv(cloth):
    world = positions(cloth)
    uv = cloth.data.uv_layers.active
    for poly in cloth.data.polygons:
        points = world[list(poly.vertices)]
        u = [angle(p)/(2*math.pi) for p in points]
        if max(u) - min(u) > .5:
            u = [x+1 if x < .5 else x for x in u]
        for loop, p, x in zip(poly.loop_indices, points, u, strict=True):
            uv.data[loop].uv = (x, (p[2]-1.03)/.405)


def seat_button(obj, x, height, support):
    hits = [mesh.ray_cast((x, -.75, height), (0., 1., 0.), 1.) for mesh in support]
    contact, normal, _, _ = min((hit for hit in hits if hit[0] is not None), key=lambda hit: hit[0].y)
    assert normal.y < -.25
    points = positions(obj)
    orient = Vector((0., -1., 0.)).rotation_difference(normal)
    local = np.array([orient @ Vector(p) for p in points - points.mean(axis=0)])
    n = np.array(normal)
    seat = -.0008 - (local @ n).min()
    update(obj, local + np.array(contact) + n * seat)


def open_buttons(scene, grid):
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    shirt, seam = [torso_support(scene.objects[key].evaluated_get(depsgraph)) for key in (CLOTH, PLACKET)]
    upper = scene.objects["Jersey / button202.004"]
    x, _, h = positions(upper).mean(axis=0)
    seat_button(upper, x, h, (shirt, seam))

    # Put one unfastened button on the outer side of the open binding.
    h = 1.330
    column = next(j for j in range(98, 115) if grid[-1, j, 2] > h + .008)
    theta = column * 2 * math.pi / COLS
    x = radial_sample(grid, h, theta) * math.cos(theta)
    spare = scene.objects["Jersey / button202.005"]
    seat_button(spare, x, h, (shirt,))
    spare.name = "Jersey / unfastened button308"
    bpy.data.objects.remove(scene.objects["Jersey / button202.006"], do_unlink=True)

def build(print_path, export_path, source_path):
    s = bpy.context.scene
    cloth = s.objects[CLOTH]
    old, new = neckline(cloth, s.objects["Skin / rounded torso"])
    cloth_edge(s.objects[BINDING], old, new)
    placket(s.objects[PLACKET], old, new)
    open_buttons(s, new)
    print_uv(cloth)
    material = cloth.data.materials[0]
    texture = next(n for n in material.node_tree.nodes if n.type == "TEX_IMAGE"
                   and n.image and "atlas" in n.image.name)
    texture.image = bpy.data.images.load(str(print_path))
    texture.image.pack()
    # Save the fitted source and export only its independently selectable top.
    bpy.context.view_layer.update()
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(source_path))
    bpy.ops.object.select_all(action="DESELECT")
    for obj in s.objects:
        if obj.get("component159") == "top":
            obj.select_set(True)
    bpy.context.view_layer.objects.active = cloth
    bpy.ops.export_scene.gltf(filepath=str(export_path), export_format="GLB",
                              use_selection=True, export_apply=True, export_yup=True)
    print("Opening apex", new[-1, 96].tolist(), flush=True)


if __name__ == "__main__":
    build(*map(Path, sys.argv[-3:]))
