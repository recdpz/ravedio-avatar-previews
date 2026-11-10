"""Render the new fits under the exact 316 lighting and a shared portrait camera."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import bpy

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("gloss_assembler",ROOT/"315/tools/blender.py")
assembler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(assembler)

SIDE_CASES = {"ponytail-beanie-jersey","flow-cap-bare-eyes","flow-long"}
MASTER = {"span":1.60,"target_z":1.68,"size":640}
CROPS = {
    "original":{"span":1.16,"target_z":1.85,"box":[88,20,552,484]},
    "chat":{"span":1.25,"target_z":1.805,"box":[70,20,570,520]},
    "profile":{"span":1.36,"target_z":1.75,"box":[48,20,592,564]},
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def master_camera(scene, set_camera, yaw):
    set_camera(scene,yaw)
    scene.camera.data.ortho_scale=MASTER["span"]
    scene.camera.location.z=MASTER["target_z"]
    scene.render.resolution_x=scene.render.resolution_y=MASTER["size"]
    scene.render.resolution_percentage=100


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("output","baseline","palette","mobile_tools"):
        p.add_argument(name,type=Path)
    p.add_argument("--pilot",action="store_true")
    p.add_argument("--case",action="append")
    a=p.parse_args(sys.argv[sys.argv.index("--")+1:])
    sys.path.insert(0,str(a.mobile_tools))
    from chat_portrait_blender import set_camera
    from render_chat_review_blender import recolor

    data=assembler.json_file(a.output/"source.json")
    palette=assembler.json_file(a.palette)
    index=assembler.json_file(ROOT/"315/catalogue-input.json")
    frames={key:rgb for key,_,rgb in index["options"]["colors"]["frames"]}
    target=a.output/("pilot" if a.pilot else "raw")
    target.mkdir(exist_ok=True)
    sources=a.output/"blender"
    sources.mkdir(exist_ok=True)
    prefs=bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type="CUDA"
    prefs.get_devices()
    for adapter in prefs.devices:
        adapter.use=adapter.type=="CUDA"
    device="GPU" if any(adapter.use for adapter in prefs.devices) else "CPU"
    bpy.context.preferences.filepaths.save_version=0
    stats,scenes={},{}
    if a.case:
        assert not a.pilot and set(a.case)<=data["cases"].keys()
        prior=assembler.json_file(target/"receipt.json")
        stats,scenes=prior["frames"],prior["scenes"]
    for key,case in data["cases"].items():
        if a.case and key not in a.case:
            continue
        if a.pilot and key not in ("ponytail-beanie-jersey","flow-cap-bare-eyes","flow-mustache"):
            continue
        reference=key if key in ("curls-pashmina","ponytail-beanie-jersey") else "flow-cap"
        template=a.baseline/"blender"/(reference+".blend")
        for revision in (316,317):
            bpy.ops.wm.open_mainfile(filepath=str(template))
            scene=bpy.context.scene
            field="old" if revision==316 else "new"
            paths={}
            for role,item in case["parts"].items():
                file=Path(item[field])
                assert sha(file)==item[field+"_sha256"]
                paths[role]=str(file)
            template_roles={o["component269"]:"packed" for o in scene.objects if o.type=="MESH" and "component269" in o}
            assembler.change_parts(scene,template_roles,paths)
            if "glasses" in paths:
                assembler.frame_color(scene,case["features"]["frameColor"],frames)
            scene.cycles.device=device
            scene.cycles.samples=32
            scene.cycles.seed=42
            scene.render.use_compositing=False
            for obj in scene.objects:
                if obj.type=="MESH" and obj.get("component269")=="top":
                    obj.visible_glossy=False
            for skin in ((3,) if a.pilot else range(4)):
                recolor(scene,palette,skin)
                views=[("front",15)]
                if skin==3 and key in SIDE_CASES:
                    views.extend([("side",90),("rear",150)])
                for name,yaw in views:
                    master_camera(scene,set_camera,yaw)
                    file=target/f"{revision}-{key}-skin{skin}-{name}.png"
                    scene.render.filepath=str(file)
                    bpy.ops.render.render(write_still=True)
                    stats[file.name]=sha(file)
            if revision==317 and not a.pilot and key in ("ponytail-beanie-jersey","flow-cap-bare-eyes","flow-long"):
                set_camera(scene,15)
                scene.camera.data.ortho_scale=CROPS["profile"]["span"]
                scene.camera.location.z=CROPS["profile"]["target_z"]
                scene.render.filepath="//"+key+"-317.png"
                bpy.data.orphans_purge(do_recursive=True)
                bpy.ops.file.pack_all()
                used=[im for im in bpy.data.images if im.source=="FILE" and im.users]
                assert all(im.packed_file and im.packed_file.size>0 for im in used)
                file=sources/f"{key}.blend"
                bpy.ops.wm.save_as_mainfile(filepath=str(file),copy=True)
                scenes[file.name]={"sha256":sha(file),"packed_images":len(used)}
            print("Fit review",revision,key,flush=True)
    (target/"receipt.json").write_text(json.dumps({"frames":stats,"crops":CROPS,"camera":MASTER,
        "scenes":scenes,"device":device,"side_cases":sorted(SIDE_CASES)},indent=2)+"\n",newline="\n")


if __name__=="__main__":
    main()
