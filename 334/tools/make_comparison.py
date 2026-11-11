"""Lay out the actual Blender renders beside the three concept directions."""
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont

STYLES=(("blowout","A"),("waves","B"),("asymmetric","C"))


def title_font(size):
    for path in ("DejaVuSans-Bold.ttf","C:/Windows/Fonts/arialbd.ttf"):
        try:
            return ImageFont.truetype(path,size)
        except OSError:
            pass
    return ImageFont.load_default(size=size)


def image_at(output,style,angle,size):
    with Image.open(output/"review"/f"{style}-{angle}.png") as source:
        return source.convert("RGBA").resize((size,size),Image.Resampling.LANCZOS)


def main(output):
    size=512
    canvas=Image.new("RGB",(3*size,2*size),"#f1f2f5")
    draw=ImageDraw.Draw(canvas)
    font=title_font(52)
    for x,(style,label) in enumerate(STYLES):
        for y,angle in enumerate(("threequarter","rearquarter")):
            portrait=image_at(output,style,angle,size)
            canvas.paste(portrait,(x*size,y*size),portrait)
        box=draw.textbbox((0,0),label,font=font)
        draw.text((x*size+(size-box[2])/2,5),label,font=font,fill="#32404d")
    canvas.save(output/"comparison.jpg",quality=95)

    thumb=245
    labels=("front","threequarter","profile","rightprofile","rear","rearquarter","above","underneath")
    contact=Image.new("RGB",(thumb*4,(thumb+25)*6),"#f1f2f5")
    draw=ImageDraw.Draw(contact)
    font=ImageFont.load_default(size=13)
    for s,(style,_) in enumerate(STYLES):
        for i,angle in enumerate(labels):
            x,y=(i%4)*thumb,(s*2+i//4)*(thumb+25)
            draw.text((x+9,y+3),style+" / "+angle,font=font,fill="#32404d")
            portrait=image_at(output,style,angle,thumb)
            contact.paste(portrait,(x,y+25),portrait)
    contact.save(output/"angles.jpg",quality=94)


if __name__=="__main__":
    main(Path(sys.argv[1]))
