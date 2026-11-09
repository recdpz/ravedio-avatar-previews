"""Build the fit comparisons from existing review and native reference PNGs."""
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parents[1]
STYLES = ("curls", "straight", "box-braids", "twin-braids", "bob")
ANGLES = ("front", "threequarter", "profile", "rightprofile", "rear")
VIEWS = ("Front", "Three-quarter", "Left", "Right", "Rear")
FONT = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 18)


def put(sheet, path, x, y, size, text):
    image = Image.open(path).convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)
    sheet.paste("#eef2f7", (x, y, x+size, y+size))
    sheet.paste(image, (x, y), image)
    ImageDraw.Draw(sheet).text((x+6,y+size+4),text,font=FONT,fill="white")


def browser_path(folder, hair, visible, angle):
    return folder / f"{hair}-pashmina-open-default-{visible}-{angle}.png"


def build(before, after, old_native, native):
    dest = BASE / "verification"
    for style in STYLES:
        size = 235
        sheet = Image.new("RGB",(size*5,(size+31)*3),"#172031")
        rows = ((before,"visible","298"), (after,"visible","299"),
                (after,"hidden","299 · cloth hidden"))
        for row,(folder,cloth,name) in enumerate(rows):
            for i,(angle,view) in enumerate(zip(ANGLES,VIEWS)):
                caption = f"{name} / {view}" if row < 2 else (name if i == 0 else view)
                put(sheet,browser_path(folder,style,cloth,angle),i*size,row*(size+31),size,caption)
        sheet.save(dest / f"{style}.jpg",quality=92)

    size = 255
    sheet = Image.new("RGB",(size*3,(size+31)*2),"#172031")
    new = native / "Feminine/portrait-20"
    refs = ((old_native,"298 hair · fitted collar"),(new/"portrait-skin1-color.png","299 hair · 20°"),
            (new/"front-color.png","Front · scarf fit"),(new/"left-side-color.png","Left · scarf fit"),
            (new/"right-side-color.png","Right · scarf fit"),(new/"rear-color.png","Rear · scarf fit"))
    for i,(path,label) in enumerate(refs):
        put(sheet,path,(i%3)*size,(i//3)*(size+31),size,label)
    sheet.save(dest / "native-references.jpg",quality=94)


if __name__ == "__main__":
    build(*map(Path,sys.argv[-4:]))
