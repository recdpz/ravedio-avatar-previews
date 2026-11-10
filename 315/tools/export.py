"""Export the 314 catalogue with embedded Aero PBR materials and untouched geometry."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import struct
import zlib

ROOT = Path(__file__).resolve().parents[1]


def write_json(path, value):
    path.write_text(json.dumps(value,sort_keys=True,indent=2)+"\n",encoding="utf8",newline="\n")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def components(catalogue):
    roles = defaultdict(set)

    def add(row):
        for role, path in row.items():
            if path:
                roles[path].add(role)

    for row in catalogue["rows"].values():
        add(row)
    for build in catalogue["builds"].values():
        for group in ("faces","glasses"):
            for row in build[group].values():
                add(row)
        for group, role in (("grooms","groom"),("bottoms","bottom")):
            for path in build[group].values():
                add({role:path})
        for row in build["bases"].values():
            for path in row.values():
                add({"base":path})
        add({"extra":build["hot"]})
    for case in catalogue["cases"].values():
        add(case["parts"])
    result = {}
    for path, options in sorted(roles.items()):
        assert options <= {"extra","sprout"} or len(options) == 1, (path,options)
        result[path] = "sprout" if "sprout" in options else next(iter(options))
    return result


def read_glb(data):
    magic, version, total, length, kind = struct.unpack_from("<4sIIII",data)
    assert (magic,version,total,kind) == (b"glTF",2,len(data),0x4E4F534A)
    doc = json.loads(data[20:20+length])
    count,kind = struct.unpack_from("<II",data,20+length)
    assert kind == 0x004E4942 and len(data) == 28+length+count
    assert len(doc["buffers"]) == 1 and not doc["buffers"][0].get("uri")
    return doc, data[28+length:]


def write_glb(doc, binary):
    js = json.dumps(doc,separators=(",",":"),ensure_ascii=False).encode()
    js += b" "*(-len(js)%4)
    return struct.pack("<4sIIII",b"glTF",2,28+len(js)+len(binary),len(js),0x4E4F534A)+js+struct.pack(
        "<II",len(binary),0x004E4942)+binary


def png_map(depth, repeat):
    # Periodic weave values in glTF's green roughness channel. Blue leaves
    # the scalar metallic input intact. Use no external PNG dependencies.
    width = 64
    raw = bytearray()
    for y in range(width):
        raw.append(0)
        for x in range(width):
            u = math.cos(2*math.pi*x*repeat[0]/width)
            v = math.cos(2*math.pi*y*repeat[1]/width)
            raised = .5+.24*u+.19*v+.07*u*v
            raw.extend((255,round(255*(1-depth*raised)),255))

    def chunk(tag, data):
        return struct.pack(">I",len(data))+tag+data+struct.pack(">I",zlib.crc32(tag+data))

    return b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",struct.pack(">IIBBBBB",width,width,8,2,0,0,0))+chunk(
        b"IDAT",zlib.compress(bytes(raw)))+chunk(b"IEND",b"")


def texture(doc, binary, data, name):
    views = doc.setdefault("bufferViews",[])
    images = doc.setdefault("images",[])
    samplers = doc.setdefault("samplers",[])
    textures = doc.setdefault("textures",[])
    image, view, sampler, index = len(images),len(views),len(samplers),len(textures)
    views.append({"buffer":0,"byteOffset":len(binary),"byteLength":len(data)})
    binary.extend(data)
    binary.extend(b"\0"*(-len(binary)%4))
    doc["buffers"][0]["byteLength"] = len(binary)
    images.append({"bufferView":view,"mimeType":"image/png","name":f"Aero {name} roughness"})
    samplers.append({"wrapS":10497,"wrapT":10497,"minFilter":9987,"magFilter":9729})
    textures.append({"source":image,"sampler":sampler})
    return index


def classify(role, name):
    if name.startswith(("Skin","Chest / shade191")):
        return "skin"
    n = name.lower()
    if role in {"lashes","mouth","nose"} or "ink" in n:
        return "ink"
    if role == "eyes":
        return "eye" if "charcoal" in n else "catchlight"
    if role == "glasses":
        return "hardware" if "metal" in n else "frame"
    if role == "sprout":
        return "hardware" if "clip" in n else "sprout"
    if role == "extra":
        return "sticker"
    if role == "groom":
        return "stubble" if "stubble" in n else "groom"
    if role in {"hair","hairLengths"}:
        if "fade" in n or "buzz" in n:
            return "fade"
        return "hardware" if "tie" in n else "hair"
    if re.search(r"button|emblem|crystal|iridescent|graphite facets|zipper", n):
        return "hardware"
    if "jersey" in n:
        return "jersey"
    if any(word in n for word in ("beanie","knit","ribbed","sweatshirt","hoodie")):
        return "knit"
    if any(word in n for word in ("woven","pashmina","bandana","cotton","cowboy","fringe","face edge239")):
        return "woven"
    return "cloth"


def surface(material, values):
    roughness, metallic, coat, coat_roughness, specular = values
    pbr = material.setdefault("pbrMetallicRoughness",{})
    pbr["roughnessFactor"] = roughness
    if metallic is not None:
        pbr["metallicFactor"] = metallic
    ext = material.setdefault("extensions",{})
    clearcoat = ext.setdefault("KHR_materials_clearcoat",{})
    clearcoat.update(clearcoatFactor=coat,clearcoatRoughnessFactor=coat_roughness)
    ext.setdefault("KHR_materials_specular",{})["specularFactor"] = specular


def linear(color):
    rgb = [int(color[i:i+2],16)/255 for i in (1,3,5)]
    return [round(c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4,8) for c in rgb]


def convert(data, role, recipe, maps, tint=None):
    doc, source_bin = read_glb(data)
    binary = bytearray(source_bin)
    meshes = json.dumps(doc["meshes"],sort_keys=True)
    view_count = len(doc["bufferViews"])
    image_count = len(doc.get("images",[]))
    texture_indices = {}
    slots = defaultdict(list)
    for mesh in doc["meshes"]:
        for primitive in mesh["primitives"]:
            slots[primitive.get("material")].append(primitive["attributes"])
    stats = Counter()
    for index,material in enumerate(doc["materials"]):
        if tint:
            choice = recipe["lenses"][tint]
            surface(material,choice["surface"])
            material["pbrMetallicRoughness"]["baseColorFactor"] = linear(choice["srgb"])+[choice["alpha"]]
            material["alphaMode"] = "BLEND"
            material["doubleSided"] = False
            ext = material["extensions"]
            ext["KHR_materials_ior"] = {"ior":1}
            ext.pop("KHR_materials_transmission",None)
            ext.pop("KHR_materials_volume",None)
            stats["lens_"+tint] += 1
            continue
        kind = classify(role,material.get("name",""))
        surface(material,recipe["surfaces"][kind])
        stats[kind] += 1
        pbr = material["pbrMetallicRoughness"]
        if (kind in maps and "metallicRoughnessTexture" not in pbr and slots[index]
            and all("TEXCOORD_0" in attrs for attrs in slots[index])):
            if kind not in texture_indices:
                texture_indices[kind] = texture(doc,binary,maps[kind],kind)
            pbr["metallicRoughnessTexture"] = {"index":texture_indices[kind]}
            stats["textured_materials"] += 1
    used = {ext for m in doc["materials"] for ext in m.get("extensions",{})}
    doc["extensionsUsed"] = sorted(used | set(doc.get("extensionsUsed",[])))
    output = write_glb(doc,bytes(binary))

    # Verify the actual bytes to be handed off. New buffer views and images
    # can be appended, but original material-independent data must match.
    check, check_bin = read_glb(output)
    original,_ = read_glb(data)
    assert check_bin[:len(source_bin)] == source_bin
    assert json.dumps(check["meshes"],sort_keys=True) == meshes
    assert check["bufferViews"][:view_count] == original["bufferViews"]
    assert check.get("images",[])[:image_count] == original.get("images",[])
    for key in ("nodes","accessors","scene","scenes","animations","skins"):
        assert check.get(key) == original.get(key), key
    for before,after in zip(original["materials"],check["materials"]):
        if tint is None:
            assert before.get("alphaMode") == after.get("alphaMode")
            assert before.get("pbrMetallicRoughness",{}).get("baseColorFactor") == after["pbrMetallicRoughness"].get("baseColorFactor")
    return output,stats


def write_catalogue(output, source, mapping):
    def bind(value):
        if isinstance(value,dict):
            return {key:bind(part) for key,part in value.items()}
        return mapping[value] if value else None

    index = {
        "schema":"ravedio-art-catalogue-1",
        "revision":315,
        "fit_selector":["build","hair","headwear","top","baked_hair_finish"],
        "coordinates":"+Y up, +Z forward. Preserve authored transforms and independent roles.",
        "fit_rows":bind(source["rows"]),
        "independent_roles":bind(source["builds"]),
        "options":source["options"],
        "components":{},
        "palette":"palette.json",
        "studio":"studio.json",
        "finish":"finish.json",
    }
    for value in mapping.values():
        for content in value.values() if isinstance(value,dict) else (value,):
            file = output/(content+".glb")
            index["components"][content] = {"file":file.name,"bytes":file.stat().st_size}
    for name in ("studio.json","finish.json"):
        shutil.copyfile(ROOT/name,output/name)
    shutil.copyfile(ROOT.parent/"235/face-palette209.json",output/"palette.json")
    legacy = output/"jersey-dyes"
    legacy.mkdir(exist_ok=True)
    for path in (ROOT.parent/"213/colors").glob("jersey-*.png"):
        shutil.copyfile(path,legacy/path.name)
    wardrobe = json.loads((ROOT.parent/"308/wardrobe.json").read_bytes())
    dyes = {}
    for key,relative in wardrobe["Feminine"]["jersey"]["atlases"].items():
        source_file = ROOT.parent/"308"/relative
        dest = legacy/("feminine-"+source_file.name)
        shutil.copyfile(source_file,dest)
        dyes[key] = dest.relative_to(output).as_posix()
    index["feminine_jersey_dyes"] = dyes
    index["shared_jersey_dyes_dir"] = "jersey-dyes"
    write_json(output/"catalogue.json",index)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output",type=Path)
    parser.add_argument("--source-mount",type=Path,action="append",default=[])
    args = parser.parse_args()
    art = ROOT.parent
    source_roots = [art.resolve(), *(p.resolve() for p in args.source_mount)]
    recipe = json.loads((ROOT/"finish.json").read_bytes())
    catalogue = json.loads((ROOT/"catalogue-input.json").read_bytes())
    inputs = components(catalogue)
    assert len(inputs) == 611 and len(catalogue["rows"]) == 1792
    args.output.mkdir(parents=True,exist_ok=True)
    maps = {key:png_map(**value) for key,value in recipe["roughness_maps"].items()}
    mapping, counts, roles = {},Counter(),Counter()
    receipts = {}
    for relative,role in inputs.items():
        safe = Path(relative)
        assert not safe.is_absolute() and ".." not in safe.parts and safe.suffix == ".glb"
        source = (art/safe).resolve()
        assert any(root in source.parents for root in source_roots), source
        data = source.read_bytes()
        original = digest(data)
        versions = {}
        for tint in (("clear","dark") if role=="lenses" else (None,)):
            blob, stats = convert(data,role,recipe,maps,tint)
            content = digest(blob)
            destination = args.output/(content+".glb")
            if not destination.exists() or digest(destination.read_bytes()) != content:
                destination.write_bytes(blob)
            counts.update(stats)
            roles[role] += 1
            versions[tint or "default"] = content
        mapping[relative] = versions if role=="lenses" else versions["default"]
        receipts[relative] = {"role":role,"input_sha256":original,"exports":versions}
    asset_map = {"schema":1,"art_revision":315,"components":mapping}
    write_json(ROOT/"asset-map.json",asset_map)
    record = {"art_revision":315,"source_revision":314,"resolved_fits":len(catalogue["rows"]),
              "source_components":len(inputs),"variant_exports":sum(roles.values()),
              "unique_glbs":len({c for r in receipts.values() for c in r["exports"].values()}),
              "roles":dict(roles),"materials":dict(counts),"geometry_and_original_buffers_verified":True}
    write_json(ROOT/"verification/assets.json",record)
    write_json(args.output/"receipt.json",{**record,"source_components_by_path":receipts})
    write_catalogue(args.output,catalogue,mapping)
    print(record,flush=True)


if __name__ == "__main__":
    main()
