"""Export small, shape-preserving Aero Gloss assemblies from actual 314 GLBs."""
from collections import Counter
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/"315/tools"))
from export import classify, digest, linear, read_glb, surface, write_glb, write_json

CASES = ("curls-pashmina","flow-cap","flow-cap-bare-eyes","ponytail-beanie-jersey")


def selections(catalogue):
    result = {key:catalogue["cases"][key] for key in CASES}
    ponytail = result["ponytail-beanie-jersey"]
    ponytail["features"].update(topColor="default",detail="sprout")
    row = "Feminine/ponytail/beanie/jersey/ombre"
    ponytail["parts"]["extra"] = catalogue["rows"][row]["sprout"]
    assert ponytail["parts"]["extra"]
    return result


def revise(data,role,recipe,tint):
    gltf,binary = read_glb(data)
    original,_ = read_glb(data)
    changes = Counter()
    for material in gltf["materials"]:
        name = material.get("name","")
        if role=="lenses":
            lens = recipe["lenses"][tint]
            surface(material,lens["surface"])
            material["pbrMetallicRoughness"]["baseColorFactor"] = linear(lens["srgb"])+[lens["alpha"]]
            material["alphaMode"] = "BLEND"
            material["doubleSided"] = False
            ext = material["extensions"]
            ext["KHR_materials_ior"] = {"ior":1}
            ext.pop("KHR_materials_transmission",None)
            ext.pop("KHR_materials_volume",None)
            changes["lens_"+tint] += 1
        else:
            kind = classify(role,name)
            if kind in recipe["surfaces"]:
                surface(material,recipe["surfaces"][kind])
                changes[kind] += 1
    if changes:
        used = {ext for m in gltf["materials"] for ext in m.get("extensions",{})}
        gltf["extensionsUsed"] = sorted(used | set(gltf.get("extensionsUsed",[])))
    candidate = write_glb(gltf,binary) if changes else data
    check,output_bin = read_glb(candidate)
    assert output_bin==binary
    assert all(check.get(key)==original.get(key) for key in original if key not in ("materials","extensionsUsed"))
    for a,b in zip(original["materials"],check["materials"]):
        assert a.get("name")==b.get("name")
        if role!="lenses":
            assert a.get("alphaMode")==b.get("alphaMode")
            assert a.get("pbrMetallicRoughness",{}).get("baseColorFactor")==b.get("pbrMetallicRoughness",{}).get("baseColorFactor")
    return candidate,changes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output",type=Path)
    parser.add_argument("--source-mount",type=Path,required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    assets = output/"assets"
    assets.mkdir(parents=True,exist_ok=True)
    catalogue = json.loads((ROOT.parent/"315/catalogue-input.json").read_bytes())
    assert catalogue["revision"]==314
    recipe = json.loads((ROOT/"finish.json").read_bytes())
    source_roots = (ROOT.parent.resolve(),args.source_mount.resolve())
    cases, parts, changed = {}, {}, set()
    for key, item in selections(catalogue).items():
        bindings = {}
        for role,path in item["parts"].items():
            if not path:
                continue
            relative = Path(path)
            assert not relative.is_absolute() and ".." not in relative.parts and relative.suffix==".glb"
            source = (ROOT.parent/relative).resolve()
            assert any(root in source.parents for root in source_roots)
            data = source.read_bytes()
            tint = item["features"]["lensTint"] if role=="lenses" else None
            blob,changes = revise(data,"sprout" if role=="extra" and item["features"]["detail"]=="sprout" else role,recipe,tint)
            before,after = digest(data),digest(blob)
            target = assets/(after+".glb")
            target.write_bytes(blob)
            assert digest(target.read_bytes()) == after
            bindings[role] = {"file":target.name,"source":path,"source_sha256":before,"sha256":after}
            parts[after] = {"bytes":len(blob),"materials":dict(changes)}
            if before!=after:
                changed.add(after)
        cases[key] = {**item,"parts":bindings}
    write_json(output/"source-receipt.json",{
        "schema":"ravedio-gloss-source-samples-1",
        "reference_revision":314,"review_revision":316,"cases":cases,"glbs":parts,
        "changed_glbs":len(changed),"geometry_and_texture_bytes_verified":True,
    })
    print(f"Verified {len(parts)} GLBs for {len(cases)} assemblies, {len(changed)} with embedded material changes",flush=True)


if __name__=="__main__":
    main()
