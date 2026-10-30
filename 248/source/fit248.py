"""Authored rear drapes and covered hair; accepted247 front stays fixed."""
import sys,json,math
from pathlib import Path
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue235')
import common235 as c
c.P=Path(__file__).parent
from common235 import *
import bmesh
from scarf_support235 import convex_support
BASE=P.parent/'catalogue247';CAT=json.loads((R/'247/catalogue247.json').read_text())
for folder in ['sources','components','review1','review2','fixtures','browser']:(P/folder).mkdir(exist_ok=True)
FAMILIES={'Feminine':{'bob':'compact','ponytail':'gathered','straight':'long','curls':'volume','side-sweep':'long','space-buns':'compact','twin-braids':'compact','box-braids':'volume'},'Masculine':{k:'compact' for k in CAT['builds']['Masculine']['hair']}}

def normalise(ob):
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()

def drape(build,top,family):
 bpy.ops.wm.open_mainfile(filepath=str(BASE/'sources'/f'{build}-{top}-pashmina247.blend'));s=bpy.context.scene
 ob=next(o for o in s.objects if 'joined hood wrap and ends239' in o.name);n=len(ob.data.vertices)//2;uv={};old=[ob.matrix_world@v.co for v in ob.data.vertices]
 protected={k:v for k,v in u.object_geometry(s).items() if k!=ob.name}
 for f in ob.data.polygons:
  if max(f.vertices)>=n:continue
  for li,i in zip(f.loop_indices,f.vertices):uv[i]=ob.data.uv_layers.active.data[li].uv.copy()
 desired=[p.copy() for p in old];changed=[]
 for i,q in uv.items():
  if not (0<=q.x<=1 and q.y>.36):continue
  p=old[i];rear=math.sin(math.pi*q.x)**.9;low=smooth((1.79-p.z)/.30);terminal=smooth((q.y-.77)/.18)
  if family=='compact':rx=.255;ry=.18;dz=-.065
  elif family=='long':rx=.44;ry=.39;dz=.015
  elif family=='volume':rx=.47;ry=.42;dz=.035
  else:rx=.30;ry=.325;dz=.020
  # Broad cowl slack bridges small hollows; it is not a neck ring, rear
  # curtain or per-lock imprint. Front/side sewn roots stay untouched.
  z=p.z+dz*rear*low
  lift=smooth((z-1.42)/.36)
  target=Vector((-math.cos(math.pi*q.x)*(rx+(.50-rx)*lift),math.sin(math.pi*q.x)*(ry+(.445-ry)*lift),z))
  delta=(target-p)*low*rear
  desired[i]=p+delta;desired[i+n]=old[i+n]+delta
  if delta.length>1e-9:changed.append(i)
 inv=ob.matrix_world.inverted().to_3x3()
 for i in changed:
  for j in [i,i+n]:ob.data.vertices[j].co+=inv@(desired[j]-old[j])
 normalise(ob)
 changed_ids=set(changed)
 assert all((ob.matrix_world@ob.data.vertices[i].co-old[i]).length<1e-8 for i in range(len(old)) if i%n not in changed_ids)
 assert all(u.object_geometry(s).get(k)==v for k,v in protected.items())
 bm=bmesh.new();bm.from_mesh(ob.data);assert all(len(e.link_faces)==2 for e in bm.edges);bm.free()
 # Keep this source as an independently aligned component plus studio.
 # Bodies/garments have already passed the protected-geometry assertion;
 # assembled fixtures are saved separately after the actual GLB review.
 for o in list(s.objects):
  if o.type in ['MESH','CURVE'] and o.get('component159')!='headgear' and o.name!='Studio floor':u.delete(o)
 bpy.data.orphans_purge(do_recursive=True)
 key=f'{build}-{top}-{family}-pashmina248';parts=save(s,key,['headgear'])
 return dict(source=str(P/'sources'/f'{key}.blend'),component=parts['headgear'],family=family,top=top,closed_surface=True,front247_exact=True,other_components_exact=True,modified_outer_vertices=len(changed))

def fit_hair(build,style,cloth=None):
 top='open' if build=='Feminine' else 'tank'
 bpy.ops.wm.open_mainfile(filepath=str(BASE/'sources'/f'{build}-{top}-pashmina247.blend'))
 s=bpy.context.scene;remove(['hair']);a.setup();h._support_cache=None
 if cloth:
  remove(['headgear']);cloth_obs=imported(P/cloth['component'],'headgear');cloth_tree=tree(cloth_obs)
 else:cloth_tree=None
 family=FAMILIES[build][style];records=[]
 if family=='compact':
  obs=imported((R/'247'/CAT['fits'][build+'-'+style]['pashmina']['hair']).resolve(),'hair');changed=0
  for o in obs:
   inv=o.matrix_world.inverted()
   for v in o.data.vertices:
    p=o.matrix_world@v.co
    if p.z<1.47 or p.y<-.20 or not cloth_tree:continue
    radial=p-a.C;hit,_,_,distance=cloth_tree.ray_cast(a.C,radial.normalized(),1.5)
    if hit is not None and radial.length>distance-.018:v.co=inv@(a.C+radial.normalized()*max(.1,distance-.018));changed+=1
   normalise(o)
  method='Existing compact arrangement with clearance refreshed against the actual248 cloth only in concealed crown/nape regions. Exposed front and free lengths retained.'
  records.append(dict(concealed_vertices=changed,exposed_front_preserved=True))
 elif style=='ponytail':
  obs=imported((R/'247'/CAT['fits'][build+'-'+style]['pashmina']['hair']).resolve(),'hair')
  for o in obs:
   if len(o.data.vertices)==691:u.delete(o)
  from hair235 import lock
  for k in range(5):
   dx=(k-2)*.017
   pts=[(dx*.4,.24,1.68),(dx*.7,.27,1.57),(dx+.010,.305,1.47),(dx+.027,.385,1.37),(dx+.012,.415,1.27),(dx-.005,.390,1.18+.013*math.cos(k))]
   lock('Hair / draped low pony248 '+str(k),pts,[.023,.030,.032,.030,.019,.003],[.018,.025,.027,.026,.016,.003],k*.8,n=72,tip=.13)
  method='Hood-specific low gathered pony: whole sculpted locks follow one smooth descent beneath the rear edge; front locks and pulled-back crown retained.'
 elif build=='Feminine' and style in ['straight','curls','side-sweep','box-braids']:
  garment_obs=[o for o in s.objects if o.type=='MESH' and (o.name=='Skin / rounded torso' or o.get('component159')=='top') and 'sleeve' not in o.name.lower()]
  hoodie=imported((R/'247'/CAT['builds'][build]['tops']['sweatshirt']['path']).resolve(),'supportOnly248');envelope=convex_support(garment_obs+hoodie)
  for o in hoodie:u.delete(o)
  def back_y(x,z,radius=.034):
   hits=[]
   for dx in [-radius,0,radius]:
    hit,_,_,_=envelope.ray_cast(Vector((x+dx,2,z)),Vector((0,-1,0)),4)
    if hit is not None:hits.append(hit.y)
   return max(hits)+.034 if hits else None
  # The old lower lengths were damaged by pointwise cloth fitting. Retain
  # only their genuinely concealed crown and build deliberate exit guides.
  obs=imported((R/'247'/CAT['fits'][build+'-'+style]['pashmina']['hair']).resolve(),'hair')
  material=next(m for o in obs for m in o.data.materials if 'ties' not in m.name.lower() and 'root' not in m.name.lower())
  for o in obs:
   if o.type!='MESH':continue
   bm=bmesh.new();bm.from_mesh(o.data);plane=Vector((0,0,1.78));local=o.matrix_world.inverted()@plane;normal=o.matrix_world.to_3x3().transposed()@Vector((0,0,1))
   bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=local,plane_no=normal,clear_inner=True,dist=1e-6)
   if not bm.faces:bm.free();u.delete(o);continue
   bm.to_mesh(o.data);bm.free()
  a.M['hair']=material
  from hair235 import lock
  from hair227 import plait
  curly=style=='curls';braided=style=='box-braids';count=12 if braided else 9
  for k in range(count):
   x=-.23+k*.46/(count-1);phase=k*.63;end=1.20+.018*math.cos(k*1.7)
   edge=(abs(x)/.23)**2
   pts=[(x*.72,.34-.03*edge,1.71),(x*.9,.30-.04*edge,1.56),(x,.26-.06*edge,1.43),(x*.98,back_y(x*.98,1.33) or .27,1.33),(x*.94,back_y(x*.94,end) or .27,end)]
   if braided:plait('Hair / covered rear braid248 '+str(k),pts,.029)
   else:
    ps=a.sample(pts,72)
    for j,p in enumerate(ps):
     t=j/71;env=smooth((1.42-p.z)/.14);p.x+=(.021 if curly else .005)*math.sin(t*(2.7 if curly else 1.4)*math.pi+phase)*env;p.y+=(.012 if curly else .004)*math.sin(t*2.4*math.pi+phase)*env
    lock('Hair / covered '+style+' rear248 '+str(k),ps,[.026,.046,.046,.041,.013],[.015,.024,.024,.022,.009],phase,n=72,tip=.10)
  for side in [-1,1]:
   for k in range(2 if braided else 1):
    x=side*(.345+.038*k)
    pts=[(side*.36,-.245,1.99),(side*.395,-.25,1.79),(side*.375,-.27,1.58),(x,-.32,1.39),(side*(.33+.03*k),-.315,1.20+.025*k)]
    if braided:plait('Hair / covered face braid248 '+str(side)+' '+str(k),pts,.030)
    else:
     ps=a.sample(pts,72)
     for j,p in enumerate(ps):
      t=j/71;wave=(.016 if curly else .005)*math.sin(t*2.4*math.pi+side*.4)*smooth((t-.2)/.3);p.x+=side*wave;p.y+=wave*.45
     lock('Hair / covered '+style+' face248 '+str(side),ps,[.018,.027,.030,.030,.008],[.010,.019,.021,.020,.006],side*.7,n=72,tip=.12)
  method='Retained concealed crown with newly authored continuous rear and face exit guides; visible widths/relief preserved by sculpted sections, never individual cloth projection.'
  records.append(dict(method='Fresh natural lower-edge guides',rear_locks=count,front_locks=4 if braided else 2,concealed_crown_boundary_z=1.78))
 else:
  raise ValueError(('Missing authored covered arrangement',build,style))
 key=f'{build}-{style}-covered248';parts=save(s,key,['hair'])
 return dict(source=str(P/'sources'/f'{key}.blend'),component=parts['hair'],family=family,style=style,method=method,sections=records,uncovered_unchanged=True)

def assembly(build,top,style,cloth,hair):
 bpy.ops.wm.open_mainfile(filepath=str(BASE/'sources'/f'{build}-{top}-pashmina247.blend'));s=bpy.context.scene
 remove(['hair','headgear']);library(cloth['source'],['headgear']);imported(P/hair['component'],'hair')
 return s

def views(s,key,close=True):
 render(s,key,['front','threequarter','profile','rightprofile','rear','top','underside'],size=320,body=True)
 if close:
  for angle,direction in [('rear',Vector((0,8,0))),('rear-quarter',Vector((-6,8,0))),('profile',Vector((-8,0,0)))]:
   u.camera(s,'rear',640,True);target=Vector((0,0,1.51));s.camera.location=target+direction;s.camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=1.1;s.cycles.samples=16;s.render.filepath=str(P/'review1'/f'{key}-detail-{angle}.png');bpy.ops.render.render(write_still=True)

if __name__=='__main__':
 cloths=json.loads((P/'fits248.json').read_text()) if (P/'fits248.json').exists() else {};hairs=json.loads((P/'hair248.json').read_text()) if (P/'hair248.json').exists() else {}
 draft='--draft' in sys.argv
 looks=[('Feminine','ponytail'),('Feminine','straight'),('Feminine','curls'),('Feminine','box-braids'),('Masculine','taper')] if draft else [(b,k) for b in FAMILIES for k in FAMILIES[b]]
 only=next((arg.split('=',1)[1].split(',') for arg in sys.argv if arg.startswith('--styles=')),None)
 if only:looks=[(b,k) for b,k in looks if k in only]
 if '--cloth-refresh' in sys.argv:looks=[]
 for build,style in looks:
  top='open' if build=='Feminine' else 'tank';family=FAMILIES[build][style];ck=build+'-'+top+'-'+family
  if '--compact-refresh' in sys.argv and family!='compact':continue
  if '--remaining' in sys.argv and build+'-'+style in hairs and ck in cloths:continue
  if ('--remaining' not in sys.argv and '--compact-refresh' not in sys.argv and '--hair-refresh' not in sys.argv) or ck not in cloths:cloths[ck]=drape(build,top,family);u.dump(P/'fits248.json',cloths)
  hairs[build+'-'+style]=fit_hair(build,style,cloths[ck]);u.dump(P/'hair248.json',hairs)
  s=assembly(build,top,style,cloths[ck],hairs[build+'-'+style]);views(s,build+'-'+style,True);print('FIT248',build,style,flush=True)
 if '--all-tops' in sys.argv:
  for build in FAMILIES:
   for family in sorted(set(FAMILIES[build].values())):
    families=next((x.split('=',1)[1].split(',') for x in sys.argv if x.startswith('--families=')),None)
    if families and family not in families:continue
    style=next(k for k,v in FAMILIES[build].items() if v==family)
    for top in CAT['builds'][build]['tops']:
     key=build+'-'+top+'-'+family
     if key in cloths and '--cloth-refresh' not in sys.argv:continue
     cloths[key]=drape(build,top,family);u.dump(P/'fits248.json',cloths)
     s=assembly(build,top,style,cloths[key],hairs[build+'-'+style]);render(s,key,['front','profile','rear'],size=256,body=True)
     print('DRAPE248',key,flush=True)
