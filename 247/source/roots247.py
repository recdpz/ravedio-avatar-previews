"""Clean the short upper joins without moving246's approved main strips."""
import sys,json,math
from pathlib import Path
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue235')
import common235 as c
c.P=Path(__file__).parent
from common235 import *
from scarf_support235 import convex_support
import bmesh
BASE=P.parent/'catalogue246'
for folder in ['sources','components','review1','review2','fixtures','browser']:(P/folder).mkdir(parents=True,exist_ok=True)

def at(row,w):
 for (a,p),(b,q) in zip(row,row[1:]):
  if a-1e-7<=w<=b+1e-7:return p.lerp(q,max(0,min(1,(w-a)/(b-a))))
 return row[0][1] if w<row[0][0] else row[-1][1]

def relax(values,amount,weights=None):
 n=len(values);d=np.diff(np.eye(n),n=2,axis=0);ww=np.ones(n) if weights is None else np.asarray(weights)
 return np.linalg.solve(np.diag(ww)+amount*(d.T@d),np.asarray(values)*ww.reshape((-1,)+(1,)*(np.asarray(values).ndim-1)))

def run(build,top,quick=False):
 bpy.ops.wm.open_mainfile(filepath=str(BASE/'sources'/f'{build}-{top}-pashmina246.blend'));s=bpy.context.scene
 ob=next(o for o in s.objects if 'joined hood wrap and ends239' in o.name);hem=next(o for o in s.objects if 'continuous face to fold hem239' in o.name)
 frozen={k:v for k,v in u.object_geometry(s).items() if k not in [ob.name,hem.name]}
 n=len(ob.data.vertices)//2;old=[ob.matrix_world@v.co for v in ob.data.vertices];uv={};grids={};rows={};reliable={-1:{},1:{}};adj=[set() for _ in range(n)]
 outer=[]
 for f in ob.data.polygons:
  if max(f.vertices)>=n:continue
  ids=list(f.vertices);outer.append(ids)
  for a0,b0 in zip(ids,ids[1:]+ids[:1]):adj[a0].add(b0);adj[b0].add(a0)
  for li,i in zip(f.loop_indices,f.vertices):uv[i]=ob.data.uv_layers.active.data[li].uv.copy()
 for i,q in uv.items():
  if q.x<-.8*.18:side=-1;t=-q.x/.8;w=1-q.y/.175
  elif q.x>1+.8*.18:side=1;t=(q.x-1)/.8;w=q.y/.175
  else:continue
  reliable[side].setdefault(round(t*127),[]).append((i,float(w)))
 end_ids=set()
 for side in [-1,1]:
  ref=sorted(reliable[side][30]);count=len(ref);start=ref[0][0]-29*count
  for j,items in reliable[side].items():assert sorted(i for i,w in items)==list(range(start+(j-1)*count,start+j*count))
  grids[side]={j:[(start+(j-1)*count+k,w) for k,(i,w) in enumerate(ref)] for j in range(1,128)}
  end_ids.update(i for row in grids[side].values() for i,w in row)
 for side in [-1,1]:
  root=[]
  for i,w in grids[side][1]:
   candidates=adj[i]-end_ids;assert len(candidates)==1,('Sewn root',side,i,candidates)
   root.append((next(iter(candidates)),w))
  grids[side][0]=root
  rows[side]={j:sorted((w,old[i]) for i,w in row) for j,row in grids[side].items()}
 bodies=[o for o in s.objects if o.type=='MESH' and (o.name=='Skin / rounded torso' or (o.get('component159')=='top' and not any(w in o.name.lower() for w in ['sleeve','string','lace','button','collar','hood','cuff'])))]
 support=convex_support(bodies)
 heads=[o for o in s.objects if o.type=='MESH' and any(m and m.name.startswith('Skin') for m in o.data.materials) and min((o.matrix_world@v.co).z for v in o.data.vertices)>1.42 and max((o.matrix_world@v.co).z for v in o.data.vertices)>2.0]
 head=tree(heads) if heads else None
 band_faces=[f for f in outer if all(-1e-5<=uv[i].x<=1.00001 and uv[i].y>=.99999 for i in f)]
 band=BVHTree.FromPolygons(old[:n],band_faces)
 def front(p):
  hits=[]
  for surface in [support,head]:
   if surface is None:continue
   hit,_,_,_=surface.ray_cast(Vector((p.x,-2,p.z)),Vector((0,1,0)),4)
   if hit is not None:hits.append(hit.y)
  return min(hits) if hits else float('nan')
 desired=[p.copy() for p in old];moved={};metrics={}
 for side in [-1,1]:
  rr=rows[side];count=len(grids[side][1]);wv=[w for i,w in grids[side][1]]
  root_a=rr[0][0][1];root_b=rr[0][-1][1]
  start_center=root_a.lerp(root_b,.5);end_center=at(rr[34],.5);m0=(end_center-start_center)*.8
  points=np.zeros((35,count,3));limits=np.full((35,count),np.nan)
  for j in range(35):
   t=j/34
   for col,w in enumerate(wv):
    a0=root_a.lerp(root_b,w);b0=at(rr[34],w);m1=(at(rr[36],w)-b0)*17
    # A single smooth bridge runs from the actual sewn hood boundary into
    # the approved246 strip. No extra crossing, bunch or filler panel.
    p=a0*(2*t**3-3*t*t+1)+m0*(t**3-2*t*t+t)+b0*(-2*t**3+3*t*t)+m1*(t**3-t*t)
    points[j,col]=p
    if p.y<.015 and j>2:limits[j,col]=front(p)
  ww=np.ones(35);ww[:2]=1e5;ww[-2:]=1e5
  depth=relax(points[:,:,1],28,ww)
  clear=.005
  required=np.maximum(0,np.max(np.where(np.isfinite(limits),depth-(limits-clear),-1),axis=1))
  padded=np.pad(required,2,mode='edge');dilated=np.array([max(padded[k:k+5]) for k in range(35)]);guard=np.convolve(np.pad(dilated,2,mode='edge'),np.ones(5)/5,mode='valid')
  points[:,:,1]=depth-guard[:,None]
  for j in range(0,34):
   weight=1-smooth((j-25)/9)
   for col,(i,w) in enumerate(grids[side][j]):
    desired[i]=old[i].lerp(Vector(points[j,col]),weight);desired[i+n]=old[i+n]+desired[i]-old[i];moved[i]=weight
  metrics[str(side)]=dict(sewn_root_continuous=True,approved_row34_exact=True,max_depth_guard=float(max(guard)),bridge_rows=34)
 # Shared hood vertices follow the cleaned seam through a small local
 # neighborhood, so straightening the root does not leave a crease or gap.
 root_ids={i for side in [-1,1] for i,w in grids[side][0]}
 active=set(root_ids);frontier=set(root_ids)
 for step in range(5):
  frontier={j for i in frontier for j in adj[i] if j not in end_ids and old[j].z<1.455}-active
  active.update(frontier)
 hood_free=active-root_ids
 displacement={i:desired[i]-old[i] for i in root_ids}
 displacement.update({i:Vector() for i in hood_free})
 for iteration in range(100):
  update={i:sum((displacement.get(j,Vector()) for j in adj[i]),Vector())/len(adj[i]) for i in hood_free}
  displacement.update(update)
 for i in hood_free:
  desired[i]=old[i]+displacement[i];desired[i+n]=old[i+n]+displacement[i];moved[i]=1.0
 # Rebuild inner offsets along the cleaned local surface normals.
 verts=np.array(desired[:n],float);tri=np.asarray([(f[0],f[k],f[k+1]) for f in outer for k in range(1,len(f)-1)])
 fn=np.cross(verts[tri[:,1]]-verts[tri[:,0]],verts[tri[:,2]]-verts[tri[:,0]]);normals=np.zeros((n,3))
 for k in range(3):np.add.at(normals,tri[:,k],fn)
 normals/=np.maximum(np.linalg.norm(normals,axis=1)[:,None],1e-12)
 inv=ob.matrix_world.inverted().to_3x3();thickness=float(np.median([(old[i]-old[i+n]).length for i in moved]));assert .002<thickness<.005
 for i,weight in moved.items():
  normal=Vector(normals[i]);radial=Vector((desired[i].x,desired[i].y,0))
  if normal.dot(radial)<0:normal=-normal
  desired[i+n]=desired[i]+(old[i+n]-old[i]).lerp(-normal*thickness,weight)
  for k in [i,i+n]:ob.data.vertices[k].co+=inv@(desired[k]-old[k])
 # Follow each actual root-edge curve; rotate its existing border rings to
 # match the cleaned tangent, preserving the upper hood's border in place.
 segments=[]
 for side in [-1,1]:
  edge=[(row[-1] if side<0 else row[0])[0] for j,row in sorted(grids[side].items()) if j<=23]
  for a0,b0 in zip(edge,edge[1:]):segments.append((a0,b0))
 hm=hem.matrix_world;hi=hm.inverted();centers=[sum((hm@v.co for v in hem.data.vertices[k:k+6]),Vector())/6 for k in range(0,len(hem.data.vertices),6)];hem_rings=0
 for ring,center in enumerate(centers):
  best=None
  for a0,b0 in segments:
   span=old[b0]-old[a0];f=max(0,min(1,(center-old[a0]).dot(span)/max(span.length_squared,1e-12)));p=old[a0].lerp(old[b0],f);distance=(p-center).length
   if best is None or distance<best[0]:best=(distance,a0,b0,f)
  distance,a0,b0,f=best
  if distance>.0055 or center.z>1.455:continue
  delta=(desired[a0]-old[a0]).lerp(desired[b0]-old[b0],f)
  if delta.length<1e-9:continue
  before=centers[min(ring+1,len(centers)-1)]-centers[max(0,ring-1)];after=desired[b0]-desired[a0]
  if before.length<1e-9 or after.length<1e-9:continue
  if after.dot(before)<0:after=-after
  rotation=before.normalized().rotation_difference(after.normalized())
  for v in hem.data.vertices[ring*6:ring*6+6]:v.co=hi@(center+delta+rotation@(hm@v.co-center))
  hem_rings+=1
 changed=set(moved)|{i+n for i in moved}
 # End-root UVs previously blended over almost a fifth of each panel,
 # squeezing the woven border into a jagged cluster under the chin. Let
 # that transition finish within the tucked root so visible cloth has a
 # continuous, lengthwise border like the accepted main strips.
 uvnew={}
 for side in [-1,1]:
  for j in range(1,24):
   for col,(i,w) in enumerate(grids[side][j]):
    rootuv=uv[grids[side][0][col][0]]
    standard=Vector(((0 if side<0 else 1)+side*.8*j/127,(w if side>0 else 1-w)*.175))
    uvnew[i]=rootuv.lerp(standard,smooth(j/5))
 for face in ob.data.polygons:
  for li,i in zip(face.loop_indices,face.vertices):
   if i%n in uvnew:ob.data.uv_layers.active.data[li].uv=uvnew[i%n]
 assert all((ob.matrix_world@ob.data.vertices[i].co-old[i]).length<1e-9 for i in range(len(old)) if i not in changed)
 for side in [-1,1]:assert all(i not in moved for j,row in grids[side].items() if j>=34 for i,w in row)
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(len(e.link_faces)==2 for e in bm.edges);bm.to_mesh(ob.data);bm.free()
 assert all(u.object_geometry(s).get(k)==v for k,v in frozen.items())
 key=f'{build}-{top}-pashmina247';parts=save(s,key,['headgear']);s=bpy.context.scene
 render(s,key,['front','threequarter','profile'],size=384 if quick else 256,body=True)
 if quick:
  for angle in ['front','threequarter','profile','rightprofile']:
   u.camera(s,angle,768,True);s.camera.data.ortho_scale=.65;s.camera.location.z+=.10;s.cycles.samples=16;s.render.filepath=str(P/'review1'/f'roots-{angle}.png');bpy.ops.render.render(write_still=True)
 return dict(source=str(P/'sources'/f'{key}.blend'),component=parts['headgear'],top=top,closed_surface=True,protected_neighbors_exact=True,approved_strips_exact246_from_row34=True,upper_hood_and_neck_wrap_exact246=True,free_ends_and_fringe_exact246=True,changed_rows=[0,33],local_hood_join_vertices=len(hood_free),moved_vertices=len(changed),hem_rings=hem_rings,root_metrics=metrics,thickness=thickness,construction='Cleaned upper joins bridge straightened sewn roots into approved246 strips, with local shared-vertex relaxation, coherent thickness and tangent-aligned edging. Main crossing and all lower lengths remain exact246.')
if __name__=='__main__':
 cat=json.loads((R/'246/catalogue246.json').read_text());records=json.loads((P/'fits247.json').read_text()) if (P/'fits247.json').exists() else {}
 for build in (['Feminine'] if '--draft' in sys.argv else ['Feminine','Masculine']):
  for top in (['open'] if '--draft' in sys.argv else cat['builds'][build]['tops']):
   records.setdefault(build,{})[top]=run(build,top,'--draft' in sys.argv);u.dump(P/'fits247.json',records);print('ROOTS247',build,top,flush=True)
