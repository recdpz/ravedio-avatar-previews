from pathlib import Path
from PIL import Image,ImageDraw
import json
P=Path(__file__).parent;data=json.loads((P/'top-proof249.json').read_text())
groups={'Feminine-base':[k for k in data if k.startswith('Feminine-curls-')],'Feminine-other':[k for k in data if k.startswith('Feminine-') and not k.startswith('Feminine-curls-')],'Masculine':[k for k in data if k.startswith('Masculine-')]}
for name,keys in groups.items():
 out=Image.new('RGB',(900,len(keys)*326),'#243343');d=ImageDraw.Draw(out)
 for row,key in enumerate(keys):
  for col,angle in enumerate(['profile','rear','underside']):
   im=Image.open(P/'review2'/f'{key}-stress249-{angle}.png').convert('RGB').resize((300,300));out.paste(im,(col*300,row*326+26));d.text((col*300+4,row*326+5),key.split('-',1)[1]+' / '+angle,fill='white')
 out.save(P/'review2'/f'{name}-stress-review249.jpg',quality=94)
out=Image.new('RGB',(4*192,2*170),'#243343');d=ImageDraw.Draw(out)
for row,b in enumerate(['Feminine','Masculine']):
 for tone in range(4):
  im=Image.open(P/'fixtures'/f'{b}-skin{tone}-portrait249-front.png').convert('RGB');out.paste(im,(tone*192+32,row*170+25));d.text((tone*192+4,row*170+5),b+' / '+str(tone),fill='white')
out.save(P/'review2/skin-readability249.jpg',quality=94)
print('STRESS249 all22 close matrices and four-tone readability ready')
