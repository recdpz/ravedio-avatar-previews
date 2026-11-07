"""Sculpt a side-brushed brow fringe in the shared avatar coordinates."""
import json
import sys
from pathlib import Path

import bpy
import numpy as np

REV = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REV.parent / "275/tools"))
from build_hair import BANGS_COLOR, CENTER, RADIUS, ease, hair_material, shell, smooth_max

def fringe_surface():
    azimuth, length = np.meshgrid(
        np.linspace(-np.pi, np.pi, 384, endpoint=False),
        np.linspace(0, 1, 104),
    )
    # A single sloping fringe drops over one brow before sweeping into the
    # longer hair. A shallow separation marks the longer corner layer.
    brow = 2.061 - .098 * ease((azimuth + .58) / 1.22)
    brow -= .038 * np.exp(-((azimuth - .185) / .303)**2)
    brow += .015 * np.exp(-((azimuth - .447) / .124)**2)
    temple_drop = .165 * ease((-azimuth - .37) / .59)
    temple_drop += .098 * ease((azimuth - .63) / .37)
    brow -= temple_drop
    back_hem = 1.365 + .019 * np.sin(3 * azimuth + .9)
    back_hem += .009 * np.sin(8 * azimuth + .5) + .005 * np.cos(13 * azimuth)
    transition = ease((np.abs(azimuth) - .79) / .91)
    hem = brow + transition * (back_hem - brow)
    crown = 2.214
    y = crown + length * (hem - crown)

    front = 1 - ease((np.abs(azimuth) - .76) / .52)
    fall = ease((crown - y) / .257)
    theta = azimuth + .036 * np.sin(3 * azimuth + .6) * (1 - fall)
    # The flow follows the volume of the fringe. Keep the sampling grid on
    # its original meridians so the crown cannot fold over itself.
    sweep = .390 * ease((2.196 - y) / .237) - .042 * ease((1.991 - y) / .115)
    strand = azimuth - front * (sweep - .304)
    height_fade = ease((crown - y) / .142)
    grain = .0015 * np.cos(31 * strand + .74 * np.sin(4 * azimuth))
    grain += .0017 * np.cos(16 * strand + .58 * np.sin(3 * azimuth) - 1.3 * fall)
    # Broad convex layers catch separate highlights across the forehead.
    locks = np.zeros_like(y)
    for center, width, volume in ((-.39, .18, .006), (-.13, .16, .011),
                                  (.16, .22, .015), (.54, .15, .009)):
        locks += volume * np.exp(-((strand - center) / width)**2)
    divide = np.exp(-((strand - .371) / .084)**2)
    locks -= .0045 * divide * ease((2.120 - y) / .095)
    root = np.exp(-((azimuth + .37 + .08 * (1 - fall)) / .065)**2)
    locks -= .004 * root * (1 - ease((2.164 - y) / .12))
    texture = height_fade * (grain + front * locks)
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
    arc_peak = 2.048 - .030 * ease((azimuth + .43) / 1.15)
    brow_arc = (.017 + .003 * np.sin(2 * azimuth + .30)) * np.exp(-((y - arc_peak) / .064)**2)
    root_lift = .019 * (1 - ease((2.177 - y) / .119))
    face_radius = skin + .008 + brow_arc + root_lift - .007 * ease((2.015 - y) / .073)
    face_fit = front * ease((2.203 - y) / .113)
    rho += face_fit * (face_radius - rho) + texture
    # Draw the rim toward the forehead over a broad curve. The shorter side
    # reaches the rim higher up and needs the same close fit as the long side.
    rim = (1 - ease((np.abs(azimuth) - .64) / .46)) * np.exp(-((y - hem) / .098)**2)
    rim *= 1 - ease((y - 2.086) / .089)
    rho += .84 * rim * (skin + .008 + .34 * texture - rho)
    rho = smooth_max(rho, skin + .006, .012)

    return np.stack((rho * np.sin(theta), y, CENTER[2] + rho * np.cos(theta)), axis=-1)


def export():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    points = fringe_surface()
    material = hair_material(False, BANGS_COLOR, .42)
    neutral = np.ones(points.shape[:2])
    shell("Hair / side-brushed fringe", points, neutral, neutral, material, False, BANGS_COLOR, loop=True)
    bpy.ops.export_scene.gltf(filepath=str(REV / "assets/brushed.glb"), export_format="GLB",
                              export_apply=True, export_materials="EXPORT")
    manifest = {"Feminine": {"side-sweep": {
        "label": "Side-brushed fringe", "note": "Bare-head review",
        "fits": {"none": {"default": "./assets/brushed.glb", "ombre": "./assets/brushed.glb"}},
    }}}
    (REV / "hair.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf8", newline="\n")


if __name__ == "__main__":
    export()
