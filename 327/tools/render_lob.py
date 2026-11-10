"""Compare the source Lob and its fitted headwear in the saved studio."""
from argparse import ArgumentParser
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "326"))
from render_catalogue import change_parts, select


ANGLES = {"front": 0, "threequarter": -30, "profile": -90, "rear": 180, "rearquarter": -145,
          "rightprofile": 90, "above": -30, "underneath": -30}


def load(path):
    return json.loads(path.read_bytes())


def main():
    parser = ArgumentParser(description=__doc__)
    for name in ("base", "revised", "studio", "tools"):
        parser.add_argument(name, type=Path)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args(sys.argv[sys.argv.index("--")+1:])
    sys.path.insert(0, str(args.tools))
    from render_chat_review_blender import recolor

    fixtures = load(args.studio / "fixtures.json")["fixtures"]
    packed = "r321-ponytail-jersey"
    palette = load(args.base / "palette.json")
    output = args.revised / "review"
    output.mkdir(exist_ok=True)
    preferences = bpy.context.preferences.addons["cycles"].preferences
    preferences.compute_device_type = "CUDA"
    preferences.get_devices()
    for adapter in preferences.devices:
        adapter.use = adapter.type == "CUDA"
    device = "GPU" if any(a.use for a in preferences.devices) else "CPU"
    bpy.context.preferences.filepaths.save_version = 0

    for directory in (args.base, args.revised):
        catalogue = load(directory / "catalogue.json")
        revision = catalogue["revision"]
        bare_angles = ("front", "threequarter", "profile", "rear") if args.quick else tuple(ANGLES)
        if args.quick:
            cases = [("none", "default", "jersey", bare_angles), ("pashmina", "default", "jersey", ("threequarter", "rearquarter"))]
        else:
            cases = [("none", "default", "jersey", bare_angles)]
            if revision == 327:
                cases += [(hat, "default", "open", ("threequarter", "rearquarter"))
                          for hat in ("cap","beanie","bucket","cowboy","ears","headband","pashmina")]
                cases += [("none","ombre","sweatshirt",("threequarter","rear")),
                          ("pashmina","ombre","sweatshirt",("threequarter","rearquarter"))]
        for hat, finish, top, angles in cases:
            row = select(catalogue, ("F","bob",hat,top,"pants","bean","none","none","clear","none",2,finish))
            bpy.ops.wm.open_mainfile(filepath=str(args.studio / f"scenes/{packed}.blend"))
            scene = bpy.context.scene
            previous = {role: item["sha256"] for role, item in fixtures[packed]["parts"].items()}
            target = {role: str(directory / catalogue["components"][digest]["file"]) for role, digest in row["parts"].items()}
            old = {role: target[role] if row["parts"].get(role)==digest else "packed" for role,digest in previous.items()}
            change_parts(scene, old, target)
            recolor(scene, palette, row["skin"])
            for obj in scene.objects:
                if obj.type == "MESH" and obj.get("component269") == "top":
                    obj.visible_glossy = False
            scene.render.use_compositing = False
            scene.render.film_transparent = True
            scene.render.resolution_x = scene.render.resolution_y = 480
            scene.render.resolution_percentage = 100
            scene.render.image_settings.file_format = "PNG"
            scene.render.image_settings.color_mode = "RGBA"
            scene.cycles.device = device
            scene.cycles.samples = 24
            for angle in angles:
                yaw = math.radians(ANGLES[angle])
                pitch = math.radians({"above":42,"underneath":-28}.get(angle,0))
                target = Vector((0, 0, 1.67 if hat=="cowboy" else 1.61))
                scene.camera.data.ortho_scale = 1.67 if hat=="cowboy" else 1.51
                scene.camera.location = target + 8 * Vector((math.sin(yaw)*math.cos(pitch),
                    -math.cos(yaw)*math.cos(pitch), math.sin(pitch)))
                scene.camera.rotation_euler = (target - scene.camera.location).to_track_quat("-Z", "Y").to_euler()
                if revision == 327 and hat=="none" and finish=="default" and angle=="threequarter" and not args.quick:
                    scene.render.filepath = "//review/lob.png"
                    bpy.ops.file.pack_all()
                    bpy.ops.wm.save_as_mainfile(filepath=str(args.revised / "Ravedio327-Lob.blend"))
                scene.render.filepath = str(output / f"{revision}-{hat}-{finish}-{angle}.png")
                bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
