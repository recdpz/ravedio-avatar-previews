"""Verify the Box Braids exports against the prior preview and its worn fits."""
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


@lru_cache(maxsize=24)
def lower_braids(path):
    meshes = []
    for _, _, p, _, rotation, offset, faces in geometry(*read_glb(path)):
        world = p @ rotation.T + offset
        lower = faces[world[faces, 1].min(axis=1) < 1.50]
        meshes.append(tree(world, lower))
    return meshes


@lru_cache(maxsize=32)
def support(path):
    return surface(path)


def lower_contacts(path, component):
    collider = support(component)
    return sum(len({i for i, _ in braid.overlap(collider)}) for braid in lower_braids(path))


def components(row):
    return {role: local_path(path) for role, path in row["components"].items()}


def verify(before, after):
    assert len(before) == len(after) == 104
    assets = {}
    report = []
    for previous, current in zip(before, after, strict=True):
        features = current["features"]
        assert previous["features"] == features and previous["build"] == current["build"]
        old, new = map(components, (previous, current))
        assert old.keys() == new.keys()
        change = {role for role in old if old[role] != new[role]}
        box = features["hair"] == "box-braids"
        assert change == ({"hair"} if box else set()), (features, change)
        if not box:
            continue

        source, target = old["hair"], new["hair"]
        if target not in assets:
            topology(source, target)
            assets[target] = sha256(target.read_bytes()).hexdigest()
        counts = {}
        for role in ("base", "top", "headgear"):
            if role not in new:
                continue
            previous_count = lower_contacts(source, old[role])
            current_count = lower_contacts(target, new[role])
            assert current_count == 0, (features, role, previous_count, current_count)
            counts[role] = {"305": previous_count, "306": current_count}
        report.append({"headwear": features["headwear"], "top": features["top"],
                       "hair_color": features["hairColor"], "lower_triangle_contacts": counts})

    assert len(assets) == 10 and len(report) == 44
    return {"browser_selections": len(after), "braid_fit_checks": report,
            "sha256": {path.name: value for path, value in assets.items()}}


if __name__ == "__main__":
    before, after = (json.loads(Path(p).read_text(encoding="utf-8-sig")) for p in sys.argv[-2:])
    result = verify(before, after)
    (REV / "verification/fit.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("Verified 104 selections, 44 Box Braids fits and 10 exported assets")
