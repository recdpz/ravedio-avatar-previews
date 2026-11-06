import sys,json
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import struct
def glb(f):
 raw=f.read_bytes();n=struct.unpack_from('<I',raw,12)[0];return json.loads(raw[20:20+n]),raw[28+n:]

def array(g,b,i):
 a=g['accessors'][i];v=g['bufferViews'][a['bufferView']];dt={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']];width={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];step=np.dtype(dt).itemsize
 values=np.ndarray((a['count'],width),dtype=dt,buffer=b,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',width*step),step)).copy()
 return values.astype('f')/np.iinfo(dt).max if a.get('normalized') else values

D=Path('E:/Ravedio-Avatar/floating138/mobile-preview/263');P=Path('E:/Ravedio-Avatar/catalogue263');C=json.loads((D/'catalogue263.json').read_text());rows=[]
for build,bc in C['builds'].items():
 pg,pb=glb(D/bc['bottoms']['pants']['path']);mesh=next(m for m in pg['meshes'] if 'continuous pants' in m['name']);pr=mesh['primitives'][0];pv=array(pg,pb,pr['attributes']['POSITION']);ix=array(pg,pb,pr['indices']).reshape(-1,3);tree=BVHTree.FromPolygons([Vector(p) for p in pv],ix.tolist(),all_triangles=True)
 for variant,path in bc['pantsBases'].items():
  g,bb=glb(D/path)
  for node in g['nodes']:
   if 'pants fitted leg' not in node.get('name',''):continue
   pr=g['meshes'][node['mesh']]['primitives'][0];v=array(g,bb,pr['attributes']['POSITION']);cx=(v[:,0].min()+v[:,0].max())/2;cz=(v[:,2].min()+v[:,2].max())/2;clearance=[];misses=[]
   for p in v:
    if not .596<p[1]<.996:continue
    origin=Vector((cx,float(p[1]),cz));dr=Vector((p[0]-cx,0,p[2]-cz));radius=dr.length
    if radius<.001:continue
    hit=tree.ray_cast(origin,dr.normalized(),1)
    if hit[0] is None:misses.append(p.tolist())
    else:clearance.append(hit[3]-radius)
   rows.append(dict(build=build,variant=variant,node=node['name'],tested=len(clearance),minimum_clearance=min(clearance),misses=len(misses),penetrations=sum(x<0 for x in clearance)))
(P/'fitcheck263.json').write_text(json.dumps(rows,indent=2));print('FITCHECK263',rows);assert all(r['penetrations']==0 and r['misses']==0 for r in rows);print('FITCHECK263_COMPLETE')
