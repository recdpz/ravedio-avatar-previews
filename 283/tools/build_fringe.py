"""Refine the 281 soft brow fringe in the shared avatar coordinates."""
import json
import sys
from pathlib import Path

import bpy
import numpy as np

REV = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REV.parent / "275/tools"))
from build_hair import BANGS_COLOR, CENTER, RADIUS, ease, hair_material, shell, smooth_max

GAPS = (
    (-.577, .040, .034),
    (-.416, .025, .019),
    (-.307, .052, .056),
    (-.102, .036, .043),
    (.050, .067, .062),
    (.223, .026, .031),
    (.363, .048, .046),
    (.530, .031, .023),
    (.619, .046, .037),
)


def fringe_surface():
    azimuth, length = np.meshgrid(
        np.linspace(-np.pi, np.pi, 384, endpoint=False),
        np.linspace(0, 1, 104),
    )
    # The edge keeps the original brow coverage and has uneven, open spaces.
    temple = ease((np.abs(azimuth) - .42) / .49)
    brow = 1.971 - .077 * temple
    brow += .008 * np.sin(3.3 * azimuth + .5) + .007 * np.cos(9 * azimuth + .7)
    brow -= .014 * np.exp(-((azimuth - .115) / .108)**2)
    for center, width, height in GAPS:
        spread = width * np.where(azimuth < center, 1.10, .90)
        brow += height * np.exp(-((azimuth - center) / spread)**2)

    back_hem = 1.365 + .019 * np.sin(3 * azimuth + .9)
    back_hem += .009 * np.sin(8 * azimuth + .5) + .005 * np.cos(13 * azimuth)
    transition = ease((np.abs(azimuth) - .79) / .91)
    hem = brow + transition * (back_hem - brow)
    crown = 2.214
    y = crown + length * (hem - crown)

    front = 1 - ease((np.abs(azimuth) - .76) / .52)
    fall = ease((crown - y) / .205)
    sweep = (.112 + .056 * np.cos(3.4 * azimuth + .75)) * fall
    sweep -= (.036 - .016 * np.sin(7 * azimuth + .2)) * ease((2.036 - y) / .096)
    theta = azimuth + front * sweep + .036 * np.sin(3 * azimuth + .6) * (1 - fall)

    # The fine grooves lead into the openings rather than cutting across them.
    # Only the ends are separated by the silhouette. Their roots share a surface.
    height_fade = ease((crown - y) / .149)
    channels = np.zeros_like(y)
    for center, width, _ in GAPS:
        channels += np.exp(-((azimuth - center) / (width * .70))**2)
    fine_grain = .0017 * np.cos(33 * azimuth + 1.3 * fall + .80 * np.sin(4 * azimuth))
    fine_grain += .0018 * np.cos(16 * azimuth - 1.7 * fall + .56 * np.sin(3 * azimuth))
    # A softer secondary ridge carries the fringe into the longer temple hair.
    frame_center = .70 + .13 * ease((2.05 - y) / .23)
    frame = .0055 * np.exp(-((np.abs(azimuth) - frame_center) / .16)**2)
    texture = height_fade * (fine_grain + frame - .0022 * front * channels)

    dy = y - CENTER[1]
    skin = np.sqrt(np.maximum(.000001, RADIUS**2 - dy**2))
    cap = np.sqrt(np.maximum(.000001, .411**2 - dy**2))
    hang = ease((1.848 - y) / .316) * ease((np.abs(azimuth) - .58) / .69)
    side_fall = .345 + .016 * np.sin(5 * azimuth + 5.8 * y)
    side_fall += .011 * np.cos(9 * azimuth + 4.8 * y) - .011 * ease((1.55 - y) / .19)
    rho = cap + hang * (side_fall - cap)
    rho -= .008 * (1 - front) * ease((length - .90) / .10)

    # The fringe arches gently away from the forehead before the ends settle.
    # Use height to keep the cross-section smooth across the different lengths.
    arc_peak = 2.041 + .010 * np.sin(4 * azimuth + .28)
    brow_arc = (.015 - .004 * channels) * np.exp(-((y - arc_peak) / .079)**2)
    root_lift = .019 * (1 - ease((2.177 - y) / .119))
    face_radius = skin + .008 + brow_arc + root_lift
    face_fit = front * ease((2.203 - y) / .113)
    rho += face_fit * (face_radius - rho) + texture
    rho = smooth_max(rho, skin + .006, .012)

    return np.stack((rho * np.sin(theta), y, CENTER[2] + rho * np.cos(theta)), axis=-1)


def export():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    points = fringe_surface()
    material = hair_material(False, BANGS_COLOR, .405)
    neutral = np.ones(points.shape[:2])
    shell("Hair / soft brow fringe", points, neutral, neutral, material, False, BANGS_COLOR, loop=True)
    bpy.ops.export_scene.gltf(filepath=str(REV / "assets/air.glb"), export_format="GLB",
                              export_apply=True, export_materials="EXPORT")
    manifest = {"Feminine": {"side-sweep": {
        "label": "Soft brow fringe", "note": "Bare-head review",
        "fits": {"none": {"default": "./assets/air.glb", "ombre": "./assets/air.glb"}},
    }}}
    (REV / "hair.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf8", newline="\n")


if __name__ == "__main__":
    export()
