"""Replace244's tucked knot by a plain overlap at the same high placement."""
import sys,json,math
from pathlib import Path
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue235')
import common235 as c
c.P=Path(__file__).parent
from common235 import *
from scarf_support235 import convex_support
import bmesh
BASE=P.parent/'catalogue244'
for folder in ['sources','components','review1','review2','fixtures','browser']:(P/folder).mkdir(parents=True,exist_ok=True)

def at(row,w):
 for (a,p),(b,q) in zip(row,row[1:]):
  if a-1e-7<=w<=b+1e-7:return p.lerp(q,max(0,min(1,(w-a)/(b-a))))
 return row[0][1] if w<row[0][0] else row[-1][1]

def run(build,top,quick=False):
 bpy.ops.wm.open_mainfile(filepath=str(BASE/'sources'/f'{build}-{top}-pashmina244.blend'));s=bpy.context.scene
 ob=next(o for o in s.objects if 'joined hood wrap and ends239' in o.name)
 frozen={k:v for k,v in u.object_geometry(s).items() if k!=ob.name}
 n=len(ob.data.vertices)//2;old=[ob.matrix_world@v.co for v in ob.data.vertices];uv={};grids={};rows={};reliable={-1:{},1:{}}
 for f in ob.data.polygons:
  if max(f.vertices)>=n:continue
  for li,i in zip(f.loop_indices,f.vertices):uv[i]=ob.data.uv_layers.active.data[li].uv.copy()
 for i,q in uv.items():
  if q.x<-.8*.18:side=-1;t=-q.x/.8;w=1-q.y/.175
  elif q.x>1+.8*.18:side=1;t=(q.x-1)/.8;w=q.y/.175
  else:continue
  reliable[side].setdefault(round(t*127),[]).append((i,float(w)))
 for side in [-1,1]:
  ref=sorted(reliable[side][30]);count=len(ref);start=ref[0][0]-29*count
  for j,items in reliable[side].items():assert sorted(i for i,w in items)==list(range(start+(j-1)*count,start+j*count))
  grids[side]={j:[(start+(j-1)*count+k,w) for k,(i,w) in enumerate(ref)] for j in range(1,128)}
  rows[side]={j:sorted((w,old[i]) for i,w in row) for j,row in grids[side].items()}
 bodies=[o for o in s.objects if o.type=='MESH' and (o.name=='Skin / rounded torso' or (o.get('component159')=='top' and not any(w in o.name.lower() for w in ['sleeve','string','lace','button','collar','hood','cuff'])))]
 support=convex_support(bodies)
 heads=[o for o in s.objects if o.type=='MESH' and any(m and m.name.startswith('Skin') for m in o.data.materials) and min((o.matrix_world@v.co).z for v in o.data.vertices)>1.42 and max((o.matrix_world@v.co).z for v in o.data.vertices)>2.0]
 head=tree(heads) if heads else None
 def seat(p,clear):
  radial=Vector((p.x,p.y,0));radial.normalize();hit,normal,_,_=support.ray_cast(Vector((0,0,p.z)),radial,1.5)
  if hit is None and head:hit,normal,_,_=head.ray_cast(Vector((0,0,p.z)),radial,1.5)
  if hit is None:return p+Vector((0,-clear,0))
  if normal.dot(radial)<0:normal=-normal
  return hit+normal*clear
 inv=ob.matrix_world.inverted().to_3x3();deltas={};metrics={}
 for side in [-1,1]:
  rr=rows[side];A=at(rr[24],.5);B=at(rr[78],.5)
  m0=(A-at(rr[21],.5))*(54/3);m1=(at(rr[81],.5)-B)*(54/3)
  # Endpoint tangents remain downward and across the body, without the
  # previous middle path reversing direction to make a tucked loop.
  span=B-A
  for tangent in [m0,m1]:
   tangent.x=math.copysign(min(abs(tangent.x),abs(span.x)*1.3),span.x)
   tangent.z=max(span.z*1.4,min(.006,tangent.z))
  for j,row in grids[side].items():
   t=j/127;weight=smooth((t-.185)/.045)*(1-smooth((t-.55)/.065))
   if weight<1e-8:continue
   center=at(rr[j],.5);target_center=center.copy()
   if side>0:
    q=max(0,min(1,(j-24)/54));target_center=A*(2*q**3-3*q*q+1)+m0*(q**3-2*q*q+q)+B*(-2*q**3+3*q*q)+m1*(q**3-q*q)
   width_scale=1/(1-.24*math.exp(-((t-.42)/.055)**2)) if side>0 else 1.
   for i,w in row:
    offset=old[i]-center;p=old[i].copy()
    p.x=target_center.x+offset.x*width_scale;p.z=target_center.z+offset.z*width_scale
    p.y=target_center.y
    # A single cloth thickness separates the upper and lower length.
    # Remove the pillow/gather relief that made the crossing read as a knot.
    target=seat(p,(.009 if side>0 else .004)+.0006*math.sin(math.pi*w)**2)
    delta=(target-old[i])*weight
    for k in [i,i+n]:ob.data.vertices[k].co+=inv@delta;deltas[k]=delta
  metrics[str(side)]=dict(original_center=list(at(rr[48],.5)),new_center=list(at(sorted((w,ob.matrix_world@ob.data.vertices[i].co) for i,w in grids[side][48]),.5)))
 assert deltas
 assert all((ob.matrix_world@ob.data.vertices[i].co-old[i]).length<1e-9 for i in range(len(old)) if i not in deltas)
 for side,grid in grids.items():
  assert all(i not in deltas and i+n not in deltas for j,row in grid.items() if j/127<=.185 or j/127>=.615 for i,w in row)
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(len(e.link_faces)==2 for e in bm.edges);bm.to_mesh(ob.data);bm.free()
 assert all(u.object_geometry(s).get(k)==v for k,v in frozen.items())
 key=f'{build}-{top}-pashmina245';parts=save(s,key,['headgear']);s=bpy.context.scene
 render(s,key,['front','threequarter','profile'],size=384 if quick else 256,body=True)
 if quick:
  for angle in ['front','threequarter','profile']:
   u.camera(s,angle,768,True);s.camera.data.ortho_scale=.9;s.camera.location.z-=.07;s.cycles.samples=16;s.render.filepath=str(P/'review1'/f'cross-{angle}.png');bpy.ops.render.render(write_still=True)
 return dict(source=str(P/'sources'/f'{key}.blend'),component=parts['headgear'],top=top,closed_surface=True,protected_neighbors_exact=True,hood_and_neck_exact244=True,free_ends_and_fringe_exact244=True,changed_region=[.185,.615],moved_vertices=len(deltas),crossing_metrics=metrics,construction='Two cloth lengths simply overlap. Central tucked loop, pinch and gathered relief removed;244 high placement, clean neck and outward free ends retained.')
if __name__=='__main__':
 cat=json.loads((R/'244/catalogue244.json').read_text());records=json.loads((P/'fits245.json').read_text()) if (P/'fits245.json').exists() else {}
 for build in (['Feminine'] if '--draft' in sys.argv else ['Feminine','Masculine']):
  for top in (['open'] if '--draft' in sys.argv else cat['builds'][build]['tops']):
   records.setdefault(build,{})[top]=run(build,top,'--draft' in sys.argv);u.dump(P/'fits245.json',records);print('CROSS245',build,top,flush=True)
