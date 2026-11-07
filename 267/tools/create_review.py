from pathlib import Path
from PIL import Image,ImageDraw
import json,shutil
R=Path(__file__).resolve().parents[1];p=Path(__import__('sys').argv[1]);out=R/'verification'
for case in ['F-pony','F-straight','F-curls','F-pashmina','F-cap','M-short','M-long','M-cap','M-pashmina']:
 sheet=Image.new('RGB',(1120,976),(25,30,39));d=ImageDraw.Draw(sheet)
 for i,angle in enumerate(['front','threequarter','profile','rear']):
  for j,size in enumerate([0,5,8,10,12]):
   filename=f'{case}-{size if size else 5}-{angle}-'+('optimized' if size else 'source')+'.png';im=Image.open(p/filename).convert('RGBA');back=Image.new('RGB',im.size,(25,30,39));back.paste(im,mask=im.getchannel('A'));x=j*224;y=i*244;sheet.paste(back.resize((224,224)),(x,y+20));d.text((x+6,y+4),angle+' / '+('Current' if size==0 else f'{size}% smaller'),fill='white')
 sheet.save(out/f'{case}-sizes.jpg',quality=95)
for build in ['Feminine','Masculine']:
 sheet=Image.new('RGB',(760,840),(30,35,45));d=ImageDraw.Draw(sheet)
 for i,scale in enumerate([5,8,10,12]):
  for j,res in enumerate([48,64]):
   y=(i*2+j)*100;d.text((5,y+5),f'{scale}% / {res}px',fill='white')
   for skin in range(4):
    for k,view in enumerate(['source','optimized']):
     x=120+skin*160+k*78;d.text((x,y+3),str(skin)+' '+('Current' if k==0 else f'-{scale}%'),fill='white');im=Image.open(p/f'small-{build}-{scale}-{skin}-{res}-{view}.png').convert('RGBA');sheet.paste(im,(x,y+24),im)
 sheet.save(out/f'{build}-small-sizes.jpg',quality=99,subsampling=0)
shutil.copyfile(p/'checks.json',out/'browser.json');print('SHEETS267_READY')
