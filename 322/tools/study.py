"""Render beard smile candidates with the 321 studio and chat camera."""
from argparse import ArgumentParser
import importlib.util
import json
from pathlib import Path
import sys

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("art319",ROOT/"319/tools/refine.py")
art = importlib.util.module_from_spec(spec)
spec.loader.exec_module(art)
fit = art.fit
assembly = art.previous.render.assembler
STROKES = {"soft":1.25,"strong":1.48}


def thicker(points,scale):
    x,y,z = points.T
    axis = 1.6115+.014*np.clip(np.abs(x)/(.088*.94),0,1)**2
    return art.previous.conform(x,y,z,x,axis+(y-axis)*scale+.0015)


def main():
    parser = ArgumentParser(description=__doc__)
    for name in ("base","tools","output"):
        parser.add_argument(name,type=Path)
    args = parser.parse_args(sys.argv[sys.argv.index("--")+1:])
    sys.path.insert(0,str(args.tools))
    from render_chat_review_blender import recolor
    base = args.base
    output = args.output
    output.mkdir(parents=True,exist_ok=True)
    catalogue = json.loads((base/"catalogue.json").read_bytes())
    palette = json.loads((base/"palette.json").read_bytes())
    faces = catalogue["independent_roles"]["Masculine"]
    def component(digest):
        return base/catalogue["components"][digest]["file"]
    old = component(catalogue["groom_mouths"]["long"])
    long = component(faces["grooms"]["long"])
    short = component(faces["grooms"]["short"])
    candidates = {"long-321":old,"short-321":old}
    selected = {"long":"strong","short":"soft"}
    for name,scale in STROKES.items():
        path = output/(name+".glb")
        art.previous.edit(old,path,{"relaxed smile":lambda points: thicker(points,scale)})
        overlaps = fit.surface(long).overlap(fit.surface(path))
        print(name,"mouth-beard intersections",len(overlaps),flush=True)
        assert not overlaps
        candidates["long-"+name] = path
        if name==selected["short"]:
            assert not fit.surface(short).overlap(fit.surface(path))
            candidates["short-"+name] = path

    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "CUDA"
    prefs.get_devices()
    for adapter in prefs.devices:
        adapter.use = adapter.type=="CUDA"
    device = "GPU" if any(adapter.use for adapter in prefs.devices) else "CPU"
    for name,path in candidates.items():
        bpy.ops.wm.open_mainfile(filepath=str(base/"handoff/scenes/r321-flow-long-beard.blend"))
        scene = bpy.context.scene
        target = {"mouth":str(path)}
        if name=="short-321":
            target["groom"] = str(short)
        assembly.change_parts(scene,{role:"packed" for role in target},target)
        scene.render.use_compositing = False
        scene.cycles.device = device
        for skin in (0,3):
            recolor(scene,palette,skin)
            scene.render.filepath = str(output/f"{name}-skin{skin}.png")
            bpy.ops.render.render(write_still=True)


if __name__=="__main__":
    main()
