"""Build three source Bob models from the concept-led surface construction."""
from argparse import ArgumentParser
from pathlib import Path
import math
import sys
import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from sculpted_surface import build
from study_bob import ANGLES

STYLES=("chosen","blowout","waves","asymmetric")

def render(base,output,quick,selected=None):
    review=output/"review"
    review.mkdir(parents=True,exist_ok=True)
    bpy.context.preferences.filepaths.save_version=0
    for style in (STYLES if selected is None else (selected,)):
        bpy.ops.wm.open_mainfile(filepath=str(base))
        scene=bpy.context.scene
        prefs=bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type="CUDA"
        prefs.get_devices()
        for device in prefs.devices:
            device.use=device.type=="CUDA"
        scene.cycles.device="GPU" if any(d.use for d in prefs.devices) else "CPU"
        scene.cycles.samples=20 if quick else 32
        scene.render.resolution_x=scene.render.resolution_y=480 if quick else 600
        if style!="chosen":
            build(scene,style)
        for angle,(yaw,pitch) in ANGLES.items():
            if quick and angle not in ("front","threequarter","profile","rear"):
                continue
            yaw,pitch=math.radians(yaw),math.radians(pitch)
            target=Vector((0,0,1.82))
            scene.camera.data.ortho_scale=1.16
            scene.camera.location=target+8*Vector((math.sin(yaw)*math.cos(pitch),
                -math.cos(yaw)*math.cos(pitch),math.sin(pitch)))
            scene.camera.rotation_euler=(target-scene.camera.location).to_track_quat("-Z","Y").to_euler()
            if not quick and style!="chosen" and angle=="threequarter":
                bpy.ops.file.pack_all()
                scene.render.filepath=f"//review/{style}-{angle}.png"
                bpy.ops.wm.save_as_mainfile(filepath=str(output/f"Ravedio334-{style}.blend"))
            scene.render.filepath=str(review/f"{style}-{angle}.png")
            bpy.ops.render.render(write_still=True)


if __name__=="__main__":
    parser=ArgumentParser(description=__doc__)
    parser.add_argument("base",type=Path)
    parser.add_argument("output",type=Path)
    parser.add_argument("--quick",action="store_true")
    parser.add_argument("--style",choices=STYLES)
    args=parser.parse_args(sys.argv[sys.argv.index("--")+1:])
    render(args.base,args.output,args.quick,args.style)
