"""Render the revised GLBs and matched 314 controls on an identical camera."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT.parent/"315/tools"),str(ROOT.parent/"314/tools/handoff")]

# Load the existing scene assembler under its own name. Its "render" import is
# resolved from 314/tools/handoff, keeping the 314 camera and importer rules.
spec = importlib.util.spec_from_file_location("aero_assembly",ROOT.parent/"315/tools/blender.py")
assembler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(assembler)
from export import linear


def configure_reference(scene, set_lighting):
    set_lighting(scene)
    scene.render.use_compositing = False
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.cycles.samples = 32
    scene.cycles.seed = 42
    scene.cycles.use_denoising = True
    if floor := scene.objects.get("Studio floor"):
        floor.hide_render = True
    for obj in scene.objects:
        if obj.type=="MESH" and obj.get("component269")=="top":
            obj.visible_glossy = False


def reference_lens(scene, tint, reduce_clear_lens_glare):
    lenses = {m for obj in scene.objects if obj.type=="MESH" and obj.get("component269")=="lenses"
              for m in obj.data.materials}
    if lenses and tint=="clear":
        reduce_clear_lens_glare(lenses)
    rgb = linear("#DCE9EB" if tint=="clear" else "#1C2029")
    for mat in lenses:
        n = next(n for n in mat.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
        n.inputs["Base Color"].default_value = (*rgb,1)
        n.inputs["Alpha"].default_value = .075 if tint=="clear" else .74


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("baseline","old_selection","mobile_tools","output"):
        p.add_argument(name,type=Path)
    p.add_argument("--pilot",action="store_true")
    a = p.parse_args(sys.argv[sys.argv.index("--")+1:])
    sys.path.insert(0,str(a.mobile_tools))
    from chat_portrait_blender import set_camera, set_lighting, reduce_clear_lens_glare
    from render_chat_review_blender import SOURCE_MANIFEST, recolor
    assert bpy.app.version[:3]==(5,2,0) and assembler.sha(a.baseline/"manifest.json")==SOURCE_MANIFEST
    bpy.context.preferences.filepaths.save_version = 0
    original = assembler.json_file(a.baseline/"manifest.json")
    palette = assembler.json_file(a.baseline/"palette.json")
    old = assembler.json_file(a.old_selection)["cases"]
    catalogue = assembler.json_file(ROOT.parent/"315/catalogue-input.json")
    frame_colors = {key:rgb for key,_,rgb in catalogue["options"]["colors"]["frames"]}
    source = assembler.json_file(a.output/"source-receipt.json")
    studio = assembler.json_file(ROOT/"studio.json")["blender"]
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "CUDA"
    prefs.get_devices()
    for adapter in prefs.devices:
        adapter.use = adapter.type=="CUDA"
    device = "GPU" if any(adapter.use for adapter in prefs.devices) else "CPU"
    target = a.output/("pilot" if a.pilot else "raw")
    target.mkdir(exist_ok=True)
    scenes = a.output/"blender"
    scenes.mkdir(exist_ok=True)
    frames, blends = {}, {}
    cameras = {"chat":15,"profile":27,"side":90,"rear":150,"front":0}
    for key, case in source["cases"].items():
        if a.pilot and key=="flow-cap":
            continue
        fixture = case["baseline_scene"]
        relative = original["fixtures"][fixture]["scene"]
        packed = a.baseline/relative
        assert assembler.sha(packed)==original["files"][relative]
        for candidate in (False,True):
            revision = 316 if candidate else 314
            bpy.ops.wm.open_mainfile(filepath=str(packed))
            scene = bpy.context.scene
            targets = {}
            for role, part in case["parts"].items():
                path = a.output/"assets"/part["file"] if candidate else ROOT.parent/part["source"]
                assert assembler.sha(path)==part["sha256" if candidate else "source_sha256"]
                targets[role]=str(path.resolve())
            assembler.change_parts(scene,{k:v for k,v in old[fixture[5:]]["parts"].items() if v},targets)
            if "glasses" in targets:
                assembler.frame_color(scene,case["features"]["frameColor"],frame_colors)
            if candidate:
                assembler.configure(scene,studio,set_lighting)
            else:
                configure_reference(scene,set_lighting)
                reference_lens(scene,case["features"]["lensTint"],reduce_clear_lens_glare)
            scene.cycles.device = device
            scene.render.resolution_x = scene.render.resolution_y = 512
            for skin in (3,) if a.pilot else range(4):
                recolor(scene,palette,skin)
                views = ("chat",) if a.pilot or skin!=3 else cameras
                for view in views:
                    set_camera(scene,cameras[view])
                    if view!="chat":
                        scene.camera.data.ortho_scale=1.65
                        scene.camera.location.z=1.73
                    name = f"{revision}-{key}-skin{skin}-{view}.png"
                    image = target/name
                    scene.render.filepath=str(image)
                    bpy.ops.render.render(write_still=True)
                    frames[name]=assembler.sha(image)
            if candidate and not a.pilot and key!="flow-cap-bare-eyes":
                set_camera(scene,15)
                scene.render.filepath="//"+key+"-gloss.png"
                bpy.data.orphans_purge(do_recursive=True)
                bpy.ops.file.pack_all()
                images = [im for im in bpy.data.images if im.source=="FILE" and im.users]
                assert all(im.packed_file and im.packed_file.size>0 for im in images)
                blend = scenes/(key+".blend")
                bpy.ops.wm.save_as_mainfile(filepath=str(blend),copy=True)
                blends[blend.name]={"sha256":assembler.sha(blend),"packed_images":len(images)}
            print("Gloss comparison",revision,key,flush=True)
    (target/"receipt.json").write_text(json.dumps({"reference_revision":314,"candidate_revision":316,
        "cameras":cameras,"frames":frames,"blender":blends,"device":device},indent=2)+"\n",newline="\n")


if __name__=="__main__":
    main()
