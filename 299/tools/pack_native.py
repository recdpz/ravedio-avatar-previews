"""Package the two native Development fixtures and their 20 degree reference."""
import json
import math
import struct
import sys
from pathlib import Path

import bpy
from mathutils import Vector

REV = Path(__file__).resolve().parents[1]
ROOT = REV.parent
sys.path.insert(0, str(ROOT / "295/tools"))
from pack_native import exr_depth, local_path, pack, sha, skin_tone

MOBILE = "d3066eec374cfa05fdba235adf66eca02332b5ed"


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf8", newline="\n")


def pair(scene, output, depth, yaw, span, height, size, tone, name):
    skin_tone(tone)
    target = Vector((0, 0, height))
    angle = math.radians(yaw)
    scene.camera.location = target + Vector((8 * math.sin(angle), -8 * math.cos(angle), 0))
    scene.camera.rotation_euler = (target - scene.camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera.data.ortho_scale = span
    scene.render.resolution_x = scene.render.resolution_y = size
    scene.render.resolution_percentage = 100
    bpy.context.view_layer.update()
    color = output / (name + "-color.png")
    depth.directory, depth.file_name = str(output), name + "-depth"
    scene.render.filepath = str(color)
    bpy.ops.render.render(write_still=True)
    z, = output.glob(name + "-depth*.exr")
    assert struct.unpack_from(">II", color.read_bytes(), 16) == (size, size)
    values = exr_depth(z, size)
    assert ((values > 0) & (values < 100)).sum() > size**2 * .12
    return {"yaw": yaw, "ortho_scale": span, "target": list(target), "size": size,
            "skin": tone, "color": color.name, "depth": z.name, "alpha_threshold": .5,
            "matrix_world": [list(row) for row in scene.camera.matrix_world]}


def add_refs(out, fixtures, previous):
    remap = {}
    looks = {}
    for build, entry in fixtures.items():
        old = previous[build]
        changed = {key: {"before": old["components"][key]["sha256"], "after": part["sha256"],
                         "file": part["file"], "source": part["source"]}
                   for key, part in entry["components"].items()
                   if old["components"][key]["sha256"] != part["sha256"]}
        assert changed.keys() == ({"hair", "headgear"} if build == "Feminine" else set())
        remap[old["id"]] = {"fixture": entry["id"], "changed": changed}
        bpy.ops.wm.open_mainfile(filepath=str(out / entry["scene"]))
        scene = bpy.context.scene
        scene.render.film_transparent = True
        floor = scene.objects.get("Studio floor")
        if floor:
            floor.visible_camera = False
        scene.cycles.samples = 64
        depth = next(n for n in scene.compositing_node_group.nodes if n.type == "OUTPUT_FILE")
        target = out / build / "portrait-20"
        target.mkdir()
        rows = [pair(scene, target, depth, -20, 1.10, 1.78, 512, skin, f"portrait-skin{skin}")
                for skin in range(4)]
        rows += [pair(scene, target, depth, -20, 1.10, 1.78, size, skin, f"chat-skin{skin}-{size}")
                 for skin in (0,3) for size in (40,64)]
        if build == "Feminine":
            scene.cycles.samples = 32
            rows.extend(pair(scene, target, depth, yaw, 1.50, 1.57, 512, 1, name)
                        for yaw, name in ((0, "front"), (-90, "left-side"), (90, "right-side"), (180, "rear")))
        for row in rows:
            for key in ("color", "depth"):
                row[key] = (target / row[key]).relative_to(out).as_posix()
        looks[entry["id"]] = rows
    write_json(out / "portrait-20.json", {"revision": 299, "display_background": "#ffffff",
               "lighting": "authored Cycles studio", "portrait_samples": 64,
               "fit_diagnostic_samples": 32, "fixtures": looks})
    write_json(out / "source-art.json", {"revision": 299, "control": 298,
               "mobile_base": MOBILE, "assemblies": remap})


if __name__ == "__main__":
    receipt, original, output = map(Path, sys.argv[-3:])
    old = json.loads(original.read_text(encoding="utf8"))["fixtures"]
    current = json.loads(receipt.read_text(encoding="utf8"))["fixtures"]
    for build, previous in old.items():
        row = current[build]
        assert row["features"] == previous["features"]
        assert row["parts"].keys() == previous["components"].keys()
        changed = {slot for slot, uri in row["parts"].items()
                   if sha(local_path(uri)) != previous["components"][slot]["sha256"]}
        assert changed == ({"hair", "headgear"} if build == "Feminine" else set()), changed
    pack(receipt, output, art_revision=299, stage_extra=lambda out, fixtures: add_refs(out, fixtures, old))
    archive = output.with_suffix(".zip")
    archive.with_suffix(".zip.sha256").write_text(f"{sha(archive)}  {archive.name}\n", encoding="ascii")
