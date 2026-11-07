"""Combine the long cut with a rounded fall and genuinely separated ends."""
import json
import sys
from pathlib import Path

import bpy
import numpy as np

REV = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REV.parent / "289/tools"))
from build_cuts import (BANGS_COLOR, CENTER, RADIUS, air_radius, angles_of,
                        ease, hair_material, longer_lob, lower_cut,
                        refine_fringe_sampling)

# Full-length bands measured clockwise from the front left to the front right.
BOUNDS = np.array([1.37, 1.71, 1.98, 2.28, 2.56, 2.80, 3.06,
                   3.32, 3.56, 3.85, 4.15, 4.46, 4.86])
END_LIFTS = (.019, .010, .005, .023, .015, -.016, .008, .020, .007, .029, .008, .023)
TURNS = (.056, .045, -.058, -.041, -.053, -.065, .048, .061, .043, -.052, -.044, -.051)


def rounded_bangs(points, angle):
    y = points[:, :, 1].copy()
    end = y[-1]
    reach = 1 - ease((np.abs(angle) - .666) / .194)
    extent = np.sin(.675)
    beat = (np.sin(angle) + extent) * 11 / (2 * extent)
    # A shallow, rounded opening gives each end a broader outline.
    wave = .5 + .5 * np.cos(2 * np.pi * beat)
    line = 1.967 + .024 * wave**2.15
    line += .003 * np.cos(5 * angle + .42) - .018 * ease((np.abs(angle) - .46) / .34)
    weight = reach * ease((2.139 - y) / np.maximum(.063, 2.139 - end))
    adjusted = y + weight * (line - end)
    radius = np.hypot(points[:, :, 0], points[:, :, 2] - CENTER[2])
    radius += air_radius(adjusted) - air_radius(y)
    skin = np.sqrt(np.maximum(.000001, RADIUS**2 - (adjusted - CENTER[1])**2))
    arch = .017 * np.exp(-((adjusted - 2.064) / .061)**2)
    detail = .0018 * (1 - wave) * ease((2.136 - adjusted) / .09)
    settled = skin + .008 + arch + detail
    fit = reach * ease((2.167 - adjusted) / .119)
    radius += fit * (settled - radius)
    a = angles_of(points)
    front = reach > 0
    points[:, front, 0] = (radius * np.sin(a))[:, front]
    points[:, front, 1] = adjusted[:, front]
    points[:, front, 2] = (CENTER[2] + radius * np.cos(a))[:, front]


def source_surface():
    points, progress, shade = longer_lob()
    points, _, _, angle = refine_fringe_sampling(points, progress, shade)
    # Insert the exact parting lines into the grid before building the crown.
    cuts = (BOUNDS + np.pi) % (2 * np.pi) - np.pi
    refined = np.unique(np.concatenate((angle, cuts)))
    points = np.stack([np.stack([np.interp(refined, angle, row, period=2 * np.pi)
                                 for row in points[:, :, dim]]) for dim in range(3)], axis=-1)
    long = points.copy()
    lower_cut(long, True)
    lower_cut(points, False)
    points[:, :, 1] = long[:, :, 1]
    # The fall from A is longer here. Retain the tested clearance from B
    # in the narrow passage between the torso and sleeves.
    a = angles_of(points)
    y = points[:, :, 1]
    sleeve = ease((np.abs(a) - 1.05) / .25) * (1 - ease((np.abs(a) - 1.89) / .32))
    sleeve *= ease((1.52 - y) / .19)
    for dim in (0, 2):
        points[:, :, dim] += sleeve * (long[:, :, dim] - points[:, :, dim])
    # Smooth the short transition where the inherited cheek frame joins the
    # longer side lengths. The fringe and the rear keep their own contours.
    near_cheek = ease((np.abs(refined) - .87) / .17)
    near_cheek *= 1 - ease((np.abs(refined) - 1.19) / .26)
    for dim in range(3):
        values = points[:, :, dim]
        left = np.stack([np.interp(refined - .064, refined, row, period=2 * np.pi) for row in values])
        right = np.stack([np.interp(refined + .064, refined, row, period=2 * np.pi) for row in values])
        values += .35 * near_cheek * (left + right - 2 * values)
    # Sculpt the grain along the same paths that separate at the ends.
    a = angles_of(points)
    r = np.hypot(points[:, :, 0], points[:, :, 2] - CENTER[2])
    y = points[:, :, 1]
    u = refined % (2 * np.pi)
    for index, (left, right) in enumerate(zip(BOUNDS[:-1], BOUNDS[1:])):
        width = right - left
        center = .5 * (left + right) + .035 * np.sin(4 * y + index)
        lane = (u - center) / (.43 * width)
        swell = .010 * np.exp(-lane**2) - .0023 * np.exp(-((lane + 1.10) / .34)**2)
        swell += .0019 * np.cos(4.8 * lane + .34 * np.sin(9 * y)) * np.exp(-lane**2)
        r += swell * ease((1.87 - y) / .28)
    side = np.abs(a) > 1.0
    points[:, :, 0][side] = (r * np.sin(a))[side]
    points[:, :, 2][side] = (CENTER[2] + r * np.cos(a))[side]
    rounded_bangs(points, refined)
    return points, refined


def crown_to_split(points, angle):
    # Keep an unbroken crown and hairline. The side and back splits start
    # around the nape, with a lower start at the outer face-framing locks.
    u = angle % (2 * np.pi)
    inside = ease((u - BOUNDS[0]) / .23) * ease((BOUNDS[-1] - u) / .22)
    y = points[:, :, 1]
    edge = y[-1]
    split_length = .114 + .021 * np.sin(3 * angle + .51)
    root = edge + inside * split_length * ease((1.61 - edge) / .14)
    crown = points.copy()
    for col in np.flatnonzero(root > edge):
        amount = (y[0, col] - root[col]) / (y[0, col] - edge[col])
        height = y[0, col] + amount * (y[:, col] - y[0, col])
        for dim in (0, 2):
            crown[:, col, dim] = np.interp(height, y[::-1, col], points[::-1, col, dim])
        crown[:, col, 1] = height
    return crown


def add_lock(vertices, faces, weights, source, crown, cols, count, index, clear_edges):
    root = crown[-1, cols]
    y0 = root[:, 1]
    a0 = np.unwrap(angles_of(root))
    center = .5 * (a0[0] + a0[-1])
    cross = np.linspace(-1, 1, len(cols))
    root_y = np.interp(0, cross, y0)
    tip_y = float(np.interp(0, cross, source[-1, cols, 1])) + END_LIFTS[index]
    tip_y = max(1.161, min(tip_y, float(y0.min()) - .016))
    drift = np.clip(TURNS[index], .82 * (a0[0] - center), .82 * (a0[-1] - center))
    heights = source[::-1, cols, 1]
    radii = np.hypot(source[::-1, cols, 0], source[::-1, cols, 2] - CENTER[2])
    previous = [(crown.shape[0] - 1) * count + col for col in cols]
    rows = 42
    for step in range(1, rows):
        t = step / rows
        closure = np.sqrt(1 - np.clip((t - .70) / .30, 0, 1)**2)
        taper = ease((t - .20) / .65)
        if clear_edges:
            # Start the split where the locks leave their shared root. Waiting
            # until a fifth of the way down leaves two coincident side walls.
            taper = .22 * ease(t / .29) + .78 * ease(t / .85)
        breadth = (1 - (.31 + .046 * (index % 3)) * taper) * closure
        theta = center + (a0 - center) * breadth + drift * (1 - breadth)
        # Keep the tips broad. The width only closes over the final arc.
        y = tip_y + (root_y - tip_y) * (1 - t)
        if clear_edges:
            # Let each lane descend all the way to the tip. The old width
            # term could leave some corners lower than the tip itself.
            y += (y0 - root_y) * (1 - t)
        else:
            y += (y0 - root_y) * breadth * (1 - .28 * t)
            y += (.004 * cross**2 + .004 * cross * np.sign(drift)) * np.sin(np.pi * t)
        r = np.array([np.interp(h, heights[:, k], radii[:, k]) for k, h in enumerate(y)])
        mid_r = np.interp(0, cross, r)
        r = mid_r + (r - mid_r) * breadth
        dome = ease(t / .55) * (1 - .77 * ease((t - .78) / .22))
        r += (.006 + .002 * (index % 3)) * dome * (1 - cross**2)**2
        r += .0016 * np.cos(3 * np.pi * cross + .5 * t) * dome
        r -= .006 * ease((t - .58) / .42)
        ring = np.column_stack((r * np.sin(theta), y, CENTER[2] + r * np.cos(theta)))
        current = list(range(len(vertices), len(vertices) + len(ring)))
        vertices.extend(ring.tolist())
        weights.extend([.010 + .004 * dome - .005 * ease((t - .73) / .27)] * len(ring))
        faces.extend((previous[i], current[i], current[i + 1], previous[i + 1])
                     for i in range(len(ring) - 1))
        previous = current

    r = np.interp(0, cross, [np.interp(tip_y, heights[:, k], radii[:, k])
                             for k in range(len(cols))]) - .006
    theta = center + drift
    tip = len(vertices)
    vertices.append((r * np.sin(theta), tip_y, CENTER[2] + r * np.cos(theta)))
    weights.append(.005)
    faces.extend((previous[i], tip, previous[i + 1]) for i in range(len(previous) - 1))


def soften_side_fall(points, angle):
    # Smooth the change in curvature above the tips where the side panels
    # move in for sleeve clearance. Leave the hem and rear grooves alone.
    y = points[:, :, 1]
    azimuth = angles_of(points)
    radius = np.hypot(points[:, :, 0], points[:, :, 2] - CENTER[2])
    filtered = radius.copy()
    for col in np.flatnonzero((np.abs(angle) > .91) & (np.abs(angle) < 2.13)):
        heights = y[::-1, col]
        radial = radius[::-1, col]
        h = y[:, col]
        filtered[:, col] = (
            np.interp(h - .082, heights, radial)
            + 2 * np.interp(h - .041, heights, radial)
            + 2 * np.interp(h + .041, heights, radial)
            + np.interp(h + .082, heights, radial)
        ) / 6
    side = ease((np.abs(angle) - .91) / .30) * (1 - ease((np.abs(angle) - 1.80) / .33))
    length = ease((y - y[-1]) / .080) * (1 - ease((y - 1.51) / .14))
    radius += .95 * side * length * np.clip(filtered - radius, -.008, .008)
    points[:, :, 0] = radius * np.sin(azimuth)
    points[:, :, 2] = CENTER[2] + radius * np.cos(azimuth)


def make_hair(clear_edges=False):
    source, angle = source_surface()
    if clear_edges:
        soften_side_fall(source, angle)
    crown = crown_to_split(source, angle)
    rows, count, _ = crown.shape
    vertices = crown.reshape(-1, 3).tolist()
    faces = [tuple(range(count))]
    y = crown[:, :, 1]
    end = 1 - ease((y - y[-1]) / .065)
    weights = (.010 - .003 * end).ravel().tolist()
    for j in range(rows - 1):
        above = j * count
        below = above + count
        faces.extend((above + i, below + i, below + (i + 1) % count, above + (i + 1) % count)
                     for i in range(count))

    u = angle % (2 * np.pi)
    order = np.argsort(u)
    for index, (left, right) in enumerate(zip(BOUNDS[:-1], BOUNDS[1:])):
        cols = order[(u[order] >= left - 1e-8) & (u[order] <= right + 1e-8)]
        add_lock(vertices, faces, weights, source, crown, cols, count, index, clear_edges)

    name = "Hair / rounded long fringe"
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([(x, -z, h) for x, h, z in vertices], [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    mesh.materials.append(hair_material(False, BANGS_COLOR, .40))
    for polygon in mesh.polygons:
        polygon.use_smooth = len(polygon.vertices) < 5
    inset = obj.modifiers.new("Soft edges", "SOLIDIFY")
    inset.thickness = .014
    inset.offset = -1
    inset.thickness_vertex_group = .004 / .014
    group = obj.vertex_groups.new(name="Tip thickness")
    for index, value in enumerate(weights):
        group.add([index], (value - .004) / .010, "REPLACE")
    inset.vertex_group = group.name


def export():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    make_hair()
    asset = "./assets/long.glb"
    bpy.ops.export_scene.gltf(filepath=str(REV / asset), export_format="GLB",
                              export_apply=True, export_materials="EXPORT")
    manifest = {"Feminine": {"side-sweep": {
        "label": "Rounded long fringe", "note": "Bare-head review",
        "fits": {"none": {"default": asset, "ombre": asset}},
    }}}
    (REV / "hair.json").write_text(json.dumps(manifest, indent=2) + "\n",
                                    encoding="utf8", newline="\n")


if __name__ == "__main__":
    export()
