from pathlib import Path
from PIL import Image,ImageDraw
import json,shutil
R=Path(__file__).resolve().parents[1];p=Path(__import__('sys').argv[1]);out=R/'verification'
for name in ['F-pony-hoodie','F-straight-tank','F-curls-shirt','F-pony-pashmina','F-straight-pashmina','F-curls-pashmina','M-taper-hoodie','M-flow-tshirt','M-middle-shirt','M-taper-pashmina','M-flow-pashmina']+['groom-'+g for g in ['stubble','mustache','patch','goatee','short','long']]:
 sheet=Image.new('RGB',(1024,1100),(22,25,33));draw=ImageDraw.Draw(sheet)
 for i,a in enumerate(['front','threequarter','profile','rightprofile','rearquarter','rear','top','underside']):
  for j,v in enumerate(['source','optimized']):
   x=(i%2*2+j)*256;y=i//2*275;sheet.paste(Image.open(p/f'{name}-{a}-{v}.png').convert('RGB').resize((256,256)),(x,y+19));draw.text((x+5,y+3),a+' '+('oval' if j==0 else 'sphere'),fill='white')
 sheet.save(out/f'{name}-contact.jpg',quality=92)
for build in ['Feminine','Masculine']:
 sheet=Image.new('RGB',(760,840),(30,35,45));d=ImageDraw.Draw(sheet)
 for i,eye in enumerate(['original','tapered','hooded','bean']):
  for j,size in enumerate([48,64]):
   y=(i*2+j)*100;d.text((5,y+5),eye+' '+str(size),fill='white')
   for skin in range(4):
    for k,v in enumerate(['source','optimized']):
     x=120+skin*160+k*78;d.text((x,y+3),str(skin)+' '+('oval' if k==0 else 'sphere'),fill='white');im=Image.open(p/f'small-{build}-{eye}-{skin}-{size}-{v}.png').convert('RGBA');sheet.paste(im,(x,y+24),im)
 sheet.save(out/f'{build}-small-portraits.jpg',quality=99,subsampling=0)
shutil.copyfile(p/'checks.json',out/'browser.json');print('REVIEW_SHEETS266_COMPLETE')
