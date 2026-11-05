from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
import json,math
P=Path('E:/Ravedio-Avatar/catalogue262');D=P.parent/'floating138/mobile-preview/262';out=D/'references';out.mkdir(exist_ok=True)
BG='#29394c'
def board(name,rows,cols=4,w=260,h=280):
 im=Image.new('RGB',(cols*w,math.ceil(len(rows)/cols)*h),BG);d=ImageDraw.Draw(im)
 for i,(f,label) in enumerate(rows):
  x=i%cols*w;y=i//cols*h;pic=Image.open(f).convert('RGBA');bg=Image.new('RGBA',pic.size,BG);bg.alpha_composite(pic);pic=ImageOps.contain(bg.convert('RGB'),(w,h-28));im.paste(pic,(x+(w-pic.width)//2,y));d.text((x+5,y+h-25),label,fill='white')
 im.save(out/name,quality=91)
for b in ['Feminine','Masculine']:
 C=json.loads((D/'catalogue262.json').read_text())['builds'][b]
 board(b+'-tops262.jpg',[(P/'final-wardrobe'/f'{b}-{t}-shorts-{a}.png',C['tops'][t]['label']+' / '+a) for t in C['tops'] for a in ['front','profile','rightprofile','rear']])
 board(b+'-contacts262.jpg',[(P/'final-wardrobe'/f'{b}-{t}-contacts-{a}.png',C['tops'][t]['label']+' / '+a) for t in C['tops'] for a in ['front','profile','rightprofile','rear']])
 board(b+'-bottoms262.jpg',[(P/'final-wardrobe'/f'{b}-{bt}-detail-{a}.png',C['bottoms'][bt]['label']+' / '+a) for bt in C['bottoms'] for a in ['front','profile','rightprofile','rear','underside']],cols=5)
for b,top in [('Feminine','triangle'),('Feminine','sweatshirt'),('Masculine','sweatshirt')]:
 board(b+'-'+top+'-comparison262.jpg',[(P/(stage+'-wardrobe')/f'{b}-{top}-shorts-{a}.png',label+' / '+a) for stage,label in [('before','261'),('final','262')] for a in ['front','profile','rightprofile','rear']])
board('pants-comparison262.jpg',[(P/(stage+'-wardrobe')/f'{b}-pants-detail-{a}.png',b+' / '+label+' / '+a) for b in ['Feminine','Masculine'] for stage,label in [('before','261'),('final','262')] for a in ['front','profile','rear','underside']])
print('BOARDS262_COMPLETE')
