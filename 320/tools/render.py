"""Render matched source color comparisons under the approved Blender rig."""
from argparse import ArgumentParser
import importlib.util
import json
from pathlib import Path
import sys

import bpy

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("ref319",ROOT/"319/tools/refine.py")
ref = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ref)
render = ref.previous.render
gloss = ref.fit.gloss

CASES = {
    "taper": ("Masculine/taper/none/sweatshirt/default","318/blender/short.blend"),
    "buzz": ("Masculine/buzz/none/sweatshirt/default","318/blender/short.blend"),
    "long-beard": ("Masculine/flow/cap/sweatshirt/default","319/blender/long.blend"),
    "long-bangs": ("Feminine/side-sweep/none/open/default","316/blender/curls-pashmina.blend"),
    "curls-pashmina": ("Feminine/curls/pashmina/open/default","316/blender/curls-pashmina.blend"),
    "ponytail-bare-ombre": ("Feminine/ponytail/none/jersey/ombre","317/blender/ponytail-beanie-jersey.blend"),
    "ponytail-ombre": ("Feminine/ponytail/beanie/jersey/ombre","317/blender/ponytail-beanie-jersey.blend"),
}


def load(path):
    return json.loads(path.read_bytes())


def main():
    parser = ArgumentParser(description=__doc__)
    for name in ("work","mobile_tools","palette"):
        parser.add_argument(name,type=Path)
    parser.add_argument("--case",choices=CASES)
    args = parser.parse_args(sys.argv[sys.argv.index("--")+1:])
    sys.path.insert(0,str(args.mobile_tools))
    from chat_portrait_blender import set_camera
    from render_chat_review_blender import recolor
    palette = load(args.palette)
    data = load(ROOT/"315/catalogue-input.json")
    old_map = load(ROOT/"315/asset-map.json")["components"]
    recipe = load(ROOT/"316/finish.json")
    output = args.work/"native320"
    overlay = load(output/"overlay.json")["components"]
    controls = output/"controls"
    controls.mkdir(exist_ok=True)
    raw = output/"raw"
    raw.mkdir(exist_ok=True)
    scenes = output/"blender"
    scenes.mkdir(exist_ok=True)
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "CUDA"
    prefs.get_devices()
    for adapter in prefs.devices:
        adapter.use = adapter.type=="CUDA"
    device = "GPU" if any(adapter.use for adapter in prefs.devices) else "CPU"
    bpy.context.preferences.filepaths.save_version = 0

    def asset(source,role,new):
        if new:
            return str(output/"assets"/(overlay[source]+".glb"))
        blob = (args.work/"native315/assets"/(old_map[source]+".glb")).read_bytes()
        blob,_ = gloss.revise(blob,role,recipe,None)
        file = controls/(gloss.digest(blob)+".glb")
        file.write_bytes(blob)
        return str(file)

    for name,(row_key,template) in CASES.items():
        if args.case and name!=args.case:
            continue
        row = data["rows"][row_key]
        style,_,headwear,*_ = row_key.split("/")
        for new in (False,True):
            bpy.ops.wm.open_mainfile(filepath=str(args.work/("native"+template)))
            scene = bpy.context.scene
            parts = {role:asset(row[role],role,new) for role in ("hair","hairLengths") if row[role]}
            remove = {}
            if headwear=="none":
                remove["headgear"] = "packed"
                if not row["hairLengths"]:
                    remove["hairLengths"] = "packed"
            if name=="long-beard":
                if new:
                    parts["groom"] = asset(data["builds"]["Masculine"]["grooms"]["long"],"groom",True)
            elif style=="Masculine":
                if name=="taper":
                    parts["groom"] = asset(data["builds"]["Masculine"]["grooms"]["stubble"],"groom",new)
                else:
                    remove["groom"] = "packed"
                parts["mouth"] = str(args.work/"native315/assets"/(old_map[data["builds"]["Masculine"]["faces"]["original"]["mouth"]]+".glb"))
            if style=="Feminine" and headwear in ("none","pashmina"):
                remove.update(extra="packed",glasses="packed",lenses="packed")
            render.assembler.change_parts(scene,{**remove,**{role:"packed" for role in parts}},parts)
            scene.render.use_compositing = False
            scene.cycles.device = device
            scene.cycles.samples = 32
            for tone in (2,3):
                recolor(scene,palette,tone)
                angles = [("chat",15)]
                if tone==3:
                    angles.extend((("side",90),("opposite",-48)))
                for label,yaw in angles:
                    render.master_camera(scene,set_camera,yaw)
                    file = raw/f"{name}-{int(new)}-skin{tone}-{label}.png"
                    scene.render.filepath = str(file)
                    bpy.ops.render.render(write_still=True)
            if new:
                render.master_camera(scene,set_camera,15)
                bpy.data.orphans_purge(do_recursive=True)
                bpy.ops.file.pack_all()
                bpy.ops.wm.save_as_mainfile(filepath=str(scenes/(name+".blend")),copy=True)


if __name__=="__main__":
    main()
