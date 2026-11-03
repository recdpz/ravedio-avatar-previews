from pathlib import Path
from PIL import Image,ImageDraw
import json
P=Path(__file__).parent;cat=json.loads((P.parent/'floating138/mobile-preview/249/catalogue249.json').read_text());folder='review1' if '--source' in __import__('sys').argv else 'review2'
for b,bc in cat['builds'].items():
 styles=list(bc['hair']);top='open' if b=='Feminine' else 'tank'
 for name,angles in [('front',['front','threequarter','top']),('sides',['profile','rightprofile','rear']),('under',['underside'])]:
  out=Image.new('RGB',(len(angles)*256,len(styles)*280),'#243343');d=ImageDraw.Draw(out)
  for row,style in enumerate(styles):
   for col,angle in enumerate(angles):
    f=P/folder/f'{b}-{style}-{top}-{angle}.png' if folder=='review1' else P/folder/f'{b}-{style}-new-{angle}.png'
    if f.exists():out.paste(Image.open(f).convert('RGB').resize((256,256)),(col*256,row*280+24))
    d.text((col*256+4,row*280+5),style+' / '+angle,fill='white')
  out.save(P/folder/f'{b}-{name}-review250.jpg',quality=94)
if folder=='review2':
 looks=[('straight','profile'),('curls','rear'),('ponytail','rear')];out=Image.new('RGB',(768,3*410),'#243343');d=ImageDraw.Draw(out)
 for r,(style,angle) in enumerate(looks):
  for c,mode in enumerate(['before249','new']):
   f=P/'review2'/f'Feminine-{style}-{mode}-{angle}.png';out.paste(Image.open(f).convert('RGB'),(c*384,r*410+26));d.text((c*384+6,r*410+6),style+' / '+('249' if c==0 else '250'),fill='white')
 out.save(P/'review2/fit-comparison250.jpg',quality=94)
 for b,bc in cat['builds'].items():
  out=Image.new('RGB',(768,len(bc['hair'])*280),'#243343');d=ImageDraw.Draw(out)
  for r,style in enumerate(bc['hair']):
   for c,angle in enumerate(['front','profile','rear']):
    f=P/'review2'/f'{b}-{style}-cloth-hidden-{angle}.png';out.paste(Image.open(f).convert('RGB').resize((256,256)),(c*256,r*280+24));d.text((c*256+4,r*280+5),style+' / cloth off / '+angle,fill='white')
  out.save(P/'review2'/f'{b}-coverage-review250.jpg',quality=94)
 print('SHEETS250 final')
