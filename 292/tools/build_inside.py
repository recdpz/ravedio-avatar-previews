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


def smooth_inside(obj):
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
    target = outer.copy()
    target[:, :2] -= radial * inset[:, None]
    angle = np.abs(np.arctan2(outer[:, 0], -outer[:, 1] - CENTER[2]))
    behind_fringe = ease((angle - .92) / .45)
    lower = ease((1.89 + .18 * behind_fringe - height) / .21)
    inside += lower[:, None] * (target - inside)
    mesh.vertices.foreach_set("co", coords.ravel())
    mesh.update()


def bare_head():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    make_cut()
    smooth_inside(bpy.context.collection.objects[0])
    asset = ASSETS / "long-none.glb"
    bpy.ops.export_scene.gltf(filepath=str(asset), export_format="GLB",
                              export_apply=True, export_materials="EXPORT")
    return asset


def build():
    catalogue = json.loads((PREVIOUS / "hair-fits.json").read_text(encoding="utf8"))
    for hat, pair in catalogue["Feminine"][STYLE]["fits"].items():
        base = bare_head() if hat == "none" else fit_mesh(hat, ASSETS, make=make_cut, finish=smooth_inside)
        colored = ombre(base, hat, ASSETS)
        pair.update(default=f"./assets/{base.name}", ombre=f"./assets/{colored.name}")
    (REV / "hair-fits.json").write_text(json.dumps(catalogue, indent=2) + "\n",
                                       encoding="utf8", newline="\n")


if __name__ == "__main__":
    build()
