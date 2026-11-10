"""Bake density-matched comparison assets against the same cool-white plate."""
from argparse import ArgumentParser
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

PLATE = [241, 244, 250]
SIZES = (24, 48, 72, 120)


def bake(root, tools):
    sys.path.insert(0, str(tools))
    from alpha_pack import Q, plate_transfer

    rows = json.loads((root / "looks.json").read_bytes())
    forward, reverse = plate_transfer()
    portraits = root / "portraits"
    portraits.mkdir(exist_ok=True)
    for look in rows:
        for mode in ("studio", "icon"):
            stem = f"{look['id']}-{mode}"
            with Image.open(root / "raw" / f"{stem}.png") as source:
                assert source.size == (384, 384) and source.mode == "RGBA"
                rgba = np.asarray(source)
            assert rgba[..., 3].min() == 0 and rgba[..., 3].max() == 255
            alpha = rgba[..., 3, None].astype(np.float64) / 255
            linear = forward[rgba[..., :3]] * alpha + forward[PLATE] * (1 - alpha)
            for size in SIZES:
                channels = [
                    np.asarray(Image.fromarray(linear[..., i].astype(np.float32)).resize(
                        (size, size), Image.Resampling.LANCZOS))
                    for i in range(3)
                ]
                rgb = reverse[np.rint(np.clip(np.stack(channels, axis=-1), 0, Q)).astype(np.int64)]
                assert rgb[0, 0].tolist() == PLATE
                Image.fromarray(rgb).save(portraits / f"{stem}-{size}.png")

    board = Image.new("RGB", (596, 622), "#151a24")
    draw = ImageDraw.Draw(board)
    font = ImageFont.load_default(size=14)
    draw.text((250, 13), "24 px", font=font, fill="white")
    draw.text((438, 13), "Enlarged", font=font, fill="white")
    for x, caption in ((205, "Studio"), (273, "Simple"), (399, "Studio"), (492, "Simple")):
        draw.text((x, 37), caption, font=font, fill="#b9c3d5")
    for index, look in enumerate(rows):
        y = 61 + index * 69
        draw.text((12, y + 22), look["label"], font=font, fill="white")
        for mode, x, size in (("studio", 213, 24), ("icon", 282, 24), ("studio", 390, 60), ("icon", 486, 60)):
            source = 24 if size == 24 else 120
            tile = Image.open(portraits / f"{look['id']}-{mode}-{source}.png")
            if tile.width != size:
                tile = tile.resize((size, size), Image.Resampling.LANCZOS)
            mask = Image.new("L", (4 * size, 4 * size))
            ImageDraw.Draw(mask).ellipse((0, 0, 4 * size - 1, 4 * size - 1), fill=255)
            board.paste(tile, (x, y + (60 - size) // 2), mask.resize((size, size), Image.Resampling.LANCZOS))
    board.save(root / "comparison.png")


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("tools", type=Path)
    args = parser.parse_args()
    bake(args.root, args.tools)
