"""Owner259: shorter lateral banks, actual214 curved direction and new forward Crop."""
import sys,json,math,hashlib,shutil
from pathlib import Path
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue258')
import refine258 as prev258
from refine258 import *
P=Path('E:/Ravedio-Avatar/catalogue259');W=P/'pass1';R=P.parent/'floating138/mobile-preview'
for folder in ['sources','components','renders']:(W/folder).mkdir(parents=True,exist_ok=True)

def strip_tip_materials(ob):
 base=next(m for m in ob.data.materials if 'blended terminal' not in m.name);ob.data.materials.clear();ob.data.materials.append(base)
 for face in ob.data.polygons:face.material_index=0

def shorter_banks(s):
 report=[]
 for ob in [o for o in s.objects if o.type=='MESH' and o.get('component159')=='hair' and len(o.data.vertices)==2530]:
  strip_tip_materials(ob)
  if not any(k in ob.name for k in ['Side part main','Side part short','Side part crown']):continue
  j=int(ob.name.split()[-1]) if not ob.name.endswith('crown') else 0;target=(2.142+.008*math.sin(j*.9)) if 'crown' not in ob.name else 2.12
  pts=[(ob.matrix_world@v.co).copy() for v in ob.data.vertices];centers=[pts[0]]+[sum(pts[1+i*32:1+(i+1)*32],Vector())/32 for i in range(79)]+[pts[-1]]
  end=next(i for i in range(36,81) if centers[i].z<target);f=(centers[end-1].z-target)/(centers[end-1].z-centers[end].z);endparam=(end-1+f)/80;new=[]
  for row in range(81):
   t=row/80;u=t-(1-endparam)*smooth((t-.30)/.70);z=u*80;k=min(79,int(z));new.append(centers[k].lerp(centers[k+1],z-k))
  inv=ob.matrix_world.inverted()
  for i,v in enumerate(ob.data.vertices):
   row=0 if i==0 else 80 if i==2529 else (i-1)//32+1
   if row<=24:continue
   lo=max(0,row-1);hi=min(80,row+1);rotation=(centers[hi]-centers[lo]).rotation_difference(new[hi]-new[lo]);v.co=inv@(new[row]+rotation@(pts[i]-centers[row]))
  report.append(dict(name=ob.name,end_before_z=centers[-1].z,end_after_z=new[-1].z,source_path_end=endparam,upper_first30pct_exact=True,original_rounded_cross_sections=True))
 return report

def direction214(s):
 for ob in list(s.objects):
  if ob.get('component159')=='hair' and 'short sculpted direction' in ob.name:u.delete(ob)
 imported214=imported(R/'214/Masculine-taper-hair.glb','hair');fine=[o for o in imported214 if 'Taper fine direction' in o.name];assert len(fine)==1
 for ob in imported214:
  if ob not in fine:u.delete(ob)
 ob=fine[0];ob.name='Hair259 / actual214 curved direction';col=ob.data.color_attributes[0];alphas=np.ones(len(ob.data.vertices),dtype='f')
 if col.domain=='POINT':alphas=np.array([x.color[3] for x in col.data])
 else:
  for poly in ob.data.polygons:
   for li,vi in zip(poly.loop_indices,poly.vertices):alphas[vi]=col.data[li].color[3]
 before=np.array([ob.matrix_world@v.co for v in ob.data.vertices]);inverse=ob.matrix_world.inverted();RADIUS=Vector((.48,.405,.455))
 for v in ob.data.vertices:
  p=ob.matrix_world@v.co;d=p-a.C;scaled=Vector((d.x/RADIUS.x,d.y/RADIUS.y,d.z/RADIUS.z));th=math.atan2(scaled.y,scaled.x);ang=math.acos(max(-1,min(1,scaled.normalized().z)));cs=math.cos(th);sn=math.sin(th);oldsurface=Vector((RADIUS.x*math.sin(ang)*math.copysign(abs(cs)**.96,cs),RADIUS.y*math.sin(ang)*math.copysign(abs(sn)**.96,sn),RADIUS.z*math.cos(ang)));N=d.normalized();hit,_,_,_=c.HEAD.ray_cast(a.C,N,2);assert hit is not None;v.co=inverse@(hit+N*max(.0005,d.length-oldsurface.length))
 prev258.vertex_alpha(ob,[(1,1,1,float(alpha)) for alpha in alphas]);m=prev258.alpha_material('Hair259 / directional fade marks214',rough=.49);bs=m.node_tree.nodes['Principled BSDF'];bs.inputs['Specular IOR Level'].default_value=.26;bs.inputs['Coat Weight'].default_value=.02;m['hairShade258']=1.;ob.data.materials.clear();ob.data.materials.append(m)
 for face in ob.data.polygons:face.material_index=0
 ob.data.update();after=np.array([ob.matrix_world@v.co for v in ob.data.vertices]);return dict(source='214/Masculine-taper-hair.glb',source_mesh='Hair / Taper fine direction',vertices=len(ob.data.vertices),alpha_sha256=hashlib.sha256(alphas.astype('<f4').tobytes()).hexdigest(),source_direction_geometry_reused=True,reseated_max_shift=float(np.linalg.norm(after-before,axis=1).max()))

def crop(s):
 for ob in list(s.objects):
  if ob.get('component159')=='hair':u.delete(ob)
 saved=prev258.CFG['fade_span'];prev258.CFG['fade_span']=.30
 try:prev258.sides258()
 finally:prev258.CFG['fade_span']=saved
 old.init();mats=[]
 for j in range(3):
  m=a.material('Hair259 / Crop sculpt '+str(j),tuple(x*(1-.035*j) for x in [.12,.047,.026]),.35);old.normal_texture(m,'long');bs=m.node_tree.nodes['Principled BSDF'];bs.inputs['Specular IOR Level'].default_value=.34;bs.inputs['Coat Weight'].default_value=.055;m['hairShade258']=1-.035*j
  for n in m.node_tree.nodes:
   if n.type=='NORMAL_MAP':n.inputs['Strength'].default_value=.12
  mats.append(m)
 created=[]
 def lock(name,points,widths,depths,j):
  ob=old.lock(name,points,widths,depths,phase=j*.51,mat=mats[j%3],n=64,sides=24,grain=.00075)
  ob.name='Hair259 / Crop '+name
  for uv in ob.data.uv_layers.active.data:uv.uv.y=1-uv.uv.y
  created.append(ob.name);return ob
 for j,x0 in enumerate(np.linspace(-.285,.285,7)):
  points=[]
  for t in np.linspace(0,1,64):
   x=x0-.022*t+.010*math.sin(PI*t)*math.sin(j*.83);y0=.13+.016*math.sin(j*.7);y1=(-.317-.008*math.sin(j*1.7))*math.sqrt(1-(x0/.51)**2);y=y0+(y1-y0)*t+.004*math.sin(2*PI*t+j*.3);points.append(c.surf(x,y,.026+.036*math.sin(PI*t)**.85+.004*math.sin(t*5+j*.8)*math.sin(PI*t)))
  lock('forward lock '+str(j),points,[.016,.046,.058,.050,.030,.012],[.012,.024,.030,.029,.020,.010],j)
 for j,x0 in enumerate(np.linspace(-.25,.25,5)):
  points=[]
  for t in np.linspace(0,1,64):
   x=x0-.015*t+.008*math.sin(PI*t+j);y0=.295*math.sqrt(1-(x0/.49)**2);y=y0+(.045-y0)*t;points.append(c.surf(x,y,.018+.022*math.sin(PI*t)))
  lock('crown flow '+str(j),points,[.018,.070,.080,.072,.040,.010],[.010,.020,.025,.020,.014,.007],j+7)
 for side in [-1,1]:
  for j,phi in enumerate([1.04,1.55,2.11]):
   points=[c.sp(.50+.68*t,side*(phi-.055*t),.024+.010*math.sin(PI*t)) for t in np.linspace(0,1,64)]
   lock('side flow '+str(side)+' '+str(j),points,[.014,.055,.058,.047,.027,.008],[.009,.020,.022,.018,.011,.006],j+12)
 return dict(label='Crop',key='sidepart',new_geometry=True,locks=created,flow='Crown forward with slight diagonal drift; no hard part; compact textured fringe',fade_span=.30)

def render_views(s,style):
 c.gpu()
 for angle in ['front','threequarter','profile','rightprofile','rear','rearquarter','top','underside']:
  u.camera(s,'rear' if angle=='rearquarter' else angle,512,False)
  if angle=='rearquarter':
   target=Vector((0,0,1.88));s.camera.location=target+Vector((-4,8,0));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler()
  s.camera.data.ortho_scale=1.65;s.cycles.samples=24;s.render.filepath=str(W/'renders'/f'{style}-{angle}.png');floor=s.objects.get('Studio floor');hidden=floor.hide_render if floor else False
  if floor and angle=='underside':floor.hide_render=True
  try:bpy.ops.render.render(write_still=True)
  finally:
   if floor:floor.hide_render=hidden

if __name__=='__main__':
 out={}
 for style in ['taper','sidepart','curly-top']:
  bpy.ops.wm.open_mainfile(filepath=str(P.parent/'catalogue258/pass4/sources'/f'Masculine-{style}-hair258.blend'));s=bpy.context.scene;frozen=protect(s);a.setup();c.reset_head(s);report={}
  if style=='sidepart':report=crop(s)
  elif style=='taper':report['banks']=shorter_banks(s);report['tip_alpha']=prev258.tips258(s)
  report['direction214']=direction214(s);check(s,frozen);u.bake(s);source=W/'sources'/f'Masculine-{style}-hair259.blend';target=W/'components'/f'Masculine-{style}-hair259.glb';assert not source.exists() and not target.exists();bpy.ops.outliner.orphans_purge(do_recursive=True);bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True);ex.export(s,target,'hair');prev258.patch258(target,s);report.update(source=str(source),path=str(target),other_geometry_preserved=True);out[style]=report;(W/'hair259.json').write_text(json.dumps(out,indent=2)+'\n');render_views(s,style);print('SOURCE259',style,flush=True)
 shutil.copy2(__file__,W/'build259.py');print('SOURCE259_COMPLETE3',flush=True)
