from pathlib import Path
import json,struct,hashlib,copy
import numpy as np
P=Path(__file__).parent;D=P.parent/'floating138/mobile-preview/259';c=json.loads((D/'catalogue259.json').read_text())
def acc(g,b,i):
 a=g['accessors'][i];v=g['bufferViews'][a['bufferView']];dt={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']];n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];item=np.dtype(dt).itemsize;q=np.ndarray((a['count'],n),dtype=dt,buffer=b,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',n*item),item)).copy();return q.astype('f')/np.iinfo(dt).max if a.get('normalized') else q
def smooth(x):x=np.clip(x,0,1);return x*x*(3-2*x)
def ramp(s):
 a=smooth((s-.30)/.37)[:,None];b=smooth((s-.58)/.36)[:,None];rgb=np.array([.145,.062,.034])*(1-a)+np.array([.32,.17,.078])*a;return rgb*(1-b)+np.array([.50,.32,.16])*b
records=[]
for st in ['taper','sidepart','curly-top']:
 paths={c['builds']['Masculine']['hair'][st]['path']}|{r['hair'] for r in c['fits']['Masculine-'+st].values()}


 assert len(paths)==8
 for path in sorted(paths):
  assert path.startswith('components/') and '259' in path,path;r=(D/path).read_bytes();n=struct.unpack_from('<I',r,12)[0];g=json.loads(r[20:20+n]);binary=bytearray(r[28+n:]);before=[]
  for mesh in g['meshes']:
   for pr in mesh['primitives']:
    for k,i in pr['attributes'].items():
     if k!='COLOR_0':before.append((i,hashlib.sha256(acc(g,binary,i).tobytes()).hexdigest()))
    before.append((pr['indices'],hashlib.sha256(acc(g,binary,pr['indices']).tobytes()).hexdigest()));m=g['materials'][pr['material']];pbr=m.setdefault('pbrMetallicRoughness',{})
    if ('smooth side fade' in m.get('name','') or 'directional fade marks' in m.get('name','')):pbr['baseColorFactor']=[x*m.get('extras',{}).get('hairShade258',1) for x in [.145,.062,.034]]+[1];continue
    if 'recessed roots' in m.get('name',''):
     pbr['baseColorFactor']=[x*.8 for x in [.145,.062,.034]]+[1];continue
    pos=acc(g,binary,pr['attributes']['POSITION']);old=acc(g,binary,pr['attributes']['COLOR_0']) if 'COLOR_0' in pr['attributes'] else np.ones((len(pos),4),dtype='f');alpha=old[:,3] if old.shape[1]==4 else np.ones(len(pos));shade=np.clip(np.sqrt((old[:,:3]@np.array([.2126,.7152,.0722]))/max(.001,old[:,:3].mean())),.83,1.05)
    if st in ['taper','sidepart']:s=acc(g,binary,pr['attributes']['TEXCOORD_0'])[:,1]
    else:
     d=pos-np.array([0,1.88,-.015]);radius=np.linalg.norm(d,axis=1);ell=np.linalg.norm(d/np.array([.48,.455,.405]),axis=1);dep=radius-radius/np.maximum(ell,1e-8);s=.10+.88*smooth((dep-.04)/.12)
    col=np.column_stack((ramp(np.clip(s,0,1))*shade[:,None],alpha)).astype('<f4');binary.extend(b'\0'*((-len(binary))%4));vi=len(g['bufferViews']);g['bufferViews'].append({'buffer':0,'byteOffset':len(binary),'byteLength':col.nbytes,'target':34962});binary.extend(col.tobytes());ai=len(g['accessors']);g['accessors'].append({'bufferView':vi,'componentType':5126,'count':len(col),'type':'VEC4'});pr['attributes']['COLOR_0']=ai;pbr['baseColorFactor']=[1,1,1,1];m['name']+=' / ombre259'
  for i,sha in before:assert hashlib.sha256(acc(g,binary,i).tobytes()).hexdigest()==sha
  g['buffers'][0]['byteLength']=len(binary);js=json.dumps(g,separators=(',',':')).encode();js+=b' '*((-len(js))%4);binary.extend(b'\0'*((-len(binary))%4));blob=struct.pack('<III',0x46546c67,2,28+len(js)+len(binary))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(binary),0x004e4942)+binary;target=path[:-4]+'-ombre.glb';(D/target).write_bytes(blob);c['ombre'][path]=target;records.append(dict(source=path,path=target,geometry_normals_indices_uv_transforms_preserved=True,side_vertex_opacity_preserved=True,post_gltf_uv_root_to_tip_correct=True,root_groom_color=[.145,.062,.034]))
(D/'catalogue259.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf8',newline='\n');(P/'ombre259.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf8');print('OMBRE259_COMPLETE',len(records))
