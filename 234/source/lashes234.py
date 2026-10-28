import bpy,sys,math,json
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).parent;O=P/'output';R=P.parent/'floating138/mobile-preview';cat=json.loads((R/'233/catalogue233.json').read_text(encoding='utf8'))
sys.path.insert(0,str(P.parent/'refinement224'));sys.path.insert(0,str(P.parent/'catalogue226'))
import utils224 as u,sculpt226 as a,export226 as ex
bpy.context.preferences.filepaths.save_version=0
for d in ['sources','components','renders','portraits']:(O/d).mkdir(parents=True,exist_ok=True)
def tree(objects,dark=False):
 verts=[];polys=[]
 for ob in objects:
  off=len(verts);verts += [ob.matrix_world@v.co for v in ob.data.vertices]
  for p in ob.data.polygons:
   if not dark or 'smoky charcoal181' in ob.data.materials[p.material_index].name:polys.append([off+i for i in p.vertices])
 return BVHTree.FromPolygons(verts,polys)
def cubic(ps,t):return (1-t)**3*ps[0]+3*(1-t)**2*t*ps[1]+3*(1-t)*t*t*ps[2]+t**3*ps[3]
def imported(path,group):
 old=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(path));new=[o for o in bpy.context.scene.objects if o not in old and o.type=='MESH']
 for o in new:o['component159']=group
 bpy.context.view_layer.update();return new
only=next((x.split('=',1)[1].split(',') for x in sys.argv if x.startswith('--only=')),None);records={}
for key,item in cat['builds']['Feminine']['eyes'].items():
 if only and key not in only:continue
 src=P.parent/'refinement224/scenes/Feminine-uncovered.blend';eye_path=(R/'233'/item['path']).resolve();mouth_path=(R/'233'/cat['builds']['Feminine']['mouths']['line']['path']).resolve()
 bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;s.cycles.device='CPU'
 for ob in list(s.objects):
  if ob.get('component159') in ['eyes','nose','mouth']:u.delete(ob)
 eye_objects=imported(eye_path,'eyes');imported(mouth_path,'mouth')
 protected=u.object_geometry(s);u.render(s,O/'renders'/f'Feminine-{key}-before-front.png',384,'front')
 dark_objects=[o for o in eye_objects if any('smoky charcoal181' in m.name for m in o.data.materials)];assert dark_objects
 dark=next(m for o in dark_objects for m in o.data.materials if 'smoky charcoal181' in m.name)
 lashmat=dark.copy();lashmat.name='Lashes / charcoal234';bs=lashmat.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.38;bs.inputs['Metallic'].default_value=0;bs.inputs['Coat Weight'].default_value=.1
 eye_tree=tree(dark_objects,True);head_tree=tree([s.objects['Skin / soft oval head']]);points=[o.matrix_world@v.co for o in dark_objects for v in o.data.vertices];anchors=[]
 def surface(x,z):
  head=head_tree.ray_cast(Vector((x,-1,z)),Vector((0,1,0)))[0];assert head is not None,'Lash leaves head support'
  hit=eye_tree.ray_cast(Vector((x,-1,z)),Vector((0,1,0)))[0]
  return min(head.y,hit.y) if hit is not None else head.y
 for side in [-1,1]:
  pts=[p for p in points if side*p.x>.045];us=[side*p.x-.15 for p in pts];zs=[p.z for p in pts];umin,umax=min(us),max(us)
  for n,(fraction,dz,width) in enumerate([(.88,.041,.0072),(.70,.034,.0057)]):
   root_u=umin+(umax-umin)*fraction;x=side*(.15+root_u);lo=min(zs);hi=max(zs)+.003
   # Find the actual upper edge at this lateral position, rather than assuming
   # each eye is an ellipse. All roots overlap its visible dark surface.
   hit_z=None
   for z in np.linspace(hi,lo,180):
    if eye_tree.ray_cast(Vector((x,-1,float(z))),Vector((0,1,0)))[0] is not None:hit_z=float(z);break
   assert hit_z is not None
   low,high=hit_z,hit_z+(hi-lo)/179
   for _ in range(15):
    mid=(low+high)/2
    if eye_tree.ray_cast(Vector((x,-1,mid)),Vector((0,1,0)))[0] is not None:low=mid
    else:high=mid
   z0=low-.0024;du=min(.040 if n==0 else .022,max(.016,.098-root_u))
   ps=np.array([[root_u,z0],[root_u+du*.36,z0+dz*.12],[root_u+du*.80,z0+dz*.56],[root_u+du,z0+dz]])
   verts=[];faces=[];rows=32;cols=12
   for t in np.linspace(0,1,rows):
    q=cubic(ps,t);ta=max(0,t-.001);tb=min(1,t+.001);v=cubic(ps,tb)-cubic(ps,ta);v/=np.linalg.norm(v);normal=np.array([-v[1],v[0]])
    half=.0008+(width-.0008)*(1-t)**.72;thick=.00065+.0010*(1-t)
    for angle in np.linspace(0,2*math.pi,cols,endpoint=False):
     xz=q+normal*(half*math.cos(angle));xx=side*(.15+xz[0]);zz=xz[1];yy=surface(xx,zz)-.0006-thick*(1+math.sin(angle));verts.append((xx,yy,zz))
   for i in range(rows-1):
    for j in range(cols):p=i*cols+j;k=i*cols+(j+1)%cols;faces.append((p,k,k+cols,p+cols))
   verts.append(tuple(np.mean(np.array(verts[:cols]),axis=0)));start=len(verts)-1;verts.append(tuple(np.mean(np.array(verts[(rows-1)*cols:rows*cols]),axis=0)));end=len(verts)-1
   for j in range(cols):k=(j+1)%cols;faces.extend([(start,k,j),(end,(rows-1)*cols+j,(rows-1)*cols+k)])
   a.mesh(f'Lash234 / {key} / {side} / {n}',verts,faces,lashmat,'eyelashes')
   anchors.append({'side':side,'stroke':n,'root':[x,z0],'tip':[side*(.15+ps[-1,0]),float(ps[-1,1])],'root_eye_hit':eye_tree.ray_cast(Vector((x,-1,z0)),Vector((0,1,0)))[0] is not None})
 assert all(a['root_eye_hit'] for a in anchors)
 assert protected=={k:v for k,v in u.object_geometry(s).items() if s.objects[k].get('component159')!='eyelashes'}
 u.bake(s);bpy.ops.file.pack_all();path=O/'sources'/f'Feminine-{key}-lashes.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene
 for angle in ['front','threequarter']:u.render(s,O/'renders'/f'Feminine-{key}-source-{angle}.png',384,angle)
 if '--quick' in sys.argv:continue
 glb=O/'components'/f'Feminine-{key}-lashes.glb';ex.export(s,glb,'eyelashes')
 for ob in list(s.objects):
  if ob.get('component159')=='eyelashes':u.delete(ob)
 imported(glb,'eyelashes')
 for angle in ['front','threequarter','profile','rightprofile','top','underside']:u.render(s,O/'renders'/f'Feminine-{key}-export-{angle}.png',384,angle)
 for tone in range(4):u.tone(s,tone);u.render(s,O/'portraits'/f'Feminine-{key}-tone{tone}.png',128,'front')
 records[key]={'source':str(path),'source_sha256':u.sha(path),'glb':str(glb),'glb_sha256':u.sha(glb),'eye_source':str(eye_path),'eye_sha256':u.sha(eye_path),'mouth_source':str(mouth_path),'mouth_sha256':u.sha(mouth_path),'protected_neighbors_exact':True,'anchors':anchors,'style':'Two short swept tapered strokes per eye, seated on actual eye/head support. Separate optional review component.'}
 u.dump(O/'lashes234.json',records);print('LASHES234',key,flush=True)
