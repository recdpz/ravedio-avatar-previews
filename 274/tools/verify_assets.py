"""Check both rigid updo fits against the exports and the unfitted catalogue."""
import json
import sys
from pathlib import Path

import numpy as np

REV = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REV / "tools"))
from fit_updos import CAT, CENTER, apply, group_geometry, load_parts, ordinary, read_glb, sha, surface, tree, vectors

ROOT = REV.parent
rows = json.loads((REV / "bandana-fits.json").read_text(encoding="utf8"))
before = json.loads((ROOT / "273/bandana-fits.json").read_text(encoding="utf8"))
reports = {}
for key, entry in rows.items():
    if key not in {"Feminine-ponytail","Feminine-space-buns"}:
        assert entry == before[key],key
        for role in ("headgear","sprout"):
            assert sha(REV/entry[role]) == entry[role+"_sha256"]
        continue
    style = key.removeprefix("Feminine-")
    assert entry["hair"] == before[key]["hair"]
    assert entry["hair_sha256"] == before[key]["hair_sha256"] == sha(ordinary(entry["hair"]))
    cloth = REV / entry["headgear"]
    all_cloth = surface(cloth)
    scarf = surface(cloth, lambda n: "scarf" in n)
    assert sha(cloth) == entry["headgear_sha256"]
    assert sha(REV / entry["sprout"]) == entry["sprout_sha256"]
    matrices = {int(k): (np.array(v["matrix"]),np.array(v["offset"])) for k,v in entry["pose"]["transforms"].items()}
    for matrix,_ in matrices.values():
        assert np.max(abs(matrix@matrix.T-np.eye(3))) < 1e-12
        assert abs(np.linalg.det(matrix)-1) < 1e-12
    poses = {}
    for color in ("default","ombre"):
        original = entry["hair"] if color == "default" else CAT["ombre"][entry["hair"]]
        g,b,parts = load_parts(ordinary(original),style)
        file = REV/entry["fittedHair"][color]
        target,blob = read_glb(file)
        assert sha(file) == entry["fittedHairSha256"][color]
        transformed = []
        for part in parts:
            p = vectors(g,b,part["p"])
            q = vectors(target,blob,part["p"])
            a = vectors(g,b,part["n"])
            n = vectors(target,blob,part["n"])
            fixed = part["labels"] == 0
            assert np.array_equal(p[fixed],q[fixed]) and np.array_equal(a[fixed],n[fixed])
            for label,(matrix,offset) in matrices.items():
                moving = part["labels"] == label
                expected = apply(part["points"][moving],matrix,offset)
                assert np.allclose(q[moving]@part["rot"].T+part["offset"],expected,rtol=0,atol=1.4e-7)
                expected_normals = (a[moving]@part["rot"].T)@matrix.T
                assert np.allclose(n[moving]@part["rot"].T,expected_normals,rtol=0,atol=1.4e-7)
            g["accessors"][part["p"]].update(min=q.min(axis=0).tolist(),max=q.max(axis=0).tolist())
            transformed.append({**part,"points":q@part["rot"].T+part["offset"]})
        assert target == g, (key,color,"GLB metadata")
        scalp = tree(*group_geometry(transformed,0))
        assert not scarf.overlap(scalp), (key,color,"scarf/scalp")
        contacts = []
        for label in matrices:
            moved = tree(*group_geometry(transformed,label))
            assert not moved.overlap(all_cloth), (key,color,"cloth")
            contact = len(moved.overlap(scalp))
            assert contact > 0, (key,color,"attachment")
            contacts.append(contact)
        poses[color] = [q["points"] for q in transformed]
        reports.setdefault(key,{})[color] = {"rigid":True,"protected_scalp_exact":True,
                                            "cloth_overlap_pairs":0,"scalp_contact_pairs":contacts}
    assert len(poses["default"]) == len(poses["ombre"])
    assert all(np.array_equal(a,b) for a,b in zip(poses["default"],poses["ombre"]))
(REV / "verification/assets.json").write_text(json.dumps(reports,indent=2)+"\n",encoding="utf8",newline="\n")
print("Verified rigid placement and scarf clearance on both colors for both updos")
