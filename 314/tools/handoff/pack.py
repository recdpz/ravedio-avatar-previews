"""Build a content-addressed 314 overlay and four staged native A/B assemblies."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import random
import shutil
import struct
import sys
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[3]
BASE_ARCHIVE = "4f1646c67e144404231494976240fb4b8ab3be6fd665044d8622c0594f0a8d9d"
ART_COMMIT = "ab3af975b5981627ed97b0d3309ad227d64ec12e"


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream,"sha256").hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,sort_keys=True,indent=2)+"\n",encoding="utf8",newline="\n")


def archive(source,target):
    with ZipFile(target,"x",compression=ZIP_DEFLATED,compresslevel=4) as zip_:
        for path in sorted(source.rglob("*")):
            if path.is_file():
                zip_.write(path,path.relative_to(source).as_posix())
    with ZipFile(target) as zip_:
        assert zip_.testzip() is None
    digest = sha(target)
    target.with_suffix(".zip.sha256").write_text(f"{digest}  {target.name}\n",encoding="ascii")
    return digest


def source(name):
    p = ROOT/name
    if not name.endswith(".glb") or Path(name).is_absolute() or ".." in Path(name).parts or not p.is_file():
        raise ValueError("Invalid preview asset "+name)
    return p


def seed(fits,faces):
    rng = random.Random(314)
    cohort = {}
    for key in sorted(fits):
        build,hair,*_ = key.split("/")
        cohort.setdefault((build,hair),[]).append(key)
    looks = []
    for (build,_),variants in cohort.items():
        for key in rng.sample(variants,8):
            index = len(looks)
            eyes = tuple(sorted(faces[build]["faces"]))
            looks.append({"id":f"r314-look-{index:03d}","selector":key,"skin":index%4,
                "eyes":eyes[index%len(eyes)],"glasses":("reading" if index%8==3 else
                    "wayfarer" if index%8==7 else "none"),
                "lensTint":"clear" if index%8==3 else "dark","detail":"none",
                "bottom":"pants","topColor":"default","headgearColor":"default","frameColor":"black"})
    rng.shuffle(looks)
    messages = [{"id":f"row-{index:04d}","appearance":look["id"],"arrival_ms":index*125}
                for index,look in enumerate(looks*4)]
    return {"schema":"ravedio-catalogue-workload-1","name":"314-catalogue-churn",
            "appearance_count":len(looks),"messages":messages,"appearances":looks}


def catalogue(before,after,base,out):
    assert sha(base)==BASE_ARCHIVE
    with ZipFile(base) as archive_:
        canonical = json.loads(archive_.read("catalogue.json"))
        assert canonical["revision"]==308
        baseline_catalogue = hashlib.sha256(archive_.read("catalogue.json")).hexdigest()
    assets,hashes = {},{}

    def bind(path):
        if path is None:
            return None
        if path not in hashes:
            hashes[path] = sha(source(path))
        digest = hashes[path]
        if digest not in canonical["components"]:
            if digest not in assets:
                dst = out/f"components/{digest}.glb"
                dst.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(source(path),dst)
                assets[digest] = {"file":dst.relative_to(out).as_posix(),"bytes":dst.stat().st_size,"sources":[]}
            if path not in assets[digest]["sources"]:
                assets[digest]["sources"].append(path)
        return digest

    def changes(old,new,prior):
        assert old.keys()==new.keys()==prior.keys()
        result = {}
        for key,value in new.items():
            if isinstance(value,dict):
                child = changes(old[key],value,prior[key])
                if child:
                    result[key] = child
            else:
                assert bind(old[key])==prior[key],key
                digest = bind(value)
                if digest!=prior[key]:
                    result[key] = digest
        return result

    rows = changes(before["rows"],after["rows"],canonical["fit_rows"])
    roles = changes(before["builds"],after["builds"],canonical["independent_roles"])
    assert set(roles)=={"Feminine","Masculine"}
    assert all(set(value)=={"faces"} for value in roles.values())
    expected = Counter(role for row in rows.values() for role in row)
    assert set(expected)<= {"hair","hairLengths","headgear","sprout"}
    material = {"dark":{"opacity":.74},
                "clear":{"opacity":.075,"roughness":.075,"clearcoat":.025,"specularIntensity":.20},
                "transmission":0,"ior":1,"alpha_mode":"BLEND","depth_write":False}
    write(out/"delta.json",{"schema":"ravedio-catalogue-delta-2","revision":314,"artwork_commit":ART_COMMIT,
        "base_archive_sha256":BASE_ARCHIVE,"base_catalogue_sha256":baseline_catalogue,
        "fit_selector":canonical["fit_selector"],"fit_rows":rows,"independent_roles":roles,"components":assets,
        "lens_overrides":material,"source_files":{name:sha(ROOT/name) for name in after["sourceFiles"]},
        "resolved_fit_rows":len(after["rows"]),"changed_fit_rows":len(rows),"changed_roles":dict(expected)})
    write(out/"catalogue-workload.json",seed(after["rows"],after["builds"]))
    print("Delta",len(rows),"fit rows,",len(assets),"new GLBs,",dict(expected),flush=True)


def encode_glb(doc,remaining):
    data = json.dumps(doc,separators=(",",":")).encode()
    data += b" "*(-len(data)%4)
    return (struct.pack("<4sII",b"glTF",2,20+len(data)+len(remaining))+
            struct.pack("<II",len(data),0x4E4F534A)+data+remaining)


def triangles(doc):
    return sum(doc["accessors"][part["indices"]]["count"]//3 for mesh in doc["meshes"]
               for part in mesh["primitives"])


def native(before,after,baseline,out,delta_sha):
    from stage_r308 import prepare as stage
    from stage_r298 import colors_for_skin,document
    out.mkdir(parents=True)
    write(out/"fixtures/index.json",{"scenarios":[]})
    write(out/"receipt.json",{})
    stage(baseline,out)
    runtime_path = out/"r308/runtime.json"
    runtime = read(runtime_path)
    palette = read(baseline/"palette.json")
    audit = {"schema":"ravedio-native-candidate-1","revision":314,"artwork_commit":ART_COMMIT,
             "base_runtime_sha256":sha(runtime_path),"catalogue_delta_sha256":delta_sha,"changes":{}}
    for key,case in after["cases"].items():
        if not case["native"]:
            continue
        identity = case["baseline_scene"]
        old = before["cases"][key]
        entry = runtime["assemblies"][identity]
        assert {p["role"] for p in entry["parts"]}==set(case["parts"])==set(old["parts"])
        materials,changes = [],{}
        for part in entry["parts"]:
            role = part["role"]
            target = out/"r308"/part["file"]
            blob = target.read_bytes()
            if case["parts"][role]!=old["parts"][role]:
                path = source(case["parts"][role])
                blob = path.read_bytes()
                part["source_sha256"] = sha(path)
            doc,remaining = document(blob)
            if role=="lenses":
                for lens in doc["materials"]:
                    pbr = lens["pbrMetallicRoughness"]
                    if case["features"]["lensTint"]=="clear":
                        pbr["roughnessFactor"] = .075
                        extensions = lens.setdefault("extensions",{})
                        extensions.setdefault("KHR_materials_clearcoat",{})["clearcoatFactor"] = .025
                        extensions.setdefault("KHR_materials_specular",{})["specularFactor"] = .20
                        used = doc.setdefault("extensionsUsed",[])
                        for name in ("KHR_materials_clearcoat","KHR_materials_specular"):
                            if name not in used:
                                used.append(name)
                    else:
                        pbr["baseColorFactor"][3] = .74
                blob = encode_glb(doc,remaining)
            assert 20<len(blob)<8*1024*1024
            assert not (doc.get("skins") or doc.get("animations") or doc.get("extensionsRequired"))
            assert all(not image.get("uri") and image.get("mimeType")=="image/png" for image in doc.get("images",[]))
            digest = hashlib.sha256(blob).hexdigest()
            if digest!=part["sha256"]:
                changes[role] = {"before":part["sha256"],"after":digest}
                target.write_bytes(blob)
                part.update(bytes=len(blob),sha256=digest,triangles=triangles(doc))
            materials.extend(doc["materials"])
        assert sum(p["bytes"] for p in entry["parts"])<32*1024*1024
        entry["colors"] = {str(skin):colors_for_skin(materials,palette,skin) for skin in range(4)}
        entry["no_depth_write"] = sorted({m["name"] for m in materials if m.get("alphaMode")=="BLEND"})
        audit["changes"][identity] = changes
    write(out/"native-stage.json",audit)
    runtime.update(art_revision=314,archive_sha256=delta_sha,stage_sha256=sha(out/"native-stage.json"))
    write(runtime_path,runtime)
    write(out/"r308/receipt.json",{"art_revision":314,"runtime_sha256":sha(runtime_path),
          "archive_sha256":delta_sha,"stage_sha256":runtime["stage_sha256"],"phone_qualified":False})
    (out/"receipt.json").unlink()
    (out/"fixtures/index.json").unlink()
    print("Staged revision 314 runtime",sha(runtime_path),flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("before","after","catalogue","fixtures","mobile_tools","work","delivery"):
        p.add_argument(name,type=Path)
    a = p.parse_args()
    sys.path.insert(0,str(a.mobile_tools))
    before,after = read(a.before),read(a.after)
    target = a.work/"catalogue"
    target.mkdir(parents=True)
    catalogue(before,after,a.catalogue,target)
    write(target/"manifest.json",{"schema":"ravedio-catalogue-delta-archive-1",
        "files":{p.relative_to(target).as_posix():sha(p) for p in sorted(target.rglob("*")) if p.is_file()}})
    delta_sha = archive(target,a.delivery/"Ravedio314-catalogue-delta.zip")
    native(before,after,a.fixtures,a.work/"native",delta_sha)


if __name__=="__main__":
    main()
