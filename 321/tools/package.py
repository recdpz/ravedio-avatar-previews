"""Package the approved bean eyes into the 320 source catalogue."""
from argparse import ArgumentParser
import hashlib
import json
import os
from pathlib import Path
import shutil

REVISION = Path(__file__).resolve().parents[1]
ART = REVISION.parent
ASSETS = {
    "Feminine": {
        "eyes": ("feminine-222-eyes.glb", "54bf381112a76b884368e9e3bfbaee92fa8ab8393770439c71aced893f675415"),
        "lashes": ("feminine-222-lashes.glb", "335cb6728c0baa6b3003542a35e8a550057fc1bd574983dbc623372fd70cbe5e"),
    },
    "Masculine": {
        "eyes": ("masculine-222-eyes.glb", "12a3fa4aabddc6e4e687c356c99035955896650ed711148dfbf4bd46a5e43a70"),
    },
}


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def load(path):
    return json.loads(path.read_bytes())


def write(path, data):
    path.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n",encoding="utf8",newline="\n")


def package(base, output):
    if output.resolve() == base.resolve():
        raise ValueError("Use a separate revision output directory")
    catalogue = load(base/"catalogue.json")
    if catalogue["revision"] != 320:
        raise ValueError("Expected the revision 320 source catalogue")
    overlay = load(base/"overlay.json")
    source = load(ART/"315/catalogue-input.json")
    assets = output/"assets"
    assets.mkdir(parents=True,exist_ok=True)
    components = catalogue["components"]
    replacements = {}
    for build,roles in ASSETS.items():
        face = catalogue["independent_roles"][build]["faces"]["bean"]
        source_face = source["builds"][build]["faces"]["bean"]
        for role,(name,digest) in roles.items():
            approved = REVISION/"assets"/name
            if sha(approved) != digest:
                raise ValueError(f"{name} differs from the approved 222 degree export")
            relative = f"assets/{digest}.glb"
            shutil.copyfile(approved,output/relative)
            replacements[face[role]] = digest
            face[role] = digest
            overlay["components"][source_face[role]] = digest
            components[digest] = {"file":relative,"bytes":approved.stat().st_size}

    referenced = set()
    def collect_parts(tree):
        for value in tree.values():
            if isinstance(value,dict):
                collect_parts(value)
            elif value is not None:
                referenced.add(value)

    for field in ("fit_rows","independent_roles","groom_mouths"):
        collect_parts(catalogue[field])
    referenced.update(overlay["components"].values())
    for previous in replacements:
        if previous not in referenced:
            components.pop(previous)
    for digest,entry in components.items():
        target = output/entry["file"]
        if not target.exists():
            original = base/entry["file"]
            try:
                os.link(original,target)
            except OSError:
                shutil.copyfile(original,target)
        if target.stat().st_size != entry["bytes"]:
            raise ValueError(f"Unexpected size for {digest}")

    for field in ("palette","studio","finish"):
        name = catalogue[field]
        shutil.copyfile(base/name,output/name)
    dyes = catalogue["shared_jersey_dyes_dir"]
    shutil.copytree(base/dyes,output/dyes,dirs_exist_ok=True)
    catalogue["revision"] = 321
    write(output/"catalogue.json",catalogue)
    write(output/"overlay.json",overlay)
    write(output/"receipt.json",{
        "revision":321,
        "base_revision":320,
        "bean_rotation_degrees":222,
        "replaced_glbs":replacements,
        "catalogue_components":len(components),
    })


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("base",type=Path)
    parser.add_argument("output",type=Path)
    args = parser.parse_args()
    package(args.base,args.output)
