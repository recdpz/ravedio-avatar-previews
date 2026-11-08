"""Verify the covered fits and count visible-review combinations."""
import json
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fit_pashmina import (REV, ROOT, STYLES, accessor, hood_tree, local_path,
                          read_glb, surface)


@lru_cache(maxsize=22)
def collision_tree(path, hood_only=False):
    return hood_tree(path) if hood_only else surface(path)


def verify_assets():
    files = json.loads((REV / "verification/fits.json").read_text(encoding="utf8"))
    for name, record in files.items():
        a, before = read_glb(ROOT / record["source"])
        b, after = read_glb(REV / "assets" / name)
        assert a.keys() == b.keys()
        for key in a:
            if key != "accessors":
                assert a[key] == b[key], (name, key)
        edited = set()
        for mesh in b["meshes"]:
            for p in mesh["primitives"]:
                for role in ("POSITION", "NORMAL"):
                    index = p["attributes"][role]
                    edited.add(b["accessors"][index]["bufferView"])
                    values = accessor(b, after, index, 3)
                    assert np.isfinite(values).all()
                    if role == "NORMAL":
                        assert np.max(np.abs(np.linalg.norm(values, axis=1) - 1)) < .004, name
                    else:
                        original = accessor(a, before, index, 3)
                        assert np.array_equal(values[:, 1], original[:, 1]), name
                        protected = original[:, 1] <= 1.365
                        assert np.array_equal(values[protected], original[protected]), name
        for i, view in enumerate(a["bufferViews"]):
            if i not in edited:
                start = view.get("byteOffset", 0)
                stop = start + view["byteLength"]
                assert before[start:stop] == after[start:stop], name
    return len(files)


def verify(before_path, after_path):
    assets = verify_assets()
    before, after = (json.loads(p.read_text(encoding="utf8")) for p in (before_path, after_path))
    assert before["revision"] == "294" and after["revision"] == "295"
    assert len(before["rows"]) == len(after["rows"]) == 120
    contacts = []
    for old, new in zip(before["rows"], after["rows"]):
        a, b = (r["parts"] for r in (old, new))
        assert {k: v for k, v in old.items() if k != "parts"} == {k: v for k, v in new.items() if k != "parts"}
        assert {k: v for k, v in a.items() if k != "hair"} == {k: v for k, v in b.items() if k != "hair"}
        if old["hair"] not in STYLES:
            assert a == b
            continue
        assert a["hair"] != b["hair"]
        old_hair, new_hair = (collision_tree(local_path(r["hair"])) for r in (a, b))
        count = {}
        for slot, hood in (("headgear", True), ("top", False)):
            target = collision_tree(local_path(b[slot]), hood)
            count[slot] = [len(hair.overlap(target)) for hair in (old_hair, new_hair)]
        assert count["headgear"][1] < count["headgear"][0], (new["hair"], new["top"], count)
        assert count["top"][1] <= count["top"][0], (new["hair"], new["top"], count)
        contacts.append({k: new[k] for k in ("hair", "top", "hairColor")} | count)
    assert len(contacts) == 48
    for build, fixture in after["fixtures"].items():
        source = before["fixtures"][build]
        assert source["features"] == fixture["features"]
        if build == "Feminine":
            assert local_path(fixture["parts"]["hair"]) == REV / "assets/curls-pashmina-default.glb"
        else:
            assert source["parts"] == fixture["parts"]
    report = {"covered_selections": len(after["rows"]), "distinct_styles": 16,
              "angles_per_original_finish": 8, "edited_assets": assets,
              "overlap_pairs_before_after": contacts}
    (REV / "verification/geometry.json").write_text(json.dumps(report, indent=2) + "\n",
                                                      encoding="utf8", newline="\n")
    print(f"Verified {assets} GLBs, {len(after['rows'])} covered selections and {len(contacts)} changed fits")


if __name__ == "__main__":
    verify(*(Path(p) for p in sys.argv[-2:]))