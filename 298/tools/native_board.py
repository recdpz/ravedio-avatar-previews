"""Create the review sheet without changing the source references."""
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont

assets, output = map(Path, sys.argv[-2:])
bg, panel, ink = "#172231", "#293747", "#e9eef4"
page = Image.new("RGB", (1404, 830), bg)
draw = ImageDraw.Draw(page)
label = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 16)
title = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 25)


def portrait(build, name, x, y, size):
    with Image.open(assets / build / (name + ".png")) as source:
        image = source.convert("RGBA")
    if size != image.width:
        image = image.resize((size, size), Image.Resampling.LANCZOS)
    page.paste(panel, (x, y, x + size, y + size))
    page.paste(image, (x, y), image)


draw.text((20, 15), "Revision 298 · Reference views for mobile testing", fill=ink, font=title)
for col, (build, skin, caption) in enumerate((
    ("Feminine", 0, "Curls · Fair"), ("Feminine", 3, "Curls · Brown"),
    ("Masculine", 0, "Flow · Fair"), ("Masculine", 3, "Flow · Brown")
)):
    x = 20 + col * 346
    draw.text((x, 63), caption, fill=ink, font=label)
    portrait(build, f"front-skin{skin}-512-color", x, 91, 324)
    for off, size, label_text, suffix in (
        (0, 120, "Blender 120 px", "color"), (133, 64, "Blender 64", "color"),
        (217, 64, "Web 64", "web"), (285, 48, "48", "color")
    ):
        draw.text((x + off, 428), label_text, fill=ink, font=label)
        portrait(build, f"front-skin{skin}-{size}-{suffix}", x + off, 453, size)
for col, (build, angle, caption) in enumerate((
    ("Feminine", "rightprofile", "Curls · right side"),
    ("Feminine", "rear", "Curls · back"),
    ("Masculine", "rightprofile", "Flow · right side"),
    ("Masculine", "rear", "Flow · back"),
)):
    x = 20 + col * 346
    draw.text((x, 590), caption, fill=ink, font=label)
    portrait(build, f"{angle}-skin1-512-color", x + 54, 615, 194)
page.save(output, quality=96, subsampling=0)
