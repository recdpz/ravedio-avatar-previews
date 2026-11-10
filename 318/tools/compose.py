"""Compose matched 317 and 318 crops and exact-size chat portraits."""
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont

current, previous = map(Path,sys.argv[1:])
out = current/"review"
out.mkdir(exist_ok=True)
background = "#f1f4fa"
styles = {"short":"Short beard","long":"Long beard"}
tones = {0:"Light warm",3:"Deep"}
views = ("front","chat","turn","profile","opposite")
baseline_cases = {"short":"flow-cap-bare-eyes","long":"flow-long"}


def read(path):
    image = Image.open(path).convert("RGBA")
    assert image.size == (640,640)
    return image


def flattened(image):
    result = Image.new("RGB",image.size,background)
    result.paste(image,(0,0),image)
    return result


def sizes(image, key):
    for size in (48,64):
        flattened(image.crop((70,20,570,520)).resize((size,size),Image.Resampling.LANCZOS)).save(out/f"{key}-{size}.png")


for style in styles:
    for tone in tones:
        tag = f"{style}-skin{tone}"
        original = read(previous/"raw"/f"317-{baseline_cases[style]}-skin{tone}-front.png")
        flattened(original.crop((88,20,552,484))).save(out/f"317-{tag}-chat.png")
        sizes(original,f"317-{tag}")
        for view in views:
            revised = read(current/"raw"/f"{tag}-{view}.png")
            flattened(revised.crop((88,20,552,484))).save(out/f"318-{tag}-{view}.png")
            if view == "chat":
                sizes(revised,f"318-{tag}")

sheet = Image.new("RGB",(1000,565),"#e5edf4")
draw = ImageDraw.Draw(sheet)
draw.text((12,9),"Connected beard · 317 and 318",font=ImageFont.load_default(25),fill="#142638")
for column,(style,label) in enumerate(styles.items()):
    for row,(tone,tone_label) in enumerate(tones.items()):
        x,y = 12+column*490,49+row*250
        draw.text((x,y),f"{label} · {tone_label}",font=ImageFont.load_default(17),fill="#142638")
        for index,revision in enumerate((317,318)):
            left = x+index*238
            stem = f"{revision}-{style}-skin{tone}"
            draw.text((left,y+26),str(revision),font=ImageFont.load_default(14),fill="#142638")
            image = Image.open(out/f"{stem}-chat.png")
            detail = image.crop((98,236,365,421)).resize((224,155),Image.Resampling.LANCZOS)
            sheet.paste(detail,(left,y+46))
            sheet.paste(Image.open(out/f"{stem}-48.png"),(left,y+201))
sheet.save(out/"comparison.jpg",quality=95,optimize=True)
