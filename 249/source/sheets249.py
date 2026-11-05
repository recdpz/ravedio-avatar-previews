from pathlib import Path
from PIL import Image,ImageDraw
import json
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview'
cat=json.loads((R/'249/catalogue249.json').read_text())
for b in cat['builds']:
 styles=list(cat['builds'][b]['hair'])
 for name,modes,angles in [('front',['uncovered','new','cloth-hidden'],['front']),('sides',['new'],['profile','rightprofile','rear']),('extra',['new'],['threequarter','top','underside'])]:
  cols=[(mode,angle) for mode in modes for angle in angles];out=Image.new('RGB',(len(cols)*256,len(styles)*282),'#243343');d=ImageDraw.Draw(out)
  for row,style in enumerate(styles):
   for col,(mode,angle) in enumerate(cols):
    f=P/'review2'/f'{b}-{style}-{mode}-{angle}.png';im=Image.open(f).convert('RGB').resize((256,256));out.paste(im,(col*256,row*282+26));d.text((col*256+4,row*282+5),style+' / '+mode+' / '+angle,fill='white')
  out.save(P/'review2'/f'{b}-{name}-review249.jpg',quality=94)
looks=['straight','curls','side-sweep','box-braids'];out=Image.new('RGB',(960,len(looks)*390),'#243343');d=ImageDraw.Draw(out)
for row,style in enumerate(looks):
 for col,mode in enumerate(['before248','new']):
  f=P/'review2'/f'Feminine-{style}-{mode}-front.png';im=Image.open(f).convert('RGB').resize((480,480));out.paste(im.crop((0,30,480,390)),(col*480,row*390+30));d.text((col*480+5,row*390+5),style+' / '+('248' if mode=='before248' else '249'),fill='white')
out.save(P/'review2/identity-comparison249.jpg',quality=94)
print('SHEETS249 reviewed hairstyles and248 comparison')
