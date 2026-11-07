"""Compare lower layers and a small spacing adjustment to the 281 fringe."""
import json
import sys
from pathlib import Path

import bpy
import numpy as np

REV = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REV.parent / "287/tools"))
from build_fringe import BANGS_COLOR, CENTER, ease, hair_material, longer_lob, shell
from build_hair import grid_mesh
from build_studies import air_radius

# Angle, beginning height, hem lift, half-width, drift, and outward relief.
LAYERS = (
    (-2.45, 1.87, -.006, .244, -.111, .024),
    (-1.95, 1.78,  .019, .176,  .086, .015),
    (-1.28, 1.84,  .014, .198,  .104, .020),
    ( 1.25, 1.83,  .007, .184, -.097, .018),
    ( 1.95, 1.76,  .018, .179,  .141, .018),
    ( 2.46, 1.84, -.004, .244,  .127, .025),
    ( 3.03, 1.74,  .014, .191, -.099, .020),
)
# Shorter, recessed layers show through at the raised parts of the hem.
UNDERLAYERS = (
    (-1.98, .185, -.010, .048),
    ( 1.93, .173, -.010, .054),
    ( 2.90, .201, -.013, .069),
)

# Same six gaps as 281. The smaller ones group pairs of locks more loosely.
GAPS = (
    ((-.542, .041, .043), (-.547, .036, .028)),
    ((-.292, .065, .074), (-.318, .067, .074)),
    ((-.047, .036, .048), (-.067, .031, .033)),
    (( .160, .065, .066), ( .184, .061, .070)),
    (( .431, .054, .055), ( .416, .046, .047)),
    (( .608, .039, .030), ( .610, .036, .019)),
)


def gap(angles, center, width, height):
    width = width * np.where(angles < center, 1.13, .80)
    return height * np.exp(-((angles - center) / width)**2)


def regroup_fringe(points):
    angle = np.linspace(-np.pi, np.pi, points.shape[1], endpoint=False)
    change = sum(gap(angle, *new) - gap(angle, *old) for old, new in GAPS)
    change *= 1 - ease((np.abs(angle) - .68) / .12)
    y = points[:, :, 1].copy()
    edge = y[-1]
    weight = ease((2.132 - y) / np.maximum(.054, 2.132 - edge))
    new_y = y + weight * change
    moved = new_y != y
    radius = np.hypot(points[:, :, 0], points[:, :, 2] - CENTER[2])
    scale = (radius + air_radius(new_y) - air_radius(y)) / radius
    points[:, :, 0][moved] *= scale[moved]
    points[:, :, 1][moved] = new_y[moved]
    points[:, :, 2][moved] = CENTER[2] + (points[:, :, 2][moved] - CENTER[2]) * scale[moved]


def around(points):
    return np.arctan2(points[..., 0], points[..., 2] - CENTER[2])


def layer_shape(points):
    y = points[:, :, 1].copy()
    angle = around(points)
    radius = np.hypot(points[:, :, 0], points[:, :, 2] - CENTER[2])
    lower = ease((1.88 - y) / .255) * ease((np.abs(angle) - .93) / .26)
    distance_to_tip = y - y[-1]
    near_tip = 1 - ease(distance_to_tip / .151)
    loft = np.zeros_like(y)
    hem_shift = np.zeros_like(y)
    body = np.zeros_like(y)
    for center, start, lift, width, turn, depth in LAYERS:
        travel = ease((start - y) / np.maximum(.20, start - y[-1]))
        direction = center + turn * travel + .061 * np.sin(np.pi * travel)
        signed = (angle - direction + np.pi) % (2 * np.pi) - np.pi
        span = width * (1 - .23 * travel)
        lock = np.exp(-(signed / span)**2)
        # The convex side blends into the next lock. A narrower trough
        # trails one edge of each curve and dies out toward the root.
        groove = np.exp(-((signed - .81 * span) / (.33 * span))**2)
        swell = ease((start - y) / .22) * (1 - .50 * near_tip)
        loft += depth * swell * (lock - .22 * groove)
        hem_shift += lift * lock
        body += lock

    changes = lower > 0
    radius += lower * (loft - .0025 * near_tip * np.minimum(body, 1.4))
    y += lower * near_tip * hem_shift
    points[:, :, 0][changes] = (radius * np.sin(angle))[changes]
    points[:, :, 1][changes] = y[changes]
    points[:, :, 2][changes] = (CENTER[2] + radius * np.cos(angle))[changes]
    return lower * np.minimum(body, 1) * (1 - .60 * near_tip)

def radius_at(points, y, angle):
    heights = points[:, :, 1]
    cols = np.arange(points.shape[1])
    row = np.clip(np.count_nonzero(heights >= y, axis=0) - 1, 0, points.shape[0] - 2)
    top = points[row, cols]
    bottom = points[row + 1, cols]
    t = np.clip((top[:, 1] - y) / (top[:, 1] - bottom[:, 1]), 0, 1)
    ring = top + t[:, None] * (bottom - top)
    radius = np.hypot(ring[:, 0], ring[:, 2] - CENTER[2])
    return np.interp(angle, around(ring), radius, period=2 * np.pi)


def add_underlayers(points, material):
    hem = points[-1]
    hem_angle = around(hem)
    t = np.linspace(0, 1, 32)
    circle = np.linspace(0, 2 * np.pi, 18, endpoint=False)
    close = np.sqrt(np.maximum(.002, 1 - np.clip((t - .76) / .24, 0, 1)**2))
    for index, (center, width, drop, turn) in enumerate(UNDERLAYERS):
        direction = center + turn * ease(t)
        angle = direction[:, None] + width * close[:, None] * np.cos(circle)
        end = np.interp(direction[-1], hem_angle, hem[:, 1], period=2 * np.pi)
        end = max(end + drop, float(hem[:, 1].min()) + .002)
        y = end + .093 * (1 - t)
        radius = np.stack([radius_at(points, height, ring) for height, ring in zip(y, angle)])
        # Seat the roots inside the shell. A thin, recessed arc shows at the
        # hem, with no exposed upper seam.
        radius += .0042 * close[:, None] * np.sin(circle) - (.0075 + .005 * t[:, None])
        rings = np.stack((radius * np.sin(angle), np.broadcast_to(y[:, None], radius.shape),
                          CENTER[2] + radius * np.cos(angle)), axis=-1)
        neutral = np.ones(rings.shape[:2])
        grid_mesh(f"Hair / tucked lower lock {index + 1}", rings, neutral, neutral, material,
                  False, BANGS_COLOR, loop=True, radial_normals=False)

def make_hair(regroup):
    points, progress, shade = longer_lob()
    mass = layer_shape(points)
    if regroup:
        regroup_fringe(points)
    material = hair_material(False, BANGS_COLOR, .37)
    name = "Hair / soft brow fringe"
    shell(name, points, progress, shade, material, False, BANGS_COLOR, loop=True)
    body = bpy.data.objects[name]
    inset = body.modifiers["Inset edge thickness"]
    group = body.vertex_groups.new(name="Hem thickness")
    hem = ease((np.abs(around(points)) - .90) / .46) * ease((1.62 - points[:, :, 1]) / .27)
    # Thicken behind the rounded surface and taper back to a light edge.
    # Use the original rim thickness at the approved fringe.
    inset.thickness = .019
    inset.thickness_vertex_group = .0045 / .019
    weight = (.010 - .0055 * hem + .008 * mass - .0045) / (.019 - .0045)
    for index, value in enumerate(weight.ravel()):
        group.add([index], float(np.clip(value, 0, 1)), "REPLACE")
    inset.vertex_group = group.name
    body.select_set(True)
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.modifier_apply(modifier=inset.name)
    add_underlayers(points, material)
    for obj in bpy.context.scene.objects:
        obj.select_set(True)
    bpy.ops.object.join()

def export():
    for key, regroup in (("depth", False), ("spacing", True)):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        make_hair(regroup)
        asset = f"./assets/{key}.glb"
        bpy.ops.export_scene.gltf(filepath=str(REV / asset), export_format="GLB",
                                  export_apply=True, export_materials="EXPORT")
        manifest = {"Feminine": {"side-sweep": {
            "label": "Soft brow fringe", "note": "Bare-head review",
            "fits": {"none": {"default": asset, "ombre": asset}},
        }}}
        (REV / f"{key}.json").write_text(json.dumps(manifest, indent=2) + "\n",
                                        encoding="utf8", newline="\n")


if __name__ == "__main__":
    export()
