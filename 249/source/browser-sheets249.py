from pathlib import Path
from PIL import Image,ImageDraw
import json
P=Path(__file__).parent;data=json.loads((P/'close249.json').read_text())
for build in ['Feminine','Masculine']:
 looks=[x for x in data['looks'] if x[0]==build]
 angles=['front','profile','rear','cloth-hidden'];out=Image.new('RGB',(4*280,len(looks)*310),'#243343');d=ImageDraw.Draw(out)
 for row,look in enumerate(looks):
  for col,angle in enumerate(angles):
   key='-'.join(look);im=Image.open(P/'browser'/f'{key}-{angle}.png').convert('RGB');im.thumbnail((280,280));out.paste(im,(col*280+(280-im.width)//2,row*310+30));d.text((col*280+4,row*310+6),look[1]+' / '+look[2]+' / '+angle,fill='white')
 out.save(P/'browser'/f'{build}-review249.jpg',quality=94)
print('BROWSER249 review matrices ready')
