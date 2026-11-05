from pathlib import Path
from PIL import Image,ImageDraw
P=Path(__file__).parent/'output'
for i,angles in enumerate([['front','threequarter','profile'],['rightprofile','top','underside']]):
 im=Image.new('RGB',(900,650),(25,33,45));d=ImageDraw.Draw(im)
 for row,b in enumerate(['Feminine','Masculine']):
  for col,a in enumerate(angles):
   im.paste(Image.open(P/'renders'/f'{b}-export-{a}.png').convert('RGB').resize((300,300)),(col*300,row*325+25));d.text((col*300+5,row*325+6),b+' / '+a,fill='white')
 im.save(P/f'angles-{i}.jpg')
im=Image.new('RGB',(900,560),(25,33,45));d=ImageDraw.Draw(im)
for row,b in enumerate(['Feminine','Masculine']):
 for col,t in enumerate(range(4)):
  src=Image.open(P/'portraits'/f'{b}-tone{t}.png').convert('RGB');x=col*225+4;y=row*280+25
  d.text((x,row*280+4),b+' tone '+str(t),fill='white')
  for size in [32,48,64]:im.paste(src.resize((size,size),Image.Resampling.LANCZOS),(x,y));x+=size+9
  im.paste(src,(col*225+35,y+80))
im.save(P/'small229.jpg')
