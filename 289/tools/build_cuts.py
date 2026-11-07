"""Compare a rounded blowout and a longer layered cut on the 281 fringe base."""
import json
import sys
from pathlib import Path

import bpy
import numpy as np

REV = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REV.parent / "287/tools"))
from build_fringe import BANGS_COLOR, CENTER, ease, hair_material, longer_lob, shell
from build_hair import RADIUS, smooth_max
from build_studies import air_radius


def angles_of(points):
    return np.arctan2(points[..., 0], points[..., 2] - CENTER[2])


def even_fringe(points, angle, count, separation, height):
    """Model closely spaced, rounded pieces across both brows."""
    # Use the original meridians for the cut so all the tips and channels
    # stay aligned as the strands sweep slightly across the forehead.
    y = points[:, :, 1].copy()
    end = y[-1]
    reach = 1 - ease((np.abs(angle) - .665) / .208)
    extent = np.sin(.675)
    spacing = 2 * extent / count
    centers = np.arcsin(np.linspace(-extent, extent, count + 1)[1:-1])
    line = height + .003 * np.sin(3.2 * angle + .44)
    line -= .019 * ease((np.abs(angle) - .47) / .34)
    # Repeated soft, narrow openings keep the tips visible individually.
    # Taper them a little near the temples as the fringe meets longer hair.
    for center in centers:
        width = spacing * (.316 + .013 * np.cos(center * 11)) / np.cos(center)
        line += separation * (1 - .20 * np.abs(center)) * np.exp(-((angle - center) / width)**2)
    weight = ease((2.145 - y) / np.maximum(.060, 2.145 - end))
    adjusted = y + reach * weight * (line - end)
    a = angles_of(points)
    r = np.hypot(points[:, :, 0], points[:, :, 2] - CENTER[2])
    section = 2 * np.pi * (np.sin(angle) + extent) / spacing
    detail = .0035 * np.sin(section / 2)**2
    detail = detail * (1 - .40 * ease((2.023 - adjusted) / .087))
    r += air_radius(adjusted) - air_radius(y) + reach * weight * detail
    skin = np.sqrt(np.maximum(.000001, RADIUS**2 - (adjusted - CENTER[1])**2))
    rim = reach * (1 - ease((adjusted - adjusted[-1]) / .088))
    rim *= 1 - ease((adjusted - 2.040) / .09)
    r += .80 * rim * (skin + .008 + .33 * detail - r)
    changed = reach > 0
    points[:, changed, 0] = (r * np.sin(a))[:, changed]
    points[:, changed, 1] = adjusted[:, changed]
    points[:, changed, 2] = (CENTER[2] + r * np.cos(a))[:, changed]


def lower_cut(points, layered):
    y = points[:, :, 1].copy()
    a = angles_of(points)
    edge = y[-1]
    side = ease((np.abs(a) - .88) / .55)
    hem_angle = a[-1]
    shoulder = np.exp(-((np.abs(hem_angle) - 1.55) / .35)**2)
    lower_length = ease((1.81 - y) / np.maximum(.12, 1.81 - edge))
    rear = ease((np.abs(a) - 1.54) / .60)
    if layered:
        # The short face layers finish above the shoulders. Longer panels
        # sit behind the arms, with a softly scalloped U shape at the back.
        hem = 1.228 + .075 * shoulder + .019 * (1 - ease((np.abs(hem_angle) - 1.62) / .85))
        for center, width, drop in ((-2.72, .31, .053), (-2.13, .29, .032),
                                    (2.40, .33, .039), (2.94, .25, .053)):
            distance = (hem_angle - center + np.pi) % (2 * np.pi) - np.pi
            hem -= drop * np.exp(-(distance / width)**2)
        hem += .007 * np.cos(5 * hem_angle + .62)
    else:
        hem = 1.285 + .063 * shoulder - .019 * ease((np.abs(hem_angle) - 2.02) / .90)
        hem += .013 * np.cos(6 * hem_angle + .48) + .005 * np.sin(9 * hem_angle + .7)
    y += side * lower_length * (hem - edge)

    r = np.hypot(points[:, :, 0], points[:, :, 2] - CENTER[2])
    flow = ease((1.91 - y) / .55)
    fall = side * ease((1.92 - y) / .34)
    if layered:
        # Sculpt broad waves with a shifting phase. The grooves follow the
        # bend and resolve into layered lengths, so the ends are not one plane.
        ribbon = a + .100 * np.sin(2.3 + 3 * a - 5 * flow) * flow
        lane = 6 * ribbon + .40 * np.sin(3 * a + .48)
        wave = .022 * np.cos(lane) + .006 * np.sin(2 * lane + .6)
        weight = .40 + .60 * rear
        r += fall * (weight * wave + .023 * rear * lower_length)
        r += fall * (.006 * np.sin(7 * (y - 1.19) + 3 * a + .3))
        r += .0030 * fall * np.cos(29 * ribbon + .70 * np.sin(5 * a))
        r -= .009 * rear * fall * ease((lower_length - .77) / .23)
        theta = a + .047 * fall * np.sin(4 * a + 6 * flow + .4)
        # Fit the side layers into the gap between the torso and sleeve.
        across = np.abs(theta)
        clearance = ease((across - 1.11) / .22) * (1 - ease((across - 1.87) / .29))
        clearance *= ease((1.49 - y) / .161)
        channel = .321 / np.maximum(.60, np.abs(np.sin(theta)))
        r += clearance * (channel - r)
        volume = fall * (.55 + .45 * np.cos(lane))
    else:
        # A blowout rounds over the shoulder before the ends curl inward.
        # The larger turn lives above the hem and rolls out of the profile.
        phase = lower_length + .18 * np.sin(3 * a + .48) * np.sin(np.pi * lower_length)
        curve = np.sin(np.pi * phase)**1.3
        turn = lower_length**2
        route = a + .093 * np.sin(3 * a + 3.5 * flow) * flow
        lane = 7 * route + .4 * np.sin(3 * a + .8)
        r += fall * ((.027 + .008 * rear) * curve - (.016 + .006 * rear) * turn)
        r += fall * (.012 * np.cos(lane) + .0045 * np.cos(2 * lane - .7))
        r += .0023 * fall * np.cos(28 * route - .6 * np.cos(4 * a))
        theta = a + .038 * fall * np.sin(3 * a + 4 * flow + .68)
        volume = fall * curve

    skin = np.sqrt(np.maximum(.000001, RADIUS**2 - (y - CENTER[1])**2))
    r = smooth_max(r, skin + .007, .011)
    changes = side > 0
    points[:, :, 0][changes] = (r * np.sin(theta))[changes]
    points[:, :, 1][changes] = y[changes]
    points[:, :, 2][changes] = (CENTER[2] + r * np.cos(theta))[changes]
    return volume, lower_length


def refine_fringe_sampling(points, progress, shade):
    angle = np.linspace(-np.pi, np.pi, points.shape[1], endpoint=False)
    intervals = np.diff(angle)
    front = np.abs(angle[:-1] + intervals / 2) < .91
    refined = np.sort(np.concatenate((
        angle, (angle[:-1] + intervals / 3)[front],
        (angle[:-1] + 2 * intervals / 3)[front],
    )))
    def resample(values):
        return np.stack([np.interp(refined, angle, row, period=2 * np.pi) for row in values])
    points = np.stack([resample(points[:, :, dim]) for dim in range(3)], axis=-1)
    return points, resample(progress), resample(shade), refined

def make_hair(layered):
    points, progress, shade = longer_lob()
    points, progress, shade, angle = refine_fringe_sampling(points, progress, shade)
    volume, fall = lower_cut(points, layered)
    even_fringe(points, angle, 13 if layered else 11, .038 if layered else .031,
                1.956 if layered else 1.971)
    name = "Hair / layered fringe" if layered else "Hair / rounded fringe"
    material = hair_material(False, BANGS_COLOR, .38)
    shell(name, points, progress, shade, material, False, BANGS_COLOR, loop=True)
    obj = bpy.data.objects[name]
    inset = obj.modifiers["Inset edge thickness"]
    group = obj.vertex_groups.new(name="Ends")
    thickness = .010 + .012 * volume - .005 * fall**6
    fringe = (1 - ease((np.abs(angle) - .68) / .19))
    edge = 1 - ease((points[:, :, 1] - points[-1, :, 1]) / .065)
    thickness -= .003 * fringe * edge
    inset.thickness = .022
    inset.thickness_vertex_group = .004 / .022
    for index, value in enumerate(((thickness - .004) / .018).ravel()):
        group.add([index], float(np.clip(value, 0, 1)), "REPLACE")
    inset.vertex_group = group.name


def export():
    for key, layered in (("rounded", False), ("layered", True)):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        make_hair(layered)
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
