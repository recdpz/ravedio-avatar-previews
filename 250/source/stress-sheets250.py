from pathlib import Path
from PIL import Image,ImageDraw
import json
P=Path(__file__).parent;q=json.loads((P/'top-proof250.json').read_text());groups={'Feminine-tops':[k for k in q if k.startswith('Feminine-curls-')],'Masculine-tops':[k for k in q if k.startswith('Masculine-taper-')],'Other-fits':[k for k in q if not k.startswith(('Feminine-curls-','Masculine-taper-'))]}
for name,keys in groups.items():
 out=Image.new('RGB',(4*256,len(keys)*280),'#243343');d=ImageDraw.Draw(out)
 for r,key in enumerate(keys):
  for c,angle in enumerate(['front','profile','rear','underside']):
   f=P/'review2'/f'{key}-stress250-{angle}.png';out.paste(Image.open(f).convert('RGB').resize((256,256)),(c*256,r*280+24));d.text((c*256+4,r*280+5),key.replace('Feminine-','F-').replace('Masculine-','M-')+' / '+angle,fill='white')
 out.save(P/'review2'/f'{name}-stress-review250.jpg',quality=94)
out=Image.new('RGB',(4*128,2*155),'#243343');d=ImageDraw.Draw(out)
for r,b in enumerate(['Feminine','Masculine']):
 for tone in range(4):
  out.paste(Image.open(P/'fixtures'/f'{b}-skin{tone}-portrait250-front.png').convert('RGB'),(tone*128,r*155+22));d.text((tone*128+5,r*155+4),b+' / '+str(tone),fill='white')
out.save(P/'review2/skin-readability-review250.jpg',quality=94)
print('STRESS_SHEETS250',len(q))
