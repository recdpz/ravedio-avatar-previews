"""Verify the shared-coordinate exports and the preview's resolved paths."""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drape import CAT, REV, ROOT, accessor, local_path, node_transforms, ordinary, read_glb


def load(path):
    return json.loads(path.read_text(encoding="utf8"))


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def verify_asset(source, output):
    original, before = read_glb(source)
    revised, after = read_glb(output)
    assert original.keys() == revised.keys(), output
    for key in original.keys() - {"accessors"}:
        assert original[key] == revised[key], (output, key)
    editable = set()
    for mesh in revised["meshes"]:
        for primitive in mesh["primitives"]:
            for role in ("POSITION", "NORMAL"):
                index = primitive["attributes"][role]
                editable.add(revised["accessors"][index]["bufferView"])
                points = accessor(revised, after, index, 3)
                assert np.isfinite(points).all(), output
                if role == "NORMAL":
                    assert np.max(np.abs(np.linalg.norm(points, axis=1) - 1)) < .004, output
                else:
                    bounds = revised["accessors"][index]
                    assert bounds["min"] == points.min(axis=0).tolist(), output
                    assert bounds["max"] == points.max(axis=0).tolist(), output
    for i, view in enumerate(revised["bufferViews"]):
        if i not in editable:
            start = view.get("byteOffset", 0)
            stop = start + view["byteLength"]
            assert before[start:stop] == after[start:stop], (output, i)
    source_path = source if source.is_relative_to(ROOT) else ROOT / "270/generated" / source.name
    assert source_path.resolve() == source.resolve(), source
    return {
        "source": source_path.relative_to(ROOT).as_posix(),
        "source_sha256": digest(source),
        "sha256": digest(output),
        "bytes": output.stat().st_size,
    }


def hem_samples(path):
    model, binary = read_glb(path)
    for node, rotation, offset in node_transforms(model):
        if "mesh" not in node:
            continue
        mesh = model["meshes"][node["mesh"]]
        if "joined hood wrap" not in mesh["name"]:
            continue
        for primitive in mesh["primitives"]:
            attrs = primitive["attributes"]
            pos = accessor(model, binary, attrs["POSITION"], 3) @ rotation.T + offset
            uv = accessor(model, binary, attrs["TEXCOORD_0"], 2)
            return [pos[(abs(uv[:, 0] - u) < .009) & (abs(uv[:, 1]) < .009)].mean(axis=0)
                    for u in (.1, .5, .9)]
    raise ValueError(path)


def verify(before_path, after_path):
    before, after = load(before_path), load(after_path)
    assert (before["revision"], after["revision"]) == ("295", "296")
    assert len(before["rows"]) == len(after["rows"]) == 120
    cloth = load(REV / "pashmina-fits.json")
    assets = {}
    for build, styles in cloth.items():
        for hair, tops in styles.items():
            family = CAT["pashminaHairFamilies"][build][hair]
            for top, output in tops.items():
                source = ordinary(CAT["pashminaVariants"][build][family][top])
                target = (REV / output).resolve()
                assert assets.setdefault(target, source) == source

    hair_paths = set()
    sample = None
    for old, new in zip(before["rows"], after["rows"]):
        assert {k: v for k, v in old.items() if k != "parts"} == {k: v for k, v in new.items() if k != "parts"}
        a, b = old["parts"], new["parts"]
        assert a.keys() == b.keys()
        for key in a.keys() - {"headgear", "hair"}:
            assert a[key] == b[key], (new["build"], new["hair"], key)
        target, source = local_path(b["hair"]), local_path(a["hair"])
        assert assets.setdefault(target, source) == source
        hair_paths.add(target)
        assert local_path(b["headgear"]) == (REV / cloth[new["build"]][new["hair"]][new["top"]]).resolve()
        if (new["hair"], new["top"], new["hairColor"]) == ("curls", "open", "default"):
            sample = {
                "295": np.array(hem_samples(local_path(a["headgear"]))).round(4).tolist(),
                "296": np.array(hem_samples(local_path(b["headgear"]))).round(4).tolist(),
            }

    for build, fixture in after["fixtures"].items():
        original = before["fixtures"][build]
        assert original["features"] == fixture["features"]
        assert original["parts"].keys() == fixture["parts"].keys()
        allowed = {"hair", "headgear"} if build == "Feminine" else set()
        for key in original["parts"].keys() - allowed:
            assert original["parts"][key] == fixture["parts"][key], (build, key)

    assert len(hair_paths) == 32 and len(assets) - len(hair_paths) == 112
    manifest = {target.relative_to(REV).as_posix(): verify_asset(source, target)
                for target, source in sorted(assets.items())}
    report = {
        "covered_selections": len(after["rows"]),
        "distinct_styles": 16,
        "camera_views_per_default_assembly": 8,
        "curls_open_lower_hood_left_nape_right": sample,
        "assets": manifest,
    }
    path = REV / "verification/geometry.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf8", newline="\n")
    print(f"Verified {len(assets)} GLBs and {len(after['rows'])} covered selections")
    print(sample)


if __name__ == "__main__":
    verify(*(Path(p) for p in sys.argv[-2:]))
