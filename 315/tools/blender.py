"""Build editable source assemblies from the revised GLBs and the 315 light rig."""
import argparse
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT.parent/"314/tools/handoff"),str(ROOT/"tools")]
from render import change_parts, sha
from export import linear

CASES = ("curls-pashmina","flow-cap","twin-jersey-bare")


def json_file(path):
    return json.loads(path.read_bytes())


def configure(scene, studio, set_lighting):
    # This adds the named lower fill to the packed baseline rig. Each light is
    # then set explicitly from the catalogue's studio recipe.
    set_lighting(scene)
    for name,(location,energy,color,width,height,specular) in studio["lights"].items():
        light = scene.objects[name]
        light.location = location
        light.rotation_euler = (Vector(studio["aim"])-light.location).to_track_quat("-Z","Y").to_euler()
        light.data.energy = energy
        light.data.color = color
        light.data.shape = "RECTANGLE" if height else "DISK"
        light.data.size = width
        if height:
            light.data.size_y = height
        light.data.specular_factor = specular
    world = next(n for n in scene.world.node_tree.nodes if n.type=="BACKGROUND")
    world.inputs["Color"].default_value = (*studio["world"]["linear_rgb"],1)
    world.inputs["Strength"].default_value = studio["world"]["strength"]
    scene.render.use_compositing = False
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.resolution_x = scene.render.resolution_y = 512
    scene.render.resolution_percentage = 100
    scene.cycles.samples = 32
    scene.cycles.seed = 42
    scene.cycles.use_denoising = True
    if floor := scene.objects.get("Studio floor"):
        floor.hide_render = True
    for obj in scene.objects:
        if obj.type=="MESH" and obj.get("component269")=="top":
            obj.visible_glossy = False


def frame_color(scene, key, colors):
    rgb = linear(colors[key])
    for obj in scene.objects:
        if obj.type != "MESH" or obj.get("component269") != "glasses":
            continue
        for material in obj.data.materials:
            shader = next(n for n in material.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
            shader.inputs["Base Color"].default_value = (*rgb,1)
            shader.inputs["Metallic"].default_value = .72 if key in ("silver","gold") else .08


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("baseline","old_selection","mobile_tools","assets","output"):
        parser.add_argument(name,type=Path)
    a = parser.parse_args(sys.argv[sys.argv.index("--")+1:])
    sys.path.insert(0,str(a.mobile_tools))
    from chat_portrait_blender import set_camera, set_lighting
    from render_chat_review_blender import SOURCE_MANIFEST, recolor

    assert bpy.app.version[:3] == (5,2,0)
    assert sha(a.baseline/"manifest.json")==SOURCE_MANIFEST
    a.output.mkdir(parents=True,exist_ok=True)
    bpy.context.preferences.filepaths.save_version = 0
    source = json_file(a.baseline/"manifest.json")
    palette = json_file(a.baseline/"palette.json")
    old = json_file(a.old_selection)["cases"]
    catalogue = json_file(ROOT/"catalogue-input.json")
    new = catalogue["cases"]
    frame_colors = {key:rgb for key,_,rgb in catalogue["options"]["colors"]["frames"]}
    mapping = json_file(ROOT/"asset-map.json")["components"]
    studio = json_file(ROOT/"studio.json")["blender"]
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "CUDA"
    prefs.get_devices()
    for adapter in prefs.devices:
        adapter.use = adapter.type=="CUDA"
    device = "GPU" if any(a.use for a in prefs.devices) else "CPU"
    result = {}
    for key in CASES:
        case = new[key]
        fixture = case["baseline_scene"]
        original = source["fixtures"][fixture]["scene"]
        packed = a.baseline/original
        assert sha(packed)==source["files"][original]
        bpy.ops.wm.open_mainfile(filepath=str(packed))
        parts = {}
        for role, relative in case["parts"].items():
            if relative is None:
                continue
            candidate = mapping[relative]
            if role == "lenses":
                candidate = candidate[case["features"]["lensTint"]]
            file = a.assets/(candidate+".glb")
            assert sha(file)==candidate
            parts[role] = str(file.resolve())
        scene = bpy.context.scene
        change_parts(scene,{k:v for k,v in old[fixture[5:]]["parts"].items() if v},parts)
        if "glasses" in parts:
            frame_color(scene,case["features"]["frameColor"],frame_colors)
        configure(scene,studio,set_lighting)
        scene.cycles.device = device
        for skin in (0,3):
            recolor(scene,palette,skin)
            for name,yaw in (("chat",15),("profile",27),("side",90),("rear",150)):
                if skin==0 and name!="chat":
                    continue
                set_camera(scene,yaw)
                if name!="chat":
                    scene.camera.data.ortho_scale=1.856
                    scene.camera.location.z=1.618
                image = a.output/f"{key}-skin{skin}-{name}.png"
                scene.render.filepath=str(image)
                bpy.ops.render.render(write_still=True)
        set_camera(scene,27)
        scene.camera.data.ortho_scale=1.856
        scene.camera.location.z=1.618
        scene.render.filepath="//"+key+"-preview.png"
        # Prune orphan data from the 308 scene before packing the selected art.
        bpy.data.orphans_purge(do_recursive=True)
        bpy.ops.file.pack_all()
        images = [im for im in bpy.data.images if im.source=="FILE" and im.users]
        assert all(im.packed_file is not None and im.packed_file.size>0 for im in images)
        blend = a.output/(key+".blend")
        bpy.ops.wm.save_as_mainfile(filepath=str(blend),copy=True)
        result[key] = {"packed_scene_sha256":sha(blend),"parts":{k:Path(v).stem for k,v in parts.items()},
                       "packed_texture_images":len(images)}
    (a.output/"receipt.json").write_text(json.dumps({"art_revision":315,"cases":result},indent=2)+"\n",newline="\n")


if __name__ == "__main__":
    main()
