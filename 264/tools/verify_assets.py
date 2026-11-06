"""Read-only geometry/material/attachment checks; Python 3 + numpy + Pillow."""
import json,struct,hashlib,io
from pathlib import Path
from collections import Counter
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent.parent
def glb(file):
 raw=file.read_bytes();assert raw[:4]==b'glTF' and struct.unpack_from('<I',raw,8)[0]==len(raw)
 n=struct.unpack_from('<I',raw,12)[0];return json.loads(raw[20:20+n]),raw[28+n:]
def array(g,b,i):
 a=g['accessors'][i];v=g['bufferViews'][a['bufferView']];dt={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']];w={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];step=np.dtype(dt).itemsize
 return np.ndarray((a['count'],w),dtype=dt,buffer=b,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',w*step),step)).copy()
def boundaries(v,ix):
 # glTF duplicates vertices at normal/UV/material seams. Test geometric edges,
 # excluding collapsed triangles, rather than mistaking those seams for holes.
 v,remap=np.unique(v,axis=0,return_inverse=True);ix=remap[ix]
 ix=ix[(ix[:,0]!=ix[:,1])&(ix[:,1]!=ix[:,2])&(ix[:,0]!=ix[:,2])]
 edges=np.concatenate([ix[:,[0,1]],ix[:,[1,2]],ix[:,[2,0]]]);edges.sort(axis=1);u,c=np.unique(edges,axis=0,return_counts=True)
 return {tuple(sorted((v[a].tobytes(),v[b].tobytes())))for a,b in u[c==1]}
def blob(g,b,image):
 view=g['bufferViews'][image['bufferView']];return b[view.get('byteOffset',0):view.get('byteOffset',0)+view['byteLength']]
rows=[]
for build in ['Feminine','Masculine']:
 src=D/'sources'/f'{build}-hoodie-pants-cap263.glb';dst=D/'assets'/f'{build}-optimized264.glb';g,b=glb(src);q,c=glb(dst)
 for k in ['nodes','scenes','scene','materials','textures','samplers','extensionsUsed','extensionsRequired']:
  assert g.get(k)==q.get(k),(build,k)
 assert len(g['meshes'])==len(q['meshes'])
 images=[]
 for im,im2 in zip(g.get('images',[]),q.get('images',[])):
  raw=blob(g,b,im);assert raw==blob(q,c,im2);p=Image.open(io.BytesIO(raw));images.append(dict(name=im.get('name'),size=list(p.size),encoded_bytes=len(raw),decoded_rgba8_estimate=p.width*p.height*4,sha256=hashlib.sha256(raw).hexdigest()))
 geometry=[];primitives=0;decoded=0
 for mi,(m,n)in enumerate(zip(g['meshes'],q['meshes'])):
  assert len(m['primitives'])==len(n['primitives'])
  node=next(x for x in g['nodes']if x.get('mesh')==mi)
  for pi,(p,z)in enumerate(zip(m['primitives'],n['primitives'])):
   assert p.get('material')==z.get('material');assert set(p['attributes'])==set(z['attributes']);primitives+=1
   ix=array(g,b,p['indices']).reshape(-1,3);iy=array(q,c,z['indices']).reshape(-1,3);v=array(g,b,p['attributes']['POSITION']);w=array(q,c,z['attributes']['POSITION']);assert iy.min()>=0 and iy.max()<len(w)
   assert np.isfinite(w).all();assert (w.min(axis=0)>=v.min(axis=0)).all() and (w.max(axis=0)<=v.max(axis=0)).all()
   assert boundaries(v,ix)==boundaries(w,iy),(node['name'],'open boundary changed')
   # A surviving vertex retains the exact complete attribute tuple. No UV/color/normal drift.
   old=np.concatenate([array(g,b,p['attributes'][k]).view('u1')for k in sorted(p['attributes'])],axis=1)
   new=np.concatenate([array(q,c,z['attributes'][k]).view('u1')for k in sorted(z['attributes'])],axis=1)
   lookup={x.tobytes()for x in old};assert all(x.tobytes()in lookup for x in new),(node['name'],'changed vertex')
   norm=array(q,c,z['attributes']['NORMAL']);assert np.max(np.abs(np.linalg.norm(norm,axis=1)-1))<.003
   leg=None
   if 'pants fitted leg' in node['name']:
    _,inv=np.unique(w,axis=0,return_inverse=True);tri=inv[iy];e=np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]);e.sort(axis=1);_,counts=np.unique(e,axis=0,return_counts=True);assert (counts==2).all(),node['name'];leg='closed manifold'
   decoded+=iy.nbytes+sum(array(q,c,a).nbytes for a in z['attributes'].values())
   geometry.append(dict(name=node['name'],role=node.get('extras',{}).get('component159'),before_triangles=len(ix),after_triangles=len(iy),boundaries_unchanged=True,surviving_attributes_exact=True,leg_topology=leg))
 lens=[]
 for i,m in enumerate(q['materials']):
  t=m.get('extensions',{}).get('KHR_materials_transmission',{}).get('transmissionFactor',0)
  if t or 'lens' in m.get('name','').lower() or 'pane' in m.get('name','').lower():lens.append(dict(index=i,name=m.get('name'),alphaMode=m.get('alphaMode','OPAQUE'),alpha=m.get('pbrMetallicRoughness',{}).get('baseColorFactor',[1,1,1,1])[3],extensions=m.get('extensions',{})))
 rows.append(dict(build=build,file='assets/'+dst.name,source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),source_bytes=src.stat().st_size,bytes=dst.stat().st_size,triangles_before=sum(x['before_triangles']for x in geometry),triangles=sum(x['after_triangles']for x in geometry),mesh_nodes=len(g['meshes']),primitives=primitives,materials=len(q['materials']),decoded_geometry_bytes=decoded,decoded_geometry_note='Sum of exported accessor array bytes; excludes engine copies, alignment, pipelines, caches and render targets.',textures=images,lens_materials=lens,checks=geometry))
(D/'verification/assets.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf8');print('ASSETS264_COMPLETE',[(r['build'],r['triangles'])for r in rows])
