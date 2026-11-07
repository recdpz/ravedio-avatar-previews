"""Correct the folded inner surfaces of Long Bangs and rebuild its color pairs."""
from functools import partial
import json
import sys
from pathlib import Path

import bpy
import numpy as np

REV = Path(__file__).resolve().parents[1]
PREVIOUS = REV.parent / "291"
ASSETS = REV / "assets"
sys.path.insert(0, str(PREVIOUS / "tools"))
from build_fits import CENTER, STYLE, ease, fit_mesh, make_hair, ombre


make_cut = partial(make_hair, clear_edges=True)


def smooth_inside(obj, lower_thickness=None):
    # Apply the original thickness so the forehead edge and outer mesh retain
    # their coordinates. Replace the lower offset with an inward radial one.
    count = len(obj.data.vertices)
    thickness = np.array([.004 + .010 * obj.vertex_groups[0].weight(i) for i in range(count)])
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="Soft edges")
    mesh = obj.data
    assert len(mesh.vertices) == 2 * count
    coords = np.empty((2 * count, 3), dtype=np.float32)
    mesh.vertices.foreach_get("co", coords.ravel())
    outer, inside = coords[:count], coords[count:]
    height = outer[:, 2]
    # A constant-height inset preserves the gaps between adjacent locks.
    # At the tips the inward surface stays separated from the outside and
    # turns back along the edge without folding across neighboring locks.
    across = outer[:, :2] - (CENTER[0], -CENTER[2])
    radial = across / np.maximum(.001, np.linalg.norm(across, axis=1))[:, None]
    inset = np.clip(thickness * .74, .0034, .0080)
    if lower_thickness is not None:
        weight = ease((1.85 - height) / .17)
        inset += weight * (lower_thickness - inset)
    target = outer.copy()
    target[:, :2] -= radial * inset[:, None]
    angle = np.abs(np.arctan2(outer[:, 0], -outer[:, 1] - CENTER[2]))
    behind_fringe = ease((angle - .92) / .45)
    lower = ease((1.89 + .18 * behind_fringe - height) / .21)
    inside += lower[:, None] * (target - inside)
    mesh.vertices.foreach_set("co", coords.ravel())
    mesh.update()


def bare_head(assets, finish):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    make_cut()
    finish(bpy.context.collection.objects[0])
    asset = assets / "long-none.glb"
    bpy.ops.export_scene.gltf(filepath=str(asset), export_format="GLB",
                              export_apply=True, export_materials="EXPORT")
    return asset


def build(rev=REV, finish=smooth_inside):
    assets = rev / "assets"
    catalogue = json.loads((PREVIOUS / "hair-fits.json").read_text(encoding="utf8"))
    for hat, pair in catalogue["Feminine"][STYLE]["fits"].items():
        base = bare_head(assets, finish) if hat == "none" else fit_mesh(hat, assets, make=make_cut, finish=finish)
        colored = ombre(base, hat, assets)
        pair.update(default=f"./assets/{base.name}", ombre=f"./assets/{colored.name}")
    (rev / "hair-fits.json").write_text(json.dumps(catalogue, indent=2) + "\n",
                                       encoding="utf8", newline="\n")


if __name__ == "__main__":
    build()
