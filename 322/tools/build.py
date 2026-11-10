"""Render the selected long and short beard smiles at the 321 camera."""
from argparse import ArgumentParser
from copy import deepcopy
import json
from pathlib import Path
import shutil
import sys

import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from study import art, assembly, fit, thicker, STROKES


def load(path):
    return json.loads(path.read_bytes())


def write(path,data):
    path.write_text(json.dumps(data,sort_keys=True,indent=2)+"\n",encoding="utf8",newline="\n")


def main():
    parser = ArgumentParser(description=__doc__)
    for name in ("base","tools","output"):
        parser.add_argument(name,type=Path)
    args = parser.parse_args(sys.argv[sys.argv.index("--")+1:])
    sys.path.insert(0,str(args.tools))
    from chat_portrait_blender import attach_depth_output
    from render_chat_review_blender import recolor

    base,output = args.base,args.output
    assets = output/"assets"
    references = output/"handoff/references"
    for folder in (assets,references):
        folder.mkdir(parents=True,exist_ok=True)
    catalogue = load(base/"catalogue.json")
    overlay = load(base/"overlay.json")
    palette = load(base/"palette.json")
    components = catalogue["components"]
    old_index = load(base/"handoff/fixtures.json")
    control = old_index["fixtures"]["r321-flow-long-beard"]["parts"]
    groom = catalogue["independent_roles"]["Masculine"]["grooms"]
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "CUDA"
    prefs.get_devices()
    for adapter in prefs.devices:
        adapter.use = adapter.type=="CUDA"
    device = "GPU" if any(adapter.use for adapter in prefs.devices) else "CPU"
    bpy.context.preferences.filepaths.save_version = 0
    fixtures, pairs, changes = {}, {}, {}

    for style,variant in (("long","strong"),("short","soft")):
        old_digest = catalogue["groom_mouths"][style]
        previous = base/components[old_digest]["file"]
        beard = base/components[groom[style]]["file"]
        mouth = assets/(style+"-smile.glb")
        scale = STROKES[variant]
        art.previous.edit(previous,mouth,{"relaxed smile":lambda points:thicker(points,scale)})
        assert not fit.surface(beard).overlap(fit.surface(mouth)),style
        digest = fit.sha(mouth)
        target = assets/(digest+".glb")
        mouth.replace(target)
        components[digest] = {"file":"assets/"+target.name,"bytes":target.stat().st_size}
        catalogue["groom_mouths"][style] = digest
        overlay["groomMouth"][style] = digest
        changes[style] = {"before":old_digest,"after":digest,"vertical_scale":scale}
        for revision in (321,322):
            bpy.ops.wm.open_mainfile(filepath=str(base/"handoff/scenes/r321-flow-long-beard.blend"))
            scene = bpy.context.scene
            scene.cycles.device = device
            used = target if revision==322 else previous
            assembly.change_parts(scene,{"groom":"packed","mouth":"packed"},{"groom":str(beard),"mouth":str(used)})
            depth = attach_depth_output(scene,references,.5)
            identity = f"r{revision}-flow-{style}-beard"
            parts = deepcopy(control)
            parts["groom"] = {"file":"components/"+groom[style]+".glb","sha256":groom[style]}
            parts["mouth"] = {"file":"components/"+fit.sha(used)+".glb","sha256":fit.sha(used)}
            for part in parts.values():
                relative = components[part["sha256"]]["file"]
                source = output/relative if part["sha256"]==digest else base/relative
                dest = output/"handoff"/part["file"]
                dest.parent.mkdir(parents=True,exist_ok=True)
                if not dest.exists():
                    shutil.copyfile(source,dest)
                assert fit.sha(dest)==part["sha256"]
            fixtures[identity] = {**old_index["fixtures"]["r321-flow-long-beard"],"revision":revision,
                                  "groom":style,"parts":parts}
            fixtures[identity].pop("scene",None)
            for skin in range(4):
                recolor(scene,palette,skin)
                name = f"{identity}-skin{skin}"
                depth.file_name = name+"-depth"
                scene.render.filepath = str(references/(name+".png"))
                bpy.ops.render.render(write_still=True)
                exr, = references.glob(depth.file_name+"*.exr")
                pairs[name] = {"fixture":identity,"skin":skin,"color":"references/"+name+".png",
                               "depth":"references/"+exr.name}

    # Retain the full 321 catalogue with just the beard-specific mouth bindings replaced.
    import os
    for entry in components.values():
        dest = output/entry["file"]
        if not dest.exists():
            src = base/entry["file"]
            try:
                os.link(src,dest)
            except OSError:
                shutil.copyfile(src,dest)
    for key in ("palette","studio","finish"):
        shutil.copyfile(base/catalogue[key],output/catalogue[key])
    shutil.copyfile(base/"palette.json",output/"handoff/palette.json")
    dyes = catalogue["shared_jersey_dyes_dir"]
    shutil.copytree(base/dyes,output/dyes,dirs_exist_ok=True)
    catalogue["revision"] = 322
    write(output/"catalogue.json",catalogue)
    write(output/"overlay.json",overlay)
    write(output/"receipt.json",{"revision":322,"base_revision":321,"groom_mouths":changes})
    write(output/"handoff/fixtures.json",{**old_index,"revision":322,"control_revision":321,
                                        "fixtures":fixtures,"pairs":pairs})


if __name__=="__main__":
    main()
