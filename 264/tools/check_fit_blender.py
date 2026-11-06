import sys,json,struct
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
D=Path(__file__).resolve().parent.parent
def glb(f):
 raw=f.read_bytes();n=struct.unpack_from('<I',raw,12)[0];return json.loads(raw[20:20+n]),raw[28+n:]
def array(g,b,i):
 a=g['accessors'][i];v=g['bufferViews'][a['bufferView']];dt={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']];w={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];return np.frombuffer(b,dtype=dt,count=a['count']*w,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,w)
rows=[]
for build in ['Feminine','Masculine']:
 g,b=glb(D/'assets'/f'{build}-optimized264.glb');node=next(n for n in g['nodes']if'continuous pants'in n.get('name',''));pr=g['meshes'][node['mesh']]['primitives'][0];pv=array(g,b,pr['attributes']['POSITION']);ix=array(g,b,pr['indices']).reshape(-1,3);tree=BVHTree.FromPolygons([Vector(p)for p in pv],ix.tolist(),all_triangles=True)
 for node in g['nodes']:
  if 'pants fitted leg'not in node.get('name',''):continue
  pr=g['meshes'][node['mesh']]['primitives'][0];v=array(g,b,pr['attributes']['POSITION']);cx=(v[:,0].min()+v[:,0].max())/2;cz=(v[:,2].min()+v[:,2].max())/2;clearance=[];misses=0
  for p in v:
   if not .596<p[1]<.996:continue
   origin=Vector((cx,float(p[1]),cz));dr=Vector((p[0]-cx,0,p[2]-cz));radius=dr.length
   if radius<.001:continue
   hit=tree.ray_cast(origin,dr.normalized(),1)
   if hit[0]is None:misses+=1
   else:clearance.append(hit[3]-radius)
  rows.append(dict(build=build,node=node['name'],samples=len(clearance),misses=misses,penetrations=sum(x<0 for x in clearance),minimum_clearance=min(clearance)))
assert all(r['misses']==0 and r['penetrations']==0 for r in rows),rows
(D/'verification/leg-clearance.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf8');print('CLEARANCE264_COMPLETE',rows)
