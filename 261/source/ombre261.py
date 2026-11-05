from pathlib import Path
import json,struct,hashlib
import numpy as np
import sys
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue259')
from glbcheck259 import glb,array
P=Path(__file__).parent;D=P.parent/'floating138/mobile-preview/261';c=json.loads((D/'catalogue261.json').read_text());rows=[]
def smooth(x):x=np.clip(x,0,1);return x*x*(3-2*x)
def ramp(s):
 a=smooth((s-.30)/.37)[:,None];b=smooth((s-.58)/.36)[:,None];rgb=np.array([.145,.062,.034])*(1-a)+np.array([.32,.17,.078])*a;return rgb*(1-b)+np.array([.50,.32,.16])*b
for key in json.loads((P/'selected261.json').read_text()):
 build,style=key.split('-',1);paths={c['builds'][build]['hair'][style]['path']}|{r['hair'] for r in c['fits'][key].values()};assert len(paths)==8
 for path in sorted(paths):
  g,bb=glb(D/path);binary=bytearray(bb);protected={i:hashlib.sha256(array(g,binary,i).tobytes()).hexdigest() for i,a in enumerate(g['accessors']) if a['type']!='VEC4'}
  for mesh in g['meshes']:
   for pr in mesh['primitives']:
    m=g['materials'][pr['material']];pbr=m.setdefault('pbrMetallicRoughness',{});pos=array(g,binary,pr['attributes']['POSITION']);old=array(g,binary,pr['attributes']['COLOR_0']) if 'COLOR_0' in pr['attributes'] else np.ones((len(pos),4),dtype='f');alpha=old[:,3] if old.shape[1]==4 else np.ones(len(pos));shade=np.clip(np.sqrt((old[:,:3]@np.array([.2126,.7152,.0722]))/max(.001,old[:,:3].mean())),.83,1.05)
    if any(q in m.get('name','').lower() for q in ['tie','elastic']):continue
    if style=='afro':
     d=pos-np.array([0,1.88,-.015]);r=np.linalg.norm(d,axis=1);e=np.linalg.norm(d/np.array([.48,.455,.405]),axis=1);dep=r-r/np.maximum(e,1e-8);s=.10+.88*smooth((dep-.04)/.12)
    elif build=='Feminine':s=np.clip((2.29-pos[:,1])/(1.12 if style=='box-braids' else 1.02),0,1)
    elif 'TEXCOORD_0' in pr['attributes']:s=array(g,binary,pr['attributes']['TEXCOORD_0'])[:,1]
    else:s=np.clip((2.3-pos[:,1])/.55,0,1)
    col=np.column_stack((ramp(s)*shade[:,None],alpha)).astype('<f4');binary.extend(b'\0'*((-len(binary))%4));vi=len(g['bufferViews']);g['bufferViews'].append({'buffer':0,'byteOffset':len(binary),'byteLength':col.nbytes,'target':34962});binary.extend(col.tobytes());ai=len(g['accessors']);g['accessors'].append({'bufferView':vi,'componentType':5126,'count':len(col),'type':'VEC4'});pr['attributes']['COLOR_0']=ai;pbr['baseColorFactor']=[1,1,1,1];m['name']+=' / ombre261'
  for i,sha in protected.items():assert hashlib.sha256(array(g,binary,i).tobytes()).hexdigest()==sha
  g['buffers'][0]['byteLength']=len(binary);js=json.dumps(g,separators=(',',':')).encode();js+=b' '*((-len(js))%4);binary.extend(b'\0'*((-len(binary))%4));blob=struct.pack('<III',0x46546c67,2,28+len(js)+len(binary))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(binary),0x004e4942)+binary;target=path[:-4]+'-ombre.glb';(D/target).write_bytes(blob);c['ombre'][path]=target;rows.append(dict(source=path,path=target,geometry_normals_indices_uv_transforms_preserved=True))
(D/'catalogue261.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf8',newline='\n');(P/'ombre261.json').write_text(json.dumps(rows,indent=2)+'\n');print('OMBRE261_COMPLETE',len(rows))
