"""Build the native chat crop comparison from the approved Blender reference renders."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

import numpy as np
from PIL import Image

LOOKS = [
    ("ponytail-jersey-skin0", 321, 0, "Feminine", "none"),
    ("flow-long-beard-skin0", 322, 0, "Masculine", "long"),
    ("ponytail-jersey-skin1", 321, 1, "Feminine", "none"),
    ("flow-short-beard-skin1", 322, 1, "Masculine", "short"),
    ("ponytail-jersey-skin2", 321, 2, "Feminine", "none"),
    ("flow-short-beard-skin2", 322, 2, "Masculine", "short"),
    ("ponytail-jersey-skin3", 321, 3, "Feminine", "none"),
    ("flow-long-beard-skin3", 322, 3, "Masculine", "long"),
]
CROP = (30, 8, 354, 332)
PLATE = [241, 244, 250]
SIZES = (48, 72, 120)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(work, tools, output):
    sys.path.insert(0, str(tools))
    from alpha_pack import Q, plate_transfer

    forward, reverse = plate_transfer()
    files, appearances = {}, []
    for identity, rev, skin, build, groom in LOOKS:
        feminine = build == "Feminine"
        # The legacy sprite catalogue has a Ponytail and Side part. It has no Flow
        # sprite or separate beard lengths. Both map to the Full beard sprite.
        profile = [0x40 | skin << 4 | (3 if feminine else 5) << 1, 0x40 if feminine else 0x4D,
                   17 if feminine else 3]
        appearances.append(dict(id=identity, build=build, skin=skin, groom=groom,
                                eye="bean", hair_tone=0, top="jersey" if feminine else "sweatshirt",
                                top_tone=0, legacy_profile=profile))
        references = work / f"native{rev}/handoff/references"
        raw = references / f"r{rev}-{identity}.png"
        with Image.open(raw) as source:
            assert source.size == (384, 384)
            rgba = np.asarray(source.convert("RGBA"))
        alpha = rgba[..., 3, None].astype(np.float64) / 255
        linear = forward[rgba[..., :3]] * alpha + forward[PLATE] * (1 - alpha)
        for mode in ("current", "tight"):
            for size in SIZES:
                filename = f"{mode}/{identity}{'' if size == 120 else f'-{size}'}.png"
                path = output / filename
                path.parent.mkdir(parents=True, exist_ok=True)
                if mode == "current" and size in (48, 120):
                    shutil.copyfile(references / f"r{rev}-{identity}-cool-{size}.png", path)
                else:
                    box = CROP if mode == "tight" else None
                    pixels = np.stack([np.asarray(Image.fromarray(linear[..., channel].astype(np.float32)).resize(
                        (size, size), Image.Resampling.LANCZOS, box=box)) for channel in range(3)], axis=-1)
                    rgb = reverse[np.rint(np.clip(pixels, 0, Q)).astype(np.int64)]
                    Image.fromarray(rgb).save(path)
                if size == 120:
                    files[filename] = sha(path)
    manifest = dict(revision=323, yaw_degrees=15, source_crop=list(CROP), plate=PLATE,
                    size=120, appearances=appearances, files=files)
    (output / "mobile-portraits.json").write_text(json.dumps(manifest, indent=2) + "\n", newline="\n")
    print(sha(output / "mobile-portraits.json"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("work", "tools", "output"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    build(args.work, args.tools, args.output)
