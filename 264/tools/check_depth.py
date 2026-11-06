"""Python 3 + numpy + OpenEXR; checks every paired render and its source hash."""
import json,hashlib,struct
from pathlib import Path
import numpy as np
import OpenEXR
D=Path(__file__).resolve().parent.parent;rows=[]
for file in sorted((D/'verification').glob('*-blender-pairs.json'))+sorted((D/'verification').glob('*-layers.json')):
 for r in json.loads(file.read_text(encoding='utf8')):
  color=D/r['color'];depth=D/r['depth'];size=r['size'];assert struct.unpack('>II',color.read_bytes()[16:24])==(size,size)
  ex=OpenEXR.File(str(depth));pixels=next(iter(ex.channels().values())).pixels;assert pixels.shape==(size,size) and not np.isnan(pixels).any()
  valid=pixels[np.isfinite(pixels)&(pixels>0)&(pixels<1e8)];assert len(valid)>0,r['depth']
  build=r['build'];variant=r.get('variant','optimized');geom=D/('assets'if variant=='optimized'else'sources')/(f'{build}-optimized264.glb'if variant=='optimized'else f'{build}-hoodie-pants-cap263.'+('blend'if variant=='artwork'else'glb'))
  assert hashlib.sha256(geom.read_bytes()).hexdigest()==r['geometry_sha256']
  rows.append(dict(color=r['color'],depth=r['depth'],size=size,finite_samples=len(valid),range=[float(valid.min()),float(valid.max())],color_sha256=hashlib.sha256(color.read_bytes()).hexdigest(),depth_sha256=hashlib.sha256(depth.read_bytes()).hexdigest(),geometry_sha256=r['geometry_sha256']))
(D/'verification/paired-depth.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf8');print('PAIRED_DEPTH264_COMPLETE',len(rows))
