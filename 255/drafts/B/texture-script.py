from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,random,json
P=Path(__file__).parent;w,h,S=2048,1024,2
for folder in sorted((P/'drafts').iterdir()):
 cfg=json.loads((folder/'settings.json').read_text());assert not (folder/'coverage.png').exists();rng=random.Random(254);im=Image.new('RGBA',(w*S,h*S),(255,255,255,0));d=ImageDraw.Draw(im);d.rectangle((0,0,w*S,cfg['fill']*h*S),fill=(245,245,245,255))
 def sm(x):x=max(0,min(1,x));return x*x*(3-2*x)
 for row,y in enumerate(np.arange(-18,h+20,8)):
  v=max(0,min(1,y/h));density=sm((1-v)/cfg['fade_span'])
  for col,x in enumerate(np.arange(-8,w+8,5.5)):
   xx=x+2.75*(row%2)+rng.uniform(-1.5,1.5);yy=y+rng.uniform(-3.2,3.2);width=.25+5.4*density;length=.7+17*density;lean=.9+np.sin(xx/w*6.283);shade=rng.randrange(216,250);points=[(int((xx+lean)*S),int((yy-length*.5)*S)),(int(xx*S),int((yy+length*.5)*S))];d.line(points,fill=(shade,shade,shade,255),width=max(1,round(width*S)))
 pix=np.asarray(im.resize((w,h),Image.Resampling.LANCZOS)).copy();pix[-2:,:,3]=0;Image.fromarray(pix).save(folder/'coverage.png');alpha=pix[:,:,3].astype(float)/255;grey=pix[:,:,0].astype(float)/255;gy,gx=np.gradient(alpha*.12+grey*.05);nx=-gx*.65;ny=-gy*.65;nz=np.ones_like(nx);norm=np.sqrt(nx*nx+ny*ny+nz*nz);normal=np.stack(((nx/norm+1)*.5,(ny/norm+1)*.5,(nz/norm+1)*.5),-1);Image.fromarray(np.uint8(np.clip(normal,0,1)*255)).save(folder/'normal.png');print('TEXTURE255',folder.name)
