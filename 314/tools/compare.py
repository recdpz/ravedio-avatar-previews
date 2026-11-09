"""Show the corrected offset from the same review cameras."""
from pathlib import Path
import sys

REV = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(REV.parent/"309/tools"))
from boards import FONT, INK, LIGHT, board, paste

old,new = map(Path,sys.argv[1:])
s = 244
views = [("none","front","Bare · Front"),("none","top","Bare · Above"),
         ("beanie","front","Beanie · Front"),("beanie","profile","Beanie · Side")]
im,draw = board(93+len(views)*(s+4),81+2*(s+6),"314 · Ponytail placement",
                "A small move toward center from 313. The gather stays on the viewer's left.")
for col,(head,angle,label) in enumerate(views):
    x = 86+col*(s+4)
    draw.text((x,60),label,font=FONT(13),fill=INK)
    for row,(rev,source) in enumerate([(313,old),(314,new)]):
        y = 79+row*(s+6)
        draw.text((12,y+s//2),str(rev),font=FONT(16),fill=LIGHT)
        paste(im,source/f"{rev}-{head}-default-{angle}.png",x,y,s)
im.save(REV/"verification/ponytail.jpg",quality=94,optimize=True)

hats = [("beanie","Beanie"),("cap","Cap"),("headband","Bandana"),("bucket","Bucket hat"),
        ("cowboy","Cowboy hat"),("ears","Ears"),("pashmina","Pashmina")]
s = 174
im,draw = board(14+len(hats)*(s+4),85+2*(s+5),"314 · Headwear fit",
                "Both hair finishes from the rear three-quarter camera.")
for col,(head,label) in enumerate(hats):
    x = 7+col*(s+4)
    draw.text((x,60),label,font=FONT(13),fill=INK)
    for row,finish in enumerate(["default","ombre"]):
        paste(im,new/f"314-{head}-{finish}-rearquarter.png",x,80+row*(s+5),s)
im.save(REV/"verification/headwear.jpg",quality=93,optimize=True)
