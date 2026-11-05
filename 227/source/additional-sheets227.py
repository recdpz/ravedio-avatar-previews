from pathlib import Path
from PIL import Image,ImageDraw
P=Path(__file__).parent/'revision227'
files=sorted((P/'roundtrip').glob('*-front.png'))
for start in range(0,len(files),5):
 out=Image.new('RGB',(4*220,5*244),(25,33,45));d=ImageDraw.Draw(out)
 for row,file in enumerate(files[start:start+5]):
  key=file.name[:-10]
  for col,angle in enumerate(['rightprofile','underside','body','front']):
   f=P/'roundtrip'/(key+'-'+angle+'.png')
   if f.exists():out.paste(Image.open(f).convert('RGB').resize((220,220)),(col*220,row*244+24))
   d.text((col*220+4,row*244+5),key+' '+angle,fill='white')
 out.save(P/f'contacts-{start//5}.jpg')
for start in range(0,len(files),5):
 out=Image.new('RGB',(4*128,5*154),(25,33,45));d=ImageDraw.Draw(out)
 for row,file in enumerate(files[start:start+5]):
  key=file.name[:-10]
  for col in range(4):
   f=P/'portraits'/(key+'-tone'+str(col)+'.png')
   if f.exists():out.paste(Image.open(f).convert('RGB'),(col*128,row*154+26))
   d.text((col*128+3,row*154+3),key.replace('Feminine-','F ').replace('Masculine-','M '),fill='white')
 out.save(P/f'tones-{start//5}.jpg')
for key in sorted(set(f.name.split('--')[0] for f in (P/'fit-review').glob('*.png'))):
 hats=['cap','beanie','bucket','cowboy','headband','ears','pashmina'];out=Image.new('RGB',(4*192,7*216),(25,33,45));d=ImageDraw.Draw(out)
 for row,hat in enumerate(hats):
  for col,angle in enumerate(['front','profile','rear','top']):
   f=P/'fit-review'/(key+'--'+hat+'-'+angle+'.png')
   if f.exists():out.paste(Image.open(f).convert('RGB').resize((192,192)),(col*192,row*216+24))
   d.text((col*192+3,row*216+3),hat+' '+angle,fill='white')
 out.save(P/('fit-'+key+'.jpg'))
