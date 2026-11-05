from pathlib import Path
import json,sys,hashlib,numpy as np,io
from PIL import Image
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue259');from glbcheck259 import glb,array
P=Path('E:/Ravedio-Avatar/catalogue261');D=P.parent/'floating138/mobile-preview/261';c=json.loads((D/'catalogue261.json').read_text());tech=[]
for f in sorted((D/'components').glob('*.glb')):
 g,bb=glb(f);tri=0;nv=0
 for m in g['meshes']:
  for pr in m['primitives']:
   pos=array(g,bb,pr['attributes']['POSITION']);n=array(g,bb,pr['attributes']['NORMAL']);assert np.isfinite(pos).all() and np.isfinite(n).all();assert np.abs(np.linalg.norm(n,axis=1)-1).max()<.001;ix=array(g,bb,pr['indices']).reshape(-1,3).astype('i');assert ix.min()>=0 and ix.max()<len(pos);nv+=len(pos);tri+=len(ix)
 ext=g.get('extensionsUsed',[]);assert not set(ext)&{'EXT_meshopt_compression','KHR_draco_mesh_compression','KHR_mesh_quantization','KHR_materials_transmission'}
 tech.append({'path':f.relative_to(D).as_posix(),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'vertices':nv,'triangles':tri,'primitives':sum(len(m['primitives']) for m in g['meshes']),'materials':len(g.get('materials',[])),'alpha_modes':sorted(set(m.get('alphaMode','OPAQUE') for m in g.get('materials',[]))),'textures':[{'width':Image.open(io.BytesIO(bb[g['bufferViews'][im['bufferView']].get('byteOffset',0):g['bufferViews'][im['bufferView']].get('byteOffset',0)+g['bufferViews'][im['bufferView']]['byteLength']])).width,'height':Image.open(io.BytesIO(bb[g['bufferViews'][im['bufferView']].get('byteOffset',0):g['bufferViews'][im['bufferView']].get('byteOffset',0)+g['bufferViews'][im['bufferView']]['byteLength']])).height,'mime':im['mimeType']} for im in g.get('images',[])],'finite_positions_unit_normals_valid_indices':True,'compression':False,'transmission':False})
assert len(tech)==144,len(tech);(P/'technical261.json').write_text(json.dumps(tech,indent=2));print('TECHNICAL261_COMPLETE',len(tech))
