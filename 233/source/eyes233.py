import bpy,sys,math,json
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).parent;O=P/'output'
sys.path.insert(0,str(P.parent/'refinement224'));sys.path.insert(0,str(P.parent/'catalogue226'))
import utils224 as u,sculpt226 as a,export226 as ex
bpy.context.preferences.filepaths.save_version=0
for d in ['sources','components','renders','portraits']:(O/d).mkdir(parents=True,exist_ok=True)
shapes={
 'tapered':{'label':'Tapered oval','center':(0,0),'curves':[
 [[-.055,-.005],[-.055,.027],[-.035,.064],[-.009,.066]],
 [[-.009,.066],[.020,.068],[.057,.042],[.077,.016]],
 [[.077,.016],[.085,.007],[.081,-.003],[.071,-.011]],
 [[.071,-.011],[.050,-.036],[.015,-.061],[-.010,-.060]],
 [[-.010,-.060],[-.040,-.061],[-.057,-.036],[-.055,-.005]]]},
 'hooded':{'label':'Soft hooded','center':(0,-.005),'curves':[
 [[-.040,.037],[-.020,.044],[.014,.045],[.035,.040]],
 [[.035,.040],[.051,.037],[.055,.016],[.052,.002]],
 [[.052,.002],[.047,-.040],[.030,-.064],[.005,-.066]],
 [[.005,-.066],[-.027,-.067],[-.054,-.036],[-.054,.002]],
 [[-.054,.002],[-.055,.019],[-.052,.034],[-.040,.037]]]},
 'bean':{'label':'Rounded bean','center':(-.005,.006),'curves':[
 [[-.061,-.013],[-.065,.032],[-.039,.075],[-.009,.075]],
 [[-.009,.075],[.027,.075],[.062,.050],[.066,.018]],
 [[.066,.018],[.066,-.007],[.052,-.018],[.038,-.017]],
 [[.038,-.017],[.016,-.015],[.013,-.048],[-.009,-.057]],
 [[-.009,-.057],[-.035,-.067],[-.059,-.042],[-.061,-.013]]]}}
shapes['squint']={'label':'Curved squint','center':(0,.012),'curves':[
 [[-.071,-.010],[-.060,.020],[-.030,.060],[-.005,.060]],
 [[-.005,.060],[.025,.062],[.060,.027],[.072,-.004]],
 [[.072,-.004],[.080,-.021],[.071,-.042],[.058,-.043]],
 [[.058,-.043],[.038,-.046],[.018,-.037],[-.003,-.037]],
 [[-.003,-.037],[-.025,-.037],[-.048,-.045],[-.061,-.043]],
 [[-.061,-.043],[-.075,-.041],[-.079,-.023],[-.071,-.010]]]}

shapes={k:v for k,v in shapes.items() if k in ['tapered','bean']}

def tree(ob):return BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[list(p.vertices) for p in ob.data.polygons])
def bezier(ps):
 p=np.asarray(ps);return [(1-t)**3*p[0]+3*(1-t)**2*t*p[1]+3*(1-t)*t*t*p[2]+t**3*p[3] for t in np.linspace(0,1,32,endpoint=False)]
only=next((x.split('=',1)[1] for x in sys.argv if x.startswith('--only=')),None)
records=json.loads((O/'eyes233.json').read_text(encoding='utf8')) if only and (O/'eyes233.json').exists() else {}
for build,case in [('Feminine','Feminine-uncovered'),('Masculine','Masculine-taper')]:
 for key,shape in shapes.items():
  if only and key!=only:continue
  src=P.parent/'refinement224/scenes'/f'{case}.blend';bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;s.cycles.device='CPU'
  protected={k:v for k,v in u.object_geometry(s).items() if s.objects[k].get('component159')!='eyes'}
  eyes=[o for o in s.objects if o.get('component159')=='eyes']
  dark=next(o for o in eyes if o.name.startswith('Eye /')).data.materials[0]
  shine=next(o for o in eyes if o.name.startswith('Eye highlight / main')).data.materials[0]
  glint=next(o for o in eyes if o.name.startswith('Eye highlight / small')).data.materials[0]
  material_values={m.name:{i:tuple(m.node_tree.nodes.get('Principled BSDF').inputs[i].default_value) if i=='Base Color' else m.node_tree.nodes.get('Principled BSDF').inputs[i].default_value for i in ['Base Color','Roughness','Metallic','Coat Weight']} for m in [dark,shine,glint]}
  if key=='tapered':u.render(s,O/'renders'/f'{build}-original-front.png',384,'front')
  for ob in eyes:u.delete(ob)
  support=tree(s.objects['Skin / soft oval head']);outline=np.array([q for c in shape['curves'] for q in bezier(c)]);N=len(outline);rows=20;cx,cz=shape['center']
  for side in [-1,1]:
   def point(x,z,r,back=False):
    hit=support.ray_cast(Vector((side*(.15+x),-1,1.895+z)),Vector((0,1,0)))[0];assert hit is not None
    hit.y-=(-.003 if back else .0025+.013*max(0,1-r*r)**1.5);return hit
   vv=[point(cx,cz,0)];ff=[]
   for rr in np.linspace(1/rows,1,rows):
    for x,z in outline:vv.append(point(cx+(x-cx)*rr,cz+(z-cz)*rr,rr))
   for j in range(N):ff.append((0,1+j,1+(j+1)%N))
   for i in range(rows-1):
    for j in range(N):p=1+i*N+j;n=1+i*N+(j+1)%N;ff.append((p,p+N,n+N,n))
   off=len(vv);vv += [point(x,z,1,True) for x,z in outline];back=len(vv);vv.append(point(cx,cz,0,True))
   for j in range(N):k=(j+1)%N;ff.extend([(1+(rows-1)*N+j,off+j,off+k,1+(rows-1)*N+k),(back,off+k,off+j)])
   ob=a.mesh('Eye / '+key+'233 '+str(side),vv,ff,dark,'eyes');surface=tree(ob)
   for name,x,z,rx,rz,mat in [('main',side*.15-.010,1.909 if key=='hooded' else 1.916,.0085,.0085 if key=='hooded' else .0115,shine),('small',side*.15+.016,1.882 if key=='squint' else 1.877,.0026,.0030,glint)]:
    verts=[];faces=[];cols=36;rs=8
    for rr in np.linspace(0,1,rs):
     for t in np.linspace(0,2*math.pi,cols,endpoint=False):
      hit=surface.ray_cast(Vector((x+rx*rr*math.cos(t),-1,z+rz*rr*math.sin(t))),Vector((0,1,0)))[0];assert hit is not None
      verts.append(hit+Vector((0,-.0008,0)))
    for i in range(rs-1):
     for j in range(cols):p=i*cols+j;n=i*cols+(j+1)%cols;faces.append((p,n,n+cols,p+cols))
    a.mesh('Eye highlight / '+name+'233 '+str(side),verts,faces,mat,'eyes')
  assert protected=={k:v for k,v in u.object_geometry(s).items() if s.objects[k].get('component159')!='eyes'}
  u.bake(s);bpy.ops.file.pack_all();path=O/'sources'/f'{build}-{key}.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
  bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene
  for angle in ['front','threequarter']:u.render(s,O/'renders'/f'{build}-{key}-source-{angle}.png',384,angle)
  if '--quick' in sys.argv:continue
  glb=O/'components'/f'{build}-eyes-{key}.glb';ex.export(s,glb,'eyes')
  for ob in list(s.objects):
   if ob.get('component159')=='eyes':u.delete(ob)
  bpy.ops.import_scene.gltf(filepath=str(glb))
  for angle in ['front','threequarter','profile','rightprofile','top','underside']:u.render(s,O/'renders'/f'{build}-{key}-export-{angle}.png',384,angle)
  for tone in range(4):u.tone(s,tone);u.render(s,O/'portraits'/f'{build}-{key}-tone{tone}.png',128,'front')
  records[build+'-'+key]={'build':build,'shape':key,'label':shape['label'],'source':str(path),'source_sha256':u.sha(path),'glb':str(glb),'glb_sha256':u.sha(glb),'baseline_source':str(src),'baseline_sha256':u.sha(src),'protected_neighbors_exact':True,'eye_centers':[.15,1.895],'materials_unchanged_from_baseline':material_values}
  u.dump(O/'eyes233.json',records);print('EYES233',build,key,flush=True)
u.dump(O/'outlines233.json',shapes)
