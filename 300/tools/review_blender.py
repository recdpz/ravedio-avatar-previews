"""Render the revised Curls fixture in the same Blender studio used in 299."""
import importlib.util
import json
import sys
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location("preview299",ROOT/"299/tools/pack_native.py")
review=importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)
from pack_native import local_path
from render_references import configure, load_studio
from pack_native import apply_materials, material_overrides

source, out = map(Path, sys.argv[-2:])
out.mkdir(parents=True, exist_ok=False)
report = json.loads(source.read_text(encoding="utf8"))
assert report["revision"] == "300"
parts = {role:local_path(uri) for role,uri in report["fixtures"]["Feminine"]["parts"].items()}
scene, _ = load_studio("Feminine", parts)
scene["avatar_revision"] = "300"
apply_materials(scene,material_overrides("Feminine"))
depth = configure(scene)
scene.render.film_transparent = True
floor = scene.objects.get("Studio floor")
if floor:
    floor.visible_camera = False
scene.cycles.samples = 48
rows = [review.pair(scene,out,depth,yaw,span,height,512,1,name)
        for yaw,span,height,name in (
            (-20,1.10,1.78,"portrait"),(0,1.50,1.57,"front"),
            (-90,1.50,1.57,"left"),(90,1.50,1.57,"right"),(180,1.50,1.57,"rear"),
        )]
(out/"views.json").write_text(json.dumps(rows,indent=2)+"\n",encoding="utf8")
