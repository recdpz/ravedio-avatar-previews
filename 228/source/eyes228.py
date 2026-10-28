import bpy,sys,math,json
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).parent;O=P/'output';R=P.parent/'floating138/mobile-preview'
sys.path.insert(0,str(P.parent/'refinement224'));sys.path.insert(0,str(P.parent/'catalogue226'))
import utils224 as u,sculpt226 as a,export226 as ex
bpy.context.preferences.filepaths.save_version=0
for d in ['sources','components','renders','portraits']:(O/d).mkdir(parents=True,exist_ok=True)
def tree(ob):return BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[list(p.vertices) for p in ob.data.polygons])
def bezier(ps):
 p=np.asarray(ps);return [(1-t)**3*p[0]+3*(1-t)**2*t*p[1]+3*(1-t)*t*t*p[2]+t**3*p[3] for t in np.linspace(0,1,24,endpoint=False)]
# A softly peaked upper lid and a shallow rising lower edge. The lower edge
# stays concave rather than a straight triangular base or a thin caret stroke.
curves=[[[-.078,-.012],[-.056,.002],[-.028,.044],[-.005,.044]],[[-.005,.044],[.025,.045],[.060,.004],[.080,-.012]],[[.080,-.012],[.087,-.019],[.083,-.026],[.075,-.028]],[[.075,-.028],[.053,-.030],[.026,-.017],[.003,-.018]],[[.003,-.018],[-.021,-.017],[-.051,-.028],[-.072,-.027]],[[-.072,-.027],[-.080,-.027],[-.085,-.019],[-.078,-.012]]]
outline=np.array([q for c in curves for q in bezier(c)])
record={}
for build,case in [('Feminine','Feminine-uncovered'),('Masculine','Masculine-taper')]:
 src=P.parent/'refinement224/scenes'/f'{case}.blend';bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;s.cycles.device='CPU'
 protected={k:v for k,v in u.object_geometry(s).items() if s.objects[k].get('component159')!='eyes'}
 eyes=[o for o in s.objects if o.get('component159')=='eyes']
 dark=next(o for o in eyes if o.name.startswith('Eye /')).data.materials[0]
 shine=next(o for o in eyes if o.name.startswith('Eye highlight / main')).data.materials[0]
 glint=next(o for o in eyes if o.name.startswith('Eye highlight / small')).data.materials[0]
 u.render(s,O/'renders'/f'{build}-original-front.png',384,'front')
 for ob in eyes:u.delete(ob)
 support=tree(s.objects['Skin / soft oval head']);N=len(outline);rows=18
 for side in [-1,1]:
  def point(x,z,r,back=False):
   hit=support.ray_cast(Vector((side*(.15+x),-1,1.895+z)),Vector((0,1,0)))[0];assert hit is not None
   hit.y-=(-.003 if back else .0025+.005*max(0,1-r*r)**1.5);return hit
  vv=[point(0,.022,0)];ff=[]
  for rr in np.linspace(1/rows,1,rows):
   for x,z in outline:vv.append(point(x*rr,.022+(z-.022)*rr,rr))
  for j in range(N):ff.append((0,1+j,1+(j+1)%N))
  for i in range(rows-1):
   for j in range(N):p=1+i*N+j;n=1+i*N+(j+1)%N;ff.append((p,p+N,n+N,n))
  off=len(vv);vv += [point(x,z,1,True) for x,z in outline];back=len(vv);vv.append(point(0,.022,0,True))
  for j in range(N):k=(j+1)%N;ff.extend([(1+(rows-1)*N+j,off+j,off+k,1+(rows-1)*N+k),(back,off+k,off+j)])
  ob=a.mesh('Eye / soft squint228 '+str(side),vv,ff,dark,'eyes');surface=tree(ob)
  for name,x,z,rx,rz,mat in [('main',side*.15-.009,1.922,.006,.006,shine),('small',side*.15+.032,1.903,.0023,.0028,glint)]:
   verts=[];faces=[];cols=32;rs=8
   for rr in np.linspace(0,1,rs):
    for t in np.linspace(0,2*math.pi,cols,endpoint=False):
     hit,no,_,_=surface.ray_cast(Vector((x+rx*rr*math.cos(t),-1,z+rz*rr*math.sin(t))),Vector((0,1,0)));assert hit is not None
     verts.append(hit+Vector((0,-.0008,0)))
   for i in range(rs-1):
    for j in range(cols):p=i*cols+j;n=i*cols+(j+1)%cols;faces.append((p,n,n+cols,p+cols))
   a.mesh('Eye highlight / '+name+'228 '+str(side),verts,faces,mat,'eyes')
 assert protected=={k:v for k,v in u.object_geometry(s).items() if s.objects[k].get('component159')!='eyes'}
 u.bake(s);bpy.ops.file.pack_all();path=O/'sources'/f'{build}-soft-squint.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene
 for angle in ['front','threequarter','profile','rightprofile','rear','top','underside']:u.render(s,O/'renders'/f'{build}-source-{angle}.png',384,angle)
 glb=O/'components'/f'{build}-eyes-squint.glb';ex.export(s,glb,'eyes')
 for ob in list(s.objects):
  if ob.get('component159')=='eyes':u.delete(ob)
 bpy.ops.import_scene.gltf(filepath=str(glb))
 for angle in ['front','threequarter','profile','rightprofile','rear','top','underside']:u.render(s,O/'renders'/f'{build}-export-{angle}.png',384,angle)
 for tone in range(4):u.tone(s,tone);u.render(s,O/'portraits'/f'{build}-tone{tone}.png',128,'front')
 record[build]={'source':str(path),'source_sha256':u.sha(path),'glb':str(glb),'glb_sha256':u.sha(glb),'baseline_source':str(src),'baseline_sha256':u.sha(src),'protected_neighbors_exact':True,'eye_placement':[.15,1.895],'style':'Owner correction: larger rounded arch/arrow squint; upper AND lower edges rise toward the middle. No flat lower base or literal filled triangle. Retained charcoal finish; additional review option, no profile-slot change.'}
 u.dump(O/'eyes228.json',record);print('EYES228',build,flush=True)
