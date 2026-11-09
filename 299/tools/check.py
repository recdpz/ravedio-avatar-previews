"""Compare resolved 298 and 299 geometry while protecting shared roles."""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fit import (FIT_STYLES, geometry, local_path, read_glb, sha, surface, tree)

def receipt(path):
    data = json.loads(path.read_text(encoding="utf8"))
    return {(r["hair"], r["headwear"], r["top"], r["hairColor"]): r["parts"] for r in data["rows"]}


def intersections(path, cloth):
    doc, binary = read_glb(path)
    total = 0
    for _, _, pos, _, rotation, offset, faces in geometry(doc, binary):
        points = pos @ rotation.T + offset
        faces = faces[points[faces, 1].min(axis=1) < 1.77]
        if len(faces):
            total += len({i for i, _ in tree(points, faces).overlap(cloth)})
    return total


def topology(source, final):
    original, before = read_glb(source)
    changed, after = read_glb(final)
    allowed = set()
    for mesh in changed["meshes"]:
        for primitive in mesh["primitives"]:
            for key in ("POSITION", "NORMAL"):
                allowed.add(primitive["attributes"][key])
    geometry_views = {changed["accessors"][i]["bufferView"] for i in allowed}
    for index, view in enumerate(changed["bufferViews"]):
        if index not in geometry_views:
            offset = view.get("byteOffset", 0)
            end = offset + view["byteLength"]
            assert before[offset:end] == after[offset:end]
    for document in (original, changed):
        for index in allowed:
            for key in ("min", "max"):
                document["accessors"][index].pop(key, None)
    assert original == changed
    for _, _, points, normals, _, _, _ in geometry(changed, after):
        assert np.isfinite(points).all() and np.isfinite(normals).all()
        assert np.max(np.abs(np.linalg.norm(normals, axis=1) - 1)) < 1e-4


def check(before, after, uncovered_before, uncovered_after, output):
    source, final = receipt(before), receipt(after)
    uncovered_source, uncovered_final = receipt(uncovered_before), receipt(uncovered_after)
    assert source.keys() == final.keys() and len(final) == 128
    assert uncovered_source == uncovered_final and len(uncovered_final) == 16
    records = []
    checked = set()
    for (style, hat, top, color), parts in final.items():
        key = (style, hat, top, color)
        prior = source[key]
        expected = set()
        if style in FIT_STYLES:
            expected.add("hair")
        if style == "twin-braids":
            expected.add("hairLengths")
        if style == "curls" and top == "open":
            expected.add("headgear")
        changed = {role for role in parts if prior[role] != parts[role]}
        assert changed == expected, (key, changed)
        for role in changed:
            src, dst = (local_path(p[role]) for p in (prior, parts))
            if dst not in checked:
                topology(src, dst)
                checked.add(dst)
        if style not in FIT_STYLES and style != "twin-braids":
            continue
        before_cloth, after_cloth = (surface(local_path(p["headgear"])) for p in (prior, parts))
        slots = [s for s in ("hair", "hairLengths") if s in parts]
        hits = [sum(intersections(local_path(p[s]), cloth) for s in slots)
                for p, cloth in ((prior,before_cloth),(parts,after_cloth))]
        if style in {"curls","straight","bob","twin-braids"}:
            assert hits[1] == 0, (key,hits)
        if style == "box-braids":
            assert hits[1] <= hits[0], (key,hits)
        records.append({"style":style,"top":top,"color":color,"before":hits[0],"after":hits[1]})
    output.write_text(json.dumps({"overlap":records, "uncovered_controls":len(uncovered_final),
                                  "resolved_worn_controls":len(final),
                                  "assets":{p.name:sha(p) for p in sorted(checked)}},indent=2)+"\n",
                      encoding="utf8")
    for style in (*FIT_STYLES,"twin-braids"):
        selected = [r for r in records if r["style"] == style]
        print(style, max(r["before"] for r in selected), "→", max(r["after"] for r in selected))


if __name__ == "__main__":
    check(*map(Path, sys.argv[-5:]))
