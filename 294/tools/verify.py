"""Verify the edited exports against the assembled 293 variants."""
import json
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from repair import REV, ROOT, local_path, read_glb, surface, triangles, accessor, LINER_STYLES


@lru_cache(maxsize=24)
def tree(path):
    return surface(path)


def verify_files(exports):
    for item in exports:
        source, target = ROOT / item["source"], REV / item["path"]
        original, old_data = read_glb(source)
        corrected, new_data = read_glb(target)
        for key in ("nodes", "meshes", "materials", "images", "bufferViews"):
            assert original.get(key) == corrected.get(key), (target, key)
        for mesh in original["meshes"]:
            for p in mesh["primitives"]:
                a = p["attributes"]
                assert np.array_equal(triangles(original, old_data, p["indices"]),
                                      triangles(corrected, new_data, p["indices"])), target
                for key in a:
                    if key in {"POSITION", "NORMAL"}:
                        continue
                    i = original["accessors"][a[key]]["bufferView"]
                    view = original["bufferViews"][i]
                    start = view.get("byteOffset", 0)
                    end = start + view["byteLength"]
                    assert old_data[start:end] == new_data[start:end], (target, key)
                coords = accessor(corrected, new_data, a["POSITION"], 3)
                normals = accessor(corrected, new_data, a["NORMAL"], 3)
                assert np.isfinite(coords).all() and np.isfinite(normals).all()
                if any(target.name.startswith(f"{style}-") for style in LINER_STYLES):
                    if "continuous recessed" not in mesh["name"]:
                        assert np.array_equal(coords, accessor(original, old_data, a["POSITION"], 3)), target
                        assert np.array_equal(normals, accessor(original, old_data, a["NORMAL"], 3)), target


def verify(before_path, after_path):
    exports = json.loads((REV / "verification/exports.json").read_text(encoding="utf8"))
    verify_files(exports)
    before = json.loads(before_path.read_text(encoding="utf8"))
    after = json.loads(after_path.read_text(encoding="utf8"))
    assert before["revision"] == "293" and after["revision"] == "294"
    assert len(before["rows"]) == len(after["rows"]) == 288
    contact = {}
    modified = 0
    for old, new in zip(before["rows"], after["rows"]):
        old_parts, new_parts = old["parts"], new["parts"]
        assert {k:v for k,v in old.items() if k != "parts"} == {k:v for k,v in new.items() if k != "parts"}
        assert {k:v for k,v in old_parts.items() if k != "hair"} == {k:v for k,v in new_parts.items() if k != "hair"}
        style, hat = old["hair"], old["headwear"]
        if style not in LINER_STYLES | {"box-braids"} and (style, hat) != ("flow", "cap"):
            assert old_parts == new_parts
            continue
        assert old_parts["hair"] != new_parts["hair"]
        modified += 1
        hair = local_path(new_parts["hair"])
        for slot in ("headgear", "top"):
            if slot not in new_parts:
                continue
            other = local_path(new_parts[slot])
            key = (hair, other)
            if key not in contact:
                before_count = len(tree(local_path(old_parts["hair"])).overlap(tree(other)))
                after_count = len(tree(hair).overlap(tree(other)))
                contact[key] = {"hair": hair.name, "component": other.relative_to(ROOT).as_posix(),
                                "slot": slot, "before": before_count, "after": after_count}
            counts = contact[key]
            if style == "flow" and slot == "headgear":
                assert counts["before"] > 0 and counts["after"] == 0, counts
    regressions = [c for c in contact.values() if c["after"] > c["before"]]
    report = {"assemblies_checked": len(after["rows"]), "changed_assemblies": modified,
              "checked_exports": len(exports), "clearance_increases": regressions,
              "contacts": list(contact.values())}
    (REV / "verification/geometry.json").write_text(json.dumps(report, indent=2) + "\n",
                                                     encoding="utf8", newline="\n")
    print(f"{len(exports)} exports and {len(after['rows'])} assemblies checked")
    print(f"{len(regressions)} pairs with increased intersections")
    for item in regressions:
        print(item)
    assert not regressions, "A repair increased external contact"


if __name__ == "__main__":
    verify(*(Path(path) for path in sys.argv[-2:]))