import sys,json,math,hashlib
from pathlib import Path
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue260')
from common260 import *
from mathutils.bvhtree import BVHTree
from math import sin,cos,pi,sqrt
P=Path('E:/Ravedio-Avatar/catalogue261');R=P.parent/'floating138/mobile-preview';BASE=R/'260';CAT=json.loads((BASE/'catalogue260.json').read_text());W=P/'pass1'
sel=json.loads((P.parent/'catalogue260/selected260.json').read_text())
sources={k:v['source'] for k,v in sel.items()}
sources.update({'Feminine-bob':str(P.parent/'refinement208/Feminine-tank.blend'),'Feminine-curls':str(P.parent/'catalogue226/revision227/sources/Feminine-curls.blend')})

def load261(build,style):
 bpy.ops.wm.open_mainfile(filepath=str(P.parent/'catalogue251/sources'/f'{build}-assembly251.blend'));s=bpy.context.scene
 for o in list(s.objects):
  if o.type in ['MESH','CURVE'] and o.name!='Studio floor':u.delete(o)
 bc=CAT['builds'][build];top='open' if build=='Feminine' else 'tank';paths=dict(base=bc['base'],top=bc['tops'][top]['path'],bottom=bc['bottoms']['skirt' if build=='Feminine' else 'shorts']['path'],eyes=bc['eyes']['original']['path'],mouth=bc['mouths']['line']['path'])
 if build=='Feminine':paths['lashes']=bc['lashes']['original']['path']
 for group,path in paths.items():
  if path:imported((BASE/path).resolve(),group)
 with bpy.data.libraries.load(sources[build+'-'+style],link=False) as (src,dst):dst.objects=list(src.objects)
 for o in dst.objects:
  if o and o.type in ['MESH','CURVE'] and o.get('component159')=='hair':s.collection.objects.link(o)
 u.tone(s,1);a.setup();c.reset_head(s);s['build235']=build;s['hairStyle235']=style;return s

def surface_dir(th,ph):return Vector((.48*sin(th)*sin(ph),-.405*sin(th)*cos(ph),.455*cos(th))).normalized()
def roots(s,style):
 obs=[o for o in s.objects if o.type=='MESH' and o.get('component159')=='hair'];support=[o for o in obs if o.name.startswith('Recessed roots') or 'recessed layered continuation' in o.name or 'compact section-root continuation' in o.name]
 assert support
 mat=support[0].data.materials[0];vv=[];ff=[]
 for o in obs:
  if o in support:continue
  offset=len(vv);vv.extend(o.matrix_world@v.co for v in o.data.vertices);ff.extend(tuple(offset+i for i in f.vertices) for f in o.data.polygons)
 tree=BVHTree.FromPolygons(vv,ff,all_triangles=False);nu,nv=256,64;boundary=[]
 for j in range(nu):
  ph=2*pi*j/nu;ok=[]
  for th in np.linspace(.35,1.85,180):
   N=surface_dir(th,ph);hit,_,_,dist=tree.ray_cast(a.C,N,2);_,_,_,hd=c.HEAD.ray_cast(a.C,N,2)
   if hit is not None and hd is not None and -.025<dist-hd<.16:ok.append(th)
  boundary.append(max(.65,min(1.72,max(ok,default=.8)-.055)))
 # Continuous boundary follows the overlying banks; cap stays behind them.
 raw=boundary[:]
 for j in range(nu):
  weights=[(k,math.exp(-(k/2.0)**2)) for k in range(-5,6)];boundary[j]=min(raw[j],sum(raw[(j+k)%nu]*w for k,w in weights)/sum(w for k,w in weights))
 for o in support:u.delete(o)
 vv=[tuple(c.sp(0,0,.0025))];uvs=[(.5,0)];ff=[]
 for i in range(1,nv+1):
  t=i/nv
  for j in range(nu):
   ph=2*pi*j/nu;N=surface_dir(t*boundary[j],ph);hit=c.HEAD.ray_cast(a.C,N,2)[0];vv.append(tuple(hit+N*.0025));uvs.append((j/nu,t))
 for j in range(nu):ff.append((0,1+j,1+(j+1)%nu))
 for i in range(nv-1):
  for j in range(nu):aa=1+i*nu+j;bb=1+i*nu+(j+1)%nu;ff.append((aa,aa+nu,bb+nu,bb))
 ob=a.mesh('Hair261 / continuous recessed coverage',vv,ff,mat,'hair');uv=ob.data.uv_layers.new(name='Root coverage261')
 for f in ob.data.polygons:
  for li,vi in zip(f.loop_indices,f.vertices):uv.data[li].uv=uvs[vi]
 clean_normals(ob)
 return {'replaced_support_objects':len(support),'boundary_range': [min(boundary),max(boundary)],'continuous_boundary':True,'actual_head_clearance':.0025,'main_locks_preserved':True}

if __name__=='__main__':
 report={};arg=next((x.split('=',1)[1].split(',') for x in sys.argv if x.startswith('--styles=')),['Feminine-side-sweep','Feminine-straight','Feminine-curls','Feminine-bob','Masculine-flow','Masculine-middle-part'])
 for key in arg:
  build,style=key.split('-',1);s=load261(build,style);frozen=protect(s);r=roots(s,style);check(s,frozen);u.bake(s)
  for ob in s.objects:
   if ob.type=='MESH' and ob.get('component159')=='hair':clean_normals(ob)
  for d in ['components','sources']:(W/d).mkdir(parents=True,exist_ok=True)
  source=W/'sources'/f'{key}-hair261.blend';out=W/'components'/f'{key}-hair261.glb';assert not source.exists();bpy.ops.outliner.orphans_purge(do_recursive=True);bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True);ex.export(s,out,'hair');prev258.patch258(out,s);r.update(source=str(source),path=str(out));report[key]=r;(W/'selected261.json').write_text(json.dumps(report,indent=2));(P/'selected261.json').write_text(json.dumps(report,indent=2));print('ROOT_REPAIR261',key,flush=True)
 print('ROOT_REPAIR261_COMPLETE',flush=True)
