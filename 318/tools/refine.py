"""Fit connected mustaches and quieter smiles to the 317 short and long beard."""
from argparse import ArgumentParser
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import struct
import sys
import zlib

import bpy
import numpy as np

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]/"317"/"tools"
spec = importlib.util.spec_from_file_location("fit317", BASE/"refine.py")
fit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fit)
spec = importlib.util.spec_from_file_location("render317", BASE/"render-fit.py")
render = importlib.util.module_from_spec(spec)
spec.loader.exec_module(render)

CASES = {"short": ("flow-cap-bare-eyes", "short body"), "long": ("flow-long", "rounded long")}


def conform(x, y, z, new_x, new_y, loft=1, offset=0):
    new_z = fit.head_front(new_x,new_y)+(z-fit.head_front(x,y))*loft+offset
    return np.column_stack((new_x,new_y,new_z))


def smile(points):
    x,y,z = points.T
    axis = 1.6095 + .014*np.clip(np.abs(x)/.088,0,1)**2
    return conform(x,y,z,x*.94,axis+.73*(y-axis)+.002,.62)


def mustache(points, long):
    x,y,z = points.T
    t = np.clip(np.abs(x)/.0985,0,1)
    axis = 1.648-.0085*t**1.55
    outer = fit.smooth(.35,1,t)
    new_x = x+np.sign(x)*(.069 if long else .065)*outer
    drop = (.068 if long else .065)*fit.smooth(.65,1,t)
    thickness = .83+(3.6 if long else 2.8)*fit.smooth(.60,.86,t)
    # The center part cuts into the upper edge and fades before the lower edge.
    part = .005*(1-fit.smooth(.012,.034,np.abs(x)))*fit.smooth(-.003,.010,y-axis)
    new_y = axis - drop + (y-axis)*thickness - part
    # Sink the ends behind the cheek hair so the joint does not show a tip.
    seat = (.0044 if long else .0021)*fit.smooth(.50,.76,t)-.014*fit.smooth(.86,1,t)
    return conform(x,y,z,new_x,new_y,.84 if long else .66,seat)


def beard(points, long):
    x,y,z = points.T
    lateral = np.abs(x)
    front = fit.smooth(.191,.258,z)
    rim = fit.smooth(1.537,1.598,y)
    middle = 1-fit.smooth(.075,.150,lateral)
    clearance = (.003+.009*fit.smooth(.035,.092,lateral))*front*rim
    clearance *= 1-fit.smooth(.089,.120,lateral)
    # Broaden the cheek into the descending mustache at each side.
    cheek = .009*front*rim*fit.smooth(.095,.126,lateral)*(1-fit.smooth(.150,.199,lateral))
    # Ease the volume only along the front edge. Let the chin keep its mass.
    loft = 1-(.68 if long else .36)*front*rim*middle
    return conform(x,y,z,x,y+cheek-clearance,loft)


def soften_join(doc,binary,mesh,points):
    for primitive in mesh["primitives"]:
        attributes = primitive["attributes"]
        x,y,z = points.T
        depth = z-fit.head_front(x,y)
        fade = fit.smooth(-.0005,.0020,depth)
        colors = np.ones((len(points),4),dtype="<f4")
        colors[:,3] = .70+.30*fade
        attributes["COLOR_0"] = fit.append_accessor(doc,binary,colors,5126,"VEC4",34962)
        material = deepcopy(doc["materials"][primitive["material"]])
        material["name"] += " / connected mustache"
        material["alphaMode"] = "BLEND"
        material["pbrMetallicRoughness"]["roughnessFactor"] = .52
        material["extensions"]["KHR_materials_clearcoat"]["clearcoatFactor"] = .06
        material["extensions"]["KHR_materials_specular"]["specularFactor"] = .32
        primitive["material"] = len(doc["materials"])
        doc["materials"].append(material)


def rim_finish(doc,binary,mesh,points):
    """Bake a smooth material transition into the front of the long beard."""
    x,y,z = points.T
    weight = fit.smooth(1.488,1.553,y)*fit.smooth(.190,.249,z)
    weight *= 1-fit.smooth(.113,.189,np.abs(x))
    # Sample texel centers. R controls coat, G roughness, A specular.
    uv = np.column_stack((.25+.50*weight,np.full(len(points),.5))).astype("<f4")
    coordinates = fit.append_accessor(doc,binary,uv,5126,"VEC2",34962)

    def chunk(name,payload):
        return struct.pack(">I",len(payload))+name+payload+struct.pack(">I",zlib.crc32(name+payload))

    pixels = bytes((0,255,152,255,255,24,255,255,61))
    data = b"\x89PNG\r\n\x1a\n"
    data += chunk(b"IHDR",struct.pack(">IIBBBBB",2,1,8,6,0,0,0))
    data += chunk(b"IDAT",zlib.compress(pixels))+chunk(b"IEND",b"")
    views = doc["bufferViews"]
    views.append({"buffer":0,"byteOffset":len(binary),"byteLength":len(data)})
    binary.extend(data)
    binary.extend(b"\0"*(-len(binary)%4))
    images = doc.setdefault("images",[])
    images.append({"bufferView":len(views)-1,"mimeType":"image/png","name":"Long beard mouth finish"})
    textures = doc.setdefault("textures",[])
    textures.append({"source":len(images)-1})
    texture = {"index":len(textures)-1}
    for primitive in mesh["primitives"]:
        primitive["attributes"]["TEXCOORD_0"] = coordinates
        material = doc["materials"][primitive["material"]]
        pbr = material["pbrMetallicRoughness"]
        pbr["roughnessFactor"] = .72
        pbr["metallicRoughnessTexture"] = texture
        extensions = material["extensions"]
        extensions["KHR_materials_clearcoat"]["clearcoatTexture"] = texture
        extensions["KHR_materials_specular"]["specularTexture"] = texture


def edit(source, output, warps, groom=False):
    doc,binary = fit.read_glb(source)
    shared = []
    for mesh in doc["meshes"]:
        primitives = mesh["primitives"]
        unique = {p["attributes"]["POSITION"]: p for p in primitives}
        if len(unique) < len(primitives):
            shared.append((mesh,primitives))
            mesh["primitives"] = list(unique.values())
    for substring,warp in warps.items():
        assert fit.update_meshes(doc,binary,lambda name: warp if substring in name else None)>0
    for mesh,primitives in shared:
        mesh["primitives"] = primitives
    if groom:
        original,old_binary = fit.read_glb(source)
        for node,rotation,origin in fit.node_transforms(original):
            if "mesh" not in node:
                continue
            mesh = doc["meshes"][node["mesh"]]
            position = mesh["primitives"][0]["attributes"]["POSITION"]
            points = fit.accessor(original,old_binary,position,3)@rotation.T+origin
            if "shared mustache" in mesh["name"]:
                soften_join(doc,binary,mesh,points)
            if "rounded long" in mesh["name"]:
                rim_finish(doc,binary,mesh,points)
        for material in doc["materials"]:
            if material["name"].endswith("/ mouth edge"):
                material["extensions"]["KHR_materials_clearcoat"]["clearcoatFactor"] = .07
        doc["buffers"][0]["byteLength"] = len(binary)
    fit.write_glb(output,doc,binary)


def bake(args):
    output = args.output
    source = json.loads((args.baseline/"source.json").read_bytes())
    mouth = output/"assets"/"bearded-smile.glb"
    edit(Path(source["cases"][CASES["short"][0]]["parts"]["mouth"]["new"]),mouth,{"relaxed smile": smile})
    mouth_bvh = fit.surface(mouth)
    receipt = {}
    for style,(key,body) in CASES.items():
        old = Path(source["cases"][key]["parts"]["groom"]["new"])
        target = output/"assets"/f"groom-{style}.glb"
        long = style=="long"
        edit(old,target,{"shared mustache": lambda p: mustache(p,long),body: lambda p: beard(p,long)},groom=True)
        face_hair = fit.surface(target,lambda name: "shared mustache" in name)
        cheek = fit.surface(target,lambda name: body in name)
        assert not face_hair.overlap(mouth_bvh), style
        assert face_hair.overlap(cheek), style
        assert not cheek.overlap(mouth_bvh), style
        receipt[style] = {
            "source_case": key,
            "groom": target.name,
            "groom_sha256": fit.sha(target),
            "mouth": mouth.name,
            "mouth_sha256": fit.sha(mouth),
        }
    (output/"source.json").write_text(json.dumps({"base":317,"revision":318,"cases":receipt},indent=2)+"\n")
    return receipt


def review(args, cases):
    sys.path.insert(0,str(args.mobile_tools))
    from chat_portrait_blender import set_camera
    from render_chat_review_blender import recolor

    palette = json.loads(args.palette.read_bytes())
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "CUDA"
    prefs.get_devices()
    for adapter in prefs.devices:
        adapter.use = adapter.type=="CUDA"
    device = "GPU" if any(adapter.use for adapter in prefs.devices) else "CPU"
    bpy.context.preferences.filepaths.save_version = 0
    for style,info in cases.items():
        bpy.ops.wm.open_mainfile(filepath=str(args.baseline/"blender"/(info["source_case"]+".blend")))
        scene = bpy.context.scene
        render.assembler.change_parts(scene,{"mouth":"packed","groom":"packed"},{
            role:str(args.output/"assets"/info[role]) for role in ("mouth","groom")
        })
        scene.render.use_compositing = False
        scene.cycles.device = device
        scene.cycles.samples = 32
        for skin in (0,3):
            recolor(scene,palette,skin)
            for angle,yaw in (("front",0),("chat",15),("turn",48),("profile",90),("opposite",-48)):
                render.master_camera(scene,set_camera,yaw)
                scene.render.filepath = str(args.output/"raw"/f"{style}-skin{skin}-{angle}.png")
                bpy.ops.render.render(write_still=True)
        render.master_camera(scene,set_camera,15)
        bpy.data.orphans_purge(do_recursive=True)
        bpy.ops.file.pack_all()
        bpy.ops.wm.save_as_mainfile(filepath=str(args.output/"blender"/f"{style}.blend"),copy=True)


def main():
    parser = ArgumentParser(description=__doc__)
    for name in ("output","baseline","palette","mobile_tools"):
        parser.add_argument(name,type=Path)
    args = parser.parse_args(sys.argv[sys.argv.index("--")+1:])
    for folder in ("assets","raw","blender"):
        (args.output/folder).mkdir(parents=True,exist_ok=True)
    review(args,bake(args))


if __name__=="__main__":
    main()
