from pathlib import Path
from PIL import Image,ImageDraw
import shutil
P=Path(__file__).parent;D=P.parent/'floating138/mobile-preview/249'
for f in (P/'fixtures').glob('*.png'):shutil.copy2(f,D/'references'/f.name)
looks=['straight','curls','side-sweep','box-braids'];out=Image.new('RGB',(960,len(looks)*390),'#243343');d=ImageDraw.Draw(out)
for row,style in enumerate(looks):
 for col,mode in enumerate(['before248','new']):
  f=P/'review2'/f'Feminine-{style}-{mode}-front.png';im=Image.open(f).convert('RGB').resize((480,480));out.paste(im.crop((0,30,480,390)),(col*480,row*390+30));d.text((col*480+5,row*390+5),style+' / '+('248' if mode=='before248' else '249'),fill='white')
out.save(D/'references/identity-comparison249.jpg',quality=94)
print('REFS249 final stable fixture references staged')
