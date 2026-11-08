"""Validate the fitted assets and record the review measurements."""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sculpt import REV, ROOT, accessor, local_path, read_glb, surface


def load(path):
    return json.loads(path.read_text(encoding="utf8"))


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def verify_asset(source, result):
    a, before = read_glb(source)
    b, after = read_glb(result)
    for key in ("nodes", "scenes", "materials", "textures", "samplers", "images"):
        assert a.get(key) == b.get(key), (result.name, key)
    changed_views = set()
    for old_mesh, new_mesh in zip(a["meshes"], b["meshes"], strict=True):
        old_primitives = old_mesh["primitives"]
        new_primitives = new_mesh["primitives"]
        assert old_primitives == new_primitives[:len(old_primitives)], result
        for i, primitive in enumerate(new_primitives):
            attrs = primitive["attributes"]
            for role in ("POSITION", "NORMAL"):
                index = attrs[role]
                p = accessor(b, after, index, 3)
                assert np.isfinite(p).all(), result
                if i < len(old_primitives):
                    changed_views.add(b["accessors"][index]["bufferView"])
                if role == "NORMAL":
                    assert np.max(abs(np.linalg.norm(p, axis=1) - 1)) < .004, result
                else:
                    bounds = b["accessors"][index]
                    assert bounds["min"] == p.min(axis=0).tolist(), result
                    assert bounds["max"] == p.max(axis=0).tolist(), result
    for i, view in enumerate(a["bufferViews"]):
        assert view == b["bufferViews"][i], result
        if i not in changed_views:
            start = view.get("byteOffset", 0)
            stop = start + view["byteLength"]
            assert before[start:stop] == after[start:stop], (result, i)
    return {"source": source.relative_to(ROOT).as_posix(), "source_sha256": sha256(source),
            "output_sha256": sha256(result), "bytes": result.stat().st_size}


def rear_gap_samples(path):
    tree = surface(path)
    xs = np.linspace(-.25, .25, 101)
    ys = np.linspace(1.40, 1.52, 25)
    return sum(tree.ray_cast((x, y, -.7), (0, 0, 1), .57)[3] is None for x in xs for y in ys)


def max_difference(normal, fitted):
    first, a = read_glb(normal)
    second, b = read_glb(fitted)
    distances = []
    for m, n in zip(first["meshes"], second["meshes"], strict=True):
        for p, q in zip(m["primitives"], n["primitives"], strict=True):
            old = accessor(first, a, p["attributes"]["POSITION"], 3)
            new = accessor(second, b, q["attributes"]["POSITION"], 3)
            distances.extend(np.linalg.norm(new - old, axis=1))
    return round(float(max(distances)), 4)


def verify(before, after):
    old, new = load(before), load(after)
    assert (old["revision"], new["revision"]) == ("296", "297")
    assert len(new["rows"]) == 60
    key = lambda row: (row["hair"], row["headwear"], row["top"], row["hairColor"])
    previous = {key(r): r for r in old["rows"]}
    hair = {}
    for row in new["rows"]:
        changed = {"hair", "headgear"} if row["headwear"] == "pashmina" else {"hair"}
        if key(row) in previous:
            original = previous[key(row)]["parts"]
            assert row["parts"].keys() == original.keys()
            for name in original.keys() - changed:
                assert original[name] == row["parts"][name], (key(row), name)
        if row["top"] == "open" and row["hairColor"] == "default":
            hair[row["hair"], row["headwear"]] = local_path(row["parts"]["hair"])
    for name in ("hair-fits.json", "pashmina-fits.json"):
        def resolve(revision, p):
            return (ROOT / str(revision) / p).resolve()
        base, fit = (load(ROOT / str(r) / name) for r in (296, 297))
        for build, styles in base.items():
            for style, entry in styles.items():
                if build == "Feminine" and style in {"straight", "curls"}:
                    continue
                if name == "hair-fits.json":
                    for hat, colors in entry["fits"].items():
                        for color, path in colors.items():
                            assert resolve(296, path) == resolve(297, fit[build][style]["fits"][hat][color])
                else:
                    for top, path in entry.items():
                        assert resolve(296, path) == resolve(297, fit[build][style][top])
    manifest = {name: verify_asset(ROOT / source, REV / "assets" / name)
                for name, source in load(REV / "verification/sources.json").items()}
    gaps = [rear_gap_samples(p) for p in [
        local_path(previous["curls", "none", "open", "default"]["parts"]["hair"]),
        hair["curls", "none"], hair["curls", "pashmina"]]]
    assert gaps[1] < gaps[0] and gaps[2] < gaps[0], gaps
    deltas = {name: max_difference(hair[name, "none"], hair[name, "pashmina"])
              for name in ("curls", "straight")}
    report = {"covered_and_uncovered_selections": len(new["rows"]),
              "curls_nape_open_samples_before_uncovered_fitted": gaps,
              "fitted_max_vertex_displacement": deltas, "assets": manifest}
    (REV / "verification/geometry.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf8", newline="\n")
    print(f"{len(manifest)} GLBs checked, {len(new['rows'])} selections")
    print(f"Curls nape gap samples {gaps}, covered movement {deltas}")


if __name__ == "__main__":
    verify(*(Path(arg) for arg in sys.argv[-2:]))
