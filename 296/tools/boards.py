from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont

before, after, output = (Path(p) for p in sys.argv[-3:])
output.mkdir(exist_ok=True)
font = "C:/Windows/Fonts/segoeui.ttf"
title = ImageFont.truetype(font, 23)
label = ImageFont.truetype(font, 16)
text = "#e2eaf3"
bg = "#16202b"
panel = "#29394c"


def tile(page, path, x, y, size, crop=None):
    with Image.open(path) as source:
        img = source.convert("RGBA")
    if crop:
        img = img.crop(crop)
    img.thumbnail(size, Image.Resampling.LANCZOS)
    w, h = size
    page.paste(panel, (x, y, x + w, y + h))
    page.paste(img, (x + (w - img.width) // 2, y + (h - img.height) // 2), img)


angles = [
    ("front", "Front"), ("threequarter", "Three-quarter"), ("profile", "Left"),
    ("rightprofile", "Right"), ("rearquarter", "Rear three-quarter"), ("rear", "Back"),
    ("top", "Above"), ("underside", "Below"),
]
styles = {
    "Feminine": [
        ("bob", "Bob"), ("ponytail", "Ponytail"), ("straight", "Straight"), ("curls", "Curls"),
        ("side-sweep", "Long Bangs"), ("space-buns", "Space Buns"),
        ("twin-braids", "Twin Braids"), ("box-braids", "Box Braids"),
    ],
    "Masculine": [
        ("sidepart", "Crop"), ("taper", "Taper"), ("buzz", "Buzz"), ("curly-top", "Curly Top"),
        ("afro", "Afro"), ("flow", "Flow"), ("locs", "Locs"), ("middle-part", "Middle Part"),
    ],
}
for build, haircuts in styles.items():
    page = Image.new("RGB", (1366, 1309), bg)
    draw = ImageDraw.Draw(page)
    draw.text((15, 13), f"{build} pashmina fits  /  Revision 296", font=title, fill=text)
    for col, (_, caption) in enumerate(angles):
        draw.text((126 + col * 154, 51), caption, font=label, fill=text)
    for row, (style, caption) in enumerate(haircuts):
        y = 76 + 154 * row
        draw.text((15, y + 9), caption, font=label, fill=text)
        for col, (angle, _) in enumerate(angles):
            tile(page, after / f"{build}-{style}-tank-{angle}.png",
                 126 + col * 154, y, (150, 150))
    page.save(output / f"covered-{build.lower()}.jpg", quality=94, subsampling=0)

page = Image.new("RGB", (1434, 740), bg)
draw = ImageDraw.Draw(page)
draw.text((20, 14), "Pashmina drape and hair exits  /  Revisions 295 and 296", font=title, fill=text)
samples = [
    ("Curls · three-quarter", "curls-open-threequarter"),
    ("Curls · right side", "curls-open-rightprofile"),
    ("Straight · rear three-quarter", "straight-sweatshirt-rearquarter"),
    ("Box Braids · back", "box-braids-open-rear"),
]
for col, (caption, name) in enumerate(samples):
    x = 19 + col * 352
    draw.text((x, 54), caption, font=label, fill=text)
    for row, (folder, tag) in enumerate(((before, "295 / Before"), (after, "296 / Revised"))):
        y = 86 + row * 317
        draw.text((x, y), tag, font=label, fill=text)
        tile(page, folder / f"Feminine-{name}.png", x, y + 26, (342, 279), (54, 111, 434, 458))
page.save(output / "changes.jpg", quality=95, subsampling=0)
