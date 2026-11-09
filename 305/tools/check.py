"""Check selector isolation, braid clearance, and rigid Ponytail reuse."""
from hashlib import sha256
import json
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from twin import ROOT
from beanie import attachment, fitted_crown
from fit import geometry, local_path, read_glb, surface, tree

REV = ROOT / "305"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def meshes(path, keep=lambda name: True):
    return {
        name: (points @ rotation.T + offset, normals @ rotation.T, faces)
        for name, _, points, normals, rotation, offset, faces in geometry(*read_glb(path))
        if keep(name)
    }


def verify_twin(source, target):
    assert read_glb(source)[0]["materials"] == read_glb(target)[0]["materials"]
    old = meshes(source)
    new = meshes(target)
    assert old.keys() == new.keys()
    for name, (points, normals, faces) in new.items():
        original, original_normals, original_faces = old[name]
        assert np.array_equal(faces, original_faces)
        assert np.isfinite(points).all()
        assert np.max(abs(np.linalg.norm(normals, axis=1) - 1)) < .005
        roots = original[:, 1] >= 1.785
        assert np.array_equal(points[roots], original[roots])
        assert np.array_equal(normals[roots], original_normals[roots])


def verify_beanie(source, old_crown, crown, tail, hat):
    original = meshes(source, attachment)
    posed = meshes(tail)
    assert original.keys() == posed.keys() and len(original) == 6
    a = np.concatenate([part[0] for part in original.values()])
    b = np.concatenate([posed[name][0] for name in original])
    a_mean, b_mean = a.mean(axis=0), b.mean(axis=0)
    u, _, v = np.linalg.svd((a - a_mean).T @ (b - b_mean))
    rotation = u @ v
    assert np.linalg.det(rotation) > .99999
    error = float(np.linalg.norm((a - a_mean) @ rotation + b_mean - b, axis=1).max())
    assert error < .000003
    for name, (_, normals, faces) in original.items():
        assert np.array_equal(faces, posed[name][2])
        assert np.max(np.linalg.norm(normals @ rotation - posed[name][1], axis=1)) < .00005
    old, new = meshes(old_crown, fitted_crown), meshes(crown)
    assert old.keys() == new.keys()
    for name, part in old.items():
        assert all(np.array_equal(a, b) for a, b in zip(part, new[name], strict=True))
    assert not surface(tail).overlap(surface(hat))
    return {"maximum_rigid_fit_error": error, "tail_parts": len(posed), "beanie_contacts": 0}


def braid_contacts(current):
    features, components = current["features"], current["components"]
    front = []
    for points, _, faces in meshes(components["hairLengths"]).values():
        mask = (points[faces, 1].min(axis=1) < 1.90) & (points[faces, 2].mean(axis=1) > 0)
        front.append(tree(points, faces[mask]))
    counts = {}
    for role in ("base", "top", "headgear"):
        if role in components:
            neighbor = surface(components[role])
            counts[role] = sum(len({a for a, _ in braid.overlap(neighbor)}) for braid in front)
    assert counts["top"] == 0 and counts.get("headgear", 0) == 0, (features, counts)
    return {"headwear": features["headwear"], "top": features["top"],
            "hair_color": features["hairColor"], "front_triangle_contacts": counts}


def verify(before, after):
    assert len(before) == len(after) == 104
    bare = {row["features"]["hairColor"]: local_path(row["components"]["hair"])
            for row in before if row["features"]["hair"] == "ponytail"
            and row["features"]["headwear"] == "none"}
    result = {"browser_selections": len(after), "unchanged_box_braid_selections": 0,
              "braid_contact_checks": [], "beanie_checks": {}}
    changed_assets = set()
    for previous, current in zip(before, after, strict=True):
        assert previous["features"] == current["features"] and previous["build"] == current["build"]
        features = current["features"]
        hair, hat, color = (features[key] for key in ("hair", "headwear", "hairColor"))
        a, b = ({role: local_path(path) for role, path in row["components"].items()}
                for row in (previous, current))
        edits = {role for role in a.keys() | b.keys() if a.get(role) != b.get(role)}
        if hair == "twin-braids" and hat in {"none", "pashmina"}:
            assert edits == {"hairLengths"}, (features, edits)
            verify_twin(a["hairLengths"], b["hairLengths"])
            result["braid_contact_checks"].append(braid_contacts({**current, "components": b}))
        elif hair == "ponytail" and hat == "beanie":
            assert edits == {"hair", "hairLengths"}, (features, edits)
            result["beanie_checks"][color] = verify_beanie(
                bare[color], a["hair"], b["hair"], b["hairLengths"], b["headgear"])
        else:
            assert not edits, (features, edits)
        if hair == "box-braids":
            result["unchanged_box_braid_selections"] += 1
        changed_assets.update(b[role] for role in edits)
    assert len(changed_assets) == 36
    result["revised_hair_glbs"] = len(changed_assets)
    result["asset_sha256"] = {asset.name: sha256(asset.read_bytes()).hexdigest()
                              for asset in sorted(changed_assets)}
    return result


if __name__ == "__main__":
    result = verify(*map(load, sys.argv[-2:]))
    (REV / "verification/fit.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("Verified 104 browser selections, 36 GLBs, 32 braid fits and two beanie finishes")
