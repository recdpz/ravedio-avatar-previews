"""Sculpt soft, full-width bangs in the shared avatar coordinates."""
import json
import sys
from pathlib import Path

import bpy
import numpy as np

REV = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REV.parent / "275/tools"))
from build_hair import BANGS_COLOR, CENTER, RADIUS, ease, hair_material, shell, smooth_max

# Angular placement, width and length of each feathered end.
ENDS = (
    (-.591, .103, .022),
    (-.418, .069, .009),
    (-.266, .087, .020),
    (-.110, .078, .010),
    (.054, .079, .018),
    (.197, .065, .013),
    (.350, .086, .020),
    (.496, .065, .011),
    (.621, .093, .020),
)


def fringe_surface():
    azimuth, length = np.meshgrid(
        np.linspace(-np.pi, np.pi, 384, endpoint=False),
        np.linspace(0, 1, 104),
    )
    # Keep the cut across both brows. Shallow tips feather the lower edge
    # without cutting deep openings into the fringe.
    brow = 1.976 + .005 * np.sin(5 * azimuth + .62)
    brow -= .028 * ease((np.abs(azimuth) - .30) / .52)
    brow -= .067 * ease((np.abs(azimuth + .014) - .58) / .45)
    for center, width, drop in ENDS:
        spread = width * np.where(azimuth < center, .88, 1.12)
        brow -= drop * np.exp(-((azimuth - center) / spread)**2)
    # Slight separations sit between the groups of tips.
    for center, width, lift in ((-.346, .044, .014), (-.034, .058, .019), (.426, .042, .012)):
        spread = width * np.where(azimuth < center, .91, 1.09)
        brow += lift * np.exp(-((azimuth - center) / spread)**2)

    back_hem = 1.365 + .019 * np.sin(3 * azimuth + .9)
    back_hem += .009 * np.sin(8 * azimuth + .5) + .005 * np.cos(13 * azimuth)
    transition = ease((np.abs(azimuth) - .79) / .91)
    hem = brow + transition * (back_hem - brow)
    crown = 2.214
    y = crown + length * (hem - crown)

    front = 1 - ease((np.abs(azimuth) - .76) / .52)
    fall = ease((crown - y) / .245)
    theta = azimuth + .030 * np.sin(3 * azimuth + .6) * (1 - fall)
    # The locks share their roots and bend subtly toward the temples as they
    # descend. The surface relief follows the ends of the cut.
    flow = .100 * np.sin(2.3 * azimuth + .30) + .027
    strand = azimuth + front * flow * (1 - fall)
    height_fade = ease((crown - y) / .157)
    grain = .0015 * np.cos(37 * strand + .84 * np.sin(4 * azimuth))
    grain += .0015 * np.cos(19 * strand + .58 * np.sin(3 * azimuth) - 1.1 * fall)
    volume = np.zeros_like(y)
    for center, width, drop in ENDS:
        layer_width = width + .044 * (1 - fall)
        volume += (.002 + .31 * drop) * np.exp(-((strand - center) / layer_width)**2)
    texture = height_fade * (grain + front * volume)
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
    arc_peak = 2.038 + .010 * np.sin(4 * azimuth + .38)
    brow_arc = (.015 + .003 * np.sin(2 * azimuth + .30)) * np.exp(-((y - arc_peak) / .076)**2)
    root_lift = .019 * (1 - ease((2.177 - y) / .119))
    face_radius = skin + .008 + brow_arc + root_lift - .007 * ease((2.015 - y) / .073)
    face_fit = front * ease((2.203 - y) / .113)
    rho += face_fit * (face_radius - rho) + texture
    # Roll the ends close to the forehead without crowding the lashes.
    rim = (1 - ease((np.abs(azimuth) - .64) / .46)) * np.exp(-((y - hem) / .098)**2)
    rim *= 1 - ease((y - 2.086) / .089)
    rho += .84 * rim * (skin + .008 + .34 * texture - rho)
    rho = smooth_max(rho, skin + .006, .012)

    return np.stack((rho * np.sin(theta), y, CENTER[2] + rho * np.cos(theta)), axis=-1)


def export():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    points = fringe_surface()
    material = hair_material(False, BANGS_COLOR, .43)
    neutral = np.ones(points.shape[:2])
    shell("Hair / soft bangs", points, neutral, neutral, material, False, BANGS_COLOR, loop=True)
    bpy.data.objects["Hair / soft bangs"].modifiers["Inset edge thickness"].thickness = .007
    bpy.ops.export_scene.gltf(filepath=str(REV / "assets/bangs.glb"), export_format="GLB",
                              export_apply=True, export_materials="EXPORT")
    manifest = {"Feminine": {"side-sweep": {
        "label": "Soft bangs", "note": "Bare-head review",
        "fits": {"none": {"default": "./assets/bangs.glb", "ombre": "./assets/bangs.glb"}},
    }}}
    (REV / "hair.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf8", newline="\n")


if __name__ == "__main__":
    export()
