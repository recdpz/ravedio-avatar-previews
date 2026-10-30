"""Rebuild the high crossing as ruled ribbons; fit depth without warping X/Z."""
import sys,json,math
from pathlib import Path
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue235')
import common235 as c
c.P=Path(__file__).parent
from common235 import *
from scarf_support235 import convex_support
import bmesh
BASE=P.parent/'catalogue245'
for folder in ['sources','components','review1','review2','fixtures','browser']:(P/folder).mkdir(parents=True,exist_ok=True)

def at(row,w):
 for (a,p),(b,q) in zip(row,row[1:]):
  if a-1e-7<=w<=b+1e-7:return p.lerp(q,max(0,min(1,(w-a)/(b-a))))
 return row[0][1] if w<row[0][0] else row[-1][1]

def relax(values,amount,weights=None):
 n=len(values);d=np.diff(np.eye(n),n=2,axis=0);ww=np.ones(n) if weights is None else np.asarray(weights)
 return np.linalg.solve(np.diag(ww)+amount*(d.T@d),np.asarray(values)*ww.reshape((-1,)+(1,)*(np.asarray(values).ndim-1)))

def run(build,top,quick=False):
 bpy.ops.wm.open_mainfile(filepath=str(BASE/'sources'/f'{build}-{top}-pashmina245.blend'));s=bpy.context.scene
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
 def front(x,z):
  hits=[]
  for surface in [support,head]:
   if surface is None:continue
   hit,_,_,_=surface.ray_cast(Vector((x,-2,z)),Vector((0,1,0)),4)
   if hit is not None:hits.append(hit.y)
  return min(hits) if hits else float('nan')
 inv=ob.matrix_world.inverted().to_3x3();moved={};metrics={};desired=[p.copy() for p in old]
 for side in [-1,1]:
  rr=rows[side];js=list(range(24,89));count=len(grids[side][30]);centers=np.array([at(rr[j],.5) for j in js],float)
  ww=np.ones(len(js));ww[:2]=1000;ww[-2:]=1000;ww[16:29]=2
  path=relax(centers,400,ww)
  previous=(rr[24][-1][1]-rr[24][0][1]);previous.y=0;previous.normalize()
  spans=[];turns=[];points=np.zeros((len(js),count,3));limits=np.full((len(js),count),np.nan)
  wvalues=[w for i,w in grids[side][30]]
  end_span=rr[88][-1][1]-rr[88][0][1];end_span.y=0;end_width=end_span.length;end_span.normalize()
  if end_span.dot(previous)<0:end_span=-end_span
  middle_span=Vector((.86,0,-.51*side)).normalized()
  for k,j in enumerate(js):
   t=j/127
   root_span=rr[24][-1][1]-rr[24][0][1];root_span.y=0;root_span.normalize()
   span=root_span.lerp(middle_span,smooth((t-.19)/.12)).normalized()
   span=span.lerp(end_span,smooth((t-.42)/.273)).normalized()
   turns.append(math.degrees(span.angle(previous)));previous=span;spans.append(span)
   width=.045+(end_width-.045)*smooth((t-.39)/.303)
   center=Vector(path[k]);center.z=min(center.z,1.418-abs(span.z)*width/2)
   for col,w in enumerate(wvalues):
    p=center+span*((w-.5)*width);points[k,col]=p;limits[k,col]=front(p.x,p.z)
  # Fit only depth against major forms. This preserves the authored strip
  # width/frame instead of radially dragging each edge into a different shape.
  for col in range(count):
   good=np.isfinite(limits[:,col]);fallback=np.array([at(rr[j],wvalues[col]).y for j in js])
   depth=np.interp(np.arange(len(js)),np.where(good)[0],limits[good,col]) if good.any() else fallback
   points[:,col,1]=depth
  depth=relax(points[:,:,1],250)
  depth=relax(depth.T,18).T
  clear=.011 if side>0 else .005
  required=np.maximum(0,np.nanmax(np.where(np.isfinite(limits),depth-(limits-clear),-1),axis=1))
  padded=np.pad(required,2,mode='edge');dilated=np.array([max(padded[k:k+5]) for k in range(len(js))]);guard=np.convolve(np.pad(dilated,2,mode='edge'),np.ones(5)/5,mode='valid')
  depth-=guard[:,None]+.0005
  points[:,:,1]=depth
  for k,j in enumerate(js):
   t=j/127;weight=smooth((t-.185)/.075)*(1-smooth((t-.54)/.14))
   if weight<1e-8:continue
   for col,(i,w) in enumerate(grids[side][j]):
    target=old[i].lerp(Vector(points[k,col]),weight);delta=target-old[i]
    desired[i]=target;desired[i+n]=old[i+n]+delta;moved[i]=weight
  metrics[str(side)]=dict(central_width=.045,max_frame_turn_degrees=max(turns),maximum_depth_guard=float(max(guard)),end_width_xz=end_width)
 # The old knot's inner-layer offsets also carried twist. Rebuild thickness
 # along the new outer normals, rather than carrying those offsets forward.
 verts=np.array(desired[:n],float);triangles=[]
 for f in ob.data.polygons:
  ids=list(f.vertices)
  if max(ids)>=n:continue
  triangles.extend((ids[0],ids[k],ids[k+1]) for k in range(1,len(ids)-1))
 tri=np.asarray(triangles);face_norm=np.cross(verts[tri[:,1]]-verts[tri[:,0]],verts[tri[:,2]]-verts[tri[:,0]])
 normals=np.zeros((n,3))
 for k in range(3):np.add.at(normals,tri[:,k],face_norm)
 normals/=np.maximum(np.linalg.norm(normals,axis=1)[:,None],1e-12)
 thickness=float(np.median([(old[i]-old[i+n]).length for i in moved]));assert .002<thickness<.005
 for i,weight in moved.items():
  normal=Vector(normals[i])
  if normal.y>0:normal=-normal
  offset=(old[i+n]-old[i]).lerp(-normal*thickness,weight)
  desired[i+n]=desired[i]+offset
  for k in [i,i+n]:ob.data.vertices[k].co+=inv@(desired[k]-old[k])
 changed=set(moved)|{i+n for i in moved}
 assert all((ob.matrix_world@ob.data.vertices[i].co-old[i]).length<1e-9 for i in range(len(old)) if i not in changed)
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(len(e.link_faces)==2 for e in bm.edges);bm.to_mesh(ob.data);bm.free()
 assert all(u.object_geometry(s).get(k)==v for k,v in frozen.items())
 key=f'{build}-{top}-pashmina246';parts=save(s,key,['headgear']);s=bpy.context.scene
 render(s,key,['front','threequarter','profile'],size=384 if quick else 256,body=True)
 if quick:
  for angle in ['front','threequarter','profile','rightprofile']:
   u.camera(s,angle,768,True);s.camera.data.ortho_scale=.9;s.camera.location.z-=.07;s.cycles.samples=16;s.render.filepath=str(P/'review1'/f'ribbon-{angle}.png');bpy.ops.render.render(write_still=True)
 return dict(source=str(P/'sources'/f'{key}.blend'),component=parts['headgear'],top=top,closed_surface=True,protected_neighbors_exact=True,hood_and_neck_exact245=True,free_ends_and_fringe_exact245=True,changed_region=[.185,.68],moved_vertices=len(changed),ribbon_metrics=metrics,thickness=thickness,construction='High crossing rebuilt as two consistently framed ruled ribbons. Smooth conservative depth envelope bridges minor hollows without radial X/Z warping; thickness follows the rebuilt surface normals.')
if __name__=='__main__':
 cat=json.loads((R/'245/catalogue245.json').read_text());records=json.loads((P/'fits246.json').read_text()) if (P/'fits246.json').exists() else {}
 for build in (['Feminine'] if '--draft' in sys.argv else ['Feminine','Masculine']):
  for top in (['open'] if '--draft' in sys.argv else cat['builds'][build]['tops']):
   records.setdefault(build,{})[top]=run(build,top,'--draft' in sys.argv);u.dump(P/'fits246.json',records);print('RIBBON246',build,top,flush=True)
