from pathlib import Path
from PIL import Image,ImageDraw
P=Path(__file__).parent/'revision227'
keys=sorted(f.name[:-10] for f in (P/'roundtrip').glob('*-front.png'))
for batch in range(0,len(keys),9):
 out=Image.new('RGB',(820,9*92),(25,33,45));d=ImageDraw.Draw(out)
 for row,key in enumerate(keys[batch:batch+9]):
  d.text((5,row*92+4),key,fill='white')
  for tone in range(4):
   im=Image.open(P/'portraits'/f'{key}-tone{tone}.png').convert('RGB')
   x=8+tone*204
   for size in [32,48,64]:
    out.paste(im.resize((size,size),Image.Resampling.LANCZOS),(x,row*92+24));x+=size+10
 out.save(P/f'small-{batch//9}.png')
