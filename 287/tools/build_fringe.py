"""Lengthen and layer the original 281 Soft brow fringe."""
import json
import sys
from pathlib import Path

import bpy
import numpy as np

REV = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REV.parent / "281/tools"))
from build_studies import study_surface
from build_hair import BANGS_COLOR, CENTER, ease, hair_material, shell


def longer_lob():
    points, progress, shade = study_surface("air")
    y = points[:, :, 1].copy()
    a = np.arctan2(points[:, :, 0], points[:, :, 2] - CENTER[2])
    radius = np.hypot(points[:, :, 0], points[:, :, 2] - CENTER[2])
    side = ease((np.abs(a) - .85) / .49)
    fall = ease((1.83 - y) / .45)
    lower = side * fall

    # Keep the shorter face frame and let the longer panels fall behind it.
    # The hem is a shallow arc with subtle variation between the layers.
    edge = y[-1]
    hem_angle = a[-1]
    shoulder = np.exp(-((np.abs(hem_angle) - 1.58) / .36)**2)
    hem = 1.286 + .035 * shoulder - .018 * ease((np.abs(hem_angle) - 1.95) / 1.02)
    hem += .006 * np.cos(5 * hem_angle + .62) + .004 * np.sin(9 * hem_angle + .5)
    hem_weight = ease((np.abs(hem_angle) - .89) / .79)
    edge_drop = hem_weight * (hem - edge)
    y = y + edge_drop * ease((1.835 - y) / np.maximum(.12, 1.835 - edge))

    # The side and rear panels narrow gradually from the round head into a
    # falling shape. The shoulders guide the sides inward by a little more
    # than the back. This removes the pinch and flare from the old drape.
    rear = ease((np.abs(a) - 1.62) / .66)
    descent = ease((1.841 - y) / .54)
    profile = .412 - (.084 - .026 * rear) * descent
    profile += .005 * np.sin(3 * a + 1.3) * descent
    profile -= .011 * ease((1.387 - y) / .15)
    drape = side * ease((1.885 - y) / .29)
    radius += drape * (profile - radius)

    sweep = .039 * np.sin(3 * a + 3.5 * fall + .72)
    theta = a + lower * sweep
    # Wide, uneven layers break up the evenly spaced ridges on the old cap.
    # A smaller grain follows each bend. The fringe and its roots are masked.
    length = np.linspace(0, 1, points.shape[0])[:, None]
    original_grain = .0038 * np.cos(23 * a + 4 * length)**4
    original_grain += .0026 * np.cos(13 * a - 5 * length + .6)
    route = a - .082 * np.sin(2 * a + 2.8 * fall) * fall
    route += .040 * np.sin(4 * a - 4 * fall + .55) * fall
    layer = 8 * route + .44 * np.sin(3 * a + .53)
    relief = .0064 * np.cos(layer) + .0027 * np.cos(2 * layer + .8)
    relief += .0017 * np.cos(3 * layer - .75 + .44 * np.sin(3 * a + 2 * fall))
    fine = .00145 * np.cos(27 * route + .54 * np.sin(3 * a) + 1.1 * fall)
    fine += .0009 * np.cos(36 * route - .8 * np.sin(5 * a) + 1.4 * fall)
    depth = ease((2.191 - y) / .225) * side
    radius += depth * (relief + fine - .65 * original_grain * (1 - drape))

    # Use the original positions exactly at the front and around the part.
    changes = side > 0
    points[:, :, 0][changes] = (radius * np.sin(theta))[changes]
    points[:, :, 1][changes] = y[changes]
    points[:, :, 2][changes] = (CENTER[2] + radius * np.cos(theta))[changes]
    return points, progress, shade


def export():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    points, progress, shade = longer_lob()
    material = hair_material(False, BANGS_COLOR, .37)
    shell("Hair / soft brow fringe", points, progress, shade, material,
          False, BANGS_COLOR, loop=True)
    # Keep the original edge thickness at the fringe and taper only the ends.
    body = bpy.data.objects["Hair / soft brow fringe"]
    inset = body.modifiers["Inset edge thickness"]
    thickness = body.vertex_groups.new(name="Hem thickness")
    angles = np.arctan2(points[:, :, 0], points[:, :, 2] - CENTER[2])
    hem = ease((np.abs(angles) - .90) / .46) * ease((1.62 - points[:, :, 1]) / .27)
    for index, weight in enumerate(1 - hem.ravel()):
        thickness.add([index], float(weight), "REPLACE")
    inset.vertex_group = thickness.name
    inset.thickness_vertex_group = .50
    bpy.ops.export_scene.gltf(filepath=str(REV / "assets/fringe.glb"), export_format="GLB",
                              export_apply=True, export_materials="EXPORT")
    manifest = {"Feminine": {"side-sweep": {
        "label": "Soft brow fringe", "note": "Bare-head review",
        "fits": {"none": {"default": "./assets/fringe.glb", "ombre": "./assets/fringe.glb"}},
    }}}
    (REV / "hair.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf8", newline="\n")


if __name__ == "__main__":
    export()
