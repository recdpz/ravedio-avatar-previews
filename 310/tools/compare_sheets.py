"""Assemble same-camera comparison boards from the local review captures."""
from pathlib import Path
import sys

REV = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(REV.parent/"309/tools"))
from boards import board, FONT, INK, LIGHT, paste

STYLES = ["bob","ponytail","straight","curls","side-sweep","space-buns","twin-braids","box-braids",
          "sidepart","taper","buzz","curly-top","afro","flow","locs","middle-part"]
ANGLES = [("front","Front"),("threequarter","Three-quarter"),("profile","Left side"),
          ("rightprofile","Right side"),("rear","Back"),("rearquarter","Rear three-quarter"),
          ("top","Above"),("underside","Underneath")]
OUT = REV/"verification"


def capture(source, im, revision, case, view, x, y, size):
    paste(im,source/f"{revision}-{case}-{view}.png",x,y,size)


def all_hats(source):
    s = 132
    pad = 96
    im,draw = board(pad+8*(s+4)+12,80+16*(s+4),"310 · Fitted beanies",
                    "Sixteen hairstyles in eight views. Each cuff is shaped for the covered hair.")
    for i,(_,label) in enumerate(ANGLES):
        draw.text((pad+i*(s+4),61),label,font=FONT(11),fill=INK)
    for row,hair in enumerate(STYLES):
        y = 78+row*(s+4)
        draw.text((10,y+s//2-6),hair.replace("side-sweep","long bangs"),font=FONT(12),fill=LIGHT)
        for col,(view,_) in enumerate(ANGLES):
            capture(source,im,310,hair,view,pad+col*(s+4),y,s)
    im.save(OUT/"beanies.jpg",quality=91,optimize=True)


def hat_comparison(source):
    s = 232
    im,draw = board(88+4*(s+5)+12,85+4*(s+8),"Beanie fit and knit detail",
                    "Same camera and colors. The tighter cuff follows the style beneath it.")
    for i,label in enumerate(["309 · Profile","310 · Profile","309 · Rear three-quarter","310 · Rear three-quarter"]):
        draw.text((88+i*(s+5),61),label,font=FONT(13),fill=INK)
    for row,hair in enumerate(["ponytail","buzz","curls","locs"]):
        y = 80+row*(s+8)
        draw.text((10,y+s//2-7),hair.capitalize(),font=FONT(13),fill=LIGHT)
        for col,(rev,view) in enumerate([(309,"profile"),(310,"profile"),(309,"rearquarter"),(310,"rearquarter")]):
            capture(source,im,rev,hair,view,88+col*(s+5),y,s)
    im.save(OUT/"closeups.jpg",quality=94,optimize=True)


def twin_comparison(source):
    s = 260
    cases = [("open","Button-up"),("jersey","Jersey"),("tank","Tank"),("sweatshirt","Hoodie")]
    im,draw = board(95+4*(s+4)+12,85+len(cases)*(s+6),"Twin Braids · Shoulder turn",
                    "The plaits stay nearer the side of the face, then arc forward as they approach the shoulders.")
    for i,label in enumerate(["309 · Side","310 · Side","309 · Three-quarter","310 · Three-quarter"]):
        draw.text((95+i*(s+4),61),label,font=FONT(13),fill=INK)
    for row,(top,name) in enumerate(cases):
        y = 80+row*(s+6)
        draw.text((10,y+s//2-7),name,font=FONT(13),fill=LIGHT)
        for col,(rev,view) in enumerate([(309,"rightprofile"),(310,"rightprofile"),
                                        (309,"threequarter"),(310,"threequarter")]):
            capture(source,im,rev,"braids-"+top,view,95+col*(s+4),y,s)
    im.save(OUT/"twins.jpg",quality=93,optimize=True)


if __name__=="__main__":
    source = Path(sys.argv[1])
    all_hats(source)
    hat_comparison(source)
    twin_comparison(source)
