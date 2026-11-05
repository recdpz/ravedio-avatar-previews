from pathlib import Path
import json
from PIL import Image,ImageDraw
P=Path(__file__).parent;O=P/'output'
labels=[('tapered','Tapered oval'),('bean','Rounded bean')]
for angle in ['front','threequarter']:
 im=Image.new('RGB',(1120,610),(25,33,45));d=ImageDraw.Draw(im)
 for row,b in enumerate(['Feminine','Masculine']):
  for col,(key,label) in enumerate(labels):
   for offset,(rev,version) in enumerate([(232,'Before232'),(233,'New233')]):
    path=P.parent/f'refinement{rev}/output/renders'/f'{b}-{key}-export-{angle}.png'
    x=(2*col+offset)*280
    im.paste(Image.open(path).convert('RGB').resize((280,280)),(x,row*305+25));d.text((x+5,row*305+5),b+' '+label+' / '+version,fill='white')
 im.save(O/f'comparison-{angle}.jpg')
for key,label in labels:
 im=Image.new('RGB',(900,560),(25,33,45));d=ImageDraw.Draw(im)
 for row,b in enumerate(['Feminine','Masculine']):
  for col,t in enumerate(range(4)):
   src=Image.open(O/'portraits'/f'{b}-{key}-tone{t}.png').convert('RGB');x=col*225+4;y=row*280+25
   d.text((x,row*280+4),b+' '+key+' tone '+str(t),fill='white')
   for size in [32,48,64]:im.paste(src.resize((size,size),Image.Resampling.LANCZOS),(x,y));x+=size+9
   im.paste(src,(col*225+35,y+80))
 im.save(O/f'small-{key}.jpg')
 im=Image.new('RGB',(1120,610),(25,33,45));d=ImageDraw.Draw(im)
 for row,b in enumerate(['Feminine','Masculine']):
  for col,angle in enumerate(['profile','rightprofile','top','underside']):
   im.paste(Image.open(O/'renders'/f'{b}-{key}-export-{angle}.png').convert('RGB').resize((280,280)),(col*280,row*305+25));d.text((col*280+5,row*305+5),b+' '+key+' / '+angle,fill='white')
 im.save(O/f'angles-{key}.jpg')
old=json.loads((P.parent/'refinement232/output/outlines232.json').read_text(encoding='utf8'));new=json.loads((O/'outlines233.json').read_text(encoding='utf8'))
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="800" height="190" viewBox="0 0 800 190"><rect width="800" height="190" fill="#edf0f3"/><text x="16" y="25" font-family="sans-serif" font-size="15" fill="#283140">Authored flat outlines · no highlights</text>']
for col,(key,label,source,version) in enumerate([(k,l,s,v) for k,l in labels for s,v in [(old,'Before232'),(new,'New233')]]):
 curves=source[key]['curves'];d=f'M {curves[0][0][0]} {curves[0][0][1]} '+' '.join('C '+' '.join(str(q) for p in c[1:] for q in p) for c in curves)+' Z'
 svg.append(f'<text x="{col*200+12}" y="55" font-family="sans-serif" font-size="12" fill="#283140">{label} · {version}</text><g transform="translate({col*200+100},125) scale(780,-780)"><path d="{d}" fill="#1b2430"/></g>')
svg.append('</svg>');(O/'outlines233.svg').write_text(''.join(svg),encoding='utf8')
