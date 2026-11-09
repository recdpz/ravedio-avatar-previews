"""Create the matching-camera Ponytail fit comparison."""
from pathlib import Path
import sys

REV = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(REV.parent/"309/tools"))
from boards import FONT, INK, LIGHT, board, paste

source = Path(sys.argv[1])
cases = [("beanie","default","Beanie"),("beanie","ombre","Beanie · Ombre"),
         ("none","default","Uncovered"),("cap","default","Cap"),("headband","default","Bandana")]
size = 212
left = 104
im,draw = board(left+4*(size+5)+10,83+len(cases)*(size+7),"Ponytail · Cuff and elastic",
                "Matched views. The wider tie follows the way the gathered hair leaves the scalp.")
for col,(revision,view) in enumerate([(310,"profile"),(311,"profile"),(310,"rearquarter"),(311,"rearquarter")]):
    title = "Side" if view=="profile" else "Rear three-quarter"
    draw.text((left+col*(size+5),61),f"{revision} · {title}",font=FONT(13),fill=INK)
    for row,(head,finish,label) in enumerate(cases):
        y = 79+row*(size+7)
        if col==0:
            draw.text((9,y+size//2-7),label,font=FONT(13),fill=LIGHT)
        paste(im,source/f"{revision}-{head}-{finish}-{view}.png",left+col*(size+5),y,size)
im.save(REV/"verification/ponytail.jpg",quality=94,optimize=True)
