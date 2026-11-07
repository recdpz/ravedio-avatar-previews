"""Verify exact color geometry, catalogue paths, and headwear and top clearance."""
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_fits import HATS, REV, ROOT, SOURCE, STYLE, cloth_paths, surface

sys.path.insert(0, str(ROOT / "275/tools"))
from build_hair import CAT
from build_bandanas import FIT
from verify_assets import geometry


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify():
    catalogue = json.loads((REV / "hair-fits.json").read_text(encoding="utf8"))
    before = json.loads((ROOT / "280/hair-fits.json").read_text(encoding="utf8"))
    assert catalogue["Feminine"]["space-buns"] == before["Feminine"]["space-buns"]
    fits = catalogue["Feminine"][STYLE]["fits"]
    assert set(fits) == set(HATS)
    assert (REV / fits["none"]["default"]).resolve() == SOURCE

    wardrobe = {}
    for top, entry in CAT["builds"]["Feminine"]["tops"].items():
        relative = entry["path"]
        fitted = FIT["components"].get(relative, {}).get("path", relative)
        wardrobe[top] = surface(ROOT / "270" / fitted)

    report = {}
    for hat, colors in fits.items():
        paths = {color: (REV / path).resolve() for color, path in colors.items()}
        original = geometry(paths["default"])
        ombre = geometry(paths["ombre"])
        assert original.keys() == ombre.keys(), hat
        assert len(original) == 1, (hat, "one hair primitive expected")
        for key in original:
            assert all(np.array_equal(a, b) for a, b in zip(original[key], ombre[key])), hat
        hair = surface(paths["default"])
        headwear = [len(hair.overlap(surface(path))) for path in cloth_paths(hat)] if hat != "none" else []
        tops = {top: len(hair.overlap(tree)) for top, tree in wardrobe.items()}
        assert not any(headwear), (hat, headwear)
        assert not any(tops.values()), (hat, tops)
        report[hat] = {
            "triangle_count": sum(len(arrays[2]) for arrays in original.values()),
            "same_geometry_both_colors": True,
            "headwear_intersections": headwear,
            "top_intersections": tops,
            "sha256": {color: digest(path) for color, path in paths.items()},
            "bytes": {color: path.stat().st_size for color, path in paths.items()},
        }
    (REV / "verification/assets.json").write_text(
        json.dumps({"approved_source": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
                    "approved_source_sha256": digest(SOURCE), "fits": report}, indent=2) + "\n",
        encoding="utf8", newline="\n",
    )
    print("Verified 8 fit pairs, exact color geometry, all headwear and all clothing")


if __name__ == "__main__":
    verify()
