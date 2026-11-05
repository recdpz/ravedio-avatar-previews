"""Remove the inherited outward neck tabs; preserve243 knot and free drape."""
import sys,json
from pathlib import Path
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue235')
import common235 as c
c.P=Path(__file__).parent
from common235 import *
from mathutils.kdtree import KDTree
import bmesh
BASE=P.parent/'catalogue243'
for folder in ['sources','components','review1','review2','fixtures','browser']:(P/folder).mkdir(parents=True,exist_ok=True)
def run(build,top,quick=False):
 bpy.ops.wm.open_mainfile(filepath=str(BASE/'sources'/f'{build}-{top}-pashmina243.blend'));s=bpy.context.scene
 ob=next(o for o in s.objects if 'joined hood wrap and ends239' in o.name);hem=next(o for o in s.objects if 'continuous face to fold hem239' in o.name)
 frozen={k:v for k,v in u.object_geometry(s).items() if k not in [ob.name,hem.name]}
 n=len(ob.data.vertices)//2;old=[ob.matrix_world@v.co for v in ob.data.vertices];uv={}
 for f in ob.data.polygons:
  if max(f.vertices)>=n:continue
  for li,i in zip(f.loop_indices,f.vertices):uv[i]=ob.data.uv_layers.active.data[li].uv.copy()
 end={};reliable={-1:{},1:{}}
 for i,q in uv.items():
  if q.x<-.8*.18:side=-1;t=-q.x/.8
  elif q.x>1+.8*.18:side=1;t=(q.x-1)/.8
  else:continue
  reliable[side].setdefault(round(t*127),[]).append(i)
 for side in [-1,1]:
  ref=sorted(reliable[side][30]);count=len(ref);start=ref[0]-29*count
  for j,items in reliable[side].items():assert sorted(items)==list(range(start+(j-1)*count,start+j*count))
  for j in range(1,128):
   for k in range(count):end[start+(j-1)*count+k]=j/127
 inv=ob.matrix_world.inverted().to_3x3();deltas={}
 for i in range(n):
  p=old[i];weight=(1-smooth((p.z-1.40)/.09))*(1-smooth((end.get(i,0)-.10)/.17))
  if weight<1e-8:continue
  q=p.copy();q.z=1.409+.35*(p.z-1.360)
  # The lower hood gathers into a narrow neck wrap. Its short outer edge
  # must not reverse outward into a separate scalloped shoulder tab.
  rx=.172+max(0.,q.z-1.416)*1.65;ry=.100+max(0.,q.z-1.416)*1.3
  radius=((q.x/rx)**2+(q.y/ry)**2)**.5
  if radius>1:q.x/=radius;q.y/=radius
  delta=(q-p)*weight
  for k in [i,i+n]:ob.data.vertices[k].co+=inv@delta;deltas[k]=delta
 # Existing continuous border follows the exact displaced cloth boundary.
 kd=KDTree(n)
 for i,p in enumerate(old[:n]):kd.insert(p,i)
 kd.balance();changed_rings=0
 for k in range(0,len(hem.data.vertices),6):
  centre=sum((hem.matrix_world@v.co for v in hem.data.vertices[k:k+6]),Vector())/6
  near,index,distance=kd.find(centre)
  if distance<.006 and index in deltas:
   d=hem.matrix_world.inverted().to_3x3()@deltas[index]
   for v in hem.data.vertices[k:k+6]:v.co+=d
   changed_rings+=1
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(len(e.link_faces)==2 for e in bm.edges);bm.to_mesh(ob.data);bm.free()
 assert all((ob.matrix_world@ob.data.vertices[i].co-old[i]).length<1e-9 for i in range(len(old)) if i not in deltas)
 assert all(u.object_geometry(s).get(k)==v for k,v in frozen.items())
 key=f'{build}-{top}-pashmina244';parts=save(s,key,['headgear']);s=bpy.context.scene
 render(s,key,['front','threequarter','profile'],size=384 if quick else 256,body=True)
 if quick:
  for angle in ['front','threequarter','profile']:
   u.camera(s,angle,768,True);s.camera.data.ortho_scale=.9;s.camera.location.z-=.07;s.cycles.samples=16;s.render.filepath=str(P/'review1'/f'clean-{angle}.png');bpy.ops.render.render(write_still=True)
 return dict(source=str(P/'sources'/f'{key}.blend'),component=parts['headgear'],top=top,protected_neighbors_exact=True,closed_surface=True,upper_hood_exact_above=1.49,free_drape_exact243_after_t=.27,moved_vertices=len(deltas),border_rings=changed_rings,construction='Inherited lower-neck tabs gathered inward into one clean continuous neck transition.243 raised knot and outer-chest drape retained; border follows its attached fabric.')
if __name__=='__main__':
 cat=json.loads((R/'243/catalogue243.json').read_text());records=json.loads((P/'fits244.json').read_text()) if (P/'fits244.json').exists() else {}
 for build in (['Feminine'] if '--draft' in sys.argv else ['Feminine','Masculine']):
  for top in (['open'] if '--draft' in sys.argv else cat['builds'][build]['tops']):
   records.setdefault(build,{})[top]=run(build,top,'--draft' in sys.argv);u.dump(P/'fits244.json',records);print('CLEAN244',build,top,flush=True)
