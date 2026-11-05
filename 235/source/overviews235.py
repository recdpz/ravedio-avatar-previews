from pathlib import Path
from PIL import Image,ImageDraw
import json
P=Path(__file__).parent;c=json.loads((P/'fits235.json').read_text());styles={b:[k.split('-',1)[1] for k in c if k.startswith(b+'-')] for b in ['Feminine','Masculine']}
for build,ss in styles.items():
 for category,hats,angles,size in [('bandana',['headband'],['front','profile','rear','top'],192),('pashmina',['pashmina'],['front','profile','rear','top'],192),('remaining',['none','cap','beanie','bucket','cowboy','headband','ears','pashmina'],['threequarter','rightprofile','underside'],96)]:
  if category=='remaining':
   out=Image.new('RGB',(len(ss)*size,len(hats)*3*(size+16)),'white');d=ImageDraw.Draw(out)
   for col,s in enumerate(ss):
    for hi,hat in enumerate(hats):
     for ai,ang in enumerate(angles):row=hi*3+ai;out.paste(Image.open(P/'review2'/f'{build}-{s}--{hat}-{ang}.png').convert('RGB').resize((size,size)),(col*size,row*(size+16)+16));d.text((col*size+2,row*(size+16)+2),s+' '+hat[:3]+' '+ang[:2],fill='black')
  else:
   out=Image.new('RGB',(4*size,len(ss)*(size+20)),'white');d=ImageDraw.Draw(out)
   for row,s in enumerate(ss):
    for col,ang in enumerate(angles):out.paste(Image.open(P/'review2'/f'{build}-{s}--{hats[0]}-{ang}.png').convert('RGB'),(col*size,row*(size+20)+20));d.text((col*size+2,row*(size+20)+2),s+' '+ang,fill='black')
  out.save(P/'review2'/f'{build}-{category}-overview.jpg',quality=90)
