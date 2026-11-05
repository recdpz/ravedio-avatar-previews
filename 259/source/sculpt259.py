import sys,json,math,shutil
from pathlib import Path
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue259')
import build259 as b
from build259 import *
P=Path('E:/Ravedio-Avatar/catalogue259');W=P/'pass3';b.W=W
for name in ['sources','components','renders']:(W/name).mkdir(parents=True,exist_ok=True)

def cut_banks(s):
 report=[]
 for ob in [o for o in s.objects if o.type=='MESH' and o.get('component159')=='hair' and len(o.data.vertices)==2530]:
  b.strip_tip_materials(ob)
  if not any(k in ob.name for k in ['Side part main','Side part short','Side part crown']):continue
  j=int(ob.name.split()[-1]) if not ob.name.endswith('crown') else 0;target=2.11+.008*math.sin(j*.9) if 'crown' not in ob.name else 2.10
  pts=[(ob.matrix_world@v.co).copy() for v in ob.data.vertices];centers=[pts[0]]+[sum(pts[1+i*32:1+(i+1)*32],Vector())/32 for i in range(79)]+[pts[-1]];end=next(i for i in range(36,81) if centers[i].z<target);f=(centers[end-1].z-target)/(centers[end-1].z-centers[end].z);endparam=(end-1+f)/80;capstart=endparam-.14;inverse=ob.matrix_world.inverted()
  def sample(u):
   z=u*80;k=min(79,int(z));v=z-k;return centers[k].lerp(centers[k+1],v),k,v
  for i,vertex in enumerate(ob.data.vertices):
   row=0 if i==0 else 80 if i==2529 else (i-1)//32+1;t=row/80
   if t<=capstart:continue
   cap=(t-capstart)/(1-capstart);u=capstart+(endparam-capstart)*cap;center,k,v=sample(u)
   if i==2529:point=center
   else:
    col=(i-1)%32;d0=Vector() if k==0 else pts[1+(k-1)*32+col]-centers[k];d1=pts[1+k*32+col]-centers[k+1];point=center+d0.lerp(d1,v)*math.sqrt(max(.0001,1-cap*cap))
   vertex.co=inverse@point
  report.append(dict(name=ob.name,end_before_z=centers[-1].z,end_after_z=sample(endparam)[0].z,original_path_end=endparam,round_cap_start=capstart,upper_positions_exact_before=capstart,method='Original path truncated and rounded with interpolated original cross sections; no relocated/compressed path'))
 return report

def sculpt_crop(s):
 for ob in list(s.objects):
  if ob.get('component159')=='hair':u.delete(ob)
 oldspan=prev258.CFG['fade_span'];prev258.CFG['fade_span']=.30
 try:prev258.sides258()
 finally:prev258.CFG['fade_span']=oldspan
 mat=a.material('Hair259 / forward Crop sculpt',(.12,.047,.026),.35);old.normal_texture(mat,'long');bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Specular IOR Level'].default_value=.34;bs.inputs['Coat Weight'].default_value=.055
 for n in mat.node_tree.nodes:
  if n.type=='NORMAL_MAP':n.inputs['Strength'].default_value=.18
 nu,nv=144,176;verts=[];under=[];uvs=[];faces=[]
 for j in range(nv+1):
  t=j/nv;width=.36*(1-t)+.345*t+.075*math.sin(PI*t)
  for i in range(nu+1):
   side=i/nu*2-1;x=side*width+.025*math.sin(PI*t)*(1-side*side);endangle=.87+.014*math.sin(side*19+.6)+.009*math.sin(side*39+1.2);endx=side*.345;endy=-.405*math.sqrt(max(.015,math.sin(endangle)**2-(endx/.48)**2));startx=side*.36;starty=.405*math.sqrt(max(.015,math.sin(1.05)**2-(startx/.48)**2));y=starty*(1-t)+endy*t
   hit=c.surf(x,y,0);N=(hit-a.C).normalized();phase=(side+1)*4.2+.18*math.sin(t*4.7)+.12*math.sin(side*4+t*2);envelope=math.sin(PI*t)**.65*(.5+.5*math.sqrt(max(0,1-side*side)));ridge=.012*(.5+.5*math.cos(phase*2*PI))**1.45*envelope;grain=.0014*math.cos(phase*2*PI*5+.3*math.sin(t*5))*envelope;clumps=0
   for sc,amp in [(-.53,.010),(.07,.016),(.59,.011)]:clumps+=amp*math.exp(-((side-sc-.07*math.sin(t*3))/.18)**2)*math.sin(PI*t)**1.8
   lift=.014+.025*math.sin(PI*t)**.70+ridge+grain+clumps;verts.append(tuple(hit+N*lift));under.append(tuple(hit+N*.003));uvs.append(((side+1)/2+.022*math.sin(t*4.7),1-t))
 count=len(verts);verts+=under;uvs+=uvs
 for j in range(nv):
  for i in range(nu):
   k=j*(nu+1)+i;faces.append((k,k+nu+1,k+nu+2,k+1));faces.append((count+k,count+k+1,count+k+nu+2,count+k+nu+1))
 edge=list(range(nu+1))+[j*(nu+1)+nu for j in range(1,nv+1)]+list(range(nv*(nu+1)+nu-1,nv*(nu+1)-1,-1))+[j*(nu+1) for j in range(nv-1,0,-1)]
 for i,k in enumerate(edge):n=edge[(i+1)%len(edge)];faces.append((k,n,count+n,count+k))
 ob=a.mesh('Hair259 / continuous forward Crop',verts,faces,mat,'hair');uv=ob.data.uv_layers.new(name='Forward Crop flow259')
 for face in ob.data.polygons:
  for li,k in zip(face.loop_indices,face.vertices):uv.data[li].uv=uvs[k]
 return dict(label='Crop',key='sidepart',new_geometry=True,construction='One closed fitted flow surface with shallow varied clumps and coherent forward grooves; no layered rows of separate tubes or exposed foundation',flow='Crown to front with gentle diagonal drift, compact textured fringe, no hard part',fade_span=.30,vertices=len(verts))

out={}
for style in ['taper','sidepart','curly-top']:
 bpy.ops.wm.open_mainfile(filepath=str(P.parent/'catalogue258/pass4/sources'/f'Masculine-{style}-hair258.blend'));s=bpy.context.scene;frozen=protect(s);a.setup();c.reset_head(s);report={}
 if style=='sidepart':report=sculpt_crop(s)
 elif style=='taper':report['banks']=cut_banks(s);report['tip_alpha']=prev258.tips258(s)
 report['direction214']=b.direction214(s)
 for ob in s.objects:
  if ob.type=='MESH' and ob.get('component159')=='hair' and (style=='taper' or 'actual214 curved direction' in ob.name) and ob.data.has_custom_normals:ob.data.update();ob.data.normals_split_custom_set([(0.,0.,0.)]*len(ob.data.loops))
 report['modified_geometry_normals_rebuilt']=True;check(s,frozen);u.bake(s);source=W/'sources'/f'Masculine-{style}-hair259.blend';target=W/'components'/f'Masculine-{style}-hair259.glb';assert not source.exists() and not target.exists();bpy.ops.outliner.orphans_purge(do_recursive=True);bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True);ex.export(s,target,'hair');prev258.patch258(target,s);report.update(source=str(source),path=str(target),other_geometry_preserved=True);out[style]=report;(W/'hair259.json').write_text(json.dumps(out,indent=2)+'\n');b.render_views(s,style);print('SCULPT259',style,flush=True)
shutil.copy2(__file__,W/'sculpt259.py');print('SCULPT259_COMPLETE3',flush=True)
