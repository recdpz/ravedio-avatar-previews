"""Verify packed maps, preserved non-hair objects and ordinary GLB material export."""
from pathlib import Path
import json
import sys
import tempfile

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "331/tools"))
from bob_directions import TO_BLENDER
from drape import CENTER, read_glb

def positions(hair):
    return {obj.data.name: np.array([v.co[:] for v in obj.data.vertices]) @ TO_BLENDER.T
            for obj in bpy.context.scene.objects
            if obj.type == "MESH" and (obj.get("component269") == "hair") == hair}

def main(base, output):
    bpy.ops.wm.open_mainfile(filepath=str(base))
    original_hair, original_other = positions(True), positions(False)
    report = {}
    for shape in ("tucked", "volume", "side-tuck"):
        bpy.ops.wm.open_mainfile(filepath=str(output / f"Ravedio332-{shape}.blend"))
        for name, points in positions(False).items():
            assert np.array_equal(original_other[name], points), ("Non-hair geometry changed", shape, name)
        distances = {}
        for name, points in positions(True).items():
            assert np.isfinite(points).all()
            original = original_hair[name]
            visible = np.linalg.norm(original - CENTER, axis=1) >= .3845
            minimum = float(np.linalg.norm(points[visible] - CENTER, axis=1).min())
            distances[name] = minimum
            assert minimum >= .3835, ("Hair intersects scalp", shape, name, minimum)
        for image in bpy.data.images:
            if image.name.startswith("bob-"):
                assert image.packed_file is not None and tuple(image.size) == (512, 1024)
        bpy.ops.object.select_all(action="DESELECT")
        for obj in bpy.context.scene.objects:
            if obj.type == "MESH" and obj.get("component269") == "hair":
                obj.select_set(True)
        with tempfile.TemporaryDirectory(prefix="ravedio332-") as temporary:
            path = Path(temporary) / "hair.glb"
            bpy.ops.export_scene.gltf(filepath=str(path), export_format="GLB", use_selection=True,
                                     export_materials="EXPORT")
            doc, _ = read_glb(path)
            maps = [m for m in doc["materials"] if "normalTexture" in m]
            assert len(maps) == 3, (shape, "Missing normal maps", len(maps))
            assert all("metallicRoughnessTexture" in m["pbrMetallicRoughness"] for m in maps)
            report[shape] = {"normal_mapped_materials":len(maps), "glb_bytes":path.stat().st_size,
                             "scalp_clearance":distances}
    (output / "source-review.json").write_text(json.dumps(report, indent=2)+"\n",encoding="utf8")
    print("Verified all three packed source scenes and normal/roughness GLB exports.")

if __name__ == "__main__":
    main(*(Path(p) for p in sys.argv[sys.argv.index("--") + 1:]))
