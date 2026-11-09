"""Author ordinary, independently selectable 309 GLBs from the 308 art."""
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys

import bpy
import numpy as np

REV = Path(__file__).resolve().parents[1]
ROOT = REV.parent
OUT = REV / "assets"
sys.path.insert(0, str(ROOT / "305/tools"))
from beanie import attachment, fitted_crown, isolate, updos

CENTER = updos.CENTER
SOURCES = json.loads((REV / "sources.json").read_text())
ASSETS = {}
SLICES = 216


def smooth(lo, hi, value):
    t = np.clip((value - lo) / (hi - lo), 0., 1.)
    return t*t*(3 - 2*t)


def cap_ring(theta, alpha):
    """The seat follows the head; ease gathers up and toward the back."""
    height = np.sin(alpha)
    c, s = np.cos(theta), np.sin(theta)
    hem = 1.916 + .026*c + .007*np.cos(2*theta) + .005*np.sin(theta + .8)
    crown = 2.298 + .004*np.sin(theta - .7)*(1-height)
    y = hem + (crown - hem)*height
    # A rolled hem and a slightly pinched fold above its rear quarter.
    rolled = .016*smooth(0., .040, height)*(1-smooth(.138, .236, height))
    cuff_edge = .004*np.exp(-((height - .196 - .014*np.sin(theta+.6))/.030)**2)
    fold = .015*np.exp(-((height-.52)/.21)**2) * np.exp(-((c+.82)/.20)**2)*(1+.30*s)
    rib_phase = 36*theta + 2.3*height*np.sin(theta + .6)
    rib_height = (.0036 - .0023*smooth(.18,.26,height))*(1-smooth(.81,.99,height))
    ribs = rib_height*(.5+.5*np.cos(rib_phase))**2
    r = (.409 + .019*smooth(.18,.60,height) + rolled + cuff_edge - fold)*np.cos(alpha) + ribs
    lean = smooth(.21, 1., height)
    return np.column_stack((r*s + .020*lean, y, CENTER[2] + r*c - .065*lean))


def knit_material(name, color):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color,1)
    shader.inputs["Roughness"].default_value = .78
    shader.inputs["Specular IOR Level"].default_value = .25
    return material


def beanie_mesh(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    theta = np.arange(SLICES)*2*np.pi/SLICES
    alphas = np.r_[np.linspace(0., .258, 14, endpoint=False),
                   np.linspace(.258, np.pi/2, 26, endpoint=False)]
    rings = len(alphas)
    outer = np.concatenate([cap_ring(theta, alpha) for alpha in alphas])
    pole = cap_ring(np.zeros(1), np.pi/2)[0]
    # Give the rolled hem real thickness, returning smoothly inside the cap.
    inner = outer.copy()
    for row, alpha in enumerate(alphas):
        sl = slice(row*SLICES, (row+1)*SLICES)
        inner[sl,0] -= .013*np.sin(theta)*np.cos(alpha)
        inner[sl,1] -= .012*np.sin(alpha)
        inner[sl,2] -= .013*np.cos(theta)*np.cos(alpha)
    layer = len(outer)+1
    points = np.vstack([outer, pole, inner, pole-[0,.012,0]])
    faces, cuff_faces = [], []
    for ring in range(rings-1):
        for i in range(SLICES):
            j = (i+1)%SLICES
            a,b,c,d = ring*SLICES+i,ring*SLICES+j,(ring+1)*SLICES+j,(ring+1)*SLICES+i
            if np.sin(alphas[ring]) < .214:
                cuff_faces.append(len(faces))
            faces.extend([(a,b,c,d),(layer+d,layer+c,layer+b,layer+a)])
    for i in range(SLICES):
        j = (i+1)%SLICES
        a,b = (rings-1)*SLICES+i,(rings-1)*SLICES+j
        faces.extend([(a,b,len(outer)),(layer+b,layer+a,2*layer-1)])
        cuff_faces.append(len(faces))
        faces.append((j,i,layer+i,layer+j))
    mesh = bpy.data.meshes.new("Knit beanie shell and rolled hem")
    # glTF (x,y,z) to Blender (x,-z,y).
    mesh.from_pydata(points[:,[0,2,1]] * [1,-1,1],[],faces)
    mesh.update()
    cap = bpy.data.objects.new("Beanie / soft rib knit", mesh)
    bpy.context.collection.objects.link(cap)
    mesh.materials.append(knit_material("Beanie / knit", (.065,.115,.180)))
    mesh.materials.append(knit_material("Beanie / rolled cuff", (.053,.095,.152)))
    for poly in mesh.polygons:
        poly.use_smooth = True
    for index in cuff_faces:
        mesh.polygons[index].material_index = 1
    bpy.ops.export_scene.gltf(filepath=str(path),export_format="GLB",export_materials="EXPORT")


def revise_features(source, target, role):
    model, data = updos.read_glb(source)
    changed = 0
    for node, rot, offset in updos.node_transforms(model):
        if "mesh" not in node:
            continue
        for prim in model["meshes"][node["mesh"]]["primitives"]:
            material = model["materials"][prim["material"]]
            attr = prim["attributes"]
            if role == "eyes" and material["name"].startswith("Eye highlight181"):
                pos = updos.vectors(model, data, attr["POSITION"])
                world = pos @ rot.T + offset
                for mask in [world[:,0] >= 0, world[:,0] < 0]:
                    if mask.any():
                        pivot = world[mask].mean(axis=0)
                        world[mask] = pivot + 1.43*(world[mask] - pivot)
                pos[:] = (world - offset) @ rot
            elif role == "mouth" and material["name"].startswith("Face / ink209"):
                pos = updos.vectors(model, data, attr["POSITION"])
                pos += .0058 * updos.vectors(model, data, attr["NORMAL"])
                material.setdefault("extensions",{}).setdefault("KHR_materials_specular",{})["specularFactor"] = .18
                if "KHR_materials_specular" not in model.setdefault("extensionsUsed", []):
                    model["extensionsUsed"].append("KHR_materials_specular")
            else:
                continue
            model["accessors"][attr["POSITION"]].update(min=pos.min(0).tolist(), max=pos.max(0).tolist())
            changed += 1
    assert changed, (source,role)
    updos.write_glb(target,model,data)


def pin_sprout(source, path, old_hat, new_hat):
    model, data = updos.read_glb(source)
    pin = next((node,rot,offset) for node,rot,offset in updos.node_transforms(model)
               if "clip silver235" in node.get("name",""))
    node, rot, offset = pin
    p = model["meshes"][node["mesh"]]["primitives"][0]["attributes"]["POSITION"]
    center = (updos.vectors(model,data,p) @ rot.T + offset).mean(0)
    # A rigid move of the whole clip assembly keeps leaves and clip together.
    shift = np.array([.008,0.,-.038])
    old_hit = old_hat.ray_cast((center[0],3.,center[2]),(0.,-1.,0.))[0]
    new_hit = new_hat.ray_cast((center[0]+shift[0],3.,center[2]+shift[2]),(0.,-1.,0.))[0]
    assert old_hit is not None and new_hit is not None, source
    shift[1] = new_hit.y - old_hit.y
    for index in model["scenes"][model.get("scene",0)]["nodes"]:
        root = model["nodes"][index]
        root["translation"] = (root.get("translation",[0.,0.,0.]) + shift).tolist()
    updos.write_glb(path, model,data)


def pose_ponytail(uncovered, covered, hat):
    _,_,parts = updos.load_parts(uncovered,"ponytail")
    vertices,faces = updos.group_geometry(parts,1)
    elastic = next(p["points"].mean(0) for p in parts if "tie220" in p["name"])
    scalp = updos.surface(covered,lambda name:"roots220" in name)
    options = product(np.linspace(-.96,-1.32,10),(.20,.24,.16,.28,.12,.08,.0),
                      (-.20,-.24,-.16,-.28,-.12,-.32), (0.,-.08,.08))
    def cost(values):
        lift,yaw,pitch,roll = values
        return 2.8*abs(lift+1.10)+abs(yaw-.22)+1.5*abs(pitch+.20)+abs(roll)
    for lift,yaw,pitch,roll in sorted(options,key=cost):
        rotate = updos.axis_rotation
        target = updos.apply(elastic,rotate("y",yaw)@rotate("x",lift),np.zeros(3))
        rotation = rotate("z",roll)@rotate("y",yaw)@rotate("x",pitch)
        offset = target-updos.apply(elastic,rotation,np.zeros(3))
        points = updos.apply(vertices,rotation,offset)
        if points[:,1].min() < 1.49 or points[:,2].min() < -.64:
            continue
        tail = updos.tree(points,faces)
        if tail.overlap(hat):
            continue
        contact = len(tail.overlap(scalp))
        if contact < 3:
            continue
        return {1:(rotation,offset)}, {"tieCenter":target.tolist(),"tiePitch":float(lift),
                                      "tailPitch":pitch,"yaw":yaw,"roll":roll,"scalpContacts":contact}
    raise ValueError("Ponytail needs a lower rear release")


def record(path):
    ASSETS[path.name] = {"bytes":path.stat().st_size,"sha256":sha256(path.read_bytes()).hexdigest()}
    return "./assets/" + path.name


def main():
    OUT.mkdir(exist_ok=True)
    manifest = {"darkLensOpacity":.74, "eyes":{}, "mouth":{}, "beanie":{}}
    for build, choices in SOURCES["eyes"].items():
        manifest["eyes"][build] = {}
        for eye, source in choices.items():
            output = OUT / f"{build.lower()}-eyes-{eye}.glb"
            revise_features(ROOT/source,output,"eyes")
            manifest["eyes"][build][eye] = record(output)
        output = OUT / f"{build.lower()}-smile.glb"
        revise_features(ROOT/SOURCES["mouth"][build],output,"mouth")
        manifest["mouth"][build] = record(output)
    headgear = OUT / "knit-beanie.glb"
    beanie_mesh(headgear)
    hat = updos.surface(headgear)
    hat_url = record(headgear)
    pins = {}
    for build, styles in SOURCES["headwear"].items():
        manifest["beanie"][build] = {}
        for hair, source in styles.items():
            source_hat, source_pin = ROOT/source["headgear"], ROOT/source["extra"]
            key = (sha256(source_hat.read_bytes()).digest(),sha256(source_pin.read_bytes()).digest())
            if key not in pins:
                pin = OUT / f"beanie-sprout-{build.lower()}-{hair}.glb"
                pin_sprout(source_pin,pin,updos.surface(source_hat),hat)
                pins[key] = record(pin)
            manifest["beanie"][build][hair] = {"headgear":hat_url,"sprout":pins[key]}
    pony = SOURCES["ponytail"]
    pose, evidence = pose_ponytail(ROOT/pony["default"]["bare"],ROOT/pony["default"]["covered"],hat)
    worn = manifest["beanie"]["Feminine"]["ponytail"]
    worn["tail"] = {}
    for color, sources in pony.items():
        temporary = OUT / f".posed-{color}.glb"
        output = OUT / f"beanie-ponytail-{color}.glb"
        updos.write_pose(ROOT/sources["bare"],temporary,"ponytail",pose)
        isolate(temporary,output,attachment)
        temporary.unlink()
        tail = updos.surface(output)
        assert not tail.overlap(hat), color
        assert tail.overlap(updos.surface(ROOT/sources["covered"],fitted_crown)), color
        worn["tail"][color] = record(output)
    (REV/"art.json").write_text(json.dumps(manifest,indent=2)+"\n",newline="\n")
    (REV/"verification/geometry.json").write_text(json.dumps({"ponytail":evidence,"assets":ASSETS},indent=2)+"\n",newline="\n")
    print("309 components written", len(ASSETS), evidence, flush=True)


if __name__ == "__main__":
    main()
