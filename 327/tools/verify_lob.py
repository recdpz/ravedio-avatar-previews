"""Check the Lob exports against source scalp, clothing and headwear."""
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "296/tools"))
from drape import CENTER, accessor, node_transforms, read_glb, surface


def load(path):
    return json.loads(path.read_bytes())


def positions(path):
    doc, binary = read_glb(path)
    points = []
    for node, rotation, offset in node_transforms(doc):
        if "mesh" in node:
            for part in doc["meshes"][node["mesh"]]["primitives"]:
                points.append(accessor(doc, binary, part["attributes"]["POSITION"], 3) @ rotation.T + offset)
    return np.concatenate(points)


def main(base, candidate):
    source, lob = (load(p / "catalogue.json") for p in (base, candidate))
    receipt = load(candidate / "receipt.json")
    verified = {}
    for original, data in receipt["replacements"].items():
        start = base / source["components"][original]["file"]
        end = candidate / lob["components"][data["sha256"]]["file"]
        a, b = positions(start), positions(end)
        above = a[:, 1] >= 1.90
        if not data.get("free_crown"):
            assert np.array_equal(a[above], b[above]), "Fitted crown vertices changed"
        outside = np.linalg.norm(a - CENTER, axis=1) >= .3845
        assert np.min(np.linalg.norm(b[outside] - CENTER, axis=1)) >= .38395, "Hair penetrates the head"
        verified[original] = {"minimum_tip_height_before":float(a[:,1].min()),
                              "minimum_tip_height_after":float(b[:,1].min())}

    assert source["independent_roles"] == lob["independent_roles"]
    assert source["groom_mouths"] == lob["groom_mouths"]
    changed = 0
    for key, old in source["fit_rows"].items():
        new = lob["fit_rows"][key]
        if key.startswith("Feminine/bob/"):
            assert new == {**old,"hair":receipt["replacements"][old["hair"]]["sha256"]}
            changed += 1
        else:
            assert new == old
    assert changed == 128
    # Check each actual garment and hat fit against the original.
    overlaps = {}
    unique = {}
    for key,row in source["fit_rows"].items():
        if key.startswith("Feminine/bob/"):
            unique.setdefault((row["hair"],row["headgear"],row["top"]),key)
    hair_cache = {}
    for (old, hat, top), key in unique.items():
        new = lob["fit_rows"][key]["hair"]
        for digest, folder, catalogue in ((old,base,source),(new,candidate,lob)):
            if digest not in hair_cache:
                hair_cache[digest] = surface(folder / catalogue["components"][digest]["file"])
        row = {}
        for role,digest in (("headgear",hat),("top",top)):
            if digest is None:
                continue
            target = surface(base / source["components"][digest]["file"])
            row[role] = {"before":len(hair_cache[old].overlap(target)),
                         "after":len(hair_cache[new].overlap(target))}
        overlaps[key] = row
    report = {"rows":changed,"geometry_variants":verified,"fit_intersections":overlaps}
    (candidate / "fit-review.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    counts = [(k,role,v["before"],v["after"]) for k,row in overlaps.items() for role,v in row.items()
              if v["after"]>v["before"]]
    print("Checked 128 rows and",len(unique),"distinct fitted assemblies.")
    for key,role,before,after in counts:
        print(key,role,before,after)
    if counts:
        raise ValueError("The hair introduced a new fit intersection")


if __name__ == "__main__":
    main(*(Path(value) for value in sys.argv[sys.argv.index("--")+1:]))
