"""Recompose the RAVEDIO print at 2048 px using the existing jersey dyes."""
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

SIZE = 2048
SCALE = 4
PATTERN_WIDTH = 512 * SCALE


def wordmark(word, width, height, font_dir, color):
    font = ImageFont.truetype(str(font_dir / "impact.ttf"), 88 * SCALE)
    l, t, r, b = font.getbbox(word)
    mask = Image.new("L", (r - l + 1, b - t + 1))
    ImageDraw.Draw(mask).text((-l, -t), word, font=font, fill=255)
    mask = mask.resize((width * SCALE, height * SCALE), Image.Resampling.LANCZOS)
    mask = mask.transform(((width + 15) * SCALE, height * SCALE), Image.Transform.AFFINE,
                          (1, .15, -9 * SCALE, 0, 1, 0), Image.Resampling.BICUBIC)
    ink = Image.new("RGBA", mask.size, color)
    ink.putalpha(mask)
    return ink


def artwork(back, light, fonts):
    base = Image.new("RGBA", (PATTERN_WIDTH, PATTERN_WIDTH))
    draw = ImageDraw.Draw(base)
    primary = (40, 31, 58) if light else (238, 229, 255)
    accent = (30, 93, 101) if light else (132, 231, 218)
    for k in range(7):
        pts = [((30 + k * 75 + 9 * np.sin(y / 44 + k)) * SCALE, y * SCALE)
               for y in range(20, 501, 2)]
        draw.line(pts, fill=(*accent, 64), width=2 * SCALE)
    if back:
        base.alpha_composite(wordmark("RAVEDIO", 388, 77, fonts, primary), (56*SCALE, 41*SCALE))
        cx, cy = 256, 302
        for r in (67, 78, 109, 117):
            draw.ellipse(tuple(v * SCALE for v in (cx-r, cy-r, cx+r, cy+r)),
                         outline=(*accent, 235), width=3*SCALE)
        for k in range(12):
            a = k * np.pi / 6
            draw.line([((cx+r*np.cos(a))*SCALE, (cy+r*np.sin(a))*SCALE) for r in (121,139)],
                      fill=(*primary, 232), width=4*SCALE)
        star = [((cx+r*np.cos(k*np.pi/4))*SCALE, (cy+r*np.sin(k*np.pi/4))*SCALE)
                for k,r in enumerate([95,45]*4)]
        draw.line(star + star[:1], fill=(*primary, 250), width=6*SCALE, joint="curve")
        draw.ellipse(tuple(v * SCALE for v in (cx-24, cy-24, cx+24, cy+24)), fill=(*accent,255))
    else:
        # Keep whole letters on each sewn panel. The placket occupies
        # the space between the two halves of the same wordmark.
        base.alpha_composite(wordmark("RAVE", 174, 66, fonts, primary), (62*SCALE, 195*SCALE))
        base.alpha_composite(wordmark("DIO", 143, 66, fonts, primary), (271*SCALE, 195*SCALE))
        for y in (301, 334, 367):
            draw.line([(x*SCALE, (y+dy)*SCALE) for x,dy in ((170,0),(225,12),(280,-12),(340,0))],
                      fill=(*accent, 237), width=5*SCALE, joint="curve")
    font = ImageFont.truetype(str(fonts / "arial.ttf"), 17*SCALE)
    if back:
        draw.text((256*SCALE, 477*SCALE), "SOUND / TOGETHER", font=font, anchor="mm", fill=(*primary,255))
    else:
        draw.text((236*SCALE, 477*SCALE), "SOUND", font=font, anchor="rm", fill=(*primary,255))
        draw.text((278*SCALE, 477*SCALE), "TOGETHER", font=font, anchor="lm", fill=(*primary,255))
    return np.asarray(base)


def project(art, x, y):
    """Bilinear print projection from planar art into the existing cylindrical UV."""
    i = np.floor(x).astype(int)
    j = np.floor(y).astype(int)
    a = (x-i)[None,:,None]
    b = (y-j)[:,None,None]
    top = (1-a)*art[j[:,None], i] + a*art[j[:,None], i+1]
    lower = (1-a)*art[j[:,None]+1, i] + a*art[j[:,None]+1, i+1]
    return top*(1-b) + lower*b


def wave_weights(size, soft):
    """Sample the original 163 wave design at the requested resolution."""
    row = (np.arange(size, dtype=np.float32) + .5) * (512 / size) - .5
    x = row[None, :] - 290
    y = row[:, None] - 245
    radius = np.hypot(x, y)
    phase = 3*np.arctan2(y, x) + radius/39 + .3*np.sin(radius/65)
    wave = (.5 + .5*np.sin(phase))**4
    teal = np.sin(phase+.6) > 0
    edge = abs(np.sin(phase))
    echo = abs(np.sin(phase+.22))
    if soft:
        edge = np.clip((.067-edge)/.014, 0, 1)
        echo = np.clip((.041-echo)/.012, 0, 1)
    else:
        edge = (edge < .06).astype(np.float32)
        echo = (echo < .035).astype(np.float32)
    fabric = (1-edge)*(1-echo)
    return np.stack(((1-wave)*fabric, wave*teal*fabric, wave*~teal*fabric, edge*(1-echo), echo), axis=-1)


def build(root, out, original_pattern, fonts):
    colors = json.loads((root / "263/catalogue263.json").read_text(encoding="utf-8"))["colors"]["top"]
    theta = np.arange(SIZE) * 2 * np.pi / SIZE
    height = 1.03 + .405 * (1 - np.arange(SIZE) / SIZE)
    x = (.5 + .48*np.cos(theta)) * (PATTERN_WIDTH - 2)
    y = np.clip(1-(height-1.06)/.33, 0, 1) * (PATTERN_WIDTH - 2)
    valid = (height >= 1.06) & (height <= 1.39)
    back = np.sin(theta) > 0
    out.mkdir(parents=True, exist_ok=True)
    pattern_weights = wave_weights(SIZE, soft=True)

    for key, _, rgb in colors:
        path = original_pattern if key == "default" else root / "213/colors" / f"jersey-{key}-pattern.png"
        with Image.open(path) as im:
            assert im.width == im.height
            original = np.asarray(im.convert("RGB"), dtype=np.float32)
        basis = wave_weights(len(original), soft=False)
        palette, *_ = np.linalg.lstsq(basis.reshape(-1, 5), original.reshape(-1, 3), rcond=None)
        cloth = pattern_weights @ palette
        light = rgb is not None and sum(int(rgb[i:i+2],16)*w for i,w in zip((1,3,5),(.2126,.7152,.0722))) > 145
        for rear in (False, True):
            columns = back == rear
            view = PATTERN_WIDTH - 2 - x[columns] if rear else x[columns]
            print_layer = project(artwork(rear, light, fonts), view, y)
            a = print_layer[:,:,3:]/255 * valid[:,None,None]
            cloth[:,columns] = cloth[:,columns]*(1-a) + print_layer[:,:,:3]*a
        target = out / f"jersey-{key}.png"
        Image.fromarray(np.uint8(np.clip(cloth+.5, 0, 255))).save(target, optimize=True)
        print(target.name, flush=True)


if __name__ == "__main__":
    build(*map(Path, sys.argv[-4:]))
