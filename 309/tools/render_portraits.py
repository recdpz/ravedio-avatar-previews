"""Render candidate GLBs with the approved chat portrait rig."""
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector

REV = Path(__file__).resolve().parents[1]
source, tools, out = map(Path, sys.argv[sys.argv.index("--")+1:])
sys.path.insert(0, str(tools))
from chat_portrait_blender import APPROVED_YAW, reduce_clear_lens_glare, set_camera, set_lighting
from render_chat_review_blender import recolor

ART = json.loads((REV/"art.json").read_text())
FIXTURES = json.loads((source/"manifest.json").read_text())["fixtures"]
PALETTE = json.loads((source/"palette.json").read_text())
CASES = [
    ("r308-twin-jersey-pashmina", "Feminine", "original", 3),
    ("r308-curls-pashmina", "Feminine", "hooded", 3),
    ("r308-flow-cap", "Masculine", "bean", 3),
    ("r308-ponytail-beanie-jersey", "Feminine", "original", 2),
]


def replace(scene, role, path):
    for obj in list(scene.objects):
        if obj.type == "MESH" and obj.get("component269") == role:
            bpy.data.objects.remove(obj,do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str((REV/path).resolve()))
    for obj in bpy.context.selected_objects:
        if obj.type == "MESH":
            obj["component269"] = role


def soft_fill(scene):
    scene.objects["Chat lower fill"].data.energy = 50
    light = bpy.data.lights.new("Extra diffuse fill comparison", "AREA")
    light.energy, light.shape, light.size = 65, "DISK", 4.8
    light.color = (1, .985, .97)
    light.specular_factor = 0
    obj = bpy.data.objects.new(light.name, light)
    scene.collection.objects.link(obj)
    obj.location = (1.8, -3.8, 2.18)
    obj.rotation_euler = (Vector((0, 0, 1.79))-obj.location).to_track_quat("-Z", "Y").to_euler()


def lenses(scene):
    return {m for obj in scene.objects if obj.type == "MESH" and obj.get("component269") == "lenses"
            for m in obj.data.materials}


def render(scene, filename):
    scene.render.filepath = str(out/filename)
    bpy.ops.render.render(write_still=True)


def main():
    out.mkdir(parents=True, exist_ok=True)
    for fixture, build, eyes, skin in CASES:
        bpy.ops.wm.open_mainfile(filepath=str(source/FIXTURES[fixture]["scene"]))
        scene = bpy.context.scene
        replace(scene,"eyes",ART["eyes"][build][eyes])
        replace(scene,"mouth",ART["mouth"][build])
        if fixture == "r308-ponytail-beanie-jersey":
            fit = ART["beanie"][build]["ponytail"]
            replace(scene,"headgear",fit["headgear"])
            replace(scene,"hairLengths",fit["tail"]["ombre"])
        scene.render.use_compositing = False
        scene.render.film_transparent = True
        scene.render.image_settings.file_format = "PNG"
        scene.render.image_settings.color_mode = "RGBA"
        scene.render.image_settings.color_depth = "8"
        scene.render.resolution_x = scene.render.resolution_y = 384
        scene.render.resolution_percentage = 100
        scene.cycles.samples = 32
        scene.cycles.use_denoising = True
        preferences = bpy.context.preferences.addons["cycles"].preferences
        preferences.compute_device_type = "CUDA"
        preferences.get_devices()
        for device in preferences.devices:
            device.use = device.type == "CUDA"
        scene.cycles.device = "GPU" if any(d.use for d in preferences.devices) else "CPU"
        set_lighting(scene)
        set_camera(scene,APPROVED_YAW)
        for obj in scene.objects:
            if obj.type == "MESH" and obj.get("component269") == "top":
                obj.visible_glossy = False
        if scene.objects.get("Studio floor"):
            scene.objects["Studio floor"].hide_render = True
        if fixture == "r308-curls-pashmina":
            reduce_clear_lens_glare(lenses(scene))
        elif fixture == "r308-flow-cap":
            for material in lenses(scene):
                shader = next(node for node in material.node_tree.nodes if node.type == "BSDF_PRINCIPLED")
                assert not shader.inputs["Alpha"].is_linked
                shader.inputs["Alpha"].default_value = ART["darkLensOpacity"]
        recolor(scene,PALETTE,skin)
        render(scene,f"{fixture}-skin{skin}-309.png")
        soft_fill(scene)
        render(scene,f"{fixture}-skin{skin}-fill.png")


if __name__ == "__main__":
    main()
