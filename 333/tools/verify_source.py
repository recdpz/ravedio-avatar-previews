"""Verify the rebuilt Bob source and export its ordinary hair GLB."""
from pathlib import Path
import json
import sys

import bpy
import bmesh
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "332/tools"))
from study_bob import TO_BLENDER, CENTER
from drape import read_glb


def unchanged_geometry():
    return {obj.data.name: np.array([v.co[:] for v in obj.data.vertices])
            for obj in bpy.context.scene.objects
            if obj.type == "MESH" and obj.get("component269") != "hair"}


def main(base, output):
    bpy.ops.wm.open_mainfile(filepath=str(base))
    original = unchanged_geometry()
    bpy.ops.wm.open_mainfile(filepath=str(output / "Ravedio333-curtain-bob.blend"))
    current = unchanged_geometry()
    assert original.keys() == current.keys()
    assert all(np.array_equal(points, current[name]) for name, points in original.items())
    report = {}
    bpy.ops.object.select_all(action="DESELECT")
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH" or obj.get("component269") != "hair":
            continue
        points = np.array([v.co[:] for v in obj.data.vertices]) @ TO_BLENDER.T
        assert np.isfinite(points).all()
        if "recessed coverage" not in obj.name:
            visible = points[:, 1] < 2.115 if "back layers" in obj.name else np.ones(len(points), dtype=bool)
            minimum = float(np.linalg.norm(points[visible] - CENTER, axis=1).min())
            assert minimum >= .3868, (obj.name, minimum)
            mesh = bmesh.new()
            mesh.from_mesh(obj.data)
            assert all(edge.is_manifold for edge in mesh.edges), ("Open edge", obj.name)
            mesh.free()
            assert "Lock flow" in obj.data.uv_layers
            report[obj.name] = {"vertices":len(points), "minimum_radius":minimum}
        obj.select_set(True)
    for image in bpy.data.images:
        if image.name.startswith("bob-"):
            assert image.packed_file is not None and tuple(image.size) == (512, 1024)
    path = output / "curtain-bob.glb"
    bpy.ops.export_scene.gltf(filepath=str(path), export_format="GLB", use_selection=True,
                             export_materials="EXPORT")
    doc, _ = read_glb(path)
    assert len([m for m in doc["materials"] if "normalTexture" in m]) == 3
    triangles = sum(doc["accessors"][primitive["indices"]]["count"] // 3
                    for mesh in doc["meshes"] for primitive in mesh["primitives"])
    (output / "source-review.json").write_text(json.dumps({
        "revision":333, "selected_reference":"332 / Tucked + Brushed",
        "objects":report, "triangles":triangles, "glb_bytes":path.stat().st_size,
        "materials":len(doc["materials"])
    }, indent=2)+"\n",encoding="utf8")
    print("Verified source geometry, closed outer surfaces, scalp clearance and textured GLB export.")


if __name__ == "__main__":
    main(*(Path(value) for value in sys.argv[sys.argv.index("--")+1:]))
