"""Build review sheets from lossless, size-specific captures."""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parents[1]/"verification"
BG = "#131b29"
TILE = "#28384e"
LIGHT = "#eef3fc"
INK = "#b6c6db"
FONT = ImageFont.load_default


def board(w,h,title,note):
    im = Image.new("RGB",(w,h),BG)
    draw = ImageDraw.Draw(im)
    draw.text((16,11),title,font=FONT(21),fill=LIGHT)
    draw.text((16,40),note,font=FONT(13),fill=INK)
    return im,draw


def paste(im, path, x, y, size, bg=TILE, circle=False):
    art = Image.open(path).convert("RGBA")
    if art.width != size or art.height != size:
        art = art.resize((size,size),Image.Resampling.LANCZOS)
    tile = Image.new("RGBA",(size,size),bg)
    tile.alpha_composite(art)
    if circle:
        mask = Image.new("L",(size,size))
        ImageDraw.Draw(mask).ellipse((0,0,size-1,size-1),fill=255)
    else:
        mask = None
    im.paste(tile.convert("RGB"), (x,y), mask)


def write_hats(capture):
    styles = ["bob","ponytail","straight","curls","side-sweep","space-buns","twin-braids","box-braids",
              "sidepart","taper","buzz","curly-top","afro","flow","locs","middle-part"]
    angles = ["front","threequarter","profile","rightprofile","rear","rearquarter","top","underside"]
    s = 138
    pad = 91
    im,draw = board(pad+8*(s+4)+16,82+len(styles)*(s+4),"309 · Beanie fit across the catalogue",
                    "Eight views of each of the sixteen hairstyles. The covered hair stays in its authored fit.")
    for i,angle in enumerate(angles):
        draw.text((pad+i*(s+4)+4,60),angle.replace("quarter"," quarter"),font=FONT(12),fill=INK)
    for row,hair in enumerate(styles):
        y = 76+row*(s+4)
        draw.text((8,y+s//2-6),hair.replace("side-sweep","fringe"),font=FONT(12),fill=LIGHT)
        for col,angle in enumerate(angles):
            paste(im,capture/f"309-{hair}-{angle}.png",pad+col*(s+4),y,s)
    im.save(OUT/"beanies.jpg",quality=91,optimize=True)
    s = 241
    views = ["front","rightprofile","rearquarter","rear"]
    cases = [(308,"ponytail"),(309,"ponytail"),(308,"afro"),(309,"afro")]
    im,draw = board(16+4*(s+5),65+len(cases)*(s+26),"Beanie comparison",
                    "Ponytail and Afro with the same camera, hair and colors in both revisions.")
    for row,(revision,style) in enumerate(cases):
        y = 63+row*(s+26)
        draw.text((10,y),f"{revision} · {style.capitalize()}",font=FONT(14),fill=LIGHT)
        for col,angle in enumerate(views):
            paste(im,capture/f"{revision}-{style}-{angle}.png",8+col*(s+5),y+20,s)
    im.save(OUT/"closeups.jpg",quality=93,optimize=True)
    s = 150
    im,draw = board(16+8*(s+4),68+2*(s+25),"309 · Beanie with sprout and Ombre",
                    "All covered fits with the black recolor and the reseated sprout clip.")
    for i,hair in enumerate(styles):
        row,col=divmod(i,8)
        x,y=8+col*(s+4),64+row*(s+25)
        draw.text((x,y),hair.replace("side-sweep","fringe"),font=FONT(12),fill=LIGHT)
        paste(im,capture/f"309-{hair}-sprout.png",x,y+16,s)
    im.save(OUT/"sprouts.jpg",quality=91,optimize=True)


def write_browser_faces(capture):
    cases = [(hair,eyes,glasses) for hair in ("ponytail","flow")
             for eyes,glasses in (("original","none"),("tapered","none"),("hooded","none"),
                                  ("bean","none"),("original","reading"),("original","wayfarer"))]
    im,draw = board(762,85+len(cases)*72,"Browser preview · Brown skin",
                    "Native-size pixels on Cool white. Blender comparisons use the approved portrait lighting.")
    for x,title in [(218,"308 · 48 / 64 px"),(439,"309 · 48 / 64 px")]:
        draw.text((x,65),title,font=FONT(14),fill=LIGHT)
    for i,(hair,eyes,glasses) in enumerate(cases):
        y = 85+i*72
        draw.text((16,y+22),f"{hair} · {eyes if glasses=='none' else glasses}",font=FONT(14),fill=LIGHT)
        for x,rev in [(218,308),(439,309)]:
            for size,dx in [(48,0),(64,62)]:
                paste(im,capture/f"{rev}-{hair}-{eyes}-{glasses}-{size}.png",x+dx,y+(64-size)//2,size,"#F1F4FA",True)
    im.save(OUT/"browser-faces.png")


def write_blender_faces(before, candidate):
    cases = [
        ("r308-twin-jersey-pashmina",3,"Brown · No glasses"),
        ("r308-curls-pashmina",3,"Brown · Clear glasses"),
        ("r308-flow-cap",3,"Brown · Sunglasses"),
        ("r308-ponytail-beanie-jersey",2,"Tan · Ponytail and beanie"),
    ]
    im,draw = board(760,400,"Chat portraits · 15° on Cool white",
                    "Blender portraits at actual chat sizes, with the same framing and skin palette.")
    for x,title in [(200,"308"),(376,"309"),(552,"309 + extra fill")]:
        draw.text((x,65),title,font=FONT(15),fill=LIGHT)
    for row,(fixture,skin,label) in enumerate(cases):
        y=91+row*76
        draw.text((12,y+25),label,font=FONT(14),fill=LIGHT)
        stem=f"{fixture}-skin{skin}"
        images = [before/(stem+"-yaw15.png"),candidate/(stem+"-309.png"),candidate/(stem+"-fill.png")]
        for col,path in enumerate(images):
            for size,dx in [(48,0),(64,63)]:
                x=200+176*col+dx
                paste(im,path,x,y+(64-size)//2,size,"#F1F4FA",True)
    im.save(OUT/"readability.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("captures",type=Path)
    parser.add_argument("--baseline",type=Path)
    parser.add_argument("--portraits",type=Path)
    args = parser.parse_args()
    if bool(args.baseline) != bool(args.portraits):
        parser.error("Use --baseline and --portraits together")
    write_hats(args.captures)
    write_browser_faces(args.captures)
    if args.portraits:
        write_blender_faces(args.baseline,args.portraits)
