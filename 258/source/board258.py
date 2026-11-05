from pathlib import Path
from PIL import Image,ImageDraw,ImageOps
P=Path('E:/Ravedio-Avatar/catalogue258');S=P/'browser-final'
def paste(im,f,x,y,w,h):
 pic=Image.open(f).convert('RGBA');bg=Image.new('RGBA',pic.size,'#29394c');bg.alpha_composite(pic);pic=ImageOps.contain(bg.convert('RGB'),(w,h));im.paste(pic,(x+(w-pic.width)//2,y))
angles=['front','threequarter','profile','rightprofile','rear','rearquarter','top','underside']
for st in ['taper','sidepart','curly-top']:
 im=Image.new('RGB',(1200,1180),'#29394c');d=ImageDraw.Draw(im)
 for i,(kind,a) in enumerate((kind,a) for kind in ['none','ombre'] for a in angles):
  x=i%4*300;y=i//4*295;paste(im,S/f'final-{st}-{kind}-{a}.png',x,y,300,270);d.text((x+5,y+274),kind+' / '+a,fill='white')
 im.save(P/f'{st}-final-review258.jpg',quality=94)
 im=Image.new('RGB',(1000,3300),'#29394c');d=ImageDraw.Draw(im)
 for i,(hat,a) in enumerate((hat,a) for hat in ['cap','beanie','bucket','cowboy','headband','ears','pashmina'] for a in angles):
  x=i%4*250;y=i//4*220;paste(im,S/f'final-{st}-{hat}-{a}.png',x,y,250,200);d.text((x+5,y+202),hat+' / '+a,fill='white')
 for j,a in enumerate(['front','rear']):paste(im,S/f'final-{st}-pashmina-cloth-off-{a}.png',j*250,3080,250,200);d.text((j*250+5,3282),'Cloth off / '+a,fill='white')
 im.save(P/f'{st}-covered-review258.jpg',quality=93)
print('BOARDS258_READY')
