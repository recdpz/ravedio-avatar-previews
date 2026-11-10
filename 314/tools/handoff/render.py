"""Bake the 314 chat references from the approved 308 studio and resolved parts."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy

ROOT = Path(__file__).resolve().parents[3]
REFERENCE_SIZE = 384
SAMPLES = 32


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream,"sha256").hexdigest()


def load(path):
    return json.loads(path.read_bytes())


def change_parts(scene,source,target):
    for role in sorted(source.keys() | target.keys()):
        if source.get(role)==target.get(role):
            continue
        for obj in list(scene.objects):
            if obj.type=="MESH" and obj.get("component269")==role:
                bpy.data.objects.remove(obj,do_unlink=True)
        if role in target:
            before = set(scene.objects)
            bpy.ops.import_scene.gltf(filepath=str(ROOT/target[role]),import_shading="NORMALS")
            imported = [obj for obj in set(scene.objects)-before if obj.type=="MESH"]
            assert imported,(role,target[role])
            for obj in imported:
                obj["component269"] = role


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("fixtures","tools","before","after","out"):
        parser.add_argument(name,type=Path)
    args = parser.parse_args(sys.argv[sys.argv.index("--")+1:])
    sys.path.insert(0,str(args.tools))
    from chat_portrait_blender import (APPROVED_YAW, COOL_WHITE, SPAN, TARGET_Z,
        attach_depth_output, reduce_clear_lens_glare, set_camera, set_lighting)
    from render_chat_review_blender import SOURCE_MANIFEST, recolor
    assert bpy.app.version[:3]==(5,2,0) and sha(args.fixtures/"manifest.json")==SOURCE_MANIFEST
    manifests = {308:load(args.before),314:load(args.after)}
    fixture_manifest = load(args.fixtures/"manifest.json")
    palette = load(args.fixtures/"palette.json")
    art = load(ROOT/"314/art.json")
    args.out.mkdir(parents=True,exist_ok=True)
    preferences = bpy.context.preferences.addons["cycles"].preferences
    preferences.compute_device_type = "CUDA"
    preferences.get_devices()
    for adapter in preferences.devices:
        adapter.use = adapter.type=="CUDA"
    device = "GPU" if any(a.use for a in preferences.devices) else "CPU"

    records = {}
    for revision,resolved in manifests.items():
        for key,item in resolved["cases"].items():
            if revision==308 and item["native"]:
                continue  # The four matched controls are already in the approved pack.
            base = item["baseline_scene"]
            relative = fixture_manifest["fixtures"][base]["scene"]
            source = args.fixtures/relative
            assert sha(source)==fixture_manifest["files"][relative]
            bpy.ops.wm.open_mainfile(filepath=str(source))
            scene = bpy.context.scene
            change_parts(scene,manifests[308]["cases"][base[5:]]["parts"],item["parts"])
            lenses = {m for obj in scene.objects if obj.type=="MESH" and obj.get("component269")=="lenses"
                      for m in obj.data.materials}
            if lenses:
                if item["features"]["lensTint"]=="clear":
                    reduce_clear_lens_glare(lenses)
                elif revision==314:
                    for material in lenses:
                        shader = next(n for n in material.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
                        assert not shader.inputs["Alpha"].is_linked
                        shader.inputs["Alpha"].default_value = art["darkLensOpacity"]
            scene.render.film_transparent = True
            scene.render.image_settings.file_format = "PNG"
            scene.render.image_settings.color_mode = "RGBA"
            scene.render.image_settings.color_depth = "8"
            scene.render.resolution_x = scene.render.resolution_y = REFERENCE_SIZE
            scene.render.resolution_percentage = 100
            scene.cycles.device = device
            scene.cycles.samples = SAMPLES
            scene.cycles.use_denoising = True
            set_lighting(scene)
            set_camera(scene,APPROVED_YAW)
            for obj in scene.objects:
                if obj.type=="MESH" and obj.get("component269")=="top":
                    obj.visible_glossy = False
            if scene.objects.get("Studio floor"):
                scene.objects["Studio floor"].hide_render = True
            depth = attach_depth_output(scene,args.out,.5)
            for skin in range(4):
                recolor(scene,palette,skin)
                name = f"r{revision}-{key}-skin{skin}"
                png = args.out/(name+".png")
                depth.file_name = name+"-depth"
                scene.render.filepath = str(png)
                bpy.ops.render.render(write_still=True)
                exr, = args.out.glob(depth.file_name+"*.exr")
                records[name] = {"case":key,"revision":revision,"skin":skin,"color":png.name,"depth":exr.name,
                                 "color_sha256":sha(png),"depth_sha256":sha(exr)}
            print("Baked",revision,key,flush=True)
    (args.out/"renders.json").write_text(json.dumps({
        "scene_manifest_sha256":SOURCE_MANIFEST,"size":REFERENCE_SIZE,"samples":SAMPLES,
        "camera_span":SPAN,"target_y":TARGET_Z,"yaw_degrees":APPROVED_YAW,"plate_srgb":list(COOL_WHITE),
        "lower_fill_watts":32,"front_fill_multiplier":1.24,"top_glossy_visibility":False,
        "depth_alpha_threshold":.5,"pairs":records,
    },indent=2)+"\n",newline="\n")


if __name__=="__main__":
    main()
