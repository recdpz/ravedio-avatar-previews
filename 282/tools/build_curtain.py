"""Sculpt the selected curtain fringe into a continuous, layered hair surface."""
import json
import sys
from pathlib import Path

import bpy
import numpy as np

REV = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REV.parent / "275/tools"))
from build_hair import BANGS_COLOR, CENTER, RADIUS, ease, hair_material, shell, smooth_max

PART = -.105


def curtain_surface():
    azimuth, length = np.meshgrid(
        np.linspace(-np.pi, np.pi, 257, endpoint=False),
        np.linspace(0, 1, 120),
    )
    offset = azimuth - PART
    distance = np.sqrt(offset**2 + .028**2) - .028
    # Both sides turn away from the part, with a slightly longer heavy side.
    side = np.tanh(offset / .14)
    drop = .305 * ease((distance + .027 * side) / 1.10)
    frame = 2.114 - drop - .007 * side * ease(distance / .23)
    # The hem includes a short rounded fringe and a longer temple layer.
    tip = np.exp(-((distance - .417 + .028 * side) / .169)**2) * ease(distance / .18)
    frame -= (.071 + .019 * side) * tip
    frame += (.028 + .007 * side) * np.exp(-((distance - .614 + .025 * side) / .102)**2)
    drape = 1.365 + .018 * np.sin(azimuth * 3 + .9)
    drape += .011 * np.sin(azimuth * 8 + .5) + .006 * np.cos(azimuth * 13)
    side_blend = ease((np.abs(azimuth) - .72) / .97)
    hem = frame + side_blend * (drape - frame)
    y = 2.214 + length * (hem - 2.214)

    # The face frame lifts as it leaves the crown and rolls back in near the
    # tips. The falloff follows height, so the motion carries into the sides.
    front = 1 - ease((np.abs(azimuth) - .76) / .52)
    fall = ease((2.140 - y) / .284)
    lift = np.exp(-((y - 2.040) / .096)**2) * ease(distance / .28)
    inward = ease((1.980 - y) / .182) * ease(distance / .45)
    crown_sweep = .056 * np.sin(3 * azimuth + .55) * (1 - fall)
    theta = azimuth + crown_sweep + front * side * (.184 * fall - .128 * inward)

    # A narrow curved groove softens into the crown. Two broad ridges per
    # side carry the gloss from the part to the cheek layers.
    pole_falloff = ease((2.214 - y) / .115)
    groove_center = PART + .100 * ease((y - 2.114) / .094)
    part = np.exp(-((azimuth - groove_center) / .055)**2) * front
    travel = ease((2.171 - y) / .228)
    lock_center = .145 + (.384 - .032 * side) * travel
    lock_width = .113 + .044 * np.sin(np.pi * travel)
    lock = (distance - lock_center) / lock_width
    temple = (distance - lock_center - .206) / .185
    # The grooves follow the sweep into the temples and disappear into the
    # surrounding hair where the shorter face-framing layers end.
    layer = .018 * np.exp(-lock**2) + .010 * np.exp(-temple**2)
    layer -= .006 * np.exp(-((lock - 1.22) / .30)**2)
    layer *= front * ease(distance / .17)
    grain = .0017 * np.cos(31 * azimuth + 1.1 * fall + .65 * np.sin(3 * azimuth))
    grain += .0019 * np.cos(17 * azimuth - 1.5 * fall + .80 * np.cos(5 * azimuth))

    skin = np.sqrt(np.maximum(.000001, RADIUS**2 - (y - CENTER[1])**2))
    core = np.sqrt(np.maximum(.000001, .411**2 - (y - CENTER[1])**2))
    hang = ease((1.852 - y) / .320) * ease((np.abs(azimuth) - .51) / .70)
    skirt = .345 + .016 * np.sin(azimuth * 5 + y * 5.8)
    skirt += .010 * np.cos(azimuth * 9 + y * 4.8) - .012 * ease((1.53 - y) / .16)
    rho = core + hang * (skirt - core)
    rho = smooth_max(rho, skin + .007, .020)
    texture = pole_falloff * (layer + grain - .010 * part)
    side_radius = rho + texture - .010 * (1 - front) * ease((length - .89) / .11)
    # Use height rather than distance to the hem for the outward arc. This
    # keeps a smooth face-framing surface even where the outline changes.
    face_radius = skin + .010 + pole_falloff * (.018 * lift + layer + grain - .007 * part)
    face_radius += .016 * (1 - ease((2.177 - y) / .104))
    face_radius -= .005 * inward
    face_fit = front * ease((2.196 - y) / .085)
    rho = side_radius + face_fit * (face_radius - side_radius)
    # Keep the exposed lower temple edge clear of the spherical cheek.
    rho = smooth_max(rho, skin + .006, .014)
    points = np.stack((rho * np.sin(theta), y, CENTER[2] + rho * np.cos(theta)), axis=-1)
    return points


def export():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    points = curtain_surface()
    material = hair_material(False, BANGS_COLOR, .41)
    neutral = np.ones(points.shape[:2])
    shell("Hair / curtain bangs", points, neutral, neutral, material, False, BANGS_COLOR, loop=True)
    path = REV / "assets/curtain.glb"
    bpy.ops.export_scene.gltf(filepath=str(path), export_format="GLB", export_apply=True,
                              export_materials="EXPORT", export_image_format="AUTO")
    manifest = {"Feminine": {"side-sweep": {
        "label": "Curtain bangs", "note": "Bare-head review",
        "fits": {"none": {"default": "./assets/curtain.glb", "ombre": "./assets/curtain.glb"}},
    }}}
    (REV / "hair.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf8", newline="\n")


if __name__ == "__main__":
    export()
