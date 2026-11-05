from pathlib import Path
from PIL import Image,ImageDraw
P=Path(__file__).parent/'output';keys=['original','almond','tapered','hooded','bean','squint']
im=Image.new('RGB',(1120,915),(25,33,45));d=ImageDraw.Draw(im)
for i,key in enumerate(keys):
 row=i//2;pair=i%2
 for j,(tag,label) in enumerate([('before-front','Without'),('export-front','Lashes')]):
  x=(pair*2+j)*280;im.paste(Image.open(P/'renders'/f'Feminine-{key}-{tag}.png').convert('RGB').resize((280,280)),(x,row*305+25));d.text((x+5,row*305+5),key+' / '+label,fill='white')
im.save(P/'comparison234.jpg')
for key in keys:
 im=Image.new('RGB',(900,280),(25,33,45));d=ImageDraw.Draw(im)
 for col,t in enumerate(range(4)):
  src=Image.open(P/'portraits'/f'Feminine-{key}-tone{t}.png').convert('RGB');x=col*225+4;y=25;d.text((x,4),key+' tone '+str(t),fill='white')
  for size in [32,48,64]:im.paste(src.resize((size,size),Image.Resampling.LANCZOS),(x,y));x+=size+9
  im.paste(src,(col*225+35,y+80))
 im.save(P/f'small-{key}.jpg')
 im=Image.new('RGB',(1120,305),(25,33,45));d=ImageDraw.Draw(im)
 for col,angle in enumerate(['profile','rightprofile','top','underside']):
  im.paste(Image.open(P/'renders'/f'Feminine-{key}-export-{angle}.png').convert('RGB').resize((280,280)),(col*280,25));d.text((col*280+5,5),key+' / '+angle,fill='white')
 im.save(P/f'angles-{key}.jpg')
