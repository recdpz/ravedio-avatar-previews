"""Verify a 314 phone archive or replay its catalogue overlay on the 308 index."""
import argparse
import hashlib
from io import BytesIO
import json
from pathlib import Path, PurePosixPath
from zipfile import ZipFile


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream,"sha256").hexdigest()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def verified(zip_):
    names = zip_.namelist()
    assert len(names)==len(set(names))
    assert all(not PurePosixPath(name).is_absolute() and ".." not in PurePosixPath(name).parts
               and "\\" not in name for name in names)
    manifest = json.loads(zip_.read("manifest.json"))
    files = manifest["files"]
    assert set(files)==set(names)-{"manifest.json"}
    for name,expected in files.items():
        with zip_.open(name) as stream:
            assert hashlib.file_digest(stream,"sha256").hexdigest()==expected,name
    return manifest


def overlay(base,delta,index):
    with ZipFile(delta) as delta_zip:
        receipt = verified(delta_zip)
        assert receipt["schema"]=="ravedio-catalogue-delta-archive-1"
        changes = json.loads(delta_zip.read("delta.json"))
        assert changes["revision"]==314 and sha(base)==changes["base_archive_sha256"]
        with ZipFile(base) as base_zip:
            raw = base_zip.read("catalogue.json")
            assert digest(raw)==changes["base_catalogue_sha256"]
            merged = json.loads(raw)
            assert merged["revision"]==308
        for component,entry in changes["components"].items():
            assert entry["file"]==f"components/{component}.glb"
            assert digest(delta_zip.read(entry["file"]))==component
        assert not (merged["components"].keys() & changes["components"].keys())
        merged["components"].update(changes["components"])
        merged["lens_overrides"] = changes["lens_overrides"]

        def merge(target,patch):
            assert patch.keys() <= target.keys()
            for key,value in patch.items():
                if isinstance(value,dict):
                    merge(target[key],value)
                else:
                    assert value is None or value in merged["components"]
                    target[key] = value

        merge(merged["fit_rows"],changes["fit_rows"])
        merge(merged["independent_roles"],changes["independent_roles"])
        assert len(merged["fit_rows"])==1792
        workload = json.loads(delta_zip.read("catalogue-workload.json"))
        looks = workload["appearances"]
        assert len(looks)==128 and len({a["selector"] for a in looks})==128
        assert all(a["selector"] in merged["fit_rows"] for a in looks)
        assert len(workload["messages"])==512 and {r["appearance"] for r in workload["messages"]}=={a["id"] for a in looks}
        if index:
            merged["revision"] = 314
            merged["artwork_commit"] = changes["artwork_commit"]
            merged["base_archive_sha256"] = changes["base_archive_sha256"]
            merged["delta_archive_sha256"] = sha(delta)
            index.write_text(json.dumps(merged,sort_keys=True,indent=2)+"\n",encoding="utf8")
        print(f"Resolved {len(merged['fit_rows'])} selectors and validated {len(looks)} distinct workload looks")


def phone(path):
    with ZipFile(path) as zip_:
        manifest = verified(zip_)
        assert manifest["schema"]=="ravedio-phone-handoff-314-1"
        raw = zip_.read("native/r308/runtime.json")
        runtime = json.loads(raw)
        assert runtime["art_revision"]==314
        assert digest(raw)==manifest["native_runtime_sha256"]
        for assembly in runtime["assemblies"].values():
            for part in assembly["parts"]:
                payload = zip_.read("native/r308/"+part["file"])
                assert len(payload)==part["bytes"] and digest(payload)==part["sha256"]
        inventory = json.loads(zip_.read("native/alpha/inventory.json"))
        alpha_payload = zip_.read("native/alpha/pack.zip")
        assert digest(alpha_payload)==inventory["archive_sha256"]
        with ZipFile(BytesIO(alpha_payload)) as alpha:
            names = alpha.namelist()
            assert len(names)==len(set(names)) and set(names)==set(inventory["files"])
            for name,expected in inventory["files"].items():
                assert digest(alpha.read(name))==expected,name
            layer_manifest = json.loads(alpha.read("manifest.json"))
            assert layer_manifest["art_revision"]==314
            assert layer_manifest["source_runtime_sha256"]==digest(raw)
            assert len(layer_manifest["cases"])==16 and len(layer_manifest["components"])==148
        depth = json.loads(zip_.read("references/receipt.json"))
        assert len(depth["pairs"])==48
        assert depth["recipe"]["yaw_degrees"]==15 and depth["recipe"]["plate_srgb"]==[241,244,250]
        for identity,pair in depth["pairs"].items():
            assert digest(zip_.read(f"references/{identity}/color-rgba.png"))==pair["rgba_sha256"]
            assert digest(zip_.read(f"references/{identity}/depth-z.exr"))==pair["depth_sha256"]
    print("Verified the 314 runtime, 148 layer groups, 48 reference pairs and every archive file")


if __name__=="__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action",required=True)
    p = sub.add_parser("phone")
    p.add_argument("archive",type=Path)
    p = sub.add_parser("catalogue")
    p.add_argument("base",type=Path)
    p.add_argument("delta",type=Path)
    p.add_argument("--index",type=Path)
    args = parser.parse_args()
    if args.action=="phone":
        phone(args.archive)
    else:
        overlay(args.base,args.delta,args.index)
