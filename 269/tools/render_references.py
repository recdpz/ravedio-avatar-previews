
"""Rebake matched reference color and depth using selected 269 geometry and the 264 studio."""
import bpy
import hashlib
import json
import math
from pathlib import Path

from mathutils import Vector

REV = Path(__file__).resolve().parents[1]
ROOT = REV.parent
FIXTURES = json.loads((REV / "fixtures.json").read_text(encoding="utf8"))
PALETTE = json.loads((ROOT / "264/palette.json").read_text(encoding="utf8"))
OUT = REV / "references"


def chosen_paths(build):
    c = FIXTURES["builds"][build]
    style, hat, eyewear = ("straight", "pashmina", "reading") if build == "Feminine" else ("taper", "cap", "rectangular")
    paths = {
        "base": c["pantsBase"], "eyes": c["eyes"]["original"]["path"],
        "mouth": c["mouths"]["line"]["path"], "top": c["tops"]["sweatshirt"]["path"],
        "bottom": c["bottoms"]["pants"]["path"],
        **c["fits"][style][hat],
        **{k: v for k, v in c["glasses"][eyewear].items() if k != "label"},
    }
    if hat == "pashmina":
        paths["headgear"] = c["pashmina"][style]["sweatshirt"]
    if build == "Feminine":
        paths["lashes"] = c["lashes"]["original"]
    else:
        paths["groom"] = c["grooms"]["short"]["path"]
    return {role: (REV / FIXTURES["selected"].get(file, file)).resolve() for role, file in paths.items()}


def load_studio(build, paths):
    studio = ROOT / "264/sources" / f"{build}-hoodie-pants-cap263.blend"
    bpy.ops.wm.open_mainfile(filepath=str(studio))
    scene = bpy.context.scene
    for ob in list(scene.objects):
        if ob.type in {"MESH", "CURVE"} and ob.name != "Studio floor":
            bpy.data.objects.remove(ob, do_unlink=True)
    bpy.ops.outliner.orphans_purge(do_recursive=True)
    for role, path in paths.items():
        original = set(scene.objects)
        bpy.ops.import_scene.gltf(filepath=str(path))
        for ob in set(scene.objects) - original:
            ob["component269"] = role
    return scene, studio


def configure(scene):
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 24
    scene.cycles.seed = 42
    scene.cycles.use_denoising = True
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "CUDA"
        prefs.get_devices()
        for dev in prefs.devices:
            dev.use = dev.type == "CUDA"
        scene.cycles.device = "GPU" if any(d.type == "CUDA" for d in prefs.devices) else "CPU"
    except (KeyError, TypeError):
        scene.cycles.device = "CPU"
    scene.view_layers[0].use_pass_z = True
    scene.view_layers[0].pass_alpha_threshold = 0.5
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.use_compositing = True
    comp = bpy.data.node_groups.new("269 paired color and linear depth", "CompositorNodeTree")
    scene.compositing_node_group = comp
    comp.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    layers = comp.nodes.new("CompositorNodeRLayers")
    output = comp.nodes.new("NodeGroupOutput")
    comp.links.new(layers.outputs["Image"], output.inputs["Image"])
    depth = comp.nodes.new("CompositorNodeOutputFile")
    depth.file_output_items.clear()
    depth.file_output_items.new("FLOAT", "Depth")
    depth.format.file_format = "OPEN_EXR_MULTILAYER"
    depth.format.color_depth = "32"
    depth.save_as_render = False
    comp.links.new(layers.outputs["Depth"], depth.inputs["Depth"])
    return depth


def skin_tone(index):
    for material in bpy.data.materials:
        if not material.use_nodes:
            continue
        bsdf = next((n for n in material.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
        if bsdf is None:
            continue
        for prefix, key in [("Skin", "skin"), ("Face / ink209", "ink"), ("Face / lip209", "lip")]:
            if material.name.startswith(prefix):
                bsdf.inputs["Base Color"].default_value = (*PALETTE[key][index], 1)
                break


def camera(scene, angle, size):
    yaw = {"front": 0, "side": -math.pi / 2}[angle]
    target = Vector((0, 0, 1.90))
    scene.camera.data.type = "ORTHO"
    scene.camera.data.ortho_scale = 1.35
    scene.camera.location = target + Vector((8*math.sin(yaw), -8*math.cos(yaw), 0))
    scene.camera.rotation_euler = (target - scene.camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.resolution_x = scene.render.resolution_y = size
    scene.render.resolution_percentage = 100
    bpy.context.view_layer.update()
    return {
        "matrix_world": [list(row) for row in scene.camera.matrix_world],
        "ortho_scale": scene.camera.data.ortho_scale, "target": list(target),
        "clip_start": scene.camera.data.clip_start, "clip_end": scene.camera.data.clip_end,
    }


def hash_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(exist_ok=True)
    for build in ("Feminine", "Masculine"):
        paths = chosen_paths(build)
        scene, studio = load_studio(build, paths)
        depth = configure(scene)
        scene["fit269"] = "Spherical head, scale 0.8, height -8% of reference head height"
        skin_tone(1)
        camera(scene, "front", 512)
        depth.directory = "//"
        scene.render.filepath = "//color.png"
        bpy.ops.file.pack_all()
        bpy.ops.wm.save_as_mainfile(filepath=str(OUT / f"{build}-269.blend"), compress=True)
        depth.directory = str(OUT)
        components = {role: {"file": path.relative_to(ROOT).as_posix(), "sha256": hash_file(path)}
                      for role, path in paths.items()}
        settings = {k: getattr(scene.view_settings, k) for k in ("view_transform", "look", "exposure", "gamma")}
        pairs = []
        cases = [(skin, "front", size) for skin in (0, 3) for size in (120, 512)]
        cases.append((1, "side", 512))
        for skin, angle, size in cases:
            skin_tone(skin)
            cam = camera(scene, angle, size)
            name = f"{build}-{angle}-skin{skin}-{size}"
            depth.file_name = name + "-depth"
            color = OUT / (name + "-color.png")
            scene.render.filepath = str(color)
            bpy.ops.render.render(write_still=True)
            exr, = OUT.glob(name + "-depth*.exr")
            pairs.append({
                "color": color.name, "depth": exr.name, "camera": cam, "skin": skin,
                "size": size, "angle": angle, "alpha_threshold": 0.5,
                "color_sha256": hash_file(color), "depth_sha256": hash_file(exr),
            })
            print("PAIR269", name, flush=True)
        receipt = {
            "build": build, "components": components, "studio_sha256": hash_file(studio),
            "scene_sha256": hash_file(OUT / f"{build}-269.blend"),
            "color_management": settings, "cycles": {"samples": 24, "seed": 42, "denoise": True},
            "pairs": pairs,
        }
        (OUT / f"{build}-pairs.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf8")


if __name__ == "__main__":
    main()
