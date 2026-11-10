"""Bake the shared chestnut dye into the fitted source catalogue."""
from argparse import ArgumentParser
from collections import defaultdict
from copy import deepcopy
from functools import lru_cache
import importlib.util
from io import BytesIO
import json
import os
from pathlib import Path
import shutil
import sys

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"315/tools"))
from export import digest, linear, read_glb, write_glb, write_json

spec = importlib.util.spec_from_file_location("gloss316",ROOT/"316/tools/source.py")
gloss = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gloss)

BROWN = "#594033"
NEW = np.array(linear(BROWN))
OLD = np.array([.160,.059,.030])
OMBRE = np.array([.145,.062,.034])
LUMA = np.array([.2126,.7152,.0722])
HARDWARE = ("tie","band","elastic","metal")


def json_file(path):
    return json.loads(path.read_bytes())


def root_shift(rgb, root):
    # Fade the change out before the authored caramel band.
    distance = (rgb-root)@LUMA
    t = np.clip(distance/.117,0,1)
    weight = 1-t*t*(3-2*t)
    return np.clip(rgb+(NEW-root)*weight[...,None],0,1)


def append(doc, binary, data, **fields):
    views = doc["bufferViews"]
    views.append({"buffer":0,"byteOffset":len(binary),"byteLength":len(data),**fields})
    binary.extend(data)
    binary.extend(b"\0"*(-len(binary)%4))
    return len(views)-1


def color_vertices(doc,binary,index):
    accessor = doc["accessors"][index]
    view = doc["bufferViews"][accessor["bufferView"]]
    width = {"VEC3":3,"VEC4":4}[accessor["type"]]
    assert accessor["componentType"]==5126 and "sparse" not in accessor
    start = view.get("byteOffset",0)+accessor.get("byteOffset",0)
    values = np.ndarray((accessor["count"],width),dtype="<f4",buffer=binary,
                        offset=start,strides=(view.get("byteStride",width*4),4)).copy()
    before = values[:,:3].copy()
    values[:,:3] = root_shift(before,OMBRE)
    if np.array_equal(before,values[:,:3]):
        return index
    updated = {k:v for k,v in accessor.items() if k not in ("bufferView","byteOffset","min","max")}
    updated["bufferView"] = append(doc,binary,values.tobytes(),target=34962)
    doc["accessors"].append(updated)
    return len(doc["accessors"])-1


@lru_cache(maxsize=8)
def ombre_image(data, ponytail):
    with Image.open(BytesIO(data)) as image:
        values = np.array(image.convert("RGBA"))
        srgb = values[:,:,:3].astype(float)/255
    rgb = np.where(srgb<=.04045,srgb/12.92,((srgb+.055)/1.055)**2.4)
    rgb = root_shift(rgb,OLD if ponytail else OMBRE)
    srgb = np.where(rgb<=.0031308,rgb*12.92,1.055*rgb**(1/2.4)-.055)
    values[:,:,:3] = np.rint(srgb*255).astype("uint8")
    out = BytesIO()
    Image.fromarray(values).save(out,format="PNG",optimize=True)
    return out.getvalue()


def dye(blob, role, finish):
    doc,original = read_glb(blob)
    before = deepcopy(doc)
    binary = bytearray(original)
    dyed,images,colors = set(),set(),{}
    for index,material in enumerate(doc["materials"]):
        name = material["name"].lower()
        if role=="groom":
            if not name.startswith("groom / ") or "stubble" in name:
                continue
        elif not name.startswith("hair") or any(word in name for word in HARDWARE):
            continue
        pbr = material["pbrMetallicRoughness"]
        old_factor = pbr.get("baseColorFactor",[1,1,1,1])
        if finish!="ombre" or "ombre" not in name:
            source = OMBRE if finish=="ombre" else OLD
            pbr["baseColorFactor"] = [*np.minimum(1,np.array(old_factor[:3])*NEW/source).tolist(),old_factor[3]]
            if "hairBase252" in material.get("extras",{}):
                material["extras"]["hairBase252"] = pbr["baseColorFactor"]
        elif texture := pbr.get("baseColorTexture"):
            image = doc["textures"][texture["index"]]["source"]
            if image not in images:
                source = doc["images"][image]
                assert source["mimeType"]=="image/png"
                view = doc["bufferViews"][source["bufferView"]]
                start = view.get("byteOffset",0)
                data = original[start:start+view["byteLength"]]
                replacement = ombre_image(data,"ponytail" in source.get("name","").lower())
                source["bufferView"] = append(doc,binary,replacement)
                images.add(image)
        else:
            for mesh in doc["meshes"]:
                for primitive in mesh["primitives"]:
                    if primitive.get("material")!=index:
                        continue
                    attrs = primitive["attributes"]
                    color = attrs["COLOR_0"]
                    if color not in colors:
                        colors[color] = color_vertices(doc,binary,color)
                    attrs["COLOR_0"] = colors[color]
        dyed.add(index)
    if not dyed:
        return blob,0
    doc["buffers"][0]["byteLength"] = len(binary)
    # Every original geometry, UV, texture, and transform byte remains intact.
    assert binary[:len(original)] == original
    for key in ("nodes","scenes","scene","skins","animations"):
        assert doc.get(key)==before.get(key)
    for old_mesh,new_mesh in zip(before["meshes"],doc["meshes"],strict=True):
        for a,b in zip(old_mesh["primitives"],new_mesh["primitives"],strict=True):
            assert a.get("indices")==b.get("indices")
            assert {k:v for k,v in a["attributes"].items() if k!="COLOR_0"} == {
                k:v for k,v in b["attributes"].items() if k!="COLOR_0"}
    return write_glb(doc,bytes(binary)),len(dyed)


def main():
    parser = ArgumentParser(description=__doc__)
    for name in ("output","catalogue315","source317","source318","source319"):
        parser.add_argument(name,type=Path)
    args = parser.parse_args()
    assets = args.output/"assets"
    assets.mkdir(parents=True,exist_ok=True)
    selection = json_file(ROOT/"315/catalogue-input.json")
    old_map = json_file(ROOT/"315/asset-map.json")["components"]
    catalogue = json_file(args.catalogue315/"catalogue.json")
    recipe = json_file(ROOT/"316/finish.json")
    latest = json_file(args.source317/"source.json")["replacement_assets"]
    long = json_file(args.source319/"source.json")["cases"]["long"]
    short = json_file(args.source318/"source.json")["cases"]["short"]
    roles = {}
    for key,row in selection["rows"].items():
        finish = key.rsplit("/",1)[-1]
        for role in ("hair","hairLengths"):
            if path := row[role]:
                previous = roles.setdefault(path,(role,finish))
                assert previous[1]==finish, (key,path)
    for name,path in selection["builds"]["Masculine"]["grooms"].items():
        if path:
            roles[path] = ("groom","default")
    special_grooms = {
        selection["builds"]["Masculine"]["grooms"]["long"]:args.source319/"assets"/long["groom"],
        selection["builds"]["Masculine"]["grooms"]["short"]:args.source318/"assets"/short["groom"],
    }
    replacements,remap,counts = {},{},defaultdict(int)
    files = {}

    def record(data):
        key = digest(data)
        filename = key+".glb"
        target = assets/filename
        if not target.exists():
            target.write_bytes(data)
        assert digest(target.read_bytes())==key
        files[key] = {"file":"assets/"+filename,"bytes":len(data)}
        return key

    for source,(role,finish) in sorted(roles.items()):
        older = old_map[source]
        if source in special_grooms:
            base = special_grooms[source].read_bytes()
        elif source in latest:
            base = (args.source317/"assets"/latest[source]["file"]).read_bytes()
        else:
            base = (args.catalogue315/(older+".glb")).read_bytes()
            base,_ = gloss.revise(base,role,recipe,None)
        revised,count = dye(base,role,finish)
        counts[finish] += count
        key = record(revised)
        assert remap.setdefault(older,key)==key, source
        replacements[source] = key
    for source,part in latest.items():
        if source not in replacements:
            key = record((args.source317/"assets"/part["file"]).read_bytes())
            assert remap.setdefault(old_map[source],key)==key, source
            replacements[source] = key

    paired = record((args.source319/"assets"/long["mouth"]).read_bytes())
    grooms = {"short":paired,"long":paired}

    def bind(tree):
        if isinstance(tree,dict):
            return {k:bind(v) for k,v in tree.items()}
        return remap.get(tree,tree)

    for field in ("fit_rows","independent_roles"):
        catalogue[field] = bind(catalogue[field])
    def linked_parts(tree):
        for value in tree.values():
            if isinstance(value,dict):
                yield from linked_parts(value)
            elif value is not None:
                yield value

    required = set(linked_parts(catalogue["fit_rows"])) | set(linked_parts(catalogue["independent_roles"]))
    for key in sorted(required-files.keys()):
        entry = catalogue["components"][key]
        source = args.catalogue315/entry["file"]
        target = assets/entry["file"]
        if not target.exists():
            try:
                os.link(source,target)
            except OSError:
                shutil.copyfile(source,target)
        assert target.stat().st_size == entry["bytes"], key
        files[key] = {**entry,"file":"assets/"+target.name}
    catalogue.update(revision=320,components=files,groom_mouths=grooms,
                     brown_srgb=BROWN,brown_linear=NEW.tolist())
    for field in ("palette","studio"):
        name = catalogue[field]
        shutil.copyfile(args.catalogue315/name,args.output/name)
    finish = json_file(args.catalogue315/catalogue["finish"])
    finish["surfaces"].update({key:recipe["surfaces"][key] for key in ("hair","groom")})
    finish["scope"] = "320 source catalogue. Hair uses Aero Gloss; connected beard finishes follow 318 and 319."
    write_json(args.output/catalogue["finish"],finish)
    directory = catalogue["shared_jersey_dyes_dir"]
    shutil.copytree(args.catalogue315/directory,args.output/directory,dirs_exist_ok=True)
    for row in catalogue["options"]["colors"]["hair"]:
        if row[0] in ("default","darkbrown"):
            row[2] = BROWN
    write_json(args.output/"catalogue.json",catalogue)
    write_json(args.output/"overlay.json",{"brownSrgb":BROWN,"components":replacements,"groomMouth":grooms})
    write_json(args.output/"receipt.json",{"revision":320,"fit_rows":len(selection["rows"]),
        "hair_paths":len(roles)-len(selection["builds"]["Masculine"]["grooms"])+1,
        "groom_paths":len(selection["builds"]["Masculine"]["grooms"])-1,
        "dyed_materials":dict(counts),"replacement_paths":len(replacements),
        "unique_local_glbs":len({*replacements.values(),paired})})
    print(f"Resolved {len(selection['rows'])} fit rows and baked {len(replacements)} replacement paths.",flush=True)


if __name__=="__main__":
    main()
