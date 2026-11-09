"""Verify the Box Braids rollback and all Twin Braids component selections."""
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import sys

import numpy as np

REV = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REV.parent / "299/tools"))
from check import topology
from fit import geometry, local_path, read_glb, surface, tree


@lru_cache(maxsize=100)
def colliders(path):
    return surface(path)


@lru_cache(maxsize=72)
def braid_surfaces(path):
    meshes = []
    for _, _, p, _, rotation, offset, faces in geometry(*read_glb(path)):
        world = p @ rotation.T + offset
        lower = faces[world[faces, 1].min(axis=1) < 1.50]
        meshes.append((tree(world, faces), tree(world, lower)))
    return meshes


def contacts(path, component, lower=False):
    collider = colliders(component)
    return sum(len({i for i, _ in mesh[int(lower)].overlap(collider)})
               for mesh in braid_surfaces(path))


def verify_roots(source, target):
    topology(source, target)
    for old, new in zip(geometry(*read_glb(source)), geometry(*read_glb(target)), strict=True):
        world = old[2] @ old[4].T + old[5]
        roots = world[:, 1] >= 1.82
        assert np.array_equal(old[2][roots], new[2][roots])
        assert np.array_equal(old[3][roots], new[3][roots])


def verify(before, after):
    assert len(before) == len(after) == 188
    assets, hats = {}, {}
    box_count = 0
    for previous, current in zip(before, after, strict=True):
        features = current["features"]
        assert previous["features"] == features and previous["build"] == current["build"]
        a, b = ({key: local_path(url) for key, url in row["components"].items()}
                for row in (previous, current))
        assert a.keys() == b.keys()
        hair, hat = (features[key] for key in ("hair", "headwear"))
        edits = {key for key in a if a[key] != b[key]}
        assert edits == ({"hairLengths"} if hair == "twin-braids" else set()), (features, edits)
        if hair == "box-braids":
            box_count += 1
        if hair != "twin-braids":
            continue

        old, new = a["hairLengths"], b["hairLengths"]
        if new not in assets:
            assert hat in {"none", "pashmina"}
            verify_roots(old, new)
            assets[new] = sha256(new.read_bytes()).hexdigest()

        body = contacts(new, b["base"], lower=True)
        top = contacts(new, b["top"])
        assert body == top == 0, (features, body, top)
        entry = hats.setdefault(hat, {"selections": 0, "lower_body_contacts": 0,
                                      "top_contacts": 0, "maximum_existing_hat_contacts": 0})
        entry["selections"] += 1
        if "headgear" in b:
            before_hat, after_hat = (contacts(path, b["headgear"]) for path in (old, new))
            assert after_hat <= before_hat, (features, before_hat, after_hat)
            if hat == "pashmina":
                assert after_hat == 0, (features, after_hat)
            entry["maximum_existing_hat_contacts"] = max(entry["maximum_existing_hat_contacts"], after_hat)

    assert box_count == 44 and len(assets) == 32
    assert len(hats) == 8 and all(entry["selections"] == 16 for entry in hats.values())
    return {"browser_selections": len(after), "restored_box_braid_selections": box_count,
            "twin_braid_checks": hats, "asset_sha256": {path.name: digest for path, digest in assets.items()}}


if __name__ == "__main__":
    before, after = (json.loads(Path(p).read_text(encoding="utf-8-sig")) for p in sys.argv[-2:])
    report = verify(before, after)
    (REV / "verification/fit.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("Verified 188 browser selections, 44 restored Box Braids selections and 128 Twin Braids fits")
