"""Render matched 320 and 321 native review fixtures with paired depth."""
from argparse import ArgumentParser
import importlib.util
import json
from pathlib import Path
import shutil
import sys

import bpy

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("art319",ROOT/"319/tools/refine.py")
art = importlib.util.module_from_spec(spec)
spec.loader.exec_module(art)
assembly = art.previous.render.assembler
SIZE = 384
SPAN = 1.25
TARGET = 1.805
YAW = 15
PLATE = [241,244,250]
CASES = {
    "ponytail-jersey": ("Feminine/ponytail/none/jersey/ombre","ponytail-bare-ombre","none"),
    "flow-long-beard": ("Masculine/flow/cap/sweatshirt/default","long-beard","long"),
}


def load(path):
    return json.loads(path.read_bytes())


def resolve(catalogue,selector,groom):
    build = selector.split("/")[0]
    row = catalogue["fit_rows"][selector]
    roles = catalogue["independent_roles"][build]
    face = roles["faces"]["bean"]
    parts = {role:row[role] for role in ("hair","hairLengths","headgear","top")}
    parts.update(face,base=roles["bases"]["pants"]["clothed"],bottom=roles["bottoms"]["pants"],
                 groom=roles["grooms"][groom])
    if groom in catalogue["groom_mouths"]:
        parts["mouth"] = catalogue["groom_mouths"][groom]
    return {role:digest for role,digest in parts.items() if digest}


def main():
    parser = ArgumentParser(description=__doc__)
    for name in ("base","candidate","tools","output"):
        parser.add_argument(name,type=Path)
    args = parser.parse_args(sys.argv[sys.argv.index("--")+1:])
    sys.path.insert(0,str(args.tools))
    from chat_portrait_blender import attach_depth_output, set_camera
    from render_chat_review_blender import recolor

    output = args.output.resolve()
    components = output/"components"
    scenes = output/"scenes"
    references = output/"references"
    for path in (components,scenes,references):
        path.mkdir(parents=True,exist_ok=True)
    receipt = load(args.candidate/"receipt.json")
    assert receipt["revision"]==321 and receipt["base_revision"]==320
    palette = load(args.candidate/"palette.json")
    assert palette==load(args.base/"palette.json")
    shutil.copyfile(args.candidate/"palette.json",output/"palette.json")
    catalogues = {rev:(folder,load(folder/"catalogue.json"))
                  for rev,folder in ((320,args.base),(321,args.candidate))}
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "CUDA"
    prefs.get_devices()
    for adapter in prefs.devices:
        adapter.use = adapter.type=="CUDA"
    device = "GPU" if any(adapter.use for adapter in prefs.devices) else "CPU"
    bpy.context.preferences.filepaths.save_version = 0
    fixtures, pairs = {}, {}
    for case,(selector,template,groom) in CASES.items():
        control = resolve(catalogues[320][1],selector,groom)
        for revision,(folder,catalogue) in catalogues.items():
            assert catalogue["revision"]==revision
            parts = resolve(catalogue,selector,groom)
            assert parts.keys()==control.keys()
            if revision==321:
                for role,base_hash in control.items():
                    assert parts[role]==receipt["replaced_glbs"].get(base_hash,base_hash), (case,role)
            source_scene = args.base/"blender"/(template+".blend")
            bpy.ops.wm.open_mainfile(filepath=str(source_scene))
            scene = bpy.context.scene
            target, paths = {}, {}
            for role,digest in parts.items():
                source = folder/catalogue["components"][digest]["file"]
                assert art.fit.sha(source)==digest,source
                path = components/(digest+".glb")
                if not path.exists():
                    shutil.copyfile(source,path)
                assert art.fit.sha(path)==digest,path
                target[role] = str(path)
                paths[role] = {"file":path.relative_to(output).as_posix(),"sha256":digest}
            existing = {obj["component269"]:"packed" for obj in scene.objects
                        if obj.type=="MESH" and "component269" in obj}
            assembly.change_parts(scene,existing,target)
            for obj in scene.objects:
                if obj.type=="MESH" and obj.get("component269")=="top":
                    obj.visible_glossy = False
            scene.cycles.device = device
            scene.cycles.samples = 32
            scene.cycles.seed = 42
            scene.render.film_transparent = True
            scene.render.image_settings.file_format = "PNG"
            scene.render.image_settings.color_mode = "RGBA"
            scene.render.image_settings.color_depth = "8"
            scene.render.resolution_x = scene.render.resolution_y = SIZE
            scene.render.resolution_percentage = 100
            set_camera(scene,YAW)
            scene.camera.data.ortho_scale = SPAN
            scene.camera.location.z = TARGET
            identity = f"r{revision}-{case}"
            depth = attach_depth_output(scene,references,.5)
            for skin in range(4):
                recolor(scene,palette,skin)
                name = f"{identity}-skin{skin}"
                png = references/(name+".png")
                depth.file_name = name+"-depth"
                scene.render.filepath = str(png)
                bpy.ops.render.render(write_still=True)
                exr, = references.glob(depth.file_name+"*.exr")
                pairs[name] = {"fixture":identity,"skin":skin,"color":png.relative_to(output).as_posix(),
                               "depth":exr.relative_to(output).as_posix()}
            fixture = {"revision":revision,"selector":selector,"eyes":"bean","groom":groom,
                       "bottom":"pants","parts":paths,"lighting_source":template}
            if revision==321:
                scene.render.filepath = "//portrait.png"
                depth.directory = "//"
                bpy.data.orphans_purge(do_recursive=True)
                bpy.ops.file.pack_all()
                packed = scenes/(identity+".blend")
                bpy.ops.wm.save_as_mainfile(filepath=str(packed),copy=True,compress=True)
                fixture["scene"] = packed.relative_to(output).as_posix()
            fixtures[identity] = fixture
    (output/"fixtures.json").write_text(json.dumps({"revision":321,"control_revision":320,"size":SIZE,
        "camera_span":SPAN,"target_z":TARGET,"yaw_degrees":YAW,"plate_srgb":PLATE,"depth_alpha_threshold":.5,
        "fixtures":fixtures,"pairs":pairs},indent=2)+"\n",encoding="utf8",newline="\n")


if __name__=="__main__":
    main()
