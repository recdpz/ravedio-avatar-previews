from pathlib import Path
import json,struct,hashlib,re
import numpy as np
P=Path(__file__).parent;D=P.parent/'floating138/mobile-preview/251';c=json.loads((D/'catalogue251.json').read_text());paths=set()
for b,bc in c['builds'].items():
 for style,r in bc['hair'].items():
  paths.add(r['path'])
  for fit in c['fits'][b+'-'+style].values():paths.add(fit['hair'])
for values in c['braidLengths'].values():paths.update(values.values())
def acc(g,raw,i):
 a=g['accessors'][i];v=g['bufferViews'][a['bufferView']];dtype={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']];n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];item=np.dtype(dtype).itemsize;stride=v.get('byteStride',item*n);q=np.ndarray((a['count'],n),dtype=dtype,buffer=raw,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(stride,item)).copy()
 if a.get('normalized'):q=q.astype('f')/np.iinfo(dtype).max
 return q
import os
only=json.loads(os.environ.get('RAVEDIO_HIGHLIGHT_PATHS','[]'))
if only:paths=set(only)
out=dict(c['highlights']);records=[x for x in json.loads((P/'highlights251.json').read_text()) if x['source'] not in paths] if only else []
for path in sorted(paths):
 source=(D/path).resolve();raw=source.read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);binary=bytearray(raw[28+n:]);before=[]
 for mesh in g['meshes']:
  for prim in mesh['primitives']:
   pos=acc(g,binary,prim['attributes']['POSITION']);before.append(hashlib.sha256(pos.tobytes()).hexdigest());mat=g['materials'][prim['material']];name=mat.get('name','')
   if re.search(r'tie|elastic|metal|band|Skin',name,re.I):continue
   old=acc(g,binary,prim['attributes']['COLOR_0']) if 'COLOR_0' in prim['attributes'] else np.ones((len(pos),4),dtype='f');alpha=old[:,3] if old.shape[1]==4 else np.ones(len(pos));luma=old[:,:3]@np.array([.2126,.7152,.0722]);shade=np.clip(np.sqrt(luma/max(.001,luma.mean())),.75,1.08)
   # Connected authored locks receive coherent dye; no world-space stripes.
   ids=acc(g,binary,prim['indices']).astype('i').ravel();parent=list(range(len(pos)))
   def root(i):
    while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
    return i
   def join(a,b):
    a=root(int(a));b=root(int(b))
    if a!=b:parent[b]=a
   for a,b,d in ids.reshape(-1,3):join(a,b);join(a,d)
   labels=np.array([root(i) for i in range(len(pos))]);unique,counts=np.unique(labels,return_counts=True);mask=np.zeros(len(pos),dtype='f')
   accent=('accent251' in name or 'chestnut212 1' in name or 'highlight' in name.lower())
   for k,(label,count) in enumerate(zip(unique,counts)):
    selected=labels==label
    if count>18000:
     normalized=luma/max(.001,luma.mean());mask[selected]=np.clip((normalized[selected]-1.015)/.08,0,1)*.70
    else:mask[selected]=.92 if accent or ((k*73+prim['material']*11)%7 in [1,4]) else .035
   if 'recessed' in name or 'roots220' in name:mask*=.20
   root_shadow=.40+.60*np.clip((2.48-pos[:,1])/.32,0,1);mask*=root_shadow
   base=np.array([.115,.043,.022]);gold=np.array([.60,.39,.18]);rgb=(base[None,:]*(1-mask[:,None])+gold[None,:]*mask[:,None])*shade[:,None];col=np.column_stack((rgb,alpha)).astype('<f4')
   binary.extend(b'\0'*((-len(binary))%4));offset=len(binary);data=col.tobytes();binary.extend(data);vi=len(g['bufferViews']);g['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(data),'target':34962});ai=len(g['accessors']);g['accessors'].append({'bufferView':vi,'componentType':5126,'count':len(pos),'type':'VEC4'});prim['attributes']['COLOR_0']=ai
 for mat in g['materials']:
  if not re.search(r'tie|elastic|metal|band|Skin',mat.get('name',''),re.I):
   pbr=mat.setdefault('pbrMetallicRoughness',{});factor=pbr.get('baseColorFactor',[1,1,1,1]);pbr['baseColorFactor']=[1,1,1,factor[3]];mat['name']=mat.get('name','Hair')+' / baked highlights251'
 g['buffers'][0]['byteLength']=len(binary);js=json.dumps(g,separators=(',',':')).encode();js+=b' '*((-len(js))%4);binary.extend(b'\0'*((-len(binary))%4));blob=struct.pack('<III',0x46546c67,2,28+len(js)+len(binary))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(binary),0x004e4942)+binary
 key=hashlib.sha256(path.encode()).hexdigest()[:12];target='components/Highlights-'+key+'251-hair.glb';(D/target).write_bytes(blob);out[path]=target;after=[hashlib.sha256(acc(g,binary,p['attributes']['POSITION']).tobytes()).hexdigest() for m in g['meshes'] for p in m['primitives']];assert before==after
 records.append(dict(source=path,path=target,position_buffers_unchanged=True,alpha_preserved=True,bytes=len(blob)))
c['highlights']=out;(D/'catalogue251.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf8');(P/'highlights251.json').write_text(json.dumps(records,indent=2)+'\n');print('HIGHLIGHTS251',len(out),'ordinary baked-color GLBs; unchanged geometry and alpha')
