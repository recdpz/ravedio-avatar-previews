"""Build comparisons using the same camera on 311 and 312."""
from pathlib import Path
import sys

REV = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(REV.parent/"309/tools"))
from boards import FONT, INK, LIGHT, board, paste

source = Path(sys.argv[1])
s = 256
cases = [("none","front","Bare · Front"),("none","top","Bare · Above"),
         ("beanie","rightprofile","Beanie · Side"),("beanie","front","Beanie · Front")]
w = 128+4*(s+5)+10
im,draw = board(w,86+2*(s+7),"312 · Ponytail and front locks",
                "The tail sits to the viewer's right, the gather is closed, and the fringe curves down from the cuff.")
for col,(style,angle,label) in enumerate(cases):
    x = 128+col*(s+5)
    draw.text((x,60),label,font=FONT(13),fill=INK)
    for row,revision in enumerate([311,312]):
        y = 80+row*(s+7)
        draw.text((14,y+s//2),str(revision),font=FONT(16),fill=LIGHT)
        paste(im,source/f"{revision}-{style}-default-{angle}.png",x,y,s)
im.save(REV/"verification/ponytail.jpg",quality=94,optimize=True)

s = 174
im,draw = board(14+7*(s+4),85+2*(s+5),"312 · Covered ponytail fit",
                "Rear three-quarter views of each headwear option, in both hair finishes.")
hats = [("beanie","Beanie"),("cap","Cap"),("headband","Bandana"),("bucket","Bucket hat"),
        ("cowboy","Cowboy hat"),("ears","Ears"),("pashmina","Pashmina")]
for col,(style,label) in enumerate(hats):
    x = 7+col*(s+4)
    draw.text((x,60),label,font=FONT(13),fill=LIGHT)
    for row,finish in enumerate(["default","ombre"]):
        paste(im,source/f"312-{style}-{finish}-rearquarter.png",x,80+row*(s+5),s)
im.save(REV/"verification/headwear.jpg",quality=93,optimize=True)
