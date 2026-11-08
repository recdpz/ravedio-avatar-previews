"""Verify the three hair exports and the associated headwear selections."""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from refine import CENTER, HEAD, ROOT, REV, STYLES, accessor, envelope, load, local_path, polar, sample, write
from sculpt import node_transforms, read_glb
sys.path.insert(0, str(ROOT / "297/tools"))
from verify import verify_asset


def temple_samples(path):
    model, binary = read_glb(path)
    count = inside = 0
    for node, rotation, offset in node_transforms(model):
        if "mesh" not in node:
            continue
        mesh = model["meshes"][node["mesh"]]
        if "side sweep" not in mesh["name"]:
            continue
        # The first primitive contains the outer locks. Interior fill and
        # the recessed scalp layer are deliberately excluded.
        attrs = mesh["primitives"][0]["attributes"]
        points = accessor(model, binary, attrs["POSITION"], 3) @ rotation.T + offset
        normals = accessor(model, binary, attrs["NORMAL"], 3) @ rotation.T
        theta = polar(points)[0]
        outward = np.sum(normals * (points - CENTER), axis=1) > .12
        region = outward & (points[:, 1] > 1.58) & (points[:, 1] < 1.94)
        region &= (abs(theta) > .72) & (abs(theta) < 1.80)
        count += int(region.sum())
        inside += int((region & (np.linalg.norm(points - CENTER, axis=1) < HEAD)).sum())
    return {"outer_surface_samples": count, "inside_head": inside}


def rail_samples(path):
    field = envelope(path)
    angles = np.tile([-2.57, 2.57], 4)
    heights = np.repeat([1.55, 1.65, 1.75, 1.85], 2)
    return np.round(sample(field, angles, heights), 4).tolist()


def verify(before, after):
    old, new = load(before), load(after)
    assert (old["revision"], new["revision"]) == ("297", "298")
    assert len(old["rows"]) == len(new["rows"]) == 90
    samples = {}
    for a, b in zip(old["rows"], new["rows"], strict=True):
        assert {k: v for k, v in a.items() if k != "parts"} == {k: v for k, v in b.items() if k != "parts"}
        assert a["parts"].keys() == b["parts"].keys()
        assert a["parts"]["hair"] != b["parts"]["hair"]
        for part in a["parts"].keys() - {"hair"}:
            if part != "headgear" or a["headwear"] != "pashmina":
                assert a["parts"][part] == b["parts"][part], (b["hair"], part)
        if (b["headwear"], b["top"], b["hairColor"]) == ("none", "open", "default"):
            samples[b["hair"]] = tuple(local_path(r["parts"]["hair"]) for r in (a,b))
    for name in ("hair-fits.json", "pashmina-fits.json"):
        prev, result = load(ROOT / "297" / name), load(REV / name)
        for build, styles in prev.items():
            for style, entry in styles.items():
                if build == "Feminine" and style in STYLES:
                    continue
                if name == "hair-fits.json":
                    for hat, finishes in entry["fits"].items():
                        for color, p in finishes.items():
                            assert (ROOT / "297" / p).resolve() == (
                                REV / result[build][style]["fits"][hat][color]).resolve()
                else:
                    for top, p in entry.items():
                        assert (ROOT / "297" / p).resolve() == (REV / result[build][style][top]).resolve()
    assets = {name: verify_asset(ROOT / source, REV / "assets" / name)
              for name, source in load(REV / "verification/sources.json").items()}
    curls = [temple_samples(p) for p in samples["curls"]]
    assert curls[1]["inside_head"] == 0, curls
    braids = [rail_samples(p) for p in samples["box-braids"]]
    assert max(braids[1]) < max(braids[0]), braids
    write("verification/geometry.json", {"selections": len(new["rows"]), "curls_temples_297_298": curls,
          "braid_rear_radii_297_298": braids, "assets": assets})
    print(len(new["rows"]), "selections and", len(assets), "GLBs checked")
    print("Curls temples", curls)
    print("Box braids rear", braids)


if __name__ == "__main__":
    verify(*(Path(arg) for arg in sys.argv[-2:]))
