"""Compose matched Deep and Tan reference portraits."""
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont

root = Path(sys.argv[1])
out = root/"review"
out.mkdir(exist_ok=True)
PLATE = "#f1f4fa"
INK = "#142638"
LOOKS = {
    "taper":"Taper + stubble",
    "buzz":"Buzz",
    "long-beard":"Flow + long beard",
    "long-bangs":"Long bangs",
    "curls-pashmina":"Curls + pashmina",
    "ponytail-ombre":"Ombre ponytail + beanie",
    "ponytail-bare-ombre":"Ombre ponytail",
}


def flatten(image):
    result = Image.new("RGB",image.size,PLATE)
    result.paste(image,(0,0),image)
    return result


for name in LOOKS:
    for revision in (0,1):
        for skin in (2,3):
            for angle in ("chat","side","opposite") if skin==3 else ("chat",):
                key = f"{name}-{revision}-skin{skin}"
                with Image.open(root/"raw"/f"{key}-{angle}.png") as source:
                    image = source.convert("RGBA")
                assert image.size == (640,640)
                flatten(image.crop((88,20,552,484))).save(out/f"{key}-{angle}.png")
                if angle=="chat":
                    for size in (48,64):
                        chat = image.crop((70,20,570,520)).resize((size,size),Image.Resampling.LANCZOS)
                        flatten(chat).save(out/f"{key}-{size}.png")

sheet = Image.new("RGB",(1056,60+250*((len(LOOKS)+1)//2)),"#e5edf4")
draw = ImageDraw.Draw(sheet)
draw.text((12,10),"Brown hair on Deep skin",font=ImageFont.load_default(24),fill=INK)
for i,(name,label) in enumerate(LOOKS.items()):
    x,y = 12+(i%2)*525,50+(i//2)*250
    draw.text((x,y),label,font=ImageFont.load_default(17),fill=INK)
    for revision,title in ((0,"Previous"),(1,"Chestnut")):
        left = x+revision*252
        draw.text((left,y+24),title,font=ImageFont.load_default(14),fill=INK)
        key = f"{name}-{revision}-skin3"
        with Image.open(out/f"{key}-chat.png") as portrait:
            sheet.paste(portrait.resize((181,181),Image.Resampling.LANCZOS),(left,y+45))
        with Image.open(out/f"{key}-48.png") as chat:
            sheet.paste(chat,(left+184,y+164))
sheet.save(out/"comparison.jpg",quality=95,optimize=True)
