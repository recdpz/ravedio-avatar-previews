"""Make matched before/after review boards from the browser captures."""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

before, after, out = map(Path, sys.argv[-3:])
font = "C:/Windows/Fonts/segoeui.ttf"
title = ImageFont.truetype(font, 26)
label = ImageFont.truetype(font, 17)


def sheet(name, heading, samples):
    page = Image.new("RGB", (1570, 653), "#16202b")
    draw = ImageDraw.Draw(page)
    draw.text((16, 11), heading, font=title, fill="#e2eaf3")
    for col, (caption, filename) in enumerate(samples):
        x = 16 + col * 258
        draw.text((x, 55), caption, font=label, fill="#e2eaf3")
        for row, (directory, revision) in enumerate(((before, "297"), (after, "298"))):
            y = 81 + row * 280
            draw.text((x, y), revision, font=label, fill="#e2eaf3")
            with Image.open(directory / (filename + ".png")) as source:
                image = source.convert("RGBA").crop((62, 107, 427, 478))
            image.thumbnail((246, 244), Image.Resampling.LANCZOS)
            page.paste("#29394c", (x, y + 24, x + 246, y + 268))
            page.paste(image, (x + (246 - image.width) // 2, y + 24), image)
    page.save(out / name, quality=95, subsampling=0)


sheet("changes.jpg", "Curls, Box Braids, and Bob without headwear", [
    ("Curls · front", "curls-none-open-default-visible-front"),
    ("Curls · right profile", "curls-none-open-default-visible-rightprofile"),
    ("Box Braids · rear quarter", "box-braids-none-open-default-visible-rearquarter"),
    ("Box Braids · back", "box-braids-none-open-default-visible-rear"),
    ("Bob · three-quarter", "bob-none-open-default-visible-threequarter"),
    ("Bob · back", "bob-none-open-default-visible-rear"),
])
styles = (("curls", "Curls"), ("box-braids", "Box Braids"), ("bob", "Bob"))
sheet("under-the-cloth.jpg", "Pashmina fit from the back with the cloth on and off", [
    (f"{label} · cloth {caption}", f"{style}-pashmina-open-default-{cloth}-rear")
    for style, label in styles for caption, cloth in (("on", "visible"), ("off", "hidden"))
])
