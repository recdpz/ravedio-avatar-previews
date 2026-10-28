from pathlib import Path
from PIL import Image,ImageDraw
P=Path(__file__).parent/'output'
labels=[('original','Original'),('tapered','Tapered oval'),('hooded','Soft hooded'),('bean','Rounded bean')]
for angle in ['front','threequarter']:
 im=Image.new('RGB',(1120,610),(25,33,45));d=ImageDraw.Draw(im)
 for row,b in enumerate(['Feminine','Masculine']):
  for col,(k,label) in enumerate(labels):
   f=P/'renders'/f'{b}-original-front.png' if k=='original' else P/'renders'/f'{b}-{k}-export-{angle}.png'
   im.paste(Image.open(f).convert('RGB').resize((280,280)),(col*280,row*305+25));d.text((col*280+7,row*305+5),b+' / '+label+(' (front)' if k=='original' and angle!='front' else ''),fill='white')
 im.save(P/f'comparison-{angle}.jpg')
for key in ['tapered','hooded','bean']:
 im=Image.new('RGB',(900,560),(25,33,45));d=ImageDraw.Draw(im)
 for row,b in enumerate(['Feminine','Masculine']):
  for col,t in enumerate(range(4)):
   src=Image.open(P/'portraits'/f'{b}-{key}-tone{t}.png').convert('RGB');x=col*225+4;y=row*280+25
   d.text((x,row*280+4),b+' '+key+' tone '+str(t),fill='white')
   for size in [32,48,64]:im.paste(src.resize((size,size),Image.Resampling.LANCZOS),(x,y));x+=size+9
   im.paste(src,(col*225+35,y+80))
 im.save(P/f'small-{key}.jpg')
 im=Image.new('RGB',(1120,610),(25,33,45));d=ImageDraw.Draw(im)
 for row,b in enumerate(['Feminine','Masculine']):
  for col,angle in enumerate(['profile','rightprofile','top','underside']):
   im.paste(Image.open(P/'renders'/f'{b}-{key}-export-{angle}.png').convert('RGB').resize((280,280)),(col*280,row*305+25));d.text((col*280+7,row*305+5),b+' '+key+' / '+angle,fill='white')
 im.save(P/f'angles-{key}.jpg')
