"""Compose matched long-beard views and 48/64 px chat crops."""
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont

current, previous = map(Path,sys.argv[1:])
out = current/"review"
out.mkdir(exist_ok=True)


def flatten(image):
    result = Image.new("RGB",image.size,"#f1f4fa")
    result.paste(image,(0,0),image)
    return result


for revision,root in ((318,previous),(319,current)):
    for skin in (0,3):
        for view in ("front","chat","turn","profile","opposite"):
            image = Image.open(root/"raw"/f"long-skin{skin}-{view}.png").convert("RGBA")
            assert image.size == (640,640)
            name = f"{revision}-skin{skin}"
            flatten(image.crop((88,20,552,484))).save(out/f"{name}-{view}.png")
            if view == "chat":
                for size in (48,64):
                    small = image.crop((70,20,570,520)).resize((size,size),Image.Resampling.LANCZOS)
                    flatten(small).save(out/f"{name}-{size}.png")


sheet = Image.new("RGB",(950,638),"#e5edf4")
pen = ImageDraw.Draw(sheet)
font = ImageFont.load_default(17)
pen.text((12,10),"Long beard · under-mouth contour",font=ImageFont.load_default(25),fill="#142638")
for column,(view,title) in enumerate((("chat","15° portrait"),("opposite","Opposite three-quarter"))):
    left = 12+column*470
    pen.text((left,53),title,font=font,fill="#142638")
    for row,(skin,tone) in enumerate(((0,"Light warm"),(3,"Deep"))):
        top = 87+row*272
        for i,revision in enumerate((318,319)):
            x = left+i*227
            pen.text((x,top),f"{revision} · {tone}",font=font,fill="#142638")
            stem = f"{revision}-skin{skin}"
            with Image.open(out/f"{stem}-{view}.png") as image:
                detail = image.crop((98,236,365,421)).resize((216,150),Image.Resampling.LANCZOS)
            sheet.paste(detail,(x,top+27))
            if view == "chat":
                with Image.open(out/f"{stem}-48.png") as chat:
                    sheet.paste(chat,(x,top+184))
                pen.text((x+56,top+197),"48 px",font=font,fill="#142638")
sheet.save(out/"comparison.jpg",quality=95,optimize=True)
