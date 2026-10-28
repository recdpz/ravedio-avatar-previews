import bpy,sys,math,json,shutil
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
 shutil.copy2(P.parent/'refinement228/output/renders'/f'{build}-export-front.png',O/'renders'/f'{build}-original-front.png')
 dark=bpy.data.materials.new('Eye / muted aperture230');dark.use_nodes=True
 bs=dark.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(1,1,1,1);bs.inputs['Roughness'].default_value=.33;bs.inputs['Metallic'].default_value=0;bs.inputs['Coat Weight'].default_value=.22;bs.inputs['Coat Roughness'].default_value=.24
 vc=dark.node_tree.nodes.new('ShaderNodeVertexColor');vc.layer_name='EyeTone';dark.node_tree.links.new(vc.outputs['Color'],bs.inputs['Base Color'])
 for ob in eyes:u.delete(ob)
 support=tree(s.objects['Skin / soft oval head']);N=len(outline);rows=18
 for side in [-1,1]:
  def point(x,z,r,back=False):
   hit=support.ray_cast(Vector((side*(.15+x),-1,1.895+z)),Vector((0,1,0)))[0];assert hit is not None
   hit.y-=(-.003 if back else .0025+.004*max(0,1-r*r)**1.5);return hit
  vv=[point(0,.022,0)];ff=[]
  for rr in np.linspace(1/rows,1,rows):
   for x,z in outline:vv.append(point(x*rr,.022+(z-.022)*rr,rr))
  for j in range(N):ff.append((0,1+j,1+(j+1)%N))
  for i in range(rows-1):
   for j in range(N):p=1+i*N+j;n=1+i*N+(j+1)%N;ff.append((p,p+N,n+N,n))
  off=len(vv);vv += [point(x,z,1,True) for x,z in outline];back=len(vv);vv.append(point(0,.022,0,True))
  for j in range(N):k=(j+1)%N;ff.extend([(1+(rows-1)*N+j,off+j,off+k,1+(rows-1)*N+k),(back,off+k,off+j)])
  ob=a.mesh('Eye / soft squint230 '+str(side),vv,ff,dark,'eyes');surface=tree(ob)
  # A quiet grey eye opening surrounding an actual pupil. The dark perimeter
  # is thin; the opening reads at avatar size without a realistic iris ring.
  attr=ob.data.color_attributes.new(name='EyeTone',type='FLOAT_COLOR',domain='POINT')
  for i,(v,c) in enumerate(zip(ob.data.vertices,attr.data)):
   r=0 if i==0 else min(1,((i-1)//N+1)/rows)
   rim=max(0,min(1,(r-.87)/.13));rim=rim*rim*(3-2*rim)
   base=.30-.055*max(0,min(1,(v.co.z-1.88)/.06))
   val=base*(1-rim)+.028*rim
   x=v.co.x-side*.15;z=v.co.z-1.899
   distance=math.sqrt(x*x+z*z)
   pupil=max(0,min(1,(.029-distance)/.0025));pupil=pupil*pupil*(3-2*pupil)
   c.color=tuple(a*(1-pupil)+b*pupil for a,b in zip((val*.96,val*.99,val,1),(.008,.012,.017,1)))
  # A larger pupil is integrated into the same curved surface. Its lower edge
  # is clipped by the eye opening, rather than adding a protruding ball.
  cx=side*.15;cz=1.899
  vertices=[];faces=[];cols=36
  for rr in np.linspace(0,1,7):
   for t in np.linspace(0,2*math.pi,cols,endpoint=False):
    hit=surface.ray_cast(Vector((cx-.007+.0037*rr*math.cos(t),-1,cz+.008+.0037*rr*math.sin(t))),Vector((0,1,0)))[0]
    assert hit is not None
    vertices.append(hit+Vector((0,-.0005,0)))
  for i in range(6):
   for j in range(cols):q=i*cols+j;n=i*cols+(j+1)%cols;faces.append((q,n,n+cols,q+cols))
  a.mesh('Eye pupil catchlight230 '+str(side),vertices,faces,shine,'eyes')
 assert protected=={k:v for k,v in u.object_geometry(s).items() if s.objects[k].get('component159')!='eyes'}
 u.bake(s);bpy.ops.file.pack_all();path=O/'sources'/f'{build}-soft-squint.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene
 for angle in ['front','threequarter']:u.render(s,O/'renders'/f'{build}-source-{angle}.png',384,angle)
 if '--quick' in sys.argv:break
 glb=O/'components'/f'{build}-eyes-squint.glb';ex.export(s,glb,'eyes')
 for ob in list(s.objects):
  if ob.get('component159')=='eyes':u.delete(ob)
 bpy.ops.import_scene.gltf(filepath=str(glb))
 for angle in ['front','threequarter','profile','rightprofile','rear','top','underside']:u.render(s,O/'renders'/f'{build}-export-{angle}.png',384,angle)
 for tone in range(4):u.tone(s,tone);u.render(s,O/'portraits'/f'{build}-tone{tone}.png',128,'front')
 record[build]={'source':str(path),'source_sha256':u.sha(path),'glb':str(glb),'glb_sha256':u.sha(glb),'baseline_source':str(src),'baseline_sha256':u.sha(src),'protected_neighbors_exact':True,'eye_placement':[.15,1.895],'style':'228 outline and spacing retained; muted grey opening with a larger dark round pupil integrated into the aperture and one small catchlight. Reduced dome, thin dark rim. Candidate, no profile-slot change.'}
 u.dump(O/'eyes230.json',record);print('EYES230',build,flush=True)
