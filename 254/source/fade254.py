import sys,json,math,struct
from pathlib import Path
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue252')
from common252 import *
import hair252 as old
P=Path('E:/Ravedio-Avatar/catalogue254');D=P.parent/'floating138/mobile-preview/254';CAT=json.loads((D.parent/'253/catalogue253.json').read_text());PI=math.pi

def shell(buzz=False):
 import random
 rng=random.Random(254);mat=a.material('Hair254 / rooted short groom',(.12,.047,.026),.43);mat.node_tree.nodes['Principled BSDF'].inputs['Specular IOR Level'].default_value=.28;vv=[];ff=[]
 # Buried crown coverage ends inside the dense rooted groom, not on the forehead.
 nu,nv=192,40
 for j in range(nv+1):
  for i in range(nu):
   ph=i/nu*2*PI;end=min(.79,old.boundary(ph,False));th=.003+j/nv*end;vv.append(tuple(c.sp(th,ph,.004)))
 for j in range(nv):
  for i in range(nu):x=j*nu+i;y=j*nu+(i+1)%nu;ff.append((x,y,y+nu,x+nu))
 ff.append(tuple(range(nu-1,-1,-1)));cap=a.mesh('Hair254 / buried crown support',vv,ff,mat,'hair');vv=[];ff=[];count=0
 for th in np.arange(.69,1.84,.019):
  number=round(2*PI*.47*math.sin(th)/.009)
  for k in range(number):
   phi=2*PI*(k+.5+rng.uniform(-.28,.28))/number;theta=th+rng.uniform(-.006,.006);end=old.boundary(phi,False)
   if theta>=end-.006:continue
   grade=smooth((end-theta)/.62)**.78;length=.0015+.047*grade;width=.00012+.0027*grade**.6;length=min(length,(end-theta)*.39);side=1 if phi<PI else -1;points=[]
   for t in [0,.5,1]:
    tt=theta+t*length/.45;pp=phi+side*math.sin(phi)**2*t*length/.64;points.append(c.sp(tt,pp,.0018+(.0015+.004*grade)*math.sin(PI*t)))
   start=len(vv)
   for j,p0 in enumerate(points):
    T=(points[min(j+1,2)]-points[max(j-1,0)]).normalized();N=(p0-a.C).normalized();B=T.cross(N).normalized();N=B.cross(T).normalized();r=width*([.72,1,.14][j]);depth=r*.35
    for angle in [0,PI*.5,PI,PI*1.5]:vv.append(tuple(p0+B*(r*math.cos(angle))+N*(depth*math.sin(angle))))
   for j in range(2):
    for k2 in range(4):x=start+j*4+k2;y=start+j*4+(k2+1)%4;ff.append((x,y,y+4,x+4))
   ff.extend([(start+3,start+2,start+1,start),tuple(start+8+k2 for k2 in range(4))]);count+=1
 ob=a.mesh('Hair254 / laid clipped fibers',vv,ff,mat,'hair');ob['modeled_rooted_fibers254']=count;print('ROOTED_FIBERS254',count,flush=True);return ob

def refine_long(s):
 changed=0
 for ob in [o for o in s.objects if o.type=='MESH' and o.get('component159')=='hair']:
  n=len(ob.data.vertices)
  if n!=2530:continue
  inv=ob.matrix_world.inverted();pts=[ob.matrix_world@v.co for v in ob.data.vertices];centers=[pts[0]]+[sum(pts[1+i*32:1+(i+1)*32],Vector())/32 for i in range(79)]+[pts[-1]]
  for i,v in enumerate(ob.data.vertices):
   row=0 if i==0 else 80 if i==n-1 else (i-1)//32+1;t=row/80;weight=smooth((t-.30)/.70)
   if weight<=0:continue
   center=centers[row];dv=center-a.C;q=Vector((dv.x/.48,dv.y/.405,dv.z/.455));th=math.acos(max(-1,min(1,q.normalized().z)));ph=math.atan2(q.x,-q.y);target=1.12+.10*smooth((abs(ph)-1.6)/.8);nth=th-max(0,th-target)*weight*.90;N=dv.normalized();hit,_,_,dist=c.HEAD.ray_cast(a.C,N,2);dep=max(.003,dv.length-dist);newcenter=c.sp(nth,ph,dep*(1-.93*weight));delta=pts[i]-center;rad=N*delta.dot(N);tan=delta-rad;v.co=inv@(newcenter+tan*(1-.38*weight)+rad*(1-.88*weight));changed+=1
  for v in ob.data.vertices:
   p=ob.matrix_world@v.co;w=smooth((p.y-.025)/.15);dv=p-a.C;hit,_,_,dist=c.HEAD.ray_cast(a.C,dv.normalized(),2);dep=max(.003,dv.length-dist)
   if w>0:v.co=inv@(hit+dv.normalized()*(dep*(1-.88*w)+.005*w))
  for m in ob.data.materials:
   old.normal_texture(m,'long');m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.36
   for n in m.node_tree.nodes:
    if n.type=='NORMAL_MAP':n.inputs['Strength'].default_value=.12
 return changed

def refine_curls(s):
 changed=0
 for ob in [o for o in s.objects if o.type=='MESH' and o.get('component159')=='hair']:
  inv=ob.matrix_world.inverted()
  for v in ob.data.vertices:
   p=ob.matrix_world@v.co;dv=p-a.C;q=Vector((dv.x/.48,dv.y/.405,dv.z/.455));th=math.acos(max(-1,min(1,q.normalized().z)));ph=math.atan2(q.x,-q.y);weight=smooth((th-.72)/.34)*smooth((abs(ph)-.65)/.3)
   if weight<=0:continue
   hit,_,_,dist=c.HEAD.ray_cast(a.C,dv.normalized(),2);dep=max(.003,dv.length-dist);v.co=inv@(hit+dv.normalized()*(dep*(1-.60*weight)));changed+=1
 return changed

def patch_export(path):
 raw=Path(path).read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);assert all(m.get('alphaMode','OPAQUE')=='OPAQUE' for m in g['materials']);assert any(m.get('name','').startswith('Hair254 / rooted short groom') for m in g['materials'])

def build(style):
 bpy.ops.wm.open_mainfile(filepath=str(P.parent/'catalogue252/sources'/f'Masculine-{style}-hair252.blend'));s=bpy.context.scene;frozen=protect(s);a.setup();c.reset_head(s)
 for ob in list(s.objects):
  if ob.get('component159')=='hair' and (style=='buzz' or any('fade coverage' in m.name or 'buzz edge' in m.name for m in ob.data.materials)):u.delete(ob)
 changed=refine_long(s) if style=='taper' else refine_curls(s) if style=='curly-top' else 0
 shell(style=='buzz')
 check(s,frozen);u.bake(s);bpy.ops.outliner.orphans_purge(do_recursive=True);bpy.ops.file.pack_all();src=P/'sources'/f'Masculine-{style}-hair254.blend';bpy.ops.wm.save_as_mainfile(filepath=str(src),compress=True);out=P/'components'/f'Masculine-{style}-hair254.glb';ex.export(s,out,'hair');patch_export(out);print('BUILD254',style,changed,flush=True)
 if '--render' in sys.argv:
  c.gpu()
  for angle in ['front','threequarter','profile','rightprofile','rear','top','underside']:
   u.camera(s,angle,448,False);s.camera.data.ortho_scale=1.65;s.cycles.samples=24;s.render.filepath=str(P/'review1'/f'{style}-{angle}.png');floor=s.objects.get('Studio floor');hidden=floor.hide_render if floor else False
   if floor and angle=='underside':floor.hide_render=True
   try:bpy.ops.render.render(write_still=True)
   finally:
    if floor:floor.hide_render=hidden
 return dict(path='components/'+out.name,source=str(src),protected_exact=True,modified_long_vertices=changed)
if __name__=='__main__':
 styles=next((x.split('=',1)[1].split(',') for x in sys.argv if x.startswith('--styles=')),['taper','curly-top']);out={k:v for k,v in json.loads((P/'hair254.json').read_text()).items() if k in ['taper','curly-top']} if (P/'hair254.json').exists() else {}
 for style in styles:out[style]=build(style);(P/'hair254.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8')
 print('BUILD254_COMPLETE',len(out),flush=True)
