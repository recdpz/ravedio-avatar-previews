"""Build matched review sheets from the interactive renders."""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

before, after, out = map(Path, sys.argv[-3:])
font = "C:/Windows/Fonts/segoeui.ttf"
title = ImageFont.truetype(font, 25)
label = ImageFont.truetype(font, 18)


def sheet(name, heading, samples):
    page = Image.new("RGB", (1406, 726), "#16202b")
    draw = ImageDraw.Draw(page)
    draw.text((18, 12), heading, font=title, fill="#e2eaf3")
    for col, (caption, filename) in enumerate(samples):
        x = 18 + col * 346
        draw.text((x, 53), caption, font=label, fill="#e2eaf3")
        for row, (directory, revision) in enumerate(((before, "296"), (after, "297"))):
            y = 82 + row * 316
            draw.text((x, y), revision, font=label, fill="#e2eaf3")
            with Image.open(directory / (filename + ".png")) as source:
                image = source.convert("RGBA").crop((64, 107, 425, 456))
            image.thumbnail((334, 281), Image.Resampling.LANCZOS)
            page.paste("#29394c", (x, y + 25, x + 334, y + 306))
            page.paste(image, (x + (334 - image.width) // 2, y + 25), image)
    page.save(out / name, quality=95, subsampling=0)


sheet("changes.jpg", "Curls and Straight without headwear", [
    ("Curls · three-quarter", "curls-none-open-default-visible-threequarter"),
    ("Curls · back", "curls-none-open-default-visible-rear"),
    ("Straight · three-quarter", "straight-none-open-default-visible-threequarter"),
    ("Straight · back", "straight-none-open-default-visible-rear"),
])
sheet("under-the-cloth.jpg", "Pashmina fit with the cloth on and off", [
    ("Curls · cloth on", "curls-pashmina-open-default-visible-rear"),
    ("Curls · cloth off", "curls-pashmina-open-default-hidden-rear"),
    ("Straight · cloth on", "straight-pashmina-open-default-visible-rear"),
    ("Straight · cloth off", "straight-pashmina-open-default-hidden-rear"),
])
